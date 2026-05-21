import chromadb
from sentence_transformers import SentenceTransformer
from typing import List
from src.utils.schema import DocumentChunk

MODEL_NAME = "BAAI/bge-base-en-v1.5"
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def get_collection(persist_dir: str = "data/vectorstore"):
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"}
    )

def store_chunks(chunks: List[DocumentChunk], persist_dir: str = "data/vectorstore"):
    model = get_model()
    collection = get_collection(persist_dir)
    texts = [c.content for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True).tolist()
    collection.upsert(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[{
            "doc_id": c.doc_id,
            "source_file": c.source_file,
            "page_number": c.page_number,
            "modality": c.modality,
            "section_heading": c.section_heading or "",
        } for c in chunks]
    )
    print(f"Stored {len(chunks)} chunks in vector store.")

def search(query: str, n_results: int = 5, persist_dir: str = "data/vectorstore"):
    model = get_model()
    collection = get_collection(persist_dir)
    query_embedding = model.encode([query], normalize_embeddings=True).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    return results
