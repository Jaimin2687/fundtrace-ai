"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { Download, AlertTriangle, FileText, ShieldCheck } from "lucide-react";
import { EvidencePackage, fetchEvidence, API_BASE, API_KEY } from "@/lib/api";

interface EnhancedEvidencePanelProps {
  txId: string | null;
  onClose: () => void;
}

export default function EnhancedEvidencePanel({ txId, onClose }: EnhancedEvidencePanelProps) {
  const [evidence, setEvidence] = useState<EvidencePackage | null>(null);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const activeEvidence = evidence && evidence.txId === txId ? evidence : null;
  const riskScores = activeEvidence?.risk_scores ?? [];
  const maxRisk = riskScores.length ? Math.max(...riskScores) : 0;

  useEffect(() => {
    if (!txId) return;

    const loadEvidence = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await fetchEvidence(txId);
        setEvidence(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load evidence");
      } finally {
        setLoading(false);
      }
    };

    loadEvidence();
  }, [txId]);

  const downloadJSON = () => {
    if (!activeEvidence) return;
    const dataStr = JSON.stringify(activeEvidence, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `evidence-${activeEvidence.txId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const downloadFiuReport = async () => {
    if (!txId) return;
    setExporting(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1/export/fiu-ind`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
        },
        body: JSON.stringify({ cluster_id: txId }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate FIU-IND report");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `fiu-ind-${txId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate FIU report");
    } finally {
      setExporting(false);
    }
  };

  const handleClose = () => {
    setEvidence(null);
    setError(null);
    onClose();
  };

  return (
    <AnimatePresence>
      {txId && (
        <motion.aside
          initial={{ x: 360, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 360, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="flex h-full flex-col"
        >
          <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">
            <div>
              <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
                Investigation sidebar
              </div>
              <div className="mt-1 text-lg font-headline font-semibold text-white">
                Case ID: {txId ?? "--"}
              </div>
              <div className="mt-2 inline-flex items-center gap-2 text-[11px] uppercase tracking-[0.3em] text-emerald-200">
                <ShieldCheck className="h-4 w-4" />
                System secure
              </div>
            </div>
            <button
              onClick={handleClose}
              className="rounded-full border border-white/10 px-3 py-1 text-xs uppercase tracking-[0.3em] text-slate-300"
            >
              Close
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-5">
            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-panel rounded-xl p-6 text-center text-sm text-slate-300">
                Loading evidence...
              </motion.div>
            )}

            {error && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-200">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4" />
                  {error}
                </div>
              </div>
            )}

            {activeEvidence && !loading && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ staggerChildren: 0.1 }} className="space-y-5">
                <motion.div className="glass-panel rounded-xl p-4">
                  <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
                    Threat narrative
                  </div>
                  <p className="mt-3 text-sm text-slate-200">
                    {activeEvidence.narrative}
                  </p>
                </motion.div>

                <div className="grid grid-cols-2 gap-4">
                  <motion.div className="glass-panel rounded-xl p-4">
                    <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
                      Total amount
                    </div>
                    <div className="mt-2 text-lg font-semibold text-white">
                      {new Intl.NumberFormat("en-IN", {
                        style: "currency",
                        currency: "INR",
                        maximumFractionDigits: 0,
                      }).format(activeEvidence.total_amount)}
                    </div>
                  </motion.div>
                  <motion.div className="glass-panel rounded-xl p-4">
                    <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
                      Chain length
                    </div>
                    <div className="mt-2 text-lg font-semibold text-white">
                      {activeEvidence.chain.length} hops
                    </div>
                  </motion.div>
                </div>

                <motion.div className="glass-panel rounded-xl p-4">
                  <div className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-slate-400">
                    <FileText className="h-4 w-4" />
                    Evidence locker
                  </div>
                  <div className="mt-4 space-y-3">
                    {activeEvidence.chain.map((tx, index) => (
                      <div
                        key={`${tx}-${index}`}
                        className="rounded-lg border border-white/10 bg-[#0A1222] px-3 py-2 text-xs text-slate-300"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-mono">{tx}</span>
                          <span className="text-cyan-200">
                            {(activeEvidence.risk_scores[index] * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="mt-1 text-[10px] uppercase tracking-[0.3em] text-slate-500">
                          {activeEvidence.patterns[index]}
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>

                <motion.div className="rounded-xl border border-rose-500/30 bg-[rgba(244,63,94,0.1)] p-4 text-sm text-rose-200 shadow-[0_0_20px_rgba(244,63,94,0.15)]">
                  <div className="text-xs uppercase tracking-[0.3em] text-rose-200">
                    Critical pattern detected
                  </div>
                  <ul className="mt-3 space-y-2 text-xs text-rose-100/80">
                    <li>Peak risk score {(maxRisk * 100).toFixed(1)}%</li>
                    <li>Chain length {activeEvidence.chain.length} hops</li>
                    <li>
                      Primary pattern {activeEvidence.patterns[0] ?? "Unknown"}
                    </li>
                  </ul>
                </motion.div>
              </motion.div>
            )}
          </div>

          <div className="border-t border-white/10 px-6 py-4">
            <button
              onClick={downloadJSON}
              className="group flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-3 text-sm font-semibold text-slate-950 transition-all hover:bg-cyan-300 hover:shadow-[0_0_20px_rgba(34,211,238,0.5)]"
              disabled={!activeEvidence}
            >
              <Download className="h-4 w-4 transition group-hover:-translate-y-0.5" />
              Download Evidence JSON
            </button>
            <button
              className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl border border-rose-400/40 bg-[rgba(244,63,94,0.1)] px-4 py-3 text-sm font-semibold text-rose-200 transition-all hover:bg-[rgba(244,63,94,0.2)] hover:shadow-[0_0_15px_rgba(244,63,94,0.3)] disabled:opacity-60"
              type="button"
              onClick={downloadFiuReport}
              disabled={!activeEvidence || exporting}
            >
              {exporting ? "Generating FIU report..." : "Generate FIU-IND report"}
            </button>
          </div>
        </motion.aside>
      )}
    </AnimatePresence>
  );
}
