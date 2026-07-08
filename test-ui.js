const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // Mock NextAuth session for testing the authenticated pages
  await page.setCookie({
    name: 'next-auth.session-token',
    value: 'mock-token',
    domain: 'localhost',
    path: '/',
    httpOnly: true
  });

  console.log("Going to /rooms/new");
  await page.goto('http://localhost:3001/rooms/new', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: '/root/openmeet-phase1.5-create-room.png' });

  console.log("Mocking a Room DB entry for screenshot...");
  // We cannot easily mock the DB from outside, but we can navigate to a non-existent room and capture the "Not Found" UI
  console.log("Going to /rooms/test-room");
  await page.goto('http://localhost:3001/rooms/test-room', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: '/root/openmeet-phase1.5-room-not-found.png' });

  await browser.close();
  console.log("Done");
})();
