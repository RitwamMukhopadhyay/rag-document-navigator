import os
import sys
import argparse
import logging

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal, Base, engine
from app.rag.ingestion_service import IngestionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Document Navigator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest PDFs into vector index and database")
    ingest_parser.add_argument("--pdf-dir", default="data/pdfs", help="Directory containing PDF files")
    ingest_parser.add_argument("--chunk-size", type=int, default=600, help="Chunk token size")
    ingest_parser.add_argument("--overlap", type=int, default=80, help="Chunk overlap tokens")

    args = parser.parse_args()

    if args.command == "ingest":
        print(f"Initializing database and ingesting PDFs from '{args.pdf_dir}'...")
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            result = IngestionService.ingest_pdf_directory(
                db=db,
                pdf_dir=args.pdf_dir,
                chunk_size=args.chunk_size,
                overlap=args.overlap
            )
            print(f"SUCCESS: {result.message}")
            print(f"Documents: {result.documents_processed} | Chunks Created: {result.chunks_created}")
            for fn in result.filenames:
                print(f" - {fn}")
        finally:
            db.close()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
