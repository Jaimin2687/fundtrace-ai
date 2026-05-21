import type { Metadata } from "next";
import Link from "next/link";
import {
  ClerkProvider,
  Show,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/nextjs";
import { JetBrains_Mono, Orbitron } from "next/font/google";
import ClientProviders from "@/components/ClientProviders";
import "./globals.css";

const orbitron = Orbitron({
  variable: "--font-orbitron",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const jetbrains = JetBrains_Mono({
  variable: "--font-jetbrains",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "FundTrace AI",
  description: "Precision AML acceleration platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${orbitron.variable} ${jetbrains.variable} dark antialiased`}
    >
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap"
        />
      </head>
      <body className="h-dvh flex flex-col bg-[var(--background)] text-[var(--foreground)]">
        <ClerkProvider>
          <header className="flex-shrink-0 z-50 w-full border-b border-white/10 bg-[#070b12]/80 backdrop-blur-lg">
            <div className="mx-auto flex w-full items-center justify-between px-6 py-3">
              <div className="flex items-center gap-6">
                <Link href="/" className="flex flex-col">
                  <span className="text-xs uppercase tracking-[0.4em] text-cyan-200 font-medium">
                    FundTrace AI
                  </span>
                  <span className="text-[10px] text-slate-500">
                    Secure intelligence terminal
                  </span>
                </Link>
                <nav className="hidden items-center gap-1 md:flex">
                  {[
                    { href: '/', label: 'Terminal' },
                    { href: '/dashboard', label: 'Canvas' },
                    { href: '/network', label: 'Network' },
                    { href: '/protocols', label: 'Protocols' },
                  ].map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="rounded-lg px-3 py-1.5 text-[11px] uppercase tracking-[0.2em] text-slate-400 transition hover:bg-white/5 hover:text-cyan-200"
                    >
                      {item.label}
                    </Link>
                  ))}
                </nav>
              </div>
              <div className="flex items-center gap-3 text-xs uppercase tracking-[0.25em]">
                <Show when="signed-out">
                  <SignInButton>
                    <button className="rounded-full border border-cyan-400/40 bg-cyan-400/10 px-4 py-1.5 text-[11px] text-cyan-100 transition hover:border-cyan-300">
                      Request access
                    </button>
                  </SignInButton>
                  <SignUpButton>
                    <button className="rounded-full bg-amber-400 px-4 py-1.5 text-[11px] font-semibold text-slate-950 shadow-[0_0_20px_rgba(251,191,36,0.4)] transition hover:translate-y-[-1px]">
                      Create node
                    </button>
                  </SignUpButton>
                </Show>
                <Show when="signed-in">
                  <UserButton />
                </Show>
              </div>
            </div>
          </header>
          <div className="scanline" aria-hidden="true" />
          <main className="flex flex-1 overflow-hidden min-h-0 w-full relative">
            <ClientProviders>
              {children}
            </ClientProviders>
          </main>
        </ClerkProvider>
      </body>
    </html>
  );
}
