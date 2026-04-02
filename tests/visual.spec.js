// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
  });

  test('page loads with title', async ({ page }) => {
    await expect(page).toHaveTitle(/DryRun Security/);
  });

  test('header has logo', async ({ page }) => {
    await expect(page.locator('.site-header')).toBeVisible();
    await expect(page.locator('.logo')).toBeVisible();
  });

  test('hero section is visible', async ({ page }) => {
    await expect(page.locator('.docs-hero')).toBeVisible();
    await expect(page.locator('.docs-hero-title')).toBeVisible();
  });

  test('search input exists', async ({ page }) => {
    await expect(page.locator('.docs-hero-search input')).toBeVisible();
  });

  test('section cards are present', async ({ page }) => {
    const cards = page.locator('.index-card');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(7);
  });

  test('quick start links exist', async ({ page }) => {
    const links = page.locator('.docs-quickstart-link');
    const count = await links.count();
    expect(count).toBeGreaterThanOrEqual(3);
  });

  test('footer is present', async ({ page }) => {
    const footer = page.locator('.site-footer');
    await footer.scrollIntoViewIfNeeded();
    await expect(footer).toBeVisible();
  });
});

test.describe('Documentation Pages', () => {
  test('doc page has sidebar', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Sidebar hidden by default on mobile');
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.sidebar')).toBeVisible();
  });

  test('doc page has TOC on desktop', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'TOC hidden on mobile');
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.toc-sidebar')).toBeVisible();
  });

  test('sidebar highlights active page', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Sidebar hidden on mobile');
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    const active = page.locator('.sidebar-links a.active');
    await expect(active).toBeVisible();
    const count = await active.count();
    expect(count).toBe(1);
  });

  test('breadcrumb is visible', async ({ page }) => {
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.breadcrumb')).toBeVisible();
  });

  test('prev/next navigation exists', async ({ page }) => {
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    const nav = page.locator('.prev-next');
    await nav.scrollIntoViewIfNeeded();
    await expect(nav).toBeVisible();
  });

  test('page heading is present', async ({ page }) => {
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.page-heading')).toBeVisible();
  });

  test('doc content has text', async ({ page }) => {
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    const content = page.locator('.doc-content');
    await expect(content).toBeVisible();
    const text = await content.textContent();
    expect(text.length).toBeGreaterThan(200);
  });

  test('coverage matrix page has table', async ({ page }) => {
    await page.goto('/docs/coverage-matrix.html');
    await page.waitForLoadState('domcontentloaded');
    const table = page.locator('.doc-content table');
    await expect(table).toBeVisible();
  });
});

test.describe('Mobile Specific', () => {
  test('sidebar toggle is visible on mobile', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.sidebar-toggle')).toBeVisible();
  });

  test('sidebar opens on mobile toggle click', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    await page.locator('.sidebar-toggle').click();
    await page.waitForTimeout(400);
    const sidebar = page.locator('.sidebar');
    const classList = await sidebar.getAttribute('class');
    expect(classList).toContain('open');
  });

  test('header is compact on mobile', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
    const header = page.locator('.site-header');
    const box = await header.boundingBox();
    expect(box).not.toBeNull();
    expect(box.height).toBeLessThanOrEqual(55);
  });

  test('no horizontal overflow on mobile', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
    const hasOverflow = await page.evaluate(() => {
      return document.body.scrollWidth > window.innerWidth;
    });
    expect(hasOverflow).toBe(false);
  });
});
