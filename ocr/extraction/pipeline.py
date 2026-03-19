import os
import uuid
from typing import Optional, Dict, Any

from .contract import Contract, compute_contract_confidence
from .entity_extraction import extract_entities_spacy_regex
from .minio_storage import download_from_minio, put_json_to_minio
from .ocr_multi import ocr_image_multi


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


MINIO_BUCKET_RAW = _env("MINIO_BUCKET_RAW", "raw")
MINIO_BUCKET_CLEAN_TEXTS = _env("MINIO_BUCKET_CLEAN_TEXTS", "clean")

POPPLER_PATH = _env("POPPLER_PATH", r"C:\poppler\poppler-24.08.0\Library\bin")

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
    Conversion PDF -> image PNG propre pour OCR.
    Utilise pdf2image avec poppler.
    Pas de binarisation pour les PDFs vectoriels.
    """
    from pdf2image import convert_from_path
    import tempfile
    import numpy as np
    import cv2
    from PIL import Image as PILImage

    pages = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    if not pages:
        raise ValueError(f"PDF sans page : {pdf_path}")

    img = np.array(pages[0])

    # Detection et correction de rotation via Tesseract OSD
    try:
        import pytesseract

        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        osd = pytesseract.image_to_osd(gray, output_type=pytesseract.Output.DICT)
        angle = osd.get("rotate", 0)
        if angle != 0:
            pil = PILImage.fromarray(img)
            pil = pil.rotate(-angle, expand=True)
            img = np.array(pil)
    except Exception:
        pass

    out = tempfile.mktemp(prefix="pdf_page_", suffix=".png")
    PILImage.fromarray(img).save(out, "PNG")
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

    return contract.to_dict() | {
        "_ocr_meta": {
            "engine_used": ocr_out.get("engine_used"),
            "ocr_confidence_score": ocr_out.get("confidence_score"),
        }
    }


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
