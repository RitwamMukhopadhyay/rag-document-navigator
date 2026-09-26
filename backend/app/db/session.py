import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pharma_agent.db")

# Add connect_args for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL, connect_args=connect_args, echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


from sqlalchemy import text

def ensure_sqlite_schema(engine):
    """Safely adds missing columns to existing SQLite database tables."""
    if engine.name == "sqlite":
        with engine.connect() as conn:
            try:
                conn.execute(text("ALTER TABLE nav_documents ADD COLUMN file_hash VARCHAR(64);"))
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE nav_documents ADD COLUMN file_size INTEGER DEFAULT 0;"))
            except Exception:
                pass
            try:
                conn.execute(text("ALTER TABLE nav_documents ADD COLUMN status VARCHAR(50) DEFAULT 'indexed';"))
            except Exception:
                pass
            conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
