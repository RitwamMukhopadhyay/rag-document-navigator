import pytest
from app.rag.chunker import TextChunker

def test_chunk_preserves_filename_and_page():
    filename = "policy_shipping_returns.pdf"
    page_num = 1
    page_text = "Standard delivery takes 3 to 6 business days. Returns must be initiated within 7 days of receipt."

    chunks = TextChunker.chunk_document(
        filename=filename,
        document_id="doc-123",
        page_number=page_num,
        page_text=page_text,
        chunk_size=600,
        overlap=80
    )

    assert len(chunks) == 1
    chunk = chunks[0]
    assert chunk["filename"] == filename
    assert chunk["page_number"] == page_num
    assert chunk["citation_label"] == "[policy_shipping_returns.pdf:1]"
    assert "Standard delivery" in chunk["chunk_text"]
