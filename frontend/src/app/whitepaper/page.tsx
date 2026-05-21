import Link from "next/link";

export default function WhitepaperPage() {
  return (
    <main className="min-h-screen bg-[var(--background)] text-white px-6 py-16">
      <div className="mx-auto w-full max-w-4xl">
        <div className="text-xs uppercase tracking-[0.35em] text-cyan-200">
          Whitepaper
        </div>
        <h1 className="mt-4 text-3xl font-semibold text-white">
          Architecture and validation report
        </h1>
        <p className="mt-4 text-sm text-slate-300">
          Deep technical notes, model validation metrics, and audit pipeline
          documentation will be published here.
        </p>
        <div className="mt-8 terminal-panel rounded-2xl p-6 text-sm text-slate-300">
          <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
            Draft status
          </div>
          <div className="mt-3 text-lg font-semibold text-white">Version 0.9</div>
          <p className="mt-2 text-xs text-slate-400">
            Review in progress. Distribution authorized for compliance teams only.
          </p>
        </div>
        <Link
          className="inline-flex mt-8 rounded-full border border-white/20 px-5 py-2 text-xs uppercase tracking-[0.3em] text-white/80"
          href="/"
        >
          Return to terminal
        </Link>
      </div>
    </main>
  );
}
