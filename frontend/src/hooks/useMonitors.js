import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";

const REFRESH_MS = 10000;

export default function useMonitors() {
  const [monitors, setMonitors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    try {
      setMonitors(await api.listMonitors());
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load once, then poll so the dashboard stays live
  useEffect(() => {
    refresh();
    const id = setInterval(refresh, REFRESH_MS);
    return () => clearInterval(id);
  }, [refresh]);

  const addMonitor = async (data) => {
    await api.createMonitor(data);
    await refresh();
  };
  const toggleMonitor = async (m) => {
    await api.updateMonitor(m.id, { is_active: !m.is_active });
    await refresh();
  };
  const removeMonitor = async (id) => {
    await api.deleteMonitor(id);
    await refresh();
  };
  const checkNow = async (id) => {
    await api.checkNow(id);
    await refresh();
  };

  return { monitors, loading, error, addMonitor, toggleMonitor, removeMonitor, checkNow };
}
