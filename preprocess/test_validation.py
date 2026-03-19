import requests

URL = "http://localhost:8001/validate"


def validate(payload):
    r = requests.post(URL, json=payload)
    r.raise_for_status()
    return r.json()


def afficher(label, result):
    anomalies = [a["rule"] for a in result.get("anomalies", [])]
    print(f"  {label}")
    print(f"    score={result['risk_score']} | statut={result['status']}", end="")
    if anomalies:
        print(f" | {anomalies}")
    else:
        print()


def separateur(titre):
    print(f"\n{'='*55}")
    print(f"  {titre}")
    print(f"{'='*55}")


# ── Cas 1 : Document propre ───────────────────────────────────
separateur("CAS 1 — Document propre")
r = validate(
    {
        "doc_id": "001",
        "doc_type": "facture",
        "siret": "44829292000015",
        "siren": "448292920",
        "tva": "FR59448292920",
        "total_ht": 1500.0,
        "tva_montant": 300.0,
        "total_ttc": 1800.0,
    }
)
afficher("SIRET valide + TVA correcte + montants OK → CLEAN attendu", r)

# ── Cas 2 : Format SIRET incorrect ───────────────────────────
separateur("CAS 2 — Format SIRET incorrect")
r = validate(
    {
        "doc_id": "002",
        "doc_type": "facture",
        "siret": "1234",
    }
)
afficher("SIRET trop court → FORMAT_SIRET attendu", r)

# ── Cas 3 : SIRET echoue Luhn ────────────────────────────────
separateur("CAS 3 — SIRET invalide Luhn")
r = validate(
    {
        "doc_id": "003",
        "doc_type": "facture",
        "siret": "35291840035021",
        "siren": "352918400",
    }
)
afficher("SIRET incorrect → LUHN_SIRET attendu", r)

# ── Cas 4 : Erreur arithmetique ──────────────────────────────
separateur("CAS 4 — Erreur arithmetique")
r = validate(
    {
        "doc_id": "004",
        "doc_type": "facture",
        "siret": "44829292000015",
        "siren": "448292920",
        "total_ht": 1500.0,
        "tva_montant": 300.0,
        "total_ttc": 1999.0,
    }
)
afficher("HT+TVA=1800 mais TTC=1999 → ARITHMETIC_ERROR attendu", r)

# ── Cas 5 : TVA invalide ─────────────────────────────────────
separateur("CAS 5 — TVA invalide")
r = validate(
    {
        "doc_id": "005",
        "doc_type": "facture",
        "siret": "44829292000015",
        "siren": "448292920",
        "tva": "FR99448292920",
    }
)
afficher("Cle TVA incorrecte → TVA_INVALIDE attendu", r)

# ── Cas 6 : Attestation expiree ──────────────────────────────
separateur("CAS 6 — Attestation expiree")
r = validate(
    {
        "doc_id": "006",
        "doc_type": "attestation",
        "siret": "44829292000015",
        "date_expiration": "2022-01-01",
    }
)
afficher("Date expiration 2022 → ATTESTATION_EXPIRED attendu", r)

# ── Cas 7 : Attestation valide ───────────────────────────────
separateur("CAS 7 — Attestation valide")
r = validate(
    {
        "doc_id": "007",
        "doc_type": "attestation",
        "siret": "44829292000015",
        "siren": "448292920",
        "tva": "FR59448292920",
        "date_expiration": "2027-01-01",
    }
)
afficher("Date expiration 2027 → CLEAN attendu", r)

# ── Cas 8 : SIRET mismatch inter-documents ───────────────────
separateur("CAS 8 — SIRET mismatch inter-documents")
# facture_legit_0001.pdf est liee a attestation_legit_0001.pdf
# dont le siret est 18201005800028
# on envoie un SIRET different pour declencher le mismatch
r = validate(
    {
        "doc_id": "008",
        "doc_type": "facture",
        "fichier": "facture_legit_0001.pdf",
        "siret": "44829292000015",
        "siren": "448292920",
        "total_ht": 1500.0,
        "tva_montant": 300.0,
        "total_ttc": 1800.0,
    }
)
afficher("SIRET 44829292000015 != SIRET attestation liee → SIRET_MISMATCH attendu", r)

# ── Cas 9 : Doublon facture ──────────────────────────────────
separateur("CAS 9 — Doublon facture")
# facture_legit_0001.pdf a total_ttc=4224.0 vendeur=CHAMBRE REGIONALE D'AGRICULTURE CORSE
# on envoie facture_legit_0002.pdf avec le meme vendeur et meme TTC
r = validate(
    {
        "doc_id": "009",
        "doc_type": "facture",
        "fichier": "facture_legit_0002.pdf",
        "vendeur": "CHAMBRE REGIONALE D'AGRICULTURE CORSE",
        "siret": "44829292000015",
        "total_ht": 3520.0,
        "tva_montant": 704.0,
        "total_ttc": 4224.0,
    }
)
afficher("Meme vendeur + TTC 4224 que facture_legit_0001 → DOUBLON attendu", r)

# ── Cas 10 : Cumul de fraudes ────────────────────────────────
separateur("CAS 10 — Cumul de fraudes")
r = validate(
    {
        "doc_id": "010",
        "doc_type": "facture",
        "siret": "35291840035021",
        "siren": "352918400",
        "tva": "FR99352918400",
        "total_ht": 1500.0,
        "tva_montant": 750.0,
        "total_ttc": 2999.0,
    }
)
afficher("LUHN + TVA + ARITHMETIC + ML → FRAUD score max attendu", r)

print()
