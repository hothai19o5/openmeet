import { getServerSession } from 'next-auth/next'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { redirect } from 'next/navigation'
import RoomClient from './room-client'

export default async function RoomPage({ params }: { params: Promise<{ slug: string }> }) {
  const session = await getServerSession(authOptions)
  
  if (!session || !session.user) {
    redirect('/api/auth/signin')
  }

  const { slug } = await params;

  const room = await prisma.room.findUnique({
    where: { slug },
  })

  if (!room) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-text-primary mb-2">Room Not Found</h1>
          <p className="text-text-secondary">The room "{slug}" does not exist or has been closed.</p>
        </div>
      </div>
    )
  }

  return <RoomClient room={room} user={session.user} />
}
