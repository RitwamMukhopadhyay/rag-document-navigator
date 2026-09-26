'use client';

import React, { useState, useEffect } from 'react';
import { BookOpen, RefreshCw, CheckCircle2, AlertCircle, FileText, Database } from 'lucide-react';
import { checkHealth, triggerReIngest } from '../lib/api';

interface NavbarProps {
  onOpenDocModal: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenDocModal }) => {
  const [health, setHealth] = useState<{ status: string; documents_indexed: number } | null>(null);
  const [isReingesting, setIsReingesting] = useState(false);
  const [feedbackMsg, setFeedbackMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    checkHealth()
      .then((res) => setHealth(res))
      .catch(() => setHealth(null));
  }, []);

  const handleReindex = async () => {
    setIsReingesting(true);
    setFeedbackMsg(null);
    try {
      const res = await triggerReIngest();
      const h = await checkHealth();
      setHealth(h);
      setFeedbackMsg({ type: 'success', text: `Re-indexed ${res.chunks_created || 10} chunks` });
      setTimeout(() => setFeedbackMsg(null), 4000);
    } catch (e: any) {
      setFeedbackMsg({ type: 'error', text: 'Re-indexing failed' });
      setTimeout(() => setFeedbackMsg(null), 4000);
    } finally {
      setIsReingesting(false);
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full bg-[#0b0f19]/90 border-b border-slate-800/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        
        {/* Left: Brand Icon, Title, Data Pack Pill */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
            <BookOpen className="w-4 h-4" />
          </div>
          <div className="flex items-center space-x-2.5">
            <h1 className="font-bold text-sm text-slate-100 tracking-tight">Document Navigator</h1>
            <span className="px-2 py-0.5 text-[11px] font-medium rounded-full bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
              Data Pack
            </span>
          </div>
        </div>

        {/* Right: Status Pill, Add Documents Button, Re-index Button */}
        <div className="flex items-center space-x-3">
          
          {/* Feedback Toast */}
          {feedbackMsg && (
            <span
              className={`text-xs px-2.5 py-1 rounded-md border font-medium flex items-center gap-1 animate-fadeIn ${
                feedbackMsg.type === 'success'
                  ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                  : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
              }`}
            >
              {feedbackMsg.type === 'success' ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertCircle className="w-3.5 h-3.5" />}
              {feedbackMsg.text}
            </span>
          )}

          {/* Backend Status Pill */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-slate-900/90 border border-slate-800 text-xs">
            <span className={`w-2 h-2 rounded-full ${health ? 'bg-emerald-400' : 'bg-rose-500'}`} />
            <span className="text-slate-300 font-medium">
              {health ? 'Backend Live' : 'Offline'}
            </span>
          </div>

          {/* Manage & Add Documents Metric Button */}
          <button
            onClick={onOpenDocModal}
            className="flex items-center space-x-1.5 px-3 py-1 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium border border-indigo-500/40 transition-colors shadow-sm"
            title="Click to view & add documents to knowledge base"
          >
            <FileText className="w-3.5 h-3.5 text-indigo-200" />
            <span>
              {health
                ? `${health.documents_count ?? health.documents_indexed} Docs (${health.chunks_indexed ?? health.documents_indexed} Chunks)`
                : '+ Manage Documents'}
            </span>
          </button>

          {/* Re-index Secondary Button */}
          <button
            onClick={handleReindex}
            disabled={isReingesting}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white text-xs font-medium border border-slate-800 transition-colors disabled:opacity-50"
            title="Re-index documents directory"
          >
            <RefreshCw className={`w-3 h-3 ${isReingesting ? 'animate-spin' : ''}`} />
            <span>{isReingesting ? 'Indexing...' : 'Re-index'}</span>
          </button>

        </div>

      </div>
    </header>
  );
};
