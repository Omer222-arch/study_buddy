from __future__ import annotations

from pathlib import Path
from typing import List

from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from pypdf import PdfReader


class PDFIngestionEngine:
    """Extracts text from PDF files and chunks it for semantic indexing."""

    def __init__(self, chunk_size: int = 750, chunk_overlap: int = 75):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " "]
        )

    def extract_text(self, pdf_path: Path) -> str:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        reader = PdfReader(pdf_path)
        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            pages.append(text)
        return "\n\n".join(pages)

    def chunk_text(self, text: str) -> List[str]:
        if not text.strip():
            return []
        return self.text_splitter.split_text(text)

    def ingest_pdf(self, pdf_path: Path) -> List[str]:
        raw_text = self.extract_text(pdf_path)
        chunks = self.chunk_text(raw_text)
        return chunks
