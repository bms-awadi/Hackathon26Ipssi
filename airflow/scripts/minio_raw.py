import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


MINIO_ENDPOINT = _env("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = _env("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = _env("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET_RAW = _env("MINIO_BUCKET_RAW", "raw-documents")


def _get_minio_client():
    from minio import Minio

    endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    secure = MINIO_ENDPOINT.startswith("https://")
    return Minio(
        endpoint,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=secure,
    )


def upload_raw(local_path: str, document_id: str | None = None) -> dict:
    """
    Upload un fichier local vers MinIO bucket Raw.

    Returns:
      dict { bucket, object_key, document_id, filename }
    """
    p = Path(local_path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {local_path}")

    if document_id is None or document_id == "":
        document_id = p.stem

    object_key = f"{document_id}{p.suffix.lower()}"
    client = _get_minio_client()
    client.fput_object(MINIO_BUCKET_RAW, object_key, str(p))
    log.info("[minio_raw] Uploaded %s -> %s/%s", p.name, MINIO_BUCKET_RAW, object_key)
    return {
        "bucket": MINIO_BUCKET_RAW,
        "object_key": object_key,
        "document_id": document_id,
        "filename": p.name,
    }

