import React from "react";
import { Network, Terminal, ShieldAlert, Cpu } from "lucide-react";

export const ForensicsView: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto p-6 font-mono text-xs space-y-6">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card space-y-4">
        <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2 mb-1">
          <Network className="w-5 h-5 text-ctf-cyan" /> Network & Systems Forensics
        </h1>
        <p className="text-slate-400 font-sans text-sm">
          Reconstruct TCP conversations, inspect packet captures (PCAP/PCAPNG), carve HTTP streams, credentials, and normalize server access logs.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded-lg space-y-2">
            <span className="text-ctf-cyan font-bold text-sm block">PCAP Stream Reassembly</span>
            <p className="text-slate-400 text-xs">
              Reassembles IP/TCP conversation payloads across source and destination sockets. Detects HTTP Basic Authentication tokens, FTP passwords, and scans payload buffers for flag patterns.
            </p>
          </div>

          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded-lg space-y-2">
            <span className="text-ctf-cyan font-bold text-sm block">Log Event Normalization & Threat Triage</span>
            <p className="text-slate-400 text-xs">
              Parses Apache, Nginx, auth, and syslog files. Highlights SQL injection patterns, directory traversal attempts, and client authorization errors in chronological order.
            </p>
          </div>
        </div>

        <div className="mt-4 p-4 bg-slate-900 border border-ctf-border rounded text-slate-300">
          <strong>Usage:</strong> Ingest any <code>.pcap</code>, <code>.pcapng</code>, or <code>.log</code> file into your challenge. The background orchestrator automatically triggers stream carving and credential extraction.
        </div>
      </div>
    </div>
  );
};
