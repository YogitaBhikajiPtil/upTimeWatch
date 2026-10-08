import { useState } from "react";
import { api } from "../api/client";
import ResponseChart from "./ResponseChart";
import StatusBadge from "./StatusBadge";

function timeAgo(iso) {
  if (!iso) return "never";
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000));
  if (seconds < 60) return `${seconds}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

export default function MonitorCard({ monitor, onToggle, onDelete, onCheckNow }) {
  const [open, setOpen] = useState(false);
  const [results, setResults] = useState([]);
  const [checking, setChecking] = useState(false);

  async function toggleHistory() {
    if (!open) setResults(await api.results(monitor.id, 50));
    setOpen(!open);
  }

  async function handleCheckNow() {
    setChecking(true);
    try {
      await onCheckNow(monitor.id);
      if (open) setResults(await api.results(monitor.id, 50));
    } finally {
      setChecking(false);
    }
  }

  const status = monitor.is_active ? monitor.status : "paused";
  const btn = "rounded-md border border-slate-300 px-2.5 py-1 text-xs font-medium hover:bg-slate-100 disabled:opacity-60";

  return (
    <li className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="truncate font-semibold">{monitor.name}</h3>
            <StatusBadge status={status} />
          </div>
          <p className="truncate font-mono text-xs text-slate-500">{monitor.url}</p>
        </div>

        <dl className="flex gap-5 text-sm">
          <div>
            <dt className="text-xs text-slate-500">Uptime 24h</dt>
            <dd className="font-medium">{monitor.uptime_24h === null ? "–" : `${monitor.uptime_24h}%`}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Response</dt>
            <dd className="font-medium">{monitor.last_response_ms === null ? "–" : `${monitor.last_response_ms} ms`}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Checked</dt>
            <dd className="font-medium">{timeAgo(monitor.last_checked_at)}</dd>
          </div>
        </dl>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <button className={btn} onClick={handleCheckNow} disabled={checking}>
          {checking ? "Checking…" : "Check now"}
        </button>
        <button className={btn} onClick={() => onToggle(monitor)}>
          {monitor.is_active ? "Pause" : "Resume"}
        </button>
        <button className={btn} onClick={toggleHistory}>
          {open ? "Hide history" : "History"}
        </button>
        <button className={`${btn} text-red-700`} onClick={() => onDelete(monitor.id)}>
          Delete
        </button>
      </div>

      {open && (
        <div className="mt-4 space-y-3 border-t border-slate-100 pt-4">
          <ResponseChart results={results} />
          <ul className="max-h-40 space-y-1 overflow-y-auto text-xs">
            {results.slice(0, 10).map((r) => (
              <li key={r.id} className="flex justify-between font-mono text-slate-600">
                <span>{new Date(r.checked_at).toLocaleTimeString()}</span>
                <span className={r.is_up ? "text-emerald-700" : "text-red-700"}>
                  {r.is_up ? `${r.status_code} · ${r.response_ms} ms` : r.error || `HTTP ${r.status_code}`}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </li>
  );
}
