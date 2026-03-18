from __future__ import annotations
 
import logging
import os
from datetime import datetime, timedelta
 
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
 
log = logging.getLogger(__name__)
 
# ─── Configuration MinIO ───────────────────────────────────────────────────────
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT",    "http://minio:9000")
MINIO_ACCESS   = os.environ.get("MINIO_ACCESS_KEY",  "minioadmin")
MINIO_SECRET   = os.environ.get("MINIO_SECRET_KEY",  "minioadmin")
BUCKET_RAW     = os.environ.get("MINIO_BUCKET_RAW",     "raw")
BUCKET_CLEAN   = os.environ.get("MINIO_BUCKET_CLEAN",   "clean")
BUCKET_CURATED = os.environ.get("MINIO_BUCKET_CURATED", "curated")
 
# ─── Alerte Teams (optionnelle) ────────────────────────────────────────────────
TEAMS_WEBHOOK = os.environ.get("TEAMS_WEBHOOK_URL", "")
 
 
# ─── Helper : client MinIO ─────────────────────────────────────────────────────
def _get_minio_client():
    try:
        from minio import Minio
    except ImportError:
        raise ImportError(
            "minio non installé. Ajoutez 'minio' dans requirements.txt "
            "et reconstruisez l'image Docker."
        )
    endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    secure   = MINIO_ENDPOINT.startswith("https://")
    return Minio(endpoint, access_key=MINIO_ACCESS, secret_key=MINIO_SECRET, secure=secure)
 
 
# ─── Helper : alerte Teams sur échec ──────────────────────────────────────────
def _send_alert(context: dict) -> None:
    if not TEAMS_WEBHOOK:
        log.warning("Pas de TEAMS_WEBHOOK_URL — alerte ignorée.")
        return
    import urllib.request, json as _json
    ti      = context.get("task_instance")
    dag_id  = context.get("dag").dag_id
    task_id = ti.task_id if ti else "?"
    exc     = context.get("exception", "Erreur inconnue")
    message = {
        "@type": "MessageCard",
        "summary": f"Airflow — Échec {task_id}",
        "themeColor": "FF0000",
        "sections": [{
            "activityTitle": f"DAG `{dag_id}` — tâche `{task_id}` FAILED",
            "facts": [
                {"name": "Erreur",    "value": str(exc)[:300]},
                {"name": "Timestamp", "value": datetime.now().isoformat()},
            ],
        }],
    }
    payload = _json.dumps(message).encode()
    req = urllib.request.Request(
        TEAMS_WEBHOOK, data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        log.info("Alerte Teams envoyée pour %s", task_id)
    except Exception as e:
        log.warning("Échec envoi alerte Teams : %s", e)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# TÂCHE 1 — get_file
# Récupère le fichier le plus récent dans le bucket raw MinIO
# ═══════════════════════════════════════════════════════════════════════════════
def get_latest_file(**context) -> dict:
    client  = _get_minio_client()
    objects = list(client.list_objects(BUCKET_RAW))
 
    if not objects:
        raise ValueError(
            f"Aucun fichier dans le bucket MinIO '{BUCKET_RAW}'. "
            "Le frontend a-t-il bien uploadé un document ?"
        )
 
    objects.sort(key=lambda o: o.last_modified, reverse=True)
    latest = objects[0]
 
    file_info = {
        "object_name":   latest.object_name,
        "bucket":        BUCKET_RAW,
        "size_bytes":    latest.size,
        "last_modified": latest.last_modified.isoformat(),
    }
    log.info("[get_file] %s (%d bytes)", latest.object_name, latest.size)
    return file_info
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# TÂCHE 2 — ingest_document
# Télécharge depuis raw, détecte le type de fichier
# ═══════════════════════════════════════════════════════════════════════════════
def ingest_task(**context) -> dict:
    from scripts.ingest import ingest_document
 
    file_info: dict = context["ti"].xcom_pull(task_ids="get_file")
    if not file_info:
        raise ValueError("XCom vide depuis 'get_file'.")
 
    client      = _get_minio_client()
    object_name = file_info["object_name"]
 
    # Téléchargement dans /tmp (dossier temporaire disponible dans le container)
    local_tmp = f"/tmp/{object_name.replace('/', '_')}"
    client.fget_object(BUCKET_RAW, object_name, local_tmp)
    log.info("[ingest] Téléchargé vers %s", local_tmp)
 
    result = ingest_document(local_tmp)
    result["object_name"] = object_name
    result["local_tmp"]   = local_tmp
    log.info("[ingest] Type détecté : %s", result.get("type"))
    return result
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# TÂCHE 3 — run_ocr
# OCR avec prétraitement OpenCV pour scans dégradés (J3)
# ═══════════════════════════════════════════════════════════════════════════════
def ocr_task(**context) -> dict:
    from scripts.ocr import run_ocr
 
    file_info: dict = context["ti"].xcom_pull(task_ids="ingest_document")
    if not file_info:
        raise ValueError("XCom vide depuis 'ingest_document'.")
 
    log.info("[ocr] Traitement de %s (type: %s)",
             file_info.get("local_tmp"), file_info.get("type"))
 
    result = run_ocr(file_info)
 
    if "text" not in result:
        raise ValueError("run_ocr n'a pas retourné de champ 'text'.")
    if not result["text"].strip():
        raise ValueError(
            f"OCR vide pour {file_info.get('object_name')} — "
            "fichier illisible ou corrompu."
        )
 
    log.info("[ocr] OK — %d chars | confiance : %.2f",
             len(result["text"]), result.get("confidence_score", -1))
    return result
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# TÂCHE 4 — extract_entities
# Extraction structurée + dépôt JSON en zone CLEAN
# ═══════════════════════════════════════════════════════════════════════════════
def extract_task(**context) -> dict:
    import json, io
    from scripts.extract import extract_entities
 
    ocr_result: dict = context["ti"].xcom_pull(task_ids="run_ocr")
    file_info: dict  = context["ti"].xcom_pull(task_ids="ingest_document")
    if not ocr_result:
        raise ValueError("XCom vide depuis 'run_ocr'.")
 
    object_name = file_info["object_name"]
    extracted   = extract_entities(ocr_result["text"])
 
    # Enrichissement — score OCR pour Thomas (conformité)
    extracted["ocr_confidence"] = ocr_result.get("confidence_score")
    extracted["source_file"]    = object_name
    extracted["processed_at"]   = datetime.now().isoformat()
 
    # Dépôt zone CLEAN
    client    = _get_minio_client()
    clean_key = object_name.rsplit(".", 1)[0] + "_clean.json"
    payload   = json.dumps(extracted, ensure_ascii=False, indent=2).encode("utf-8")
    client.put_object(
        BUCKET_CLEAN, clean_key,
        data=io.BytesIO(payload), length=len(payload),
        content_type="application/json",
    )
    log.info("[extract] Déposé en zone clean : %s/%s", BUCKET_CLEAN, clean_key)
 
    extracted["clean_object_name"] = clean_key
    return extracted
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# TÂCHE 5 — validate_document
# Validation métier (Luhn SIRET, cohérence TVA) + dépôt en zone CURATED
# ═══════════════════════════════════════════════════════════════════════════════
def validate_task(**context) -> dict:
    import json, io
    from scripts.validate import validate_document
 
    data: dict = context["ti"].xcom_pull(task_ids="extract_entities")
    if not data:
        raise ValueError("XCom vide depuis 'extract_entities'.")
 
    validated   = validate_document(data)
    client      = _get_minio_client()
    source_file = data.get("source_file", "unknown")
    curated_key = source_file.rsplit(".", 1)[0] + "_curated.json"
    payload     = json.dumps(validated, ensure_ascii=False, indent=2).encode("utf-8")
    client.put_object(
        BUCKET_CURATED, curated_key,
        data=io.BytesIO(payload), length=len(payload),
        content_type="application/json",
    )
    log.info("[validate] Déposé en zone curated : %s/%s", BUCKET_CURATED, curated_key)
 
    validated["curated_object_name"] = curated_key
    return validated
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# TÂCHE 6 — store_curated
# Enregistrement final (index fournisseur pour Nathalie)
# ═══════════════════════════════════════════════════════════════════════════════
def store_task(**context) -> None:
    from scripts.store import store_curated
 
    data: dict = context["ti"].xcom_pull(task_ids="validate_document")
    if not data:
        raise ValueError("XCom vide depuis 'validate_document'.")
    store_curated(data)
    log.info("[store] Enregistrement terminé.")
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# TÂCHE 7 — notify_frontend
# Notifie le backend Node.js (Ryma) que le JSON curated est disponible
# ═══════════════════════════════════════════════════════════════════════════════
def notify_task(**context) -> None:
    from scripts.notify import notify_frontend
 
    validated   = context["ti"].xcom_pull(task_ids="validate_document")
    curated_key = validated.get("curated_object_name", "") if validated else ""
    notify_frontend(curated_object_name=curated_key)
    log.info("[notify] Notification envoyée — curated : %s", curated_key)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# TÂCHE 8 — cleanup_tmp  (NOUVEAUTÉ J3)
# Supprime le fichier temporaire /tmp — toujours exécutée (succès ou échec)
# ═══════════════════════════════════════════════════════════════════════════════
def cleanup_task(**context) -> None:
    file_info = context["ti"].xcom_pull(task_ids="ingest_document")
    if not file_info:
        log.warning("[cleanup] Aucune info ingest — rien à nettoyer.")
        return
    local_tmp = file_info.get("local_tmp")
    if local_tmp and os.path.exists(local_tmp):
        os.remove(local_tmp)
        log.info("[cleanup] /tmp nettoyé : %s", local_tmp)
 
 
# ═══════════════════════════════════════════════════════════════════════════════
# DAG
# ═══════════════════════════════════════════════════════════════════════════════
 
default_args = {
    "owner":               "chaimae",
    "retries":             2,
    "retry_delay":         timedelta(minutes=5),
    "email_on_failure":    False,
    "email_on_retry":      False,
    "on_failure_callback": _send_alert,
}
 
with DAG(
    dag_id="document_pipeline",
    description="Pipeline OCR factures J3 — robustesse, retry, MinIO, monitoring",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
    tags=["document", "ocr", "minio", "hackathon", "j3"],
    max_active_runs=1,
) as dag:
 
    t0 = PythonOperator(task_id="get_file",          python_callable=get_latest_file)
    t1 = PythonOperator(task_id="ingest_document",   python_callable=ingest_task)
    t2 = PythonOperator(task_id="run_ocr",           python_callable=ocr_task)
    t3 = PythonOperator(task_id="extract_entities",  python_callable=extract_task)
    t4 = PythonOperator(task_id="validate_document", python_callable=validate_task)
    t5 = PythonOperator(task_id="store_curated",     python_callable=store_task)
    t6 = PythonOperator(task_id="notify_frontend",   python_callable=notify_task)
 
    t7 = PythonOperator(
        task_id="cleanup_tmp",
        python_callable=cleanup_task,
        trigger_rule=TriggerRule.ALL_DONE,  # S'exécute même si le pipeline échoue
    )
 
    t0 >> t1 >> t2 >> t3 >> t4 >> t5 >> t6 >> t7
    t1 >> t7   # cleanup aussi si ingest échoue (fichier /tmp déjà créé)