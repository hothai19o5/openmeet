const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  console.log("Loading dashboard to trigger NextAuth and redirect to login...");
  await page.goto('http://localhost:3001/dashboard', { waitUntil: 'networkidle2' });
  
  console.log("Typing login...");
  // Fill the standard next-auth credentials form or our custom one
  await page.evaluate(() => {
     const userInput = document.querySelector('input[name="username"]') || document.querySelector('input[type="text"]');
     const passInput = document.querySelector('input[name="password"]') || document.querySelector('input[type="password"]');
     if (userInput) userInput.value = 'analyst';
     if (passInput) passInput.value = 'analyst123';
  });

  console.log("Submitting login...");
  const btn = await page.$('button[type="submit"]');
  if (btn) {
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => console.log('Navigation timeout ignored')),
      btn.click()
    ]);
  }

  console.log("Going to /rooms/demo-room-15...");
  await page.goto('http://localhost:3001/rooms/demo-room-15', { waitUntil: 'networkidle2' });
  
  // Wait a moment for LiveKit to initialize
  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: '/root/openmeet-phase1.5-live-room.png' });

  await browser.close();
  console.log("Done");
})();
