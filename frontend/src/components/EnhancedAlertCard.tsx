"use client";

import { motion } from "framer-motion";
import { AlertEvent } from "@/lib/api";
import { formatDistanceToNow } from "date-fns";

interface EnhancedAlertCardProps {
  alert: AlertEvent;
  onSelect: (txId: string) => void;
}

const patternColors: Record<string, string> = {
  Structuring: "bg-red-500/15 text-red-300 border-red-500/30",
  Smurfing: "bg-red-500/15 text-red-300 border-red-500/30",
  Layering: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  "Layering - Cash Out": "bg-amber-500/15 text-amber-300 border-amber-500/30",
  "Dormant Account Activated": "bg-purple-500/15 text-purple-300 border-purple-500/30",
  "Round-tripping": "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
  "Round-Tripping": "bg-cyan-500/15 text-cyan-300 border-cyan-500/30",
  Normal: "bg-slate-500/15 text-slate-300 border-slate-500/30",
};

export default function EnhancedAlertCard({ alert, onSelect }: EnhancedAlertCardProps) {
  const risk = Math.min(alert.risk_score, 1);
  const riskColor =
    risk >= 0.85 ? "bg-red-500" : risk >= 0.7 ? "bg-amber-500" : "bg-emerald-500";

  const patternColor = patternColors[alert.pattern] || patternColors.Normal;
  const timeAgo = formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true });

  return (
    <motion.button
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => onSelect(alert.txId)}
      className="w-full rounded-2xl border border-white/10 glass-panel p-4 text-left shadow-[0_0_20px_rgba(15,23,42,0.35)] transition-all hover:border-cyan-400/40 hover:shadow-[0_0_25px_rgba(34,211,238,0.15)]"
    >
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span className={`rounded-full border px-2 py-1 ${patternColor}`}>
          {alert.pattern}
        </span>
        <span>{timeAgo}</span>
      </div>

      <div className="mt-3 text-sm text-white">
        <div className="text-xs uppercase tracking-[0.3em] text-slate-500">Transaction</div>
        <div className="mt-1 font-mono text-sm text-slate-200">
          {alert.txId.slice(0, 14)}...
        </div>
      </div>

      {alert.amount !== undefined && (
        <div className="mt-3 text-sm text-slate-200">
          {new Intl.NumberFormat("en-IN", {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0,
          }).format(alert.amount)}
        </div>
      )}

      <div className="mt-4">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>Risk score</span>
          <span className="text-slate-300">{(risk * 100).toFixed(1)}%</span>
        </div>
        <div className="mt-2 h-2 w-full rounded-full bg-slate-800">
          <div className={`h-2 rounded-full ${riskColor}`} style={{ width: `${risk * 100}%` }} />
        </div>
      </div>
    </motion.button>
  );
}
