# Viva Defense Preparation & Technical Q&A — Document Navigator

This document contains anticipated viva defense questions, key architectural justifications, and concise answers for evaluating **Document Navigator: Agentic and Transparent RAG Assistant**.

---

## 1. Chunking & Text Processing

### Q1: Why does chunking matter in a Retrieval-Augmented Generation (RAG) system?
> **Answer**: Large PDFs exceed LLM context window limits and introduce dilution of specific facts. Chunking breaks long narrative documents into smaller, semantically dense units. This enables vector similarity search to pinpoint exact paragraphs containing the answer rather than retrieving an entire 50-page document.

### Q2: What are the trade-offs between chunk size and overlap?
> **Answer**:
> - **Chunk Size**: Larger chunks (e.g., 800–1000 tokens) retain broader narrative context but introduce noise and lower vector similarity resolution. Smaller chunks (e.g., 200–300 tokens) provide higher precision but risk losing sentence context.
> - **Overlap**: Adding overlap (e.g., 80 tokens) prevents semantic boundary truncation where a critical sentence or key phrase spans across two adjacent chunks.

---

## 2. Embeddings & Vector Retrieval

### Q3: How do embeddings and vector similarity search work?
> **Answer**: An embedding function maps text chunks into a continuous high-dimensional vector space where semantically similar texts are placed close together. Querying computes cosine distance between the query vector $Q$ and candidate chunk vectors $V_i$:
> $$\text{CosineSimilarity}(Q, V_i) = \frac{Q \cdot V_i}{\|Q\| \|V_i\|}$$
> Chunks with highest cosine similarity are ranked and returned as top-k context.

### Q4: What does Precision@k and Recall@k measure in retrieval evaluation?
> **Answer**:
> - **Precision@k**: The proportion of the top-k retrieved chunks that belong to the relevant ground-truth document:
>   $$\text{Precision@k} = \frac{\text{Relevant Chunks in Top-k}}{k}$$
> - **Recall@k**: Whether at least one gold relevant chunk was successfully retrieved within the top-k results. In our benchmark, Document Navigator achieved **93.3% Recall@5**.

---

## 3. Hallucination Prevention & Trust

### Q5: How does Document Navigator prevent AI hallucinations?
> **Answer**: Hallucination is prevented at three distinct checkpoints:
> 1. **Evidence Thresholding**: In State 4 (Evidence Check), if the maximum similarity score falls below threshold (< 0.25), the agent refuses to guess and triggers safe refusal.
> 2. **Strict Grounding**: The answer generator is restricted exclusively to supplied top-k text.
> 3. **Citation Guard**: Every factual statement must cite `[filename:page]`. Unsubstantiated claims are rejected and replaced with `"Insufficient evidence found in document index"`.

### Q6: Why do explicit citations (`[filename:page]`) improve user trust?
> **Answer**: Citations make AI responses verifiable and auditable. Rather than taking a generated answer on blind faith, users can click any `[policy_shipping_returns.pdf:1]` badge to immediately inspect the source document, page number, and exact text snippet.

### Q7: What happens when retrieved evidence is weak?
> **Answer**: If initial retrieval yields weak similarity scores, the workflow transitions to State 5 (**Re-retrieve**). It expands query terms or boosts $k$ for a single retry. If scores remain below threshold, the agent transitions to State 6 (**Safe Refusal**) and reports `"Insufficient Evidence"` rather than hallucinating an ungrounded answer.
