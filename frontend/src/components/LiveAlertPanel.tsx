'use client';

import { useRef } from 'react';
import { useAlerts } from '@/context/AlertContext';
import { AnimatePresence } from 'framer-motion';
import EnhancedAlertCard from './EnhancedAlertCard';

interface LiveAlertPanelProps {
  onAlertSelect: (txId: string) => void;
}

export default function LiveAlertPanel({ onAlertSelect }: LiveAlertPanelProps) {
  const { alerts, isConnected, alertCount } = useAlerts();
  const scrollRef = useRef<HTMLDivElement>(null);

  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden bg-[rgba(7,11,18,0.95)] backdrop-blur-md">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
              Global triage
            </div>
            <h2 className="mt-1 text-lg font-semibold text-slate-100">Live Alerts</h2>
          </div>
          <div className="flex flex-col items-end gap-1 text-[10px] uppercase tracking-[0.3em] text-slate-400">
            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1">
              Latency &lt;0.8s
            </span>
            <span className="rounded-full border border-white/10 bg-white/5 px-2 py-1">
              System secure
            </span>
          </div>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>
            {alertCount} alert{alertCount !== 1 ? 's' : ''} received
          </span>
          <span className="flex items-center gap-2">
            <span
              className={`h-2 w-2 rounded-full ${
                isConnected ? 'bg-emerald-400' : 'bg-rose-400'
              } animate-pulse`}
            />
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Alert list */}
      <div
        ref={scrollRef}
        className="flex-1 min-h-0 overscroll-contain overflow-y-auto p-4 pr-3 space-y-3"
      >
        {alerts.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-slate-500 text-sm">
              {isConnected ? 'Waiting for alerts...' : 'Connecting to alert stream...'}
            </div>
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {alerts.map((alert, index) => (
              <EnhancedAlertCard
                key={`${alert.txId}-${index}`}
                alert={alert}
                onSelect={onAlertSelect}
              />
            ))}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
}
