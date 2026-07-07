'use client'

import { AppShell } from '@/components/layout/app-shell'
import { Button } from '@/components/ui/button'
import { Video, Lock, Copy, ArrowRight } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useState, FormEvent } from 'react'
import { useToast } from '@/components/ui/toast'

function generateSlug() {
  const adjectives = ['swift', 'silent', 'brave', 'sharp', 'bright', 'calm', 'dark', 'bold']
  const nouns = ['falcon', 'shield', 'summit', 'cipher', 'nexus', 'signal', 'vector', 'forge']
  const adj = adjectives[Math.floor(Math.random() * adjectives.length)]
  const noun = nouns[Math.floor(Math.random() * nouns.length)]
  const num = Math.floor(Math.random() * 900) + 100
  return `${adj}-${noun}-${num}`
}

export default function NewRoomPage() {
  const router = useRouter()
  const toast = useToast()
  const [name, setName] = useState('')
  const [slug, setSlug] = useState(generateSlug())
  const [encrypted, setEncrypted] = useState(false)
  const [creating, setCreating] = useState(false)

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setCreating(true)
    // Phase 1.4: POST /api/rooms → create room in DB + LiveKit
    // For now: just navigate directly
    setTimeout(() => {
      toast(`Room "${name || slug}" created!`, 'success')
      router.push(`/rooms/${slug}`)
    }, 600)
  }

  const meetingUrl = `${typeof window !== 'undefined' ? window.location.origin : ''}/rooms/${slug}`

  return (
    <AppShell title="Create Room" subtitle="Start a new secure meeting">
      <div className="max-w-lg">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Room name */}
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1.5">
              Room Name
            </label>
            <input
              className="input"
              placeholder="e.g. Daily Standup, Project Alpha Sync"
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={64}
            />
            <p className="text-xs text-text-tertiary mt-1">Optional — slug is used if empty.</p>
          </div>

          {/* Slug */}
          <div>
            <label className="block text-xs font-medium text-text-secondary mb-1.5">
              Room ID
            </label>
            <div className="flex items-center gap-2">
              <input
                className="input flex-1 font-mono text-xs"
                value={slug}
                onChange={(e) => setSlug(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                required
                maxLength={64}
              />
              <button
                type="button"
                onClick={() => setSlug(generateSlug())}
                className="btn-ghost btn-sm text-xs"
              >
                Regenerate
              </button>
            </div>
          </div>

          {/* Meeting URL preview */}
          <div className="card p-4 bg-background-elevated">
            <p className="text-xs text-text-secondary mb-1.5">Share this link</p>
            <div className="flex items-center gap-2">
              <code className="text-xs font-mono text-brand flex-1 truncate">{meetingUrl}</code>
              <button
                type="button"
                onClick={() => {
                  navigator.clipboard.writeText(meetingUrl)
                  toast('Link copied!', 'success')
                }}
                className="btn-icon !p-1"
              >
                <Copy className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>

          {/* E2EE toggle */}
          <div className="flex items-center justify-between p-4 rounded-lg border border-surface-border bg-surface">
            <div className="flex items-center gap-3">
              <Lock className="h-4 w-4 text-brand" />
              <div>
                <p className="text-sm font-medium text-text-primary">End-to-End Encryption</p>
                <p className="text-xs text-text-secondary">Media is encrypted on device. Server cannot decrypt.</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setEncrypted(!encrypted)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                encrypted ? 'bg-brand' : 'bg-surface-border'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  encrypted ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          {/* Submit */}
          <div className="flex items-center gap-3 pt-2">
            <Button type="submit" variant="primary" loading={creating} icon={<Video />}>
              Create & Join
            </Button>
            <Button
              type="button"
              variant="ghost"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </AppShell>
  )
}
