import fitz
from pathlib import Path

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_MB = 50

def validate_file(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        return {"valid": False, "error": "File not found."}

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"valid": False, "error": f"Unsupported file type '{ext}'. Supported: PDF, DOCX."}

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return {"valid": False, "error": f"File too large ({size_mb:.1f}MB). Maximum is {MAX_FILE_SIZE_MB}MB."}

    if ext == ".pdf":
        try:
            doc = fitz.open(file_path)
            if doc.needs_pass:
                return {"valid": False, "error": "PDF is password-protected. Please upload an unlocked version."}
            if len(doc) == 0:
                return {"valid": False, "error": "PDF has no pages."}
            doc.close()
        except Exception as e:
            return {"valid": False, "error": f"PDF appears corrupted: {str(e)}"}

    return {"valid": True, "error": None}
