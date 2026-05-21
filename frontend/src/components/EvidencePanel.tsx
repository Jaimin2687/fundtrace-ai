'use client';

import { useEffect, useState } from 'react';
import { EvidencePackage, fetchEvidence } from '@/lib/api';
import { X, Download, AlertTriangle } from 'lucide-react';

interface EvidencePanelProps {
  txId: string | null;
  onClose: () => void;
}

export default function EvidencePanel({ txId, onClose }: EvidencePanelProps) {
  const [evidence, setEvidence] = useState<EvidencePackage | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const activeEvidence = evidence && evidence.txId === txId ? evidence : null;

  useEffect(() => {
    if (!txId) return;

    const loadEvidence = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const data = await fetchEvidence(txId);
        setEvidence(data);
      } catch (err) {
        console.error('Failed to fetch evidence:', err);
        setError(err instanceof Error ? err.message : 'Failed to load evidence');
      } finally {
        setLoading(false);
      }
    };

    loadEvidence();
  }, [txId]);

  const downloadJSON = () => {
    if (!activeEvidence) return;

    const dataStr = JSON.stringify(activeEvidence, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `evidence-${activeEvidence.txId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleClose = () => {
    setEvidence(null);
    setError(null);
    onClose();
  };

  const getRiskColor = (score: number) => {
    if (score > 0.85) return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (score > 0.7) return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
    return 'bg-green-500/20 text-green-400 border-green-500/30';
  };

  if (!txId) return null;

  return (
    <div
      className={`fixed right-0 top-0 h-full w-96 bg-[#0b1220] border-l border-white/10 shadow-2xl transform transition-transform duration-300 ease-in-out z-50 ${
        txId ? 'translate-x-0' : 'translate-x-full'
      }`}
    >
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between">
        <div>
          <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
            Investigation sidebar
          </div>
          <h2 className="mt-1 text-lg font-semibold text-slate-100">Evidence Package</h2>
        </div>
        <button
          onClick={handleClose}
          className="p-1 hover:bg-white/10 rounded transition-colors"
        >
          <X className="w-5 h-5 text-slate-400" />
        </button>
      </div>

      {/* Content */}
      <div className="h-[calc(100%-4rem)] overflow-y-auto p-4">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-400" />
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-sm font-medium text-red-400 mb-1">Error</div>
                <div className="text-xs text-red-300">{error}</div>
              </div>
            </div>
          </div>
        )}

        {activeEvidence && !loading && (
          <div className="space-y-4">
            {/* Transaction ID */}
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Transaction ID</label>
              <div className="bg-[#0f172a] rounded p-2 font-mono text-sm text-slate-200 break-all">
                {activeEvidence.txId}
              </div>
            </div>

            {/* Narrative */}
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Narrative</label>
              <div className="bg-[#0f172a] rounded p-3 text-sm text-slate-300 leading-relaxed">
                {activeEvidence.narrative}
              </div>
            </div>

            {/* Total Amount */}
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Total Amount</label>
              <div className="bg-[#0f172a] rounded p-2 text-lg font-semibold text-slate-200">
                {new Intl.NumberFormat('en-IN', {
                  style: 'currency',
                  currency: 'INR',
                  maximumFractionDigits: 0,
                }).format(activeEvidence.total_amount)}
              </div>
            </div>

            {/* Transaction Chain */}
            <div>
              <label className="text-xs text-slate-500 mb-2 block">Transaction Chain</label>
              <div className="space-y-2">
                {activeEvidence.chain.map((txId, index) => (
                  <div
                    key={index}
                    className="bg-[#0f172a] rounded p-3 border border-white/10"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 rounded-full bg-cyan-400/20 text-cyan-300 text-xs flex items-center justify-center font-semibold">
                          {index + 1}
                        </div>
                        <span className="text-xs font-mono text-slate-400">
                          {txId.slice(0, 12)}...
                        </span>
                      </div>
                      <span
                        className={`text-xs px-2 py-0.5 rounded border ${getRiskColor(
                          activeEvidence.risk_scores[index]
                        )}`}
                      >
                        {(activeEvidence.risk_scores[index] * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="text-xs text-slate-500">
                      Pattern:{' '}
                      <span className="text-slate-400">{activeEvidence.patterns[index]}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Generated At */}
            <div>
              <label className="text-xs text-slate-500 mb-1 block">Generated At</label>
              <div className="bg-[#0f172a] rounded p-2 text-xs text-slate-400">
                {new Date(activeEvidence.generated_at).toLocaleString()}
              </div>
            </div>

            {/* Download Button */}
            <button
              onClick={downloadJSON}
              className="w-full bg-cyan-400 hover:bg-cyan-300 text-slate-950 rounded-lg py-2 px-4 flex items-center justify-center gap-2 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download JSON
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
