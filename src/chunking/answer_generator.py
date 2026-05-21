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

    return {"answer": answer, "citations": citations}
