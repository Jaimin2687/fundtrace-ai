"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

const LANDING_HTML = `<div class="scanline"></div>
<!-- TopAppBar -->
<header class="fixed top-0 w-full z-50 flex justify-between items-center px-4 h-12 bg-slate-950/80 backdrop-blur-sm border-b border-slate-800">
<div class="flex items-center gap-3">
<span class="material-symbols-outlined text-cyan-400" data-icon="terminal">terminal</span>
<h1 class="text-cyan-400 font-['Space_Grotesk'] font-black tracking-tighter text-lg uppercase">FUNDTRACE AI // TERMINAL_V.4.0</h1>
</div>
<nav class="hidden md:flex gap-8 items-center">
<a class="font-['Space_Grotesk'] text-cyan-400 font-bold uppercase tracking-widest text-[10px] hover:bg-cyan-400/10 transition-none" href="#">PROTOCOLS</a>
<a class="font-['Space_Grotesk'] text-slate-500 uppercase tracking-widest text-[10px] hover:text-cyan-300 transition-none" href="#">ARCHIVE</a>
<a class="font-['Space_Grotesk'] text-slate-500 uppercase tracking-widest text-[10px] hover:text-cyan-300 transition-none" href="#">NETWORK_STATUS</a>
</nav>
<button class="bg-primary-container text-black font-['Space_Grotesk'] font-bold uppercase tracking-widest text-[10px] px-4 py-2 glow-cyan cursor-crosshair active:bg-cyan-500 transition-none">
            LAUNCH INVESTIGATOR CANVAS
        </button>
</header>
<main class="relative pt-12 min-h-screen">
<!-- Hero Section with Full-bleed Background -->
<section class="relative h-[751px] flex flex-col justify-center items-center text-center px-6 overflow-hidden border-b border-slate-800">
<div class="absolute inset-0 z-0">
<img class="w-full h-full object-cover opacity-40 mix-blend-screen" data-alt="A cinematic, high-contrast visualization of a complex financial node network with glowing cyan data points connected by razor-thin geometric lines against a deep navy blue background. The aesthetic is tactical and futuristic, reminiscent of a cyber-security command center HUD, with subtle digital distortion and a cold, clinical lighting scheme that highlights the structural density of the network." src="https://lh3.googleusercontent.com/aida-public/AB6AXuAMxXuYsMTJHIS4VMaCyDLVgxY1CRaVPKydBzyqyw1BxiTAViq2vwwUL56my2aJ1T2DHDSCnvKBmE3kgLYK4p6fi78LxdAo3q6Zs4Lnl-RXvz7KTlspsCZARHaNLAi-WyFv0gp6lEPRLKMptiKhwGDAY0Q9ggWG49GUDPSU5U63siM5yeD2izjqb6DKJjQbjSJXZN4mf0pQOBjIP75cUIOvX2w-mL_YJFIRtx0Prc-b-1cbHsFIGhzDqPOtLXKEU63viVIznyOvB2iH"/>
<div class="absolute inset-0 bg-gradient-to-b from-[#0A0F1C] via-transparent to-[#0A0F1C]"></div>
<div class="absolute inset-0 grid-overlay opacity-20"></div>
</div>
<div class="relative z-20 max-w-5xl space-y-6">
<div class="inline-flex items-center gap-2 px-3 py-1 bg-slate-900 border border-cyan-400/30">
<span class="w-2 h-2 bg-cyan-400 cyan-pulse"></span>
<span class="font-['Space_Mono'] text-[10px] text-cyan-400 tracking-widest uppercase">LIVE THREAT STREAM ACTIVE // NODE_882</span>
</div>
<h2 class="font-display-xl text-display-xl text-on-surface uppercase max-w-3xl mx-auto leading-[0.95] tracking-tighter">
                    TRACE MONEY IN <span class="text-primary-container">MINUTES</span>
</h2>
<p class="font-body-md text-body-md text-on-surface-variant max-w-xl mx-auto">
                    The ultimate forensic AI substrate for institutional intelligence. Map illicit flows across fragmented global networks with military-grade precision and sub-millisecond response.
                </p>
<div class="flex flex-col sm:flex-row gap-4 justify-center pt-8">
<button class="bg-primary-container text-black font-['Space_Grotesk'] font-extrabold uppercase tracking-widest text-xs px-8 py-4 glow-cyan">
                        INITIALIZE DEEP_SCAN
                    </button>
<button class="border border-slate-700 bg-slate-950/50 text-on-surface font-['Space_Grotesk'] font-bold uppercase tracking-widest text-xs px-8 py-4 hover:border-cyan-400/50">
                        ACCESS WHITE_PAPER.PDF
                    </button>
</div>
</div>
</section>
<!-- KPI Strip -->
<section class="grid grid-cols-1 md:grid-cols-3 bg-black border-b border-slate-800">
<div class="p-8 border-r border-slate-800 flex flex-col items-center justify-center space-y-2">
<span class="font-['Space_Grotesk'] text-[11px] text-slate-500 uppercase tracking-widest">Global Intelligence Hub</span>
<div class="font-['Space_Mono'] text-4xl text-cyan-400 font-bold">4.2B ENTITIES</div>
<div class="w-12 h-1 bg-cyan-400/20"></div>
</div>
<div class="p-8 border-r border-slate-800 flex flex-col items-center justify-center space-y-2">
<span class="font-['Space_Grotesk'] text-[11px] text-slate-500 uppercase tracking-widest">Network Response Time</span>
<div class="font-['Space_Mono'] text-4xl text-cyan-400 font-bold">12ms LATENCY</div>
<div class="w-12 h-1 bg-cyan-400/20"></div>
</div>
<div class="p-8 flex flex-col items-center justify-center space-y-2">
<span class="font-['Space_Grotesk'] text-[11px] text-slate-500 uppercase tracking-widest">Active Alerts Detected</span>
<div class="font-['Space_Mono'] text-4xl text-crimson-alert font-bold">1,402 CLUSTERS</div>
<div class="w-12 h-1 bg-crimson-alert/20"></div>
</div>
</section>
<!-- Core Capabilities -->
<section class="p-12 md:p-24 space-y-12 bg-[#0A0F1C] grid-overlay">
<div class="flex flex-col md:flex-row justify-between items-end gap-6">
<div class="space-y-4">
<span class="font-['Space_Mono'] text-cyan-400 text-xs">// CAPABILITIES_MANIFEST_V.4</span>
<h3 class="font-headline-lg text-headline-lg text-on-surface uppercase">FORENSIC SURVEILLANCE MODULES</h3>
</div>
<div class="h-px flex-grow bg-slate-800 mx-8 hidden md:block"></div>
<div class="font-['Space_Mono'] text-slate-600 text-[10px] text-right">SYSTEM_STABILITY: 99.998%<br/>DATA_THROUGHPUT: 1.2TB/S</div>
</div>
<div class="grid grid-cols-1 md:grid-cols-3 gap-0 border border-slate-800">
<!-- Card 1 -->
<div class="p-10 bg-slate-950/40 border-r border-slate-800 hover:bg-cyan-400/[0.03] transition-colors group">
<span class="material-symbols-outlined text-cyan-400 text-4xl mb-6 block" data-icon="hub">hub</span>
<h4 class="font-['Space_Grotesk'] text-xl font-bold text-on-surface uppercase mb-4">NODE MAPPING</h4>
<p class="text-on-surface-variant text-sm leading-relaxed mb-8">
                        Visualizing multi-hop transactional paths across 400+ jurisdictions. Proprietary graph algorithms reveal hidden entity relationships instantly.
                    </p>
<ul class="font-['Space_Mono'] text-[10px] text-cyan-400 space-y-2">
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-cyan-400"></span> RECURSIVE_TRAVERSAL</li>
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-cyan-400"></span> LAYER_2_DESTRUCTION</li>
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-cyan-400"></span> ENTITY_RESOLVER</li>
</ul>
</div>
<!-- Card 2 -->
<div class="p-10 bg-slate-950/40 border-r border-slate-800 hover:bg-cyan-400/[0.03] transition-colors group">
<span class="material-symbols-outlined text-cyan-400 text-4xl mb-6 block" data-icon="analytics">analytics</span>
<h4 class="font-['Space_Grotesk'] text-xl font-bold text-on-surface uppercase mb-4">PATTERN RECOGNITION</h4>
<p class="text-on-surface-variant text-sm leading-relaxed mb-8">
                        AI-driven behavioral profiling that identifies smurfing, structuring, and complex layering cycles before funds can be liquidated.
                    </p>
<ul class="font-['Space_Mono'] text-[10px] text-cyan-400 space-y-2">
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-cyan-400"></span> ML_HEURISTICS</li>
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-cyan-400"></span> CYCLE_DETECTION</li>
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-cyan-400"></span> VELOCITY_METRICS</li>
</ul>
</div>
<!-- Card 3 -->
<div class="p-10 bg-slate-950/40 hover:bg-cyan-400/[0.03] transition-colors group">
<span class="material-symbols-outlined text-crimson-alert text-4xl mb-6 block" data-icon="emergency_home">emergency_home</span>
<h4 class="font-['Space_Grotesk'] text-xl font-bold text-on-surface uppercase mb-4">REAL-TIME ALERTS</h4>
<p class="text-on-surface-variant text-sm leading-relaxed mb-8">
                        Automated triggers configured for high-risk jurisdictions and PEP matches. Instant escalation via secure signal protocols.
                    </p>
<ul class="font-['Space_Mono'] text-[10px] text-crimson-alert space-y-2">
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-crimson-alert"></span> CRITICAL_PULSE</li>
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-crimson-alert"></span> NODE_ISOLATION</li>
<li class="flex items-center gap-2"><span class="w-1 h-1 bg-crimson-alert"></span> SEC_COMPLIANCE_AUTO</li>
</ul>
</div>
</div>
</section>
<!-- Proof Panel (Split Layout) -->
<section class="flex flex-col lg:flex-row border-t border-slate-800 min-h-[600px]">
<!-- Terminal Left -->
<div class="lg:w-3/5 bg-black p-4 relative overflow-hidden flex items-center justify-center">
<div class="w-full h-full max-h-[500px] border border-slate-700 bg-[#0d1117] p-2 relative">
<div class="flex items-center gap-1.5 px-3 py-2 border-b border-slate-800 bg-slate-900">
<div class="w-2.5 h-2.5 bg-slate-700"></div>
<div class="w-2.5 h-2.5 bg-slate-700"></div>
<div class="w-2.5 h-2.5 bg-slate-700"></div>
<span class="ml-4 font-['Space_Mono'] text-[10px] text-slate-500 uppercase tracking-widest">INVESTIGATOR_TERMINAL // SESSION_4091</span>
</div>
<img class="w-full h-full object-cover opacity-60 mix-blend-screen" data-alt="A detailed digital screenshot of a complex software terminal interface showing cascading green and cyan code, live data graphs, and a geometric network diagram. The UI is dense with information, featuring multiple panels of technical logs and financial metrics. The lighting is low and focused on the screen content, creating a professional and high-stakes forensic analysis environment." src="https://lh3.googleusercontent.com/aida-public/AB6AXuBsUXmlHY84gTNYp9KhOHRAybt5A_roeq74zo2jo77zZTONjzpUgNuR2xuG7BCNbNPdf83WVnRbnXBvoW4ouZDnTG9AJYkeq4eSJQTuf698z-PDGqVoqzTEH3mkC1epVWXqFizGdoPW5olNcHIzuAwS-0VbH5AW3d_SH4cwGiONq4G_YNqT8pSZlZd1NA3ZtmUCdgu2cG_TmDHQNHpgFRzAKlyD7Rqb9CKFf2K6Eko8XUDFMcKgM3sl40I_rzAvgKDWKtGqxGje0Z3G"/>
<div class="absolute inset-0 pointer-events-none border-[12px] border-black/50"></div>
</div>
<div class="absolute bottom-10 left-10 p-4 bg-crimson-alert text-black font-['Space_Grotesk'] font-black uppercase text-xs">
                    FRAUD_DETECTED: [CLUSTER_ALPHA_7]
                </div>
</div>
<!-- Text Right -->
<div class="lg:w-2/5 p-12 md:p-20 flex flex-col justify-center space-y-10 border-l border-slate-800 bg-slate-950">
<div class="space-y-4">
<span class="font-['Space_Mono'] text-cyan-400 text-xs">// PERFORMANCE_METADATA</span>
<h3 class="font-headline-lg text-headline-lg text-on-surface uppercase">VALIDATED MISSION OUTCOMES</h3>
</div>
<div class="space-y-8">
<div class="flex items-start gap-4">
<div class="w-10 h-10 border border-cyan-400/30 flex items-center justify-center flex-shrink-0">
<span class="material-symbols-outlined text-cyan-400" data-icon="verified">verified</span>
</div>
<div>
<div class="font-['Space_Mono'] text-xl text-on-surface font-bold">99% REDUCTION</div>
<p class="text-on-surface-variant text-sm">False positive noise filtered via Bayesian neural weighting.</p>
</div>
</div>
<div class="flex items-start gap-4">
<div class="w-10 h-10 border border-cyan-400/30 flex items-center justify-center flex-shrink-0">
<span class="material-symbols-outlined text-cyan-400" data-icon="speed">speed</span>
</div>
<div>
<div class="font-['Space_Mono'] text-xl text-on-surface font-bold">14.2x ACCELERATION</div>
<p class="text-on-surface-variant text-sm">Time-to-insight reduction compared to manual tracing methods.</p>
</div>
</div>
<div class="flex items-start gap-4">
<div class="w-10 h-10 border border-cyan-400/30 flex items-center justify-center flex-shrink-0">
<span class="material-symbols-outlined text-cyan-400" data-icon="shield">shield</span>
</div>
<div>
<div class="font-['Space_Mono'] text-xl text-on-surface font-bold">AML/CTF COMPLIANT</div>
<p class="text-on-surface-variant text-sm">Full regulatory audit trails generated for SEC and FATF filing.</p>
</div>
</div>
</div>
<button class="w-full border border-slate-700 p-4 text-on-surface font-['Space_Grotesk'] font-bold uppercase tracking-widest text-xs hover:bg-cyan-400 hover:text-black transition-none group flex justify-between items-center">
                    REQUEST ENTERPRISE DEMO
                    <span class="material-symbols-outlined text-sm group-hover:translate-x-1 transition-transform" data-icon="arrow_forward">arrow_forward</span>
</button>
</div>
</section>
</main>
<!-- Footer -->
<footer class="w-full py-12 px-6 grid grid-cols-1 md:grid-cols-2 items-center gap-8 bg-black border-t border-slate-800">
<div class="space-y-4">
<div class="text-cyan-500 font-['Space_Grotesk'] font-bold text-lg uppercase tracking-tighter">FUNDTRACE AI</div>
<p class="font-['Space_Mono'] text-[10px] text-slate-600 tracking-tight leading-relaxed max-w-sm uppercase">
                © 2024 FUNDTRACE AI. FOR OFFICIAL USE ONLY. MIL-SPEC SURVEILLANCE PROTOCOL ACTIVE. UNAUTHORIZED ACCESS IS A FEDERAL OFFENSE.
            </p>
<div class="flex gap-4 items-center pt-2">
<span class="px-2 py-1 border border-slate-800 font-['Space_Mono'] text-[8px] text-slate-500">SEC_REG_401</span>
<span class="px-2 py-1 border border-slate-800 font-['Space_Mono'] text-[8px] text-slate-500">GDPR_SOVEREIGN</span>
<span class="px-2 py-1 border border-slate-800 font-['Space_Mono'] text-[8px] text-slate-500">ISO_27001</span>
</div>
</div>
<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
<div class="flex flex-col gap-2">
<span class="font-['Space_Grotesk'] text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">NETWORK</span>
<a class="font-['Space_Mono'] text-[10px] text-slate-600 hover:text-cyan-400 transition-none" href="#">SEC_COMPLIANCE</a>
<a class="font-['Space_Mono'] text-[10px] text-slate-600 hover:text-cyan-400 transition-none" href="#">DATA_SOVEREIGNTY</a>
</div>
<div class="flex flex-col gap-2">
<span class="font-['Space_Grotesk'] text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">ENGINEERING</span>
</div>
</div>
</footer>`;

export default function Page() {
  const router = useRouter();
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    const navRoutes: Record<string, string> = {
      PROTOCOLS: "/protocols",
      ARCHIVE: "/archive",
      NETWORK_STATUS: "/network",
    };

    root.querySelectorAll("a").forEach((anchor) => {
      const label = anchor.textContent?.trim() ?? "";
      if (navRoutes[label]) {
        anchor.setAttribute("href", navRoutes[label]);
      }
    });

    const clickMap: Array<{ text: string; route: string }> = [
      { text: "LAUNCH INVESTIGATOR CANVAS", route: "/dashboard" },
      { text: "INITIALIZE DEEP_SCAN", route: "/dashboard" },
      { text: "ACCESS WHITE_PAPER.PDF", route: "/whitepaper" },
      { text: "REQUEST ENTERPRISE DEMO", route: "/demo" },
    ];

    const handlers: Array<() => void> = [];

    clickMap.forEach(({ text, route }) => {
      const button = Array.from(root.querySelectorAll("button")).find(
        (btn) => btn.textContent?.trim() === text
      );
      if (!button) return;
      const handler = () => router.push(route);
      button.addEventListener("click", handler);
      handlers.push(() => button.removeEventListener("click", handler));
    });

    return () => {
      handlers.forEach((cleanup) => cleanup());
    };
  }, [router]);

  return (
    <div ref={rootRef} dangerouslySetInnerHTML={{ __html: LANDING_HTML }} />
  );
}
