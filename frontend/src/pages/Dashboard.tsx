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
  Layers,
  Sparkles,
  Cpu,
  Globe,
  Image as ImageIcon,
  KeyRound,
  Network,
  Compass,
  Zap,
  CheckCircle2,
  Shield,
  Search,
  ExternalLink
} from "lucide-react";

interface DashboardProps {
  onNavigate: (view: string, challengeId?: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [challenges, setChallenges] = useState<ChallengeItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchFilter, setSearchFilter] = useState<string>("");

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
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4 font-mono text-xs">
        <div className="relative">
          <div className="w-12 h-12 rounded-full border-2 border-ctf-cyan/20 border-t-ctf-cyan animate-spin"></div>
          <Activity className="w-5 h-5 text-ctf-cyan absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        </div>
        <div className="text-slate-400 font-medium tracking-wider uppercase text-[11px]">
          Initializing CTF HUNTER X Telemetry...
        </div>
      </div>
    );
  }

  const engineModules = [
    {
      id: "stego",
      name: "Steganography",
      icon: ImageIcon,
      description: "PNG chunk audit, LSB RGB bitplanes, post-IEND trailing payload detection.",
      badge: "Real RGB Bitplane",
      color: "from-cyan-500/20 to-blue-500/10",
      accent: "text-cyan-400"
    },
    {
      id: "forensics",
      name: "Network Forensics",
      icon: Network,
      description: "PCAP/PCAPNG TCP stream reassembly, HTTP carver, credential pattern hunting.",
      badge: "Stream Reassembly",
      color: "from-indigo-500/20 to-purple-500/10",
      accent: "text-indigo-400"
    },
    {
      id: "crypto",
      name: "Cryptanalysis",
      icon: KeyRound,
      description: "Caesar, Atbash, Vigenère, single/multi-byte XOR brute, chi-squared scoring, weak RSA.",
      badge: "XOR & Chi-Sq",
      color: "from-amber-500/20 to-orange-500/10",
      accent: "text-amber-400"
    },
    {
      id: "web",
      name: "Web (SSRF-Guarded)",
      icon: Globe,
      description: "Strict IP validation blocks loopback, private RFC 1918 subnets, and cloud metadata.",
      badge: "SSRF Protected",
      color: "from-emerald-500/20 to-teal-500/10",
      accent: "text-emerald-400"
    },
    {
      id: "re",
      name: "Reverse Engineering",
      icon: Cpu,
      description: "ELF, PE, Mach-O header parsing, section anomaly check, embedded strings.",
      badge: "Static Safe",
      color: "from-purple-500/20 to-pink-500/10",
      accent: "text-purple-400"
    },
    {
      id: "osint",
      name: "OSINT & Media",
      icon: Compass,
      description: "EXIF GPS extraction to decimal coordinates, audio envelope & spectral analysis.",
      badge: "GPS Coords",
      color: "from-sky-500/20 to-cyan-500/10",
      accent: "text-sky-400"
    }
  ];

  const filteredChallenges = challenges.filter((c) =>
    c.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
    c.category.toLowerCase().includes(searchFilter.toLowerCase())
  );

  return (
    <div className="space-y-6 font-mono text-xs max-w-7xl mx-auto p-4 md:p-6">
      {/* World-Class Cyber Command Hero */}
      <div className="relative overflow-hidden p-6 md:p-8 bg-gradient-to-br from-[#0F172A] via-[#0B0F1A] to-[#0A0E18] border border-cyan-500/30 rounded-2xl shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
        <div className="absolute bottom-0 left-0 w-72 h-72 bg-blue-500/5 rounded-full blur-2xl pointer-events-none -ml-10 -mb-10"></div>

        <div className="relative z-10 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/80 border border-cyan-800/80 text-cyan-300 text-[10px] font-mono tracking-wider">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
              <span>AUTONOMOUS EVIDENCE-ANCHORED CTF WORKSTATION</span>
            </div>
            
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              CTF HUNTER <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-blue-500">X</span>
            </h1>

            <p className="text-slate-300 font-sans text-sm leading-relaxed">
              Zero fake flags. Every discovered candidate is cryptographically provable with source SHA-256,
              magic-byte validation, exact byte offsets, and reproducible multi-layer decode DAGs.
            </p>

            <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px] text-slate-400">
              <span className="flex items-center gap-1 px-2.5 py-1 bg-black/40 border border-slate-800 rounded">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Deterministic Fallbacks</span>
              </span>
              <span className="flex items-center gap-1 px-2.5 py-1 bg-black/40 border border-slate-800 rounded">
                <Shield className="w-3.5 h-3.5 text-cyan-400" />
                <span>Read-Only File Vault (0o444)</span>
              </span>
              <span className="flex items-center gap-1 px-2.5 py-1 bg-black/40 border border-slate-800 rounded">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>Recursive Cycle-Safe Decoder</span>
              </span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full lg:w-auto">
            <button
              onClick={() => onNavigate("new-challenge")}
              className="flex items-center justify-center gap-2 px-5 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-bold rounded-xl shadow-[0_0_25px_rgba(6,182,212,0.35)] transition-all duration-200 transform hover:-translate-y-0.5 text-sm"
            >
              <Plus className="w-4 h-4 stroke-[3]" />
              <span>New Challenge</span>
            </button>
            <button
              onClick={() => onNavigate("workspace")}
              className="flex items-center justify-center gap-2 px-4 py-3 bg-slate-900/90 hover:bg-slate-800 border border-cyan-500/30 hover:border-cyan-400 text-slate-200 rounded-xl transition-all duration-200 text-xs font-semibold"
            >
              <Layers className="w-4 h-4 text-cyan-400" />
              <span>3-Panel HUD</span>
            </button>
          </div>
        </div>
      </div>

      {/* Database-Driven Key Performance Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
        <div className="p-4 bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 rounded-xl backdrop-blur-sm transition-all duration-200">
          <div className="text-slate-400 mb-1 flex items-center justify-between">
            <span className="text-[11px] font-medium">Challenges</span>
            <Layers className="w-4 h-4 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.challenges_total ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Active investigations</div>
        </div>

        <div className="p-4 bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 rounded-xl backdrop-blur-sm transition-all duration-200">
          <div className="text-slate-400 mb-1 flex items-center justify-between">
            <span className="text-[11px] font-medium">Files Ingested</span>
            <FileCode className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats?.files_analyzed ?? 0}</div>
          <div className="text-[10px] text-slate-500 mt-1">Vault read-only</div>
        </div>

        <div className="p-4 bg-slate-900/60 border border-cyan-900/40 hover:border-cyan-500/40 rounded-xl backdrop-blur-sm transition-all duration-200">
          <div className="text-cyan-400 mb-1 flex items-center justify-between">
            <span className="text-[11px] font-medium">Flags Discovered</span>
            <Flag className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-300">{stats?.candidates_total ?? 0}</div>
          <div className="text-[10px] text-cyan-500/70 mt-1">Cryptographic proof</div>
        </div>

        <div className="p-4 bg-slate-900/60 border border-emerald-900/40 hover:border-emerald-500/40 rounded-xl backdrop-blur-sm transition-all duration-200">
          <div className="text-emerald-400 mb-1 flex items-center justify-between">
            <span className="text-[11px] font-medium">Oracle Confirmed</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{stats?.verified_flags ?? 0}</div>
          <div className="text-[10px] text-emerald-500/70 mt-1">Scoreboard verified</div>
        </div>

        <div className="p-4 bg-slate-900/60 border border-amber-900/40 hover:border-amber-500/40 rounded-xl backdrop-blur-sm transition-all duration-200">
          <div className="text-amber-400 mb-1 flex items-center justify-between">
            <span className="text-[11px] font-medium">Validation Pending</span>
            <Clock className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-300">{stats?.pending_flags ?? 0}</div>
          <div className="text-[10px] text-amber-500/70 mt-1">Awaiting oracle hook</div>
        </div>

        <div className="p-4 bg-slate-900/60 border border-purple-900/40 hover:border-purple-500/40 rounded-xl backdrop-blur-sm transition-all duration-200">
          <div className="text-purple-400 mb-1 flex items-center justify-between">
            <span className="text-[11px] font-medium">Host Tooling</span>
            <Wrench className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-white">
            {stats?.tools_installed ?? 0} <span className="text-xs text-slate-500">/ {stats?.tools_total ?? 14}</span>
          </div>
          <div className="text-[10px] text-purple-400/70 mt-1">Python fallbacks ready</div>
        </div>
      </div>

      {/* Specialized Analysis Engines Grid */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-cyan-400" /> Autonomous Domain Analyzers
            </h2>
            <p className="text-[11px] text-slate-400">Pure-Python fallbacks active when external binaries are unavailable.</p>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
            7 Analyzers Active
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {engineModules.map((m) => {
            const Icon = m.icon;
            return (
              <div
                key={m.id}
                onClick={() => onNavigate(m.id)}
                className="group p-4 bg-slate-900/50 hover:bg-slate-850 border border-slate-800 hover:border-cyan-500/50 rounded-xl transition-all duration-200 cursor-pointer flex flex-col justify-between space-y-3"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="p-2 rounded-lg bg-slate-800/80 group-hover:bg-cyan-950/60 transition-colors">
                        <Icon className={`w-4 h-4 ${m.accent}`} />
                      </div>
                      <span className="font-bold text-slate-200 group-hover:text-cyan-300 transition-colors text-xs">
                        {m.name}
                      </span>
                    </div>
                    <span className="text-[9px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700/50 font-mono">
                      {m.badge}
                    </span>
                  </div>
                  <p className="text-slate-400 text-[11px] leading-relaxed font-sans">
                    {m.description}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-[11px] text-slate-400 group-hover:text-cyan-300">
                  <span>Open Dedicated View</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Challenges Management Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="p-4 bg-slate-850 border-b border-slate-800 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-bold text-white text-sm">Active CTF Targets</span>
            <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px] font-mono">
              {challenges.length} Recorded
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Filter targets..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="pl-8 pr-3 py-1.5 bg-slate-900 border border-slate-700/80 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400 w-48 sm:w-56"
              />
            </div>
            <button
              onClick={() => onNavigate("new-challenge")}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-black font-semibold rounded-lg text-xs transition-colors"
            >
              <Plus className="w-3.5 h-3.5 stroke-[3]" />
              <span>Add</span>
            </button>
          </div>
        </div>

        {filteredChallenges.length === 0 ? (
          <div className="p-12 text-center text-slate-500 space-y-3">
            <Layers className="w-12 h-12 mx-auto opacity-20 text-cyan-400" />
            <p className="text-sm font-sans">
              {challenges.length === 0 ? "No active CTF challenges in local database." : "No targets match your filter query."}
            </p>
            {challenges.length === 0 && (
              <button
                onClick={() => onNavigate("new-challenge")}
                className="inline-flex items-center gap-1.5 px-4 py-2 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 rounded-lg transition-colors font-medium text-xs"
              >
                <Plus className="w-3.5 h-3.5" /> Ingest First CTF Challenge
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y divide-slate-800/80">
            {filteredChallenges.map((c) => (
              <div
                key={c.id}
                onClick={() => onNavigate("workspace", c.id)}
                className="p-4 hover:bg-slate-800/40 flex items-center justify-between cursor-pointer transition-colors group"
              >
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2.5">
                    <span className="font-bold text-white text-sm group-hover:text-cyan-300 transition-colors">
                      {c.title}
                    </span>
                    <span className="px-2 py-0.5 bg-slate-800 border border-slate-700/80 text-cyan-400 rounded-md text-[10px]">
                      {c.category}
                    </span>
                  </div>
                  <div className="text-slate-400 text-[11px] flex flex-wrap items-center gap-3">
                    <span>Files: <strong className="text-slate-300">{c.file_count}</strong></span>
                    <span>&bull;</span>
                    <span>Candidates: <strong className="text-cyan-300">{c.candidate_count}</strong></span>
                    <span>&bull;</span>
                    <span>Verified: <strong className="text-emerald-400">{c.verified_count}</strong></span>
                    <span>&bull;</span>
                    <span className="text-slate-500">{new Date(c.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-cyan-400 group-hover:text-cyan-300 font-medium text-xs">
                  <span>Open Workspace</span>
                  <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Security Architecture & Hardening Verification Footer */}
      <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-[11px] text-slate-400">
        <div className="flex flex-wrap items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            <span>SQLite WAL Async Storage</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
            <span>Zip-Slip & 100:1 Bomb Defense Active</span>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
            <span>SSRF Guard: Loopback & Metadata Bounded</span>
          </span>
        </div>
        <button
          onClick={() => onNavigate("tools")}
          className="text-cyan-400 hover:text-cyan-300 hover:underline flex items-center gap-1"
        >
          <span>Audit 14 Security Binaries</span>
          <ExternalLink className="w-3 h-3" />
        </button>
      </div>
    </div>
  );
};
