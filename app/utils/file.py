import charset_normalizer

def get_encoding(file) -> str :
    with open(file, "rb") as f:
        sample = f.read(50000)
        results = charset_normalizer.from_bytes(sample)
        return str(results.best().encoding) if results.best() else "utf-8"