import logging

log = logging.getLogger(__name__)

def validate_document(data: dict) -> dict:
    errors = []
    entities = data.get("entities", {})

    sirets = entities.get("sirets", [])
    if not sirets:
        errors.append("SIRET manquant")
    elif len(sirets[0]) != 14:
        errors.append(f"SIRET invalide : {sirets[0]}")

    montant_ht  = entities.get("montant_ht")
    montant_ttc = entities.get("montant_ttc")
    taux_tva    = entities.get("taux_tva")

    if montant_ht and montant_ttc and taux_tva:
        ttc_calcule = round(montant_ht * (1 + taux_tva / 100), 2)
        if abs(ttc_calcule - montant_ttc) > 0.02:
            errors.append(f"Incohérence TVA : {ttc_calcule} ≠ {montant_ttc}")

    status = "valid" if not errors else "invalid"

    return {
        **data,
        "source_file":         data.get("file_path") or data.get("path"),
        "curated_object_name": f"curated_{data.get('file_path', 'unknown').split('/')[-1]}.json",
        "ocr_confidence":      data.get("confidence_score"),
        "processed_at":        __import__("datetime").datetime.now().isoformat(),
        "validation": {
            "status":   status,
            "errors":   errors,
            "warnings": [],
        }
    }