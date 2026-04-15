import Link from "next/link";
import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen">
      <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6">
        <Link href="/" className="text-lg font-semibold tracking-[0.12em] uppercase text-stone-800">
          Event AI
        </Link>
        <nav className="flex items-center gap-3 text-sm text-stone-700">
          <Link className="rounded-full border border-[var(--border)] bg-white/60 px-4 py-2 backdrop-blur-sm" href="/questionnaire">
            Анкета
          </Link>
          <Link className="rounded-full border border-[var(--border)] bg-white/60 px-4 py-2 backdrop-blur-sm" href="/host">
            Host
          </Link>
        </nav>
      </header>
      {children}
    </div>
  );
}
