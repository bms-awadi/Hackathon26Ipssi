from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv

load_dotenv()

BUCKETS = [
    "raw",
    "clean",
    "curated",
]

def init_buckets():
    client = Minio(
        os.getenv("MINIO_ENDPOINT", "localhost:9000").replace("http://", ""),
        access_key=os.getenv("MINIO_ROOT_USER", "minio_admin"),
        secret_key=os.getenv("MINIO_ROOT_PASSWORD", "minio_password"),
        secure=False,
    )

    for bucket in BUCKETS:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            print(f"Bucket créé : {bucket}")
        else:
            print(f"Bucket déjà existant : {bucket}")

    print("\nMinIO prêt. Buckets disponibles :")
    for b in client.list_buckets():
        print(f"  - {b.name}")

if __name__ == "__main__":
    init_buckets()
