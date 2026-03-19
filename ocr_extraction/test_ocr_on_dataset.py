import argparse
import json
import os
from pathlib import Path

from .pipeline import extract_from_local_file


SUPPORTED_EXTS = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".txt", ".md", ".text"}


def iter_documents(input_dir: Path):
    for p in input_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            yield p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", type=str, default="datasets/output/test")
    ap.add_argument("--output_dir", type=str, default="ocr_extraction_outputs")
    ap.add_argument("--max_docs", type=int, default=25)
    ap.add_argument("--document_id_from_filename", action="store_true")
    ap.add_argument("--skip_pdf", action="store_true")
    args = ap.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for p in iter_documents(input_dir):
        if count >= args.max_docs:
            break

        if args.skip_pdf and p.suffix.lower() == ".pdf":
            continue

        doc_id = p.stem if args.document_id_from_filename else None
        try:
            out = extract_from_local_file(
                file_path=str(p),
                document_id=doc_id,
            )
        except Exception as e:
            out = {
                "_error": str(e),
                "_file": str(p),
                "document_id": doc_id,
            }

        out_path = output_dir / f"{p.stem}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)

        print(f"[ocr_test] {p.name} -> {out_path}")
        count += 1


if __name__ == "__main__":
    main()

