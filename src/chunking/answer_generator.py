import requests
from typing import List, Dict

def generate_answer(query: str, retrieved_chunks: List[Dict]) -> Dict:
    context = ""
    for chunk in retrieved_chunks:
        meta = chunk.get("metadatas", chunk)
        page = meta.get("page_number", "?") if isinstance(meta, dict) else "?"
        content = chunk.get("documents", chunk.get("content", ""))
        if isinstance(content, list):
            content = content[0]
        context += f"[Source: page {page}]\n{content}\n\n"

    prompt = f"""You are a precise document assistant. Answer the question using ONLY the context below.
Always cite the page number in your answer. If the answer is not in the context, say "I could not find this in the document."

Context:
{context}

Question: {query}

Answer:"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "mistral:7b", "prompt": prompt, "stream": False},
            timeout=120,
        )
        answer = response.json().get("response", "").strip()
    except Exception as e:
        answer = f"[generation failed: {e}]"

    citations = []
    for chunk in retrieved_chunks:
        meta = chunk.get("metadatas", chunk)
        if isinstance(meta, list):
            meta = meta[0]
        citations.append({
            "page": meta.get("page_number", "?"),
            "source_file": meta.get("source_file", "?"),
            "section": meta.get("section_heading", ""),
        })

    confidence = _score_confidence(query, answer, retrieved_chunks)

    return {
        "answer": answer,
        "citations": citations,
        "confidence": confidence,
        "confidence_label": _confidence_label(confidence)
    }

def _score_confidence(query: str, answer: str, chunks: List[Dict]) -> float:
    score = 0.0
    if chunks:
        score += 0.4
    if answer and "could not find" not in answer.lower():
        score += 0.3
    query_words = set(query.lower().split())
    answer_words = set(answer.lower().split())
    overlap = len(query_words & answer_words) / max(len(query_words), 1)
    score += min(0.3, overlap)
    return round(min(1.0, score), 2)

def _confidence_label(score: float) -> str:
    if score >= 0.8:
        return "High"
    elif score >= 0.5:
        return "Medium"
    else:
        return "Low"
