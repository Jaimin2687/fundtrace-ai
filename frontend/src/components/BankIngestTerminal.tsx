"use client";

import { useEffect, useMemo, useState } from "react";
import {
  fetchIngestStatus,
  ingestBankTransactions,
  fetchBankApiStatus,
  fetchBankApiBatch,
  BankTransaction,
  IngestStatus,
  BankApiStatus,
} from "@/lib/api";
import { CloudUpload, Database, ShieldCheck } from "lucide-react";

const defaultPayload: BankTransaction[] = [
  {
    tx_id: "BANK-TX-1001",
    source_id: "ACC-001",
    target_id: "ACC-002",
    amount: 45000,
    currency: "INR",
    timestamp: new Date().toISOString(),
    is_structuring_flag: false,
  },
];

export default function BankIngestTerminal() {
  const [status, setStatus] = useState<IngestStatus | null>(null);
  const [bankStatus, setBankStatus] = useState<BankApiStatus | null>(null);
  const [payload, setPayload] = useState<string>(
    JSON.stringify(defaultPayload, null, 2)
  );
  const [loading, setLoading] = useState(false);
  const [loadingBank, setLoadingBank] = useState(false);
  const [sending, setSending] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const connectionLabel = useMemo(() => {
    if (!status) return "Checking…";
    if (!status.enabled) return "Disabled";
    return status.kafka_connected ? "Kafka connected" : "Kafka idle";
  }, [status]);

  const bankLabel = useMemo(() => {
    if (!bankStatus) return "Checking…";
    if (!bankStatus.enabled) return "Disabled";
    return bankStatus.running ? "Polling" : "Ready";
  }, [bankStatus]);

  const loadStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchIngestStatus();
      setStatus(data);
    } catch (err) {
      console.warn("Backend not ready: ", err);
      setStatus(null);
    } finally {
      setLoading(false);
    }
  };

  const loadBankStatus = async () => {
    setLoadingBank(true);
    setError(null);
    try {
      const data = await fetchBankApiStatus();
      setBankStatus(data);
    } catch (err) {
      console.warn("Backend not ready: ", err);
      setBankStatus(null);
    } finally {
      setLoadingBank(false);
    }
  };

  useEffect(() => {
    loadStatus();
    loadBankStatus();
  }, []);

  const handleSend = async () => {
    setSending(true);
    setError(null);
    setSuccess(null);
    try {
      const parsed = JSON.parse(payload);
      const transactions = Array.isArray(parsed) ? parsed : [parsed];
      const result = await ingestBankTransactions(transactions);
      setSuccess(`Accepted ${result.accepted}, stored ${result.stored}`);
      await loadStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to ingest batch");
    } finally {
      setSending(false);
    }
  };

  const handleFetch = async () => {
    setFetching(true);
    setError(null);
    setSuccess(null);
    try {
      const result = await fetchBankApiBatch();
      setSuccess(`Pulled ${result.received}, streamed ${result.alerts_emitted}`);
      await loadBankStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to pull bank batch");
    } finally {
      setFetching(false);
    }
  };

  return (
    <section className="mx-auto w-full max-w-7xl px-6 py-16">
      <div className="grid gap-8 lg:grid-cols-[0.9fr,1.1fr]">
        <div className="space-y-6">
          <div className="text-xs uppercase tracking-[0.35em] text-cyan-200">
            Bank ingest terminal
          </div>
          <h2 className="text-3xl font-semibold text-white">
            Stream real transactions into FundTrace.
          </h2>
          <p className="text-sm text-slate-300">
            Enable Kafka ingestion for production banks, or post secure HTTP batches
            from a core banking API when Kafka is not available.
          </p>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-400">
              <span>Bank API status</span>
              <span className="text-emerald-200">{bankLabel}</span>
            </div>
            <div className="mt-4 grid gap-3 text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-cyan-200" />
                <span>Endpoint: {bankStatus?.endpoint ?? "—"}</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-cyan-200" />
                <span>Base URL: {bankStatus?.base_url ?? "—"}</span>
              </div>
              <div className="flex items-center gap-2">
                <CloudUpload className="h-4 w-4 text-cyan-200" />
                <span>Poll interval: {bankStatus?.poll_interval_sec ?? "—"}s</span>
              </div>
            </div>
            <div className="mt-4 flex items-center gap-3 text-xs text-slate-400">
              <button
                onClick={handleFetch}
                disabled={fetching || !bankStatus?.enabled}
                className="rounded-full border border-white/10 px-4 py-1.5 text-[10px] uppercase tracking-[0.2em] text-slate-200 disabled:opacity-50"
              >
                {fetching ? "Pulling..." : "Fetch batch"}
              </button>
              <button
                onClick={loadBankStatus}
                disabled={loadingBank}
                className="rounded-full border border-white/10 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-slate-300"
              >
                Refresh
              </button>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
              Bank ingest telemetry
            </div>
            <div className="mt-4 grid grid-cols-3 gap-3 text-center text-xs text-slate-200">
              <div className="rounded-xl border border-white/10 bg-white/5 py-3">
                <div className="text-lg font-semibold text-white">
                  {bankStatus?.received ?? 0}
                </div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
                  Received
                </div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 py-3">
                <div className="text-lg font-semibold text-white">
                  {bankStatus?.alerts_emitted ?? 0}
                </div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
                  Streamed
                </div>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 py-3">
                <div className="text-lg font-semibold text-white">
                  {bankStatus?.failed ?? 0}
                </div>
                <div className="text-[10px] uppercase tracking-[0.2em] text-slate-400">
                  Failed
                </div>
              </div>
            </div>
            {bankStatus?.last_error && (
              <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-200">
                Last error: {bankStatus.last_error}
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-5">
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-400">
              <span>Kafka / HTTP ingest</span>
              <span className="text-emerald-200">{connectionLabel}</span>
            </div>
            <div className="mt-4 grid gap-3 text-xs text-slate-300">
              <div className="flex items-center gap-2">
                <Database className="h-4 w-4 text-cyan-200" />
                <span>Broker: {status?.brokers ?? "—"}</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-cyan-200" />
                <span>Topic: {status?.topic ?? "—"}</span>
              </div>
              <div className="flex items-center gap-2">
                <CloudUpload className="h-4 w-4 text-cyan-200" />
                <span>Group: {status?.group_id ?? "—"}</span>
              </div>
            </div>
          </div>
        </div>

          <div className="terminal-panel terminal-glow rounded-3xl p-6">
            <div className="flex items-center justify-between">
              <div className="text-xs uppercase tracking-[0.35em] text-slate-400">
              Manual batch (Neo4j)
              </div>
              <button
                onClick={loadStatus}
                disabled={loading}
              className="rounded-full border border-white/10 px-3 py-1 text-[10px] uppercase tracking-[0.2em] text-slate-300"
            >
              Refresh
            </button>
          </div>
          <textarea
            value={payload}
            onChange={(event) => setPayload(event.target.value)}
            className="mt-4 h-64 w-full rounded-2xl border border-white/10 bg-[#0a1220] p-4 font-mono text-xs text-slate-200 focus:outline-none focus:border-cyan-400/50"
          />
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <button
              onClick={handleSend}
              disabled={sending || !status?.enabled}
              className="rounded-full bg-cyan-400 px-5 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-slate-950 transition disabled:opacity-50"
            >
              {sending ? "Sending..." : "Send batch"}
            </button>
            <span className="text-xs text-slate-400">
              {status?.enabled
                ? "Stores to Neo4j before scoring."
                : "Enable KAFKA_ENABLED=true to ingest."}
            </span>
          </div>
          {success && (
            <div className="mt-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-xs text-emerald-200">
              {success}
            </div>
          )}
          {error && (
            <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-200">
              {error}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
