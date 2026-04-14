import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { password } = await request.json();
  const expectedPassword = process.env.HOST_PANEL_PASSWORD;

  if (!expectedPassword) {
    return NextResponse.json(
      { error: "HOST_PANEL_PASSWORD не задан в переменных окружения" },
      { status: 500 }
    );
  }

  if (!password || password !== expectedPassword) {
    return NextResponse.json({ error: "Неверный пароль" }, { status: 401 });
  }

  const response = NextResponse.json({ status: "ok" });
  response.cookies.set("host_auth", expectedPassword, {
    httpOnly: true,
    sameSite: "lax",
    secure: request.nextUrl.protocol === "https:",
    path: "/",
    maxAge: 60 * 60 * 24 * 14,
  });

  return response;
}
