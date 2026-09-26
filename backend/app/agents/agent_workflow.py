import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.schemas.schemas import (
    AgentWorkflowRequest,
    AgentWorkflowResponse,
    RetrievedChunkSchema,
    RetrievalTraceStep,
)
from app.rag.vector_store import global_vector_store
from app.agents.query_classifier import QueryClassifier
from app.agents.retrieval_planner import RetrievalPlanner
from app.agents.evidence_checker import EvidenceChecker
from app.agents.answer_generator import AnswerGenerator
from app.models.models import QueryLogModel

logger = logging.getLogger(__name__)

class AgentWorkflowEngine:
    """Transparent 6-state agentic RAG workflow state machine."""

    @staticmethod
    def run_agentic_rag(
        req: AgentWorkflowRequest,
        db: Optional[Session] = None
    ) -> AgentWorkflowResponse:
        t0 = time.time()
        traces: List[RetrievalTraceStep] = []
        step_num = 1

        def add_trace(step_name: str, details: str):
            nonlocal step_num
            traces.append(
                RetrievalTraceStep(
                    step_number=step_num,
                    step_name=step_name,
                    details=details,
                    timestamp=datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
                )
            )
            step_num += 1

        # State 1: Query Analysis
        category, cat_score = QueryClassifier.classify(req.question)
        add_trace(
            "1. Query Analysis",
            f"Classified query category as '{category}' (confidence: {cat_score:.2f})."
        )

        # State 2: Retrieval Plan
        plan = RetrievalPlanner.create_plan(category, req.question, req.top_k)
        add_trace(
            "2. Retrieval Plan",
            f"Planned vector search with query '{plan['retrieval_query']}' and top_k={req.top_k}."
        )

        # State 3: Retrieve (Attempt 1)
        attempt_num = 1
        retrieved_chunks = global_vector_store.search(plan["retrieval_query"], top_k=req.top_k)
        add_trace(
            "3. Retrieve (Attempt 1)",
            f"Retrieved {len(retrieved_chunks)} source chunks from vector index."
        )

        # State 4: Evidence Check
        confidence, is_sufficient, ev_details = EvidenceChecker.evaluate(retrieved_chunks)
        add_trace("4. Evidence Check", f"Assessed evidence quality: Confidence='{confidence}'. {ev_details}")

        # State 5: Re-retrieve (Attempt 2 if weak evidence)
        if not is_sufficient or confidence == "Low":
            attempt_num = 2
            add_trace(
                "5. Re-retrieve (Attempt 2)",
                "Triggering single re-retrieval attempt with hybrid query expansion and top_k boost."
            )
            retry_query = f"{req.question} policy guide summary details"
            retrieved_chunks = global_vector_store.search(retry_query, top_k=req.top_k + 2)
            confidence, is_sufficient, ev_details = EvidenceChecker.evaluate(retrieved_chunks)
            add_trace(
                "5. Re-retrieve Evaluation",
                f"Re-retrieval completed ({len(retrieved_chunks)} chunks). Updated confidence='{confidence}'."
            )

        # State 6: Answer Generation & Citation Guard
        answer, citations, limitations = AnswerGenerator.generate_grounded_answer(
            req.question, retrieved_chunks, confidence
        )
        add_trace(
            "6. Answer & Citation Guard",
            f"Generated grounded answer with {len(citations)} citations {citations} and confidence '{confidence}'."
        )

        elapsed = round(time.time() - t0, 3)
        searched_docs_count = len(set(c.get("filename") for c in global_vector_store.chunks_db if c.get("filename")))
        best_score = round(max([c.similarity_score for c in retrieved_chunks], default=0.0), 4)

        response_data = AgentWorkflowResponse(
            question=req.question,
            answer=answer,
            citations=citations,
            confidence=confidence,
            retrieval_trace=traces,
            limitations=limitations,
            retrieved_chunks=retrieved_chunks,
            execution_time_seconds=elapsed,
            total_documents_searched=searched_docs_count,
            best_match_score=best_score,
            embedding_model="Deterministic 128-dim N-Gram Vector Hash",
            llm_model="Grounded Agentic Synthesizer v1.0"
        )

        # Log query to SQLite if DB session is provided
        if db is not None:
            try:
                log_entry = QueryLogModel(
                    question=req.question,
                    intent_category=category,
                    top_k=req.top_k,
                    chunk_size=req.chunk_size,
                    overlap=req.overlap,
                    confidence_level=confidence,
                    response_json=response_data.model_dump(mode="json")
                )
                db.add(log_entry)
                db.commit()
            except Exception as e:
                logger.warning(f"Failed to log query execution to DB: {e}")

        return response_data
