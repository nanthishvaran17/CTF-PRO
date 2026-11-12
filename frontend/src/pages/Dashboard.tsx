import React, { useState, useEffect } from "react";
import { api, DashboardStats, ChallengeItem } from "../api/client";
import { 
  ShieldCheck, 
  Flag, 
  FileCode, 
  AlertTriangle, 
  Wrench, 
  Plus, 
  Clock, 
  ArrowRight,
  Activity,
  Layers
} from "lucide-react";

interface DashboardProps {
  onNavigate: (view: string, challengeId?: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [challenges, setChallenges] = useState<ChallengeItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.all([
      api.getDashboardStats().catch(() => null),
      api.listChallenges().catch(() => [])
    ]).then(([s, c]) => {
      setStats(s);
      setChallenges(c);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-500 font-mono animate-pulse">
        Connecting to local CTF analysis engine...
      </div>
    );
  }

  return (
    <div className="space-y-6 font-mono text-xs max-w-7xl mx-auto p-4 md:p-6">
      {/* Hero Welcome & Quick Action */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between p-6 bg-ctf-surface border border-ctf-border rounded-card gap-4">
        <div>
          <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2">
            <Activity className="w-5 h-5 text-ctf-cyan" /> CTF HUNTER X Workstation
          </h1>
          <p className="text-slate-400 mt-1 text-sm font-sans">
            Evidence-based flag discovery platform. All findings backed by deterministic byte provenance.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate("new-challenge")}
            className="flex items-center gap-2 px-4 py-2 bg-ctf-cyan hover:bg-ctf-cyanHover text-black font-semibold rounded transition-colors shadow-lg"
          >
            <Plus className="w-4 h-4 stroke-[3]" />
            <span>New Challenge</span>
          </button>
          <button
            onClick={() => onNavigate("tools")}
            className="flex items-center gap-2 px-3 py-2 bg-[#162036] hover:bg-slate-700 border border-ctf-border text-slate-200 rounded transition-colors"
          >
            <Wrench className="w-4 h-4 text-ctf-cyan" />
            <span>Tools Status</span>
          </button>
        </div>
      </div>

      {/* Database-Driven Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="p-4 bg-ctf-surface border border-ctf-border rounded-card">
          <div className="text-slate-400 mb-1 flex items-center justify-between">
            <span>Challenges</span>
            <Layers className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.challenges_total ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Active investigations</div>
        </div>

        <div className="p-4 bg-ctf-surface border border-ctf-border rounded-card">
          <div className="text-slate-400 mb-1 flex items-center justify-between">
            <span>Files Analyzed</span>
            <FileCode className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.files_analyzed ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Ingested read-only</div>
        </div>

        <div className="p-4 bg-ctf-surface border border-ctf-border rounded-card">
          <div className="text-slate-400 mb-1 flex items-center justify-between">
            <span>Discovered Flags</span>
            <Flag className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-ctf-cyan">{stats?.candidates_total ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Candidates in DB</div>
        </div>

        <div className="p-4 bg-ctf-surface border border-ctf-border rounded-card">
          <div className="text-slate-400 mb-1 flex items-center justify-between">
            <span>Verified</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{stats?.verified_flags ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Confirmed by oracle</div>
        </div>

        <div className="p-4 bg-ctf-surface border border-ctf-border rounded-card">
          <div className="text-slate-400 mb-1 flex items-center justify-between">
            <span>Pending</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-300">{stats?.pending_flags ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Validation pending</div>
        </div>

        <div className="p-4 bg-ctf-surface border border-ctf-border rounded-card">
          <div className="text-slate-400 mb-1 flex items-center justify-between">
            <span>Host Tools</span>
            <Wrench className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {stats?.tools_installed ?? 0} <span className="text-xs text-slate-500">/ {stats?.tools_total ?? 14}</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-1">Installed binaries</div>
        </div>
      </div>

      {/* Challenges Table & Recent Activity */}
      <div className="bg-ctf-surface border border-ctf-border rounded-card overflow-hidden">
        <div className="px-5 py-3.5 bg-[#162036] border-b border-ctf-border flex items-center justify-between">
          <span className="font-bold text-slate-200 text-sm">Active CTF Challenges</span>
          <span className="text-slate-400 text-xs">{challenges.length} total</span>
        </div>

        {challenges.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-3">
            <Layers className="w-10 h-10 mx-auto opacity-30 text-ctf-cyan" />
            <p className="text-sm">Database is empty. No challenges recorded yet.</p>
            <button
              onClick={() => onNavigate("new-challenge")}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-ctf-surface hover:bg-slate-800 border border-ctf-cyan text-ctf-cyan rounded"
            >
              <Plus className="w-3.5 h-3.5" /> Create First Challenge
            </button>
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {challenges.map((c) => (
              <div
                key={c.id}
                onClick={() => onNavigate("workspace", c.id)}
                className="p-4 hover:bg-slate-800/50 flex items-center justify-between cursor-pointer transition-colors"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-sm hover:text-ctf-cyan">{c.title}</span>
                    <span className="px-2 py-0.5 bg-slate-800 border border-slate-700 text-cyan-400 rounded text-[10px]">
                      {c.category}
                    </span>
                  </div>
                  <div className="text-slate-400 text-[11px]">
                    Files: {c.file_count} &bull; Candidates: {c.candidate_count} &bull; Verified: {c.verified_count} &bull; Created {new Date(c.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-ctf-cyan hover:underline flex items-center gap-1">
                    Open Workspace <ArrowRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
