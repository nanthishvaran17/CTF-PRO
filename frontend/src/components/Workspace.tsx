import React, { useState, useEffect } from "react";
import { api, ChallengeItem, FileMeta, CandidateFlagItem, EvidenceGraphData } from "../api/client";
import { StatusBadge } from "./StatusBadge";
import { HexViewer } from "./HexViewer";
import { EvidenceGraph } from "./EvidenceGraph";
import {
  FileCode,
  Layers,
  Flag,
  Play,
  Copy,
  Check,
  Code2,
  FileText,
  ShieldCheck,
  XCircle,
  HelpCircle,
  Hash,
  Terminal,
  Activity,
  Download,
  AlertCircle
} from "lucide-react";

interface WorkspaceProps {
  challengeId?: string;
}

export const Workspace: React.FC<WorkspaceProps> = ({ challengeId }) => {
  const [challenge, setChallenge] = useState<any>(null);
  const [selectedFile, setSelectedFile] = useState<FileMeta | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<CandidateFlagItem | null>(null);
  const [centerTab, setCenterTab] = useState<"hex" | "strings" | "metadata" | "graph" | "results">("hex");
  const [highlightOffset, setHighlightOffset] = useState<number | undefined>(undefined);

  const [jobStatus, setJobStatus] = useState<string>("IDLE");
  const [jobProgress, setJobProgress] = useState<number>(0);
  const [analysisResults, setAnalysisResults] = useState<any[]>([]);
  const [graphData, setGraphData] = useState<EvidenceGraphData>({ nodes: [], edges: [] });
  const [writeup, setWriteup] = useState<string>("");
  const [reproScript, setReproScript] = useState<string>("");

  const [copiedChain, setCopiedChain] = useState<boolean>(false);
  const [validationNote, setValidationNote] = useState<string>("");

  useEffect(() => {
    if (!challengeId) return;
    refreshData();

    // Subscribe to SSE real-time stream
    const evt = api.subscribeEvents((event) => {
      if (event.type === "job_progress") {
        setJobProgress(event.data.progress);
      } else if (event.type === "job_completed" || event.type === "flag_discovered") {
        refreshData();
      }
    });

    return () => evt.close();
  }, [challengeId]);

  const refreshData = () => {
    if (!challengeId) return;
    api.getChallenge(challengeId).then((c) => {
      setChallenge(c);
      if (c.files && c.files.length > 0 && !selectedFile) {
        setSelectedFile(c.files[0]);
      }
      if (c.candidates && c.candidates.length > 0 && !selectedCandidate) {
        setSelectedCandidate(c.candidates[0]);
      }
    });
    api.getAnalysisStatus(challengeId).then((s) => {
      setJobStatus(s.status);
      setJobProgress(s.progress);
    });
    api.getAnalysisResults(challengeId).then((r) => setAnalysisResults(r.results || []));
    api.getEvidenceGraph(challengeId).then((g) => setGraphData(g));
    api.getWriteup(challengeId).then((w) => setWriteup(w.writeup_markdown || ""));
  };

  const handleStartAnalysis = async () => {
    if (!challengeId) return;
    setJobStatus("RUNNING");
    setJobProgress(5);
    await api.startAnalysis(challengeId);
  };

  const handleSelectCandidate = (cand: CandidateFlagItem) => {
    setSelectedCandidate(cand);
    if (cand.byte_offset !== undefined && cand.byte_offset !== null) {
      setHighlightOffset(cand.byte_offset);
      setCenterTab("hex");
    }
    // Fetch repro script
    api.getReproScript(cand.id).then((r) => setReproScript(r.python_script));
  };

  const handleValidate = async (isSuccess: boolean) => {
    if (!selectedCandidate) return;
    await api.validateCandidate(selectedCandidate.id, isSuccess, '{"validated_via": "analyst_oracle"}', validationNote);
    refreshData();
  };

  const copyEvidenceChain = () => {
    if (!selectedCandidate) return;
    const chainStr = JSON.stringify(
      {
        flag: selectedCandidate.flag,
        status: selectedCandidate.status,
        offset: selectedCandidate.byte_offset,
        reasons: selectedCandidate.evidence_reasons,
        method: selectedCandidate.extraction_method,
      },
      null,
      2
    );
    navigator.clipboard.writeText(chainStr);
    setCopiedChain(true);
    setTimeout(() => setCopiedChain(false), 2000);
  };

  if (!challengeId) {
    return (
      <div className="p-12 text-center text-slate-500 font-mono text-sm border border-ctf-border rounded-card bg-ctf-surface">
        <HelpCircle className="w-8 h-8 mx-auto mb-2 opacity-50 text-ctf-cyan" />
        <p>No challenge selected. Please select a challenge from the dashboard or create a new one.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] font-mono text-xs">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-ctf-surface border-b border-ctf-border">
        <div className="flex items-center gap-3">
          <span className="text-slate-100 font-bold text-sm truncate max-w-xs">
            {challenge?.title || "Challenge Workstation"}
          </span>
          <span className="px-2 py-0.5 bg-slate-800 text-cyan-300 border border-slate-700 rounded text-[11px]">
            {challenge?.category || "Misc"}
          </span>
          {jobStatus === "RUNNING" && (
            <div className="flex items-center gap-2 text-cyan-400">
              <Activity className="w-3.5 h-3.5 animate-spin" />
              <span>Analyzing ({jobProgress}%)...</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleStartAnalysis}
            disabled={jobStatus === "RUNNING"}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-ctf-cyan hover:bg-ctf-cyanHover disabled:opacity-50 text-black font-semibold rounded transition-colors shadow"
          >
            <Play className="w-3.5 h-3.5 fill-black" />
            <span>{jobStatus === "RUNNING" ? "Running..." : "Run Analysis"}</span>
          </button>
        </div>
      </div>

      {/* 3-Panel Grid */}
      <div className="flex-1 grid grid-cols-12 gap-0 overflow-hidden">
        {/* PANEL 1: Left Artifacts & Evidence Tree (Cols 3) */}
        <div className="col-span-12 md:col-span-3 bg-[#0E1424] border-r border-ctf-border flex flex-col h-full overflow-hidden">
          <div className="px-3 py-2 bg-[#162036] border-b border-ctf-border font-bold text-slate-300 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <FileCode className="w-3.5 h-3.5 text-ctf-cyan" /> Target Files ({challenge?.files?.length || 0})
            </span>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {challenge?.files?.map((f: FileMeta) => (
              <div
                key={f.id}
                onClick={() => setSelectedFile(f)}
                className={`p-2 rounded cursor-pointer transition-colors border ${
                  selectedFile?.id === f.id
                    ? "bg-slate-800 border-ctf-cyan text-white"
                    : "bg-ctf-surface/50 border-ctf-border text-slate-300 hover:bg-slate-800/60"
                }`}
              >
                <div className="flex items-center justify-between font-medium truncate">
                  <span className="truncate">{f.name}</span>
                  <span className="text-[10px] text-cyan-400 ml-1">{f.file_type}</span>
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5 truncate">
                  {f.size_bytes.toLocaleString()} B &bull; Entropy: {f.entropy}
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 border-t border-ctf-border bg-[#0B0F1A]">
            <div className="text-[11px] font-semibold text-slate-400 mb-1">Quick Links</div>
            <button
              onClick={() => setCenterTab("graph")}
              className="w-full flex items-center gap-1.5 py-1 px-2 text-left text-slate-300 hover:text-ctf-cyan hover:bg-slate-800 rounded transition-colors"
            >
              <Layers className="w-3.5 h-3.5 text-purple-400" /> Evidence Provenance DAG
            </button>
            <button
              onClick={() => setCenterTab("results")}
              className="w-full flex items-center gap-1.5 py-1 px-2 text-left text-slate-300 hover:text-ctf-cyan hover:bg-slate-800 rounded transition-colors"
            >
              <Activity className="w-3.5 h-3.5 text-emerald-400" /> Module Output Cards
            </button>
          </div>
        </div>

        {/* PANEL 2: Center Inspector & Hex Tabs (Cols 5) */}
        <div className="col-span-12 md:col-span-5 bg-ctf-bg flex flex-col h-full overflow-hidden border-r border-ctf-border">
          {/* Tab Selector */}
          <div className="flex items-center gap-1 px-3 py-1.5 bg-[#162036] border-b border-ctf-border">
            <button
              onClick={() => setCenterTab("hex")}
              className={`px-3 py-1 rounded transition-colors ${
                centerTab === "hex" ? "bg-ctf-cyan text-black font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              Hex Viewer
            </button>
            <button
              onClick={() => setCenterTab("metadata")}
              className={`px-3 py-1 rounded transition-colors ${
                centerTab === "metadata" ? "bg-ctf-cyan text-black font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              Metadata
            </button>
            <button
              onClick={() => setCenterTab("graph")}
              className={`px-3 py-1 rounded transition-colors ${
                centerTab === "graph" ? "bg-ctf-cyan text-black font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              Evidence Graph
            </button>
            <button
              onClick={() => setCenterTab("results")}
              className={`px-3 py-1 rounded transition-colors ${
                centerTab === "results" ? "bg-ctf-cyan text-black font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              Analysis Modules
            </button>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-auto p-3">
            {centerTab === "hex" && (
              <HexViewer fileId={selectedFile?.id} highlightOffset={highlightOffset} />
            )}

            {centerTab === "metadata" && selectedFile && (
              <div className="p-4 bg-ctf-surface border border-ctf-border rounded-card space-y-3">
                <div className="font-bold text-sm text-ctf-cyan mb-2">File Provenance & Magic Inspection</div>
                <div className="grid grid-cols-2 gap-2 text-slate-300">
                  <div><strong>Filename:</strong> {selectedFile.name}</div>
                  <div><strong>File Type:</strong> {selectedFile.file_type}</div>
                  <div><strong>MIME Type:</strong> {selectedFile.mime_type}</div>
                  <div><strong>Byte Size:</strong> {selectedFile.size_bytes.toLocaleString()} bytes</div>
                  <div><strong>Entropy:</strong> {selectedFile.entropy} / 8.0</div>
                  <div><strong>Trailing Bytes:</strong> {selectedFile.has_trailing_bytes ? "Detected (Anomaly)" : "Clean"}</div>
                </div>
                <div className="mt-3">
                  <div className="text-slate-400 font-semibold mb-1">SHA-256 Digest:</div>
                  <code className="p-2 bg-[#0B0F1A] border border-ctf-border rounded block text-cyan-300 break-all select-all">
                    {selectedFile.sha256}
                  </code>
                </div>
              </div>
            )}

            {centerTab === "graph" && (
              <EvidenceGraph
                data={graphData}
                onSelectNode={(id, type, meta) => {
                  if (type === "candidate" && meta?.offset !== undefined) {
                    setHighlightOffset(meta.offset);
                    setCenterTab("hex");
                  }
                }}
              />
            )}

            {centerTab === "results" && (
              <div className="space-y-3">
                {analysisResults.length === 0 ? (
                  <div className="p-8 text-center text-slate-500">Run analysis to view findings.</div>
                ) : (
                  analysisResults.map((r, i) => (
                    <div key={i} className="p-3 bg-ctf-surface border border-ctf-border rounded-card">
                      <div className="flex items-center justify-between text-xs font-bold text-ctf-cyan mb-1 uppercase">
                        <span>{r.module}</span>
                        <span className="text-slate-400">{r.summary}</span>
                      </div>
                      <pre className="p-2 bg-[#0B0F1A] border border-slate-800 rounded text-[11px] text-slate-300 overflow-x-auto max-h-48">
                        {JSON.stringify(r.data, null, 2)}
                      </pre>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>

        {/* PANEL 3: Right Candidates & Verification Inspector (Cols 4) */}
        <div className="col-span-12 md:col-span-4 bg-[#0E1424] flex flex-col h-full overflow-hidden border-l border-ctf-border">
          <div className="px-3 py-2 bg-[#162036] border-b border-ctf-border font-bold text-slate-300 flex items-center justify-between">
            <span className="flex items-center gap-1.5">
              <Flag className="w-3.5 h-3.5 text-ctf-cyan" /> Candidates ({challenge?.candidates?.length || 0})
            </span>
          </div>

          {/* Candidate Flag Cards */}
          <div className="p-2 space-y-2 overflow-y-auto max-h-64 border-b border-ctf-border">
            {challenge?.candidates?.length === 0 ? (
              <div className="p-4 text-center text-slate-500">No flags discovered yet.</div>
            ) : (
              challenge?.candidates?.map((cand: CandidateFlagItem) => (
                <div
                  key={cand.id}
                  onClick={() => handleSelectCandidate(cand)}
                  className={`p-2.5 rounded cursor-pointer border transition-colors ${
                    selectedCandidate?.id === cand.id
                      ? "bg-slate-800 border-ctf-cyan"
                      : "bg-ctf-surface/60 border-ctf-border hover:bg-slate-800/40"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <StatusBadge status={cand.status} size="sm" />
                    {cand.is_probable_decoy && (
                      <span className="text-[10px] text-amber-400 font-semibold px-1.5 py-0.5 bg-amber-950/60 border border-amber-800 rounded">
                        Decoy Signal
                      </span>
                    )}
                  </div>
                  <div className="text-ctf-cyan font-bold truncate select-all">{cand.flag}</div>
                  <div className="text-[10px] text-slate-400 mt-1 flex items-center justify-between">
                    <span>Offset: {cand.byte_offset ?? "N/A"}</span>
                    <span>{cand.extraction_method}</span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Inspector Detail for Selected Flag */}
          {selectedCandidate ? (
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              <div className="p-3 bg-ctf-surface border border-ctf-border rounded-card">
                <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Evidence Provenance
                </div>
                <div className="space-y-1 text-slate-300">
                  <div>
                    <strong>Flag:</strong> <code className="text-ctf-cyan font-bold">{selectedCandidate.flag}</code>
                  </div>
                  <div>
                    <strong>Status:</strong> <StatusBadge status={selectedCandidate.status} size="sm" />
                  </div>
                  <div>
                    <strong>Byte Offset:</strong> {selectedCandidate.byte_offset ?? "N/A"}
                  </div>
                  <div>
                    <strong>Method:</strong> {selectedCandidate.extraction_method}
                  </div>
                  <div>
                    <strong>Decoy Reasons:</strong>
                    <ul className="list-disc list-inside text-slate-400 mt-0.5">
                      {selectedCandidate.evidence_reasons?.map((r: string, idx: number) => (
                        <li key={idx}>{r}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Validation Actions */}
                <div className="mt-4 pt-3 border-t border-ctf-border">
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Authoritative Validation
                  </div>
                  <input
                    type="text"
                    placeholder="Validation note / scoreboard response..."
                    value={validationNote}
                    onChange={(e) => setValidationNote(e.target.value)}
                    className="w-full p-1.5 bg-[#0B0F1A] border border-ctf-border rounded text-slate-200 placeholder-slate-600 mb-2 focus:outline-none focus:border-ctf-cyan"
                  />
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleValidate(true)}
                      className="flex items-center justify-center gap-1 py-1.5 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 rounded font-semibold transition-colors"
                    >
                      <ShieldCheck className="w-3.5 h-3.5" /> Accept (Verified)
                    </button>
                    <button
                      onClick={() => handleValidate(false)}
                      className="flex items-center justify-center gap-1 py-1.5 bg-rose-950 hover:bg-rose-900 border border-rose-800 text-rose-300 rounded font-semibold transition-colors"
                    >
                      <XCircle className="w-3.5 h-3.5" /> Reject
                    </button>
                  </div>
                </div>

                {/* Reproduction & Evidence Chain Export */}
                <div className="mt-4 pt-3 border-t border-ctf-border space-y-2">
                  <button
                    onClick={copyEvidenceChain}
                    className="w-full flex items-center justify-center gap-1.5 py-1.5 bg-slate-800 hover:bg-slate-700 border border-ctf-border rounded text-slate-300 transition-colors"
                  >
                    {copiedChain ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedChain ? "Copied Evidence" : "Copy Evidence Chain"}</span>
                  </button>
                </div>
              </div>

              {/* Repro script preview */}
              {reproScript && (
                <div className="p-3 bg-ctf-surface border border-ctf-border rounded-card">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-slate-300 text-[11px] flex items-center gap-1">
                      <Code2 className="w-3.5 h-3.5 text-ctf-cyan" /> Repro Script
                    </span>
                    <button
                      onClick={() => navigator.clipboard.writeText(reproScript)}
                      className="text-slate-400 hover:text-ctf-cyan"
                      title="Copy Script"
                    >
                      <Copy className="w-3 h-3" />
                    </button>
                  </div>
                  <pre className="p-2 bg-[#0B0F1A] border border-slate-800 rounded text-[10px] text-slate-300 overflow-x-auto max-h-36">
                    {reproScript}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="p-8 text-center text-slate-500">Select a flag to inspect evidence chain.</div>
          )}
        </div>
      </div>
    </div>
  );
};
