#!/usr/bin/env python3
"""Create the Sumerian proverb archive from ETCSL and save to JSON."""

import argparse
from pathlib import Path

from cryptography.fernet import Fernet

from utility import build_proverb_archive, save_archive

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch ETCSL proverb pages and save to a JSON archive."
    )
    parser.add_argument(
        "--generate-key",
        action="store_true",
        help="Print a new Fernet key and exit. Set PROVERB_ARCHIVE_KEY to this value.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("ancient_wisdoms.json"),
        help="Output JSON path (default: ancient_wisdoms.json)",
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

    if args.generate_key:
        print(Fernet.generate_key().decode())
        return

    print("Fetching proverb pages from ETCSL...")
    archive = build_proverb_archive(
        include_editorial_noise=args.include_editorial_noise,
        first_page=args.first_page,
        last_page=args.last_page,
    )

    save_archive(args.output, archive)
    print(f"Saved {len(archive)} proverbs to {args.output}")


if __name__ == "__main__":
    main()
