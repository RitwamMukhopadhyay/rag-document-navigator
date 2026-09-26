import math
import zlib
import logging
from typing import List, Dict, Any, Tuple
from app.schemas.schemas import RetrievedChunkSchema
from app.rag.query_processor import QueryProcessor

logger = logging.getLogger(__name__)

def compute_embedding(text: str, dim: int = 128) -> List[float]:
    """Generates a normalized 128-dimensional embedding vector via deterministic n-gram hashing."""
    vector = [0.0] * dim
    words = text.lower().split()
    if not words:
        return vector

    for word in words:
        # Hash word deterministically to dimension index using CRC32
        idx = zlib.crc32(word.encode("utf-8")) % dim
        vector[idx] += 1.0

    # L2 Normalization
    magnitude = math.sqrt(sum(v * v for v in vector))
    if magnitude > 0:
        vector = [v / magnitude for v in vector]

    return vector

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, dot_product))

class VectorStore:
    """In-memory & SQLite persistent vector index with candidate reranking and MMR diversity."""

    def __init__(self):
        self.chunks_db: List[Dict[str, Any]] = []

    def add_chunk(self, chunk_data: Dict[str, Any]):
        # Ensure embedding exists or compute it
        if "embedding" in chunk_data and chunk_data["embedding"]:
            embedding = chunk_data["embedding"]
        else:
            embedding = compute_embedding(chunk_data["chunk_text"])
        chunk_entry = {**chunk_data, "embedding": embedding}
        self.chunks_db.append(chunk_entry)

    def clear(self):
        self.chunks_db.clear()

    def remove_document(self, document_id: str):
        """Removes all chunks associated with a specific document ID."""
        self.chunks_db = [c for c in self.chunks_db if c.get("document_id") != document_id]

    def remove_document_by_filename(self, filename: str):
        """Removes all chunks associated with a filename."""
        self.chunks_db = [c for c in self.chunks_db if c.get("filename") != filename]

    def load_from_db(self, db: Any):
        """Loads and syncs vector store with all chunks stored in SQLite database."""
        from app.models.models import DocumentChunkModel
        try:
            db_chunks = db.query(DocumentChunkModel).all()
            self.clear()
            for chunk_row in db_chunks:
                embedding = chunk_row.embedding_json
                if not embedding:
                    embedding = compute_embedding(chunk_row.chunk_text)
                
                self.chunks_db.append({
                    "chunk_id": chunk_row.id,
                    "document_id": chunk_row.document_id,
                    "filename": chunk_row.filename,
                    "page_number": chunk_row.page_number,
                    "chunk_index": chunk_row.chunk_index,
                    "chunk_text": chunk_row.chunk_text,
                    "token_count": chunk_row.token_count,
                    "embedding": embedding
                })
            logger.info(f"Loaded {len(self.chunks_db)} chunks into VectorStore from database.")
        except Exception as e:
            logger.error(f"Failed to load chunks from database into VectorStore: {e}")

    def rerank_candidate(
        self,
        query: str,
        chunk: Dict[str, Any],
        base_cos_sim: float,
        w_sim: float = 0.35,
        w_cov: float = 0.35,
        w_phrase: float = 0.15,
        w_meta: float = 0.15
    ) -> Tuple[float, Dict[str, float]]:
        """Transparent weighted reranking formula combining Cosine Sim, Keyword Coverage, Phrase Match & Metadata Match."""
        # 1. Term coverage
        coverage = QueryProcessor.compute_query_coverage(query, chunk["chunk_text"])

        # 2. Exact Phrase Match
        phrase = QueryProcessor.check_exact_phrase_match(query, chunk["chunk_text"])

        # 3. Metadata Match (filename keywords)
        q_kws = set(QueryProcessor.extract_keywords(query))
        fn_kws = set(QueryProcessor.extract_keywords(chunk.get("filename", "")))
        meta_match = 1.0 if (q_kws and fn_kws and len(q_kws.intersection(fn_kws)) > 0) else 0.0

        # Formula calculation
        score = (w_sim * base_cos_sim) + (w_cov * coverage) + (w_phrase * phrase) + (w_meta * meta_match)
        final_score = round(min(0.99, max(0.0, score)), 4)

        breakdown = {
            "cosine_sim": base_cos_sim,
            "coverage": coverage,
            "phrase_match": phrase,
            "metadata_match": meta_match,
            "final_score": final_score
        }
        return final_score, breakdown

    def search(self, query: str, top_k: int = 5) -> List[RetrievedChunkSchema]:
        if not self.chunks_db or not query or not query.strip():
            return []

        norm_query = QueryProcessor.normalize(query)
        query_vec = compute_embedding(norm_query)

        # Step 1: Candidate Retrieval (Retrieve up to max(20, 3 * top_k) candidate chunks)
        candidate_pool_size = max(20, top_k * 3)
        candidate_scores = []

        for chunk in self.chunks_db:
            base_sim = cosine_similarity(query_vec, chunk["embedding"])
            candidate_scores.append((base_sim, chunk))

        # Sort candidate pool by base similarity
        candidate_scores.sort(key=lambda x: x[0], reverse=True)
        top_candidates = candidate_scores[:candidate_pool_size]

        # Step 2: Rerank Candidates using transparent formula
        reranked_pool = []
        for base_sim, chunk in top_candidates:
            final_score, breakdown = self.rerank_candidate(norm_query, chunk, base_sim)
            reranked_pool.append({
                "chunk": chunk,
                "score": final_score,
                "breakdown": breakdown
            })

        # Sort descending by reranked final_score
        reranked_pool.sort(key=lambda x: x["score"], reverse=True)

        # Step 3: Lightweight MMR Diversity Filtering (Redundancy Penalty)
        selected_results: List[Dict[str, Any]] = []
        selected_texts: List[str] = []

        for item in reranked_pool:
            chk = item["chunk"]
            chk_text = chk["chunk_text"]

            # Compute max overlap with already selected chunks
            max_redundancy = 0.0
            for sel_t in selected_texts:
                sim_overlap = QueryProcessor.compute_query_coverage(chk_text, sel_t)
                if sim_overlap > max_redundancy:
                    max_redundancy = sim_overlap

            # Apply redundancy penalty if > 85% overlap
            penalty = 0.15 * max_redundancy if max_redundancy > 0.85 else 0.0
            adjusted_score = round(max(0.0, item["score"] - penalty), 4)

            selected_results.append({
                "chunk": chk,
                "score": adjusted_score
            })
            selected_texts.append(chk_text)

            if len(selected_results) >= top_k:
                break

        # Step 4: Construct Output Schemas
        retrieved: List[RetrievedChunkSchema] = []
        for rank, item in enumerate(selected_results, start=1):
            chunk = item["chunk"]
            score = item["score"]
            retrieved.append(
                RetrievedChunkSchema(
                    chunk_id=chunk["chunk_id"],
                    filename=chunk["filename"],
                    page_number=chunk["page_number"],
                    citation_label=f"[{chunk['filename']}:{chunk['page_number']}]",
                    chunk_text=chunk["chunk_text"],
                    similarity_score=score,
                    rank=rank,
                    document_id=chunk.get("document_id")
                )
            )

        return retrieved

# Global VectorStore instance
global_vector_store = VectorStore()

