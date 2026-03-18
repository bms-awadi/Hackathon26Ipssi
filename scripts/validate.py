import json

def validate_document():
    with open("data/clean/data.json") as f:
        data = json.load(f)

    errors = []

    if not data["siret"]:
        errors.append("Missing SIRET")

    if not data["montant"]:
        errors.append("Missing montant")

    if errors:
        print("Validation errors:", errors)
    else:
        print("Document valid")

    return errors