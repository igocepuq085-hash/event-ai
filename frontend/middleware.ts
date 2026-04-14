import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  if (!pathname.startsWith("/host")) {
    return NextResponse.next();
  }

  const expectedPassword = process.env.HOST_PANEL_PASSWORD;
  const cookie = request.cookies.get("host_auth")?.value;

  if (!expectedPassword) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (cookie !== expectedPassword) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/host/:path*"],
};