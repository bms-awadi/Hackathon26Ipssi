from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)

DATA_DIR = "/opt/airflow/data/raw"


def get_latest_file(**context) -> dict:
    from minio import Minio
    import os

    conf = context.get("dag_run").conf or {}
    document_id = conf.get("document_id")

    endpoint = os.environ.get("MINIO_ENDPOINT", "http://minio:9000").replace("http://", "")
    client = Minio(
        endpoint,
        access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
        secure=False,
    )

    bucket = os.environ.get("MINIO_BUCKET_RAW", "raw")
    if document_id:
        objects = list(client.list_objects(bucket, prefix=document_id))
        if not objects:
            raise ValueError(f"Aucun fichier trouvé pour document_id={document_id}")
        object_key = objects[0].object_name
    else:
        objects = list(client.list_objects(bucket, recursive=True))
        if not objects:
            raise ValueError(f"Aucun fichier dans MinIO bucket {bucket}")
        object_key = sorted(objects, key=lambda o: o.last_modified, reverse=True)[0].object_name
        document_id = object_key.split(".")[0]

    _, ext = os.path.splitext(object_key)
    local_path = f"/tmp/{document_id}{ext}"
    client.fget_object(bucket, object_key, local_path)
    log.info("Fichier récupéré depuis MinIO : %s -> %s", object_key, local_path)

    return {
        "local_path": local_path,
        "object_key": object_key,
        "document_id": document_id,
    }


def ingest_task(**context):
    from scripts.ingest import ingest_document
    file_info = context["ti"].xcom_pull(task_ids="get_file")
    if not file_info:
        raise ValueError("Aucune info reçue depuis get_file")
    path = file_info.get("local_path") or file_info
    result = ingest_document(path if isinstance(path, str) else path)
    result["document_id"] = file_info.get("document_id", "")
    return result


def upload_raw_task(**context) -> dict:
    from scripts.minio_raw import upload_raw

    file_info = context["ti"].xcom_pull(task_ids="ingest_document")
    if not file_info:
        raise ValueError("Aucune info recue depuis ingest_document")

    file_path = file_info.get("path")
    if not file_path:
        raise ValueError("ingest_document n'a pas fourni de path")

    # document_id stable pour une clé MinIO stable
    document_id = os.path.splitext(os.path.basename(file_path))[0]
    return upload_raw(local_path=file_path, document_id=document_id)


def minio_raw_to_clean_task(**context) -> dict:
    from scripts.minio_clean import raw_to_clean

    uploaded = context["ti"].xcom_pull(task_ids="upload_raw_to_minio")
    if not uploaded:
        raise ValueError("Aucune info recue depuis upload_raw_to_minio")

    return raw_to_clean(
        document_id=uploaded["document_id"],
        raw_object_key=uploaded["object_key"],
        document_type="facture_fournisseur",
    )


def ocr_task(**context) -> str:
    from scripts.ocr import run_ocr
    file_info = context["ti"].xcom_pull(task_ids="ingest_document")
    if not file_info:
        raise ValueError("Aucune info recue depuis ingest_document")
    log.info("OCR sur : %s", file_info.get("path"))
    return run_ocr(file_info)


def extract_task(**context) -> dict:
    from scripts.extract import extract_entities
    ocr_result = context["ti"].xcom_pull(task_ids="run_ocr")
    if not ocr_result:
        raise ValueError("Aucun résultat reçu depuis run_ocr")
    text = ocr_result["text"] if isinstance(ocr_result, dict) else ocr_result
    result = extract_entities(text)
    # Faire transiter les métadonnées OCR vers validate et store
    if isinstance(ocr_result, dict):
        result["file_path"]        = ocr_result.get("file_path")
        result["confidence_score"] = ocr_result.get("confidence_score")
    return result


def validate_task(**context) -> dict:
    from scripts.validate import validate_document
    data = context["ti"].xcom_pull(task_ids="extract_entities")
    if not data:
        raise ValueError("Aucune donnee recue depuis extract_entities")
    return validate_document(data)


def store_task(**context) -> None:
    from scripts.store import store_curated
    data = context["ti"].xcom_pull(task_ids="validate_document")
    if not data:
        raise ValueError("Aucune donnee recue depuis validate_document")
    store_curated(data)


def notify_task(**context):
    from scripts.notify import notify_frontend

    validated = context["ti"].xcom_pull(task_ids="validate_document")
    document_id = ""
    
    if validated and isinstance(validated, dict):
        source = validated.get("source_file", "") or ""
        document_id = source.split("/")[-1].split(".")[0] if source else ""

    if not document_id:
        get_file_result = context["ti"].xcom_pull(task_ids="get_file")
        if isinstance(get_file_result, dict):
            document_id = get_file_result.get("document_id", "")
        else:
            import os
            document_id = os.path.splitext(os.path.basename(str(get_file_result or "")))[0]

    notify_frontend(validated_data=validated, document_id=document_id)


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
    "email_on_retry": False,
}

with DAG(
    dag_id="document_pipeline",
    description="Pipeline OCR multi-format : pdf, image, txt",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["document", "ocr", "pipeline"],
) as dag:

    t0 = PythonOperator(task_id="get_file",          python_callable=get_latest_file)
    t1 = PythonOperator(task_id="ingest_document",   python_callable=ingest_task)
    # t1b = PythonOperator(task_id="upload_raw_to_minio", python_callable=upload_raw_task)
    # t1c = PythonOperator(task_id="raw_to_clean_texts",  python_callable=minio_raw_to_clean_task)
    t2 = PythonOperator(task_id="run_ocr",           python_callable=ocr_task)
    t3 = PythonOperator(task_id="extract_entities",  python_callable=extract_task)
    t4 = PythonOperator(task_id="validate_document", python_callable=validate_task)
    t5 = PythonOperator(task_id="store_curated",     python_callable=store_task)
    t6 = PythonOperator(task_id="notify_frontend",   python_callable=notify_task)

    # Nouveau flux : stockage zone "clean" (JSON contractuel) dans MinIO Clean
    # t0 >> t1 >> t1b >> t1c

    # Flux existant (local) conservé pour curated/validation
    t0 >> t1 >> t2 >> t3 >> t4 >> t5 >> t6