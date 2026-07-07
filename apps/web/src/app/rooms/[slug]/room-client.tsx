'use client'

import { AppShell } from '@/components/layout/app-shell'
import {
  LiveKitRoom,
  VideoConference,
  RoomAudioRenderer,
} from '@livekit/components-react'
import '@livekit/components-styles'
import { useEffect, useState } from 'react'
import { Loader2 } from 'lucide-react'

export default function RoomClient({ room, user }: { room: any; user: any }) {
  const [token, setToken] = useState('')

  useEffect(() => {
    ;(async () => {
      try {
        const resp = await fetch(`/api/livekit/token?room=${room.slug}`)
        const data = await resp.json()
        setToken(data.token)
      } catch (e) {
        console.error(e)
      }
    })()
  }, [room.slug])

  if (token === '') {
    return (
      <AppShell title={room.name} subtitle={`Connecting to ${room.slug}...`} hideSidebar>
        <div className="flex h-[calc(100vh-100px)] items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-brand" />
        </div>
      </AppShell>
    )
  }

  const liveKitUrl = process.env.NEXT_PUBLIC_LIVEKIT_URL

  if (!liveKitUrl) {
     return <div>Missing LiveKit URL Configuration</div>
  }

  return (
    <AppShell title={room.name} subtitle={room.slug} hideSidebar>
      <div className="h-[calc(100vh-100px)] rounded-xl overflow-hidden border border-surface-border bg-black">
        <LiveKitRoom
          video={true}
          audio={true}
          token={token}
          serverUrl={liveKitUrl}
          data-lk-theme="default"
          style={{ height: '100%' }}
        >
          {/* The VideoConference component provides the default UI layout */}
          <VideoConference />
          <RoomAudioRenderer />
        </LiveKitRoom>
      </div>
    </AppShell>
  )
}
