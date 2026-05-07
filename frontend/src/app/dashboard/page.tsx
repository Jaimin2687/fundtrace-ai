'use client';

import { useState, useEffect } from 'react';
import LiveAlertPanel from '@/components/LiveAlertPanel';
import GraphViewer from '@/components/GraphViewer';
import EvidencePanel from '@/components/EvidencePanel';
import { fetchGraphFocus, fetchFraudClusters, fetchStats, GraphNode, GraphEdge, StatsResponse } from '@/lib/api';
import { Activity, Database, AlertTriangle, CheckCircle } from 'lucide-react';

export default function DashboardPage() {
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([]);
  const [graphEdges, setGraphEdges] = useState<GraphEdge[]>([]);
  const [highlightTxId, setHighlightTxId] = useState<string | undefined>();
  const [evidenceTxId, setEvidenceTxId] = useState<string | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);

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
    // Refresh stats every 30 seconds
    const interval = setInterval(loadStats, 30000);
    return () => clearInterval(interval);
  }, []);

  // Handle alert selection
  const handleAlertSelect = async (txId: string) => {
    setLoading(true);
    setHighlightTxId(txId);
    
    try {
      const data = await fetchGraphFocus(txId, 2);
      setGraphNodes(data.nodes);
      setGraphEdges(data.edges);
    } catch (error) {
      console.error('Failed to fetch graph focus:', error);
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

  // Seed demo data
  const handleSeedDemoData = async () => {
    setSeeding(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/graph/seed-demo', {
        method: 'POST',
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to seed demo data');
      }
      
      const result = await response.json();
      console.log('Demo data seeded:', result);
      
      // Reload fraud clusters to show the demo data
      await handleLoadFraudClusters();
      
      // Reload stats
      const statsData = await fetchStats();
      setStats(statsData);
      
      alert('Demo data seeded successfully! ' + result.nodes_created + ' nodes created.');
    } catch (error) {
      console.error('Failed to seed demo data:', error);
      alert('Failed to seed demo data. Check console for details.');
    } finally {
      setSeeding(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-slate-950">
      {/* Top Bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Activity className="w-8 h-8 text-blue-500" />
            <h1 className="text-2xl font-bold text-slate-100">FundTrace AI</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleSeedDemoData}
              disabled={seeding || loading}
              className="bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              <Database className="w-4 h-4" />
              {seeding ? 'Seeding...' : 'Seed Demo Data'}
            </button>
            <button
              onClick={handleLoadFraudClusters}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 disabled:bg-red-800 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              <AlertTriangle className="w-4 h-4" />
              Load Fraud Clusters
            </button>
          </div>
        </div>

        {/* Stats Row */}
        {stats && (
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
              <div className="flex items-center gap-2 mb-1">
                <Database className="w-4 h-4 text-slate-400" />
                <span className="text-xs text-slate-500">Total Nodes</span>
              </div>
              <div className="text-2xl font-bold text-slate-100">
                {stats.total_nodes.toLocaleString()}
              </div>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-3 border border-red-900/30">
              <div className="flex items-center gap-2 mb-1">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <span className="text-xs text-slate-500">Fraud Nodes</span>
              </div>
              <div className="text-2xl font-bold text-red-400">
                {stats.fraud_nodes.toLocaleString()}
              </div>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-3 border border-green-900/30">
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-xs text-slate-500">Legit Nodes</span>
              </div>
              <div className="text-2xl font-bold text-green-400">
                {stats.legit_nodes.toLocaleString()}
              </div>
            </div>

            <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
              <div className="flex items-center gap-2 mb-1">
                <Activity className="w-4 h-4 text-slate-400" />
                <span className="text-xs text-slate-500">Total Edges</span>
              </div>
              <div className="text-2xl font-bold text-slate-100">
                {stats.total_edges.toLocaleString()}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Live Alerts */}
        <div className="w-80 flex-shrink-0">
          <LiveAlertPanel onAlertSelect={handleAlertSelect} />
        </div>

        {/* Main Area - Graph Viewer */}
        <div className="flex-1 relative">
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
        </div>

        {/* Right Panel - Evidence */}
        <EvidencePanel txId={evidenceTxId} onClose={() => setEvidenceTxId(null)} />
      </div>
    </div>
  );
}
