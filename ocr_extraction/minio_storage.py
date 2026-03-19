import os
import tempfile
from typing import Optional


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


MINIO_ENDPOINT = _env("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = _env("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = _env("MINIO_SECRET_KEY", "minioadmin")

# Buckets : par defaut on s'aligne sur les buckets existants dans le repo (raw/clean/curated),
# mais on peut les surcharger pour matcher le cahier ("raw-documents"/"clean-texts"/"curated-data").
MINIO_BUCKET_RAW = _env("MINIO_BUCKET_RAW", "raw")
MINIO_BUCKET_CLEAN_TEXTS = _env("MINIO_BUCKET_CLEAN_TEXTS", "clean")


def get_minio_client():
    from minio import Minio

    endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    secure = MINIO_ENDPOINT.startswith("https://")
    return Minio(
        endpoint,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=secure,
    )


def download_from_minio(
    object_key: str,
    bucket: str = MINIO_BUCKET_RAW,
    local_path: Optional[str] = None,
) -> str:
    """
    Telecharge un objet MinIO vers un fichier local.
    Retourne le chemin local.
    """
    client = get_minio_client()

    if local_path is None:
        fd, path = tempfile.mkstemp(prefix="minio_", suffix=".bin")
        os.close(fd)
        local_path = path

    client.fget_object(bucket, object_key, local_path)
    return local_path


def put_json_to_minio(
    payload: dict,
    object_key: str,
    bucket: str = MINIO_BUCKET_CLEAN_TEXTS,
) -> None:
    import json
    import io

    client = get_minio_client()
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")

    client.put_object(
        bucket,
        object_key,
        data=io.BytesIO(data),
        length=len(data),
        content_type="application/json",
    )

