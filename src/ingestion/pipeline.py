import uuid
import json
from pathlib import Path
from typing import List
from rich.console import Console
from src.utils.schema import DocumentChunk
from src.utils.validator import validate_file
from src.extraction.text_extractor import extract_text_chunks
from src.extraction.image_extractor import extract_image_regions
from src.extraction.figure_captioner import caption_figures
from src.extraction.ocr_extractor import ocr_pdf
from src.extraction.table_extractor import extract_tables
from src.extraction.docx_extractor import extract_docx_chunks

console = Console()

def run_ingestion(pdf_path: str, output_dir: str = "data/processed") -> List[DocumentChunk]:
    validation = validate_file(pdf_path)
    if not validation["valid"]:
        console.print(f"[red]✗ Validation failed: {validation['error']}[/red]")
        raise ValueError(validation["error"])

    ext = Path(pdf_path).suffix.lower()
    doc_id = uuid.uuid4().hex[:12]
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    images_dir = output_dir / "images" / doc_id
    all_chunks = []

    console.print(f"\n[bold]Processing:[/bold] {pdf_path}")
    console.print(f"[dim]doc_id: {doc_id}[/dim]\n")

    if ext == ".docx":
        console.print("[cyan]→ Extracting from Word document...[/cyan]")
        chunks = extract_docx_chunks(pdf_path, doc_id)
        console.print(f"  [green]✓[/green] {len(chunks)} chunks from docx")
        all_chunks.extend(chunks)
    else:
        console.print("[cyan]→ Extracting text blocks...[/cyan]")
        text_chunks = extract_text_chunks(pdf_path, doc_id)
        console.print(f"  [green]✓[/green] {len(text_chunks)} text chunks")
        all_chunks.extend(text_chunks)

        console.print("[cyan]→ Extracting tables...[/cyan]")
        table_chunks = extract_tables(pdf_path, doc_id)
        console.print(f"  [green]✓[/green] {len(table_chunks)} tables found")
        all_chunks.extend(table_chunks)

        console.print("[cyan]→ Extracting image regions...[/cyan]")
        image_regions = extract_image_regions(pdf_path, str(images_dir))
        console.print(f"  [green]✓[/green] {len(image_regions)} image regions found")

        if image_regions:
            console.print("[cyan]→ Captioning figures via LLaVA...[/cyan]")
            figure_chunks = caption_figures(image_regions, doc_id)
            console.print(f"  [green]✓[/green] {len(figure_chunks)} figures captioned")
            all_chunks.extend(figure_chunks)

        console.print("[cyan]→ Checking for scanned pages...[/cyan]")
        ocr_chunks = ocr_pdf(pdf_path, doc_id)
        if ocr_chunks:
            console.print(f"  [green]✓[/green] {len(ocr_chunks)} scanned pages OCR'd")
        else:
            console.print("  [dim]No scanned pages detected[/dim]")
        all_chunks.extend(ocr_chunks)

    out_file = output_dir / f"{doc_id}_chunks.json"
    with open(out_file, "w") as f:
        json.dump([c.model_dump() for c in all_chunks], f, indent=2)

    console.print(f"\n[bold green]Done.[/bold green] {len(all_chunks)} total chunks → {out_file}\n")
    return all_chunks
