from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET_RAW = "raw-documents"
BUCKET_CLEAN = "clean-texts"
BUCKET_CURATED = "curated-data"

def get_client() -> Minio:
    return Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", ""),
        access_key=os.getenv("MINIO_ROOT_USER", "minio_admin"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minio_password"),
        secure=False,
    )

def upload_file(bucket: str, object_name: str, file_path: str) -> str:
    client = get_client()
    client.fput_object(bucket, object_name, file_path)
    return f"{bucket}/{object_name}"

def download_file(bucket: str, object_name: str, dest_path: str) -> None:
    client = get_client()
    client.fget_object(bucket, object_name, dest_path)

def list_objects(bucket: str, prefix: str = "") -> list[str]:
    client = get_client()
    return [obj.object_name for obj in client.list_objects(bucket, prefix=prefix, recursive=True)]