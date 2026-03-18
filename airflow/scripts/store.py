import json
import io
import logging
import os
from datetime import datetime
 
log = logging.getLogger(__name__)
 
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT",    "http://minio:9000")
MINIO_ACCESS   = os.environ.get("MINIO_ACCESS_KEY",  "minioadmin")
MINIO_SECRET   = os.environ.get("MINIO_SECRET_KEY",  "minioadmin")
BUCKET_CURATED = os.environ.get("MINIO_BUCKET_CURATED", "curated")
 
 
def _get_minio_client():
    from minio import Minio
    endpoint = MINIO_ENDPOINT.replace("http://", "").replace("https://", "")
    secure   = MINIO_ENDPOINT.startswith("https://")
    return Minio(endpoint, access_key=MINIO_ACCESS, secret_key=MINIO_SECRET, secure=secure)
 
 
def store_curated(data: dict) -> None:
    """
    Stocke et indexe les données validées.
 
    data est le dict retourné par validate_document(), enrichi du champ curated_object_name.
    """
    client = _get_minio_client()
 
    entities = data.get("entities", {})
    siret    = _first(entities.get("sirets", []))
    iban     = _first(entities.get("ibans",  []))
    raison   = entities.get("raison_sociale", "")
 
    # Mise à jour fiche fournisseur
    # Clé stable par SIRET : supplier_XXXXXXXXXXXXXXXXX.json
    if siret:
        supplier_key    = f"suppliers/supplier_{siret}.json"
        existing_fiche  = _load_existing(client, BUCKET_CURATED, supplier_key)
        updated_fiche   = _merge_fiche(existing_fiche, data, siret, iban, raison)
        _put_json(client, BUCKET_CURATED, supplier_key, updated_fiche)
        log.info("[store] Fiche fournisseur mise à jour : %s", supplier_key)
    else:
        log.warning("[store] Pas de SIRET détecté — fiche fournisseur non créée.")
 
    # Log d'audit horodaté 
    timestamp   = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    audit_key   = f"audit/audit_{timestamp}.json"
    audit_entry = {
        "timestamp":            datetime.now().isoformat(),
        "source_file":          data.get("source_file"),
        "curated_object_name":  data.get("curated_object_name"),
        "siret":                siret,
        "validation_status":    data.get("validation", {}).get("status"),
        "validation_warnings":  data.get("validation", {}).get("warnings", []),
        "anomalies":            data.get("anomalies", []),
        "ocr_confidence":       data.get("ocr_confidence"),
    }
    _put_json(client, BUCKET_CURATED, audit_key, audit_entry)
    log.info("[store] Log d'audit écrit : %s", audit_key)
 
 
# Helpers

def _first(lst: list):
    """Retourne le premier élément d'une liste, ou None."""
    return lst[0] if lst else None
 
 
def _load_existing(client, bucket: str, key: str) -> dict:
    """Charge un JSON existant depuis MinIO, ou retourne {} s'il n'existe pas."""
    try:
        resp = client.get_object(bucket, key)
        return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}
 
 
def _put_json(client, bucket: str, key: str, data: dict) -> None:
    """Écrit un dict JSON dans MinIO."""
    payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    client.put_object(
        bucket, key,
        data=io.BytesIO(payload), length=len(payload),
        content_type="application/json",
    )
 
 
def _merge_fiche(existing: dict, data: dict, siret: str, iban: str, raison: str) -> dict:
    """
    Fusionne les nouvelles données dans la fiche fournisseur existante.
    Les nouvelles valeurs écrasent les anciennes uniquement si non vides.
    """
    entities = data.get("entities", {})
    fiche    = dict(existing)
 
    fiche["siret"]         = siret
    fiche["raison_sociale"] = raison or fiche.get("raison_sociale", "")
    fiche["iban"]           = iban   or fiche.get("iban", "")
    fiche["emails"]         = entities.get("emails",  fiche.get("emails",  []))
    fiche["phones"]         = entities.get("phones",  fiche.get("phones",  []))
    fiche["last_updated"]   = datetime.now().isoformat()
 
    # Historique des factures associées à ce fournisseur
    history = fiche.get("invoice_history", [])
    history.append({
        "source_file":     data.get("source_file"),
        "curated_key":     data.get("curated_object_name"),
        "processed_at":    data.get("processed_at"),
        "ocr_confidence":  data.get("ocr_confidence"),
        "validation":      data.get("validation", {}).get("status"),
    })
    fiche["invoice_history"] = history[-50:]   # garde les 50 dernières entrées max
 
    return fiche