"""
Test du pipeline complet :
OCR (ocr_extraction) -> adaptation du format -> Validation (:8001)
"""

import json
import os
import sys
import requests

sys.path.insert(0, os.path.abspath("."))

from ocr.extraction.pipeline import extract_from_local_file
from ocr.extraction.adapter import to_validation_payload

VALIDATION_URL = "http://localhost:8001/validate"

FILES = [
    ("datasets/output/train/legitimes/facture_legit_0001.pdf", "facture_fournisseur"),
    ("datasets/output/train/legitimes/facture_legit_0002.pdf", "facture_fournisseur"),
    (
        "datasets/output/train/legitimes/attestation_legit_0001.pdf",
        "attestation_urssaf",
    ),
    ("datasets/output/train/falsifies/facture_falsif_0001.pdf", "facture_fournisseur"),
    ("datasets/output/train/falsifies/facture_falsif_0002.pdf", "facture_fournisseur"),
    ("datasets/output/train/falsifies/facture_falsif_0003.pdf", "facture_fournisseur"),
]


def adapter_format(contract: dict, fichier: str) -> dict:
    """
    Adapte le format Contract de l'equipe OCR
    vers le format attendu par le service de validation.
    """
    total_ht = contract.get("montant_ht")
    total_ttc = contract.get("montant_ttc")

    tva_montant = None
    if total_ht is not None and total_ttc is not None:
        tva_montant = round(total_ttc - total_ht, 2)

    return {
        "doc_id": contract.get("document_id", fichier),
        "doc_type": _map_doc_type(contract.get("document_type", "")),
        "fichier": os.path.basename(fichier),
        "siret": contract.get("siret"),
        "siren": contract.get("siret", "")[:9] if contract.get("siret") else None,
        "tva": contract.get("tva_intracommunautaire"),
        "total_ht": total_ht,
        "tva_montant": tva_montant,
        "total_ttc": total_ttc,
        "date_expiration": contract.get("date_expiration"),
    }


def _map_doc_type(doc_type: str) -> str:
    mapping = {
        "facture_fournisseur": "facture",
        "attestation_urssaf": "attestation",
        "devis": "devis",
        "kbis": "kbis",
        "rib": "rib",
    }
    return mapping.get(doc_type.lower(), "facture")


def run():
    print("Test pipeline OCR -> Validation")
    print("=" * 60)

    for file_path, doc_type in FILES:
        filename = os.path.basename(file_path)
        print(f"\nFichier : {filename}")

        # Etape 1 — OCR
        try:
            contract = extract_from_local_file(
                file_path=file_path,
                document_id=os.path.splitext(filename)[0],
                document_type=doc_type,
            )
            siret = contract.get("siret", "None")
            ttc = contract.get("montant_ttc", "None")
            conf = contract.get("confidence_score", 0)
            print(
                f"  OCR        : {doc_type} | SIRET {siret} | TTC {ttc} | confiance {conf:.2f}"
            )
        except Exception as e:
            print(f"  OCR        : ERREUR — {e}")
            continue

        # Etape 2 — Adaptation du format
        payload = to_validation_payload(contract, file_path)

        # Etape 3 — Validation
        try:
            r = requests.post(VALIDATION_URL, json=payload)
            r.raise_for_status()
            result = r.json()
            anomalies = [a["rule"] for a in result.get("anomalies", [])]
            print(
                f"  Validation : score={result['risk_score']} | statut={result['status']}",
                end="",
            )
            if anomalies:
                print(f" | {anomalies}")
            else:
                print()
        except Exception as e:
            print(f"  Validation : ERREUR — {e}")


if __name__ == "__main__":
    run()
