#!/usr/bin/env python3
"""Print a random proverb from the Sumerian proverb archive."""

import argparse
from pathlib import Path

from utility import get_random_proverb


def wisdom_score(text: str) -> int:
    """Compute a deterministic wisdom score (1-10) from proverb text."""
    words = text.split()
    n = len(words)
    score = 4  # base
    if "?" in text:
        score += 1  # question suggests reflection
    if 8 <= n <= 25:
        score += 1  # moderate length
    if "," in text or ";" in text:
        score += 1  # structured / multiple clauses
    for contrast in (" not ", " but ", " though ", " yet ", " or "):
        if contrast in text.lower():
            score += 1
            break  # one bonus for contrast
    if '"' in text:
        score += 1  # cited speech / dialogue
    return max(1, min(10, score))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print a random proverb from the JSON archive."
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=Path("sumerian_proverbs.json"),
        help="Path to sumerian_proverbs.json (default: sumerian_proverbs.json)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Print only the proverb text, no composition or metadata.",
    )
    args = parser.parse_args()

    proverb = get_random_proverb(args.file)

    if args.quiet:
        print(proverb["text"])
    else:
        comp = proverb["composition"]
        num = proverb["proverb_number"]
        wisdom = wisdom_score(proverb["text"])
        print(f"Composition {comp}, proverb {num}")
        print(f"Wisdom score: {wisdom}/10")
        print(proverb["text"])


if __name__ == "__main__":
    main()
