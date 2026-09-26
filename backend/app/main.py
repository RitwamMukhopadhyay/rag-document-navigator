import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine, Base, SessionLocal, ensure_sqlite_schema
from app.api import nav_api
from app.rag.ingestion_service import IngestionService
from app.rag.vector_store import global_vector_store

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Initialize Database tables
Base.metadata.create_all(bind=engine)
ensure_sqlite_schema(engine)

# Auto-ingest PDFs on startup if directory exists & hydrate vector store from SQLite
db = SessionLocal()
try:
    IngestionService.ingest_pdf_directory(db=db, pdf_dir="data/pdfs")
    global_vector_store.load_from_db(db)
finally:
    db.close()

app = FastAPI(
    title="Document Navigator: Agentic and Transparent RAG Assistant",
    description="Agentic local PDF question-answering assistant exposing transparent retrieval traces, exact [filename:page] citations, and Precision@k evaluation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nav_api.router)

@app.get("/")
def root():
    return {
        "app": "Document Navigator: Agentic and Transparent RAG Assistant",
        "health_check": "/health",
        "docs_url": "/docs"
    }
