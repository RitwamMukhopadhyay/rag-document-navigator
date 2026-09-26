'use client';

import React, { useState } from 'react';
import { Database, CheckCircle2, ChevronDown, ChevronUp } from 'lucide-react';
import { RetrievedChunk } from '../lib/api';

interface SourceCardsProps {
  chunks: RetrievedChunk[];
  highlightLabel: string | null;
}

export const SourceCards: React.FC<SourceCardsProps> = ({ chunks, highlightLabel }) => {
  const [expandedChunks, setExpandedChunks] = useState<Record<string, boolean>>({});

  if (!chunks || chunks.length === 0) return null;

  const toggleExpand = (chunkId: string) => {
    setExpandedChunks((prev) => ({ ...prev, [chunkId]: !prev[chunkId] }));
  };

  return (
    <div className="w-full bg-slate-900 rounded-xl p-6 border border-slate-800 space-y-4">
      
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-indigo-400" />
          <h3 className="text-base font-bold text-slate-100 tracking-tight">
            Retrieved Evidence ({chunks.length})
          </h3>
        </div>
        <span className="text-xs text-slate-500 font-mono">Sorted by similarity score</span>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-1 gap-3.5">
        {chunks.map((chunk) => {
          const isHighlight = highlightLabel === `${chunk.filename}:${chunk.page_number}`;
          const isExpanded = expandedChunks[chunk.chunk_id];
          const textExcerpt = chunk.chunk_text;
          const shouldTruncate = textExcerpt.length > 200;
          const displayText = isExpanded || !shouldTruncate ? textExcerpt : textExcerpt.slice(0, 200) + '...';

          const scorePercent = Math.min(100, Math.max(10, Math.round(chunk.similarity_score * 100)));

          return (
            <div
              key={chunk.chunk_id}
              id={`source-${chunk.filename}:${chunk.page_number}`}
              className={`p-4 rounded-xl border transition-all text-xs ${
                isHighlight
                  ? 'bg-indigo-950/40 border-indigo-500 ring-2 ring-indigo-500 shadow-md'
                  : 'bg-slate-950/70 border-slate-800/80 hover:border-slate-700'
              }`}
            >
              {/* Header row */}
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
                <div className="flex items-center space-x-2">
                  <span className="w-6 h-6 rounded bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 flex items-center justify-center font-mono font-bold text-[11px]">
                    #{chunk.rank}
                  </span>
                  <span className="px-2.5 py-0.5 rounded bg-slate-900 font-mono font-semibold text-indigo-400 border border-slate-800">
                    [{chunk.filename}:{chunk.page_number}]
                  </span>
                </div>

                {/* Similarity Progress Bar */}
                <div className="flex items-center space-x-2 font-mono">
                  <span className="text-[10px] text-slate-400">Score:</span>
                  <div className="w-20 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-500 rounded-full"
                      style={{ width: `${scorePercent}%` }}
                    />
                  </div>
                  <span className="text-emerald-400 font-bold text-[11px]">
                    {(chunk.similarity_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Excerpt Content */}
              <p className="text-slate-300 leading-relaxed font-sans bg-slate-900 p-3.5 rounded-lg border border-slate-800/80 mb-2">
                "{displayText}"
                {shouldTruncate && (
                  <button
                    onClick={() => toggleExpand(chunk.chunk_id)}
                    className="ml-2 font-mono text-[11px] text-indigo-400 hover:text-indigo-300 font-semibold inline-flex items-center gap-0.5"
                  >
                    {isExpanded ? 'Show less' : 'Show more'}
                  </button>
                )}
              </p>

              {/* Muted Metadata Row */}
              <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1">
                <span>Chunk ID: {chunk.chunk_id}</span>
                <span className="text-emerald-400/90 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Indexed PDF Source
                </span>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
