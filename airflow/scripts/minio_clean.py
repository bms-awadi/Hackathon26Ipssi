import logging
import os

log = logging.getLogger(__name__)


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


MINIO_BUCKET_RAW = _env("MINIO_BUCKET_RAW", "raw")


def raw_to_clean(document_id: str, raw_object_key: str, document_type: str = "facture_fournisseur") -> dict:
    """
    Exécute le pipeline OCR_extraction : MinIO Raw -> JSON structuré -> MinIO Clean.
    """
    # Import depuis le module projet (monté dans /opt/airflow/ocr_extraction)
    from extraction.pipeline import extract_from_minio_to_clean

    log.info("[minio_clean] Processing raw object %s/%s (document_id=%s)", MINIO_BUCKET_RAW, raw_object_key, document_id)
    return extract_from_minio_to_clean(
        document_id=document_id,
        raw_object_key=raw_object_key,
        document_type=document_type,
        store_clean=True,
    )

