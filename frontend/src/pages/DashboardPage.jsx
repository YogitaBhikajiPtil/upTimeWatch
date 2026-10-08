import Navbar from "../components/Navbar";
import SummaryBar from "../components/SummaryBar";
import MonitorForm from "../components/MonitorForm";
import MonitorCard from "../components/MonitorCard";
import useMonitors from "../hooks/useMonitors";

export default function DashboardPage() {
  const { monitors, loading, error, addMonitor, toggleMonitor, removeMonitor, checkNow } = useMonitors();

  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-5xl space-y-5 px-4 py-6">
        <SummaryBar monitors={monitors} />
        <MonitorForm onAdd={addMonitor} />

        {error && <p className="text-sm text-red-600">{error}</p>}

        {loading ? (
          <p className="text-slate-500">Loading monitors…</p>
        ) : monitors.length === 0 ? (
          <p className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-500">
            No monitors yet. Add a website above to start tracking it.
          </p>
        ) : (
          <ul className="space-y-3">
            {monitors.map((m) => (
              <MonitorCard
                key={m.id}
                monitor={m}
                onToggle={toggleMonitor}
                onDelete={removeMonitor}
                onCheckNow={checkNow}
              />
            ))}
          </ul>
        )}
      </main>
    </>
  );
}
