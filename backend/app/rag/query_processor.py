import re
from typing import List, Set

class QueryProcessor:
    """Conservative query processing, normalization, and domain-preserved term extraction."""

    # Stopwords that carry little discriminative weight for vector retrieval
    STOPWORDS: Set[str] = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "of", "for", "in", "on", "at", "to", "by", "with", "from", "about",
        "into", "through", "during", "before", "after", "above", "below",
        "what", "how", "why", "which", "who", "whom", "where", "when",
        "does", "do", "did", "can", "could", "should", "would", "may", "might"
    }

    # Protected domain terms that must never be altered or stripped
    DOMAIN_TERMS: Set[str] = {
        "precision@k", "recall@k", "precision@3", "precision@5", "recall@5",
        "rag", "bm25", "cod", "upi", "pdf", "tfidf", "tf-idf", "inr", "pypdf"
    }

    @classmethod
    def normalize(cls, query: str) -> str:
        """Normalizes query string with whitespace stripping and conservative punctuation cleanup."""
        if not query:
            return ""
        
        # Collapse multiple whitespaces
        cleaned = re.sub(r'\s+', ' ', query.strip())
        return cleaned

    @classmethod
    def extract_keywords(cls, query: str) -> List[str]:
        """Extracts key search terms while filtering non-informative stopwords and preserving domain terms."""
        if not query:
            return []

        # Find terms (words, numbers, special domain tokens like precision@k)
        raw_tokens = re.findall(r'[a-zA-Z0-9@_\-]+', query.lower())
        keywords = []
        for token in raw_tokens:
            if token in cls.DOMAIN_TERMS:
                keywords.append(token)
            elif len(token) > 1 and token not in cls.STOPWORDS:
                keywords.append(token)

        return keywords

    @classmethod
    def compute_query_coverage(cls, query: str, chunk_text: str) -> float:
        """Computes ratio of unique non-stopword query keywords present in chunk_text."""
        q_keywords = set(cls.extract_keywords(query))
        if not q_keywords:
            return 0.0
        
        c_text_lower = chunk_text.lower()
        matched = 0
        for kw in q_keywords:
            if kw in c_text_lower:
                matched += 1
        
        return round(matched / len(q_keywords), 4)

    @classmethod
    def check_exact_phrase_match(cls, query: str, chunk_text: str) -> float:
        """Checks for multi-word exact phrase overlap between query and chunk_text."""
        q_norm = cls.normalize(query).lower()
        c_norm = cls.normalize(chunk_text).lower()

        # Extract 2-word and 3-word n-grams from query
        words = cls.extract_keywords(query)
        if len(words) < 2:
            return 1.0 if (words and words[0] in c_norm) else 0.0

        phrases = []
        for i in range(len(words) - 1):
            phrases.append(f"{words[i]} {words[i+1]}")
            if i < len(words) - 2:
                phrases.append(f"{words[i]} {words[i+1]} {words[i+2]}")

        matched_phrases = sum(1 for p in phrases if p in c_norm)
        return round(matched_phrases / max(1, len(phrases)), 4)
