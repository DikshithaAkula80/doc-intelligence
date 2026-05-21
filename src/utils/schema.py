from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float
    page_width: float
    page_height: float

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    source_file: str
    page_number: int
    modality: Literal["text", "table", "figure", "ocr"]
    content: str
    structured_data: Optional[dict] = None
    bbox: Optional[BoundingBox] = None
    section_heading: Optional[str] = None
    extraction_confidence: float = 1.0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
