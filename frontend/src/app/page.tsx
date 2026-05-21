import Link from "next/link";
import { ArrowUpRight, Lock, ShieldCheck, Wand2 } from "lucide-react";
import AnimatedHero from "@/components/AnimatedHero";
import BankIngestTerminal from "@/components/BankIngestTerminal";

const canvasSignals = [
  "Circular flow detection within 5 hops",
  "Counterparty clustering with velocity flags",
  "Explainable narratives with audit trails",
  "Evidence export aligned to FIU-IND",
];

const zeroTrust = [
  {
    title: "YubiKey hardware verification",
    detail: "Session bound to physical device + biometric step-up.",
    icon: Lock,
  },
  {
    title: "Enterprise SSO integration",
    detail: "Azure AD, Okta, and Google Workspace ready.",
    icon: ShieldCheck,
  },
  {
    title: "Automated narrative synthesis",
    detail: "Compliance copy drafted with deterministic evidence links.",
    icon: Wand2,
  },
];

export default function Home() {
  return (
    <main className="flex-1 overflow-y-auto text-white">
      <AnimatedHero />

      <BankIngestTerminal />

      <section className="mx-auto w-full max-w-7xl px-6 py-16">
        <div className="grid gap-10 lg:grid-cols-[1.1fr,0.9fr] lg:items-center">
          <div>
            <div className="text-xs uppercase tracking-[0.35em] text-cyan-200">
              Investigator canvas
            </div>
            <h2 className="mt-4 text-3xl font-semibold text-white sm:text-4xl">
              Trace funds through nested shells in minutes.
            </h2>
            <p className="mt-4 text-sm text-slate-300">
              Live alerts stream in, the topology canvas resolves cross-ledger
              pathways, and the evidence pack drafts your regulatory narrative
              automatically.
            </p>
            <div className="mt-6 flex flex-wrap gap-4">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-full bg-cyan-400 px-6 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-950 shadow-[0_0_25px_rgba(34,211,238,0.4)]"
              >
                Launch canvas
                <ArrowUpRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
          <div className="terminal-panel terminal-glow rounded-3xl p-6">
            <div className="text-xs uppercase tracking-[0.35em] text-slate-400">
              Canvas signals
            </div>
            <ul className="mt-5 space-y-3 text-sm text-slate-200">
              {canvasSignals.map((signal) => (
                <li key={signal} className="flex items-center gap-3">
                  <span className="h-1.5 w-1.5 rounded-full bg-cyan-300" />
                  {signal}
                </li>
              ))}
            </ul>
            <div className="mt-6 rounded-2xl border border-white/10 bg-white/5 p-4 text-xs uppercase tracking-[0.2em] text-slate-400">
              Evidence pack status: <span className="text-emerald-300">Ready</span>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-white/10 bg-[#0b1220]">
        <div className="mx-auto w-full max-w-7xl px-6 py-16">
          <div className="text-xs uppercase tracking-[0.35em] text-cyan-200">
            Secured by zero-trust architecture
          </div>
          <h2 className="mt-4 text-3xl font-semibold text-white">Enterprise gateway layers.</h2>
          <div className="mt-10 grid gap-6 md:grid-cols-3">
            {zeroTrust.map((item) => (
              <div
                key={item.title}
                className="rounded-2xl border border-white/10 bg-white/5 p-6"
              >
                <item.icon className="h-5 w-5 text-cyan-200" />
                <h3 className="mt-4 text-lg font-semibold text-white">{item.title}</h3>
                <p className="mt-2 text-sm text-slate-300">{item.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-white/10">
        <div className="mx-auto flex w-full max-w-7xl flex-col items-start justify-between gap-8 px-6 py-16 md:flex-row md:items-center">
          <div>
            <div className="text-xs uppercase tracking-[0.35em] text-slate-400">
              Additional nodes
            </div>
            <h2 className="mt-3 text-2xl font-semibold text-white">
              Explore the full investigation stack.
            </h2>
          </div>
          <div className="flex flex-wrap gap-3 text-xs uppercase tracking-[0.2em] text-slate-300">
            <Link className="rounded-full border border-white/20 px-4 py-2" href="/network">
              Network lab
            </Link>
            <Link className="rounded-full border border-white/20 px-4 py-2" href="/protocols">
              Protocols
            </Link>
            <Link className="rounded-full border border-white/20 px-4 py-2" href="/archive">
              Archive
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
