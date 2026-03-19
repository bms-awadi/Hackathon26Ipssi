"""
OCR + extraction + contrat JSON.

Ce module implémente la partie "4. OCR & Extraction" du cahier de charges :
- Preprocessing OpenCV
- OCR multi-approche (Tesseract puis fallback EasyOCR)
- Extraction (spaCy fr_core_news_lg + regex ciblées)
- Production d'un JSON contractuel (Awadi/Ryma)
- Persistance "zone Clean" dans MinIO
"""

from .pipeline import extract_from_local_file, extract_from_minio_to_clean

__all__ = ["extract_from_local_file", "extract_from_minio_to_clean"]

