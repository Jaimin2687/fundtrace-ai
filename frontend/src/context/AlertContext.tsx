'use client';

import React, { createContext, useContext, useEffect, useRef, useState, useCallback, ReactNode } from 'react';
import { AlertEvent, getWebSocketURL } from '@/lib/api';

interface AlertContextType {
  alerts: AlertEvent[];
  isConnected: boolean;
  alertCount: number;
}

const AlertContext = createContext<AlertContextType>({
  alerts: [],
  isConnected: false,
  alertCount: 0,
});

export function useAlerts() {
  return useContext(AlertContext);
}

export function AlertProvider({ children }: { children: ReactNode }) {
  const [alerts, setAlerts] = useState<AlertEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [alertCount, setAlertCount] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const reconnectRef = useRef<number | null>(null);
  const pingRef = useRef<number | null>(null);

  useEffect(() => {
    let isCancelled = false;

    const connect = () => {
      if (isCancelled) return;
      const ws = new WebSocket(getWebSocketURL());
      wsRef.current = ws;

      ws.onopen = () => {
        retryRef.current = 0;
        setIsConnected(true);
        if (pingRef.current) window.clearInterval(pingRef.current);
        pingRef.current = window.setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) ws.send('ping');
        }, 20000);
      };

      ws.onmessage = (event) => {
        try {
          const alert: AlertEvent = JSON.parse(event.data);
          setAlerts((prev) => [alert, ...prev].slice(0, 100));
          setAlertCount((prev) => prev + 1);
        } catch (err) {
          console.error('[WebSocket] Failed to parse alert:', err);
        }
      };

      ws.onerror = () => {
        setIsConnected(false);
        ws.close();
      };

      ws.onclose = () => {
        setIsConnected(false);
        if (pingRef.current) window.clearInterval(pingRef.current);
        const retry = Math.min(10000, 1000 * 2 ** retryRef.current);
        retryRef.current += 1;
        reconnectRef.current = window.setTimeout(connect, retry);
      };
    };

    connect();

    return () => {
      isCancelled = true;
      if (reconnectRef.current) window.clearTimeout(reconnectRef.current);
      if (pingRef.current) window.clearInterval(pingRef.current);
      if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.close();
    };
  }, []);

  return (
    <AlertContext.Provider value={{ alerts, isConnected, alertCount }}>
      {children}
    </AlertContext.Provider>
  );
}
