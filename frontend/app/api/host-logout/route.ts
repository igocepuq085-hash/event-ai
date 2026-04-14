import { NextResponse } from "next/server";

export async function POST() {
  const response = NextResponse.json({ status: "ok" });

  response.cookies.set("host_auth", "", {
    httpOnly: true,
    sameSite: "lax",
    secure: true,
    path: "/",
    maxAge: 0,
  });

  return response;
}