import fitz
from pathlib import Path
from typing import List
import uuid

def extract_image_regions(pdf_path: str, output_dir: str) -> List[dict]:
    doc = fitz.open(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    regions = []
    for page_num, page in enumerate(doc, start=1):
        page_rect = page.rect
        for img in page.get_images(full=True):
            xref = img[0]
            bbox_list = page.get_image_rects(xref)
            if not bbox_list:
                continue
            bbox = bbox_list[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=fitz.Rect(bbox))
            img_path = output_dir / f"page{page_num}_img{xref}_{uuid.uuid4().hex[:6]}.png"
            pix.save(str(img_path))
            regions.append({
                "page": page_num,
                "image_path": str(img_path),
                "bbox": {"x0": bbox.x0, "y0": bbox.y0, "x1": bbox.x1, "y1": bbox.y1},
                "page_width": page_rect.width,
                "page_height": page_rect.height,
            })
    doc.close()
    return regions
