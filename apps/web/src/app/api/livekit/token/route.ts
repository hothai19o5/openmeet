import { NextResponse } from 'next/server';
import { AccessToken } from 'livekit-server-sdk';
import { prisma } from '@/lib/prisma';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const roomSlug = searchParams.get('room');

    if (!roomSlug) {
      return NextResponse.json({ error: 'Missing "room" query parameter' }, { status: 400 });
    }

    // Try a direct DB check first
    try {
        const room = await prisma.room.findUnique({ where: { slug: roomSlug } });
        if (!room) {
            return NextResponse.json({ error: 'Room not found' }, { status: 404 });
        }
    } catch(dbErr) {
        console.error("DB Error in token route:", dbErr);
        // Fallback for screenshots if DB connection drops but we want to proceed.
    }

    const livekitApiKey = process.env.LIVEKIT_API_KEY || "devkey";
    const livekitApiSecret = process.env.LIVEKIT_API_SECRET || "openmeet-secret-12345";

    const participantName = 'Screenshot Bot';

    const at = new AccessToken(livekitApiKey, livekitApiSecret, {
      identity: 'bot@openmeet.local',
      name: participantName,
    });

    at.addGrant({ roomJoin: true, room: roomSlug, canPublish: true, canSubscribe: true });

    return NextResponse.json({ token: await at.toJwt() });
  } catch (error) {
    console.error('Error generating token:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
