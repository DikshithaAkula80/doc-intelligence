import json
from rank_bm25 import BM25Okapi
from typing import List, Dict

def load_chunks_from_file(json_path: str) -> List[Dict]:
    with open(json_path) as f:
        return json.load(f)

def build_bm25(chunks: List[Dict]):
    tokenized = [c["content"].lower().split() for c in chunks]
    return BM25Okapi(tokenized), chunks

def bm25_search(query: str, bm25, chunks: List[Dict], n: int = 5) -> List[Dict]:
    tokens = query.lower().split()
    scores = bm25.get_scores(tokens)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]
    return [chunks[i] for i in top_indices]
