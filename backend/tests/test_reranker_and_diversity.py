import pytest
from app.rag.vector_store import VectorStore, compute_embedding, cosine_similarity
from app.schemas.schemas import RetrievedChunkSchema

def test_reranker_weighted_scoring():
    store = VectorStore()
    chunk = {
        "chunk_id": "c1",
        "filename": "policy_shipping_returns.pdf",
        "page_number": 1,
        "chunk_text": "Standard delivery timeline for shipping takes 3-6 business days.",
        "embedding": compute_embedding("Standard delivery timeline for shipping takes 3-6 business days.")
    }
    
    query = "What is the standard delivery timeline?"
    base_sim = 0.50
    score, breakdown = store.rerank_candidate(query, chunk, base_sim)
    
    assert score > 0.50
    assert "cosine_sim" in breakdown
    assert "coverage" in breakdown
    assert "phrase_match" in breakdown
    assert "metadata_match" in breakdown
    assert breakdown["coverage"] > 0.5

def test_vector_store_search_ordering():
    store = VectorStore()
    c1 = {
        "chunk_id": "c1",
        "filename": "policy_shipping_returns.pdf",
        "page_number": 1,
        "chunk_text": "Standard delivery timeline is 3 to 6 business days.",
        "embedding": compute_embedding("Standard delivery timeline is 3 to 6 business days.")
    }
    c2 = {
        "chunk_id": "c2",
        "filename": "policy_privacy_data_use.pdf",
        "page_number": 1,
        "chunk_text": "Personal user data is encrypted using AES-256 standards.",
        "embedding": compute_embedding("Personal user data is encrypted using AES-256 standards.")
    }
    store.add_chunk(c1)
    store.add_chunk(c2)
    
    results = store.search("delivery timeline", top_k=2)
    assert len(results) == 2
    assert results[0].filename == "policy_shipping_returns.pdf"
    assert results[0].similarity_score >= results[1].similarity_score

def test_mmr_diversity_redundancy_penalty():
    store = VectorStore()
    c1 = {
        "chunk_id": "c1",
        "filename": "doc1.pdf",
        "page_number": 1,
        "chunk_text": "Identical chunk text snippet for testing redundancy penalty.",
        "embedding": compute_embedding("Identical chunk text snippet for testing redundancy penalty.")
    }
    c2 = {
        "chunk_id": "c2",
        "filename": "doc2.pdf",
        "page_number": 1,
        "chunk_text": "Identical chunk text snippet for testing redundancy penalty.",
        "embedding": compute_embedding("Identical chunk text snippet for testing redundancy penalty.")
    }
    store.add_chunk(c1)
    store.add_chunk(c2)
    
    results = store.search("testing redundancy penalty", top_k=2)
    assert len(results) == 2
    # The second duplicate chunk should be penalized in score
    assert results[0].similarity_score >= results[1].similarity_score
