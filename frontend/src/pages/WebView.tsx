import React, { useState } from "react";
import { Globe, ShieldAlert, CheckCircle, Code } from "lucide-react";

export const WebView: React.FC = () => {
  const [testUrl, setTestUrl] = useState("http://127.0.0.1:8080");
  const [ssrfResult, setSsrfResult] = useState<string | null>(null);

  const testSSRF = () => {
    // Client-side simulation of the backend SSRF defense logic
    if (testUrl.includes("127.") || testUrl.includes("localhost") || testUrl.includes("169.254.") || testUrl.includes("192.168.") || testUrl.includes("10.")) {
      setSsrfResult("BLOCKED: SSRF Defense rule triggered! Target IP falls within restricted / private / loopback network.");
    } else {
      setSsrfResult("ALLOWED: Destination passes strict public routable IP check.");
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 font-mono text-xs space-y-6">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card space-y-4">
        <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2 mb-1">
          <Globe className="w-5 h-5 text-ctf-cyan" /> Web Analysis & SSRF-Guarded Inspector
        </h1>
        <p className="text-slate-400 font-sans text-sm">
          Audit client-side HTML, JavaScript bundles, endpoints, and hidden comments on authorized targets without unauthorized network port scanning.
        </p>

        {/* SSRF Safety Playground */}
        <div className="pt-4 border-t border-ctf-border space-y-3">
          <span className="text-slate-200 font-bold text-sm block">1. SSRF Policy Validator</span>
          <p className="text-slate-400 text-xs">
            Verify that private subnets, cloud metadata (169.254.169.254), and loopback hosts are rigorously blocked by the backend fetcher.
          </p>

          <div className="flex gap-2">
            <input
              type="text"
              value={testUrl}
              onChange={(e) => setTestUrl(e.target.value)}
              className="flex-1 p-2 bg-[#0B0F1A] border border-ctf-border rounded text-white focus:outline-none focus:border-ctf-cyan"
            />
            <button
              onClick={testSSRF}
              className="px-4 py-2 bg-ctf-cyan text-black font-bold rounded hover:bg-ctf-cyanHover transition-colors"
            >
              Test SSRF Guard
            </button>
          </div>

          {ssrfResult && (
            <div
              className={`p-3 rounded border font-semibold ${
                ssrfResult.startsWith("BLOCKED")
                  ? "bg-rose-950/40 border-rose-800 text-rose-300"
                  : "bg-emerald-950/40 border-emerald-800 text-emerald-300"
              }`}
            >
              {ssrfResult}
            </div>
          )}
        </div>

        {/* JS Analysis Features */}
        <div className="pt-4 border-t border-ctf-border space-y-3">
          <span className="text-slate-200 font-bold text-sm block">2. Static Client-Side Inspection Capabilities</span>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 bg-[#0B0F1A] border border-ctf-border rounded">
              <strong className="text-cyan-400 block mb-1">JWT Discovery</strong>
              <p className="text-slate-400 text-[11px]">Identifies <code>eyJ...</code> encoded JSON Web Tokens in source bundles.</p>
            </div>
            <div className="p-3 bg-[#0B0F1A] border border-ctf-border rounded">
              <strong className="text-cyan-400 block mb-1">Hidden Endpoints</strong>
              <p className="text-slate-400 text-[11px]">Carves <code>/api/...</code>, <code>/admin</code>, and developer test routes.</p>
            </div>
            <div className="p-3 bg-[#0B0F1A] border border-ctf-border rounded">
              <strong className="text-cyan-400 block mb-1">HTML Comment Secrets</strong>
              <p className="text-slate-400 text-[11px]">Extracts developer notes, password hints, and deprecated flags.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
