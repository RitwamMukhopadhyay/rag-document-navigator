'use client';

import React, { useState } from 'react';
import { ShieldCheck, Award, AlertTriangle, FileText, CheckCircle, ExternalLink, X } from 'lucide-react';
import { AgentWorkflowResponse, RetrievedChunk } from '../lib/api';

interface AnswerPanelProps {
  data: AgentWorkflowResponse;
  onSelectCitation: (citationLabel: string) => void;
}

export const AnswerPanel: React.FC<AnswerPanelProps> = ({ data, onSelectCitation }) => {
  const [activeEvidence, setActiveEvidence] = useState<RetrievedChunk | null>(null);

  const getConfBadgeClass = (confidence: string) => {
    switch (confidence) {
      case 'High':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'Medium':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'Low':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
      case 'Insufficient Evidence':
      default:
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    }
  };

  const handleCitationClick = (citationLabel: string) => {
    onSelectCitation(citationLabel);
    // Find matching chunk in retrieved_chunks
    const matched = data.retrieved_chunks.find(
      (c) => c.citation_label === citationLabel || `${c.filename}:${c.page_number}` === citationLabel
    );
    if (matched) {
      setActiveEvidence(matched);
    }
  };

  // Convert inline citations [filename:page] into clickable buttons
  const renderFormattedAnswer = (text: string) => {
    const parts = text.split(/(\[[a-zA-Z0-9_\-\.]+\.pdf:\d+\])/g);

    return parts.map((part, idx) => {
      if (part.startsWith('[') && part.endsWith(']')) {
        const citationLabel = part.slice(1, -1);

        return (
          <button
            key={idx}
            onClick={() => handleCitationClick(citationLabel)}
            className="inline-flex items-center px-2 py-0.5 mx-1 text-xs font-mono font-medium rounded bg-indigo-600/20 text-indigo-300 hover:bg-indigo-600/40 hover:text-white border border-indigo-500/30 transition-all cursor-pointer shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            title={`Click to view Source Evidence for ${part}`}
          >
            {part}
          </button>
        );
      }

      return (
        <span key={idx} className="leading-relaxed">
          {part}
        </span>
      );
    });
  };

  return (
    <div className="w-full bg-slate-900 rounded-xl p-6 border border-slate-800 space-y-5">
      
      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-100 tracking-tight">Grounded Answer</h3>
            <p className="text-xs text-slate-400">Strict evidence matching against indexed PDF chunks</p>
          </div>
        </div>

        {/* Confidence badge */}
        <div className="flex items-center space-x-2">
          <span className={`px-3 py-1 rounded-full text-xs font-medium border flex items-center gap-1.5 ${getConfBadgeClass(data.confidence)}`}>
            <Award className="w-3.5 h-3.5" />
            <span>Confidence: {data.confidence}</span>
          </span>
        </div>
      </div>

      {/* Main Grounded Answer Text */}
      <div className="text-sm text-slate-200 whitespace-pre-line font-sans leading-relaxed bg-slate-950 p-5 rounded-xl border border-slate-800/80">
        {renderFormattedAnswer(data.answer)}
      </div>

      {/* Source Evidence Popover/Card when citation clicked */}
      {activeEvidence && (
        <div className="p-5 rounded-xl bg-indigo-950/40 border border-indigo-500/40 space-y-3 relative animate-fadeIn">
          <button
            onClick={() => setActiveEvidence(null)}
            className="absolute top-3 right-3 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800/60"
            title="Close Source Evidence View"
          >
            <X className="w-4 h-4" />
          </button>

          <div className="flex items-center space-x-2 text-indigo-300 font-bold text-xs uppercase tracking-wider">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span>SOURCE EVIDENCE EXPLICIT VERIFICATION</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono">
            <div>
              <span className="text-slate-500 block text-[10px]">Document:</span>
              <span className="text-slate-200 font-semibold">{activeEvidence.filename}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">Page Number:</span>
              <span className="text-slate-200 font-semibold">Page {activeEvidence.page_number}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px]">Similarity Rank / Score:</span>
              <span className="text-emerald-400 font-semibold">Rank #{activeEvidence.rank} ({activeEvidence.similarity_score.toFixed(3)})</span>
            </div>
          </div>

          <div>
            <span className="text-[11px] font-medium text-slate-400 block mb-1">Relevant Retrieved Passage:</span>
            <div className="p-3.5 rounded-lg bg-slate-950 border border-indigo-900/60 text-xs font-mono text-slate-300 leading-relaxed italic">
              "{activeEvidence.chunk_text}"
            </div>
          </div>
        </div>
      )}

      {/* Limitations disclosure when present */}
      {data.limitations && data.limitations.length > 0 && (
        <div className="p-4 rounded-xl bg-slate-950 border border-amber-500/30 text-xs space-y-1.5">
          <div className="flex items-center space-x-1.5 font-medium text-amber-400">
            <AlertTriangle className="w-4 h-4" />
            <span>Scope & Limitations Disclosure</span>
          </div>
          <ul className="list-disc list-inside space-y-1 text-slate-400 text-[11px]">
            {data.limitations.map((lim, lIdx) => (
              <li key={lIdx}>{lim}</li>
            ))}
          </ul>
        </div>
      )}

    </div>
  );
};

