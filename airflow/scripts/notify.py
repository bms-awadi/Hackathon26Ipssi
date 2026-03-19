import logging
import os
import urllib.request
import json
 
log = logging.getLogger(__name__)

BACKEND_URL = os.environ.get("BACKEND_API_URL", "http://back:3001")
 
 
def notify_frontend(validated_data: dict, document_id: str = "") -> None:
    from datetime import datetime

    entities = validated_data.get("entities", {}) if validated_data else {}
    sirets = entities.get("sirets", [])
    anomalies = validated_data.get("anomalies", []) if validated_data else []

    payload_dict = {
        "document_id": document_id,
        "status": "done",
        "curated_object_key": validated_data.get("curated_object_name", "") if validated_data else "",
        "ocr_confidence": validated_data.get("ocr_confidence", 0.0) if validated_data else 0.0,
        "contract": {
            "siret": sirets[0] if sirets else None,
            "raison_sociale": entities.get("raison_sociale", ""),
            "emails": entities.get("emails", []),
            "ibans": entities.get("ibans", []),
            "montant_ht": entities.get("montant_ht"),
            "montant_tva": entities.get("montant_tva"),
            "montant_ttc": entities.get("montant_ttc")
        },
        "anomalies": [a.get("message", str(a)) if isinstance(a, dict) else str(a) for a in anomalies]
    }
    
    payload = json.dumps(payload_dict).encode("utf-8")
    notify_url = f"{BACKEND_URL}/api/pipeline/done"
    log.info("[notify] POST vers %s — payload : %s", notify_url, payload_dict)

    try:
        req = urllib.request.Request(
            notify_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            log.info("[notify] Réponse backend : %s", resp.status)
    except Exception as e:
        log.warning("[notify] Backend injoignable (%s)", e)

    _write_status_file(payload_dict)
 
 
def _write_status_file(payload: dict) -> None:
    status_dir  = "/opt/airflow/data/output"
    status_path = os.path.join(status_dir, "pipeline_status.jsonl")
    os.makedirs(status_dir, exist_ok=True)
    try:
        with open(status_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception as e:
        pass