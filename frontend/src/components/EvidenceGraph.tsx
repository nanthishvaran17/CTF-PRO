import React from "react";
import { EvidenceGraphData } from "../api/client";
import { FileCode, Layers, Flag, ArrowRight, ShieldCheck } from "lucide-react";

interface EvidenceGraphProps {
  data: EvidenceGraphData;
  onSelectNode?: (nodeId: string, nodeType: string, meta: any) => void;
}

export const EvidenceGraph: React.FC<EvidenceGraphProps> = ({ data, onSelectNode }) => {
  if (!data || !data.nodes || data.nodes.length === 0) {
    return (
      <div className="p-12 text-center text-slate-500 font-mono text-sm border border-ctf-border rounded-card bg-ctf-surface">
        <Layers className="w-8 h-8 mx-auto mb-2 opacity-40 text-ctf-cyan" />
        <p>No evidence nodes constructed. Ingest a challenge file and execute analysis to generate DAG.</p>
      </div>
    );
  }

  // Group nodes by type for visual hierarchy
  const fileNodes = data.nodes.filter((n) => n.type === "file");
  const transformNodes = data.nodes.filter((n) => n.type === "transform" || n.type === "artifact");
  const candidateNodes = data.nodes.filter((n) => n.type === "candidate");

  return (
    <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card overflow-x-auto font-mono text-xs">
      <div className="flex items-center justify-between mb-6 pb-3 border-b border-ctf-border">
        <div className="flex items-center gap-2 text-ctf-cyan font-bold text-sm">
          <Layers className="w-4 h-4" /> Evidence Provenance DAG
        </div>
        <div className="text-slate-400 text-[11px]">
          {data.nodes.length} Nodes &bull; {data.edges.length} Directed Transitions
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative min-w-[700px]">
        {/* Column 1: Source Files */}
        <div className="space-y-3">
          <div className="text-slate-400 font-semibold uppercase tracking-wider text-[11px] pb-1 border-b border-slate-800">
            1. Source Artifacts
          </div>
          {fileNodes.map((n) => (
            <div
              key={n.id}
              onClick={() => onSelectNode && onSelectNode(n.id, n.type, n.metadata)}
              className="p-3 bg-[#162036] border border-ctf-border hover:border-ctf-cyan rounded-lg cursor-pointer transition-colors shadow-sm"
            >
              <div className="flex items-center gap-2 text-slate-200 font-semibold mb-1 truncate">
                <FileCode className="w-4 h-4 text-sky-400 shrink-0" />
                <span className="truncate">{n.label}</span>
              </div>
              <div className="text-[10px] text-slate-400 truncate">
                SHA: {n.metadata?.sha256?.slice(0, 16)}...
              </div>
            </div>
          ))}
        </div>

        {/* Column 2: Transform Steps & Extractions */}
        <div className="space-y-3">
          <div className="text-slate-400 font-semibold uppercase tracking-wider text-[11px] pb-1 border-b border-slate-800">
            2. Decode & Extraction Pipeline
          </div>
          {transformNodes.length === 0 ? (
            <div className="p-4 text-slate-600 italic border border-dashed border-slate-800 rounded">
              Direct match (zero transforms)
            </div>
          ) : (
            transformNodes.map((n) => (
              <div
                key={n.id}
                onClick={() => onSelectNode && onSelectNode(n.id, n.type, n.metadata)}
                className="p-3 bg-purple-950/20 border border-purple-900/60 hover:border-purple-500 rounded-lg cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-2 text-purple-300 font-medium mb-1 truncate">
                  <ArrowRight className="w-3.5 h-3.5 text-purple-400 shrink-0" />
                  <span className="truncate">{n.label}</span>
                </div>
                {n.metadata?.output_preview && (
                  <div className="text-[10px] text-purple-400/80 truncate">
                    Output: {n.metadata.output_preview}
                  </div>
                )}
              </div>
            ))
          )}
        </div>

        {/* Column 3: Flag Candidates */}
        <div className="space-y-3">
          <div className="text-slate-400 font-semibold uppercase tracking-wider text-[11px] pb-1 border-b border-slate-800">
            3. Discovered Flags
          </div>
          {candidateNodes.map((n) => (
            <div
              key={n.id}
              onClick={() => onSelectNode && onSelectNode(n.id, n.type, n.metadata)}
              className="p-3 bg-cyan-950/30 border border-cyan-800/80 hover:border-ctf-cyan rounded-lg cursor-pointer transition-colors shadow-md"
            >
              <div className="flex items-center gap-2 text-ctf-cyan font-bold mb-1 truncate">
                <Flag className="w-4 h-4 text-ctf-cyan shrink-0" />
                <span className="truncate">{n.label}</span>
              </div>
              <div className="flex items-center justify-between text-[10px] text-slate-400">
                <span>Offset: 0x{n.metadata?.offset?.toString(16)}</span>
                <span className="text-cyan-300 font-semibold">{n.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
