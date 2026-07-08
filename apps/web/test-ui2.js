const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  // Use the login form to get a real session
  await page.goto('http://localhost:3001/login', { waitUntil: 'networkidle0' });
  await page.type('input[placeholder*="username"], input[name="username"], input[type="text"]', 'analyst');
  await page.type('input[placeholder*="password"], input[name="password"], input[type="password"]', 'analyst123');
  await page.click('button[type="submit"]');
  await page.waitForNavigation({ waitUntil: 'networkidle0' });

  console.log("Going to /rooms/demo-room-15");
  await page.goto('http://localhost:3001/rooms/demo-room-15', { waitUntil: 'networkidle0' });
  await page.screenshot({ path: '/root/openmeet-phase1.5-live-room.png' });

  await browser.close();
  console.log("Done");
})();
