import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column,
    String,
    Text,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class DocumentModel(Base):
    __tablename__ = "nav_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False, unique=True)
    file_path = Column(Text, nullable=False)
    file_hash = Column(String(64), nullable=True, index=True)
    file_size = Column(Integer, default=0)
    page_count = Column(Integer, default=1)
    status = Column(String(50), default="indexed")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chunks = relationship("DocumentChunkModel", back_populates="document", cascade="all, delete-orphan")


class DocumentChunkModel(Base):
    __tablename__ = "nav_document_chunks"

    id = Column(String(64), primary_key=True)  # e.g., chunk_guid
    document_id = Column(String(36), ForeignKey("nav_documents.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    page_number = Column(Integer, nullable=False, default=1)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    start_char = Column(Integer, default=0)
    end_char = Column(Integer, default=0)
    embedding_json = Column(JSON, nullable=True)

    document = relationship("DocumentModel", back_populates="chunks")


class QueryLogModel(Base):
    __tablename__ = "nav_query_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    intent_category = Column(String(100), nullable=False)
    top_k = Column(Integer, default=5)
    chunk_size = Column(Integer, default=600)
    overlap = Column(Integer, default=80)
    confidence_level = Column(String(50), nullable=False)
    response_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
