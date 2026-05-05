export default function NetworkPage() {
  return (
    <main className="min-h-screen bg-[#0A0F1C] text-[#dce4e3] p-10">
      <h1 className="font-['Space_Grotesk'] text-3xl uppercase text-[#2DE2E6]">Network Status</h1>
      <p className="mt-4 text-sm text-[#859494] font-mono">
        Infrastructure health, ingest latency, and trust zones are surfaced here.
      </p>
      <a className="inline-block mt-8 border border-[#3b494a] px-4 py-2 text-xs tracking-widest" href="/dashboard">
        OPEN LIVE MAP
      </a>
    </main>
  );
}
