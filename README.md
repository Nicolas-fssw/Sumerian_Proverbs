# Sumerian Proverbs

I am a fashioner of words, a composer of songs, a composer of words, and that they will recite my songs as heavenly writings, and that they will bow down before my words......

https://etcsl.orinst.ox.ac.uk/index1.htm

## Encrypted archive (required)

The archive is always stored encrypted. You must set the environment variable `PROVERB_ARCHIVE_KEY` to a Fernet key. Both `create_proverb_archive` and `random_proverb` will raise if the key is missing.

Generate a key (Python):

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Then set it, e.g. `export PROVERB_ARCHIVE_KEY="your-key"` (or use a `.env` file and load it).