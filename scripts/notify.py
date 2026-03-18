import json
import requests

def notify_frontend():
    with open("data/curated/data.json") as f:
        data = json.load(f)

    print("Sending to CRM...")

    # simulation (remplace par vraie API)
    # requests.post("http://crm/api", json=data)

    print(" Sent:", data)