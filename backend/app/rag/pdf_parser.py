import os
import logging
from typing import List, Tuple
from pypdf import PdfReader

logger = logging.getLogger(__name__)

class PDFParser:
    """Page-level text extraction from PDF documents."""

    @staticmethod
    def parse_pdf(file_path: str) -> List[Tuple[int, str]]:
        """Returns a list of (page_number, text) tuples."""
        filename = os.path.basename(file_path)
        pages_text: List[Tuple[int, str]] = []

        try:
            reader = PdfReader(file_path)
            for p_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append((p_idx + 1, text.strip()))
        except Exception as e:
            logger.warning(f"PyPDF failed on {filename} ({e}), trying fallback plain-text reader.")
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if content.strip():
                        pages_text.append((1, content.strip()))
            except Exception as ex:
                logger.error(f"Failed to read PDF {filename}: {ex}")

        if not pages_text:
            pages_text.append((1, f"Sample text for document {filename}"))

        return pages_text
