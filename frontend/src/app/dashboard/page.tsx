"use client";

import { useEffect, useMemo, useState, useRef } from "react";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";

// Dynamically import force graph to avoid SSR issues
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

export default function Dashboard() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [demoMode, setDemoMode] = useState(false);
  const [focusId, setFocusId] = useState("ACC-0000");
  const [inputId, setInputId] = useState("ACC-0000");
  const [modelStatus, setModelStatus] = useState<any | null>(null);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [hoverNode, setHoverNode] = useState<any | null>(null);
  const [hoverPos, setHoverPos] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<any>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const pendingFocusRef = useRef(false);

  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
    []
  );
  const wsBase = useMemo(
    () => process.env.NEXT_PUBLIC_WS_BASE_URL || "ws://localhost:8000",
    []
  );
  const apiKey = useMemo(
    () => process.env.NEXT_PUBLIC_API_KEY || "tactical-fraud-trace-391x",
    []
  );

  // Fetch initial graph
  const applyFocusZoom = (nodes: any[]) => {
    if (!graphRef.current) {
      return;
    }

    const fraudNodes = nodes.filter((node: any) => node.aml_label === 1);
    if (fraudNodes.length > 0) {
      graphRef.current.zoomToFit(900, 80, (node: any) => node.aml_label === 1);
      return;
    }

    graphRef.current.zoomToFit(800, 80);
  };

  const resetZoom = () => {
    if (!graphRef.current) {
      return;
    }
    graphRef.current.zoomToFit(700, 60);
  };

  const fetchGraph = (clusterId: string, shouldFocus = false) => {
    setLoading(true);
    setError(null);
    setDemoMode(false);
    pendingFocusRef.current = shouldFocus;
    fetch(`${apiBase}/api/v1/graph/focus/${clusterId}` , {
      headers: { "X-API-KEY": apiKey }
    })
      .then(res => {
        if (!res.ok) {
          throw new Error(`Graph request failed (${res.status})`);
        }
        return res.json();
      })
      .then(data => {
        // Map backend 'edges' to ForceGraph 'links' requirements.
        const mappedData = {
          nodes: data.nodes.map((n: any) => ({ ...n, id: n.account_id, aml_label: n.aml_label ?? 0 })),
          links: data.edges.map((e: any) => ({ ...e, source: e.source_id, target: e.target_id }))
        };
        setGraphData(mappedData as any);
        setLoading(false);
        if (pendingFocusRef.current) {
          pendingFocusRef.current = false;
          window.setTimeout(() => applyFocusZoom(mappedData.nodes), 50);
        }
      })
      .catch(err => {
        console.error(err);
        const fallback = {
          nodes: [
            { id: "ACC-0000", account_id: "ACC-0000", kyc_risk_baseline: 88 },
            { id: "ACC-0172", account_id: "ACC-0172", kyc_risk_baseline: 62 },
            { id: "ACC-1044", account_id: "ACC-1044", kyc_risk_baseline: 41 },
            { id: "ACC-3319", account_id: "ACC-3319", kyc_risk_baseline: 77 },
          ],
          links: [
            { source: "ACC-0000", target: "ACC-0172" },
            { source: "ACC-0172", target: "ACC-1044" },
            { source: "ACC-0000", target: "ACC-3319" },
          ],
        };
        setGraphData(fallback as any);
        setDemoMode(true);
        setError("Graph API offline. Showing demo subgraph.");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchGraph(focusId, true);
  }, [focusId]);

  // Connect to websocket
  useEffect(() => {
    const ws = new WebSocket(`${wsBase}/api/v1/stream/alerts?token=${apiKey}`);
    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      setAlerts(prev => [alert, ...prev].slice(0, 10));
    };
    return () => ws.close();
  }, [wsBase, apiKey]);

  useEffect(() => {
    let active = true;
    const fetchStatus = () => {
      fetch(`${apiBase}/api/v1/stream/status/latest`)
        .then(res => res.json())
        .then(data => {
          if (!active) {
            return;
          }
          setModelStatus(data);
        })
        .catch(() => {
          if (!active) {
            return;
          }
          setModelStatus(null);
        });
    };

    fetchStatus();
    const interval = window.setInterval(fetchStatus, 15000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [apiBase]);

  useEffect(() => {
    const updateDimensions = () => {
      const width = containerRef.current?.clientWidth || 800;
      const height = containerRef.current?.clientHeight || 600;
      setDimensions({ width, height });
    };
    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  return (
    <div className="min-h-screen bg-[#0A0F1C] text-[#dce4e3] font-['Inter'] relative overflow-hidden">
      {/* Grid Background */}
      <div className="absolute inset-0 z-0 opacity-20 hud-grid" />

      <div className="relative z-10 flex h-screen">
        {/* Sidebar */}
        <div className="w-80 border-r border-[#3b494a] bg-[#0A0F1C]/90 backdrop-blur flex flex-col">
          <div className="p-4 border-b border-[#3b494a]">
            <h1 className="font-['Space_Grotesk'] text-xl font-bold text-[#2DE2E6]">FundTrace AI</h1>
            <p className="text-xs text-[#859494] font-mono mt-1">INVESTIGATOR TERMINAL</p>
          </div>

          <div className="p-4 border-b border-[#3b494a]">
            <div className="text-[10px] font-mono text-[#859494] mb-2">FOCUS CLUSTER</div>
            <div className="flex gap-2">
              <input
                className="flex-1 bg-transparent border border-[#3b494a] px-2 py-1 text-xs font-mono text-[#dce4e3]"
                value={inputId}
                onChange={(event) => setInputId(event.target.value)}
                placeholder="ACC-0000"
              />
              <button
                className="border border-[#3b494a] px-2 py-1 text-[10px] text-[#2DE2E6]"
                onClick={() => setFocusId(inputId.trim() || "ACC-0000")}
              >
                FOCUS
              </button>
              <button
                className="border border-[#3b494a] px-2 py-1 text-[10px] text-[#859494]"
                onClick={resetZoom}
              >
                RESET
              </button>
            </div>
            <div className="mt-2 text-[10px] font-mono text-[#859494]">ACTIVE: {focusId}</div>
          </div>

          <div className="p-4 border-b border-[#3b494a]">
            <div className="text-[10px] font-mono text-[#859494] mb-2">ACCOUNT DETAIL</div>
            {selectedNode ? (
              <div className="space-y-1 text-[10px] font-mono text-[#dce4e3]">
                <div>ID: {selectedNode.account_id}</div>
                <div>TYPE: {selectedNode.account_type ?? "Unknown"}</div>
                <div>KYC: {selectedNode.kyc_risk_baseline ?? 0}</div>
                <div>VOLUME: {selectedNode.total_volume ?? 0}</div>
                <div>AML: {selectedNode.aml_label === 1 ? "FLAGGED" : "CLEAR"}</div>
              </div>
            ) : (
              <div className="text-[10px] font-mono text-[#859494]">CLICK A NODE</div>
            )}
          </div>

          <div className="p-4 border-b border-[#3b494a]">
            <div className="text-[10px] font-mono text-[#859494] mb-2">MODEL STATUS</div>
            {modelStatus ? (
              <div className="space-y-1 text-[10px] font-mono text-[#dce4e3]">
                <div>LAST RUN: {modelStatus.timestamp}</div>
                <div>ALERTS SENT: {modelStatus.alerts_sent}</div>
                <div>MODEL: {modelStatus.model_version ?? "unknown"}</div>
                <div>MODE: {modelStatus.run_mode ?? "unknown"}</div>
              </div>
            ) : (
              <div className="text-[10px] font-mono text-[#859494]">NO STATUS YET</div>
            )}
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <h2 className="text-xs font-bold tracking-widest text-[#859494] uppercase mb-4">Live Threat Stream</h2>
            
            {alerts.map((alert, index) => (
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                key={`${alert.cluster_id}-${alert.timestamp ?? "no-ts"}-${index}`} 
                className="border border-[#ffb4ab]/30 bg-[#93000a]/10 p-3 relative cursor-pointer"
                onClick={() => {
                  setInputId(alert.cluster_id);
                  setFocusId(alert.cluster_id);
                }}
              >
                <div className="absolute top-0 left-0 w-1 h-full bg-[#FF3B30]" />
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] font-mono text-[#ffb4ab]">{alert.timestamp ?? "NO_TS"}</span>
                  <span className="text-[10px] font-bold bg-[#FF3B30] text-white px-1 leading-tight">SCORE: {alert.risk_score}</span>
                </div>
                <div className="text-sm font-['Space_Grotesk'] font-medium text-white">
                  {alert.threat_type}
                </div>
                <div className="mt-2 text-xs font-mono text-[#859494]">
                  {alert.cluster_id}
                </div>
                <div className="mt-2 text-[10px] text-[#859494]">
                  {alert.narrative}
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Main Graph Area */}
        <div
          className="flex-1 relative"
          ref={containerRef}
          onMouseMove={(event) => {
            const bounds = event.currentTarget.getBoundingClientRect();
            setHoverPos({ x: event.clientX - bounds.left, y: event.clientY - bounds.top });
          }}
        >
          {loading ? (
             <div className="absolute inset-0 flex items-center justify-center text-[#2DE2E6] font-mono text-sm">
               [ INITIALIZING GRAPH ENGINE... ]
             </div>
          ) : (
            <ForceGraph2D
              ref={graphRef}
              graphData={graphData}
              width={dimensions.width}
              height={dimensions.height}
              backgroundColor="transparent"
              nodeColor={node => {
                const item = node as any;
                if (item.aml_label === 1) {
                  return "#FF3B30";
                }
                if (selectedNode && selectedNode.account_id === item.account_id) {
                  return "#FFD166";
                }
                return "#2DE2E6";
              }}
              linkColor={link => {
                const item = link as any;
                const sourceId = item.source?.account_id || item.source;
                const targetId = item.target?.account_id || item.target;
                if (selectedNode && (selectedNode.account_id === sourceId || selectedNode.account_id === targetId)) {
                  return "rgba(255, 209, 102, 0.5)";
                }
                return "rgba(45, 226, 230, 0.2)";
              }}
              nodeRelSize={4}
              nodeVal={node => ((node as any).aml_label === 1 ? 2.2 : 1)}
              linkWidth={link => {
                const item = link as any;
                const sourceId = item.source?.account_id || item.source;
                const targetId = item.target?.account_id || item.target;
                if (selectedNode && (selectedNode.account_id === sourceId || selectedNode.account_id === targetId)) {
                  return 1.8;
                }
                return 1;
              }}
              onNodeClick={(node) => {
                const accountId = (node as any).account_id as string | undefined;
                if (accountId) {
                  setInputId(accountId);
                  setFocusId(accountId);
                  setSelectedNode(node);
                }
              }}
              onNodeHover={(node) => {
                setHoverNode(node || null);
              }}
            />
          )}

          {hoverNode && (
            <div
              className="absolute pointer-events-none border border-[#3b494a] bg-[#0A0F1C]/90 px-3 py-2 text-[10px] font-mono text-[#dce4e3]"
              style={{ left: hoverPos.x + 12, top: hoverPos.y + 12 }}
            >
              <div>ID: {hoverNode.account_id}</div>
              <div>TYPE: {hoverNode.account_type ?? "Unknown"}</div>
              <div>KYC: {hoverNode.kyc_risk_baseline ?? 0}</div>
              <div>VOLUME: {hoverNode.total_volume ?? 0}</div>
              <div>AML: {hoverNode.aml_label === 1 ? "FLAGGED" : "CLEAR"}</div>
            </div>
          )}
          
          {/* Top overlay */}
          <div className="absolute top-4 left-4 p-3 border border-[#3b494a] bg-[#0A0F1C]/80 backdrop-blur font-mono text-xs text-[#859494]">
            [ NODE_MAP // {focusId} SUBGRAPH ]<br/>
            TOTAL NODES: <span className="text-[#2DE2E6]">{graphData.nodes?.length || 0}</span><br/>
            TOTAL EDGES: <span className="text-[#2DE2E6]">{graphData.links?.length || 0}</span>
          </div>
          {error && (
            <div className="absolute bottom-4 left-4 border border-[#3b494a] bg-[#0A0F1C]/90 px-3 py-2 font-mono text-[10px] text-[#ffb4ab]">
              {demoMode ? "[ DEMO MODE ]" : "[ CONNECTION FAILED ]"} {error}
              <button
                className="ml-3 border border-[#3b494a] px-2 py-1 text-[#2DE2E6]"
                onClick={fetchGraph}
              >
                RETRY
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}