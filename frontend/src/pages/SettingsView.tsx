import React from "react";
import { Settings, Shield, HardDrive, Terminal } from "lucide-react";

export const SettingsView: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-6 font-mono text-xs space-y-6">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card space-y-4">
        <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2 mb-1">
          <Settings className="w-5 h-5 text-ctf-cyan" /> Workstation Configuration & Sandbox Parameters
        </h1>
        <p className="text-slate-400 font-sans text-sm">
          Platform operational mode, decompression safety boundaries, and storage paths.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-ctf-border">
          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded space-y-2">
            <span className="text-slate-300 font-bold block flex items-center gap-1.5">
              <Shield className="w-4 h-4 text-cyan-400" /> Operational Mode
            </span>
            <div className="text-white font-bold text-sm">LOCAL (Default)</div>
            <p className="text-slate-400 text-[11px]">
              Loopback zero-friction mode. Authentication is disabled for local forensic workflows. Mutating requests are restricted to localhost.
            </p>
          </div>

          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded space-y-2">
            <span className="text-slate-300 font-bold block flex items-center gap-1.5">
              <HardDrive className="w-4 h-4 text-purple-400" /> Storage Engine
            </span>
            <div className="text-white font-bold text-sm">SQLite (WAL Async)</div>
            <p className="text-slate-400 text-[11px]">
              Content-addressed file vault with read-only permission enforcement (0o444) on ingested evidence.
            </p>
          </div>
        </div>

        <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded space-y-2">
          <span className="text-slate-300 font-bold block">Hardcoded Safety Thresholds</span>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-slate-300">
            <div>Max Upload Size: <strong>500 MB</strong></div>
            <div>Max Unpacked Size: <strong>250 MB</strong></div>
            <div>Max Decode Depth: <strong>8 Steps</strong></div>
            <div>Decompression Ratio Cap: <strong>100:1</strong></div>
          </div>
        </div>
      </div>
    </div>
  );
};
