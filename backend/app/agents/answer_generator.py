import re
import logging
from typing import List, Tuple
from app.schemas.schemas import RetrievedChunkSchema

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE_MSG = (
    "Insufficient evidence found in the document index to answer this question. "
    "Please refine your search query or upload relevant policy/guide documents."
)

class AnswerGenerator:
    """Generates grounded answers strictly using the highest-relevance retrieved chunk and enforces [filename:page] citations."""

    @staticmethod
    def generate_grounded_answer(
        question: str,
        retrieved: List[RetrievedChunkSchema],
        confidence: str
    ) -> Tuple[str, List[str], List[str]]:
        
        citations: List[str] = []
        limitations: List[str] = []

        if confidence == "Insufficient Evidence" or not retrieved:
            return INSUFFICIENT_EVIDENCE_MSG, [], ["No relevant source chunks met the similarity threshold."]

        # Highest-relevance supporting chunk primary citation
        top_chunk = retrieved[0]
        label = f"[{top_chunk.filename}:{top_chunk.page_number}]"
        citations.append(label)

        # Aggregate unique citations for additional supporting chunks (score >= 0.25)
        for chunk in retrieved[1:]:
            chk_label = f"[{chunk.filename}:{chunk.page_number}]"
            if chk_label not in citations and chunk.similarity_score >= 0.25:
                citations.append(chk_label)

        raw_text = top_chunk.chunk_text.strip()
        lines = [l.strip() for l in raw_text.split("\n") if l.strip()]

        # Filter out document title lines and synthetic disclaimers
        clean_lines = []
        for line in lines:
            if line.endswith("(Sample)") or "Policy (Sample)" in line or "Guide (Sample)" in line:
                continue
            if "synthetic and intended for capstone" in line.lower():
                continue
            # Strip item numbers e.g. "1. ", "2. ", "- "
            item_text = re.sub(r"^\d+\.\s*", "", line)
            item_text = re.sub(r"^[\-\*]\s*", "", item_text).strip()
            if item_text:
                clean_lines.append(item_text)

        if not clean_lines:
            clean_lines = [raw_text]

        # Match relevant 1-3 sentences based on question terms
        stop_words = {"what", "is", "the", "a", "an", "of", "in", "for", "to", "how", "why", "when", "are", "do", "does", "or", "and", "on", "with", "by", "from", "be"}
        q_words = set(re.findall(r"\w+", question.lower())) - stop_words

        matched_lines = []
        for line in clean_lines:
            line_words = set(re.findall(r"\w+", line.lower()))
            overlap = len(q_words.intersection(line_words))
            if overlap > 0:
                matched_lines.append((overlap, line))

        if matched_lines:
            # Sort by keyword overlap descending, select top matching points (up to 2-3)
            matched_lines.sort(key=lambda x: x[0], reverse=True)
            selected_text = " ".join([m[1] for m in matched_lines[:2]])
        else:
            # Fallback to first 1-2 points of top chunk
            selected_text = " ".join(clean_lines[:2])

        selected_text = selected_text.strip()
        if not selected_text.endswith("."):
            selected_text += "."

        # Format concise answer with citation appended
        answer_text = f"{selected_text} {label}"

        if confidence == "Low":
            limitations.append("Confidence is Low due to low similarity scores across index. Verify against original PDFs.")

        return answer_text, citations, limitations
