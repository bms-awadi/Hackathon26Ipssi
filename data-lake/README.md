# Data Lake — MinIO

Responsable : Clément
Stack : MinIO (compatible S3), Docker

---

## Démarrage rapide

```bash
cd data-lake

# 1. Copier le fichier d'environnement
cp .env.example .env

# 2. Démarrer MinIO
docker-compose up -d

# 3. Initialiser les buckets
uv run python init_buckets.py
```

Console MinIO accessible sur : http://localhost:9001  
Login : `minio_admin` / `minio_password`

---

## Structure des buckets

| Bucket | Rôle | Producteur | Consommateur |
|---|---|---|---|
| `raw-documents` | Fichiers bruts uploadés (PDF, JPG, PNG) | Ryma (upload frontend) | Soufiane (OCR) |
| `clean-texts` | JSON avec texte OCR extrait | Soufiane | Awadi (validation) |
| `curated-data` | JSON structuré validé, prêt pour le frontend | Awadi | Ryma (auto-remplissage) |

**Règle importante** : chaque service écrit uniquement dans sa zone de sortie et lit uniquement dans sa zone d'entrée. On ne remonte jamais en arrière.

---

## Convention de nommage des objets

Tous les fichiers sont nommés avec le `document_id` (UUID généré à l'upload) :

```
raw-documents/  {document_id}.pdf
clean-texts/    {document_id}.json
curated-data/   {document_id}.json
```

Exemple pour le document `3f8a2c1d-4b5e-...` :
```
raw-documents/  3f8a2c1d-4b5e-....pdf
clean-texts/    3f8a2c1d-4b5e-....json
curated-data/   3f8a2c1d-4b5e-....json
```

---

## Utilisation — `storage_client.py`

Tous les services passent par ce module. Ne pas appeler l'API MinIO directement.

### Import

```python
from data_lake.storage_client import upload_file, upload_bytes, download_file, list_objects
from data_lake.storage_client import BUCKET_RAW, BUCKET_CLEAN, BUCKET_CURATED
```

### Déposer un fichier (depuis le disque)

```python
# Soufiane — déposer le PDF brut reçu de Ryma
upload_file(BUCKET_RAW, f"{document_id}.pdf", "/tmp/facture.pdf")
```

### Déposer des données en mémoire

```python
import json

# Awadi — déposer le JSON validé directement sans fichier temporaire
data = {"document_id": "3f8a2c1d", "siret": "83214056700024", ...}
upload_bytes(BUCKET_CURATED, f"{document_id}.json", json.dumps(data).encode(), "application/json")
```

### Récupérer un fichier

```python
# Soufiane — télécharger le PDF brut pour le passer à Tesseract
download_file(BUCKET_RAW, f"{document_id}.pdf", f"/tmp/{document_id}.pdf")
```

### Lister les fichiers d'un bucket

```python
# Lister tous les fichiers
list_objects(BUCKET_CLEAN)
# → ['3f8a2c1d.json', 'a1b2c3d4.json', ...]

# Filtrer par préfixe si besoin
list_objects(BUCKET_CURATED, prefix="2026-03-")
```

---

## Variables d'environnement

Créer un fichier `.env` à la racine de `data-lake/` :

```env
MINIO_ROOT_USER=minio_admin
MINIO_ROOT_PASSWORD=minio_password
MINIO_ENDPOINT=http://localhost:9000
```

### Dans le réseau Docker (Airflow, services Python)

Utiliser `minio` comme hostname à la place de `localhost` :

```env
MINIO_ENDPOINT=http://minio:9000
```

Chaimae : dans les DAGs Airflow, les variables d'env sont à déclarer dans le `docker-compose.yml` global sous `environment:`.

---

## Intégration docker-compose global

Pour intégrer MinIO dans le `docker-compose.yml` global du projet, ajouter ce bloc dans `services:` :

```yaml
minio:
  image: minio/minio:latest
  container_name: minio
  ports:
    - "9000:9000"
    - "9001:9001"
  environment:
    MINIO_ROOT_USER: ${MINIO_ROOT_USER:-minio_admin}
    MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:-minio_password}
  volumes:
    - minio_data:/data
  command: server /data --console-address ":9001"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
    interval: 10s
    timeout: 5s
    retries: 3

volumes:
  minio_data:
```

---

## Dépendances Python

```bash
uv add minio python-dotenv
```

ou via `requirements.txt` :
```
minio==7.2.7
python-dotenv==1.0.0
```