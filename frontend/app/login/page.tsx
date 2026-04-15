"use client";

import { Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";
import { AppShell } from "@/components/shell";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  const next = searchParams.get("next") || "/host";

  const handleLogin = () => {
    setError("");
    startTransition(async () => {
      const response = await fetch("/api/host-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      if (!response.ok) {
        const data = (await response.json()) as { message?: string };
        setError(data.message || "Ошибка входа");
        return;
      }

      router.push(next);
      router.refresh();
    });
  };

  return (
    <AppShell>
      <main className="mx-auto flex min-h-[70vh] w-full max-w-xl items-center px-6 py-12">
        <div className="w-full rounded-[36px] border border-[var(--border)] bg-white/80 p-8 shadow-[0_20px_80px_rgba(77,54,31,0.08)]">
          <div className="text-xs uppercase tracking-[0.3em] text-stone-500">Host Login</div>
          <h1 className="mt-3 text-4xl font-semibold text-stone-900">Вход в панель ведущего</h1>
          <p className="mt-3 text-sm leading-7 text-stone-600">Панель `/host` закрыта через middleware и cookie. Введите пароль, чтобы открыть список заявок.</p>
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Пароль"
            className="mt-6 w-full rounded-[20px] border border-[var(--border)] bg-[var(--surface)] px-4 py-4 text-sm"
          />
          <button
            type="button"
            onClick={handleLogin}
            disabled={isPending}
            className="mt-4 w-full rounded-full bg-[var(--accent)] px-6 py-4 text-sm font-semibold text-white transition hover:bg-[var(--accent-strong)] disabled:opacity-70"
          >
            {isPending ? "Входим..." : "Войти"}
          </button>
          {error ? <p className="mt-3 text-sm text-red-700">{error}</p> : null}
        </div>
      </main>
    </AppShell>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<AppShell><main className="mx-auto flex min-h-[70vh] w-full max-w-xl items-center px-6 py-12"><div className="w-full rounded-[36px] border border-[var(--border)] bg-white/80 p-8 text-sm text-stone-600">Загрузка формы входа...</div></main></AppShell>}>
      <LoginForm />
    </Suspense>
  );
}
