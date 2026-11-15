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
  X,
  Sun,
  Moon
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
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    return (localStorage.getItem("ctfx-theme") as "dark" | "light") || "dark";
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "light") {
      root.classList.add("light");
      root.classList.remove("dark");
    } else {
      root.classList.add("dark");
      root.classList.remove("light");
    }
    localStorage.setItem("ctfx-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

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

  const navGroups = [
    {
      label: "Core Operations",
      items: [
        { id: "dashboard", label: "Dashboard", icon: Terminal, badge: "Home" },
        { id: "new-challenge", label: "New Challenge", icon: Plus, badge: "+" },
        { id: "workspace", label: "3-Panel Workspace", icon: Layers, badge: "HUD" },
      ]
    },
    {
      label: "Forensic Analyzers",
      items: [
        { id: "flags", label: "Flag Discovery", icon: Flag, badge: "Core" },
        { id: "stego", label: "Steganography", icon: ImageIcon },
        { id: "crypto", label: "Cryptography", icon: KeyRound },
        { id: "forensics", label: "Network Forensics", icon: Network },
        { id: "web", label: "Web Analysis", icon: Globe },
        { id: "re", label: "Reverse Engineering", icon: Cpu },
        { id: "osint", label: "OSINT Coordinates", icon: Compass },
      ]
    },
    {
      label: "Intel & System",
      items: [
        { id: "tools", label: "Tool Inventory", icon: Wrench },
        { id: "reports", label: "Reports & Writeup", icon: FileText },
        { id: "settings", label: "Settings", icon: Settings },
      ]
    }
  ];

  const allNavItems = navGroups.flatMap(g => g.items);

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

        {/* Nav Links Grouped */}
        <nav className="flex-1 overflow-y-auto p-2.5 space-y-4 font-mono text-xs">
          {navGroups.map((group) => (
            <div key={group.label} className="space-y-1">
              <div className="px-2 py-1 text-[10px] font-bold text-slate-500 uppercase tracking-wider flex items-center justify-between">
                <span>{group.label}</span>
                <span className="text-[9px] text-slate-600">{group.items.length}</span>
              </div>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const active = activeView === item.id;
                  return (
                    <button
                      key={item.id}
                      onClick={() => setActiveView(item.id)}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-all duration-150 ${
                        active
                          ? "bg-slate-800 text-ctf-cyan font-semibold border-l-2 border-ctf-cyan shadow-sm"
                          : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon className={`w-4 h-4 ${active ? "text-ctf-cyan" : "text-slate-500"}`} />
                        <span>{item.label}</span>
                      </div>
                      {item.badge && (
                        <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded ${
                          active ? "bg-cyan-950 text-cyan-300 border border-cyan-800/60" : "bg-slate-800/60 text-slate-500"
                        }`}>
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer info & shortcut reminder */}
        <div className="p-3 border-t border-ctf-border text-[11px] font-mono text-slate-500 flex items-center justify-between bg-black/20">
          <span className="flex items-center gap-1.5">
            <kbd className="px-1 py-0.5 bg-slate-800 border border-slate-700 rounded text-[9px] text-slate-400">Ctrl+K</kbd>
            <span>palette</span>
          </span>
          <span className="text-emerald-400 flex items-center gap-1 font-semibold text-[10px]">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> READY
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
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                {allNavItems.find((n) => n.id === activeView)?.label || "Workstation"}
              </span>
              <span className="hidden lg:inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-950/60 border border-emerald-800/50 text-[10px] text-emerald-400 font-mono">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                <span>ZERO-SIMULATION CORE</span>
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              title={theme === "light" ? "Switch to Dark Mode" : "Switch to Light Mode"}
              className="flex items-center gap-1.5 px-2.5 py-1 bg-[#121829] border border-ctf-border rounded text-slate-300 hover:text-white hover:border-ctf-cyan transition-colors"
            >
              {theme === "light" ? (
                <>
                  <Moon className="w-3.5 h-3.5 text-indigo-500" />
                  <span className="text-[11px] font-medium hidden sm:inline">Dark</span>
                </>
              ) : (
                <>
                  <Sun className="w-3.5 h-3.5 text-amber-400" />
                  <span className="text-[11px] font-medium hidden sm:inline">Light</span>
                </>
              )}
            </button>

            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="flex items-center gap-2 px-3 py-1 bg-[#121829] border border-ctf-border rounded text-slate-400 hover:text-white hover:border-ctf-cyan transition-colors"
            >
              <Search className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Search or command...</span>
              <kbd className="px-1 bg-slate-800 border border-slate-700 rounded text-[10px]">Ctrl+K</kbd>
            </button>
          </div>
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
