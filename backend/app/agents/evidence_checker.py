from typing import List, Tuple, Dict, Any
from app.schemas.schemas import RetrievedChunkSchema

class EvidenceChecker:
    """Evaluates evidence sufficiency, similarity score threshold, chunk agreement, and confidence rating."""

    SCORE_THRESHOLD_HIGH = 0.40
    SCORE_THRESHOLD_MEDIUM = 0.25
    SCORE_THRESHOLD_MINIMUM = 0.12

    @staticmethod
    def evaluate(retrieved: List[RetrievedChunkSchema]) -> Tuple[str, bool, str]:
        """Returns (confidence_level, is_sufficient, detail_message)."""
        if not retrieved:
            return "Insufficient Evidence", False, "No source chunks retrieved matching query parameters."

        max_score = max(c.similarity_score for c in retrieved)

        # Count chunks that provide supporting relevance (score >= 0.20)
        supporting_chunks = [c for c in retrieved if c.similarity_score >= EvidenceChecker.SCORE_THRESHOLD_MEDIUM]
        unique_docs = set(c.filename for c in supporting_chunks)

        if max_score >= EvidenceChecker.SCORE_THRESHOLD_HIGH:
            detail = f"Strong evidence retrieved (Max similarity score: {max_score:.2f}, {len(supporting_chunks)} chunk(s) across {len(unique_docs)} document(s))."
            return "High", True, detail
        elif max_score >= EvidenceChecker.SCORE_THRESHOLD_MEDIUM:
            detail = f"Moderate evidence retrieved (Max similarity score: {max_score:.2f}, {len(supporting_chunks)} chunk(s) supporting answer)."
            return "Medium", True, detail
        elif max_score >= EvidenceChecker.SCORE_THRESHOLD_MINIMUM:
            detail = f"Weak evidence retrieved (Max similarity score: {max_score:.2f}). Re-retrieval or verification recommended."
            return "Low", True, detail
        else:
            detail = f"Evidence score below threshold ({max_score:.2f} < {EvidenceChecker.SCORE_THRESHOLD_MINIMUM}). Safe refusal triggered."
            return "Insufficient Evidence", False, detail

