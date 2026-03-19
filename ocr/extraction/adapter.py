"""
Adapte le format Contract produit par ocr_extraction
vers le format attendu par le service de validation.

Format entrant (Contract) :
    document_id, document_type, siret, tva_intracommunautaire,
    montant_ht, montant_ttc, date_emission, date_expiration,
    confidence_score, raw_text

Format sortant (Validation) :
    doc_id, doc_type, fichier, siret, siren, tva,
    total_ht, tva_montant, total_ttc, date_expiration
"""

import os

DOC_TYPE_MAP = {
    "facture_fournisseur": "facture",
    "attestation_urssaf": "attestation",
    "attestation_siret": "attestation",
    "devis": "devis",
    "kbis": "kbis",
    "rib": "rib",
}


def to_validation_payload(contract: dict, fichier: str) -> dict:
    siret = contract.get("siret") or None
    siren = siret[:9] if siret and len(siret) >= 9 else None
    total_ht = contract.get("montant_ht")
    total_ttc = contract.get("montant_ttc")

    tva_montant = None
    if total_ht is not None and total_ttc is not None:
        tva_montant = round(total_ttc - total_ht, 2)

    doc_type_raw = contract.get("document_type", "")
    doc_type = DOC_TYPE_MAP.get(doc_type_raw.lower(), "facture")

    return {
        "doc_id": contract.get(
            "document_id", os.path.splitext(os.path.basename(fichier))[0]
        ),
        "doc_type": doc_type,
        "fichier": os.path.basename(fichier),
        "siret": siret,
        "siren": siren,
        "tva": contract.get("tva_intracommunautaire") or None,
        "total_ht": total_ht,
        "tva_montant": tva_montant,
        "total_ttc": total_ttc,
        "date_expiration": contract.get("date_expiration") or None,
    }
