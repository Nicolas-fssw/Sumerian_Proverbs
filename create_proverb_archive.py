#!/usr/bin/env python3
"""Create the Sumerian proverb archive from ETCSL and save to JSON."""

import argparse
import json
from pathlib import Path

from utility import build_proverb_archive


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch ETCSL proverb pages and save to a JSON archive."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("sumerian_proverbs.json"),
        help="Output JSON path (default: sumerian_proverbs.json)",
    )
    parser.add_argument(
        "--include-editorial-noise",
        action="store_true",
        help="Include proverbs that are only editorial (e.g. '1 line unclear'). "
        "By default these are skipped.",
    )
    parser.add_argument(
        "--first-page",
        type=int,
        default=1,
        metavar="N",
        help="First page number 1–28 (default: 1)",
    )
    parser.add_argument(
        "--last-page",
        type=int,
        default=28,
        metavar="N",
        help="Last page number 1–28 inclusive (default: 28)",
    )
    args = parser.parse_args()

    print("Fetching proverb pages from ETCSL...")
    archive = build_proverb_archive(
        include_editorial_noise=args.include_editorial_noise,
        first_page=args.first_page,
        last_page=args.last_page,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(archive)} proverbs to {args.output}")


if __name__ == "__main__":
    main()
