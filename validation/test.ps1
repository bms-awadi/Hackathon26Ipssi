# Status du serveur
Invoke-RestMethod -Uri "http://localhost:8001/health"

# Document propre
Invoke-RestMethod -Method POST -Uri "http://localhost:8001/validate" `
  -ContentType "application/json" `
  -Body '{
    "doc_id": "001",
    "doc_type": "facture",
    "siret": "84490681378609",
    "siren": "844906813",
    "tva": "FR65844906813",
    "total_ht": 1500,
    "tva_montant": 300,
    "total_ttc": 1800
  }' | ConvertTo-Json -Depth 5

# Erreur de calcul
Invoke-RestMethod -Method POST -Uri "http://localhost:8001/validate" `
  -ContentType "application/json" `
  -Body '{
    "doc_id": "002",
    "doc_type": "facture",
    "siret": "84490681378609",
    "siren": "844906813",
    "total_ht": 1500,
    "tva_montant": 300,
    "total_ttc": 1900
  }' | ConvertTo-Json -Depth 5

# SIRET mismatch inter-document
Invoke-RestMethod -Method POST -Uri "http://localhost:8001/validate" `
  -ContentType "application/json" `
  -Body '{
    "doc_id": "004",
    "doc_type": "facture",
    "fichier": "facture_legit_0001.pdf",
    "vendeur": "Air France",
    "siret": "35291848960021",
    "siren": "352918489",
    "total_ht": 1920,
    "tva_montant": 384,
    "total_ttc": 2304
  }' | ConvertTo-Json -Depth 5

# Doublon facture
Invoke-RestMethod -Method POST -Uri "http://localhost:8001/validate" `
  -ContentType "application/json" `
  -Body '{
    "doc_id": "005",
    "doc_type": "facture",
    "fichier": "facture_legit_0003.pdf",
    "vendeur": "Orange",
    "siret": "84490681378609",
    "total_ht": 3160,
    "tva_montant": 632,
    "total_ttc": 3792
  }' | ConvertTo-Json -Depth 5

# Attestation expirée
Invoke-RestMethod -Method POST -Uri "http://localhost:8001/validate" `
  -ContentType "application/json" `
  -Body '{
    "doc_id": "006",
    "doc_type": "attestation",
    "siret": "84490681378609",
    "date_expiration": "2023-01-01"
  }' | ConvertTo-Json -Depth 5