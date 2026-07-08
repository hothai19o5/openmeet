const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const room = await prisma.room.create({
    data: {
      name: "Phase 1.5 Demo Room",
      slug: "demo-room-15",
      createdBy: "analyst",
      isE2EE: false
    }
  });
  console.log("Room created: ", room.slug);
}
main().catch(console.error).finally(() => prisma.$disconnect());
