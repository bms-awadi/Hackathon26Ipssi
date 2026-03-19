from dataclasses import dataclass
from typing import Optional


@dataclass
class Contract:
    document_id: str
    document_type: str
    siret: str
    tva_intracommunautaire: str
    montant_ht: Optional[float]
    montant_ttc: Optional[float]
    date_emission: Optional[str]
    date_expiration: Optional[str]
    confidence_score: float
    raw_text: str

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "document_type": self.document_type,
            "siret": self.siret,
            "tva_intracommunautaire": self.tva_intracommunautaire,
            "montant_ht": self.montant_ht,
            "montant_ttc": self.montant_ttc,
            "date_emission": self.date_emission,
            "date_expiration": self.date_expiration,
            "confidence_score": self.confidence_score,
            "raw_text": self.raw_text,
        }


def compute_contract_confidence(
    ocr_confidence: float,
    siret: str,
    tva_intracommunautaire: str,
    montant_ht: Optional[float],
    montant_ttc: Optional[float],
    date_emission: Optional[str],
    date_expiration: Optional[str],
) -> float:
    """
    Score [0..1] derive :
    - moyenne de confiance OCR
    - bonus sur la presence des champs "majeurs"
    """
    base = max(0.0, min(1.0, float(ocr_confidence or 0.0)))

    parts = 0
    total = 6
    if siret:
        parts += 1
    if tva_intracommunautaire:
        parts += 1
    if montant_ht is not None:
        parts += 1
    if montant_ttc is not None:
        parts += 1
    if date_emission is not None:
        parts += 1
    # expiration est parfois absente selon le doc
    if date_expiration is not None:
        parts += 1

    entity_factor = parts / float(total)
    # On garde un melange simple.
    score = 0.7 * base + 0.3 * entity_factor
    return round(max(0.0, min(1.0, score)), 3)

