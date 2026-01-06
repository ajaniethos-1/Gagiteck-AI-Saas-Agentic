import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

// Public paths that don't require authentication
const publicPaths = [
  "/auth/signin",
  "/auth/signup",
  "/auth/error",
  "/api/auth",
];

export default withAuth(
  function middleware() {
    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ req, token }) => {
        const { pathname } = req.nextUrl;

        // Allow public paths without authentication
        for (const path of publicPaths) {
          if (pathname.startsWith(path)) {
            return true;
          }
        }

        // Allow static files
        if (
          pathname.startsWith("/_next") ||
          pathname.startsWith("/favicon") ||
          pathname.startsWith("/robots")
        ) {
          return true;
        }

        // Require token for all other routes
        return !!token;
      },
    },
    pages: {
      signIn: "/auth/signin",
    },
  }
);

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
