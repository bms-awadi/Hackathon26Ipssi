import logging
import os
import urllib.request
import json
 
log = logging.getLogger(__name__)
 
# URL du backend Node.js — définie dans docker-compose via variable d'env
BACKEND_URL = os.environ.get("BACKEND_API_URL", "http://backend:3000")
 
 
def notify_frontend(curated_object_name: str = "") -> None:
    """
    Envoie un POST au backend Node.js pour signaler qu'un document est traité.
 
    Payload envoyé :
        {
          "status": "done",
          "curated_object_name": "facture_001_curated.json",
          "bucket": "curated",
          "timestamp": "2026-03-05T14:30:00"
        }
    """
    from datetime import datetime
 
    payload_dict = {
        "status":               "done",
        "curated_object_name":  curated_object_name,
        "bucket":               os.environ.get("MINIO_BUCKET_CURATED", "curated"),
        "timestamp":            datetime.now().isoformat(),
    }
    payload = json.dumps(payload_dict).encode("utf-8")
 
    notify_url = f"{BACKEND_URL}/api/pipeline/done"
    log.info("[notify] POST vers %s — payload : %s", notify_url, payload_dict)
 
    try:
        req = urllib.request.Request(
            notify_url,
            data=payload,
            headers={
                "Content-Type":   "application/json",
                "Content-Length": str(len(payload)),
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            log.info("[notify] Réponse backend : %s — %s", resp.status, body[:200])
 
    except urllib.error.URLError as e:
        # On log l'erreur mais on ne fait pas échouer la tâche Airflow
        # Le pipeline est terminé — une notification ratée ne doit pas annuler le résultat
        log.warning(
            "[notify] Backend injoignable (%s). "
            "Le JSON curated est bien dans MinIO mais le frontend n'a pas été notifié.",
            e,
        )
 
    # Fallback : écriture d'un fichier de statut local
    _write_status_file(payload_dict)
 
 
def _write_status_file(payload: dict) -> None:
    """Écrit un fichier de statut en backup ."""
    status_dir  = "/opt/airflow/data/output"
    status_path = os.path.join(status_dir, "pipeline_status.jsonl")
    os.makedirs(status_dir, exist_ok=True)
    try:
        with open(status_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
        log.info("[notify] Statut écrit dans %s", status_path)
    except Exception as e:
        log.warning("[notify] Impossible d'écrire le fichier statut : %s", e)