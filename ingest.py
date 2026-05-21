import sys
from src.ingestion.pipeline import run_ingestion

if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else "data/raw/sample.pdf"
    chunks = run_ingestion(pdf)
    modalities = {}
    for c in chunks:
        modalities[c.modality] = modalities.get(c.modality, 0) + 1
    print("\nChunk breakdown:", modalities)
