import fitz
from pathlib import Path
from typing import List
import uuid
from src.utils.schema import DocumentChunk, BoundingBox

def extract_text_chunks(pdf_path: str, doc_id: str) -> List[DocumentChunk]:
    doc = fitz.open(pdf_path)
    chunks = []
    source_file = Path(pdf_path).name
    current_heading = None
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        page_rect = page.rect
        for block in blocks:
            if block["type"] != 0:
                continue
            full_text = ""
            is_heading = False
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    if not text:
                        continue
                    if span["size"] > 14 and len(text) < 120:
                        is_heading = True
                    full_text += text + " "
            full_text = full_text.strip()
            if not full_text or len(full_text) < 20:
                continue
            if is_heading:
                current_heading = full_text
            b = block["bbox"]
            chunks.append(DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=doc_id,
                source_file=source_file,
                page_number=page_num,
                modality="text",
                content=full_text,
                section_heading=current_heading,
                bbox=BoundingBox(x0=b[0], y0=b[1], x1=b[2], y1=b[3],
                    page_width=page_rect.width, page_height=page_rect.height)
            ))
    doc.close()
    return chunks
