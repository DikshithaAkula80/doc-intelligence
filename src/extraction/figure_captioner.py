import requests
import base64
from pathlib import Path
from typing import List
import uuid
from src.utils.schema import DocumentChunk, BoundingBox

def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def caption_figures(image_regions: List[dict], doc_id: str) -> List[DocumentChunk]:
    chunks = []
    for region in image_regions:
        img_path = region["image_path"]
        if not Path(img_path).exists():
            continue
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": "Describe this figure from a document. If it is a chart or graph, describe what it shows including axis labels and trends. If it is a diagram, describe its structure. Be concise and precise. Output only the description.",
                    "images": [_encode_image(img_path)],
                    "stream": False,
                },
                timeout=60,
            )
            caption = response.json().get("response", "").strip()
        except Exception as e:
            caption = f"[caption failed: {e}]"
        b = region["bbox"]
        chunks.append(DocumentChunk(
            chunk_id=str(uuid.uuid4()),
            doc_id=doc_id,
            source_file=Path(img_path).name,
            page_number=region["page"],
            modality="figure",
            content=caption,
            extraction_confidence=0.85,
            bbox=BoundingBox(x0=b["x0"], y0=b["y0"], x1=b["x1"], y1=b["y1"],
                page_width=region["page_width"], page_height=region["page_height"])
        ))
    return chunks
