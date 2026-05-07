'use client';

import { AlertEvent } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

interface AlertCardProps {
  alert: AlertEvent;
  onSelect: (txId: string) => void;
}

const patternColors: Record<string, string> = {
  'Structuring': 'bg-red-500/20 text-red-400 border-red-500/30',
  'Smurfing': 'bg-red-500/20 text-red-400 border-red-500/30',
  'Layering': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  'Layering - Cash Out': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  'Dormant Account Activated': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  'Round-tripping': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  'Suspicious Transfer': 'bg-gray-500/20 text-gray-400 border-gray-500/30',
};

export default function AlertCard({ alert, onSelect }: AlertCardProps) {
  const patternColor = patternColors[alert.pattern] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  
  // Risk score color
  const riskColor = alert.risk_score > 0.85 
    ? 'bg-red-500' 
    : alert.risk_score > 0.7 
    ? 'bg-orange-500' 
    : 'bg-green-500';

  // Format timestamp
  const timeAgo = formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true });

  // Truncate txId
  const truncatedTxId = alert.txId.length > 12 
    ? `${alert.txId.slice(0, 12)}...` 
    : alert.txId;

  // Format amount
  const formattedAmount = alert.amount 
    ? new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0,
      }).format(alert.amount)
    : null;

  return (
    <div
      onClick={() => onSelect(alert.txId)}
      className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 cursor-pointer hover:bg-slate-800 hover:border-slate-600 transition-all"
    >
      {/* Header: Pattern badge and risk score */}
      <div className="flex items-center justify-between mb-3">
        <span className={`text-xs px-2 py-1 rounded border ${patternColor} font-medium`}>
          {alert.pattern}
        </span>
        <span className="text-xs text-slate-400">{timeAgo}</span>
      </div>

      {/* Transaction ID */}
      <div className="mb-2">
        <span className="text-xs text-slate-500">Transaction ID</span>
        <p className="text-sm font-mono text-slate-200">{truncatedTxId}</p>
      </div>

      {/* Amount if present */}
      {formattedAmount && (
        <div className="mb-3">
          <span className="text-xs text-slate-500">Amount</span>
          <p className="text-sm font-semibold text-slate-200">{formattedAmount}</p>
        </div>
      )}

      {/* Risk score progress bar */}
      <div>
        <div className="flex items-center justify-between mb-1">
          <span className="text-xs text-slate-500">Risk Score</span>
          <span className="text-xs font-semibold text-slate-200">
            {(alert.risk_score * 100).toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <div
            className={`${riskColor} h-2 rounded-full transition-all`}
            style={{ width: `${alert.risk_score * 100}%` }}
          />
        </div>
      </div>

      {/* Source badge */}
      {alert.source && (
        <div className="mt-2">
          <span className="text-xs px-2 py-0.5 rounded bg-slate-700 text-slate-400">
            {alert.source}
          </span>
        </div>
      )}
    </div>
  );
}
