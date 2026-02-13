import random
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup
import re
import json
from pathlib import Path
from time import sleep

HEADERS = {"User-Agent": "Mozilla/5.0"}
BASE_URL = "https://etcsl.orinst.ox.ac.uk/proverbs/"


# Boilerplate that appears at the start of every ETCSL proverb page
ETCSL_BOILERPLATE = (
    "The Electronic Text Corpus of Sumerian Literature "
    "Catalogues: by date | by number | in full "
    "Website info: navigation help | site description | display conventions | recent changes "
    "Project info: consolidated bibliography | about the project | credits and copyright | links "
    "This composition: composite text"
)


def _strip_editorial(line: str) -> str:
    """Remove editorial notes, references, and variants from a line."""
    # Remove {...} inline variants
    line = re.sub(r"\{.*?\}", "", line)
    # Remove (1 ms. has instead: ...)
    line = re.sub(r"\(\s*1 ms\. has instead:.*?\)", "", line, flags=re.IGNORECASE)
    # Remove ( cf. ... ) and ( cf. ... ) with optional space after (
    line = re.sub(r"\(\s*cf\..*?\)", "", line)
    # Remove ( = Alster ... ) style references
    line = re.sub(r"\(\s*=.*?\)", "", line)
    # Remove bare ( 6.1.07.43 ) style catalogue refs (optional)
    line = re.sub(r"\(\s*\d+\.\d+\.\d+.*?\)", "", line)
    return line


# Line starts with proverb number: "1." or "2." or "1-2." or "10-11."
_PROVERB_LINE_START = re.compile(r"^(\d+)(?:-\d+)?\.\s*")

# Phrases that indicate editorial noise (no real proverb content)
_NO_CONTENT_PHRASES = (
    re.compile(r"\d+\s*lines?\s*unclear", re.IGNORECASE),
    re.compile(r"\d+\s*lines?\s*fragmentary", re.IGNORECASE),
    re.compile(r"unknown\s+no\.?\s*of\s*lines?\s*missing", re.IGNORECASE),
    re.compile(r"approx\.?\s*\d+\s*lines?\s*missing", re.IGNORECASE),
    re.compile(r"^\d+\s*lines?\s*missing\s*$", re.IGNORECASE),
)


def _is_substantive_proverb(text: str) -> bool:
    """True if the text is real proverb content; False if only editorial noise."""
    t = text.strip()
    if not t or len(t) < 15:
        return False
    # Strip known noise phrases and dots; require substantial content left
    reduced = t
    for pat in _NO_CONTENT_PHRASES:
        reduced = pat.sub(" ", reduced)
    reduced = re.sub(r"[.\s…]+", " ", reduced).strip()
    return len(reduced) >= 20


def _parse_collection_from_page(soup) -> str:
    """Extract collection number from page (e.g. 'Proverbs: collection 1' -> '1')."""
    page_text = soup.get_text(" ", strip=False)
    m = re.search(r"[Pp]roverbs:?\s*collection\s+(\d+)", page_text, re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"collection\s+(\d+)", page_text, re.IGNORECASE)
    if m:
        return m.group(1)
    return "1"  # default for proverb pages


def _split_into_proverbs(cleaned_lines: list[str]) -> list[tuple[int, str]]:
    """Split lines into individual proverbs. Returns list of (proverb_number, text)."""
    blocks: list[list[str]] = []
    current: list[str] | None = None

    for line in cleaned_lines:
        match = _PROVERB_LINE_START.match(line)
        if match:
            # Start a new proverb block; first number is the line ref (we use running index)
            if current is not None and any(s.strip() for s in current):
                blocks.append(current)
            # Strip the leading "1." or "1-2." from this line
            rest = _PROVERB_LINE_START.sub("", line, count=1).strip()
            current = [rest] if rest else []
        else:
            if current is None:
                current = []
            if line.strip():
                current.append(line.strip())

    if current is not None and any(s.strip() for s in current):
        blocks.append(current)

    # Assign proverb_number as running index 1, 2, 3, ...
    return [(i, " ".join(block)) for i, block in enumerate(blocks, start=1)]


def parse_proverb_page(url: str, *, include_editorial_noise: bool = False):
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Collection from page text: "Proverbs: collection 1" -> "1"
    collection = _parse_collection_from_page(soup)

    # Page/composition id from URL for reference (e.g. 6.1.01)
    url_match = re.search(r"t\.(\d+\.\d+)\.(\d+)\.html", url)
    composition = f"{url_match.group(1)}.{url_match.group(2)}" if url_match else ""

    paragraphs = soup.find_all("p")
    cleaned_lines = []

    for p in paragraphs:
        line = p.get_text(" ", strip=True)

        # Skip site boilerplate (exact or prefix)
        if line.startswith("The Electronic Text Corpus") or ETCSL_BOILERPLATE in line:
            continue
        # Skip lines that are only editorial notes or footnotes
        if line.startswith("(") or line.startswith("{") or "line fragmentary" in line.lower():
            continue

        line = _strip_editorial(line)

        # Remove extra whitespace and collapse multiple spaces
        line = " ".join(line.split()).strip()

        if line:
            cleaned_lines.append(line)

    # Strip any leading boilerplate that might appear in first line
    if cleaned_lines and cleaned_lines[0].startswith("The Electronic Text Corpus"):
        idx = cleaned_lines[0].find("This composition: composite text")
        if idx != -1:
            first = cleaned_lines[0][idx + len("This composition: composite text") :].strip()
            if first:
                cleaned_lines[0] = first
            else:
                cleaned_lines.pop(0)

    proverb_blocks = _split_into_proverbs(cleaned_lines)

    # One JSON object per proverb; optionally skip editorial-only entries
    return [
        {
            "collection": collection,
            "proverb_number": num,
            "composition": composition,
            "text": text,
        }
        for num, text in proverb_blocks
        if include_editorial_noise or _is_substantive_proverb(text)
    ]


def build_proverb_archive(
    *,
    include_editorial_noise: bool = False,
    first_page: int = 1,
    last_page: int = 28,
) -> list[dict]:
    """Fetch ETCSL proverb pages and return a list of proverb dicts.

    Args:
        include_editorial_noise: If True, include entries that are only editorial
            (e.g. "1 line unclear"). If False, only include substantive proverbs.
        first_page: First page number (default 1 → 6.1.01).
        last_page: Last page number inclusive (default 28 → 6.1.28).

    Returns:
        List of proverb dicts (collection, proverb_number, composition, text).
    """
    archive = []
    for i in range(first_page, last_page + 1):
        url = f"{BASE_URL}t.6.1.{i:02d}.html"
        try:
            proverbs = parse_proverb_page(url, include_editorial_noise=include_editorial_noise)
            archive.extend(proverbs)
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                continue  # page does not exist (e.g. 6.1.06), skip
            raise RuntimeError(f"Failed to fetch {url}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to parse {url}: {e}") from e
        sleep(0.2)
    return archive


def get_random_proverb(path: str | Path = "sumerian_proverbs.json") -> dict:
    """Load the proverb archive from JSON and return a random proverb.

    Args:
        path: Path to sumerian_proverbs.json (default: "sumerian_proverbs.json").

    Returns:
        A single proverb dict with keys: collection, proverb_number, composition, text.

    Raises:
        FileNotFoundError: If the JSON file does not exist.
        ValueError: If the archive is empty.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Proverb archive not found: {path}")

    with open(path, encoding="utf-8") as f:
        proverbs = json.load(f)

    if not proverbs:
        raise ValueError("Proverb archive is empty")

    return random.choice(proverbs)
