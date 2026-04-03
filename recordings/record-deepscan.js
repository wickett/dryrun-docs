/**
 * Record a "Start a DeepScan" walkthrough as a .webm video.
 *
 * Prerequisites:
 *   npm install @playwright/test
 *   npx playwright install chromium
 *
 * Usage (uses a fresh browser — you will need to log in):
 *   node recordings/record-deepscan.js
 *
 * Usage (reuses your existing Chrome profile so you're already logged in):
 *   node recordings/record-deepscan.js --profile
 *
 * Output:
 *   recordings/output/deepscan.webm   — raw Playwright video
 *
 * Then convert to GIF:
 *   bash recordings/convert-to-gif.sh recordings/output/deepscan.webm recordings/output/deepscan.gif
 */

const { chromium } = require('playwright');
const path = require('path');
const os = require('os');
const fs = require('fs');

const OUTPUT_DIR = path.join(__dirname, 'output');
const VIEWPORT = { width: 1280, height: 800 };

// Pause helper — gives the viewer time to see each step
const pause = (ms) => new Promise((r) => setTimeout(r, ms));

// Default Chrome user-data-dir per platform
function defaultChromeProfile() {
  switch (process.platform) {
    case 'darwin':
      return path.join(os.homedir(), 'Library', 'Application Support', 'Google', 'Chrome');
    case 'win32':
      return path.join(os.homedir(), 'AppData', 'Local', 'Google', 'Chrome', 'User Data');
    default:
      return path.join(os.homedir(), '.config', 'google-chrome');
  }
}

(async () => {
  const useProfile = process.argv.includes('--profile');

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  let browser, context, page;

  if (useProfile) {
    // ---------------------------------------------------------------
    // Persistent context — reuses your logged-in Chrome session.
    // NOTE: Close Chrome first; Playwright can't share the profile
    // with a running Chrome instance.
    // ---------------------------------------------------------------
    const profileDir = process.env.CHROME_PROFILE || defaultChromeProfile();
    console.log(`Using Chrome profile at: ${profileDir}`);
    console.log('Make sure Chrome is closed before running this.\n');

    context = await chromium.launchPersistentContext(profileDir, {
      headless: false,
      viewport: VIEWPORT,
      recordVideo: { dir: OUTPUT_DIR, size: VIEWPORT },
      args: ['--disable-blink-features=AutomationControlled'],
    });
    page = context.pages()[0] || await context.newPage();
  } else {
    // ---------------------------------------------------------------
    // Fresh browser — you'll need to log in manually or the script
    // will record the login flow too.
    // ---------------------------------------------------------------
    browser = await chromium.launch({ headless: false });
    context = await browser.newContext({
      viewport: VIEWPORT,
      recordVideo: { dir: OUTPUT_DIR, size: VIEWPORT },
    });
    page = await context.newPage();
  }

  try {
    console.log('▶ Starting recording...\n');

    // 1. Navigate to the DryRun Security dashboard
    console.log('  → Navigating to app.dryrun.security');
    await page.goto('https://app.dryrun.security', { waitUntil: 'networkidle' });
    await pause(2000);

    // 2. Look for a repository / repos list and click into one
    //    Adjust the selector below if the dashboard layout differs.
    console.log('  → Looking for a repository to scan...');

    // Try common dashboard patterns — click the first repo link visible
    const repoLink = page.locator('a[href*="repo"], [data-testid*="repo"], .repo-name, .repository-item, tr a, .repo-link').first();
    if (await repoLink.isVisible({ timeout: 5000 }).catch(() => false)) {
      await repoLink.click();
      await pause(2000);
    } else {
      console.log('  ⚠  Could not find a repo link automatically.');
      console.log('     Pausing 10s — manually navigate to a repo page now.');
      await pause(10000);
    }

    // 3. Find and click the DeepScan / "Start Scan" button
    console.log('  → Looking for the DeepScan button...');
    const scanButton = page.locator(
      'button:has-text("DeepScan"), button:has-text("Deep Scan"), ' +
      'button:has-text("Start Scan"), button:has-text("Run DeepScan"), ' +
      'a:has-text("DeepScan"), a:has-text("Start Scan"), ' +
      '[data-testid*="deepscan"], [data-testid*="deep-scan"]'
    ).first();

    if (await scanButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Hover first to show any tooltip, then click
      await scanButton.hover();
      await pause(1000);
      await scanButton.click();
      console.log('  → Clicked DeepScan button');
      await pause(3000);
    } else {
      console.log('  ⚠  Could not find a DeepScan button automatically.');
      console.log('     Pausing 10s — manually click "Start DeepScan" now.');
      await pause(10000);
    }

    // 4. If there's a confirmation dialog, capture it
    const confirmButton = page.locator(
      'button:has-text("Confirm"), button:has-text("Start"), button:has-text("Yes")'
    ).first();

    if (await confirmButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      await pause(1500);
      await confirmButton.click();
      console.log('  → Confirmed scan');
      await pause(3000);
    }

    // 5. Hold on the result / progress screen for a moment
    console.log('  → Capturing final state...');
    await pause(3000);

    console.log('\n✓ Recording complete.');
  } finally {
    // Close context to finalize the video file
    await context.close();
    if (browser) await browser.close();
  }

  // Playwright saves the video with a random name — rename it
  const files = fs.readdirSync(OUTPUT_DIR).filter((f) => f.endsWith('.webm'));
  if (files.length > 0) {
    const latest = files
      .map((f) => ({ name: f, time: fs.statSync(path.join(OUTPUT_DIR, f)).mtimeMs }))
      .sort((a, b) => b.time - a.time)[0];
    const dest = path.join(OUTPUT_DIR, 'deepscan.webm');
    fs.renameSync(path.join(OUTPUT_DIR, latest.name), dest);
    console.log(`\nSaved: ${dest}`);
    console.log(`\nConvert to GIF:\n  bash recordings/convert-to-gif.sh ${dest} recordings/output/deepscan.gif`);
  }
})();
