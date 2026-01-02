import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

export default withAuth(
  function middleware(req) {
    // If we get here, user is authenticated
    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
    pages: {
      signIn: "/auth/signin",
    },
  }
);

// Protect all routes except auth pages and public assets
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - /auth/signin (sign in page)
     * - /auth/signup (sign up page)
     * - /auth/error (error page)
     * - /api/auth/* (NextAuth API routes)
     * - /_next/* (Next.js internals)
     * - /favicon.ico, /robots.txt (static files)
     */
    "/((?!auth/signin|auth/signup|auth/error|api/auth|_next/static|_next/image|favicon.ico|robots.txt).*)",
  ],
};
