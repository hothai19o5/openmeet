'use client'

import { AppShell } from '@/components/layout/app-shell'
import { Button } from '@/components/ui/button'
import { Video, Plus, Search, Lock, Users, ArrowUpRight, LayoutGrid, List } from 'lucide-react'
import Link from 'next/link'
import { useState } from 'react'
import { cn } from '@/lib/utils'

// Mock — replaced with API in 1.4
const rooms = [
  { id: 'daily-standup', name: 'Daily Standup', participants: 5, encrypted: false, active: true },
  { id: 'project-alpha', name: 'Project Alpha', participants: 3, encrypted: true, active: true },
  { id: 'team-review', name: 'Weekly Review', participants: 0, encrypted: false, active: false },
  { id: 'command-brief', name: 'Command Briefing', participants: 8, encrypted: true, active: true },
  { id: 'onboarding', name: 'Onboarding Call', participants: 0, encrypted: false, active: false },
  { id: 'incident-1', name: 'Incident Response', participants: 2, encrypted: true, active: true },
]

export default function RoomsPage() {
  const [search, setSearch] = useState('')
  const [view, setView] = useState<'grid' | 'list'>('grid')

  const filtered = rooms.filter((r) =>
    r.name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <AppShell title="Rooms" subtitle={`${rooms.filter((r) => r.active).length} active`}>
      {/* Toolbar */}
      <div className="flex items-center gap-3 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-text-tertiary" />
          <input
            className="input pl-9"
            placeholder="Search rooms…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-1 p-0.5 rounded bg-surface border border-surface-border">
          <button
            onClick={() => setView('grid')}
            className={cn('btn-icon !p-1.5', view === 'grid' && 'bg-surface-hover text-text-primary')}
          >
            <LayoutGrid className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={() => setView('list')}
            className={cn('btn-icon !p-1.5', view === 'list' && 'bg-surface-hover text-text-primary')}
          >
            <List className="h-3.5 w-3.5" />
          </button>
        </div>
        <Link href="/rooms/new">
          <Button variant="primary" icon={<Plus />} size="sm">
            New Room
          </Button>
        </Link>
      </div>

      {/* Grid view */}
      {view === 'grid' ? (
        <div className="grid grid-cols-3 gap-4">
          {filtered.map((room) => (
            <Link key={room.id} href={`/rooms/${room.id}`} className="card-hover p-5 group">
              <div className="flex items-center justify-between mb-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10">
                  <Video className="h-4 w-4 text-brand" />
                </div>
                {room.active && (
                  <span className="badge badge-success text-[10px]">
                    <span className="h-1.5 w-1.5 rounded-full bg-status-success animate-pulse-dot" />
                    Live
                  </span>
                )}
              </div>
              <h3 className="font-medium text-text-primary text-sm mb-1 truncate">{room.name}</h3>
              <div className="flex items-center gap-3 text-xs text-text-secondary">
                <span className="flex items-center gap-1">
                  <Users className="h-3 w-3" /> {room.participants}
                </span>
                {room.encrypted && (
                  <span className="flex items-center gap-1 text-brand">
                    <Lock className="h-3 w-3" /> E2EE
                  </span>
                )}
              </div>
              <div className="mt-4 flex items-center gap-1 text-xs text-brand opacity-0 group-hover:opacity-100 transition-opacity">
                Join room <ArrowUpRight className="h-3 w-3" />
              </div>
            </Link>
          ))}
        </div>
      ) : (
        /* List view */
        <div className="space-y-1">
          {filtered.map((room) => (
            <Link
              key={room.id}
              href={`/rooms/${room.id}`}
              className="flex items-center gap-4 px-4 py-3 rounded-lg hover:bg-surface transition-colors group"
            >
              <div className="flex h-8 w-8 items-center justify-center rounded bg-brand/10">
                <Video className="h-3.5 w-3.5 text-brand" />
              </div>
              <span className="flex-1 text-sm font-medium text-text-primary">{room.name}</span>
              {room.encrypted && <span className="badge badge-brand text-[10px]"><Lock className="h-2.5 w-2.5" /> E2EE</span>}
              <span className="flex items-center gap-1 text-xs text-text-secondary">
                <Users className="h-3 w-3" /> {room.participants}
              </span>
              {room.active && <span className="h-2 w-2 rounded-full bg-status-success" />}
              <ArrowUpRight className="h-4 w-4 text-text-tertiary group-hover:text-brand transition-colors" />
            </Link>
          ))}
        </div>
      )}
    </AppShell>
  )
}
