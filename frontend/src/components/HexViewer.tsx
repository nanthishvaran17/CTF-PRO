import React, { useState, useEffect } from "react";
import { api, HexRow } from "../api/client";
import { ChevronLeft, ChevronRight, Hash, Copy, Check } from "lucide-react";

interface HexViewerProps {
  fileId?: string;
  highlightOffset?: number;
}

export const HexViewer: React.FC<HexViewerProps> = ({ fileId, highlightOffset }) => {
  const [offset, setOffset] = useState<number>(0);
  const [length] = useState<number>(256);
  const [rows, setRows] = useState<HexRow[]>([]);
  const [totalSize, setTotalSize] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    if (highlightOffset !== undefined && highlightOffset >= 0) {
      // Align offset to previous 16-byte boundary
      const aligned = Math.max(0, Math.floor(highlightOffset / 16) * 16 - 32);
      setOffset(aligned);
    }
  }, [highlightOffset]);

  useEffect(() => {
    if (!fileId) return;
    setLoading(true);
    api.getFileHex(fileId, offset, length)
      .then((data) => {
        setRows(data.rows || []);
        setTotalSize(data.total_size || 0);
      })
      .catch((err) => console.error("Hex fetch error", err))
      .finally(() => setLoading(false));
  }, [fileId, offset, length]);

  const copyHex = () => {
    const fullText = rows.map((r) => `${r.offset}  ${r.hex}  |${r.ascii}|`).join("\n");
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!fileId) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-slate-500 font-mono text-sm border border-ctf-border rounded-card bg-ctf-surface">
        <Hash className="w-8 h-8 mb-2 opacity-50 text-ctf-cyan" />
        <p>Select a file from the workspace to inspect hex bytes and offsets.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-ctf-surface border border-ctf-border rounded-card overflow-hidden text-xs font-mono">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#162036] border-b border-ctf-border">
        <div className="flex items-center gap-3">
          <span className="text-ctf-cyan font-bold flex items-center gap-1.5">
            <Hash className="w-4 h-4" /> Hex Viewer
          </span>
          <span className="text-slate-400">
            Offset: <span className="text-slate-200">0x{offset.toString(16).toUpperCase()}</span> ({offset} of {totalSize.toLocaleString()} B)
          </span>
          {highlightOffset !== undefined && (
            <span className="px-2 py-0.5 bg-cyan-950 border border-cyan-700 text-cyan-300 rounded text-[11px]">
              Target: 0x{highlightOffset.toString(16).toUpperCase()} ({highlightOffset})
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={copyHex}
            className="flex items-center gap-1 px-2.5 py-1 bg-ctf-surface hover:bg-slate-700 border border-ctf-border rounded text-slate-300 transition-colors"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? "Copied" : "Copy Hex"}</span>
          </button>
          <button
            disabled={offset <= 0 || loading}
            onClick={() => setOffset(Math.max(0, offset - length))}
            className="p-1 bg-ctf-surface hover:bg-slate-700 disabled:opacity-40 border border-ctf-border rounded text-slate-300"
            title="Previous Page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            disabled={offset + length >= totalSize || loading}
            onClick={() => setOffset(offset + length)}
            className="p-1 bg-ctf-surface hover:bg-slate-700 disabled:opacity-40 border border-ctf-border rounded text-slate-300"
            title="Next Page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Hex Content Grid */}
      <div className="flex-1 overflow-auto p-4 select-text">
        {loading ? (
          <div className="text-slate-500 py-8 text-center animate-pulse">Reading chunk bytes...</div>
        ) : rows.length === 0 ? (
          <div className="text-slate-500 py-8 text-center">No byte content at this offset range.</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="text-slate-500 border-b border-ctf-border pb-1">
                <th className="w-24 pb-1">OFFSET</th>
                <th className="pb-1 tracking-widest">
                  00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F
                </th>
                <th className="w-36 pb-1">DECODED ASCII</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40">
              {rows.map((row) => {
                const isTargetRow =
                  highlightOffset !== undefined &&
                  highlightOffset >= row.offset_dec &&
                  highlightOffset < row.offset_dec + 16;

                return (
                  <tr
                    key={row.offset}
                    className={`hover:bg-slate-800/50 ${isTargetRow ? "bg-cyan-950/40 font-semibold text-cyan-200" : ""}`}
                  >
                    <td className="py-1 text-slate-500">{row.offset.padStart(8, "0")}</td>
                    <td className="py-1 text-slate-300 font-mono tracking-wider">{row.hex}</td>
                    <td className="py-1 text-slate-400 font-mono border-l border-slate-800 pl-3">
                      {row.ascii}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
