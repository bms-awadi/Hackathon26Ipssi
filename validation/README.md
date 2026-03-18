# Validation Dataset

Le sservice de validation reçoit les données extraites par l'OCR et décide si un document est sain,
suspect ou frauduleux. Il produit un score de risque entre 0 et 100 et une
liste d'anomalies détectées.

---

## Rôle dans le pipeline

```
OCR Service  →  Validation Service  →  Backend Node.js
             POST /validate              stockage MongoDB / data lake
             { entités extraites }       { score, statut, anomalies }
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Lancement

```bash
uvicorn main:app --port 8001 --reload
```

Swagger disponible sur : http://localhost:8001/docs

---

## Structure des fichiers

```
validation-service/
├── main.py          Point d'entrée FastAPI — orchestre tous les appels
├── rules.py         7 règles de validation (format, calcul, croisement)
├── scorer.py        Calcul du score de risque et du statut final
├── config.py        Poids des règles et seuils CLEAN / WARNING / FRAUD
├── features.py      Extraction des features pour le modèle ML
├── train.py         Entraînement du modèle AdaBoost sur le dataset
├── evaluate.py      Mesure de la performance du modèle
├── predict.py       Prédiction ML sur un document
├── best_model.pkl   Modèle entraîné (généré par train.py)
├── scaler.pkl       Normalisation des features (généré par train.py)
└── requirements.txt
```

---

## Les deux niveaux de validation

### Niveau 1 — Règles déterministes

Règles logiques appliquées sur les données extraites. Chaque règle retourne
un message d'erreur ou None si tout est correct.

| Règle | Ce qu'elle vérifie | Poids | Justification |
|---|---|---|---|
| FORMAT_SIRET | SIRET contient exactement 14 chiffres | 40 | Un SIRET mal formé ne peut pas être une faute de frappe. C'est soit un identifiant inventé, soit volontairement tronqué. Impact légal direct car le SIRET est obligatoire sur toute facture. |
| LUHN_SIRET | SIRET valide selon l'algorithme de Luhn | 40 | L'algorithme de Luhn est une vérification mathématique. Un SIRET qui échoue est forcément construit avec de faux chiffres. Personne ne fait ça involontairement. Même poids que FORMAT_SIRET car même nature : intentionnel et objectif. |
| ARITHMETIC_ERROR | HT + TVA = TTC (tolérance 0.01€) | 30 | Peut être une erreur de saisie ou une fraude. L'intention n'est pas certaine. Poids modéré : seul il ne bloque pas, il signale pour revue humaine. Deux anomalies de ce niveau ensemble passent en WARNING. |
| TVA_INVALIDE | Clé TVA intracommunautaire correcte | 30 | La clé TVA se calcule mathématiquement à partir du SIREN. Une clé fausse peut venir d'une TVA copiée d'une autre entreprise ou d'une erreur de saisie. Même ambiguïté que l'arithmétique, même poids. |
| ATTESTATION_EXPIRED | Date d'expiration non dépassée | 35 | Peut être un oubli administratif ou une tentative de faire passer un fournisseur non à jour URSSAF. Impact réglementaire : travailler avec un fournisseur non à jour engage la responsabilité de l'acheteur. Légèrement au dessus des erreurs de calcul. |
| SIRET_MISMATCH | SIRET facture = SIRET attestation liée | 50 | Deux documents du même fournisseur avec deux SIRET différents. Difficile d'expliquer par une erreur involontaire. L'un des deux documents est nécessairement faux. Impact direct sur la validité juridique de la relation commerciale. |
| DOUBLON_FACTURE | Pas de facture identique (même vendeur + même TTC) | 50 | Même vendeur, même montant, deux fichiers différents. Intention claire de double paiement. Impact financier direct et immédiat. Même poids que SIRET_MISMATCH car même niveau de certitude sur l'intention frauduleuse. |

### Niveau 2 — Détection ML (AdaBoost)

Modèle entraîné sur 1000 documents du dataset (500 légitimes, 500 falsifiés).
Il détecte les anomalies que les règles ne couvrent pas en analysant les
patterns des montants.

- Précision globale : 87.9%
- F1-score : 0.892
- Rappel : 1.000 (aucun légitime classé comme frauduleux)

Features utilisées :
- total_ht, tva, total_ttc, taux_tva, ratio_tva, ratio_ttc

Le score ML va de 0 à 40 et s'additionne au score des règles déterministes.

---

## Calcul du score de risque

On additionne les poids des règles qui échouent, plafonné à 100.

```
score = min(somme des poids des anomalies détectées, 100)
```

| Score | Statut | Action |
|---|---|---|
| 0 - 29 | CLEAN | Document accepté automatiquement |
| 30 - 69 | WARNING | Revue humaine recommandée |
| 70 - 100 | FRAUD | Document bloqué, alerte créée |

---

## Format des échanges

### Requête

```json
{
  "doc_id":          "facture_001",
  "doc_type":        "facture",
  "fichier":         "facture_legit_0001.pdf",
  "vendeur":         "Air France",
  "siret":           "35291840035021",
  "siren":           "352918400",
  "tva":             "FR48352918400",
  "total_ht":        1920.0,
  "tva_montant":     384.0,
  "total_ttc":       2304.0,
  "date_expiration": null
}
```

### Réponse

```json
{
  "doc_id":     "facture_001",
  "risk_score": 0,
  "status":     "CLEAN",
  "anomalies":  []
}
```

### Réponse avec anomalies

```json
{
  "doc_id":     "facture_002",
  "risk_score": 100,
  "status":     "FRAUD",
  "anomalies": [
    {
      "rule":     "SIRET_MISMATCH",
      "severity": "CRITICAL",
      "message":  "SIRET facture 35291848960021 different du SIRET attestation 35291840035021"
    },
    {
      "rule":     "DOUBLON_FACTURE",
      "severity": "CRITICAL",
      "message":  "Doublon detecte avec facture_legit_0002.pdf : meme vendeur Orange et meme montant TTC 3792.0"
    }
  ]
}
```

---

## Entraîner le modèle ML

A faire une seule fois avant de lancer le serveur, ou après avoir régénéré
le dataset.

```bash
python train.py
```

Pour mesurer la performance :

```bash
python evaluate.py
```

---

## Tester sans lancer le serveur

```bash
python -c "
from predict import predict
from features import extract_features

doc = {'total_ht': 1500, 'tva': 300, 'total_ttc': 1800, 'taux_tva': 0.2}
print(predict(extract_features(doc)))
"
```
