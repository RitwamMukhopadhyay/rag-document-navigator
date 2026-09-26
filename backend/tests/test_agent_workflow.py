import pytest
from app.schemas.schemas import AgentWorkflowRequest
from app.agents.agent_workflow import AgentWorkflowEngine
from app.agents.query_classifier import QueryClassifier

def test_query_classifier():
    cat1, _ = QueryClassifier.classify("What is the standard delivery timeline?")
    assert cat1 == "policy"

    cat2, _ = QueryClassifier.classify("What chunk size is recommended for narrative PDFs?")
    assert cat2 == "RAG-concept"

def test_agent_workflow_execution():
    req = AgentWorkflowRequest(
        question="What is the standard delivery timeline?",
        top_k=3,
        chunk_size=600,
        overlap=80
    )
    res = AgentWorkflowEngine.run_agentic_rag(req)
    assert res.question == req.question
    assert res.confidence in ["High", "Medium", "Low", "Insufficient Evidence"]
    assert len(res.retrieval_trace) >= 5
