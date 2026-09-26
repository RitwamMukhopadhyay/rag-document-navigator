from typing import Dict, Any, List

class RetrievalPlanner:
    """Generates focused retrieval query strings and parameters based on query classification."""

    @staticmethod
    def create_plan(category: str, question: str, top_k: int = 5) -> Dict[str, Any]:
        # Keep original query primary to preserve exact term weights
        return {
            "category": category,
            "original_query": question,
            "retrieval_query": question.strip(),
            "planned_top_k": top_k
        }

