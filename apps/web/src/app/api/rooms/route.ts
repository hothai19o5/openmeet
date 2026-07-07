import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/prisma';
import { RoomServiceClient } from 'livekit-server-sdk';

export async function POST(req: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session || !session.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { name, isE2EE } = await req.json();

    // 1. Generate slug
    const slug = Math.random().toString(36).substring(2, 10);

    // 2. Create room in Database
    const room = await prisma.room.create({
      data: {
        slug,
        name: name || `Room ${slug}`,
        createdBy: session.user.email || 'unknown',
        isE2EE: !!isE2EE,
      },
    });

    // 3. Create room in LiveKit
    const livekitUrl = process.env.LIVEKIT_URL;
    const livekitApiKey = process.env.LIVEKIT_API_KEY;
    const livekitApiSecret = process.env.LIVEKIT_API_SECRET;

    if (livekitUrl && livekitApiKey && livekitApiSecret) {
      const roomService = new RoomServiceClient(livekitUrl, livekitApiKey, livekitApiSecret);
      await roomService.createRoom({
        name: room.slug,
        emptyTimeout: 10 * 60, // 10 minutes
        maxParticipants: 50,
      });
    } else {
        console.warn("LiveKit config missing, only creating room in DB.");
    }

    return NextResponse.json(room);
  } catch (error) {
    console.error('Failed to create room:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
