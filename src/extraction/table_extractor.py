import fitz
from pathlib import Path
from typing import List
import uuid
from src.utils.schema import DocumentChunk, BoundingBox

def extract_tables(pdf_path: str, doc_id: str) -> List[DocumentChunk]:
    doc = fitz.open(pdf_path)
    chunks = []
    source_file = Path(pdf_path).name

    for page_num, page in enumerate(doc, start=1):
        tabs = page.find_tables()
        if not tabs or not tabs.tables:
            continue
        for table in tabs.tables:
            try:
                data = table.extract()
                if not data:
                    continue
                headers = data[0]
                rows = data[1:]
                structured = {"headers": headers, "rows": rows}
                text_repr = " | ".join(str(h) for h in headers) + "\n"
                for row in rows:
                    text_repr += " | ".join(str(c) for c in row) + "\n"
                bbox = table.bbox
                chunks.append(DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    doc_id=doc_id,
                    source_file=source_file,
                    page_number=page_num,
                    modality="table",
                    content=text_repr.strip(),
                    structured_data=structured,
                    extraction_confidence=0.9,
                    bbox=BoundingBox(
                        x0=bbox[0], y0=bbox[1], x1=bbox[2], y1=bbox[3],
                        page_width=page.rect.width,
                        page_height=page.rect.height
                    )
                ))
            except Exception:
                continue
    doc.close()
    return chunks
