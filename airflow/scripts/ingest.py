import os
import logging
 
log = logging.getLogger(__name__)
 
SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".tiff": "image",
    ".tif": "image",
    ".bmp": "image",
    ".txt": "txt",
    ".text": "txt",
    ".md": "txt",
}
 
 
def ingest_document(file_path: str) -> dict:
    """
    Analyse le fichier et retourne ses métadonnées.
 
    Returns:
        dict avec les clés :
          - path (str)       : chemin absolu
          - type (str)       : "pdf" | "image" | "txt"
          - filename (str)   : nom du fichier
          - size_bytes (int) : taille
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Fichier introuvable : {file_path}")
 
    ext = os.path.splitext(file_path)[1].lower()
    file_type = SUPPORTED_EXTENSIONS.get(ext)
 
    if file_type is None:
        raise ValueError(
            f"Format non supporté : '{ext}'. "
            f"Formats acceptés : {list(SUPPORTED_EXTENSIONS.keys())}"
        )
 
    file_info = {
        "path": file_path,
        "type": file_type,
        "filename": os.path.basename(file_path),
        "size_bytes": os.path.getsize(file_path),
    }
 
    log.info("Fichier ingéré : %s", file_info)
    return file_info