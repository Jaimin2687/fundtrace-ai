import Link from "next/link";

export default function ArchivePage() {
  return (
    <main className="min-h-screen bg-[var(--background)] text-white px-6 py-16">
      <div className="mx-auto w-full max-w-4xl">
        <div className="text-xs uppercase tracking-[0.35em] text-cyan-200">
          Archive
        </div>
        <h1 className="mt-4 text-3xl font-semibold text-white">
          Historical evidence vault
        </h1>
        <p className="mt-4 text-sm text-slate-300">
          Investigations, case exports, and regulator packages are retained here
          with immutable audit links.
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          <div className="terminal-panel rounded-2xl p-5">
            <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
              Last export
            </div>
            <div className="mt-2 text-lg font-semibold text-white">Case #8821-X</div>
            <div className="mt-1 text-xs text-slate-400">
              Generated 00:14:22 ago · FIU-IND ready
            </div>
          </div>
          <div className="terminal-panel rounded-2xl p-5">
            <div className="text-xs uppercase tracking-[0.3em] text-slate-400">
              Chain archive
            </div>
            <div className="mt-2 text-lg font-semibold text-white">1,402 alerts</div>
            <div className="mt-1 text-xs text-slate-400">
              Stored with zero-trust checksum
            </div>
          </div>
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
