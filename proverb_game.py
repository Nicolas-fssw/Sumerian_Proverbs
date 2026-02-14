#!/usr/bin/env python3
"""Game: guess whether each proverb is Sumerian (from the archive) or Synthetic."""

import argparse
import random
from pathlib import Path

from utility import get_random_proverb


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sumerian or Synthetic? Guess if the proverb is from the archive or generated."
    )
    parser.add_argument(
        "-f",
        "--archive",
        type=Path,
        default=Path("ancient_wisdoms.json"),
        help="Path to encrypted proverb archive",
    )
    parser.add_argument(
        "-m",
        "--model-dir",
        type=Path,
        default=Path("proverb_model"),
        help="Path to fine-tuned model (default: proverb_model)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=20,
        help="Number of rounds (default: 5)",
    )
    args = parser.parse_args()

    try:
        from generate_proverb import generate_proverb, load_proverb_model
    except ImportError:
        raise SystemExit("Install ML dependencies: uv add torch transformers")

    if not args.model_dir.is_dir():
        raise SystemExit(
            f"Model not found at {args.model_dir}. Run train_proverb_model.py first."
        )

    print("Sumerian or Synthetic? — proverb edition")
    print("You'll see a proverb. Type 1 for Sumerian (from the archive), 2 for Synthetic.\n")
    print("Loading model...")
    tokenizer, model = load_proverb_model(args.model_dir)
    # Decide round types and pre-generate all synthetic proverbs (no delay during play)
    round_types = [random.choice([True, False]) for _ in range(args.rounds)]
    n_synthetic = sum(1 for x in round_types if not x)
    if n_synthetic:
        print(f"Generating synthetic proverb(s) for this game...")
        synthetic_list = [
            generate_proverb(tokenizer=tokenizer, model=model)
            for _ in range(n_synthetic)
        ]
    else:
        synthetic_list = []
    synthetic_idx = 0
    print()

    score = 0
    for r in range(1, args.rounds + 1):
        is_real = round_types[r - 1]
        if is_real:
            proverb = get_random_proverb(args.archive)
            text = proverb["text"]
        else:
            text = synthetic_list[synthetic_idx]
            synthetic_idx += 1

        print(f"--- Round {r}/{args.rounds} ---")
        print(f'"{text}"')
        while True:
            guess = input("Sumerian (1) or Synthetic (2)? ").strip()
            if guess in ("1", "2"):
                break
            print("Type 1 or 2.")

        correct = (guess == "1") == is_real
        if correct:
            score += 1
            print("Correct!")
        else:
            print("Wrong!")
        print("It was", "SUMERIAN" if is_real else "SYNTHETIC")
        print()

    print(f"Score: {score}/{args.rounds}")


if __name__ == "__main__":
    main()
