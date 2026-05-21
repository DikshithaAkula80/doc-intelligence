# Document Intelligence Pipeline

An end-to-end multimodal document intelligence system that ingests PDFs and Word documents, extracts text, tables, and figures, stores them in a vector database, and answers natural language questions with page-level citations.

## Architecture

- **Ingestion** — PDF/DOCX parsing with PyMuPDF, table extraction, figure captioning via LLaVA, OCR fallback for scanned pages
- **Chunking** — semantic splitting with overlap, BAAI/bge-base-en-v1.5 embeddings, ChromaDB vector store
- **Retrieval** — hybrid BM25 + dense search, cross-encoder reranking (ms-marco-MiniLM)
- **Generation** — Mistral 7B via Ollama, answers with page citations
- **API** — FastAPI with /ingest and /query endpoints
- **UI** — Streamlit demo interface

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
brew install tesseract poppler
ollama pull llava:7b
ollama pull mistral:7b
```

## Run

```bash
# Terminal 1 — API server
uvicorn api:app --reload --port 8000

# Terminal 2 — Streamlit UI
streamlit run app.py
```

## API

```bash
# Ingest a document
curl -X POST http://localhost:8000/ingest -F "file=@yourfile.pdf"

# Ask a question
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

## Stack

| Layer | Technology |
|-------|-----------|
| PDF parsing | PyMuPDF |
| Table extraction | PyMuPDF table finder |
| Vision/figures | LLaVA 7B via Ollama |
| OCR | pytesseract |
| Embeddings | BAAI/bge-base-en-v1.5 |
| Vector store | ChromaDB |
| Keyword search | BM25 (rank-bm25) |
| Reranker | cross-encoder/ms-marco-MiniLM-L-6-v2 |
| LLM | Mistral 7B via Ollama |
| API | FastAPI |
| UI | Streamlit |
