'use client';

import { useEffect, useState, useRef } from 'react';
import { AlertEvent, getWebSocketURL } from '@/lib/api';
import AlertCard from './AlertCard';

interface LiveAlertPanelProps {
  onAlertSelect: (txId: string) => void;
}

export default function LiveAlertPanel({ onAlertSelect }: LiveAlertPanelProps) {
  const [alerts, setAlerts] = useState<AlertEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket(getWebSocketURL());
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[WebSocket] Connected to alert stream');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const alert: AlertEvent = JSON.parse(event.data);
        console.log('[WebSocket] Received alert:', alert);
        
        setAlerts((prev) => {
          const newAlerts = [alert, ...prev];
          // Keep only last 50 alerts
          return newAlerts.slice(0, 50);
        });

        // Auto-scroll to top
        if (scrollRef.current) {
          scrollRef.current.scrollTop = 0;
        }
      } catch (error) {
        console.error('[WebSocket] Failed to parse alert:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('[WebSocket] Disconnected');
      setIsConnected(false);
    };

    // Cleanup on unmount
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  return (
    <div className="h-full flex flex-col bg-slate-900 border-r border-slate-800">
      {/* Header */}
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-semibold text-slate-100">Live Alerts</h2>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-green-500' : 'bg-red-500'
              } animate-pulse`}
            />
            <span className="text-xs text-slate-400">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
        <p className="text-xs text-slate-500">
          {alerts.length} alert{alerts.length !== 1 ? 's' : ''} received
        </p>
      </div>

      {/* Alert list */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {alerts.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-slate-500 text-sm">
              {isConnected ? 'Waiting for alerts...' : 'Connecting to alert stream...'}
            </div>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <AlertCard
              key={`${alert.txId}-${index}`}
              alert={alert}
              onSelect={onAlertSelect}
            />
          ))
        )}
      </div>
    </div>
  );
}
