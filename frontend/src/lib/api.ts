/**
 * API client for FundTrace AI backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

// TypeScript interfaces
export interface GraphNode {
  txId: string;
  aml_label: string;
  risk_score: number;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface AlertEvent {
  txId: string;
  risk_score: number;
  aml_label?: string;
  pattern: string;
  timestamp: string;
  amount?: number;
  source?: string;
}

export interface EvidencePackage {
  txId: string;
  chain: string[];
  risk_scores: number[];
  patterns: string[];
  total_amount: number;
  generated_at: string;
  narrative: string;
}

export interface StatsResponse {
  total_nodes: number;
  fraud_nodes: number;
  legit_nodes: number;
  unknown_nodes: number;
  total_edges: number;
}

/**
 * Fetch graph focus subgraph for a transaction
 */
export async function fetchGraphFocus(
  txId: string,
  depth: number = 2
): Promise<GraphResponse> {
  const response = await fetch(
    `${API_BASE}/api/v1/graph/focus?txId=${encodeURIComponent(txId)}&depth=${depth}`,
    {
      headers: {
        'X-API-Key': API_KEY,
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch graph focus: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch fraud clusters
 */
export async function fetchFraudClusters(): Promise<GraphResponse> {
  const response = await fetch(`${API_BASE}/api/v1/graph/fraud-clusters`, {
    headers: {
      'X-API-Key': API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch fraud clusters: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch evidence package for a transaction
 */
export async function fetchEvidence(txId: string): Promise<EvidencePackage> {
  const response = await fetch(`${API_BASE}/api/v1/graph/evidence/${encodeURIComponent(txId)}`, {
    headers: {
      'X-API-Key': API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch evidence: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Fetch graph statistics
 */
export async function fetchStats(): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE}/api/v1/graph/stats`, {
    headers: {
      'X-API-Key': API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch stats: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get WebSocket URL for alerts
 */
export function getWebSocketURL(): string {
  const wsBase = process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000';
  return `${wsBase}/api/v1/stream/alerts`;
}
