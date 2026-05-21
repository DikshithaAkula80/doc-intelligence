import fitz
import pytesseract
from pathlib import Path
from typing import List
import uuid
from src.utils.schema import DocumentChunk

def page_has_selectable_text(pdf_path: str, page_num: int) -> bool:
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    text = page.get_text("text").strip()
    doc.close()
    return len(text) > 50

def ocr_pdf(pdf_path: str, doc_id: str) -> List[DocumentChunk]:
    try:
        from pdf2image import convert_from_path
    except ImportError:
        return []
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    doc.close()
    chunks = []
    source_file = Path(pdf_path).name
    for page_num in range(num_pages):
        if page_has_selectable_text(pdf_path, page_num):
            continue
        try:
            images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1, dpi=300)
            if not images:
                continue
            text = pytesseract.image_to_string(images[0]).strip()
            if len(text) < 20:
                continue
            chunks.append(DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc_id,
                source_file=source_file,
                page_number=page_num+1,
                modality="ocr",
                content=text,
                extraction_confidence=0.75,
            ))
        except Exception:
            continue
    return chunks
