import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function AuthForm() {
  const { authenticate } = useAuth();
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await authenticate(mode, email, password);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const isLogin = mode === "login";
  const input =
    "mt-1 w-full rounded-md border border-slate-300 px-3 py-2 focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600";

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold">{isLogin ? "Log in" : "Create your account"}</h2>

      <label className="block text-sm font-medium">
        Email
        <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className={input} />
      </label>

      <label className="block text-sm font-medium">
        Password
        <input
          type="password"
          required
          minLength={8}
          maxLength={64}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={input}
        />
        {!isLogin && <span className="mt-1 block text-xs font-normal text-slate-500">8–64 characters</span>}
      </label>

      {error && <p className="text-sm text-red-600">{error}</p>}

      <button
        type="submit"
        disabled={busy}
        className="w-full rounded-md bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800 disabled:opacity-60"
      >
        {busy ? "Please wait…" : isLogin ? "Log in" : "Sign up"}
      </button>

      <p className="text-center text-sm text-slate-600">
        {isLogin ? "New here?" : "Already have an account?"}{" "}
        <button
          type="button"
          onClick={() => { setMode(isLogin ? "register" : "login"); setError(""); }}
          className="font-medium text-emerald-700 hover:underline"
        >
          {isLogin ? "Create an account" : "Log in"}
        </button>
      </p>
    </form>
  );
}
