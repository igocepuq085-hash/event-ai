import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { password } = (await request.json()) as { password?: string };
  const expectedPassword =
    process.env.HOST_PANEL_PASSWORD ||
    process.env.ADMIN_PASSWORD ||
    process.env.HOST_PASSWORD ||
    "change-me";

  if (!password || password !== expectedPassword) {
    return NextResponse.json({ message: "Неверный пароль" }, { status: 401 });
  }

  const cookieStore = await cookies();
  cookieStore.set("event-ai-host-auth", "ok", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 8,
    path: "/",
  });

  return NextResponse.json({ status: "success" });
}
