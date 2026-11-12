import React, { useState, useEffect } from "react";
import { 
  Terminal, 
  Layers, 
  Flag, 
  Wrench, 
  FileText, 
  Plus, 
  Settings, 
  Image as ImageIcon, 
  KeyRound, 
  Network, 
  Globe, 
  Cpu, 
  Compass, 
  Search,
  Activity,
  Menu,
  X
} from "lucide-react";

import { Dashboard } from "./pages/Dashboard";
import { NewChallenge } from "./pages/NewChallenge";
import { Workspace } from "./components/Workspace";
import { FlagDiscoveryView } from "./pages/FlagDiscoveryView";
import { StegoView } from "./pages/StegoView";
import { CryptoView } from "./pages/CryptoView";
import { ForensicsView } from "./pages/ForensicsView";
import { WebView } from "./pages/WebView";
import { ReView } from "./pages/ReView";
import { OsintView } from "./pages/OsintView";
import { ToolManager } from "./pages/ToolManager";
import { Reports } from "./pages/Reports";
import { SettingsView } from "./pages/SettingsView";
import { CommandPalette } from "./components/CommandPalette";
import { api, ChallengeItem } from "./api/client";

export function App() {
  const [activeView, setActiveView] = useState<string>("dashboard");
  const [selectedChallengeId, setSelectedChallengeId] = useState<string | undefined>(undefined);
  const [challenges, setChallenges] = useState<ChallengeItem[]>([]);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState<boolean>(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);

  const refreshChallenges = () => {
    api.listChallenges().then((list) => {
      setChallenges(list);
      if (list.length > 0 && !selectedChallengeId) {
        setSelectedChallengeId(list[0].id);
      }
    });
  };

  useEffect(() => {
    refreshChallenges();
  }, []);

  useEffect(() => {
    let lastKey = "";
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setCommandPaletteOpen((prev) => !prev);
      } else if (e.key === "/" && document.activeElement?.tagName !== "INPUT" && document.activeElement?.tagName !== "TEXTAREA") {
        e.preventDefault();
        setCommandPaletteOpen(true);
      } else if (lastKey === "g") {
        if (e.key === "h") {
          setActiveView("workspace");
        } else if (e.key === "e") {
          setActiveView("workspace");
        } else if (e.key === "r") {
          setActiveView("reports");
        }
      }
      lastKey = e.key;
      setTimeout(() => { lastKey = ""; }, 1000);
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: Terminal },
    { id: "new-challenge", label: "New Challenge", icon: Plus },
    { id: "workspace", label: "3-Panel Workspace", icon: Layers },
    { id: "flags", label: "Flag Discovery", icon: Flag },
    { id: "stego", label: "Steganography", icon: ImageIcon },
    { id: "crypto", label: "Cryptography", icon: KeyRound },
    { id: "forensics", label: "Network Forensics", icon: Network },
    { id: "web", label: "Web Analysis", icon: Globe },
    { id: "re", label: "Reverse Engineering", icon: Cpu },
    { id: "osint", label: "OSINT Coordinates", icon: Compass },
    { id: "tools", label: "Tool Inventory", icon: Wrench },
    { id: "reports", label: "Reports & Writeup", icon: FileText },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-ctf-bg text-[#F8FAFC] overflow-hidden font-sans">
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        onNavigate={(view) => setActiveView(view)}
      />

      {/* Sidebar Navigation */}
      <aside className="hidden md:flex flex-col w-64 bg-[#0A0E18] border-r border-ctf-border select-none">
        <div className="p-4 border-b border-ctf-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-ctf-cyan animate-pulse"></span>
            <span className="font-mono font-bold text-sm tracking-wider text-ctf-cyan">CTF HUNTER X</span>
          </div>
          <span className="text-[10px] font-mono px-1.5 py-0.5 bg-slate-800 text-slate-400 rounded">v1.0</span>
        </div>

        {/* Challenge Switcher */}
        <div className="p-3 border-b border-ctf-border font-mono text-xs">
          <label className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block mb-1">
            Active Target
          </label>
          <select
            value={selectedChallengeId || ""}
            onChange={(e) => setSelectedChallengeId(e.target.value)}
            className="w-full p-1.5 bg-ctf-surface border border-ctf-border rounded text-cyan-300 focus:outline-none focus:border-ctf-cyan text-xs"
          >
            {challenges.length === 0 ? (
              <option value="">No Active Challenges</option>
            ) : (
              challenges.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.title}
                </option>
              ))
            )}
          </select>
        </div>

        {/* Nav Links */}
        <nav className="flex-1 overflow-y-auto p-2 space-y-0.5 font-mono text-xs">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = activeView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id)}
                className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-colors ${
                  active
                    ? "bg-slate-800 text-ctf-cyan font-semibold border-l-2 border-ctf-cyan"
                    : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
                }`}
              >
                <Icon className={`w-4 h-4 ${active ? "text-ctf-cyan" : "text-slate-500"}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer info & shortcut reminder */}
        <div className="p-3 border-t border-ctf-border text-[11px] font-mono text-slate-500 flex items-center justify-between">
          <span>Ctrl+K / for palette</span>
          <span className="text-emerald-400 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Online
          </span>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Top Navbar */}
        <header className="h-12 border-b border-ctf-border bg-[#0B0F1A] px-4 flex items-center justify-between font-mono text-xs">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-1 text-slate-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <span className="text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
              {navItems.find((n) => n.id === activeView)?.label || "Workstation"}
            </span>
          </div>

          <button
            onClick={() => setCommandPaletteOpen(true)}
            className="flex items-center gap-2 px-3 py-1 bg-[#121829] border border-ctf-border rounded text-slate-400 hover:text-white hover:border-ctf-cyan transition-colors"
          >
            <Search className="w-3.5 h-3.5" />
            <span>Search or command...</span>
            <kbd className="px-1 bg-slate-800 border border-slate-700 rounded text-[10px]">Ctrl+K</kbd>
          </button>
        </header>

        {/* Active Page View */}
        <div className="flex-1 overflow-auto bg-[#0B0F1A]">
          {activeView === "dashboard" && (
            <Dashboard
              onNavigate={(view, cId) => {
                setActiveView(view);
                if (cId) setSelectedChallengeId(cId);
              }}
            />
          )}

          {activeView === "new-challenge" && (
            <NewChallenge
              onChallengeCreated={(newId) => {
                refreshChallenges();
                setSelectedChallengeId(newId);
                setActiveView("workspace");
              }}
            />
          )}

          {activeView === "workspace" && (
            <Workspace challengeId={selectedChallengeId} />
          )}

          {activeView === "flags" && <FlagDiscoveryView />}
          {activeView === "stego" && <StegoView />}
          {activeView === "crypto" && <CryptoView />}
          {activeView === "forensics" && <ForensicsView />}
          {activeView === "web" && <WebView />}
          {activeView === "re" && <ReView />}
          {activeView === "osint" && <OsintView />}
          {activeView === "tools" && <ToolManager />}
          {activeView === "reports" && <Reports />}
          {activeView === "settings" && <SettingsView />}
        </div>
      </main>
    </div>
  );
}

export default App;
