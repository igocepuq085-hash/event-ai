"use client";

import { useState } from "react";

export default function LoginPage() {
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch("/api/host-login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.error || "Неверный пароль");
      }

      window.location.href = "/host";
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : "Ошибка входа";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#07070b] px-4 text-white">
      <div className="w-full max-w-md rounded-[32px] border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
        <div className="inline-flex rounded-full border border-white/15 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.24em] text-white/60">
          Host Access
        </div>

        <h1 className="mt-5 text-3xl font-semibold tracking-tight">
          Вход в панель ведущего
        </h1>

        <p className="mt-3 text-sm leading-7 text-white/60">
          Введи пароль, чтобы открыть защищенную панель с заявками.
        </p>

        <div className="mt-6">
          <div className="mb-2 text-sm text-white/80">Пароль</div>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white outline-none placeholder:text-white/30 focus:border-white/30"
            placeholder="Введите пароль"
          />
        </div>

        {error ? (
          <div className="mt-4 rounded-2xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {error}
          </div>
        ) : null}

        <button
          type="button"
          onClick={handleLogin}
          disabled={loading}
          className="mt-6 w-full rounded-full bg-white px-5 py-3 text-sm font-medium text-neutral-950 transition hover:scale-[1.02] disabled:opacity-60"
        >
          {loading ? "Вход..." : "Войти"}
        </button>
      </div>
    </main>
  );
}