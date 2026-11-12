import React, { useState } from "react";
import { api } from "../api/client";
import { UploadCloud, FileCode, CheckCircle, ArrowRight, AlertCircle, Plus } from "lucide-react";

interface NewChallengeProps {
  onChallengeCreated: (challengeId: string) => void;
}

export const NewChallenge: React.FC<NewChallengeProps> = ({ onChallengeCreated }) => {
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("Forensics");
  const [description, setDescription] = useState("");
  const [flagFormat, setFlagFormat] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      setError("Challenge title is required.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const challenge = await api.createChallenge({
        title,
        category,
        description,
        flag_format: flagFormat ? flagFormat : undefined,
      });

      if (files.length > 0) {
        await api.uploadFiles(challenge.id, files);
      }

      onChallengeCreated(challenge.id);
    } catch (err: any) {
      setError(err?.message || "Failed to create challenge.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 font-mono text-xs">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card space-y-6">
        <div>
          <h2 className="text-lg font-bold text-ctf-cyan flex items-center gap-2">
            <Plus className="w-5 h-5 text-ctf-cyan" /> Register Target CTF Challenge
          </h2>
          <p className="text-slate-400 mt-1 font-sans">
            Configure challenge metadata and upload suspect target files for safe intake.
          </p>
        </div>

        {error && (
          <div className="p-3 bg-rose-950/80 border border-rose-800 text-rose-300 rounded flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Challenge Title *</label>
            <input
              type="text"
              required
              placeholder="e.g. Hidden Transmission 2026"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-2.5 bg-[#0B0F1A] border border-ctf-border rounded text-white placeholder-slate-600 focus:outline-none focus:border-ctf-cyan"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full p-2.5 bg-[#0B0F1A] border border-ctf-border rounded text-white focus:outline-none focus:border-ctf-cyan"
              >
                <option value="Forensics">Forensics (PCAP, Logs)</option>
                <option value="Steganography">Steganography (Images, Audio)</option>
                <option value="Cryptography">Cryptography (Ciphers, RSA)</option>
                <option value="Reverse Engineering">Reverse Engineering (ELF, PE)</option>
                <option value="Web">Web Exploitation (Client, HTTP)</option>
                <option value="OSINT">OSINT (Metadata, Coordinates)</option>
                <option value="Misc">Miscellaneous / Archive</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">Flag Format Regex (Optional)</label>
              <input
                type="text"
                placeholder="e.g. ctf\{[A-Za-z0-9_]+\}"
                value={flagFormat}
                onChange={(e) => setFlagFormat(e.target.value)}
                className="w-full p-2.5 bg-[#0B0F1A] border border-ctf-border rounded text-white placeholder-slate-600 focus:outline-none focus:border-ctf-cyan"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Challenge Description / Clues</label>
            <textarea
              rows={4}
              placeholder="Paste challenge prompt, organizer hints, or server port details..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2.5 bg-[#0B0F1A] border border-ctf-border rounded text-white placeholder-slate-600 focus:outline-none focus:border-ctf-cyan"
            />
          </div>

          {/* Drag & Drop File Intake Area */}
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Target Files (Read-Only Intake)</label>
            <div className="border-2 border-dashed border-ctf-border hover:border-ctf-cyan rounded-card p-6 text-center cursor-pointer transition-colors bg-[#0B0F1A]">
              <input
                type="file"
                multiple
                id="file-upload"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="file-upload" className="cursor-pointer block">
                <UploadCloud className="w-8 h-8 mx-auto text-ctf-cyan mb-2 opacity-80" />
                <span className="text-slate-300 font-semibold block">Click to select files or drag & drop</span>
                <span className="text-slate-500 text-[11px] block mt-1">
                  Supports PCAP, PNG, JPEG, ELF, PE, ZIP, WAV, TXT, PDF & raw binary
                </span>
              </label>
            </div>

            {files.length > 0 && (
              <div className="mt-3 space-y-1.5">
                <span className="text-slate-400 font-semibold text-[11px]">Selected files ({files.length}):</span>
                {files.map((f, i) => (
                  <div key={i} className="flex items-center justify-between p-2 bg-[#0B0F1A] border border-ctf-border rounded">
                    <span className="text-slate-200 flex items-center gap-1.5 truncate">
                      <FileCode className="w-3.5 h-3.5 text-cyan-400" /> {f.name}
                    </span>
                    <span className="text-slate-500 text-[11px]">{(f.size / 1024).toFixed(1)} KB</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-ctf-border flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2.5 bg-ctf-cyan hover:bg-ctf-cyanHover disabled:opacity-50 text-black font-bold rounded transition-colors shadow-lg"
            >
              <span>{loading ? "Ingesting..." : "Create & Launch Workspace"}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
