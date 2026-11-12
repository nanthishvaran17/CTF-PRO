import React from "react";
import { Image as ImageIcon, Eye, Split, Hash } from "lucide-react";

export const StegoView: React.FC = () => {
  return (
    <div className="max-w-5xl mx-auto p-6 font-mono text-xs space-y-6">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card">
        <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2 mb-1">
          <ImageIcon className="w-5 h-5 text-ctf-cyan" /> Steganography Inspector
        </h1>
        <p className="text-slate-400 font-sans text-sm">
          Analyze PNG structural chunks, extract LSB (Least Significant Bit) channels across RGB and Alpha planes, compute visual entropy, and detect appended trailing bytes.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded-lg space-y-1">
            <span className="text-ctf-cyan font-bold block">PNG Chunk Parser</span>
            <p className="text-slate-400 text-[11px]">Inspects IHDR, IDAT, PLTE, custom chunks, and checks valid IEND CRC termination.</p>
          </div>
          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded-lg space-y-1">
            <span className="text-ctf-cyan font-bold block">LSB Bit-Plane Extractor</span>
            <p className="text-slate-400 text-[11px]">Carves bit planes 0-7 individually from Red, Green, Blue, and combined interleaved streams.</p>
          </div>
          <div className="p-4 bg-[#0B0F1A] border border-ctf-border rounded-lg space-y-1">
            <span className="text-ctf-cyan font-bold block">Visual Diff & Compare</span>
            <p className="text-slate-400 text-[11px]">Computes exact pixel differences and percentage variances between suspect and reference images.</p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-cyan-950/20 border border-cyan-800/40 rounded text-cyan-300">
          <strong>Workstation Tip:</strong> To run stego analysis on an uploaded image, navigate to the 3-panel workspace and click <em>Run Analysis</em>. Detected flags appear in the candidates panel with exact bit offsets.
        </div>
      </div>
    </div>
  );
};
