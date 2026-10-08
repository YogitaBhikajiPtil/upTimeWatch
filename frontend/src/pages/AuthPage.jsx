import AuthForm from "../components/AuthForm";

export default function AuthPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 px-4">
      <div className="text-center">
        <h1 className="text-3xl font-semibold tracking-tight">UptimeWatch</h1>
        <p className="mt-1 text-slate-600">Know when your website goes down, before your users do.</p>
      </div>
      <AuthForm />
    </main>
  );
}
