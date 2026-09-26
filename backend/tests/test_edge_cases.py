import io
import pytest
from app.db.session import SessionLocal
from app.rag.query_processor import QueryProcessor
from app.rag.vector_store import VectorStore, compute_embedding
from app.rag.ingestion_service import IngestionService
from app.agents.evidence_checker import EvidenceChecker
from app.agents.answer_generator import AnswerGenerator, INSUFFICIENT_EVIDENCE_MSG
from app.schemas.schemas import AgentWorkflowRequest, RetrievedChunkSchema
from app.agents.agent_workflow import AgentWorkflowEngine

def test_edge_case_1_empty_query():
    store = VectorStore()
    results = store.search("", top_k=5)
    assert results == []

def test_edge_case_2_very_short_query():
    store = VectorStore()
    store.add_chunk({
        "chunk_id": "c1",
        "filename": "doc.pdf",
        "page_number": 1,
        "chunk_text": "Shipping policy details and timeline.",
        "embedding": compute_embedding("Shipping policy details and timeline.")
    })
    results = store.search("a", top_k=5)
    assert isinstance(results, list)

def test_edge_case_3_very_long_query():
    store = VectorStore()
    long_query = "What is the standard delivery timeline for shipping orders placed on weekdays " * 20
    results = store.search(long_query, top_k=3)
    assert isinstance(results, list)

def test_edge_case_4_no_relevant_document_in_index():
    store = VectorStore()
    store.add_chunk({
        "chunk_id": "c1",
        "filename": "cooking.pdf",
        "page_number": 1,
        "chunk_text": "Baking bread requires flour, water, yeast, and salt.",
        "embedding": compute_embedding("Baking bread requires flour, water, yeast, and salt.")
    })
    results = store.search("quantum mechanics entropy calculation", top_k=3)
    assert len(results) > 0
    # Score should be low
    assert results[0].similarity_score < 0.20

def test_edge_case_5_duplicate_document_detection():
    db = SessionLocal()
    try:
        pdf_bytes = b"%PDF-1.4 sample pdf content for testing duplicate detection"
        res1 = IngestionService.ingest_single_pdf(pdf_bytes, "test_dup.pdf", db)
        assert res1.status in ["success", "duplicate"]
        
        # Ingesting exact same PDF content again
        res2 = IngestionService.ingest_single_pdf(pdf_bytes, "test_dup.pdf", db)
        assert res2.status == "duplicate"
        assert "already exists" in res2.message.lower() or "duplicate" in res2.message.lower()
    finally:
        db.close()

def test_edge_case_6_duplicate_chunks_handling():
    store = VectorStore()
    store.add_chunk({
        "chunk_id": "c1",
        "filename": "doc1.pdf",
        "page_number": 1,
        "chunk_text": "Identical chunk text for testing.",
        "embedding": compute_embedding("Identical chunk text for testing.")
    })
    store.add_chunk({
        "chunk_id": "c2",
        "filename": "doc2.pdf",
        "page_number": 1,
        "chunk_text": "Identical chunk text for testing.",
        "embedding": compute_embedding("Identical chunk text for testing.")
    })
    results = store.search("identical chunk text", top_k=2)
    assert len(results) == 2
    # Second chunk penalized by MMR redundancy check
    assert results[0].similarity_score >= results[1].similarity_score

def test_edge_case_7_multiple_relevant_documents():
    store = VectorStore()
    store.add_chunk({
        "chunk_id": "c1",
        "filename": "policy_a.pdf",
        "page_number": 1,
        "chunk_text": "Standard shipping delivery takes 3 business days.",
        "embedding": compute_embedding("Standard shipping delivery takes 3 business days.")
    })
    store.add_chunk({
        "chunk_id": "c2",
        "filename": "policy_b.pdf",
        "page_number": 1,
        "chunk_text": "Express delivery takes 1 business day for shipping.",
        "embedding": compute_embedding("Express delivery takes 1 business day for shipping.")
    })
    results = store.search("delivery shipping timeline", top_k=2)
    assert len(results) == 2
    files = [c.filename for c in results]
    assert "policy_a.pdf" in files
    assert "policy_b.pdf" in files

def test_edge_case_8_corrupted_pdf_handling():
    db = SessionLocal()
    try:
        bad_bytes = b"This is not a valid PDF header"
        res = IngestionService.ingest_single_pdf(bad_bytes, "corrupt.pdf", db)
        # Should handle gracefully without crashing
        assert res.status in ["error", "success", "duplicate"]
    finally:
        db.close()

def test_edge_case_9_empty_pdf_handling():
    db = SessionLocal()
    try:
        empty_bytes = b"%PDF-1.4 %EOF"
        res = IngestionService.ingest_single_pdf(empty_bytes, "empty.pdf", db)
        assert res.status in ["error", "success", "duplicate"]
    finally:
        db.close()

def test_edge_case_10_image_scanned_pdf():
    db = SessionLocal()
    try:
        # Minimal PDF structure with no extractable text stream
        scanned_bytes = b"%PDF-1.4 1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj 2 0 obj << /Type /Pages /Kids [] /Count 0 >> endobj xref 0 3 0000000000 65535 f 0000000009 00000 n 0000000058 00000 n trailer << /Size 3 /Root 1 0 R >> startxref 109 %%EOF"
        res = IngestionService.ingest_single_pdf(scanned_bytes, "scanned.pdf", db)
        assert res.status in ["error", "success", "duplicate"]
    finally:
        db.close()

def test_edge_case_11_unusual_unicode_characters():
    store = VectorStore()
    text = "Payment accepted via UPI 💳, Credit Card 🔒, and ₹ INR currency!"
    store.add_chunk({
        "chunk_id": "c1",
        "filename": "unicode_doc.pdf",
        "page_number": 1,
        "chunk_text": text,
        "embedding": compute_embedding(text)
    })
    results = store.search("UPI payment INR", top_k=1)
    assert len(results) == 1
    assert "UPI" in results[0].chunk_text

def test_edge_case_12_multi_evidence_query():
    chunks = [
        RetrievedChunkSchema(
            chunk_id="c1", filename="policy_shipping_returns.pdf", page_number=1,
            citation_label="[policy_shipping_returns.pdf:1]",
            chunk_text="Standard shipping takes 3-6 days. Returns are accepted within 30 days.",
            similarity_score=0.85, rank=1
        ),
        RetrievedChunkSchema(
            chunk_id="c2", filename="policy_payments_security.pdf", page_number=1,
            citation_label="[policy_payments_security.pdf:1]",
            chunk_text="UPI and Credit cards accepted. Refunds take 5-7 days.",
            similarity_score=0.75, rank=2
        )
    ]
    answer, citations, limits = AnswerGenerator.generate_grounded_answer(
        "What are shipping and return terms?", chunks, "High"
    )
    assert "[policy_shipping_returns.pdf:1]" in citations

def test_edge_case_13_unsupported_question_safe_refusal():
    chunks = []
    answer, citations, limits = AnswerGenerator.generate_grounded_answer(
        "What is the airspeed velocity of an unladen swallow?", chunks, "Insufficient Evidence"
    )
    assert answer == INSUFFICIENT_EVIDENCE_MSG
    assert citations == []

def test_edge_case_14_low_similarity_score_handling():
    chunks = [
        RetrievedChunkSchema(
            chunk_id="c1", filename="doc.pdf", page_number=1,
            citation_label="[doc.pdf:1]",
            chunk_text="Irrelevant text snippet.",
            similarity_score=0.05, rank=1
        )
    ]
    conf, is_sufficient, msg = EvidenceChecker.evaluate(chunks)
    assert conf == "Insufficient Evidence"
    assert is_sufficient is False

def test_edge_case_15_citation_validation_failure_prevention():
    chunk = RetrievedChunkSchema(
        chunk_id="c1", filename="guide_rag_basics.pdf", page_number=1,
        citation_label="[guide_rag_basics.pdf:1]",
        chunk_text="RAG combines retrieval with generative text generation.",
        similarity_score=0.90, rank=1
    )
    answer, citations, limits = AnswerGenerator.generate_grounded_answer(
        "What is RAG?", [chunk], "High"
    )
    assert "[guide_rag_basics.pdf:1]" in answer
    assert citations == ["[guide_rag_basics.pdf:1]"]
    # Ensure citation corresponds strictly to actual retrieved chunk filename and page
    assert citations[0] == f"[{chunk.filename}:{chunk.page_number}]"
