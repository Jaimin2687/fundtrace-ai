"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import { ArrowUpRight, Network, Radar, ShieldCheck } from "lucide-react";
import HeroNetworkCanvas from "@/components/HeroNetworkCanvas";

const modules = [
  {
    title: "Global Triage",
    descriptor: "Latency <0.8s",
    detail:
      "Real-time ML alerts with sub-second latency. Prioritize the highest-risk nodes instantly.",
    icon: Radar,
  },
  {
    title: "Network Topology",
    descriptor: "Render: WebGL 2.0",
    detail:
      "Visual money tracing across layered rails. Identify rings, shells, and bursts within seconds.",
    icon: Network,
  },
  {
    title: "Regulatory Export",
    descriptor: "Compliance: AML/KYC",
    detail:
      "Automated FIU-IND narrative packs with cryptographic audit trails and chain-of-custody.",
    icon: ShieldCheck,
  },
];

const terminalLines = [
  "14:02:44.102 > SESSION_INIT",
  "14:02:44.150 > ENFORCING_MFA_POLICY [STRICT]",
  "14:02:44.201 > SYSTEM_READY_FOR_INPUT",
  "14:02:45.020 > STREAM_FEED CONNECTED",
  "14:02:45.418 > ALERT_CLUSTER IDENTIFIED",
];

export default function AnimatedHero() {
  const reduceMotion = useReducedMotion();

  return (
    <section className="relative overflow-hidden border-b border-white/10">
      <HeroNetworkCanvas />
      <div className="absolute inset-0 terminal-noise" aria-hidden="true" />
      <div className="absolute inset-0 bg-gradient-to-b from-[rgba(10,16,32,0.95)] via-[rgba(7,11,18,0.85)] to-[rgba(5,8,15,1)]" />

      <div className="relative mx-auto w-full max-w-7xl px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: reduceMotion ? 0 : 0.6 }}
          className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[11px] uppercase tracking-[0.35em] text-cyan-200 terminal-chip"
        >
          Live threat feed active
          <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
        </motion.div>

        <div className="mt-10 grid gap-12 lg:grid-cols-[1.1fr,0.9fr] lg:items-center">
          <div>
            <motion.h1
              initial={{ opacity: 0, y: 22 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: reduceMotion ? 0 : 0.7, delay: 0.05 }}
              className="font-headline text-4xl uppercase tracking-[0.08em] text-white sm:text-5xl lg:text-6xl"
            >
              The End of Financial Anonymity.
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: reduceMotion ? 0 : 0.6, delay: 0.15 }}
              className="mt-6 max-w-2xl text-sm text-slate-300 sm:text-base"
            >
              High-speed visual workflows for Tier-1 AML investigations. Trace money
              movement through complex networks in real time, with explainable,
              export-ready evidence trails.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: reduceMotion ? 0 : 0.6, delay: 0.25 }}
              className="mt-8 flex flex-wrap items-center gap-4"
            >
              <Link
                href="/sign-in"
                className="group inline-flex items-center gap-2 rounded-full bg-amber-400 px-6 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-950 shadow-[0_0_30px_rgba(251,191,36,0.35)] transition-all hover:bg-amber-300 hover:shadow-[0_0_40px_rgba(251,191,36,0.6)] hover:translate-y-[-2px]"
              >
                Request access
                <ArrowUpRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
              </Link>
              <Link
                href="/whitepaper"
                className="inline-flex items-center gap-2 rounded-full border border-white/20 px-6 py-3 text-xs font-semibold uppercase tracking-[0.2em] text-white/80 transition-all hover:border-cyan-400 hover:text-cyan-400 hover:shadow-[0_0_20px_rgba(34,211,238,0.3)]"
              >
                View protocol
              </Link>
            </motion.div>
            <div className="mt-8 flex flex-wrap gap-4 text-[11px] uppercase tracking-[0.3em] text-slate-400">
              <span>Latency &lt;0.8s</span>
              <span>Render: WebGL 2.0</span>
              <span>Compliance: AML/KYC</span>
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: reduceMotion ? 0 : 0.7, delay: 0.2 }}
            className="terminal-panel rounded-3xl p-6"
          >
            <div className="flex items-center justify-between text-[11px] uppercase tracking-[0.3em] text-slate-400">
              <span>[ Terminal View Activated ]</span>
              <span className="text-cyan-200">Node://investigator</span>
            </div>
            <div className="mt-4 space-y-2 font-mono text-[11px] text-slate-300">
              {terminalLines.map((line) => (
                <div key={line} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-cyan-300/70" />
                  <span>{line}</span>
                </div>
              ))}
            </div>
            <div className="mt-6 grid grid-cols-2 gap-3 text-[11px] uppercase tracking-[0.2em] text-slate-400">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                Threat density
                <div className="mt-2 text-xl font-semibold text-white">94.2%</div>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                Active sessions
                <div className="mt-2 text-xl font-semibold text-white">18</div>
              </div>
            </div>
          </motion.div>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {modules.map((module, index) => (
            <motion.div
              key={module.title}
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: reduceMotion ? 0 : 0.6, delay: 0.3 + index * 0.15 }}
              whileHover={{ y: -4, scale: 1.02 }}
              className="group glass-panel rounded-2xl p-6 transition-all hover:border-cyan-400/50 hover:shadow-[0_0_30px_rgba(34,211,238,0.2)]"
            >
              <module.icon className="h-5 w-5 text-cyan-200" />
              <div className="mt-4 text-xs uppercase tracking-[0.3em] text-slate-400">
                {module.descriptor}
              </div>
              <h3 className="mt-3 text-lg font-semibold text-white">{module.title}</h3>
              <p className="mt-3 text-sm text-slate-300">{module.detail}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
