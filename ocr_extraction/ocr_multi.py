import os
from dataclasses import dataclass
from typing import Optional, Tuple


def _env(name: str, default: str) -> str:
    v = os.environ.get(name)
    return v if v is not None and v != "" else default


TESSERACT_CONF_THRESHOLD = float(_env("TESSERACT_CONF_THRESHOLD", "0.55"))


@dataclass
class OcrResult:
    text: str
    confidence_score: float
    engine_used: str  # "tesseract" | "tesseract+easyocr" | "easyocr"


def _preprocess_image_cv(img):
    """
    Pre-traitement OpenCV pour ameliorer OCR sur scans degrades :
    denoise, CLAHE, threshold + deskew.
    """
    import cv2
    import numpy as np

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    denoised = cv2.fastNlMeansDenoising(
        gray, h=10, templateWindowSize=7, searchWindowSize=21
    )

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(denoised)

    _, binary = cv2.threshold(
        equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Deskew
    coords = np.column_stack(np.where(binary > 0))
    if len(coords) < 10:
        return binary

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    if abs(angle) < 0.5:
        return binary

    h, w = binary.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        binary,
        M,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return rotated


def _confidence_from_tesseract_image_data(data: dict) -> float:
    confs = []
    for c in data.get("conf", []):
        try:
            if str(c) != "-1":
                ci = int(c)
                if ci >= 0:
                    confs.append(ci)
        except Exception:
            continue
    if not confs:
        return 0.0
    return round(sum(confs) / len(confs) / 100.0, 3)


def ocr_tesseract(image_path: str, lang: str = "fra+eng") -> OcrResult:
    import numpy as np
    import pytesseract
    import cv2
    from PIL import Image

    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Image introuvable ou illisible : {image_path}")

    processed = _preprocess_image_cv(img)
    pil = Image.fromarray(processed)

    data = pytesseract.image_to_data(
        pil, lang=lang, output_type=pytesseract.Output.DICT
    )
    text = pytesseract.image_to_string(pil, lang=lang)
    conf = _confidence_from_tesseract_image_data(data)
    return OcrResult(text=text.strip(), confidence_score=conf, engine_used="tesseract")


def ocr_easyocr(image_path: str, lang: Tuple[str, ...] = ("fr", "en")) -> OcrResult:
    import easyocr

    reader = easyocr.Reader(list(lang), gpu=False)
    results = reader.readtext(image_path)
    # results: [(bbox, text, prob), ...]
    texts = []
    probs = []
    for _bbox, text, prob in results:
        if text:
            texts.append(str(text))
        try:
            probs.append(float(prob))
        except Exception:
            continue
    text_out = "\n".join(texts).strip()
    conf = round(sum(probs) / len(probs), 3) if probs else 0.0
    return OcrResult(text=text_out, confidence_score=conf, engine_used="easyocr")


def ocr_image_multi(image_path: str) -> OcrResult:
    """
    Pipeline OCR multi-approche :
    1) Tesseract
    2) fallback EasyOCR si confidence basse ou texte trop court
    """
    tess = ocr_tesseract(image_path=image_path)

    # Conditions de fallback
    if tess.text and len(tess.text) >= 80 and tess.confidence_score >= TESSERACT_CONF_THRESHOLD:
        return tess

    # Tesseract faible => EasyOCR
    try:
        easy = ocr_easyocr(image_path=image_path)
        if easy.text:
            # On pref config : si EasyOCR trouve mieux, on le garde
            if easy.confidence_score >= tess.confidence_score:
                return OcrResult(
                    text=easy.text,
                    confidence_score=easy.confidence_score,
                    engine_used="tesseract+easyocr",
                )
    except Exception:
        # Si EasyOCR plante, on garde Tesseract.
        pass

    return tess

