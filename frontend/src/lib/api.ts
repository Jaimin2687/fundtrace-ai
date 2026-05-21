/**
 * API client for FundTrace AI backend
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
export const API_KEY = process.env.NEXT_PUBLIC_API_KEY || '';

// TypeScript interfaces
export interface GraphNode {
  txId: string;
  aml_label: string;
  risk_score: number;
  time_step?: number;
  x?: number;
  y?: number;
  z?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  is_suspicious?: boolean;
  pattern?: string | null;
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

export interface BankTransaction {
  tx_id: string;
  source_id: string;
  target_id: string;
  amount: number;
  currency?: string;
  timestamp: string;
  is_structuring_flag?: boolean;
}

export interface IngestStatus {
  enabled: boolean;
  brokers?: string | null;
  topic?: string | null;
  group_id?: string | null;
  received: number;
  stored: number;
  failed: number;
  last_error?: string | null;
  last_ingest_at?: string | null;
  last_tx_id?: string | null;
  last_batch_size: number;
  kafka_connected: boolean;
}

export interface IngestBatchResponse {
  accepted: number;
  stored: number;
  failed: number;
}

export interface BankApiStatus {
  enabled: boolean;
  base_url?: string | null;
  endpoint?: string | null;
  poll_interval_sec: number;
  verify_ssl: boolean;
  received: number;
  alerts_emitted: number;
  failed: number;
  last_error?: string | null;
  last_ingest_at?: string | null;
  last_tx_id?: string | null;
  last_batch_size: number;
  last_pull_at?: string | null;
  running: boolean;
}

export interface BankApiFetchResponse {
  received: number;
  alerts_emitted: number;
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

export async function fetchIngestStatus(): Promise<IngestStatus> {
  const response = await fetch(`${API_BASE}/api/v1/ingest/status`, {
    headers: {
      'X-API-Key': API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch ingest status: ${response.statusText}`);
  }

  return response.json();
}

export async function ingestBankTransactions(
  transactions: BankTransaction[]
): Promise<IngestBatchResponse> {
  const response = await fetch(`${API_BASE}/api/v1/ingest/transactions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    },
    body: JSON.stringify({ transactions }),
  });

  if (!response.ok) {
    throw new Error(`Failed to ingest transactions: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchBankApiStatus(): Promise<BankApiStatus> {
  const response = await fetch(`${API_BASE}/api/v1/ingest/bank/status`, {
    headers: {
      'X-API-Key': API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch bank API status: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchBankApiBatch(): Promise<BankApiFetchResponse> {
  const response = await fetch(`${API_BASE}/api/v1/ingest/bank/fetch`, {
    method: 'POST',
    headers: {
      'X-API-Key': API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch bank batch: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get WebSocket URL for alerts
 */
export function getWebSocketURL(): string {
  const rawBase = (process.env.NEXT_PUBLIC_WS_BASE_URL || API_BASE).replace(/\/$/, '');
  const wsBase = rawBase.replace(/^http/, 'ws');
  return `${wsBase}/api/v1/stream/alerts`;
}
