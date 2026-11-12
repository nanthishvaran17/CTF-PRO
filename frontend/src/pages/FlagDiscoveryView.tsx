import React, { useState, useEffect } from "react";
import { api, CandidateFlagItem } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { Flag, Search, Filter, ShieldCheck, Copy, Check } from "lucide-react";

export const FlagDiscoveryView: React.FC = () => {
  const [candidates, setCandidates] = useState<CandidateFlagItem[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [hideDecoys, setHideDecoys] = useState<boolean>(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  useEffect(() => {
    api.getCandidates(undefined, statusFilter || undefined).then((res) => {
      setCandidates(res || []);
    });
  }, [statusFilter]);

  const filtered = candidates.filter((c) => {
    if (hideDecoys && c.is_probable_decoy) return false;
    if (search && !c.flag.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const copyFlag = (id: string, flag: string) => {
    navigator.clipboard.writeText(flag);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-6 font-mono text-xs space-y-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between p-6 bg-ctf-surface border border-ctf-border rounded-card gap-4">
        <div>
          <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2">
            <Flag className="w-5 h-5 text-ctf-cyan" /> Universal Flag Discovery Matrix
          </h1>
          <p className="text-slate-400 mt-1 font-sans text-sm">
            Comprehensive audit table of discovered candidates, decode chains, and authoritative verification records.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col md:flex-row items-center gap-3 p-4 bg-ctf-surface border border-ctf-border rounded-card">
        <div className="flex-1 flex items-center gap-2 bg-[#0B0F1A] border border-ctf-border px-3 py-2 rounded w-full">
          <Search className="w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search discovered flag text or regex..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-transparent text-white placeholder-slate-600 focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="p-2 bg-[#0B0F1A] border border-ctf-border rounded text-white focus:outline-none focus:border-ctf-cyan text-xs"
          >
            <option value="">All Statuses</option>
            <option value="DISCOVERED">DISCOVERED</option>
            <option value="CANDIDATE">CANDIDATE</option>
            <option value="EVIDENCE-SUPPORTED">EVIDENCE-SUPPORTED</option>
            <option value="VALIDATION-PENDING">VALIDATION-PENDING</option>
            <option value="VERIFIED-BY-CHALLENGE">VERIFIED-BY-CHALLENGE</option>
            <option value="REJECTED">REJECTED</option>
            <option value="UNRESOLVED">UNRESOLVED</option>
          </select>

          <label className="flex items-center gap-2 text-slate-300 cursor-pointer select-none whitespace-nowrap">
            <input
              type="checkbox"
              checked={hideDecoys}
              onChange={(e) => setHideDecoys(e.target.checked)}
              className="accent-cyan-400 rounded"
            />
            <span>Hide Decoys</span>
          </label>
        </div>
      </div>

      {/* Flag Table */}
      <div className="bg-ctf-surface border border-ctf-border rounded-card overflow-hidden">
        {filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-500">No flags match the current query and filters.</div>
        ) : (
          <div className="divide-y divide-slate-800">
            {filtered.map((cand) => (
              <div key={cand.id} className="p-4 hover:bg-slate-800/40 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-3">
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <StatusBadge status={cand.status} size="sm" />
                    {cand.is_probable_decoy && (
                      <span className="text-[10px] text-amber-400 font-semibold px-1.5 py-0.5 bg-amber-950/60 border border-amber-800 rounded">
                        Decoy Signal
                      </span>
                    )}
                  </div>
                  <div className="text-ctf-cyan font-bold text-sm truncate font-mono select-all">
                    {cand.flag}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Byte Offset: <code>{cand.byte_offset ?? "N/A"}</code> &bull; Method: <code>{cand.extraction_method}</code> &bull; Discovered: {new Date(cand.created_at).toLocaleString()}
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => copyFlag(cand.id, cand.flag)}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-[#0B0F1A] hover:bg-slate-800 border border-ctf-border rounded text-slate-300 hover:text-ctf-cyan transition-colors"
                  >
                    {copiedId === cand.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    <span>{copiedId === cand.id ? "Copied" : "Copy"}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
