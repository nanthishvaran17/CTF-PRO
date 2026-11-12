import React, { useState, useEffect } from "react";
import { api, ToolItem } from "../api/client";
import { Wrench, CheckCircle2, XCircle, Terminal, HelpCircle, RefreshCw } from "lucide-react";

export const ToolManager: React.FC = () => {
  const [tools, setTools] = useState<ToolItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchTools = () => {
    setLoading(true);
    api.listTools()
      .then((data) => setTools(data || []))
      .catch((err) => console.error("Error fetching tools", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchTools();
  }, []);

  const installedCount = tools.filter((t) => t.is_installed).length;

  return (
    <div className="max-w-6xl mx-auto p-4 md:p-6 font-mono text-xs space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between p-6 bg-ctf-surface border border-ctf-border rounded-card">
        <div>
          <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2">
            <Wrench className="w-5 h-5 text-ctf-cyan" /> Host Security Tool Inventory
          </h1>
          <p className="text-slate-400 mt-1 font-sans text-sm">
            Real-time status of installed security utilities and decompiler frameworks.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-lg font-bold text-white">
              {installedCount} <span className="text-slate-500 text-sm">/ {tools.length}</span>
            </div>
            <div className="text-[10px] text-slate-400">Tools Available</div>
          </div>
          <button
            onClick={fetchTools}
            disabled={loading}
            className="p-2 bg-[#162036] hover:bg-slate-700 border border-ctf-border text-slate-200 rounded transition-colors"
            title="Refresh Inventory"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </div>

      {/* Tools Table */}
      <div className="bg-ctf-surface border border-ctf-border rounded-card overflow-hidden">
        <div className="divide-y divide-slate-800">
          {tools.map((tool) => (
            <div key={tool.binary} className="p-4 hover:bg-slate-800/40 transition-colors space-y-2">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  {tool.is_installed ? (
                    <span className="p-1.5 bg-emerald-950/80 border border-emerald-700 text-emerald-400 rounded">
                      <CheckCircle2 className="w-4 h-4" />
                    </span>
                  ) : (
                    <span className="p-1.5 bg-slate-800 border border-slate-700 text-slate-400 rounded">
                      <XCircle className="w-4 h-4" />
                    </span>
                  )}
                  <div>
                    <span className="font-bold text-sm text-slate-100">{tool.name}</span>
                    <span className="text-slate-500 ml-2">({tool.binary})</span>
                    <span className="ml-3 px-2 py-0.5 bg-[#0B0F1A] border border-ctf-border text-cyan-400 rounded text-[10px]">
                      {tool.category}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span
                    className={`font-semibold ${
                      tool.is_installed ? "text-emerald-400" : "text-slate-500"
                    }`}
                  >
                    {tool.is_installed ? "INSTALLED" : "UNAVAILABLE"}
                  </span>
                </div>
              </div>

              <div className="text-slate-400 font-sans text-xs">{tool.description}</div>

              {tool.is_installed ? (
                <div className="text-[11px] text-slate-400 bg-[#0B0F1A] p-2 rounded border border-slate-800 font-mono">
                  <strong>Version:</strong> {tool.version} &bull; <strong>Path:</strong> {tool.executable_path}
                </div>
              ) : (
                <div className="text-[11px] text-slate-400 bg-amber-950/20 border border-amber-900/40 p-2 rounded">
                  <span className="text-amber-400 font-semibold block mb-0.5">Installation Guidance:</span>
                  <code>{tool.install_guidance}</code>
                  <span className="text-slate-500 block mt-1 text-[10px]">
                    (Python fallback active: native functionality remains operational)
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
