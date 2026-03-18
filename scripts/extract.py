import re
import json

def extract_entities():
    with open("data/clean/text.txt") as f:
        text = f.read()

    data = {}

    # SIRET (14 chiffres)
    siret = re.findall(r"\b\d{14}\b", text)
    data["siret"] = siret[0] if siret else None

    # TVA (FR + chiffres)
    tva = re.findall(r"FR\d+", text)
    data["tva"] = tva[0] if tva else None

    # Montant
    montant = re.findall(r"\d+[\.,]?\d*\s?€", text)
    data["montant"] = montant[0] if montant else None

    # Date
    date = re.findall(r"\d{4}-\d{2}-\d{2}", text)
    data["date"] = date[0] if date else None

    with open("data/clean/data.json", "w") as f:
        json.dump(data, f, indent=4)

    print(" Data extracted:", data)