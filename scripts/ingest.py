import os

def ingest_document(file_path):
    ext = file_path.lower().split('.')[-1]

    print(f"Processing file: {file_path}")

    if ext == "pdf":
        return {"type": "pdf", "path": file_path}

    elif ext in ["png", "jpg", "jpeg"]:
        return {"type": "image", "path": file_path}

    elif ext == "txt":
        return {"type": "text", "path": file_path}

    else:
        raise ValueError(f"Unsupported file type: {ext}")