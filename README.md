# Sumerian Proverbs

I am a fashioner of words, a composer of songs, a composer of words, and that they will recite my songs as heavenly writings, and that they will bow down before my words......

https://etcsl.orinst.ox.ac.uk/index1.htm

## Encrypted archive (required)

The archive is always stored encrypted. Put your Fernet key in a `.env` file in the project root:

```
PROVERB_ARCHIVE_KEY=your-fernet-key-here
```

Generate a key: `uv run python create_proverb_archive.py --generate-key`, then copy the output into `.env`. The `.env` file is gitignored.

## Train a proverb generator

Fine-tune DistilGPT-2 on the archive so it can generate new proverbs in a similar style:

```bash
uv sync
uv run python train_proverb_model.py
```

Training runs on CPU by default (slower); use a GPU or Google Colab for faster runs. The model is saved in `proverb_model/`.

Generate a single proverb:

```bash
uv run python generate_proverb.py -m proverb_model
```

## Sumerian or Synthetic? (game)

Guess whether each proverb is from the archive (Sumerian) or generated (Synthetic). Requires a trained model and your `.env` key.

```bash
uv run python proverb_game.py --rounds 5
```

Type `1` for Real, `2` for AI. Score is shown at the end.