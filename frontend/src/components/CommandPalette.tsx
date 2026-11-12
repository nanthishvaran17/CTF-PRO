import React, { useState, useEffect } from "react";
import { Search, Terminal, FileCode, Shield, Layers, Wrench, FileText } from "lucide-react";

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (view: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose, onNavigate }) => {
  const [query, setQuery] = useState("");

  const commands = [
    { id: "dashboard", label: "Go to Dashboard", icon: Terminal, category: "Navigation" },
    { id: "new-challenge", label: "Create New Challenge", icon: FileCode, category: "Action" },
    { id: "workspace", label: "Open 3-Panel Workspace", icon: Layers, category: "Navigation" },
    { id: "hex-viewer", label: "Jump to Hex Viewer (g+h)", icon: Terminal, category: "Inspection" },
    { id: "evidence", label: "Open Evidence Graph (g+e)", icon: Shield, category: "Verification" },
    { id: "tools", label: "Security Tool Manager", icon: Wrench, category: "System" },
    { id: "reports", label: "Generate Reports (g+r)", icon: FileText, category: "Export" },
  ];

  const filtered = commands.filter((c) =>
    c.label.toLowerCase().includes(query.toLowerCase()) ||
    c.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-lg bg-ctf-surface border border-ctf-border rounded-card shadow-2xl overflow-hidden font-mono text-xs">
        <div className="flex items-center gap-2.5 px-4 py-3 border-b border-ctf-border bg-[#162036]">
          <Search className="w-4 h-4 text-ctf-cyan" />
          <input
            autoFocus
            type="text"
            placeholder="Type a command or jump to page... (Esc to exit)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 focus:outline-none"
          />
        </div>

        <div className="max-h-72 overflow-y-auto p-2">
          {filtered.length === 0 ? (
            <div className="p-4 text-slate-500 text-center">No matching command.</div>
          ) : (
            filtered.map((cmd) => {
              const Icon = cmd.icon;
              return (
                <button
                  key={cmd.id}
                  onClick={() => {
                    onNavigate(cmd.id);
                    onClose();
                  }}
                  className="w-full flex items-center justify-between p-2.5 hover:bg-slate-800 rounded-lg text-slate-300 hover:text-ctf-cyan text-left transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 text-slate-400" />
                    <span>{cmd.label}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 uppercase px-1.5 py-0.5 border border-slate-700 rounded">
                    {cmd.category}
                  </span>
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
