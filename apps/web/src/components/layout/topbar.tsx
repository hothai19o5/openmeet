'use client'

import { Bell, Search } from 'lucide-react'
import { useSession } from 'next-auth/react'

type TopBarProps = { title: string; subtitle?: string }

export function TopBar({ title, subtitle }: TopBarProps) {
  const { data: session } = useSession()

  return (
    <header className="flex items-center h-14 px-6 border-b border-surface-border bg-background-subtle shrink-0 gap-4">
      {/* Title */}
      <div className="flex-1 min-w-0">
        <h1 className="font-semibold text-text-primary text-sm truncate">{title}</h1>
        {subtitle && <p className="text-[11px] text-text-secondary truncate">{subtitle}</p>}
      </div>

      {/* Search trigger */}
      <button className="flex items-center gap-2 px-3 py-1.5 rounded bg-surface border border-surface-border text-text-tertiary text-xs hover:border-surface-active transition-colors">
        <Search className="h-3.5 w-3.5" />
        <span>Search rooms…</span>
        <kbd className="ml-2 font-mono text-[10px] px-1.5 py-0.5 rounded bg-background-elevated border border-surface-border">⌘K</kbd>
      </button>

      {/* Notification */}
      <button className="btn-icon relative">
        <Bell className="h-4 w-4" />
        <span className="absolute top-1 right-1 h-1.5 w-1.5 rounded-full bg-status-error" />
      </button>
    </header>
  )
}
