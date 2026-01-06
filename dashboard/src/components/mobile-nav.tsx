import Link from 'next/link'
import { useRouter } from 'next/router'
import { Bot, Workflow, Zap, Settings, Home } from 'lucide-react'

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Agents', href: '/agents', icon: Bot },
  { name: 'Workflows', href: '/workflows', icon: Workflow },
  { name: 'Executions', href: '/executions', icon: Zap },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export function MobileNav() {
  const router = useRouter()

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background lg:hidden">
      <div className="flex items-center justify-around h-16 px-2">
        {navigation.map((item) => {
          const isActive = router.pathname === item.href ||
            (item.href !== '/' && router.pathname.startsWith(item.href))

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex flex-col items-center justify-center flex-1 h-full gap-1 transition-colors ${
                isActive
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <item.icon className="h-5 w-5" />
              <span className="text-xs font-medium">{item.name}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
