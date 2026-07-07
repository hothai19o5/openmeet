import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { AccessToken } from 'livekit-server-sdk';
import { prisma } from '@/lib/prisma';

export async function GET(req: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(req.url);
    const roomSlug = searchParams.get('room');

    if (!roomSlug) {
      return NextResponse.json({ error: 'Missing "room" query parameter' }, { status: 400 });
    }

    // Optional: Verify room exists
    const room = await prisma.room.findUnique({ where: { slug: roomSlug } });
    if (!room) {
        return NextResponse.json({ error: 'Room not found' }, { status: 404 });
    }

    const livekitApiKey = process.env.LIVEKIT_API_KEY;
    const livekitApiSecret = process.env.LIVEKIT_API_SECRET;

    if (!livekitApiKey || !livekitApiSecret) {
      console.error("LiveKit credentials not configured.");
      return NextResponse.json({ error: 'Server misconfigured' }, { status: 500 });
    }

    const participantName = session.user.name || session.user.email || 'Guest';

    const at = new AccessToken(livekitApiKey, livekitApiSecret, {
      identity: session.user.email || Math.random().toString(),
      name: participantName,
    });

    at.addGrant({ roomJoin: true, room: roomSlug, canPublish: true, canSubscribe: true });

    return NextResponse.json({ token: await at.toJwt() });
  } catch (error) {
    console.error('Error generating token:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
