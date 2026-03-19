import os
import uuid
from typing import Optional, Dict, Any

from .contract import Contract, compute_contract_confidence
from .entity_extraction import extract_entities_spacy_regex
from .minio_storage import (
    download_from_minio,
    put_json_to_minio,
)
from .ocr_multi import ocr_image_multi


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


MINIO_BUCKET_RAW = _env("MINIO_BUCKET_RAW", "raw")
MINIO_BUCKET_CLEAN_TEXTS = _env("MINIO_BUCKET_CLEAN_TEXTS", "clean")


SUPPORTED_LOCAL_EXTS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
    ".txt",
    ".md",
    ".text",
}


def _read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().strip()


def _pdf_to_first_page_image(pdf_path: str) -> str:
    """
    Conversion PDF -> image pour OCR.
    Note : pour rester simple, on OCR la 1ere page pour l'extraction.
    Ajustable si vous voulez OCR toutes les pages (plus lent).
    """
    from pdf2image import convert_from_path

    pages = convert_from_path(pdf_path, dpi=200)
    if not pages:
        raise ValueError(f"PDF sans page : {pdf_path}")
    pil = pages[0]
    # Sauvegarde image temporaire.
    import tempfile
    out = tempfile.mktemp(prefix="pdf_page_", suffix=".png")
    pil.save(out, "PNG")
    return out


def _ocr_text_for_file(file_path: str) -> Dict[str, Any]:
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".txt", ".md", ".text"]:
        text = _read_txt(file_path)
        return {"text": text, "confidence_score": 1.0, "engine_used": "txt"}

    if ext == ".pdf":
        img_path = _pdf_to_first_page_image(file_path)
        try:
            res = ocr_image_multi(img_path)
            return {
                "text": res.text,
                "confidence_score": res.confidence_score,
                "engine_used": res.engine_used,
            }
        finally:
            try:
                os.remove(img_path)
            except Exception:
                pass

    # Image
    res = ocr_image_multi(file_path)
    return {
        "text": res.text,
        "confidence_score": res.confidence_score,
        "engine_used": res.engine_used,
    }


def extract_from_local_file(
    file_path: str,
    document_id: Optional[str] = None,
    document_type: str = "facture_fournisseur",
) -> dict:
    """
    Pipeline locale : OCR + extraction + generation contract JSON.
    """
    if document_id is None:
        # UUID stable pour un test (pas besoin d'un UUID extern).
        document_id = str(uuid.uuid4())

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_LOCAL_EXTS:
        raise ValueError(f"Extension non supportee : {ext}")

    ocr_out = _ocr_text_for_file(file_path)
    extracted = extract_entities_spacy_regex(
        text=ocr_out.get("text", ""),
        document_type=document_type,
    )

    conf = compute_contract_confidence(
        ocr_confidence=ocr_out.get("confidence_score", 0.0),
        siret=extracted.siret,
        tva_intracommunautaire=extracted.tva_intracommunautaire,
        montant_ht=extracted.montant_ht,
        montant_ttc=extracted.montant_ttc,
        date_emission=extracted.date_emission,
        date_expiration=extracted.date_expiration,
    )

    contract = Contract(
        document_id=document_id,
        document_type=document_type,
        siret=extracted.siret,
        tva_intracommunautaire=extracted.tva_intracommunautaire,
        montant_ht=extracted.montant_ht,
        montant_ttc=extracted.montant_ttc,
        date_emission=extracted.date_emission,
        date_expiration=extracted.date_expiration,
        confidence_score=conf,
        raw_text=extracted.raw_text,
    )

    result = contract.to_dict()
    result["_ocr_meta"] = {
        "engine_used": ocr_out.get("engine_used"),
        "ocr_confidence_score": ocr_out.get("confidence_score"),
    }
    return result


def extract_from_minio_to_clean(
    document_id: str,
    raw_object_key: str,
    document_type: str = "facture_fournisseur",
    store_clean: bool = True,
) -> dict:
    """
    Pipeline "Input MinIO Raw -> Output MinIO Clean".
    Telecharge depuis MinIO, OCR+extraction, puis stocke dans clean-texts.
    """
    local_path = download_from_minio(
        object_key=raw_object_key,
        bucket=MINIO_BUCKET_RAW,
    )
    try:
        contract_out = extract_from_local_file(
            file_path=local_path,
            document_id=document_id,
            document_type=document_type,
        )
    finally:
        try:
            os.remove(local_path)
        except Exception:
            pass

    if store_clean:
        # Cle MinIO : clean-texts/<document_id>.json
        clean_key = f"{document_id}.json"
        put_json_to_minio(
            payload=contract_out,
            object_key=clean_key,
            bucket=MINIO_BUCKET_CLEAN_TEXTS,
        )
    return contract_out

