#!/usr/bin/env python3
"""Generate a single proverb using the fine-tuned model."""

import argparse
import re
from pathlib import Path

# Min length (chars) and min fraction of letters (excluding spaces) for acceptable output
MIN_ACCEPTABLE_LENGTH = 15
MIN_LETTER_RATIO = 0.35
MAX_LEADING_JUNK = 2  # max punctuation/symbols at start before real content
MAX_REPEAT_RUN = 4    # max repeated dots/underscores/same punctuation in a row

# Keep only ASCII letters, digits, and common English punctuation
ALLOWED_CHARS = re.compile(r"[^a-zA-Z0-9\s.,!?\'\"\-;:()]")


def sanitize_proverb(text: str) -> str:
    """Remove weird/non-ASCII characters; keep only letters, digits, and common punctuation."""
    cleaned = ALLOWED_CHARS.sub("", text)
    # Collapse multiple spaces and strip
    cleaned = " ".join(cleaned.split()).strip()
    # Drop leading punctuation/space left after removing junk (e.g. ", a house..." -> "a house...")
    cleaned = re.sub(r"^[\s.,!?\'\"\-;:()]+", "", cleaned).strip()
    return cleaned


def is_acceptable_proverb(text: str) -> bool:
    """Return False if the generated text looks like junk (punctuation soup, ellipsis, etc.)."""
    t = text.strip()
    if len(t) < MIN_ACCEPTABLE_LENGTH:
        return False
    # Reject if it starts with a long run of punctuation/underscores/dots (e.g. "!!!", "_____", "......")
    leading_junk = re.match(r"^[\s\._!?\-\"']*", t)
    if leading_junk:
        junk_len = len(leading_junk.group(0).strip())
        if junk_len > MAX_LEADING_JUNK:
            return False
    # Count letters vs other printable chars (ignore spaces)
    no_spaces = "".join(t.split())
    if not no_spaces:
        return False
    letters = sum(1 for c in no_spaces if c.isalpha())
    if letters / len(no_spaces) < MIN_LETTER_RATIO:
        return False
    # Reject long runs of the same punctuation (...., ___, !!!, ???)
    if re.search(r"(\.|_|\?|!|\-)\1{" + str(MAX_REPEAT_RUN) + r",}", t):
        return False
    # Reject if it's mostly dots/ellipsis
    if t.count(".") >= len(t) // 2:
        return False
    # Reject CJK / fullwidth punctuation that slipped in (e.g. 『)
    if re.search(r"[\u3000-\u303f\uff00-\uffef]", t):
        return False
    return True


def _generate_one(tokenizer, model, prompt: str, temperature: float) -> str:
    import torch
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=80,
            do_sample=True,
            temperature=temperature,
            pad_token_id=tokenizer.eos_token_id,
        )
    full = tokenizer.decode(out[0], skip_special_tokens=True)
    rest = full[len(prompt) :].strip()
    for sep in ("\n", ". ", "!"):
        if sep in rest:
            rest = rest.split(sep)[0].strip() + (sep.strip() or "")
            break
    rest = rest or full[len(prompt) :].strip()
    return sanitize_proverb(rest)


def load_proverb_model(model_dir: Path | str):
    """Load tokenizer and model once. Returns (tokenizer, model) for reuse."""
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_dir = Path(model_dir)
    if not model_dir.is_dir():
        raise FileNotFoundError(f"Model not found at {model_dir}")
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForCausalLM.from_pretrained(str(model_dir))
    model.eval()
    return tokenizer, model


def generate_proverb(
    model_dir: Path | str | None = None,
    temperature: float = 0.9,
    max_retries: int = 15,
    tokenizer=None,
    model=None,
) -> str:
    """Generate one proverb. Pass tokenizer+model to reuse a loaded model (no reload)."""
    from transformers import AutoTokenizer, AutoModelForCausalLM

    if tokenizer is not None and model is not None:
        pass  # use provided
    else:
        model_dir = Path(model_dir or Path("proverb_model"))
        if not model_dir.is_dir():
            raise FileNotFoundError(f"Model not found at {model_dir}")
        tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        model = AutoModelForCausalLM.from_pretrained(str(model_dir))
        model.eval()

    prompt = "Proverb: "
    best = None
    best_score = -1.0

    for _ in range(max_retries):
        rest = _generate_one(tokenizer, model, prompt, temperature)
        if is_acceptable_proverb(rest):
            return rest
        no_spaces = "".join(rest.split())
        if no_spaces:
            score = sum(1 for c in no_spaces if c.isalpha()) / len(no_spaces) * len(rest)
            if score > best_score:
                best_score = score
                best = rest

    return best if best is not None else rest


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a proverb with the fine-tuned model."
    )
    parser.add_argument(
        "-m",
        "--model-dir",
        type=Path,
        default=Path("proverb_model"),
        help="Path to saved model (default: proverb_model)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.9,
        help="Sampling temperature 0.0–2.0 (default: 0.9)",
    )
    args = parser.parse_args()

    try:
        text = generate_proverb(
            model_dir=args.model_dir,
            temperature=args.temperature,
        )
    except FileNotFoundError as e:
        raise SystemExit(e) from e
    except ImportError:
        raise SystemExit("Install ML dependencies: uv add torch transformers")

    print(text)


if __name__ == "__main__":
    main()
