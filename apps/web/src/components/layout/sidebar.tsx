'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useSession, signOut } from 'next-auth/react'
import {
  Video, LayoutDashboard, Settings, Shield,
  LogOut, ChevronDown, Plus, Users
} from 'lucide-react'
import { Avatar } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'
import { useState } from 'react'

const nav = [
  { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/rooms',     icon: Video,           label: 'Rooms' },
  { href: '/members',   icon: Users,            label: 'Members' },
  { href: '/settings',  icon: Settings,         label: 'Settings' },
  { href: '/admin',     icon: Shield,           label: 'Admin', adminOnly: true },
]

export function Sidebar() {
  const pathname = usePathname()
  const { data: session } = useSession()
  const [userOpen, setUserOpen] = useState(false)

  const isAdmin = (session?.user as any)?.role === 'admin'

  return (
    <aside className="sidebar w-60 shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 h-14 border-b border-surface-border">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-brand">
          <Video className="h-4 w-4 text-white" />
        </div>
        <span className="font-semibold text-text-primary tracking-tight">OpenMeet</span>
        <span className="ml-auto badge badge-brand text-[10px]">Beta</span>
      </div>

      {/* New Room button */}
      <div className="px-3 py-3">
        <Link
          href="/rooms/new"
          className="btn-primary w-full justify-center text-xs py-1.5"
        >
          <Plus className="h-3.5 w-3.5" />
          New Room
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 space-y-0.5">
        {nav
          .filter((item) => !item.adminOnly || isAdmin)
          .map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                pathname.startsWith(href) ? 'nav-item-active' : 'nav-item'
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {label}
            </Link>
          ))}
      </nav>

      {/* User section */}
      <div className="border-t border-surface-border p-3">
        <button
          onClick={() => setUserOpen((v) => !v)}
          className="flex w-full items-center gap-2.5 rounded px-2 py-1.5 hover:bg-surface transition-colors duration-100"
        >
          <Avatar name={session?.user?.name} size="sm" online />
          <div className="flex-1 text-left min-w-0">
            <p className="text-xs font-medium text-text-primary truncate">
              {session?.user?.name ?? 'Unknown'}
            </p>
            <p className="text-[11px] text-text-secondary truncate">
              {session?.user?.email ?? ''}
            </p>
          </div>
          <ChevronDown className={cn('h-3.5 w-3.5 text-text-secondary transition-transform', userOpen && 'rotate-180')} />
        </button>

        {userOpen && (
          <div className="mt-1 rounded border border-surface-border bg-background-elevated p-1 shadow-popup animate-in">
            <button
              onClick={() => signOut({ callbackUrl: '/login' })}
              className="flex w-full items-center gap-2 px-3 py-1.5 text-xs text-status-error hover:bg-status-error/10 rounded transition-colors"
            >
              <LogOut className="h-3.5 w-3.5" />
              Sign out
            </button>
          </div>
        )}
      </div>
    </aside>
  )
}
