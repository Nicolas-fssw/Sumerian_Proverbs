# Sumerian Proverbs

I am a fashioner of words, a composer of songs, a composer of words, and that they will recite my songs as heavenly writings, and that they will bow down before my words......

https://etcsl.orinst.ox.ac.uk/index1.htm

## Encrypted archive (required)

The archive is always stored encrypted. Put your Fernet key in a `.env` file in the project root:

```
PROVERB_ARCHIVE_KEY=your-fernet-key-here
```

Generate a key: `uv run python create_proverb_archive.py --generate-key`, then copy the output into `.env`. The `.env` file is gitignored.