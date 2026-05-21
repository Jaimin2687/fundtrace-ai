"use client";

import React, { ReactNode, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { LayoutDashboard, Menu, Network, ShieldCheck, X } from "lucide-react";

interface DashboardLayoutProps {
  left: ReactNode;
  center: ReactNode;
  right?: ReactNode;
  top?: ReactNode;
  rightOpen?: boolean;
  onToggleRight?: () => void;
}

export default function DashboardLayout({
  left,
  center,
  right,
  top,
  rightOpen = true,
  onToggleRight,
}: DashboardLayoutProps) {
  const pathname = usePathname();
  const [navOpen, setNavOpen] = useState(false);

  const navItems = [
    { href: "/dashboard", label: "Live Canvas", icon: LayoutDashboard },
    { href: "/network", label: "Network Lab", icon: Network },
  ];

  const renderNavLink = (href: string, label: string, Icon: typeof LayoutDashboard) => {
    const active = pathname === href;
    return (
      <Link
        key={href}
        href={href}
        onClick={() => setNavOpen(false)}
        className={`flex items-center gap-3 rounded-xl border px-4 py-3 text-sm transition ${
          active
            ? "border-cyan-400/30 bg-cyan-400/10 text-white"
            : "border-transparent text-slate-300 hover:border-white/10 hover:bg-white/5"
        }`}
      >
        <Icon className={`h-4 w-4 ${active ? "text-cyan-300" : "text-slate-400"}`} />
        {label}
      </Link>
    );
  };

  return (
    <div className="flex h-full w-full min-h-0 bg-[var(--background)] text-white overflow-hidden">
      <AnimatePresence>
        {navOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/60 xl:hidden"
            onClick={() => setNavOpen(false)}
          >
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: "spring", stiffness: 220, damping: 24 }}
              className="h-full w-72 bg-[rgba(7,11,18,0.95)] backdrop-blur-md border-r border-white/10"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="flex items-center justify-between p-6">
                <div>
                  <div className="text-xs uppercase tracking-[0.35em] text-cyan-200">
                    FundTrace AI
                  </div>
                  <p className="mt-2 text-sm text-slate-400">
                    Investigator command deck
                  </p>
                </div>
                <button
                  onClick={() => setNavOpen(false)}
                  className="rounded-full border border-white/10 p-2 text-slate-200"
                  aria-label="Close navigation"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <nav className="space-y-2 px-4">
                {navItems.map((item) =>
                  renderNavLink(item.href, item.label, item.icon)
                )}
              </nav>
              <div className="mt-auto p-6">
                <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-emerald-200">
                    <ShieldCheck className="h-4 w-4" />
                    FIU-IND Ready
                  </div>
                  <p className="mt-2 text-xs text-emerald-100/70">
                    Evidence pack templated for compliance export.
                  </p>
                </div>
              </div>
            </motion.aside>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.aside
        initial={{ x: -40, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ duration: 0.4 }}
        className="hidden w-72 flex-shrink-0 border-r border-white/10 bg-[rgba(7,11,18,0.95)] backdrop-blur-md xl:sticky xl:top-0 xl:flex xl:h-full xl:flex-col xl:overflow-y-auto"
      >
        <div className="p-6">
          <div className="text-xs uppercase tracking-[0.35em] text-cyan-200">
            FundTrace AI
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Investigator command deck
          </p>
        </div>

        <nav className="space-y-2 px-4">
          {navItems.map((item) => renderNavLink(item.href, item.label, item.icon))}
        </nav>

        <div className="mt-auto p-6">
          <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4">
            <div className="flex items-center gap-2 text-sm font-medium text-emerald-200">
              <ShieldCheck className="h-4 w-4" />
              FIU-IND Ready
            </div>
            <p className="mt-2 text-xs text-emerald-100/70">
              Evidence pack templated for compliance export.
            </p>
          </div>
        </div>
      </motion.aside>

      <div className="flex flex-1 flex-col min-h-0">
        {top && (
          <div className="relative flex-shrink-0 max-h-[45vh] overflow-y-auto border-b border-white/10 bg-[rgba(7,11,18,0.7)] backdrop-blur-md">
            <button
              onClick={() => setNavOpen(true)}
              className="absolute left-4 top-5 rounded-full border border-white/10 bg-[#0b1220] p-2 text-slate-200 xl:hidden"
              aria-label="Open navigation"
            >
              <Menu className="h-4 w-4" />
            </button>
            <div className="pl-12 xl:pl-0">{top}</div>
          </div>
        )}

        <div className="flex flex-1 min-h-0 overflow-hidden">
          <div className="flex w-full max-w-xs min-h-0 flex-shrink-0 flex-col overflow-hidden border-r border-white/10">
            {left}
          </div>

          <div className="relative flex-1 min-h-0 overflow-hidden">{center}</div>

          {right && (
            <motion.aside
              initial={{ x: 40, opacity: 0 }}
              animate={{ x: rightOpen ? 0 : 340, opacity: rightOpen ? 1 : 0 }}
              transition={{ duration: 0.35 }}
              className={`hidden w-[360px] flex-shrink-0 border-l border-white/10 bg-[rgba(7,11,18,0.95)] backdrop-blur-md lg:block`}
            >
              <div className="h-full">{right}</div>
            </motion.aside>
          )}
        </div>

        {right && onToggleRight && (
          <button
            onClick={onToggleRight}
            className="fixed bottom-6 right-6 z-50 rounded-full border border-white/20 bg-[#111b33] px-4 py-2 text-xs uppercase tracking-[0.3em] text-white/80 shadow-lg transition hover:border-cyan-400/50"
          >
            {rightOpen ? "Hide intel" : "Show intel"}
          </button>
        )}
      </div>
    </div>
  );
}
