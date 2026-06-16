import re

def has_vowel(text: str) -> bool:
    return bool(re.search(r'[AIUEOaiueo]', text))

def clean_text(text: str) -> str:
    # Mengikuti utils.CleanText di Golang: mempertahankan huruf, angka, spasi, titik, koma, strip, dan slash
    s = re.sub(r'[^A-Za-z0-9\s\.,\-/]', '', text)
    s = re.sub(r'[\.\s,]+$', '', s)  # Hapus noise di akhir kata
    return re.sub(r'\s+', ' ', s).strip()