function Stat({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-4 py-3">
      <div className="text-xs font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-1 text-2xl font-semibold">{value}</div>
    </div>
  );
}

export default function SummaryBar({ monitors }) {
  const up = monitors.filter((m) => m.is_active && m.status === "up").length;
  const down = monitors.filter((m) => m.is_active && m.status === "down").length;
  const withData = monitors.filter((m) => m.uptime_24h !== null);
  const avg = withData.length
    ? (withData.reduce((sum, m) => sum + m.uptime_24h, 0) / withData.length).toFixed(1) + "%"
    : "–";

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <Stat label="Monitors" value={monitors.length} />
      <Stat label="Up" value={up} />
      <Stat label="Down" value={down} />
      <Stat label="Avg uptime (24h)" value={avg} />
    </div>
  );
}
