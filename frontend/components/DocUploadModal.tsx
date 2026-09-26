'use client';

import React, { useEffect, useState, useRef } from 'react';
import { X, FileText, CheckCircle2, Upload, Trash2, AlertTriangle, RefreshCw, FileUp, Database, Layers } from 'lucide-react';
import { listDocuments, uploadDocuments, deleteDocument, DocumentItem, BatchUploadResponse } from '../lib/api';

interface DocUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onDocumentChange?: () => void;
}

export const DocUploadModal: React.FC<DocUploadModalProps> = ({ isOpen, onClose, onDocumentChange }) => {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [overwriteDuplicates, setOverwriteDuplicates] = useState(false);
  const [uploadResult, setUploadResult] = useState<BatchUploadResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchDocs = async () => {
    setIsLoading(true);
    try {
      const data = await listDocuments();
      setDocs(data);
    } catch (err: any) {
      setErrorMessage("Failed to fetch document library.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchDocs();
      setUploadResult(null);
      setErrorMessage(null);
      setSelectedFiles([]);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArr = Array.from(e.target.files).filter(f => f.name.toLowerCase().endsWith('.pdf') || f.type === 'application/pdf');
      if (filesArr.length === 0) {
        setErrorMessage("Only PDF files (.pdf) are supported.");
        return;
      }
      setSelectedFiles(filesArr);
      setErrorMessage(null);
      setUploadResult(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArr = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
      if (filesArr.length === 0) {
        setErrorMessage("Only PDF files (.pdf) are supported.");
        return;
      }
      setSelectedFiles(filesArr);
      setErrorMessage(null);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) return;
    setIsUploading(true);
    setErrorMessage(null);
    setUploadResult(null);

    try {
      const result = await uploadDocuments(selectedFiles, overwriteDuplicates);
      setUploadResult(result);
      setSelectedFiles([]);
      if (fileInputRef.current) fileInputRef.current.value = '';
      await fetchDocs();
      if (onDocumentChange) onDocumentChange();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to upload and ingest documents.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (docId: string, filename: string) => {
    if (!confirm(`Are you sure you want to remove "${filename}" from the knowledge base?`)) return;
    setDeletingId(docId);
    try {
      await deleteDocument(docId);
      await fetchDocs();
      if (onDocumentChange) onDocumentChange();
    } catch (err: any) {
      setErrorMessage(err.message || `Failed to delete ${filename}`);
    } finally {
      setDeletingId(null);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const totalChunks = docs.reduce((acc, d) => acc + d.chunk_count, 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-3xl bg-slate-900 rounded-xl p-6 border border-slate-800 shadow-2xl relative max-h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">Knowledge Base Management</h3>
              <p className="text-xs text-slate-400">
                {docs.length} Documents indexed • {totalChunks} Total Vector Chunks
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="overflow-y-auto space-y-6 pr-1 flex-1">
          
          {/* Section 1: Upload Documents */}
          <div className="bg-slate-950/60 rounded-xl p-4 border border-slate-800/80 space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                <FileUp className="w-4 h-4" /> Add Documents to RAG Knowledge Base
              </h4>
              <label className="flex items-center space-x-2 text-[11px] text-slate-400 cursor-pointer">
                <input
                  type="checkbox"
                  checked={overwriteDuplicates}
                  onChange={(e) => setOverwriteDuplicates(e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-0 w-3.5 h-3.5"
                />
                <span>Overwrite duplicates</span>
              </label>
            </div>

            {/* Drag & Drop Area */}
            <div
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-700 hover:border-indigo-500/60 rounded-xl p-6 text-center cursor-pointer transition-colors bg-slate-900/40 hover:bg-slate-900/80 group"
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".pdf,application/pdf"
                onChange={handleFileSelect}
                className="hidden"
              />
              <div className="w-10 h-10 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mx-auto mb-2 group-hover:scale-110 transition-transform">
                <Upload className="w-5 h-5" />
              </div>
              <p className="text-xs font-medium text-slate-200">
                Click to browse or drag & drop PDF files here
              </p>
              <p className="text-[11px] text-slate-500 mt-1">
                Supports single or batch PDF ingestion. Duplicate files automatically detected via SHA-256 hash.
              </p>
            </div>

            {/* Selected files preview before ingestion */}
            {selectedFiles.length > 0 && (
              <div className="space-y-3">
                <div className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                  <span>Selected PDF Files ({selectedFiles.length}):</span>
                  <button
                    onClick={() => setSelectedFiles([])}
                    className="text-[11px] text-rose-400 hover:underline"
                  >
                    Clear selection
                  </button>
                </div>
                <div className="max-h-36 overflow-y-auto space-y-1.5 pr-1">
                  {selectedFiles.map((file, idx) => (
                    <div key={idx} className="p-2 rounded bg-slate-900 border border-slate-800 text-xs flex items-center justify-between">
                      <div className="flex items-center space-x-2 truncate">
                        <FileText className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
                        <span className="truncate font-medium text-slate-200">{file.name}</span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400 shrink-0 ml-2">
                        {formatFileSize(file.size)}
                      </span>
                    </div>
                  ))}
                </div>

                <button
                  onClick={handleUpload}
                  disabled={isUploading}
                  className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center justify-center space-x-2 shadow-lg shadow-indigo-600/20 transition-all disabled:opacity-50"
                >
                  {isUploading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      <span>Ingesting PDF Text & Generating Vector Embeddings...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      <span>Ingest Selected PDF(s) into Knowledge Base</span>
                    </>
                  )}
                </button>
              </div>
            )}

            {/* Upload results & duplicate notifications */}
            {uploadResult && (
              <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center space-x-2 text-emerald-400 font-semibold">
                  <CheckCircle2 className="w-4 h-4 shrink-0" />
                  <span>{uploadResult.message}</span>
                </div>
                <div className="space-y-1 pl-6">
                  {uploadResult.results.map((res, i) => (
                    <div key={i} className="flex items-center justify-between text-[11px]">
                      <span className="truncate font-mono text-slate-300">{res.filename}</span>
                      <span
                        className={`px-2 py-0.5 rounded font-mono text-[10px] ${
                          res.status === 'success'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                            : res.status === 'duplicate'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                        }`}
                      >
                        {res.status === 'success'
                          ? `✓ Indexed (${res.chunks_created} chunks)`
                          : res.status === 'duplicate'
                          ? 'Duplicate (Skipped)'
                          : 'Error'}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Error Banner */}
            {errorMessage && (
              <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-rose-300 text-xs flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}
          </div>

          {/* Section 2: Indexed Document Library */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-indigo-400" /> Document Library ({docs.length})
              </span>
              <button
                onClick={fetchDocs}
                disabled={isLoading}
                className="text-[11px] text-indigo-400 hover:underline flex items-center gap-1 normal-case font-normal"
              >
                <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} /> Refresh
              </button>
            </h4>

            {isLoading ? (
              <div className="py-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
                Loading document library...
              </div>
            ) : docs.length === 0 ? (
              <div className="py-8 text-center text-xs text-slate-500 bg-slate-950/40 rounded-xl border border-slate-800">
                No documents found in knowledge base. Upload a PDF above to populate the vector index.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {docs.map((doc) => (
                  <div
                    key={doc.id}
                    className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-slate-700 flex flex-col justify-between space-y-2 text-xs transition-colors group"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-2.5 truncate pr-2">
                        <FileText className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                        <div className="truncate">
                          <span className="font-semibold text-slate-200 block truncate" title={doc.filename}>
                            {doc.filename}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono">
                            {doc.page_count} Pages • {doc.chunk_count} Chunks • {formatFileSize(doc.file_size)}
                          </span>
                        </div>
                      </div>

                      {/* Delete button */}
                      <button
                        onClick={() => handleDelete(doc.id, doc.filename)}
                        disabled={deletingId === doc.id}
                        className="p-1.5 rounded bg-slate-900 hover:bg-rose-950/80 text-slate-400 hover:text-rose-300 border border-slate-800 hover:border-rose-800 transition-colors shrink-0"
                        title={`Delete ${doc.filename} from vector store`}
                      >
                        {deletingId === doc.id ? (
                          <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Trash2 className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-900 text-[10px]">
                      <span className="text-emerald-400 font-medium flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> Indexed
                      </span>
                      <span className="text-slate-500 font-mono">
                        {new Date(doc.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

      </div>
    </div>
  );
};

