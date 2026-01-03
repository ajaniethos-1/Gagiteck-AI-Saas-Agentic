import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// Public paths that don't require authentication
const publicPaths = [
  "/auth/signin",
  "/auth/signup",
  "/auth/error",
  "/api/auth",
];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip auth for public paths
  for (const path of publicPaths) {
    if (pathname.startsWith(path)) {
      return NextResponse.next();
    }
  }

  // Skip auth for static files
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon") ||
    pathname.startsWith("/robots")
  ) {
    return NextResponse.next();
  }

  // For all other routes, use withAuth
  return (withAuth as any)(request);
}

export const config = {
  matcher: [
    /*
     * Match all request paths except static files
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
