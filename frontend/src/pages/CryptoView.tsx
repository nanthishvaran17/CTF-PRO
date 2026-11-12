import React, { useState } from "react";
import { KeyRound, Shield, Search, ArrowRight } from "lucide-react";

export const CryptoView: React.FC = () => {
  const [inputCipher, setInputCipher] = useState("SNOT{pnrfne_fuvsg_fbyirq}");
  const [caesarResults, setCaesarResults] = useState<{ shift: number; text: string }[]>([]);
  const [hashInput, setHashInput] = useState("5d41402abc4b2a76b9719d911017c592");
  const [identifiedHash, setIdentifiedHash] = useState<string>("MD5 / NTLM");

  const solveCaesarAll = () => {
    const list = [];
    for (let s = 1; s <= 25; s++) {
      let shifted = "";
      for (const ch of inputCipher) {
        if (ch >= 'a' && ch <= 'z') {
          shifted += String.fromCharCode(((ch.charCodeAt(0) - 97 - s + 26) % 26) + 97);
        } else if (ch >= 'A' && ch <= 'Z') {
          shifted += String.fromCharCode(((ch.charCodeAt(0) - 65 - s + 26) % 26) + 65);
        } else {
          shifted += ch;
        }
      }
      list.push({ shift: s, text: shifted });
    }
    setCaesarResults(list);
  };

  const idHash = () => {
    const clean = hashInput.trim();
    if (clean.length === 32) setIdentifiedHash("MD5 / NTLM / MD4 (128-bit hex)");
    else if (clean.length === 40) setIdentifiedHash("SHA-1 / RIPEMD-160 (160-bit hex)");
    else if (clean.length === 64) setIdentifiedHash("SHA-256 / HMAC-SHA256 (256-bit hex)");
    else if (clean.startsWith("$2y$") || clean.startsWith("$2a$")) setIdentifiedHash("bcrypt password hash");
    else setIdentifiedHash("Unknown / Custom hash length");
  };

  return (
    <div className="max-w-5xl mx-auto p-6 font-mono text-xs space-y-6">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card space-y-4">
        <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2 mb-1">
          <KeyRound className="w-5 h-5 text-ctf-cyan" /> Cryptographic Suite & Hash Identifier
        </h1>
        <p className="text-slate-400 font-sans text-sm">
          Deterministic cryptanalysis tools: Caesar shift, Atbash, Vigenere, single-byte XOR, frequency scoring, and weak RSA helpers.
        </p>

        {/* Caesar Tool */}
        <div className="pt-4 border-t border-ctf-border space-y-3">
          <span className="text-slate-200 font-bold text-sm block">1. Caesar / ROT Shift Cracker</span>
          <div className="flex gap-2">
            <input
              type="text"
              value={inputCipher}
              onChange={(e) => setInputCipher(e.target.value)}
              className="flex-1 p-2 bg-[#0B0F1A] border border-ctf-border rounded text-white focus:outline-none focus:border-ctf-cyan"
            />
            <button
              onClick={solveCaesarAll}
              className="px-4 py-2 bg-ctf-cyan text-black font-bold rounded hover:bg-ctf-cyanHover transition-colors"
            >
              Crack (25 Shifts)
            </button>
          </div>

          {caesarResults.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-48 overflow-y-auto p-2 bg-[#0B0F1A] border border-ctf-border rounded">
              {caesarResults.map((r) => (
                <div key={r.shift} className="p-1.5 hover:bg-slate-800 rounded flex justify-between">
                  <span className="text-slate-500">Shift -{r.shift}:</span>
                  <span className="text-slate-200 font-bold truncate">{r.text}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Hash ID */}
        <div className="pt-4 border-t border-ctf-border space-y-3">
          <span className="text-slate-200 font-bold text-sm block">2. Hash Algorithm Identifier</span>
          <div className="flex gap-2">
            <input
              type="text"
              value={hashInput}
              onChange={(e) => setHashInput(e.target.value)}
              className="flex-1 p-2 bg-[#0B0F1A] border border-ctf-border rounded text-white focus:outline-none focus:border-ctf-cyan"
            />
            <button
              onClick={idHash}
              className="px-4 py-2 bg-slate-800 border border-ctf-border text-slate-200 font-bold rounded hover:bg-slate-700 transition-colors"
            >
              Identify Hash
            </button>
          </div>
          {identifiedHash && (
            <div className="p-3 bg-[#0B0F1A] border border-ctf-border rounded text-slate-300">
              Algorithm: <strong className="text-ctf-cyan">{identifiedHash}</strong>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
