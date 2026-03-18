import logging
import os
 
log = logging.getLogger(__name__)
 
 
# Prétraitement OpenCV 
 
def _preprocess_image(img):
    """
    Applique une chaîne de prétraitements OpenCV pour améliorer la lisibilité
    des scans dégradés (flou, rotation, bruit, faible contraste).
 
    Args:
        img : image numpy array (BGR, depuis cv2.imread)
 
    Returns:
        image numpy array prétraitée (niveaux de gris, binarisée)
    """
    import cv2
    import numpy as np
 
    # Conversion en niveaux de gris
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
    # Débruitage (conserve les bords texte)
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
 
    # Augmentation du contraste local (CLAHE)
    clahe   = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    equalized = clahe.apply(denoised)
 
    # Binarisation adaptative Otsu
    _, binary = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
 
    # Correction de l'inclinaison (deskew)
    binary = _deskew(binary)
 
    return binary
 
 
def _deskew(img):
    """Corrige l'inclinaison d'un scan via la transformée de Hough."""
    import cv2
    import numpy as np
 
    coords  = np.column_stack(np.where(img > 0))
    if len(coords) < 10:
        return img   # pas assez de pixels, on ne touche pas à l'image
 
    angle = cv2.minAreaRect(coords)[-1]
 
    # minAreaRect retourne des angles entre -90 et 0
    if angle < -45:
        angle = 90 + angle
    # On ne corrige que si l'angle est significatif (> 0.5°)
    if abs(angle) < 0.5:
        return img
 
    h, w    = img.shape[:2]
    center  = (w // 2, h // 2)
    M       = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    log.info("[ocr] Deskew appliqué : angle=%.2f°", angle)
    return rotated
 
 
def _compute_confidence(data: dict) -> float:
    """
    Calcule le score de confiance moyen depuis les données Tesseract (image_to_data).
    Ignore les valeurs -1 (mots non reconnus).
    """
    confs = [int(c) for c in data["conf"] if str(c) != "-1" and int(c) >= 0]
    if not confs:
        return 0.0
    return round(sum(confs) / len(confs) / 100.0, 3)   # normalise 0-100 → 0.0-1.0
 
 
# Extraction PDF 
 
def _extract_pdf(file_path: str) -> dict:
    """
    Tente d'abord l'extraction texte native (pdfplumber).
    Si le PDF est un scan, bascule sur OCR image par page (pdf2image + tesseract).
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("pdfplumber non installé — ajoutez-le dans requirements.txt")
 
    text_parts       = []
    total_confidence = []
 
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_parts.append(page_text)
                total_confidence.append(1.0)   # texte natif = confiance max
            else:
                log.info("[ocr] Page %d : pas de texte natif, OCR image...", i + 1)
                page_result = _ocr_page_as_image(page)
                text_parts.append(page_result["text"])
                total_confidence.append(page_result["confidence_score"])
 
    avg_conf = round(sum(total_confidence) / len(total_confidence), 3) if total_confidence else 0.0
    return {
        "text":             "\n".join(text_parts).strip(),
        "confidence_score": avg_conf,
        "preprocessed":     any(c < 1.0 for c in total_confidence),
    }
 
 
def _ocr_page_as_image(page) -> dict:
    """OCR d'une page pdfplumber convertie en image numpy."""
    import pytesseract
    import numpy as np
    from PIL import Image
 
    pil_img  = page.to_image(resolution=200).original
    np_img   = np.array(pil_img)
    processed = _preprocess_image(np_img)
 
    pil_processed = Image.fromarray(processed)
    data  = pytesseract.image_to_data(pil_processed, lang="fra+eng", output_type=pytesseract.Output.DICT)
    text  = pytesseract.image_to_string(pil_processed, lang="fra+eng")
    conf  = _compute_confidence(data)
 
    return {"text": text.strip(), "confidence_score": conf}
 
 
# Extraction image
 
def _extract_image(file_path: str) -> dict:
    """OCR sur image avec prétraitement OpenCV."""
    try:
        import cv2
        import pytesseract
        from PIL import Image
        import numpy as np
    except ImportError as e:
        raise ImportError(
            f"Dépendance manquante : {e}. "
            "Installez opencv-python-headless pytesseract pillow dans requirements.txt "
            "et tesseract-ocr dans le Dockerfile."
        )
 
    img       = cv2.imread(file_path)
    processed = _preprocess_image(img)
    pil_img   = Image.fromarray(processed)
 
    data = pytesseract.image_to_data(pil_img, lang="fra+eng", output_type=pytesseract.Output.DICT)
    text = pytesseract.image_to_string(pil_img, lang="fra+eng")
    conf = _compute_confidence(data)
 
    log.info("[ocr] Image — confiance : %.2f", conf)
    return {
        "text":             text.strip(),
        "confidence_score": conf,
        "preprocessed":     True,
    }
 
 
# Extraction texte brut 
 
def _extract_txt(file_path: str) -> dict:
    """Lecture directe d'un fichier .txt — pas d'OCR nécessaire."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read().strip()
    return {
        "text":             content,
        "confidence_score": 1.0,   # texte natif = confiance parfaite
        "preprocessed":     False,
    }
 
 
# Point d'entrée
def run_ocr(file_info: dict) -> dict:
    """
    Point d'entrée appelé par la tâche Airflow.
 
    Args:
        file_info : dict retourné par ingest_document()
                    Clés attendues : path, type, local_tmp
 
    Returns:
        dict avec text, confidence_score, preprocessed, fields (vide ici, rempli par extract.py)
    """
    file_path: str = file_info.get("local_tmp") or file_info.get("path")
    file_type: str = file_info["type"]
 
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier introuvable pour OCR : {file_path}")
 
    log.info("[ocr] Début extraction — type=%s, fichier=%s", file_type, file_path)
 
    if file_type == "pdf":
        result = _extract_pdf(file_path)
    elif file_type == "image":
        result = _extract_image(file_path)
    elif file_type == "txt":
        result = _extract_txt(file_path)
    else:
        raise ValueError(f"Type non supporté : {file_type}")
    
    result["file_path"] = file_path
    result["fields"] = {}   # sera rempli par extract_entities()
    log.info(
        "[ocr] Terminé — %d chars | confiance=%.2f | prétraitement=%s",
        len(result["text"]), result["confidence_score"], result["preprocessed"],
    )
    return result