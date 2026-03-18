import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def run_ocr():
    print("Running OCR...")

    input_folder = "data/raw/"
    output_folder = "data/clean/"
    os.makedirs(output_folder, exist_ok=True)

    files = os.listdir(input_folder)

    if not files:
        raise Exception("No files found")

    file_name = files[0]
    file_path = os.path.join(input_folder, file_name)

    text = ""

    #  CAS PDF
    if file_name.endswith(".pdf"):
        images = convert_from_path(file_path)

        for img in images:
            text += pytesseract.image_to_string(img)

    # CAS IMAGE
    elif file_name.endswith((".png", ".jpg", ".jpeg")):
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)

    else:
        raise Exception("Unsupported file format")

    # sauvegarde
    with open(os.path.join(output_folder, "text.txt"), "w") as f:
        f.write(text)

    print("OCR completed")