from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from rules import (
    check_format_siret,
    check_luhn_siret,
    check_arithmetic,
    check_tva,
    check_attestation_expired,
    check_siret_mismatch,
    check_doublon,
)
from scorer import build_result
from predict import predict
from features import extract_features

app = FastAPI()


class DocumentData(BaseModel):
    doc_id: str
    doc_type: str
    fichier: Optional[str] = None
    vendeur: Optional[str] = None
    siret: Optional[str] = None
    siren: Optional[str] = None
    tva: Optional[str] = None
    total_ht: Optional[float] = None
    tva_montant: Optional[float] = None
    total_ttc: Optional[float] = None
    date_expiration: Optional[str] = None


@app.post("/validate")
def validate(doc: DocumentData):
    anomalies = []

    def add(rule, severity, message):
        anomalies.append({"rule": rule, "severity": severity, "message": message})

    msg = check_format_siret(doc.siret)
    if msg:
        add("FORMAT_SIRET", "CRITICAL", msg)

    if not any(a["rule"] == "FORMAT_SIRET" for a in anomalies):
        msg = check_luhn_siret(doc.siret)
        if msg:
            add("LUHN_SIRET", "CRITICAL", msg)

    msg = check_arithmetic(doc.total_ht, doc.tva_montant, doc.total_ttc)
    if msg:
        add("ARITHMETIC_ERROR", "HIGH", msg)

    msg = check_tva(doc.tva, doc.siren)
    if msg:
        add("TVA_INVALIDE", "HIGH", msg)

    if doc.doc_type == "attestation":
        msg = check_attestation_expired(doc.date_expiration)
        if msg:
            add("ATTESTATION_EXPIRED", "HIGH", msg)

    if doc.doc_type == "facture" and doc.fichier and doc.siret:
        msg = check_siret_mismatch(doc.fichier, doc.siret)
        if msg:
            add("SIRET_MISMATCH", "CRITICAL", msg)

    if (
        doc.doc_type == "facture"
        and doc.fichier
        and doc.vendeur
        and doc.total_ttc is not None
    ):
        msg = check_doublon(doc.fichier, doc.vendeur, doc.total_ttc)
        if msg:
            add("DOUBLON_FACTURE", "CRITICAL", msg)

    features = extract_features(
        {
            "total_ht": doc.total_ht,
            "tva": doc.tva_montant,
            "total_ttc": doc.total_ttc,
            "taux_tva": (
                round(doc.tva_montant / doc.total_ht, 2)
                if doc.total_ht and doc.tva_montant
                else 0
            ),
        }
    )
    if doc.doc_type == "facture":
        ml_score = predict(features)
        if ml_score > 0:
            add("ML_ANOMALY", "MEDIUM", f"Score d'anomalie AdaBoost : {ml_score}/40")

    return build_result(doc.doc_id, anomalies)


@app.get("/health")
def health():
    return {"status": "ok"}
