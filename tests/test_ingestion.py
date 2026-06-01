from pathlib import Path

from src.ingest import PDFIngestionEngine


def test_chunk_text_returns_empty_for_blank_text() -> None:
    engine = PDFIngestionEngine()
    chunks = engine.chunk_text("")
    assert chunks == []


def test_extract_text_raises_for_missing_file() -> None:
    engine = PDFIngestionEngine()
    missing_path = Path("does_not_exist.pdf")
    try:
        engine.extract_text(missing_path)
    except FileNotFoundError as exc:
        assert "PDF file not found" in str(exc)
    else:
        raise AssertionError("Expected FileNotFoundError")
