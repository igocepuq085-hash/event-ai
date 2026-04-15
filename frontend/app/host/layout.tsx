import type { ReactNode } from "react";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function HostLayout({ children }: { children: ReactNode }) {
  const cookieStore = await cookies();
  const authCookie = cookieStore.get("event-ai-host-auth")?.value;

  if (authCookie !== "ok") {
    redirect("/login?next=/host");
  }

  return children;
}
