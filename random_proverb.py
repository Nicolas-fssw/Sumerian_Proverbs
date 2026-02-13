#!/usr/bin/env python3
"""Print a random proverb from the Sumerian proverb archive."""

import argparse
from pathlib import Path

from utility import get_random_proverb, wisdom_score


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print a random proverb from the JSON archive."
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=Path("ancient_wisdoms.json"),
        help="Path to ancient_wisdoms.json (default: ancient_wisdoms.json)",
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
        wisdom = proverb.get("wisdom_score") or wisdom_score(proverb["text"])
        print(f"Composition {comp}, proverb {num}")
        print(f"Wisdom score: {wisdom}/10")
        print(proverb["text"])


if __name__ == "__main__":
    main()
