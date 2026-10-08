// A small dependency-free SVG line chart of response times (oldest -> newest)
export default function ResponseChart({ results }) {
  const points = [...results].reverse(); // API returns newest first
  if (points.length < 2) {
    return <p className="text-sm text-slate-500">Not enough data for a chart yet.</p>;
  }

  const W = 600, H = 120, PAD = 6;
  const values = points.map((p) => p.response_ms ?? 0);
  const max = Math.max(...values, 1);
  const x = (i) => PAD + (i / (points.length - 1)) * (W - PAD * 2);
  const y = (v) => H - PAD - (v / max) * (H - PAD * 2);
  const line = points.map((p, i) => `${x(i)},${y(p.response_ms ?? 0)}`).join(" ");

  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-slate-500">
        <span>Response time (ms)</span>
        <span>max {max} ms</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="h-28 w-full rounded-md bg-slate-50">
        <polyline points={line} fill="none" stroke="#047857" strokeWidth="2" strokeLinejoin="round" />
        {points.map((p, i) =>
          p.is_up ? null : <circle key={p.id} cx={x(i)} cy={y(0)} r="4" fill="#dc2626" />
        )}
      </svg>
      <p className="mt-1 text-xs text-slate-500">Red dots are failed checks.</p>
    </div>
  );
}
