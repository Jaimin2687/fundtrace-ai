"use client";

import Link from "next/link";
import { SignUp, SignUpButton } from "@clerk/nextjs";
import { Cloud, KeyRound, ShieldCheck } from "lucide-react";

const ssoOptions = [
  {
    label: "Continue with Google",
    detail: "Workspace or consumer accounts",
    icon: Cloud,
  },
  {
    label: "Register with Azure AD",
    detail: "Enterprise identity provider",
    icon: ShieldCheck,
  },
  {
    label: "Register with Okta",
    detail: "Zero-trust policies enforced",
    icon: KeyRound,
  },
];

export default function SignUpPage() {
  return (
    <main className="min-h-screen bg-[var(--background)] text-white px-6 py-16">
      <div className="mx-auto grid w-full max-w-6xl gap-10 lg:grid-cols-[1.05fr,0.95fr] lg:items-center">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-[11px] uppercase tracking-[0.35em] text-cyan-200 terminal-chip">
            FundTrace AI Access Provisioning
          </div>
          <h1 className="mt-6 font-headline text-3xl uppercase tracking-[0.1em] text-white sm:text-4xl">
            Create investigator credentials
          </h1>
          <p className="mt-4 max-w-lg text-sm text-slate-300">
            Enroll your identity with email or a trusted SSO provider. Multi-factor
            authentication will be enforced at first login.
          </p>

          <div className="mt-8 grid gap-3">
            {ssoOptions.map((option) => (
              <SignUpButton key={option.label}>
                <button className="terminal-panel flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm text-white transition hover:border-cyan-400/40">
                  <div className="flex items-center gap-3">
                    <option.icon className="h-4 w-4 text-cyan-200" />
                    <div>
                      <div className="text-xs uppercase tracking-[0.25em] text-slate-400">
                        {option.label}
                      </div>
                      <div className="mt-1 text-xs text-slate-500">{option.detail}</div>
                    </div>
                  </div>
                  <span className="text-[11px] uppercase tracking-[0.3em] text-cyan-200">
                    Connect
                  </span>
                </button>
              </SignUpButton>
            ))}
          </div>
        </div>

        <div className="terminal-panel rounded-3xl p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <div className="text-xs uppercase tracking-[0.35em] text-slate-400">
                Investigator enrollment
              </div>
              <h2 className="mt-2 text-xl font-semibold text-white">Create account</h2>
            </div>
            <Link href="/" className="text-xs uppercase tracking-[0.3em] text-cyan-200">
              Return to terminal
            </Link>
          </div>
          <SignUp
            routing="path"
            path="/sign-up"
            signInUrl="/sign-in"
            fallbackRedirectUrl="/dashboard"
            appearance={{
              variables: {
                colorPrimary: "#22d3ee",
                colorBackground: "transparent",
                colorText: "#e2e8f0",
                colorTextSecondary: "#94a3b8",
                colorInputBackground: "#0f172a",
                colorInputText: "#e2e8f0",
              },
              elements: {
                card: "bg-transparent shadow-none p-0",
                headerTitle: "text-white",
                headerSubtitle: "text-slate-400",
                socialButtonsBlockButton:
                  "bg-white/5 border border-white/10 text-white hover:border-cyan-400/40",
                formButtonPrimary:
                  "bg-amber-400 text-slate-950 hover:bg-amber-300",
                formFieldInput:
                  "bg-[#0f172a] border border-white/10 text-white focus:border-cyan-400/60",
                footerActionLink: "text-cyan-200",
              },
            }}
          />
        </div>
      </div>
    </main>
  );
}
