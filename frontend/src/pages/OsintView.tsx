import React, { useState } from "react";
import { Compass, MapPin, Camera, ExternalLink } from "lucide-react";

export const OsintView: React.FC = () => {
  const [degLat, setDegLat] = useState("37");
  const [minLat, setMinLat] = useState("46");
  const [secLat, setSecLat] = useState("29.74");
  const [refLat, setRefLat] = useState("N");

  const [degLon, setDegLon] = useState("122");
  const [minLon, setMinLon] = useState("25");
  const [secLon, setSecLon] = useState("09.84");
  const [refLon, setRefLon] = useState("W");

  const [decimalCoords, setDecimalCoords] = useState<{ lat: number; lon: number } | null>(null);

  const convertDMS = () => {
    let lat = parseFloat(degLat) + parseFloat(minLat) / 60.0 + parseFloat(secLat) / 3600.0;
    if (refLat === "S") lat = -lat;

    let lon = parseFloat(degLon) + parseFloat(minLon) / 60.0 + parseFloat(secLon) / 3600.0;
    if (refLon === "W") lon = -lon;

    setDecimalCoords({ lat: parseFloat(lat.toFixed(6)), lon: parseFloat(lon.toFixed(6)) });
  };

  return (
    <div className="max-w-5xl mx-auto p-6 font-mono text-xs space-y-6">
      <div className="p-6 bg-ctf-surface border border-ctf-border rounded-card space-y-4">
        <h1 className="text-xl font-bold text-ctf-cyan flex items-center gap-2 mb-1">
          <Compass className="w-5 h-5 text-ctf-cyan" /> OSINT & Geolocation Coordinate Calculator
        </h1>
        <p className="text-slate-400 font-sans text-sm">
          Extract camera EXIF hardware, timestamps, and convert Degree-Minute-Second GPS tuples to clickable satellite coordinates.
        </p>

        {/* GPS DMS Calculator */}
        <div className="pt-4 border-t border-ctf-border space-y-4">
          <span className="text-slate-200 font-bold text-sm block flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-rose-400" /> GPS DMS to Decimal Degrees Converter
          </span>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Latitude */}
            <div className="p-3 bg-[#0B0F1A] border border-ctf-border rounded space-y-2">
              <span className="text-slate-300 font-semibold block">Latitude (Deg &bull; Min &bull; Sec &bull; Ref)</span>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={degLat}
                  onChange={(e) => setDegLat(e.target.value)}
                  className="w-16 p-1.5 bg-ctf-surface border border-ctf-border rounded text-center text-white"
                  placeholder="Deg"
                />
                <input
                  type="text"
                  value={minLat}
                  onChange={(e) => setMinLat(e.target.value)}
                  className="w-16 p-1.5 bg-ctf-surface border border-ctf-border rounded text-center text-white"
                  placeholder="Min"
                />
                <input
                  type="text"
                  value={secLat}
                  onChange={(e) => setSecLat(e.target.value)}
                  className="w-20 p-1.5 bg-ctf-surface border border-ctf-border rounded text-center text-white"
                  placeholder="Sec"
                />
                <select
                  value={refLat}
                  onChange={(e) => setRefLat(e.target.value)}
                  className="p-1.5 bg-ctf-surface border border-ctf-border rounded text-white"
                >
                  <option value="N">N</option>
                  <option value="S">S</option>
                </select>
              </div>
            </div>

            {/* Longitude */}
            <div className="p-3 bg-[#0B0F1A] border border-ctf-border rounded space-y-2">
              <span className="text-slate-300 font-semibold block">Longitude (Deg &bull; Min &bull; Sec &bull; Ref)</span>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={degLon}
                  onChange={(e) => setDegLon(e.target.value)}
                  className="w-16 p-1.5 bg-ctf-surface border border-ctf-border rounded text-center text-white"
                  placeholder="Deg"
                />
                <input
                  type="text"
                  value={minLon}
                  onChange={(e) => setMinLon(e.target.value)}
                  className="w-16 p-1.5 bg-ctf-surface border border-ctf-border rounded text-center text-white"
                  placeholder="Min"
                />
                <input
                  type="text"
                  value={secLon}
                  onChange={(e) => setSecLon(e.target.value)}
                  className="w-20 p-1.5 bg-ctf-surface border border-ctf-border rounded text-center text-white"
                  placeholder="Sec"
                />
                <select
                  value={refLon}
                  onChange={(e) => setRefLon(e.target.value)}
                  className="p-1.5 bg-ctf-surface border border-ctf-border rounded text-white"
                >
                  <option value="E">E</option>
                  <option value="W">W</option>
                </select>
              </div>
            </div>
          </div>

          <button
            onClick={convertDMS}
            className="px-4 py-2 bg-ctf-cyan text-black font-bold rounded hover:bg-ctf-cyanHover transition-colors"
          >
            Calculate Coordinates
          </button>

          {decimalCoords && (
            <div className="p-4 bg-emerald-950/20 border border-emerald-800/40 rounded space-y-2">
              <div className="text-slate-200">
                Decimal Degrees: <strong className="text-emerald-400">{decimalCoords.lat}, {decimalCoords.lon}</strong>
              </div>
              <div className="flex items-center gap-3">
                <a
                  href={`https://www.google.com/maps?q=${decimalCoords.lat},${decimalCoords.lon}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:underline flex items-center gap-1"
                >
                  Open in Google Maps <ExternalLink className="w-3.5 h-3.5" />
                </a>
                <a
                  href={`https://www.openstreetmap.org/?mlat=${decimalCoords.lat}&mlon=${decimalCoords.lon}#map=16/${decimalCoords.lat}/${decimalCoords.lon}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:underline flex items-center gap-1"
                >
                  Open in OpenStreetMap <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
