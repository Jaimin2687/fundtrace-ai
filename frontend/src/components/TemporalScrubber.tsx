"use client";

import { motion } from "framer-motion";

interface TemporalScrubberProps {
  min: number;
  max: number;
  value: number;
  onChange: (value: number) => void;
}

export default function TemporalScrubber({ min, max, value, onChange }: TemporalScrubberProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-[#0b1220]/90 px-6 py-4 backdrop-blur">
      <div className="flex items-center justify-between text-xs uppercase tracking-[0.3em] text-slate-400">
        <span>Temporal Scrubber</span>
        <span className="text-cyan-200">T+{value}</span>
      </div>
      <div className="mt-4 flex items-center gap-4">
        <span className="text-xs text-slate-500">Start</span>
        <input
          type="range"
          min={min}
          max={max}
          value={value}
          onChange={(event) => onChange(Number(event.target.value))}
          className="flex-1 accent-cyan-400"
        />
        <span className="text-xs text-slate-500">End</span>
      </div>
      <motion.div
        layout
        className="mt-3 h-1 w-full rounded-full bg-gradient-to-r from-cyan-400/30 via-amber-300/30 to-emerald-400/30"
      />
    </div>
  );
}
