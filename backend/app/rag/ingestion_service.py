import os
import uuid
import hashlib
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.models import DocumentModel, DocumentChunkModel
from app.rag.pdf_parser import PDFParser
from app.rag.chunker import TextChunker
from app.rag.vector_store import global_vector_store, compute_embedding
from app.schemas.schemas import IngestResponse, DocumentUploadResult, BatchUploadResponse

logger = logging.getLogger(__name__)

PDF_DIR = os.getenv("PDF_DIR", "data/pdfs")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/uploads")


class IngestionService:
    """Service layer for PDF document ingestion, duplicate detection, incremental indexing, and document deletion."""

    @staticmethod
    def compute_file_hash(file_bytes: bytes) -> str:
        """Computes SHA-256 hash of file content for duplicate detection."""
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def ingest_single_pdf(
        file_bytes: bytes,
        filename: str,
        db: Session,
        chunk_size: int = 600,
        overlap: int = 80,
        overwrite: bool = False
    ) -> DocumentUploadResult:
        if not file_bytes:
            return DocumentUploadResult(
                filename=filename,
                status="error",
                message="Uploaded file is empty (0 bytes)."
            )

        file_hash = IngestionService.compute_file_hash(file_bytes)
        file_size = len(file_bytes)

        # Check for existing document by file_hash or filename
        existing_doc = db.query(DocumentModel).filter(
            (DocumentModel.file_hash == file_hash) | (DocumentModel.filename == filename)
        ).first()

        if existing_doc:
            if not overwrite:
                chunk_count = db.query(DocumentChunkModel).filter(DocumentChunkModel.document_id == existing_doc.id).count()
                logger.info(f"Duplicate detected for file '{filename}' (hash: {file_hash[:8]}). Skipping ingestion.")
                return DocumentUploadResult(
                    filename=filename,
                    status="duplicate",
                    message=f"Document '{filename}' already exists in knowledge base.",
                    document_id=existing_doc.id,
                    page_count=existing_doc.page_count,
                    chunks_created=chunk_count,
                    file_size=existing_doc.file_size or file_size
                )
            else:
                # Remove existing document first
                IngestionService.delete_document(existing_doc.id, db)

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, filename)

        try:
            with open(file_path, "wb") as f:
                f.write(file_bytes)
        except Exception as e:
            return DocumentUploadResult(
                filename=filename,
                status="error",
                message=f"Failed to save file to disk: {str(e)}"
            )

        # Parse text from PDF
        try:
            pages_text = PDFParser.parse_pdf(file_path)
        except Exception as e:
            return DocumentUploadResult(
                filename=filename,
                status="error",
                message=f"Failed to parse PDF document: {str(e)}"
            )

        if not pages_text or not any(text.strip() for _, text in pages_text):
            return DocumentUploadResult(
                filename=filename,
                status="error",
                message=f"Document '{filename}' contains no extractable text."
            )

        doc_id = str(uuid.uuid4())
        db_doc = DocumentModel(
            id=doc_id,
            filename=filename,
            file_path=file_path,
            file_hash=file_hash,
            file_size=file_size,
            page_count=len(pages_text),
            status="indexed",
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_doc)
        db.flush()

        doc_chunks_count = 0
        for page_num, page_text in pages_text:
            chunks = TextChunker.chunk_document(
                filename=filename,
                document_id=doc_id,
                page_number=page_num,
                page_text=page_text,
                chunk_size=chunk_size,
                overlap=overlap
            )

            for chunk_data in chunks:
                embedding = compute_embedding(chunk_data["chunk_text"])

                db_chunk = DocumentChunkModel(
                    id=chunk_data["chunk_id"],
                    document_id=doc_id,
                    filename=filename,
                    page_number=page_num,
                    chunk_index=chunk_data["chunk_index"],
                    chunk_text=chunk_data["chunk_text"],
                    token_count=chunk_data["token_count"],
                    start_char=chunk_data["start_char"],
                    end_char=chunk_data["end_char"],
                    embedding_json=embedding
                )
                db.add(db_chunk)

                # Add incrementally to global vector store
                chunk_data_with_doc = {**chunk_data, "document_id": doc_id, "embedding": embedding}
                global_vector_store.add_chunk(chunk_data_with_doc)
                doc_chunks_count += 1

        db.commit()
        logger.info(f"Successfully ingested single PDF '{filename}' into vector store ({doc_chunks_count} chunks).")

        return DocumentUploadResult(
            filename=filename,
            status="success",
            message=f"Successfully indexed document '{filename}'.",
            document_id=doc_id,
            page_count=len(pages_text),
            chunks_created=doc_chunks_count,
            file_size=file_size
        )

    @staticmethod
    def delete_document(doc_id: str, db: Session) -> Dict[str, Any]:
        """Deletes document record, chunk records, disk file, and memory vector store entries."""
        doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id).first()
        if not doc:
            return {"success": False, "message": f"Document ID '{doc_id}' not found."}

        filename = doc.filename
        file_path = doc.file_path

        # Delete from DB (cascades to DocumentChunkModel)
        db.delete(doc)
        db.commit()

        # Delete from vector store memory
        global_vector_store.remove_document(doc_id)
        global_vector_store.remove_document_by_filename(filename)

        # Delete physical file from disk if it exists
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not delete physical file {file_path}: {e}")

        logger.info(f"Deleted document '{filename}' (ID: {doc_id}) from database and vector store.")
        return {
            "success": True,
            "message": f"Successfully deleted document '{filename}' from knowledge base."
        }

    @staticmethod
    def ingest_pdf_directory(
        db: Session,
        pdf_dir: str = "data/pdfs",
        chunk_size: int = 600,
        overlap: int = 80
    ) -> IngestResponse:
        
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir, exist_ok=True)

        pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
        if not pdf_files and os.path.exists("../data/pdfs"):
            pdf_dir = "../data/pdfs"
            pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]

        if not pdf_files:
            # Ensure global vector store is loaded from existing DB
            global_vector_store.load_from_db(db)
            return IngestResponse(
                message=f"No PDF files found in {pdf_dir}",
                documents_processed=0,
                chunks_created=len(global_vector_store.chunks_db),
                filenames=[]
            )

        processed_count = 0
        total_chunks_created = 0
        filenames_processed = []

        for pdf_name in sorted(pdf_files):
            file_path = os.path.join(pdf_dir, pdf_name)
            try:
                with open(file_path, "rb") as f:
                    file_bytes = f.read()

                res = IngestionService.ingest_single_pdf(
                    file_bytes=file_bytes,
                    filename=pdf_name,
                    db=db,
                    chunk_size=chunk_size,
                    overlap=overlap,
                    overwrite=False
                )

                if res.status in ["success", "duplicate"]:
                    processed_count += 1
                    total_chunks_created += res.chunks_created
                    filenames_processed.append(pdf_name)
            except Exception as e:
                logger.error(f"Error ingesting directory PDF {pdf_name}: {e}")

        # Ensure global vector store is in sync with database
        global_vector_store.load_from_db(db)

        return IngestResponse(
            message=f"Ingestion check complete. Total indexed chunks: {len(global_vector_store.chunks_db)}.",
            documents_processed=processed_count,
            chunks_created=len(global_vector_store.chunks_db),
            filenames=filenames_processed
        )

