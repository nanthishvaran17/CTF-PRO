import React from "react";
import { Cpu, Terminal, Shield, Lock } from "lucide-react";

export const ReView: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto p-6 font-mono text-xs space-y-6">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card space-y-4">
        <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2 mb-1">
          <Cpu className="w-5 h-5 text-ctf-cyan" /> Reverse Engineering Workstation
        </h1>
        <p className="text-slate-400 font-sans text-sm">
          Static binary inspection for Linux ELF, Windows PE, and macOS Mach-O binaries. Decompilation hooks and suspicious API syscall detection.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded-lg space-y-2">
            <span className="text-ctf-cyan font-bold block">ELF 32/64 Header Inspection</span>
            <p className="text-slate-400 text-xs">
              Extracts section headers (.text, .rodata, .symtab), entrypoint virtual address, architecture (x86_64, ARM, MIPS), and string tables.
            </p>
          </div>

          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded-lg space-y-2">
            <span className="text-ctf-cyan font-bold block">Windows PE Section & COFF Analysis</span>
            <p className="text-slate-400 text-xs">
              Parses MS-DOS header, PE signature, Optional header, sections (.text, .rdata), import tables, and entrypoint offsets.
            </p>
          </div>

          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded-lg space-y-2">
            <span className="text-ctf-cyan font-bold block">Suspicious API Call Audit</span>
            <p className="text-slate-400 text-xs">
              Flags imports and references to <code>system</code>, <code>VirtualAlloc</code>, <code>ptrace</code>, <code>mprotect</code>, and remote process injection routines.
            </p>
          </div>
        </div>

        <div className="mt-4 p-4 bg-purple-950/20 border border-purple-900/60 rounded text-purple-300">
          <strong className="block mb-1">Execution Safety Policy:</strong>
          Uploaded binaries are NEVER executed directly on the host operating system. All analysis is strictly static or performed within isolated, unprivileged container boundaries.
        </div>
      </div>
    </div>
  );
};
