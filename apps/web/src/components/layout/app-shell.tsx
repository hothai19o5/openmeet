'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { Sidebar } from '@/components/layout/sidebar'
import { TopBar } from '@/components/layout/topbar'

type AppShellProps = {
  children: React.ReactNode
  title: string
  subtitle?: string
}

export function AppShell({ children, title, subtitle }: AppShellProps) {
  const { status } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (status === 'unauthenticated') router.replace('/login')
  }, [status, router])

  if (status === 'loading') {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 rounded-full border-2 border-brand/30 border-t-brand animate-spin" />
          <p className="text-xs text-text-secondary">Loading…</p>
        </div>
      </div>
    )
  }

  if (status === 'unauthenticated') return null

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopBar title={title} subtitle={subtitle} />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  )
}
