import re
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Tuple, List


_SIRET_RE = re.compile(r"\b(\d{3}[\s.]?\d{3}[\s.]?\d{3}[\s.]?\d{5})\b")
_TVA_RE = re.compile(r"\b(FR\d{11})\b", re.IGNORECASE)

# Montants avec separateurs simples; on normalise apres.
_AMOUNT_RE = re.compile(r"\b(\d{1,3}(?:[ \u00A0]\d{3})+|\d{1,6})(?:[.,](\d{2,3}))?\b")

_DATE_FR_RE = re.compile(r"\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})\b")

_MONTHS = {
    "janvier": 1,
    "février": 2,
    "fevrier": 2,
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


def _normalize_amount(raw: str) -> Optional[float]:
    if raw is None:
        return None
    s = str(raw).strip()
    # Enleve les espaces (incl. espace insécable)
    s = s.replace("\u00A0", " ").replace(" ", "")

    # Cas decimal avec virgule
    if "," in s and "." in s:
        # Probablement milliers avec '.' et decimal avec ','
        s = s.replace(".", "")
        s = s.replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    else:
        # garde '.' si present comme decimal
        pass

    try:
        return float(s)
    except Exception:
        return None


def _parse_dd_mm_yyyy(d: str, m: str, y: str) -> Optional[str]:
    try:
        day = int(d)
        month = int(m)
        yy = int(y)
        if yy < 100:
            # Heureux cas 2 chiffres (peu probable ici)
            yy = 2000 + yy
        dt = date(yy, month, day)
        return dt.isoformat()
    except Exception:
        return None


def _parse_date_candidates(text: str) -> List[str]:
    out = []
    for m in _DATE_FR_RE.finditer(text):
        iso = _parse_dd_mm_yyyy(m.group(1), m.group(2), m.group(3))
        if iso:
            out.append(iso)
    # Dates longues avec mois en toutes lettres
    # Exemple: "15 mars 2025"
    # On fait une extraction simple pour couvrir le cahier, pas un parse complet.
    month_pat = r"(\d{1,2})\s+(" + "|".join(_MONTHS.keys()) + r")\s+(\d{4})"
    month_re = re.compile(month_pat, flags=re.IGNORECASE)
    for m in month_re.finditer(text):
        day = int(m.group(1))
        mon_name = m.group(2).lower()
        yy = int(m.group(3))
        mon = _MONTHS.get(mon_name)
        if mon:
            try:
                out.append(date(yy, mon, day).isoformat())
            except Exception:
                continue
    # Dedup
    return list(dict.fromkeys(out))


def _find_labelled_amounts(lines: List[str]) -> Tuple[Optional[float], Optional[float]]:
    """
    Cherche montants HT/TTC a partir de labels dans les lignes.
    Strategie : pour chaque ligne qui contient un montant, on regarde si un label HT/TTC
    est present, et on associe le dernier montant trouve.
    """
    montant_ht = None
    montant_ttc = None

    for line in lines:
        lower = line.lower()
        # Detection labels
        is_ht = ("ht" in lower) or ("hors taxe" in lower) or ("hors-taxe" in lower)
        is_ttc = ("ttc" in lower) or ("toutes taxes" in lower) or ("toutes taxes comprises" in lower)

        # Montant(s) de la ligne
        amounts = []
        for m in _AMOUNT_RE.finditer(line.replace(",", ".")):
            # m.group(0) contient le nombre mais on normalise via groupe(1)+groupe(2)
            whole = m.group(1)
            dec = m.group(2)
            if dec:
                num = f"{whole}.{dec}"
            else:
                num = whole
            val = _normalize_amount(num)
            if val is not None:
                amounts.append(val)
        if not amounts:
            continue
        last_amt = amounts[-1]

        if is_ttc:
            montant_ttc = last_amt
        elif is_ht:
            montant_ht = last_amt

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
    """
    Extraction entites via segmentation spaCy (targeting) + regex par champ.
    """
    # spaCy : segmentation uniquement (les patterns restent regex, car le modele NER fr_core_news_lg
    # n'est pas specialise "SIRET/TVA/montants").
    try:
        import spacy

        try:
            nlp = spacy.load("fr_core_news_lg")
        except Exception:
            # fallback modele leger si pas present
            nlp = spacy.load("fr_core_news_sm")
    except Exception:
        nlp = None

    raw_text = text or ""

    # Lignes : extraction montants
    lines = raw_text.splitlines()

    # SIRET
    # On utilise spaCy si dispo pour parcourir les phrases.
    siret = ""
    tva_intracommunautaire = ""

    candidates_siret = []
    candidates_tva = []

    if nlp is not None:
        doc = nlp(raw_text)
        for sent in doc.sents:
            st = sent.text
            candidates_siret.extend([_clean_siret(x) for x in _SIRET_RE.findall(st)])
            candidates_tva.extend([x.upper() for x in _TVA_RE.findall(st)])
    else:
        candidates_siret = [_clean_siret(x) for x in _SIRET_RE.findall(raw_text)]
        candidates_tva = [x.upper() for x in _TVA_RE.findall(raw_text)]

    # Dedup en gardant l'ordre
    siret = list(dict.fromkeys(candidates_siret))[0] if candidates_siret else ""
    tva_intracommunautaire = (
        list(dict.fromkeys(candidates_tva))[0] if candidates_tva else ""
    )

    # Montants
    montant_ht, montant_ttc = _find_labelled_amounts(lines)

    # Dates
    # Emission : premiere date detectee.
    all_dates = _parse_date_candidates(raw_text)
    date_emission = all_dates[0] if all_dates else None

    # Expiration : cherche une date proche de mots-clés.
    date_expiration = None
    if document_type.lower().startswith("facture"):
        # Par defaut facture : pas forcement une expiration, on la laisse a None.
        pass

    kw = [
        "expiration",
        "expir",
        "echeance",
        "valable jusqu",
        "jusqu",
        "date d'expiration",
        "date_expiration",
    ]
    lower = raw_text.lower()
    if any(k in lower for k in kw):
        # On prend la premiere date apres un keyword (heuristique).
        # Pour rester simple/robuste, on scanne sur les lignes.
        for line in lines:
            if any(k in line.lower() for k in kw):
                ds = _parse_date_candidates(line)
                if ds:
                    date_expiration = ds[0]
                    break

    return ExtractedEntities(
        siret=siret,
        tva_intracommunautaire=tva_intracommunautaire,
        montant_ht=montant_ht,
        montant_ttc=montant_ttc,
        date_emission=date_emission,
        date_expiration=date_expiration,
        raw_text=raw_text,
    )

