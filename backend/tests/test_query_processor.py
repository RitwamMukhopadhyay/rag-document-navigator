import pytest
from app.rag.query_processor import QueryProcessor

def test_query_normalize():
    raw_query = "  What   is   the   standard  delivery   timeline?  "
    normalized = QueryProcessor.normalize(raw_query)
    assert normalized == "What is the standard delivery timeline?"

def test_empty_and_whitespace_query():
    assert QueryProcessor.normalize("") == ""
    assert QueryProcessor.extract_keywords("") == []
    assert QueryProcessor.compute_query_coverage("", "some text") == 0.0

def test_extract_keywords_preserves_domain_terms():
    query = "What is Precision@k and BM25 in RAG evaluation?"
    keywords = QueryProcessor.extract_keywords(query)
    assert "precision@k" in keywords
    assert "bm25" in keywords
    assert "rag" in keywords
    assert "evaluation" in keywords
    # Stopwords should be filtered out
    assert "what" not in keywords
    assert "is" not in keywords
    assert "in" not in keywords

def test_compute_query_coverage():
    query = "standard delivery timeline"
    text_match = "The standard delivery timeline for shipping is 3-6 business days."
    text_no_match = "Personal data encryption details and privacy rules."
    
    cov_match = QueryProcessor.compute_query_coverage(query, text_match)
    cov_no_match = QueryProcessor.compute_query_coverage(query, text_no_match)
    
    assert cov_match == 1.0
    assert cov_no_match == 0.0

def test_check_exact_phrase_match():
    query = "standard delivery timeline"
    text_exact = "Our standard delivery timeline is 3-6 business days."
    text_partial = "Delivery of timeline items is standard procedure."
    
    phrase_score_exact = QueryProcessor.check_exact_phrase_match(query, text_exact)
    phrase_score_partial = QueryProcessor.check_exact_phrase_match(query, text_partial)
    
    assert phrase_score_exact > 0.5
    assert phrase_score_exact > phrase_score_partial
