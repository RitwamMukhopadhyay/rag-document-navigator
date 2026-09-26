'use client';

import React, { useState } from 'react';
import { Search, SlidersHorizontal, ArrowRight, ChevronDown, ChevronUp, CornerDownLeft } from 'lucide-react';

interface WorkbenchFormProps {
  onSubmit: (data: { question: string; top_k: number; chunk_size: number; overlap: number }) => void;
  isLoading: boolean;
}

const SAMPLE_CHIPS = [
  { id: 'Q01', label: 'Standard delivery timeline', question: 'What is the standard delivery timeline?' },
  { id: 'Q04', label: 'Accepted payment methods', question: 'What payment methods are accepted?' },
  { id: 'Q06', label: 'Basic RAG pipeline steps', question: 'What are the main components of a basic RAG pipeline?' },
  { id: 'Q07', label: 'Precision@k vs Recall@k', question: 'How is Precision@k calculated versus Recall@k in retrieval evaluation?' },
  { id: 'Q08', label: 'Recommended chunk size', question: 'What chunk size is recommended for narrative policy PDFs?' },
  { id: 'Q12', label: 'Privacy data retention', question: 'What is the user data retention policy for account deletion?' },
];

export const WorkbenchForm: React.FC<WorkbenchFormProps> = ({ onSubmit, isLoading }) => {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(5);
  const [chunkSize, setChunkSize] = useState(600);
  const [overlap, setOverlap] = useState(80);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!question.trim()) return;
    onSubmit({
      question: question.trim(),
      top_k: topK,
      chunk_size: chunkSize,
      overlap: overlap,
    });
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full bg-slate-900 rounded-xl p-6 border border-slate-800 shadow-lg space-y-5">
      
      {/* Title & Subtitle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-bold text-slate-100 tracking-tight">Ask your document collection</h2>
          <p className="text-xs text-slate-400">Answers are grounded in the 10 supplied PDFs with verifiable citations.</p>
        </div>

        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border text-xs transition-colors ${
            showAdvanced
              ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40 font-medium'
              : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
          }`}
        >
          <SlidersHorizontal className="w-3.5 h-3.5" />
          <span>Advanced settings</span>
          {showAdvanced ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* Main Textarea Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a research question about policy PDFs or RAG guides (e.g., What is the standard delivery timeline?)..."
            className="w-full px-4 py-3.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none font-sans"
            required
          />
        </div>

        {/* 6 Sample Chips */}
        <div>
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Sample Benchmark Questions
          </span>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_CHIPS.map((chip) => (
              <button
                key={chip.id}
                type="button"
                onClick={() => setQuestion(chip.question)}
                disabled={isLoading}
                className={`px-3 py-1.5 rounded-lg border text-xs text-left transition-all ${
                  question === chip.question
                    ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-300 font-medium shadow-sm'
                    : 'bg-slate-950/70 border-slate-800 text-slate-300 hover:bg-slate-800 hover:text-slate-100'
                }`}
              >
                <span className="font-mono text-indigo-400 text-[10px] mr-1.5">[{chip.id}]</span>
                <span>{chip.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Advanced Settings Accordion */}
        {showAdvanced && (
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 grid grid-cols-1 md:grid-cols-3 gap-5 animate-fadeIn">
            
            {/* Top-k slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <label className="font-medium text-slate-300">Top-k Chunks</label>
                <span className="px-2 py-0.5 rounded bg-slate-900 font-mono text-indigo-400 text-[11px] border border-slate-800 font-bold">
                  {topK}
                </span>
              </div>
              <input
                type="range"
                min={1}
                max={10}
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
              <p className="text-[10px] text-slate-500">Number of candidate chunks retrieved</p>
            </div>

            {/* Chunk size slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <label className="font-medium text-slate-300">Chunk Size (Tokens)</label>
                <span className="px-2 py-0.5 rounded bg-slate-900 font-mono text-indigo-400 text-[11px] border border-slate-800 font-bold">
                  {chunkSize}
                </span>
              </div>
              <input
                type="range"
                min={200}
                max={1000}
                step={50}
                value={chunkSize}
                onChange={(e) => setChunkSize(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
              <p className="text-[10px] text-slate-500">Target token count per document chunk</p>
            </div>

            {/* Overlap slider */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <label className="font-medium text-slate-300">Chunk Overlap (Tokens)</label>
                <span className="px-2 py-0.5 rounded bg-slate-900 font-mono text-indigo-400 text-[11px] border border-slate-800 font-bold">
                  {overlap}
                </span>
              </div>
              <input
                type="range"
                min={0}
                max={200}
                step={10}
                value={overlap}
                onChange={(e) => setOverlap(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
              <p className="text-[10px] text-slate-500">Token overlap between adjacent chunks</p>
            </div>

          </div>
        )}

        {/* Footer Row: Keyboard Hint & Primary Action Button */}
        <div className="flex items-center justify-between pt-1">
          <div className="hidden sm:flex items-center space-x-1.5 text-xs text-slate-500 font-mono">
            <CornerDownLeft className="w-3.5 h-3.5 text-slate-400" />
            <span>Ctrl + Enter to run</span>
          </div>

          <button
            type="submit"
            disabled={isLoading || !question.trim()}
            className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold tracking-wide transition-all shadow-md shadow-indigo-600/20 flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Processing agent workflow...</span>
              </>
            ) : (
              <>
                <span>Run transparent RAG</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

      </form>
    </div>
  );
};
