import logging
import urllib.request
import json
import os
from datetime import datetime

log = logging.getLogger(__name__)

VALIDATION_URL = os.environ.get("VALIDATION_URL", "http://validation:8001")

def validate_document(data: dict) -> dict:
    entities = data.get("entities", {})
    sirets = entities.get("sirets", [])
    siret = sirets[0] if sirets else None

    # Mapping extract.py → format attendu
    payload = {
        "doc_id":          data.get("file_path", "unknown").split("/")[-1],
        "doc_type":        "facture",
        "fichier":         data.get("file_path", "").split("/")[-1],
        "vendeur":         entities.get("raison_sociale") or None,
        "siret":           siret,
        "siren":           siret[:9] if siret else None,
        "tva":             entities.get("tva_intracommunautaire") or None,
        "total_ht":        entities.get("montant_ht"),
        "tva_montant":     entities.get("montant_tva"),
        "total_ttc":       entities.get("montant_ttc"),
        "date_expiration": None,
    }

    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{VALIDATION_URL}/validate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            log.info("[validate] status=%s score=%s", result.get("status"), result.get("risk_score"))

            return {
                **data,
                "source_file":         data.get("file_path") or data.get("path"),
                "curated_object_name": f"curated_{payload['doc_id']}.json",
                "ocr_confidence":      data.get("confidence_score"),
                "processed_at":        datetime.now().isoformat(),
                "validation": {
                    "status":   result.get("status"),
                    "errors":   [a["message"] for a in result.get("anomalies", [])],
                    "warnings": [],
                },
                "anomalies":  result.get("anomalies", []),
                "risk_score": result.get("risk_score", 0),
            }

    except Exception as e:
        log.warning("[validate] Service injoignable (%s)", e)

        errors = []
        if not siret:
            errors.append("SIRET manquant")
        return {
            **data,
            "source_file":         data.get("file_path"),
            "curated_object_name": f"curated_{payload['doc_id']}.json",
            "ocr_confidence":      data.get("confidence_score"),
            "processed_at":        datetime.now().isoformat(),
            "validation": {
                "status":   "invalid" if errors else "valid",
                "errors":   errors,
                "warnings": ["Service de validation injoignable"],
            },
            "anomalies":  [],
            "risk_score": 0,
        }