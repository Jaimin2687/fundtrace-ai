'use client';

import { useState, useEffect } from 'react';
import GraphViewer from '@/components/GraphViewer';
import EvidencePanel from '@/components/EvidencePanel';
import {
  fetchGraphFocus,
  fetchFraudClusters,
  fetchStats,
  GraphNode,
  GraphEdge,
  StatsResponse,
} from '@/lib/api';
import { Search, Network, AlertTriangle, Loader2 } from 'lucide-react';

export default function NetworkPage() {
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [highlightTxId, setHighlightTxId] = useState<string | undefined>();
  const [evidenceTxId, setEvidenceTxId] = useState<string | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTxId, setSearchTxId] = useState('');
  const [searchDepth, setSearchDepth] = useState(2);

  // Load stats on mount
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

  // Handle search
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
      alert('Failed to load transaction. Please check the transaction ID.');
    } finally {
      setLoading(false);
    }
  };

  // Handle node click
  const handleNodeClick = (txId: string) => {
    setEvidenceTxId(txId);
  };

  // Load fraud clusters
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

  return (
    <div className="h-screen flex flex-col bg-slate-950">
      {/* Top Bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Network className="w-8 h-8 text-blue-500" />
            <div>
              <h1 className="text-2xl font-bold text-slate-100">Network Visualization</h1>
              <p className="text-sm text-slate-400">
                Explore transaction networks and fraud patterns
              </p>
            </div>
          </div>
        </div>

        {/* Search and Controls */}
        <div className="flex items-center gap-4">
          {/* Search Input */}
          <div className="flex-1 flex items-center gap-2">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={searchTxId}
                onChange={(e) => setSearchTxId(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="Enter transaction ID..."
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            {/* Depth Selector */}
            <select
              value={searchDepth}
              onChange={(e) => setSearchDepth(Number(e.target.value))}
              className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-slate-200 focus:outline-none focus:border-blue-500"
            >
              <option value={1}>Depth: 1</option>
              <option value={2}>Depth: 2</option>
              <option value={3}>Depth: 3</option>
              <option value={4}>Depth: 4</option>
            </select>

            {/* Search Button */}
            <button
              onClick={handleSearch}
              disabled={loading || !searchTxId.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Search className="w-4 h-4" />
              )}
              Search
            </button>
          </div>

          {/* Load Fraud Clusters Button */}
          <button
            onClick={handleLoadFraudClusters}
            disabled={loading}
            className="bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <AlertTriangle className="w-4 h-4" />
            Fraud Clusters
          </button>
        </div>

        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-5 gap-3 mt-4">
            <div className="bg-slate-800/50 rounded p-2 border border-slate-700">
              <div className="text-xs text-slate-500 mb-1">Total Nodes</div>
              <div className="text-lg font-bold text-slate-100">
                {stats.total_nodes.toLocaleString()}
              </div>
            </div>
            <div className="bg-slate-800/50 rounded p-2 border border-red-900/30">
              <div className="text-xs text-slate-500 mb-1">Fraud</div>
              <div className="text-lg font-bold text-red-400">
                {stats.fraud_nodes.toLocaleString()}
              </div>
            </div>
            <div className="bg-slate-800/50 rounded p-2 border border-green-900/30">
              <div className="text-xs text-slate-500 mb-1">Legit</div>
              <div className="text-lg font-bold text-green-400">
                {stats.legit_nodes.toLocaleString()}
              </div>
            </div>
            <div className="bg-slate-800/50 rounded p-2 border border-slate-700">
              <div className="text-xs text-slate-500 mb-1">Unknown</div>
              <div className="text-lg font-bold text-slate-400">
                {stats.unknown_nodes.toLocaleString()}
              </div>
            </div>
            <div className="bg-slate-800/50 rounded p-2 border border-slate-700">
              <div className="text-xs text-slate-500 mb-1">Edges</div>
              <div className="text-lg font-bold text-slate-100">
                {stats.total_edges.toLocaleString()}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 relative overflow-hidden">
        {loading && (
          <div className="absolute inset-0 bg-slate-950/50 flex items-center justify-center z-10">
            <div className="bg-slate-900 rounded-lg p-6 border border-slate-800">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4" />
              <div className="text-slate-300 text-sm">Loading graph data...</div>
            </div>
          </div>
        )}

        <GraphViewer
          nodes={graphNodes}
          edges={graphEdges}
          highlightTxId={highlightTxId}
          onNodeClick={handleNodeClick}
        />

        {/* Legend */}
        <div className="absolute bottom-4 left-4 bg-slate-900/90 backdrop-blur border border-slate-800 rounded-lg p-4">
          <div className="text-sm font-semibold text-slate-100 mb-3">Legend</div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-xs text-slate-300">Fraud</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-xs text-slate-300">Legit</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-500" />
              <span className="text-xs text-slate-300">Unknown</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-xs text-slate-300">Highlighted</span>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-700">
            <div className="text-xs text-slate-400">
              Node size = Risk score
            </div>
            <div className="text-xs text-slate-400">
              Click node for evidence
            </div>
          </div>
        </div>

        {/* Graph Info */}
        {graphNodes.length > 0 && (
          <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur border border-slate-800 rounded-lg p-3">
            <div className="text-xs text-slate-400">
              Showing {graphNodes.length} nodes, {graphEdges.length} edges
            </div>
          </div>
        )}

        {/* Evidence Panel */}
        <EvidencePanel txId={evidenceTxId} onClose={() => setEvidenceTxId(null)} />
      </div>
    </div>
  );
}
