import { useState } from "react";

const INTERVALS = [
  { label: "Every 30 seconds", value: 30 },
  { label: "Every minute", value: 60 },
  { label: "Every 5 minutes", value: 300 },
  { label: "Every 15 minutes", value: 900 },
];

export default function MonitorForm({ onAdd }) {
  const [name, setName] = useState("");
  const [url, setUrl] = useState("");
  const [interval, setInterval] = useState(60);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await onAdd({ name, url, interval_seconds: Number(interval) });
      setName("");
      setUrl("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const field = "rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600";

  return (
    <form onSubmit={handleSubmit} className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-2 md:flex-row">
        <input className={`${field} md:w-44`} placeholder="Name" required value={name} onChange={(e) => setName(e.target.value)} />
        <input className={`${field} flex-1`} placeholder="https://example.com" required value={url} onChange={(e) => setUrl(e.target.value)} />
        <select className={field} value={interval} onChange={(e) => setInterval(e.target.value)}>
          {INTERVALS.map((i) => (
            <option key={i.value} value={i.value}>{i.label}</option>
          ))}
        </select>
        <button disabled={busy} className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-60">
          {busy ? "Adding…" : "Add monitor"}
        </button>
      </div>
      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
    </form>
  );
}
