# OCR Extraction (zone Clean)

Ce dossier implémente la partie **4. OCR & Extraction** du cahier de charges :

- Input : fichier brut (local) ou objet MinIO en zone Raw
- Preprocessing OpenCV (denoise/CLAHE/threshold/deskew)
- OCR multi-approche :
  - Tesseract en priorité
  - fallback EasyOCR quand la confiance OCR est faible
- Extraction entités :
  - spaCy (fr_core_news_lg si disponible) pour segmenter le texte en phrases
  - regex ciblées par champ : `siret`, `tva_intracommunautaire`, montants, dates
- Génération JSON contractuel :
  - `document_id`, `document_type`, `siret`, `tva_intracommunautaire`,
    `montant_ht`, `montant_ttc`, `date_emission`, `date_expiration`,
    `confidence_score`, `raw_text`
- Output : persistance de la "zone Clean" dans MinIO via bucket `clean-texts`

## Usage local (test sur datasets/output/test)
1. Installer les dependances (si besoin) :
   - `pytesseract`, `easyocr`, `spacy`, `pdfplumber` (si OCR PDF natif a ete etendu), `minio`
2. Lancer :
```bash
python -m ocr_extraction.test_ocr_on_dataset --input_dir datasets/output/test --output_dir /tmp/ocr_out --max_docs 10 --document_id_from_filename
```

## Usage MinIO (Input Raw -> Output Clean)
Dans un DAG Airflow ou un script de traitement :
```python
from ocr_extraction.pipeline import extract_from_minio_to_clean

extract_from_minio_to_clean(
  document_id="uuid-ou-stem",
  raw_object_key="raw/<document_id>/<nom_fichier>.pdf",
  document_type="facture_fournisseur",
  store_clean=True
)
```

### Variables d'environnement MinIO
- `MINIO_ENDPOINT` (default `http://minio:9000`)
- `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY`
- `MINIO_BUCKET_RAW` (default `raw`)
- `MINIO_BUCKET_CLEAN_TEXTS` (default `clean`)

> Le cahier demande `raw-documents` et `clean-texts`. Tu peux changer les buckets via les env variables.

