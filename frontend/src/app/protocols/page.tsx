import Link from "next/link";

export default function ProtocolsPage() {
  return (
    <main className="min-h-screen bg-[var(--background)] text-white px-6 py-16">
      <div className="mx-auto w-full max-w-4xl">
        <div className="text-xs uppercase tracking-[0.35em] text-cyan-200">
          Protocols
        </div>
        <h1 className="mt-4 text-3xl font-semibold text-white">
          Tactical compliance playbooks
        </h1>
        <p className="mt-4 text-sm text-slate-300">
          Escalation rules, audit workflows, and regulator-ready narratives will
          be orchestrated from this node.
        </p>
        <div className="mt-8 terminal-panel rounded-2xl p-6 text-sm text-slate-300">
          <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
            Active protocol
          </div>
          <div className="mt-3 text-lg font-semibold text-white">
            STR-44.A - Layering & Velocity
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Auto-escalate when ring topology confidence &gt; 0.92 or velocity exceeds
            12x baseline.
          </p>
        </div>
        <Link
          className="inline-flex mt-8 rounded-full border border-white/20 px-5 py-2 text-xs uppercase tracking-[0.3em] text-white/80"
          href="/dashboard"
        >
          Open investigator canvas
        </Link>
      </div>
    </main>
  );
}
