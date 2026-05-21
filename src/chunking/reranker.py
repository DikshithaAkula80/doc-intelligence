from sentence_transformers import CrossEncoder
from typing import List, Dict

_reranker = None

def get_reranker():
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return _reranker

def rerank(query: str, chunks: List[Dict], top_k: int = 3) -> List[Dict]:
    if not chunks:
        return chunks
    reranker = get_reranker()
    contents = []
    for c in chunks:
        doc = c.get("documents", c.get("content", ""))
        if isinstance(doc, list):
            doc = doc[0]
        contents.append(doc)
    pairs = [[query, c] for c in contents]
    scores = reranker.predict(pairs)
    scored = sorted(zip(scores, chunks), key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]
