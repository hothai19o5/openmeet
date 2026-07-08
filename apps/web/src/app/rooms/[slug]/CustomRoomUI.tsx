'use client'

import { 
  useRoomContext,
  useParticipants,
  useLocalParticipant,
  RoomAudioRenderer,
  GridLayout,
  ParticipantTile,
  ControlBar,
  Chat,
  FocusLayout,
  FocusLayoutContainer,
  WidgetState,
  LayoutContextProvider
} from '@livekit/components-react'
import { RoomEvent, Track, Participant } from 'livekit-client'
import { useEffect, useState } from 'react'
import { useToast } from '@/components/ui/toast'
import { MessageSquare, Users } from 'lucide-react'

export function CustomRoomUI() {
  const room = useRoomContext()
  const toast = useToast()
  
  // States cho Custom UI
  const [showChat, setShowChat] = useState(false)
  const [showParticipants, setShowParticipants] = useState(false)
  const participants = useParticipants()
  
  // Track events for Toast notifications (Task 1.6)
  useEffect(() => {
    if (!room) return

    const handleParticipantConnected = (participant: Participant) => {
      toast(`${participant.identity || 'A participant'} joined the room`, 'info')
    }

    const handleParticipantDisconnected = (participant: Participant) => {
      toast(`${participant.identity || 'A participant'} left the room`, 'info')
    }

    const handleTrackMuted = (pub: any, participant: Participant) => {
      if (pub.kind === Track.Kind.Audio) {
        toast(`${participant.identity} muted their mic`, 'info')
      }
    }

    const handleTrackUnmuted = (pub: any, participant: Participant) => {
      if (pub.kind === Track.Kind.Audio) {
        toast(`${participant.identity} unmuted their mic`, 'success')
      }
    }
    
    const handleLocalScreenShare = () => {
       toast('You are sharing your screen', 'info')
    }

    room
      .on(RoomEvent.ParticipantConnected, handleParticipantConnected)
      .on(RoomEvent.ParticipantDisconnected, handleParticipantDisconnected)
      .on(RoomEvent.TrackMuted, handleTrackMuted)
      .on(RoomEvent.TrackUnmuted, handleTrackUnmuted)
      .on(RoomEvent.LocalTrackPublished, (pub) => {
        if (pub.source === Track.Source.ScreenShare) handleLocalScreenShare()
      })

    return () => {
      room
        .off(RoomEvent.ParticipantConnected, handleParticipantConnected)
        .off(RoomEvent.ParticipantDisconnected, handleParticipantDisconnected)
        .off(RoomEvent.TrackMuted, handleTrackMuted)
        .off(RoomEvent.TrackUnmuted, handleTrackUnmuted)
    }
  }, [room, toast])

  // Lọc ra người đang share screen
  const screenShareTracks = participants
    .map((p) => p.getTrackPublication(Track.Source.ScreenShare))
    .filter((pub) => pub !== undefined)

  const hasScreenShare = screenShareTracks.length > 0

  return (
    <LayoutContextProvider>
      <div className="flex flex-col h-full w-full bg-surface relative">
        <div className="flex flex-1 overflow-hidden">
          {/* Main Video Area (Task 1.9 & 1.8) */}
          <div className="flex-1 flex flex-col p-4">
            {hasScreenShare ? (
              <FocusLayoutContainer>
                <FocusLayout />
              </FocusLayoutContainer>
            ) : (
              <GridLayout tracks={participants.map(p => ({ participant: p, source: Track.Source.Camera }))}>
                <ParticipantTile />
              </GridLayout>
            )}
          </div>
          
          {/* Sidebar Area (Chat / Participants) */}
          {showChat && (
            <div className="w-80 border-l border-surface-border flex flex-col h-full bg-background relative z-10 transition-all">
              <div className="p-3 border-b border-surface-border flex justify-between items-center text-text-primary">
                <span className="font-medium text-sm">In-room Chat</span>
                <button onClick={() => setShowChat(false)} className="text-text-secondary hover:text-text-primary">✕</button>
              </div>
              <div className="flex-1 overflow-hidden lk-chat-override">
                {/* Custom styling class .lk-chat-override will be added in global CSS */}
                <Chat />
              </div>
            </div>
          )}

          {showParticipants && !showChat && (
             <div className="w-80 border-l border-surface-border flex flex-col h-full bg-background relative z-10">
               <div className="p-3 border-b border-surface-border flex justify-between items-center text-text-primary">
                  <span className="font-medium text-sm">Participants ({participants.length})</span>
                  <button onClick={() => setShowParticipants(false)} className="text-text-secondary hover:text-text-primary">✕</button>
               </div>
               <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {participants.map(p => (
                    <div key={p.sid} className="flex items-center gap-3">
                       <div className="w-8 h-8 rounded-full bg-surface-border flex items-center justify-center text-xs font-bold text-text-primary uppercase">
                          {p.identity.slice(0, 2)}
                       </div>
                       <div className="flex-1">
                          <p className="text-sm text-text-primary font-medium">{p.identity}</p>
                          <p className="text-xs text-text-secondary">{p.isLocal ? 'You' : 'Guest'}</p>
                       </div>
                    </div>
                  ))}
               </div>
             </div>
          )}
        </div>

        {/* Bottom Control Bar */}
        <div className="h-20 border-t border-surface-border bg-background flex items-center justify-between px-6">
          <div className="flex-1" /> {/* Spacer */}
          
          <div className="flex-1 flex justify-center">
            {/* LiveKit built-in ControlBar handles Mic, Cam, ScreenShare, Leave (Task 1.8) */}
            <ControlBar variation="minimal" />
          </div>

          <div className="flex-1 flex justify-end gap-3">
             <button 
               onClick={() => { setShowParticipants(!showParticipants); setShowChat(false) }}
               className={`p-3 rounded-full hover:bg-surface-border transition-colors ${showParticipants ? 'bg-surface-border text-brand' : 'text-text-secondary'}`}
             >
               <Users size={20} />
             </button>
             <button 
               onClick={() => { setShowChat(!showChat); setShowParticipants(false) }}
               className={`p-3 rounded-full hover:bg-surface-border transition-colors relative ${showChat ? 'bg-surface-border text-brand' : 'text-text-secondary'}`}
             >
               <MessageSquare size={20} />
             </button>
          </div>
        </div>

        <RoomAudioRenderer />
      </div>
    </LayoutContextProvider>
  )
}
