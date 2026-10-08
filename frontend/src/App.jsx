import { useAuth } from "./context/AuthContext";
import AuthPage from "./pages/AuthPage";
import DashboardPage from "./pages/DashboardPage";

export default function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <p className="p-10 text-center text-slate-500">Loading…</p>;
  }
  return user ? <DashboardPage /> : <AuthPage />;
}
