# Hackathon 2026 — Validation automatique de documents administratifs

Plateforme de traitement intelligent de factures fournisseurs : upload, OCR, extraction d'entités, validation et auto-remplissage des applications métiers.

---

## Architecture

```
Frontend (React/Vite)
        │ upload fichier
        ▼
Backend Node.js ──────────────────► MongoDB
        │ stocke dans MinIO         (documents, fournisseurs, users)
        │ déclenche Airflow
        ▼
MinIO Data Lake
  ├── raw/        ← fichiers bruts uploadés
  ├── clean/      ← texte OCR extrait (JSON)
  └── curated/    ← données validées + fiches fournisseurs
        │
        ▼
Airflow (pipeline orchestré)
  get_file → ingest → run_ocr → extract → validate → store → notify
                                                               │
                                                     Backend notifié
                                                               │
                                                        Frontend mis à jour
```

---

## Stack technique

| Composant | Technologie |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS |
| Backend API | Node.js, Express, MongoDB |
| Data Lake | MinIO (compatible S3) |
| Orchestration | Apache Airflow 2.7.3 |
| OCR | Tesseract + EasyOCR + OpenCV |
| Extraction | spaCy, regex |
| Validation | FastAPI, AdaBoost (ML) |
| Base de données | PostgreSQL (Airflow), MongoDB (API) |
| Conteneurisation | Docker, Docker Compose |

---

## Structure du projet

```
HACKATHON 2026/
├── airflow/
│   ├── dags/               ← DAG Airflow (document_pipeline.py)
│   ├── scripts/            ← Modules Python du pipeline
│   │   ├── ingest.py
│   │   ├── ocr.py
│   │   ├── extract.py
│   │   ├── validate.py
│   │   ├── store.py
│   │   └── notify.py
│   └── data/               ← Dossier de données local Airflow
├── back/                   ← Backend Node.js
│   └── src/
│       ├── routes/         ← auth, documents, suppliers, pipeline
│       ├── models/         ← User, Document, Supplier
│       └── server.js
├── data-lake/              ← Module Python MinIO (storage_client.py)
├── datasets/               ← Génération de données synthétiques
│   └── generate.ipynb
├── deploy/                 ← Docker Compose + Dockerfiles
│   ├── docker-compose.yml
│   ├── .env
│   ├── Dockerfile.airflow
│   ├── Dockerfile.back
│   ├── Dockerfile.front
│   └── Dockerfile.validation
├── front/                  ← Frontend React
│   └── src/
│       ├── api/client.js   ← Client API centralisé
│       ├── pages/
│       └── components/
├── ocr/
│   └── extraction/         ← Module OCR (pipeline.py, ocr_multi.py)
└── validation/             ← Service de validation FastAPI
    ├── main.py
    ├── rules.py
    ├── scorer.py
    └── train.py
```

---

## Démarrage rapide

### Prérequis

- Docker Desktop (≥ 4.x)
- Git

### Installation

```bash
git clone <url-du-repo>
cd HACKATHON2026
cp deploy/.env.example deploy/.env
```

### Lancement

```bash
cd deploy
docker-compose up -d
```

Attendre ~2 minutes, puis vérifier :

```bash
docker-compose ps
```

### Accès aux services

| Service | URL | Credentials |
|---|---|---|
| Frontend | http://localhost:5173 | Créer un compte via /register |
| Backend API | http://localhost:3001 | JWT via /api/auth/login |
| Airflow UI | http://localhost:8083 | airflow / airflow |
| MinIO Console | http://localhost:9006 | minioadmin / minioadmin |
| Service Validation | http://localhost:8001/docs | — |

---

## Flux de traitement

### 1. Upload d'une facture

1. Se connecter avec le rôle **Opérateur** sur le frontend
2. Glisser-déposer une facture (PDF, JPG, PNG)
3. Le fichier est stocké dans MinIO `raw/` et enregistré dans MongoDB
4. Le backend déclenche automatiquement le DAG Airflow

### 2. Pipeline Airflow

```
get_file        → récupère le fichier depuis MinIO raw
ingest_document → identifie le type (PDF, image, texte)
run_ocr         → Tesseract + OpenCV → texte brut
extract_entities → SIRET, TVA, montants, dates
validate_document → règles métier + score d'anomalie ML
store_curated   → JSON validé dans MinIO curated
notify_frontend → webhook POST vers le backend
```

Déclencher manuellement :
`http://localhost:8083` → DAG `document_pipeline` → **▶ Trigger DAG**

### 3. Résultats dans le frontend

- **Conformité** : tableau de bord avec statut et anomalies
- **CRM** : fiche fournisseur auto-remplie (SIRET, raison sociale, IBAN)
- **Opérateur** : suivi du statut de traitement

---

## Rôles utilisateurs

| Rôle | Valeur backend | Accès |
|---|---|---|
| Opérateur | `operator` | Upload, suivi pipeline |
| Comptable / CRM | `supplier` | Fiches fournisseurs |
| Conformité | `admin` | Anomalies, audit trail |

---

## Équipe

| Membre | Rôle | Responsabilité |
|---|---|---|
| Clément (Chef de projet) | Data Lake | MinIO, zones Raw/Clean/Curated, docker-compose |
| Chaimae | Orchestration | Airflow DAGs, pipeline, DevOps |
| Ryma | Frontend | React, gestion des rôles, auto-remplissage |
| Soufiane | OCR & Backend | Tesseract, EasyOCR, spaCy, Node.js |
| Awadi | Validation | Règles métier, anomaly detection |
| Conambot | Datasets | Factures synthétiques (Faker, SIRENE) |

---

## Buckets MinIO

| Bucket | Contenu | Producteur | Consommateur |
|---|---|---|---|
| `raw` | Fichiers bruts uploadés | Backend | Airflow (OCR) |
| `clean` | JSON texte OCR extrait | Airflow | Airflow (validation) |
| `curated` | JSON validé + fiches fournisseurs | Airflow | Backend |

---

## Entraîner le modèle ML

```bash
cd validation
pip install -r requirements.txt
python train.py   # entraînement
python evaluate.py   # évaluation
```

---

## Génération du dataset

```bash
cd datasets
jupyter notebook generate.ipynb
```

Scénarios couverts : factures légitimes, SIRET invalide, TVA incohérente, montants falsifiés, scans dégradés.