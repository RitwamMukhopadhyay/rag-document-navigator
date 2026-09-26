const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface RetrievedChunk {
  chunk_id: string;
  filename: string;
  page_number: number;
  citation_label: string;  // e.g. [policy_shipping_returns.pdf:1]
  chunk_text: string;
  similarity_score: number;
  rank: number;
  document_id?: string;
}

export interface RetrievalTraceStep {
  step_number: number;
  step_name: string;
  details: string;
  timestamp: string;
}

export interface AgentWorkflowResponse {
  question: string;
  answer: string;
  citations: string[];
  confidence: 'High' | 'Medium' | 'Low' | 'Insufficient Evidence';
  retrieval_trace: RetrievalTraceStep[];
  limitations: string[];
  retrieved_chunks: RetrievedChunk[];
  execution_time_seconds: number;
}

export interface EvalQuestion {
  id: string;
  question: string;
  gold_citation: string;
  gold_key_phrase: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_size: number;
  page_count: number;
  chunk_count: number;
  file_hash?: string;
  status: string;
  created_at: string;
}

export interface DocumentUploadResult {
  filename: string;
  status: 'success' | 'duplicate' | 'error';
  message: string;
  document_id?: string;
  page_count: number;
  chunks_created: number;
  file_size: number;
}

export interface BatchUploadResponse {
  message: string;
  documents_processed: number;
  duplicates_skipped: number;
  total_chunks_created: number;
  results: DocumentUploadResult[];
}

export async function checkHealth(): Promise<{ status: string; service: string; documents_count?: number; documents_indexed: number; chunks_indexed?: number }> {
  const res = await fetch(`${API_BASE}/health`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Backend connection failed');
  return res.json();
}

export async function runAgenticWorkflow(payload: {
  question: string;
  top_k: number;
  chunk_size: number;
  overlap: number;
}): Promise<AgentWorkflowResponse> {
  const res = await fetch(`${API_BASE}/api/agent/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Agent execution failed' }));
    throw new Error(err.detail || 'Server error');
  }

  return res.json();
}

export async function getEvalQuestions(): Promise<EvalQuestion[]> {
  const res = await fetch(`${API_BASE}/api/eval/questions`, { cache: 'no-store' });
  if (!res.ok) return [];
  return res.json();
}

export async function triggerReIngest(top_k = 5, chunk_size = 600, overlap = 80): Promise<{ message: string; chunks_created: number }> {
  const res = await fetch(`${API_BASE}/api/ingest?chunk_size=${chunk_size}&overlap=${overlap}`, {
    method: 'POST',
  });

  if (!res.ok) throw new Error('Ingestion failed');
  return res.json();
}

export async function listDocuments(): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE}/api/documents`, { cache: 'no-store' });
  if (!res.ok) return [];
  return res.json();
}

export async function uploadDocuments(
  files: File[],
  overwrite = false,
  chunkSize = 600,
  overlap = 80
): Promise<BatchUploadResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));
  formData.append('overwrite', overwrite ? 'true' : 'false');
  formData.append('chunk_size', chunkSize.toString());
  formData.append('overlap', overlap.toString());

  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Failed to upload documents');
  }

  return res.json();
}

export async function deleteDocument(docId: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${API_BASE}/api/documents/${docId}`, {
    method: 'DELETE',
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Delete failed' }));
    throw new Error(err.detail || 'Failed to delete document');
  }

  return res.json();
}
