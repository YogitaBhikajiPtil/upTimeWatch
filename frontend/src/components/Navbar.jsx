import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-emerald-500" />
          <span className="text-lg font-semibold tracking-tight">UptimeWatch</span>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="hidden text-slate-500 sm:inline">{user?.email}</span>
          <button
            onClick={logout}
            className="rounded-md border border-slate-300 px-3 py-1.5 font-medium hover:bg-slate-100"
          >
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}
