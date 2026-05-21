"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  fetchGraphFocus,
  fetchFraudClusters,
  fetchStats,
  GraphEdge,
  GraphNode,
  StatsResponse,
} from "@/lib/api";
import DashboardLayout from "@/components/DashboardLayout";
import LiveAlertPanel from "@/components/LiveAlertPanel";
import EnhancedGraphViewer from "@/components/EnhancedGraphViewer";
import EnhancedEvidencePanel from "@/components/EnhancedEvidencePanel";
import TemporalScrubber from "@/components/TemporalScrubber";
import { Activity, AlertTriangle, CheckCircle, Database } from "lucide-react";

export default function DashboardPage() {
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [highlightTxId, setHighlightTxId] = useState<string | undefined>();
  const [evidenceTxId, setEvidenceTxId] = useState<string | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [timeStep, setTimeStep] = useState(1);

  const getMaxTimeStep = (nodes: GraphNode[]) => {
    const steps = nodes.map((node) => node.time_step ?? 0);
    return Math.max(1, ...steps);
  };

  const applyGraphData = (data: { nodes: GraphNode[]; edges: GraphEdge[] }) => {
    setGraphNodes(data.nodes);
    setGraphEdges(data.edges);
    setTimeStep(getMaxTimeStep(data.nodes));
  };

  const maxTimeStep = useMemo(() => getMaxTimeStep(graphNodes), [graphNodes]);

  const filteredNodes = useMemo(() => {
    return graphNodes.filter((node) => (node.time_step ?? maxTimeStep) <= timeStep);
  }, [graphNodes, maxTimeStep, timeStep]);

  const filteredEdges = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map((node) => node.txId));
    return graphEdges.filter(
      (edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );
  }, [filteredNodes, graphEdges]);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to load stats:", error);
      }
    };

    loadStats();
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleAlertSelect = async (txId: string) => {
    setLoading(true);
    setHighlightTxId(txId);

    try {
      const data = await fetchGraphFocus(txId, 2);
      applyGraphData(data);
    } catch (error) {
      console.error("Failed to fetch graph focus:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNodeClick = (txId: string) => {
    setEvidenceTxId(txId);
  };

  const handleLoadFraudClusters = async () => {
    setLoading(true);
    setHighlightTxId(undefined);

    try {
      const data = await fetchFraudClusters();
      applyGraphData(data);
    } catch (error) {
      console.error("Failed to fetch fraud clusters:", error);
    } finally {
      setLoading(false);
    }
  };

  const topBar = (
    <div className="px-6 py-5">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Activity className="h-7 w-7 text-cyan-300" />
          <div>
            <div className="text-xs uppercase tracking-[0.35em] text-slate-400">
              Investigator canvas
            </div>
            <h1 className="text-xl font-semibold text-white">FundTrace AI</h1>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleLoadFraudClusters}
            disabled={loading}
            className="flex items-center gap-2 rounded-full border border-rose-500/40 px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-rose-200 transition hover:bg-rose-500/10 disabled:opacity-60"
          >
            <AlertTriangle className="h-4 w-4" />
            Load clusters
          </button>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-3 text-xs uppercase tracking-[0.3em] text-slate-400">
        <span className="rounded-full border border-emerald-400/30 bg-emerald-500/10 px-3 py-1 text-emerald-200">
          System secure
        </span>
        <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1">
          Case ID: {highlightTxId ?? "Awaiting selection"}
        </span>
      </div>

      {stats && (
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          {[
            { label: "Total Nodes", value: stats.total_nodes, icon: Database },
            { label: "Fraud Nodes", value: stats.fraud_nodes, icon: AlertTriangle },
            { label: "Legit Nodes", value: stats.legit_nodes, icon: CheckCircle },
            { label: "Total Edges", value: stats.total_edges, icon: Activity },
          ].map((item) => (
            <div
              key={item.label}
              className="rounded-2xl border border-white/10 bg-white/5 p-4"
            >
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-slate-400">
                <item.icon className="h-4 w-4" />
                {item.label}
              </div>
              <div className="mt-2 text-2xl font-semibold text-white">
                {item.value.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <DashboardLayout
      top={topBar}
      left={<LiveAlertPanel onAlertSelect={handleAlertSelect} />}
      center={
        <div className="relative h-full">
          {loading && (
            <div className="absolute inset-0 z-10 flex items-center justify-center bg-[#070b12]/70">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-6 py-4 text-sm text-slate-200">
                Loading graph data...
              </div>
            </div>
          )}
          <EnhancedGraphViewer
            nodes={filteredNodes}
            edges={filteredEdges}
            highlightTxId={highlightTxId}
            onNodeClick={handleNodeClick}
          />
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="absolute bottom-4 left-4 right-4"
          >
            <TemporalScrubber
              min={1}
              max={maxTimeStep}
              value={timeStep}
              onChange={setTimeStep}
            />
          </motion.div>
        </div>
      }
      right={
        <EnhancedEvidencePanel txId={evidenceTxId} onClose={() => setEvidenceTxId(null)} />
      }
      rightOpen={Boolean(evidenceTxId)}
      onToggleRight={() =>
        setEvidenceTxId((prev) => (prev ? null : highlightTxId ?? null))
      }
    />
  );
}
