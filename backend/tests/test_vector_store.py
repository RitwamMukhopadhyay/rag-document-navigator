import pytest
from app.rag.vector_store import VectorStore

def test_vector_store_search():
    vstore = VectorStore()
    chunk1 = {
        "chunk_id": "chk_1",
        "document_id": "doc_1",
        "filename": "policy_shipping_returns.pdf",
        "page_number": 1,
        "citation_label": "[policy_shipping_returns.pdf:1]",
        "chunk_index": 1,
        "chunk_text": "Standard delivery takes 3-6 business days. Items returned within 7 days.",
        "token_count": 12,
        "start_char": 0,
        "end_char": 70
    }
    chunk2 = {
        "chunk_id": "chk_2",
        "document_id": "doc_2",
        "filename": "policy_payments_security.pdf",
        "page_number": 1,
        "citation_label": "[policy_payments_security.pdf:1]",
        "chunk_index": 1,
        "chunk_text": "Accepted payment methods include credit cards, debit cards, and UPI.",
        "token_count": 10,
        "start_char": 0,
        "end_char": 65
    }

    vstore.add_chunk(chunk1)
    vstore.add_chunk(chunk2)

    results = vstore.search("delivery timeline standard", top_k=2)
    assert len(results) == 2
    assert results[0].filename == "policy_shipping_returns.pdf"
    assert results[0].citation_label == "[policy_shipping_returns.pdf:1]"
    assert results[0].similarity_score > 0.0
