from typing import List
from src.utils.schema import DocumentChunk
import uuid

def semantic_chunk(chunks: List[DocumentChunk], max_tokens: int = 500, overlap: int = 50) -> List[DocumentChunk]:
    result = []
    text_chunks = [c for c in chunks if c.modality == "text"]
    other_chunks = [c for c in chunks if c.modality != "text"]

    current_words = []
    current_meta = None

    for chunk in text_chunks:
        words = chunk.content.split()
        if current_meta is None:
            current_meta = chunk

        current_words.extend(words)

        if len(current_words) >= max_tokens:
            result.append(DocumentChunk(
                chunk_id=str(uuid.uuid4()),
                doc_id=chunk.doc_id,
                source_file=chunk.source_file,
                page_number=current_meta.page_number,
                modality="text",
                content=" ".join(current_words[:max_tokens]),
                section_heading=current_meta.section_heading,
                bbox=current_meta.bbox,
                extraction_confidence=current_meta.extraction_confidence,
            ))
            current_words = current_words[max_tokens - overlap:]
            current_meta = chunk

    if current_words:
        result.append(DocumentChunk(
            chunk_id=str(uuid.uuid4()),
            doc_id=current_meta.doc_id,
            source_file=current_meta.source_file,
            page_number=current_meta.page_number,
            modality="text",
            content=" ".join(current_words),
            section_heading=current_meta.section_heading,
            bbox=current_meta.bbox,
            extraction_confidence=current_meta.extraction_confidence,
        ))

    result.extend(other_chunks)
    return result
