from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

log = logging.getLogger(__name__)

DATA_DIR = "/opt/airflow/data/raw"


def get_latest_file(**context) -> str:
    if not os.path.exists(DATA_DIR):
        raise FileNotFoundError(f"Dossier introuvable : {DATA_DIR}")

    files = [
        f for f in os.listdir(DATA_DIR)
        if os.path.isfile(os.path.join(DATA_DIR, f)) and not f.startswith(".")
    ]

    if not files:
        raise ValueError(f"Aucun fichier dans {DATA_DIR}")

    files_sorted = sorted(
        files,
        key=lambda x: os.path.getmtime(os.path.join(DATA_DIR, x)),
        reverse=True,
    )

    latest = os.path.join(DATA_DIR, files_sorted[0])
    log.info("Fichier detecte : %s", latest)
    return latest


def ingest_task(**context) -> dict:
    from scripts.ingest import ingest_document
    file_path = context["ti"].xcom_pull(task_ids="get_file")
    if not file_path:
        raise ValueError("Aucun fichier recu depuis get_file")
    log.info("Ingestion : %s", file_path)
    return ingest_document(file_path)


def ocr_task(**context) -> str:
    from scripts.ocr import run_ocr
    file_info = context["ti"].xcom_pull(task_ids="ingest_document")
    if not file_info:
        raise ValueError("Aucune info recue depuis ingest_document")
    log.info("OCR sur : %s", file_info.get("path"))
    return run_ocr(file_info)


def extract_task(**context) -> dict:
    from scripts.extract import extract_entities
    text = context["ti"].xcom_pull(task_ids="run_ocr")
    if not text:
        raise ValueError("Aucun texte recu depuis run_ocr")
    log.info("Extraction sur %d caracteres", len(text))
    return extract_entities(text)


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


def notify_task(**context) -> None:
    from scripts.notify import notify_frontend
    notify_frontend()


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
    t2 = PythonOperator(task_id="run_ocr",           python_callable=ocr_task)
    t3 = PythonOperator(task_id="extract_entities",  python_callable=extract_task)
    t4 = PythonOperator(task_id="validate_document", python_callable=validate_task)
    t5 = PythonOperator(task_id="store_curated",     python_callable=store_task)
    t6 = PythonOperator(task_id="notify_frontend",   python_callable=notify_task)

    t0 >> t1 >> t2 >> t3 >> t4 >> t5 >> t6