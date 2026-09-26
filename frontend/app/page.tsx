'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { WorkbenchForm } from '../components/WorkbenchForm';
import { WorkflowTraceDrawer } from '../components/WorkflowTraceDrawer';
import { AnswerPanel } from '../components/AnswerPanel';
import { SourceCards } from '../components/SourceCards';
import { DocUploadModal } from '../components/DocUploadModal';
import { runAgenticWorkflow, listDocuments, AgentWorkflowResponse, DocumentItem } from '../lib/api';
import { BookOpen, AlertCircle, RefreshCw, Database, Plus, CheckCircle2, FileText } from 'lucide-react';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [workflowData, setWorkflowData] = useState<AgentWorkflowResponse | null>(null);
  const [highlightCitation, setHighlightCitation] = useState<string | null>(null);
  const [isDocModalOpen, setIsDocModalOpen] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [lastInput, setLastInput] = useState<{ question: string; top_k: number; chunk_size: number; overlap: number } | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [docUpdateKey, setDocUpdateKey] = useState(0);

  useEffect(() => {
    listDocuments()
      .then((res) => setDocuments(res))
      .catch(() => setDocuments([]));
  }, [docUpdateKey]);

  const handleExecute = async (input: { question: string; top_k: number; chunk_size: number; overlap: number }) => {
    setIsLoading(true);
    setErrorMsg(null);
    setHighlightCitation(null);
    setLastInput(input);

    try {
      const response = await runAgenticWorkflow(input);
      setWorkflowData(response);
    } catch (err: any) {
      setErrorMsg(err.message || 'Execution failed. Ensure backend API is running on port 8000.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectCitation = (citationLabel: string) => {
    setHighlightCitation(citationLabel);
    const targetEl = document.getElementById(`source-${citationLabel}`);
    if (targetEl) {
      targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  const totalChunks = documents.reduce((acc, d) => acc + d.chunk_count, 0);

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      <Navbar key={docUpdateKey} onOpenDocModal={() => setIsDocModalOpen(true)} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Hero / Question Workspace Card */}
        <WorkbenchForm onSubmit={handleExecute} isLoading={isLoading} />

        {/* Knowledge Base Overview Card */}
        <div className="w-full bg-slate-900/60 rounded-xl p-5 border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
                <Database className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-100">RAG Knowledge Base</h3>
                <p className="text-xs text-slate-400 font-mono">
                  {documents.length} Documents | {totalChunks} Indexed Vector Chunks
                </p>
              </div>
            </div>

            <button
              onClick={() => setIsDocModalOpen(true)}
              className="px-3.5 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center justify-center space-x-1.5 shadow-md transition-all self-start sm:self-auto"
            >
              <Plus className="w-4 h-4" />
              <span>+ Add / Manage Documents</span>
            </button>
          </div>

          {/* Quick list of indexed documents */}
          {documents.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
              {documents.slice(0, 6).map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => setIsDocModalOpen(true)}
                  className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800/80 hover:border-indigo-500/40 flex items-center justify-between text-xs cursor-pointer transition-colors"
                >
                  <div className="flex items-center space-x-2 truncate pr-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span className="truncate text-slate-300 font-medium">{doc.filename}</span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500 shrink-0 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {doc.chunk_count} chunks
                  </span>
                </div>
              ))}
              {documents.length > 6 && (
                <button
                  onClick={() => setIsDocModalOpen(true)}
                  className="p-2.5 rounded-lg bg-slate-900/40 border border-dashed border-slate-800 text-indigo-400 text-xs font-medium hover:bg-slate-900 transition-colors flex items-center justify-center"
                >
                  + {documents.length - 6} more documents...
                </button>
              )}
            </div>
          )}
        </div>

        {/* Error Alert Banner */}
        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMsg}</span>
            </div>
            {lastInput && (
              <button
                onClick={() => handleExecute(lastInput)}
                className="px-3 py-1 rounded bg-rose-900/60 hover:bg-rose-800 text-white font-medium flex items-center gap-1 transition-colors"
              >
                <RefreshCw className="w-3 h-3" /> Retry
              </button>
            )}
          </div>
        )}

        {/* Loading Progress State */}
        {isLoading && (
          <div className="w-full bg-slate-900 rounded-xl p-6 border border-slate-800 space-y-4 animate-pulse">
            <div className="flex items-center space-x-3">
              <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
              <h3 className="text-sm font-bold text-slate-100">Executing 6-State Agentic RAG Workflow...</h3>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-6 gap-2 text-[11px] font-mono text-slate-400">
              <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-center text-indigo-400 font-semibold">1. Query Analysis</div>
              <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-center">2. Retrieval Plan</div>
              <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-center">3. Vector Search</div>
              <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-center">4. Evidence Check</div>
              <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-center">5. Re-retrieve</div>
              <div className="p-2.5 rounded bg-slate-950 border border-slate-800 text-center">6. Grounded Answer</div>
            </div>
          </div>
        )}

        {/* Empty State Prompt */}
        {!isLoading && !workflowData && !errorMsg && (
          <div className="py-12 px-6 rounded-xl bg-slate-900/50 border border-slate-800 text-center space-y-3">
            <div className="w-12 h-12 rounded-xl bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mx-auto">
              <BookOpen className="w-6 h-6" />
            </div>
            <h3 className="text-base font-bold text-slate-100">Ready for Document Question Answering</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Select one of the sample benchmark chips above, upload custom PDFs, or type a query to view explicit retrieval traces and exact <code className="text-indigo-300 font-mono">[filename:page]</code> citations.
            </p>
          </div>
        )}

        {/* Results Layout: Two-Column Desktop Grid (65% Answer & Sources / 35% Retrieval Trace Sidebar) */}
        {workflowData && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start animate-fadeIn">
            
            {/* Main Column (65% width / lg:col-span-8) */}
            <div className="lg:col-span-8 space-y-6">
              <AnswerPanel
                data={workflowData}
                onSelectCitation={handleSelectCitation}
              />

              <SourceCards
                chunks={workflowData.retrieved_chunks}
                highlightLabel={highlightCitation}
              />
            </div>

            {/* Sidebar Column (35% width / lg:col-span-4) */}
            <div className="lg:col-span-4">
              <WorkflowTraceDrawer
                traces={workflowData.retrieval_trace}
                confidence={workflowData.confidence}
                executionTime={workflowData.execution_time_seconds}
              />
            </div>

          </div>
        )}

      </main>

      {/* Footer */}
      <footer className="w-full border-t border-slate-900 bg-[#080b12] py-6 text-center text-xs text-slate-500">
        <p>Document Navigator: Agentic and Transparent RAG Assistant • Boston Data Pack Edition</p>
        <p className="text-[11px] text-slate-600 mt-1">
          Showing how it reached an answer, not merely providing an answer. Powered by FastAPI, Next.js, and verifiable [filename:page] citations.
        </p>
      </footer>

      {/* Modals */}
      <DocUploadModal
        isOpen={isDocModalOpen}
        onClose={() => setIsDocModalOpen(false)}
        onDocumentChange={() => setDocUpdateKey((prev) => prev + 1)}
      />
    </div>
  );
}
