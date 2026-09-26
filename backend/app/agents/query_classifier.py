import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class QueryClassifier:
    """Classifies questions into policy, RAG-concept, support-escalation, or unknown."""

    CATEGORIES = ["policy", "RAG-concept", "support-escalation", "unknown"]

    @staticmethod
    def classify(question: str) -> Tuple[str, float]:
        q_lower = question.lower()

        if any(w in q_lower for w in ["policy", "shipping", "delivery", "return", "refund", "payment", "card", "cash on delivery", "privacy"]):
            return "policy", 0.95

        if any(w in q_lower for w in ["rag", "chunk", "chunking", "token", "vector", "embedding", "search", "hybrid", "precision", "citation", "system prompt", "logging"]):
            return "RAG-concept", 0.95

        if any(w in q_lower for w in ["support", "escalat", "human agent", "agent", "verification", "identity"]):
            return "support-escalation", 0.90

        return "unknown", 0.60
