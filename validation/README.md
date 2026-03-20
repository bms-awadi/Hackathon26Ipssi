# Validation Service

Le service de validation reçoit les entités extraites par l'OCR et décide si un document est sain,
suspect ou frauduleux. Il produit un score de risque entre 0 et 100 et une liste d'anomalies détectées.

---

## Rôle dans le pipeline

```
OCR Service  →  Validation Service  →  Backend Node.js
             POST /validate              stockage data lake
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
validation/
├── main.py          Point d'entrée FastAPI — orchestre tous les appels
├── rules.py         7 règles de validation (format, calcul, croisement)
├── scorer.py        Calcul du score de risque et du statut final
├── config.py        Poids des règles et seuils CLEAN / WARNING / FRAUD
├── features.py      Extraction des 8 features pour le modèle ML
├── train.py         Entraînement automatique via LazyClassifier (meilleur modèle sélectionné)
├── evaluate.py      Mesure de la performance sur le dataset complet
├── predict.py       Prédiction ML sur un document
├── best_model.pkl   Modèle entraîné (généré par train.py)
├── scaler.pkl       Normalisation StandardScaler (généré par train.py)
└── requirements.txt
```

---

## Les deux niveaux de validation

### Niveau 1 — Règles déterministes

Règles logiques appliquées sur les données extraites. Chaque règle retourne un message d'erreur ou `None` si tout est correct.

| Règle | Ce qu'elle vérifie | Poids | Justification |
|---|---|---|---|
| `FORMAT_SIRET` | SIRET contient exactement 14 chiffres numériques | 40 | Un SIRET mal formé ne peut pas être une faute de frappe. C'est soit un identifiant inventé, soit volontairement tronqué. Impact légal direct : le SIRET est obligatoire sur toute facture. |
| `LUHN_SIRET` | SIRET valide selon l'algorithme de Luhn | 40 | Vérification mathématique : un SIRET qui échoue est forcément construit avec de faux chiffres. Personne ne fait ça involontairement. N'est évalué que si `FORMAT_SIRET` passe. |
| `ARITHMETIC_ERROR` | HT + TVA = TTC (tolérance 0,01 €) | 30 | Peut être une erreur de saisie ou une fraude. Seul, il ne bloque pas — il signale pour revue humaine. Deux anomalies de ce niveau ensemble suffisent à passer en WARNING. |
| `TVA_INVALIDE` | Clé TVA intracommunautaire correcte `(12 + 3 × SIREN mod 97) mod 97` | 30 | La clé se calcule mathématiquement. Une clé fausse peut venir d'une TVA copiée d'une autre entreprise ou d'une erreur de saisie. Même ambiguïté que l'arithmétique, même poids. |
| `ATTESTATION_EXPIRED` | Date d'expiration de l'attestation non dépassée | 35 | Peut être un oubli administratif ou une tentative de faire passer un fournisseur non à jour URSSAF. Travailler avec un fournisseur non à jour engage la responsabilité de l'acheteur. |
| `SIRET_MISMATCH` | SIRET facture = SIRET de l'attestation liée | 50 | Deux documents du même fournisseur avec deux SIRET différents — l'un est forcément faux. Impact direct sur la validité juridique de la relation commerciale. |
| `DOUBLON_FACTURE` | Pas de facture identique (même vendeur + même TTC) dans le dataset | 50 | Même vendeur, même montant, deux fichiers distincts : intention claire de double paiement. Impact financier direct et immédiat. |

### Niveau 2 — Détection ML (sélection automatique via LazyClassifier)

Le modèle est sélectionné automatiquement à chaque exécution de `train.py` : tous les classifieurs scikit-learn sont évalués sur le dataset et le meilleur F1-score remporte la mise.

**Résultats sur 2 000 factures PDF (1 000 légitimes / 1 000 falsifiées) :**

| Modèle | Accuracy | F1 Score |
|---|---|---|
| **GaussianNB** *(sélectionné)* | **86,75 %** | **0.865** |
| QuadraticDiscriminantAnalysis | 86,75 % | 0.865 |
| AdaBoostClassifier | 86,00 % | 0.858 |
| LGBMClassifier | 83,50 % | 0.833 |
| RandomForestClassifier | 81,25 % | 0.812 |

> GaussianNB est sélectionné automatiquement car il obtient le meilleur F1-score avec le temps d'inférence le plus bas (7 ms). Le modèle et le scaler sont sauvegardés dans `best_model.pkl` et `scaler.pkl`.

**Features utilisées (8 au total) :**

| # | Nom | Description |
|---|---|---|
| 0 | `total_ht` | Montant hors taxes |
| 1 | `tva` | Montant TVA déclaré |
| 2 | `total_ttc` | Montant toutes taxes comprises |
| 3 | `taux_tva` | Taux TVA calculé |
| 4 | `ratio_tva` | `tva / total_ht` |
| 5 | `ratio_ttc` | `total_ttc / total_ht` |
| 6 | `taux_normal` | 1 si taux TVA ≈ 20 %, 0 sinon |
| 7 | `ecart_tva` | Écart absolu entre taux TVA et 20 % |

Le score ML va de **0 à 40** et s'additionne au score des règles déterministes.

---

## Calcul du score de risque

```
score = min(somme des poids des anomalies détectées, 100)
```

| Score | Statut | Action |
|---|---|---|
| 0 – 29 | `CLEAN` | Document accepté automatiquement |
| 30 – 69 | `WARNING` | Revue humaine recommandée |
| 70 – 100 | `FRAUD` | Document bloqué, alerte créée |

---

## Résultats des tests (10 cas de test)

```
CAS 1  — Document propre                → score=0   CLEAN    
CAS 2  — Format SIRET incorrect         → score=80  FRAUD    ['FORMAT_SIRET', 'ML_ANOMALY']
CAS 3  — SIRET invalide Luhn            → score=80  FRAUD    ['LUHN_SIRET', 'ML_ANOMALY']
CAS 4  — Erreur arithmétique            → score=70  FRAUD    ['ARITHMETIC_ERROR', 'ML_ANOMALY']
CAS 5  — TVA invalide                   → score=70  FRAUD    ['TVA_INVALIDE', 'ML_ANOMALY']
CAS 6  — Attestation expirée            → score=35  WARNING  ['ATTESTATION_EXPIRED']
CAS 7  — Attestation valide             → score=0   CLEAN    
CAS 8  — SIRET mismatch inter-docs      → score=50  WARNING  ['SIRET_MISMATCH']
CAS 9  — Doublon facture                → score=100 FRAUD    ['SIRET_MISMATCH', 'DOUBLON_FACTURE']
CAS 10 — Cumul de fraudes               → score=100 FRAUD    ['LUHN_SIRET', 'ARITHMETIC_ERROR', 'TVA_INVALIDE', 'ML_ANOMALY']
```

---

## Format des échanges

### Requête POST /validate

```json
{
  "doc_id":          "facture_001",
  "doc_type":        "facture",
  "fichier":         "facture_legit_0001.pdf",
  "vendeur":         "Air France",
  "siret":           "44829292000015",
  "siren":           "448292920",
  "tva":             "FR59448292920",
  "total_ht":        1920.0,
  "tva_montant":     384.0,
  "total_ttc":       2304.0,
  "date_expiration": null
}
```

### Réponse — document propre

```json
{
  "doc_id":     "facture_001",
  "risk_score": 0,
  "status":     "CLEAN",
  "anomalies":  []
}
```

### Réponse — fraude détectée

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

À faire une seule fois avant de lancer le serveur, ou après avoir régénéré le dataset.

```bash
python train.py
```

Pour mesurer la performance sur le dataset complet :

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

## Lancer les 10 cas de test

```bash
# 1. Démarrer le serveur
uvicorn main:app --port 8001 --reload

# 2. Dans un autre terminal
python preprocess/test_validation.py
```