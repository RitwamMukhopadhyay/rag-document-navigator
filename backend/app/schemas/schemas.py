from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class ChunkMetadata(BaseModel):
    filename: str
    page_number: int
    citation_label: str  # Format: [filename:page]
    chunk_id: str
    document_id: str
    chunk_index: int
    token_count: int

    model_config = ConfigDict(from_attributes=True)


class RetrievedChunkSchema(BaseModel):
    chunk_id: str
    filename: str
    page_number: int
    citation_label: str  # e.g., [policy_shipping_returns.pdf:1]
    chunk_text: str
    similarity_score: float
    rank: int
    document_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class IngestResponse(BaseModel):
    message: str
    documents_processed: int
    chunks_created: int
    filenames: List[str]


class DocumentItemSchema(BaseModel):
    id: str
    filename: str
    file_size: int
    page_count: int
    chunk_count: int
    file_hash: Optional[str] = None
    status: str = "indexed"
    created_at: str


class DocumentUploadResult(BaseModel):
    filename: str
    status: str  # "success" | "duplicate" | "error"
    message: str
    document_id: Optional[str] = None
    page_count: int = 0
    chunks_created: int = 0
    file_size: int = 0


class BatchUploadResponse(BaseModel):
    message: str
    documents_processed: int
    duplicates_skipped: int
    total_chunks_created: int
    results: List[DocumentUploadResult]


class RetrievalRequest(BaseModel):
    question: str = Field(..., description="Query string to retrieve context for")
    top_k: int = Field(5, ge=1, le=20, description="Top-k chunks to retrieve")
    chunk_size: int = Field(600, ge=100, le=2000, description="Token size for chunking")
    overlap: int = Field(80, ge=0, le=500, description="Token overlap between chunks")


class RetrievalResponse(BaseModel):
    question: str
    top_k: int
    retrieved_chunks: List[RetrievedChunkSchema]
    total_retrieved: int


class AgentWorkflowRequest(BaseModel):
    question: str = Field(..., description="User query for agentic RAG system")
    top_k: int = Field(5, ge=1, le=20)
    chunk_size: int = Field(600, ge=100, le=2000)
    overlap: int = Field(80, ge=0, le=500)


class RetrievalTraceStep(BaseModel):
    step_number: int
    step_name: str
    details: str
    timestamp: str


class AgentWorkflowResponse(BaseModel):
    question: str
    answer: str
    citations: List[str]
    confidence: str  # High, Medium, Low, Insufficient Evidence
    retrieval_trace: List[RetrievalTraceStep]
    limitations: List[str]
    retrieved_chunks: List[RetrievedChunkSchema]
    execution_time_seconds: float
    total_documents_searched: int = 0
    best_match_score: float = 0.0
    embedding_model: str = "Deterministic 128-dim N-Gram Vector Hash"
    llm_model: str = "Grounded Agentic Synthesizer v1.0"
