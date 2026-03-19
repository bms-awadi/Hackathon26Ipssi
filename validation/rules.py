import json
import os
from datetime import date
from config import TOLERANCE_ARITHMETIQUE

LABELS_PATH = os.path.join(os.path.dirname(__file__), "..", "output", "labels.json")


def load_labels():
    if not os.path.exists(LABELS_PATH):
        return {}
    with open(LABELS_PATH, encoding="utf-8") as f:
        return json.load(f)


# Verificationt format SIRET
def check_format_siret(siret):
    if not siret:
        return "SIRET absent"
    if not siret.isdigit():
        return f"SIRET contient des caracteres non numeriques : {siret}"
    if len(siret) != 14:
        return f"SIRET doit contenir 14 chiffres, recu {len(siret)} : {siret}"
    return None


# Verification SIRET avec algorithme de Luhn
def check_luhn_siret(siret):
    if not siret or not siret.isdigit() or len(siret) != 14:
        return None
    total = 0
    for i, digit in enumerate(siret):
        n = int(digit)
        if i % 2 == 0:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    if total % 10 != 0:
        return f"SIRET invalide selon algorithme de Luhn : {siret}"
    return None


# Verification de l'arithmetique : total_ttc = total_ht + tva (avec une tolerance pour les arrondis)
def check_arithmetic(total_ht, tva, total_ttc):
    if total_ht is None or tva is None or total_ttc is None:
        return None
    expected = round(total_ht + tva, 2)
    if abs(expected - total_ttc) > TOLERANCE_ARITHMETIQUE:
        return f"HT {total_ht} + TVA {tva} = {expected} mais TTC affiche {total_ttc}"
    return None


# Verification du format de la TVA et de sa cle
def check_tva(tva, siren):
    if not tva or not siren:
        return None
    tva_clean = tva.replace(" ", "")
    if not tva_clean.startswith("FR"):
        return f"TVA ne commence pas par FR : {tva}"
    if len(tva_clean) != 13:
        return f"TVA doit contenir 13 caracteres, recu {len(tva_clean)} : {tva}"
    siren_int = int(siren)
    cle_attendue = (12 + 3 * (siren_int % 97)) % 97
    try:
        cle_doc = int(tva_clean[2:4])
    except ValueError:
        return f"Cle TVA non numerique : {tva_clean[2:4]}"
    if cle_doc != cle_attendue:
        return f"Cle TVA incorrecte : attendu {cle_attendue:02d}, recu {cle_doc}"
    return None


# Verification de la date d'expiration de l'attestation
def check_attestation_expired(date_expiration):
    if not date_expiration:
        return None
    if isinstance(date_expiration, str):
        date_expiration = date_expiration.split("T")[0]
        date_expiration = date.fromisoformat(date_expiration)
    if date_expiration < date.today():
        return f"Attestation expiree le {date_expiration.isoformat()}"
    return None


# verification de la correspondance du SIRET entre la facture et l'attestation liee
def check_siret_mismatch(fichier, siret_facture):
    labels = load_labels()
    doc = labels.get(fichier)
    if not doc:
        return None
    fichier_lie = doc.get("doc_lie")
    if not fichier_lie:
        return None
    doc_lie = labels.get(fichier_lie)
    if not doc_lie:
        return None
    siret_attestation = doc_lie.get("siret")
    if not siret_attestation:
        return None
    if siret_facture != siret_attestation:
        return f"SIRET facture {siret_facture} different du SIRET attestation {siret_attestation}"
    return None


# verification de doublon : meme vendeur et meme montant TTC dans une autre facture
def check_doublon(fichier, vendeur, total_ttc):
    labels = load_labels()
    for nom, doc in labels.items():
        if nom == fichier:
            continue
        if doc.get("type") != "facture":
            continue
        if doc.get("vendeur") != vendeur:
            continue
        if doc.get("total_ttc") is None:
            continue
        if abs(doc["total_ttc"] - total_ttc) < TOLERANCE_ARITHMETIQUE:
            return f"Doublon detecte avec {nom} : meme vendeur {vendeur} et meme montant TTC {total_ttc}"
    return None
