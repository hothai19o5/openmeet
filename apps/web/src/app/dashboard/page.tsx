'use client'

import { AppShell } from '@/components/layout/app-shell'
import { Button } from '@/components/ui/button'
import { Avatar } from '@/components/ui/avatar'
import { Video, Plus, Users, Clock, Lock, ArrowUpRight, Activity } from 'lucide-react'
import Link from 'next/link'
import { useSession } from 'next-auth/react'
import { formatDistanceToNow } from 'date-fns'

// Mock data — replaced with API calls in Phase 1.4+
const recentRooms = [
  { id: 'daily-standup', name: 'Daily Standup', participants: 5, createdAt: new Date(Date.now() - 3600000), encrypted: false },
  { id: 'project-alpha', name: 'Project Alpha Sync', participants: 3, createdAt: new Date(Date.now() - 7200000), encrypted: true },
  { id: 'team-review', name: 'Weekly Team Review', participants: 12, createdAt: new Date(Date.now() - 86400000), encrypted: false },
  { id: 'command-brief', name: 'Command Briefing', participants: 8, createdAt: new Date(Date.now() - 172800000), encrypted: true },
]

const statCards = [
  { icon: Video, label: 'Active Rooms', value: '3', change: '+1 today', color: 'text-brand' },
  { icon: Users, label: 'Online Members', value: '14', change: '/ 32 total', color: 'text-status-success' },
  { icon: Clock, label: 'Total Hours Today', value: '4.2h', change: '+1.5h vs yesterday', color: 'text-status-warning' },
  { icon: Lock, label: 'E2EE Sessions', value: '67%', change: '↑ 12% this week', color: 'text-brand' },
]

export default function DashboardPage() {
  const { data: session } = useSession()

  return (
    <AppShell title="Dashboard" subtitle={`Welcome back, ${session?.user?.name ?? 'User'}`}>
      {/* Quick actions */}
      <div className="flex items-center gap-3 mb-8">
        <Link href="/rooms/new">
          <Button variant="primary" icon={<Plus />}>
            New Room
          </Button>
        </Link>
        <Link href="/rooms">
          <Button variant="secondary" icon={<Video />}>
            Join Room
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {statCards.map(({ icon: Icon, label, value, change, color }) => (
          <div key={label} className="card p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-text-secondary font-medium">{label}</span>
              <Icon className={`h-4 w-4 ${color}`} />
            </div>
            <p className="text-2xl font-bold text-text-primary">{value}</p>
            <p className="text-xs text-text-tertiary mt-1">{change}</p>
          </div>
        ))}
      </div>

      {/* Recent rooms */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-text-primary flex items-center gap-2">
            <Activity className="h-4 w-4 text-text-secondary" />
            Recent Rooms
          </h2>
          <Link href="/rooms" className="text-xs text-brand hover:text-brand-hover transition-colors">
            View all →
          </Link>
        </div>

        <div className="space-y-1">
          {recentRooms.map((room) => (
            <Link
              key={room.id}
              href={`/rooms/${room.id}`}
              className="flex items-center gap-4 px-4 py-3 rounded-lg hover:bg-surface transition-colors group"
            >
              {/* Room icon */}
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand/10">
                <Video className="h-4 w-4 text-brand" />
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-text-primary truncate">{room.name}</span>
                  {room.encrypted && (
                    <span className="badge badge-brand text-[10px]">
                      <Lock className="h-2.5 w-2.5" /> E2EE
                    </span>
                  )}
                </div>
                <span className="text-xs text-text-secondary">
                  {formatDistanceToNow(room.createdAt, { addSuffix: true })}
                </span>
              </div>

              {/* Participants */}
              <div className="flex items-center gap-1.5 text-xs text-text-secondary">
                <Users className="h-3.5 w-3.5" />
                {room.participants}
              </div>

              {/* Join arrow */}
              <ArrowUpRight className="h-4 w-4 text-text-tertiary group-hover:text-brand transition-colors" />
            </Link>
          ))}
        </div>
      </div>
    </AppShell>
  )
}
