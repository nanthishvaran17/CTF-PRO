import React, { useState, useEffect } from "react";
import { api, ChallengeItem } from "../api/client";
import { FileText, Download, Check, AlertCircle, Copy } from "lucide-react";

export const Reports: React.FC = () => {
  const [challenges, setChallenges] = useState<ChallengeItem[]>([]);
  const [selectedChallengeId, setSelectedChallengeId] = useState<string>("");
  const [writeup, setWriteup] = useState<string>("");
  const [format, setFormat] = useState<"HTML" | "JSON" | "CSV" | "PDF">("HTML");
  const [generating, setGenerating] = useState<boolean>(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    api.listChallenges().then((list) => {
      setChallenges(list);
      if (list.length > 0) {
        setSelectedChallengeId(list[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (!selectedChallengeId) return;
    setDownloadUrl(null);
    api.getWriteup(selectedChallengeId).then((w) => setWriteup(w.writeup_markdown || ""));
  }, [selectedChallengeId]);

  const handleGenerate = async () => {
    if (!selectedChallengeId) return;
    setGenerating(true);
    try {
      const res = await api.generateReport(selectedChallengeId, format);
      setDownloadUrl(`http://127.0.0.1:8000${res.download_url}`);
    } catch (e) {
      console.error(e);
    } finally {
      setGenerating(false);
    }
  };

  const copyWriteup = () => {
    navigator.clipboard.writeText(writeup);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-6 font-mono text-xs space-y-6">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card">
        <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2 mb-1">
          <FileText className="w-5 h-5 text-ctf-cyan" /> Multi-Format Report Exporter
        </h1>
        <p className="text-slate-400 font-sans text-sm">
          Export verified intelligence, hashes, offsets, and automated writeup chains to HTML, JSON, CSV, or PDF.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="col-span-2">
            <label className="block text-slate-300 font-semibold mb-1">Select Target Challenge</label>
            <select
              value={selectedChallengeId}
              onChange={(e) => setSelectedChallengeId(e.target.value)}
              className="w-full p-2.5 bg-[#0B0F1A] border border-ctf-border rounded text-white focus:outline-none focus:border-ctf-cyan"
            >
              {challenges.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title} ({c.category}) - {c.candidate_count} candidates
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Export Format</label>
            <div className="grid grid-cols-4 gap-1">
              {(["HTML", "JSON", "CSV", "PDF"] as const).map((fmt) => (
                <button
                  key={fmt}
                  type="button"
                  onClick={() => setFormat(fmt)}
                  className={`py-2 rounded font-bold transition-colors ${
                    format === fmt ? "bg-ctf-cyan text-black" : "bg-[#0B0F1A] border border-ctf-border text-slate-300 hover:bg-slate-800"
                  }`}
                >
                  {fmt}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-4 pt-4 border-t border-ctf-border flex items-center justify-between">
          <button
            onClick={handleGenerate}
            disabled={generating || !selectedChallengeId}
            className="flex items-center gap-2 px-5 py-2.5 bg-ctf-cyan hover:bg-ctf-cyanHover disabled:opacity-50 text-black font-bold rounded transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>{generating ? "Exporting..." : `Generate ${format} Report`}</span>
          </button>

          {downloadUrl && (
            <a
              href={downloadUrl}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-4 py-2 bg-emerald-950 border border-emerald-700 text-emerald-300 rounded font-bold hover:bg-emerald-900 transition-colors"
            >
              <Download className="w-4 h-4" /> Download File
            </a>
          )}
        </div>
      </div>

      {/* Auto Writeup Markdown Preview */}
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card space-y-3">
        <div className="flex items-center justify-between pb-2 border-b border-ctf-border">
          <span className="font-bold text-slate-200 text-sm flex items-center gap-2">
            <FileText className="w-4 h-4 text-ctf-cyan" /> Automated CTF Writeup (Markdown)
          </span>
          <button
            onClick={copyWriteup}
            className="flex items-center gap-1.5 px-3 py-1 bg-[#0B0F1A] hover:bg-slate-800 border border-ctf-border rounded text-slate-300 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? "Copied" : "Copy Markdown"}</span>
          </button>
        </div>

        <textarea
          readOnly
          rows={16}
          value={writeup}
          className="w-full p-4 bg-[#0B0F1A] border border-ctf-border rounded font-mono text-xs text-slate-300 select-all focus:outline-none"
        />
      </div>
    </div>
  );
};
