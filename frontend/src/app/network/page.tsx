'use client';

import { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import EnhancedGraphViewer from '@/components/EnhancedGraphViewer';
import EnhancedEvidencePanel from '@/components/EnhancedEvidencePanel';
import DashboardLayout from '@/components/DashboardLayout';
import {
  fetchGraphFocus,
  fetchFraudClusters,
  fetchStats,
  GraphNode,
  GraphEdge,
  StatsResponse,
} from '@/lib/api';
import { Search, Network, AlertTriangle, Loader2, Database, CheckCircle, Activity } from 'lucide-react';

export default function NetworkPage() {
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [highlightTxId, setHighlightTxId] = useState<string | undefined>();
  const [evidenceTxId, setEvidenceTxId] = useState<string | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTxId, setSearchTxId] = useState('');
  const [searchDepth, setSearchDepth] = useState(2);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await fetchStats();
        setStats(data);
      } catch (error) {
        console.error('Failed to load stats:', error);
      }
    };
    loadStats();
  }, []);

  const handleSearch = async () => {
    if (!searchTxId.trim()) return;
    setLoading(true);
    setHighlightTxId(searchTxId);
    try {
      const data = await fetchGraphFocus(searchTxId, searchDepth);
      setGraphNodes(data.nodes);
      setGraphEdges(data.edges);
    } catch (error) {
      console.error('Failed to fetch graph focus:', error);
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
      setGraphNodes(data.nodes);
      setGraphEdges(data.edges);
    } catch (error) {
      console.error('Failed to fetch fraud clusters:', error);
    } finally {
      setLoading(false);
    }
  };

  const topBar = (
    <div className="px-6 py-5">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="flex items-center gap-3">
          <Network className="h-7 w-7 text-cyan-300" />
          <div>
            <div className="text-xs uppercase tracking-[0.35em] text-slate-400">
              Network lab
            </div>
            <h1 className="text-xl font-semibold text-white">
              Transaction Graph
            </h1>
          </div>
        </div>
      </div>

      {/* Search and Controls */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={searchTxId}
            onChange={(e) => setSearchTxId(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Enter transaction ID..."
            className="w-full rounded-xl border border-white/10 bg-white/5 pl-10 pr-4 py-2.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400/50 transition"
          />
        </div>
        <select
          value={searchDepth}
          onChange={(e) => setSearchDepth(Number(e.target.value))}
          className="rounded-xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-cyan-400/50"
        >
          <option value={1}>Depth: 1</option>
          <option value={2}>Depth: 2</option>
          <option value={3}>Depth: 3</option>
          <option value={4}>Depth: 4</option>
        </select>
        <button
          onClick={handleSearch}
          disabled={loading || !searchTxId.trim()}
          className="flex items-center gap-2 rounded-xl bg-cyan-400 px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-300 hover:shadow-[0_0_15px_rgba(34,211,238,0.4)] disabled:opacity-50"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          Search
        </button>
        <button
          onClick={handleLoadFraudClusters}
          disabled={loading}
          className="flex items-center gap-2 rounded-xl border border-rose-500/40 bg-rose-500/10 px-5 py-2.5 text-sm font-semibold text-rose-200 transition hover:bg-rose-500/20 hover:shadow-[0_0_15px_rgba(244,63,94,0.3)] disabled:opacity-50"
        >
          <AlertTriangle className="h-4 w-4" />
          Fraud Clusters
        </button>
      </div>

      {/* Stats Row */}
      {stats && (
        <div className="mt-4 grid gap-3 md:grid-cols-5">
          {[
            { label: 'Total Nodes', value: stats.total_nodes, icon: Database },
            { label: 'Fraud Nodes', value: stats.fraud_nodes, icon: AlertTriangle, accent: true },
            { label: 'Legit Nodes', value: stats.legit_nodes, icon: CheckCircle },
            { label: 'Unknown', value: stats.unknown_nodes, icon: Activity },
            { label: 'Edges', value: stats.total_edges, icon: Network },
          ].map((item) => (
            <div
              key={item.label}
              className={`glass-panel rounded-xl p-3 ${
                item.accent ? 'border-rose-500/30' : ''
              }`}
            >
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-400">
                <item.icon className="h-3.5 w-3.5" />
                {item.label}
              </div>
              <div className={`mt-1 text-lg font-semibold ${item.accent ? 'text-rose-300' : 'text-white'}`}>
                {item.value.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // Left panel: legend and graph info
  const leftPanel = (
    <div className="flex h-full flex-col p-5">
      <div className="text-xs uppercase tracking-[0.3em] text-slate-400 mb-4">
        Graph Legend
      </div>
      <div className="space-y-3">
        {[
          { color: 'bg-rose-500', label: 'Fraud' },
          { color: 'bg-emerald-400', label: 'Legit' },
          { color: 'bg-slate-500', label: 'Unknown' },
          { color: 'bg-cyan-400', label: 'Highlighted' },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-3">
            <div className={`h-3 w-3 rounded-full ${item.color}`} />
            <span className="text-sm text-slate-300">{item.label}</span>
          </div>
        ))}
      </div>
      <div className="mt-6 border-t border-white/10 pt-4">
        <div className="text-xs text-slate-500">Node size = Risk score</div>
        <div className="text-xs text-slate-500 mt-1">Click node for evidence</div>
      </div>
      {graphNodes.length > 0 && (
        <div className="mt-6 glass-panel rounded-xl p-4">
          <div className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-2">
            Current View
          </div>
          <div className="text-sm text-white">{graphNodes.length} nodes</div>
          <div className="text-sm text-white">{graphEdges.length} edges</div>
        </div>
      )}
    </div>
  );

  return (
    <DashboardLayout
      top={topBar}
      left={leftPanel}
      center={
        <div className="relative h-full">
          {loading && (
            <div className="absolute inset-0 z-10 flex items-center justify-center bg-[#070b12]/70">
              <div className="glass-panel rounded-2xl p-6 text-center">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-cyan-400 mx-auto mb-3" />
                <div className="text-sm text-slate-300">Loading graph data...</div>
              </div>
            </div>
          )}
          <EnhancedGraphViewer
            nodes={graphNodes}
            edges={graphEdges}
            highlightTxId={highlightTxId}
            onNodeClick={handleNodeClick}
          />
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
