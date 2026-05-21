import json
import glob
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from src.ingestion.pipeline import run_ingestion
from src.chunking.semantic_chunker import semantic_chunk
from src.chunking.vector_store import store_chunks, search
from src.chunking.bm25_search import build_bm25, bm25_search, load_chunks_from_file
from src.chunking.reranker import rerank
from src.chunking.answer_generator import generate_answer

app = FastAPI(title="Document Intelligence API")

class QueryRequest(BaseModel):
    question: str
    n_results: int = 5

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    allowed = (".pdf", ".docx")
    if not any(file.filename.endswith(ext) for ext in allowed):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    tmp_path = f"data/raw/{file.filename}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        chunks = run_ingestion(tmp_path)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    chunks = semantic_chunk(chunks)
    store_chunks(chunks)
    return {
        "status": "success",
        "doc_id": chunks[0].doc_id if chunks else None,
        "total_chunks": len(chunks),
        "breakdown": {m: sum(1 for c in chunks if c.modality == m) for m in set(c.modality for c in chunks)}
    }

@app.post("/query")
async def query(req: QueryRequest):
    dense_results = search(req.question, n_results=req.n_results)
    flat = []
    if dense_results and dense_results["documents"]:
        for doc, meta in zip(dense_results["documents"][0], dense_results["metadatas"][0]):
            flat.append({"documents": doc, "metadatas": meta})

    files = sorted(glob.glob("data/processed/*_chunks.json"))
    if files:
        raw_chunks = load_chunks_from_file(files[-1])
        bm25, chunks = build_bm25(raw_chunks)
        bm25_results = bm25_search(req.question, bm25, raw_chunks, n=req.n_results)
        seen = {c["documents"] for c in flat}
        for c in bm25_results:
            if c["content"] not in seen:
                flat.append({"documents": c["content"], "metadatas": c})

    reranked = rerank(req.question, flat, top_k=3)
    result = generate_answer(req.question, reranked)
    return result

@app.get("/health")
def health():
    return {"status": "ok"}
