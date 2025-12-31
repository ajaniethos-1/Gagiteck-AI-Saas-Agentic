import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import { SessionProvider, useSession } from 'next-auth/react'
import { useRouter } from 'next/router'
import { Layout } from '@/components/layout'
import { Loader2 } from 'lucide-react'

// Pages that don't require authentication
const publicPages = ['/auth/signin', '/auth/error']

function AuthWrapper({ children }: { children: React.ReactNode }) {
  const { status } = useSession()
  const router = useRouter()

  // Check if current page is public
  const isPublicPage = publicPages.includes(router.pathname)

  if (isPublicPage) {
    return <>{children}</>
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (status === 'unauthenticated') {
    router.push('/auth/signin')
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return <>{children}</>
}

export default function App({ Component, pageProps: { session, ...pageProps } }: AppProps) {
  const router = useRouter()
  const isPublicPage = publicPages.includes(router.pathname)

  return (
    <SessionProvider session={session}>
      <AuthWrapper>
        {isPublicPage ? (
          <Component {...pageProps} />
        ) : (
          <Layout>
            <Component {...pageProps} />
          </Layout>
        )}
      </AuthWrapper>
    </SessionProvider>
  )
}
