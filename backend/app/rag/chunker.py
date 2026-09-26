import uuid
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class TextChunker:
    """Configurable text chunking with exact filename:page metadata tracking."""

    @staticmethod
    def chunk_document(
        filename: str,
        document_id: str,
        page_number: int,
        page_text: str,
        chunk_size: int = 600,
        overlap: int = 80
    ) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []

        words = page_text.split()
        if not words:
            return chunks

        # If page_text is smaller than chunk_size, create single chunk
        if len(words) <= chunk_size:
            chunk_id = f"chk_{uuid.uuid4().hex[:12]}"
            citation_label = f"[{filename}:{page_number}]"
            chunks.append({
                "chunk_id": chunk_id,
                "document_id": document_id,
                "filename": filename,
                "page_number": page_number,
                "citation_label": citation_label,
                "chunk_index": 1,
                "chunk_text": page_text,
                "token_count": len(words),
                "start_char": 0,
                "end_char": len(page_text)
            })
            return chunks

        # Sliding window chunking
        step = max(1, chunk_size - overlap)
        chunk_idx = 1

        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size]
            chunk_str = " ".join(chunk_words)
            chunk_id = f"chk_{uuid.uuid4().hex[:12]}"
            citation_label = f"[{filename}:{page_number}]"

            chunks.append({
                "chunk_id": chunk_id,
                "document_id": document_id,
                "filename": filename,
                "page_number": page_number,
                "citation_label": citation_label,
                "chunk_index": chunk_idx,
                "chunk_text": chunk_str,
                "token_count": len(chunk_words),
                "start_char": i,
                "end_char": i + len(chunk_str)
            })
            chunk_idx += 1

            if i + chunk_size >= len(words):
                break

        return chunks
