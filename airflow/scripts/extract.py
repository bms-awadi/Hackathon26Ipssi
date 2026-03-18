import logging
import re
from typing import Optional
 
log = logging.getLogger(__name__)
 
 
# Patterns regex
_SIRET_RE         = re.compile(r'\b(\d{3}[\s.]?\d{3}[\s.]?\d{3}[\s.]?\d{5})\b')
_IBAN_RE          = re.compile(r'\b([A-Z]{2}\d{2}[\s]?(?:[A-Z0-9]{4}[\s]?){3,7}[A-Z0-9]{1,4})\b')
_DATE_FR_RE       = re.compile(r'\b(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})\b')
_DATE_LONG_RE     = re.compile(
    r'\b(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|'
    r'octobre|novembre|décembre)\s+\d{4})\b', re.IGNORECASE
)
_MONTANT_RE       = re.compile(r'\b(\d{1,6}(?:[.,]\d{2,3})?)\s*(?:€|EUR|euros?)\b', re.IGNORECASE)
_PHONE_FR_RE      = re.compile(r'\b((?:0|\+33)[1-9](?:[\s.\-]?\d{2}){4})\b')
_EMAIL_RE         = re.compile(r'\b([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})\b')
_FACTURE_NUM_RE   = re.compile(
    r'(?:facture|fact|invoice|n°|num[eé]ro)[^\w]*([A-Z0-9\-/]{3,20})', re.IGNORECASE
)
_RAISON_RE        = re.compile(
    r'(?:SARL|SAS|SA|SASU|EURL|SNC|GIE|EI|AUTO[\-\s]?ENTREPRENEUR)[^\n]{0,60}', re.IGNORECASE
)
 
# Labels fréquents pour les montants
_LABEL_HT_RE  = re.compile(r'(?:total\s+)?h\.?t\.?|hors\s+taxe', re.IGNORECASE)
_LABEL_TTC_RE = re.compile(r'(?:total\s+)?t\.?t\.?c\.?|toutes\s+taxes', re.IGNORECASE)
_LABEL_TVA_RE = re.compile(r't\.?v\.?a\.?|taxe', re.IGNORECASE)
 
 
def _clean_siret(raw: str) -> str:
    """Supprime les séparateurs pour obtenir 14 chiffres bruts."""
    return re.sub(r'[\s.]', '', raw)
 
 
def _clean_iban(raw: str) -> str:
    """Normalise l'IBAN en supprimant les espaces."""
    return re.sub(r'\s', '', raw).upper()
 
 
def _parse_amount(raw: str) -> Optional[float]:
    """Convertit une string montant en float."""
    try:
        return float(raw.replace(' ', '').replace(',', '.'))
    except (ValueError, AttributeError):
        return None
 
 
def _extract_montants(text: str) -> dict:
    """
    Tente d'associer les montants trouvés aux labels HT / TVA / TTC.
    Stratégie : cherche le label sur la même ligne que le montant.
    """
    result = {"montant_ht": None, "montant_tva": None, "montant_ttc": None, "taux_tva": None}
 
    for line in text.splitlines():
        amounts_in_line = _MONTANT_RE.findall(line)
        if not amounts_in_line:
            continue
        amount = _parse_amount(amounts_in_line[-1])   # dernier montant de la ligne
        if amount is None:
            continue
 
        if _LABEL_TTC_RE.search(line):
            result["montant_ttc"] = amount
        elif _LABEL_HT_RE.search(line):
            result["montant_ht"] = amount
        elif _LABEL_TVA_RE.search(line):
            result["montant_tva"] = amount
            # Tentative de déduction du taux TVA (ex: "TVA 20%")
            taux_match = re.search(r'(\d{1,2}(?:[.,]\d+)?)\s*%', line)
            if taux_match:
                result["taux_tva"] = _parse_amount(taux_match.group(1))
 
    return result
 
 
def extract_entities(text: str) -> dict:
    """
    Extraction principale — appelée par la tâche Airflow.
 
    Args:
        text : texte brut retourné par run_ocr()
 
    Returns:
        dict conforme au schéma JSON signé avec Awadi.
    """
    if not text or not text.strip():
        raise ValueError("Texte vide — extraction impossible.")
 
    #SIRET 
    raw_sirets = _SIRET_RE.findall(text)
    sirets     = list(dict.fromkeys(_clean_siret(s) for s in raw_sirets))  # déduplique
 
    #IBAN
    raw_ibans = _IBAN_RE.findall(text)
    ibans     = list(dict.fromkeys(_clean_iban(i) for i in raw_ibans))
 
    #Raison sociale
    raison_matches = _RAISON_RE.findall(text)
    raison_sociale = raison_matches[0].strip() if raison_matches else ""
 
    #Dates
    dates = _DATE_FR_RE.findall(text) + _DATE_LONG_RE.findall(text)
    dates = list(dict.fromkeys(dates))
 
    #Numéro de facture
    facture_matches = _FACTURE_NUM_RE.findall(text)
    numero_facture  = facture_matches[0] if facture_matches else ""
 
    #Montants
    montants = _extract_montants(text)
 
    # Contacts
    emails = list(dict.fromkeys(_EMAIL_RE.findall(text)))
    phones = list(dict.fromkeys(_PHONE_FR_RE.findall(text)))
 
    result = {
        "entities": {
            "sirets":         sirets,
            "ibans":          ibans,
            "raison_sociale": raison_sociale,
            "dates":          dates,
            "numero_facture": numero_facture,
            "montant_ht":     montants["montant_ht"],
            "montant_tva":    montants["montant_tva"],
            "montant_ttc":    montants["montant_ttc"],
            "taux_tva":       montants["taux_tva"],
            "emails":         emails,
            "phones":         phones,
        },
        "word_count": len(text.split()),
        "char_count":  len(text),
        "raw_text":    text,
    }
 
    log.info(
        "[extract] SIRET=%s | IBAN=%s | TTC=%s | TVA=%s",
        sirets[:1], ibans[:1],
        montants["montant_ttc"], montants["montant_tva"],
    )
    return result