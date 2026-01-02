import NextAuth, { NextAuthOptions } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import GithubProvider from "next-auth/providers/github";

// Production app URL - hardcoded as fallback when env vars not set
const PRODUCTION_APP_URL = "https://app.mimoai.co";

// Check if URL is an AWS ALB/ELB URL that should be rejected
const isAlbUrl = (url: string | undefined): boolean => {
  if (!url) return false;
  return url.includes(".elb.amazonaws.com") || url.includes(".alb.amazonaws.com");
};

// Get the base URL for redirects - use custom domain, not ALB
const getBaseUrl = () => {
  // Use NEXTAUTH_URL only if it's NOT an ALB URL
  if (process.env.NEXTAUTH_URL && !isAlbUrl(process.env.NEXTAUTH_URL)) {
    return process.env.NEXTAUTH_URL;
  }
  if (process.env.NEXT_PUBLIC_APP_URL && !isAlbUrl(process.env.NEXT_PUBLIC_APP_URL)) {
    return process.env.NEXT_PUBLIC_APP_URL;
  }

  // In production (NODE_ENV=production or running on AWS), use production URL
  if (process.env.NODE_ENV === "production") {
    return PRODUCTION_APP_URL;
  }

  // Local development fallback
  return "http://localhost:3000";
};

export const authOptions: NextAuthOptions = {
  providers: [
    // GitHub OAuth
    GithubProvider({
      clientId: process.env.GITHUB_ID ?? "",
      clientSecret: process.env.GITHUB_SECRET ?? "",
    }),
    // Credentials (email/password)
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email", placeholder: "admin@gagiteck.com" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        // Demo credentials for development
        if (
          credentials?.email === "admin@gagiteck.com" &&
          credentials?.password === "admin123"
        ) {
          return {
            id: "1",
            name: "Admin User",
            email: "admin@gagiteck.com",
            role: "admin",
          };
        }

        // Authenticate against the API for real users
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
          const response = await fetch(`${apiUrl}/v1/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              email: credentials?.email,
              password: credentials?.password,
            }),
          });

          if (response.ok) {
            const data = await response.json();
            const userResponse = await fetch(`${apiUrl}/v1/auth/me`, {
              headers: { Authorization: `Bearer ${data.access_token}` },
            });
            if (userResponse.ok) {
              const user = await userResponse.json();
              return {
                id: user.id,
                name: user.name,
                email: user.email,
                role: user.role || "user",
                accessToken: data.access_token,
              };
            }
          }
        } catch (error) {
          console.error("Auth API error:", error);
        }

        return null;
      },
    }),
  ],
  pages: {
    signIn: "/auth/signin",
    signOut: "/auth/signin",
    error: "/auth/error",
  },
  callbacks: {
    async redirect({ url, baseUrl }) {
      // Always use the custom domain URL, not the ALB URL
      const customBaseUrl = getBaseUrl();

      // Allow relative URLs
      if (url.startsWith("/")) {
        return `${customBaseUrl}${url}`;
      }
      // Allow URLs on the same domain
      if (url.startsWith(customBaseUrl)) {
        return url;
      }
      // Default to signin page
      return `${customBaseUrl}/auth/signin`;
    },
    async jwt({ token, user }) {
      if (user) {
        token.role = (user as any).role;
        token.accessToken = (user as any).accessToken;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).role = token.role;
        (session.user as any).accessToken = token.accessToken;
      }
      return session;
    },
  },
  session: {
    strategy: "jwt",
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  secret: process.env.NEXTAUTH_SECRET,
};

export default NextAuth(authOptions);
