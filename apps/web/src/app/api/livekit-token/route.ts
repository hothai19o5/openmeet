import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { AccessToken } from 'livekit-server-sdk'

const LK_KEY    = process.env.LIVEKIT_API_KEY    ?? 'devkey'
const LK_SECRET = process.env.LIVEKIT_API_SECRET ?? 'secret'

/**
 * POST /api/livekit-token
 * Body: { room: string, metadata?: string }
 * Returns: { token: string }
 */
export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions)
  if (!session?.user) {
    return NextResponse.json({ error: 'unauthenticated' }, { status: 401 })
  }

  const body = (await req.json()) as { room?: string; metadata?: string }
  const room = body?.room?.trim()

  if (!room || room.length > 64) {
    return NextResponse.json({ error: 'invalid room name' }, { status: 400 })
  }

  const at = new AccessToken(LK_KEY, LK_SECRET, {
    identity: session.user.id,
    name: session.user.name ?? session.user.id,
    metadata: body.metadata,
    ttl: '2h',
  })

  at.addGrant({
    room,
    roomJoin: true,
    canPublish: true,
    canSubscribe: true,
    canPublishData: true,
    canUpdateOwnMetadata: true,
  })

  const token = await at.toJwt()
  return NextResponse.json({ token })
}
