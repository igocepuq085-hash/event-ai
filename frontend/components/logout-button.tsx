"use client";

import { useRouter } from "next/navigation";
import { useTransition } from "react";

export function LogoutButton() {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  return (
    <button
      type="button"
      disabled={isPending}
      onClick={() =>
        startTransition(async () => {
          await fetch("/api/host-logout", { method: "POST" });
          router.push("/login");
          router.refresh();
        })
      }
      className="rounded-full border border-[var(--border)] bg-white/70 px-4 py-2 text-sm font-medium text-stone-800"
    >
      {isPending ? "Выход..." : "Выйти"}
    </button>
  );
}
