from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import sys

# rendre /opt/airflow accessible
sys.path.append("/opt/airflow")

# Imports scripts
from scripts.ingest import ingest_document
from scripts.ocr import run_ocr
from scripts.extract import extract_entities
from scripts.validate import validate_document
from scripts.store import store_curated
from scripts.notify import notify_frontend


#Dossier data dans Docker
DATA_DIR = "/opt/airflow/data"


# Trouver automatiquement un fichier
def get_latest_file(**context):
    files = os.listdir(DATA_DIR)

    if not files:
        raise ValueError("Aucun fichier dans /data")

    files = sorted(
        files,
        key=lambda x: os.path.getmtime(os.path.join(DATA_DIR, x)),
        reverse=True
    )

    latest_file = os.path.join(DATA_DIR, files[0])
    print(f"Fichier détecté : {latest_file}")

    return latest_file


# INGEST
def ingest_task(**context):
    file_path = context["ti"].xcom_pull(task_ids="get_file")
    result = ingest_document(file_path)
    return result


#  OCR
def ocr_task(**context):
    file_info = context["ti"].xcom_pull(task_ids="ingest_document")
    result = run_ocr(file_info)
    return result


#  EXTRACT
def extract_task(**context):
    text = context["ti"].xcom_pull(task_ids="run_ocr")
    result = extract_entities(text)
    return result


#  VALIDATE
def validate_task(**context):
    data = context["ti"].xcom_pull(task_ids="extract_entities")
    result = validate_document(data)
    return result


#  STORE
def store_task(**context):
    data = context["ti"].xcom_pull(task_ids="validate_document")
    store_curated(data)


#  NOTIFY
def notify_task(**context):
    notify_frontend()


# DAG
with DAG(
    dag_id="document_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,  
    catchup=False
) as dag:

    t0 = PythonOperator(
        task_id="get_file",
        python_callable=get_latest_file
    )

    t1 = PythonOperator(
        task_id="ingest_document",
        python_callable=ingest_task
    )

    t2 = PythonOperator(
        task_id="run_ocr",
        python_callable=ocr_task
    )

    t3 = PythonOperator(
        task_id="extract_entities",
        python_callable=extract_task
    )

    t4 = PythonOperator(
        task_id="validate_document",
        python_callable=validate_task
    )

    t5 = PythonOperator(
        task_id="store_curated",
        python_callable=store_task
    )

    t6 = PythonOperator(
        task_id="notify_frontend",
        python_callable=notify_task
    )

    # pipeline
    t0 >> t1 >> t2 >> t3 >> t4 >> t5 >> t6
