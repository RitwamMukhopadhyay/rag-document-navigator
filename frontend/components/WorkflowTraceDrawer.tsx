'use client';

import React, { useState } from 'react';
import { Terminal, ChevronDown, ChevronUp, Clock, CheckCircle2 } from 'lucide-react';
import { RetrievalTraceStep } from '../lib/api';

interface WorkflowTraceDrawerProps {
  traces: RetrievalTraceStep[];
  confidence: string;
  executionTime: number;
}

export const WorkflowTraceDrawer: React.FC<WorkflowTraceDrawerProps> = ({ traces, confidence, executionTime }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (!traces || traces.length === 0) return null;

  return (
    <div className="w-full bg-slate-900 rounded-xl p-5 border border-slate-800 space-y-4">
      
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-bold text-slate-100 tracking-tight">Agent Execution Trace</h3>
          <span className="text-[11px] px-2 py-0.5 rounded-full bg-slate-950 text-slate-400 border border-slate-800 font-mono">
            {traces.length} States • {executionTime}s
          </span>
        </div>

        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center space-x-1 text-xs text-slate-400 hover:text-slate-200 font-mono"
        >
          <span>{isOpen ? 'Collapse' : 'Expand'}</span>
          {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {/* Stepper Timeline */}
      {isOpen && (
        <div className="relative pl-5 space-y-3 border-l border-slate-800 ml-2 py-1">
          {traces.map((trace) => (
            <div key={trace.step_number} className="relative">
              {/* Timeline circle node */}
              <div className="absolute -left-[27px] top-0.5 w-3.5 h-3.5 rounded-full bg-slate-950 border-2 border-indigo-500 flex items-center justify-center">
                <span className="w-1 h-1 rounded-full bg-indigo-400" />
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 font-mono">
                    <span className="text-indigo-400 font-bold">State {trace.step_number}:</span>
                    <span className="font-semibold text-slate-200">{trace.step_name}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                    <Clock className="w-3 h-3 text-slate-500" /> {trace.timestamp}
                  </span>
                </div>
                <p className="text-slate-400 font-sans leading-relaxed">{trace.details}</p>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
};
