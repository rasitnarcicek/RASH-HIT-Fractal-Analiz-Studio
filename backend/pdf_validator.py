# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Mehmet Raşit Narçiçek

from pathlib import Path
import fitz

def validate_pdf_file(pdf_path: Path) -> dict:
    if not pdf_path.exists():
        return {"status": "FAIL", "reason": "PDF file does not exist on disk"}

    size_bytes = pdf_path.stat().st_size
    if size_bytes == 0:
        return {"status": "FAIL", "reason": "PDF file is 0 bytes"}

    with open(pdf_path, "rb") as f:
        header = f.read(5)
    if header != b"%PDF-":
        return {"status": "FAIL", "reason": f"Invalid PDF header magic bytes: {header}"}

    try:
        doc = fitz.open(str(pdf_path))
        page_count = doc.page_count
        if page_count < 1:
            doc.close()
            return {"status": "FAIL", "reason": "PDF page count is less than 1"}

        p1_text = doc[0].get_text().strip()
        doc.close()

        if len(p1_text) == 0:
            return {"status": "FAIL", "reason": "PDF page 1 text extraction returned empty string"}

        return {
            "status": "PASS",
            "size_bytes": size_bytes,
            "page_count": page_count,
            "sample_text": p1_text[:100]
        }
    except Exception as e:
        return {"status": "FAIL", "reason": f"PyMuPDF failed to parse PDF: {e}"}
