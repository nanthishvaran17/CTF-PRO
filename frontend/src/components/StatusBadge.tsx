import React from "react";
import { 
  Eye, 
  HelpCircle, 
  CheckCircle2, 
  Clock, 
  ShieldCheck, 
  XCircle, 
  AlertTriangle 
} from "lucide-react";

interface StatusBadgeProps {
  status: string;
  size?: "sm" | "md";
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = "md" }) => {
  const norm = status.toUpperCase();

  let bg = "bg-slate-800/80 text-slate-300 border-slate-700";
  let Icon = Eye;
  let text = "DISCOVERED";

  switch (norm) {
    case "DISCOVERED":
      bg = "bg-slate-800/90 text-slate-300 border-slate-600";
      Icon = Eye;
      text = "DISCOVERED";
      break;
    case "CANDIDATE":
      bg = "bg-sky-950/80 text-sky-400 border-sky-800";
      Icon = HelpCircle;
      text = "CANDIDATE";
      break;
    case "EVIDENCE-SUPPORTED":
      bg = "bg-teal-950/80 text-teal-300 border-teal-800";
      Icon = CheckCircle2;
      text = "EVIDENCE-SUPPORTED";
      break;
    case "VALIDATION-PENDING":
      bg = "bg-amber-950/80 text-amber-300 border-amber-800";
      Icon = Clock;
      text = "VALIDATION-PENDING";
      break;
    case "VERIFIED-BY-CHALLENGE":
    case "VERIFIED":
      bg = "bg-emerald-950/90 text-emerald-300 border-emerald-700 shadow-sm shadow-emerald-900/50";
      Icon = ShieldCheck;
      text = "VERIFIED-BY-CHALLENGE";
      break;
    case "REJECTED":
      bg = "bg-rose-950/80 text-rose-300 border-rose-800";
      Icon = XCircle;
      text = "REJECTED";
      break;
    case "UNRESOLVED":
      bg = "bg-purple-950/80 text-purple-300 border-purple-800";
      Icon = AlertTriangle;
      text = "UNRESOLVED";
      break;
  }

  const padding = size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-xs";

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-medium border rounded-md font-mono ${padding} ${bg}`}
      title={`Candidate Status: ${text}`}
    >
      <Icon className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} />
      <span>{text}</span>
    </span>
  );
};
