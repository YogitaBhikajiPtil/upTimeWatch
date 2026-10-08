const STYLES = {
  up: "bg-emerald-100 text-emerald-800",
  down: "bg-red-100 text-red-800",
  unknown: "bg-slate-200 text-slate-700",
  paused: "bg-amber-100 text-amber-800",
};

export default function StatusBadge({ status }) {
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide ${STYLES[status] || STYLES.unknown}`}>
      {status}
    </span>
  );
}
