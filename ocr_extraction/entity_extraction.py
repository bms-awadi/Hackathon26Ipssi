import re
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Tuple, List


_SIRET_RE = re.compile(r"\b(\d{3}[\s.]?\d{3}[\s.]?\d{3}[\s.]?\d{5})\b")
_TVA_RE = re.compile(r"\b(FR\s*\d{2}\s*\d{9})\b", re.IGNORECASE)

# Montant avec point ou virgule decimale + unite optionnelle EUR/€
_AMOUNT_RE = re.compile(
    r"\b(\d+(?:[.,]\d{2})?)\s*(?:EUR|€)",
    re.IGNORECASE,
)

# Labels pour montants HT et TTC par position dans le texte
_HT_LABEL_RE = re.compile(r"total\s+ht", re.IGNORECASE)
_TTC_LABEL_RE = re.compile(r"total\s+ttc", re.IGNORECASE)
_TVA_LABEL_RE = re.compile(r"\btva\b", re.IGNORECASE)

_DATE_FR_RE = re.compile(r"\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})\b")

_DATE_EXPIRATION_RE = re.compile(
    r"expir[^\d]*(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})",
    re.IGNORECASE,
)

_MONTHS = {
    "janvier": 1,
    "fevrier": 2,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12,
    "décembre": 12,
}


def _clean_siret(raw: str) -> str:
    return re.sub(r"[\s.]", "", raw)


def _parse_amount(s: str) -> Optional[float]:
    if not s:
        return None
    s = s.strip().replace("\u00a0", "").replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except Exception:
        return None


def _parse_dd_mm_yyyy(d: str, m: str, y: str) -> Optional[str]:
    try:
        day, month, yy = int(d), int(m), int(y)
        if yy < 100:
            yy += 2000
        return date(yy, month, day).isoformat()
    except Exception:
        return None


def _parse_date_candidates(text: str) -> List[str]:
    out = []
    for m in _DATE_FR_RE.finditer(text):
        iso = _parse_dd_mm_yyyy(m.group(1), m.group(2), m.group(3))
        if iso:
            out.append(iso)
    month_pat = r"(\d{1,2})\s+(" + "|".join(_MONTHS.keys()) + r")\s+(\d{4})"
    for m in re.finditer(month_pat, text, re.IGNORECASE):
        day = int(m.group(1))
        mon = _MONTHS.get(m.group(2).lower())
        yy = int(m.group(3))
        if mon:
            try:
                out.append(date(yy, mon, day).isoformat())
            except Exception:
                continue
    return list(dict.fromkeys(out))


def _find_labelled_amounts(lines: List[str]) -> Tuple[Optional[float], Optional[float]]:
    montant_ht = None
    montant_ttc = None

    for i, line in enumerate(lines):
        amounts = [_parse_amount(m.group(1)) for m in _AMOUNT_RE.finditer(line)]
        amounts = [a for a in amounts if a is not None and a > 0]

        # Si pas de montant sur cette ligne, chercher sur la ligne suivante
        if not amounts and i + 1 < len(lines):
            next_line = lines[i + 1]
            amounts = [
                _parse_amount(m.group(1)) for m in _AMOUNT_RE.finditer(next_line)
            ]
            amounts = [a for a in amounts if a is not None and a > 0]

        if not amounts:
            continue
        last = amounts[-1]

        if _TTC_LABEL_RE.search(line):
            montant_ttc = last
        elif _HT_LABEL_RE.search(line):
            montant_ht = last

    return montant_ht, montant_ttc


@dataclass
class ExtractedEntities:
    siret: str
    tva_intracommunautaire: str
    montant_ht: Optional[float]
    montant_ttc: Optional[float]
    date_emission: Optional[str]
    date_expiration: Optional[str]
    raw_text: str


def extract_entities_spacy_regex(
    text: str,
    document_type: str = "facture_fournisseur",
) -> ExtractedEntities:
    try:
        import spacy

        try:
            nlp = spacy.load("fr_core_news_lg")
        except Exception:
            nlp = spacy.load("fr_core_news_sm")
    except Exception:
        nlp = None

    raw_text = text or ""
    lines = raw_text.splitlines()

    candidates_siret = []
    candidates_tva = []

    if nlp is not None:
        doc = nlp(raw_text)
        for sent in doc.sents:
            st = sent.text
            candidates_siret.extend([_clean_siret(x) for x in _SIRET_RE.findall(st)])
            candidates_tva.extend(
                [x.replace(" ", "").upper() for x in _TVA_RE.findall(st)]
            )
    else:
        candidates_siret = [_clean_siret(x) for x in _SIRET_RE.findall(raw_text)]
        candidates_tva = [x.replace(" ", "").upper() for x in _TVA_RE.findall(raw_text)]

    siret = list(dict.fromkeys(candidates_siret))[0] if candidates_siret else ""
    tva_intracommunautaire = (
        list(dict.fromkeys(candidates_tva))[0] if candidates_tva else ""
    )

    montant_ht, montant_ttc = _find_labelled_amounts(lines)

    all_dates = _parse_date_candidates(raw_text)
    date_emission = all_dates[0] if all_dates else None
    date_expiration = None

    # Expiration : cherche par label "expir"
    m = _DATE_EXPIRATION_RE.search(raw_text)
    if m:
        date_expiration = _parse_dd_mm_yyyy(m.group(1), m.group(2), m.group(3))
    elif document_type not in ("facture_fournisseur", "devis"):
        # Fallback : deuxieme date trouvee pour attestations/kbis
        if len(all_dates) > 1:
            date_expiration = all_dates[1]

    return ExtractedEntities(
        siret=siret,
        tva_intracommunautaire=tva_intracommunautaire,
        montant_ht=montant_ht,
        montant_ttc=montant_ttc,
        date_emission=date_emission,
        date_expiration=date_expiration,
        raw_text=raw_text,
    )
