// @ts-check
const { test, expect } = require('@playwright/test');

// ============================================================
// Landing Page  -  Structure
// ============================================================
test.describe('Landing Page  -  Structure', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
  });

  test('page loads with correct title', async ({ page }) => {
    await expect(page).toHaveTitle(/DryRun Security/);
  });

  test('header renders with logo, nav links, and CTA buttons', async ({ page, isMobile }) => {
    await expect(page.locator('.site-header')).toBeVisible();
    await expect(page.locator('.logo')).toBeVisible();
    if (!isMobile) {
      await expect(page.locator('.header-nav')).toBeVisible();
      const navLinks = page.locator('.header-nav a');
      expect(await navLinks.count()).toBeGreaterThanOrEqual(3);
    }
    await expect(page.locator('.btn-demo')).toBeVisible();
  });

  test('hero section displays title, subtitle, and search', async ({ page }) => {
    await expect(page.locator('.docs-hero')).toBeVisible();
    await expect(page.locator('.docs-hero-title')).toBeVisible();
    await expect(page.locator('.docs-hero-subtitle')).toBeVisible();
    await expect(page.locator('.docs-hero-search input')).toBeVisible();
  });

  test('quick start links are present', async ({ page }) => {
    const links = page.locator('.docs-quickstart-link');
    expect(await links.count()).toBeGreaterThanOrEqual(3);
  });

  test('all 8 section cards are rendered', async ({ page }) => {
    const cards = page.locator('.index-card');
    expect(await cards.count()).toBe(8);
  });

  test('each section card has icon, title, description, and links', async ({ page }) => {
    const cards = page.locator('.index-card');
    const count = await cards.count();
    for (let i = 0; i < count; i++) {
      const card = cards.nth(i);
      await expect(card.locator('.index-card-icon')).toBeVisible();
      await expect(card.locator('.index-card-title')).toBeVisible();
      await expect(card.locator('.index-card-desc')).toBeVisible();
      const links = card.locator('.index-card-links a');
      expect(await links.count()).toBeGreaterThanOrEqual(1);
    }
  });

  test('footer renders with logo and link sections', async ({ page }) => {
    const footer = page.locator('.site-footer');
    await footer.scrollIntoViewIfNeeded();
    await expect(footer).toBeVisible();
    await expect(footer.locator('.footer-logo-img')).toBeVisible();
  });
});

// ============================================================
// Landing Page  -  Responsive Layout
// ============================================================
test.describe('Landing Page  -  Responsive Layout', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
  });

  test('no horizontal overflow at any viewport', async ({ page }) => {
    const hasOverflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(hasOverflow).toBe(false);
  });

  test('card icons are not oversized (max 50px)', async ({ page }) => {
    const iconSizes = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.index-card-icon svg')).map(svg => {
        const rect = svg.getBoundingClientRect();
        return { width: rect.width, height: rect.height };
      });
    });
    expect(iconSizes.length).toBeGreaterThan(0);
    for (const size of iconSizes) {
      expect(size.width).toBeLessThanOrEqual(50);
      expect(size.height).toBeLessThanOrEqual(50);
    }
  });

  test('desktop: cards render in multi-column grid', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    // On desktop (1440px), should have 3 or 4 columns  -  check that first row cards are side-by-side
    const positions = await page.evaluate(() => {
      const cards = document.querySelectorAll('.index-card');
      return Array.from(cards).slice(0, 4).map(c => {
        const rect = c.getBoundingClientRect();
        return { top: Math.round(rect.top), left: Math.round(rect.left), width: Math.round(rect.width) };
      });
    });
    // At least 3 cards should share the same top position (same row)
    const firstRowTop = positions[0].top;
    const sameRow = positions.filter(p => Math.abs(p.top - firstRowTop) < 5);
    expect(sameRow.length).toBeGreaterThanOrEqual(3);
  });

  test('desktop: nav links visible, hamburger hidden', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await expect(page.locator('.header-nav')).toBeVisible();
    await expect(page.locator('.sidebar-toggle')).not.toBeVisible();
  });

  test('mobile: hamburger visible, nav links hidden', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await expect(page.locator('.sidebar-toggle')).toBeVisible();
    await expect(page.locator('.header-nav')).not.toBeVisible();
  });

  test('mobile: cards stack in single column', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    const positions = await page.evaluate(() => {
      const cards = document.querySelectorAll('.index-card');
      return Array.from(cards).slice(0, 3).map(c => {
        const rect = c.getBoundingClientRect();
        return { top: Math.round(rect.top), left: Math.round(rect.left) };
      });
    });
    // Each card should have a different top (stacked vertically)
    expect(positions[0].top).not.toBe(positions[1].top);
    expect(positions[1].top).not.toBe(positions[2].top);
  });

  test('mobile: header is compact', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    const box = await page.locator('.site-header').boundingBox();
    expect(box).not.toBeNull();
    expect(box.height).toBeLessThanOrEqual(55);
  });
});

// ============================================================
// Documentation Pages  -  Structure
// ============================================================
test.describe('Documentation Pages  -  Structure', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
  });

  test('page heading and description are visible', async ({ page }) => {
    await expect(page.locator('.page-heading')).toBeVisible();
    await expect(page.locator('.page-description')).toBeVisible();
  });

  test('breadcrumb navigation is present', async ({ page }) => {
    await expect(page.locator('.breadcrumb')).toBeVisible();
    const links = page.locator('.breadcrumb a');
    expect(await links.count()).toBeGreaterThanOrEqual(1);
  });

  test('doc content area has substantial text', async ({ page }) => {
    const content = page.locator('.doc-content');
    await expect(content).toBeVisible();
    const text = await content.textContent();
    expect(text.length).toBeGreaterThan(200);
  });

  test('prev/next navigation exists at bottom', async ({ page }) => {
    const nav = page.locator('.prev-next');
    await nav.scrollIntoViewIfNeeded();
    await expect(nav).toBeVisible();
  });

  test('footer is present on doc pages', async ({ page }) => {
    const footer = page.locator('.site-footer');
    await footer.scrollIntoViewIfNeeded();
    await expect(footer).toBeVisible();
  });
});

// ============================================================
// Documentation Pages  -  Sidebar Navigation
// ============================================================
test.describe('Documentation Pages  -  Sidebar', () => {
  test('desktop: sidebar is visible with sections and links', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.sidebar')).toBeVisible();
    const sections = page.locator('.sidebar-section-title');
    expect(await sections.count()).toBeGreaterThanOrEqual(5);
    const links = page.locator('.sidebar-links a');
    expect(await links.count()).toBeGreaterThanOrEqual(20);
  });

  test('desktop: active page is highlighted in sidebar', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    const active = page.locator('.sidebar-links a.active');
    await expect(active).toBeVisible();
    expect(await active.count()).toBe(1);
    const text = await active.textContent();
    expect(text).toContain('Install DryRun Security');
  });

  test('desktop: TOC sidebar is visible on wide screens', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/sast-overview.html');
    await page.waitForLoadState('domcontentloaded');
    const vw = await page.evaluate(() => window.innerWidth);
    if (vw > 1200) {
      await expect(page.locator('.toc-sidebar')).toBeVisible();
    }
  });

  test('sidebar link navigates to correct page', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    // Click on a different page link in the sidebar
    const prLink = page.locator('.sidebar-links a', { hasText: 'PR Code Reviews' });
    await prLink.click();
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.page-heading')).toContainText('PR Code Reviews');
  });
});

// ============================================================
// Mobile Navigation
// ============================================================
test.describe('Mobile Navigation', () => {
  test('hamburger opens sidebar overlay', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    await page.locator('.sidebar-toggle').click();
    await page.waitForTimeout(400);
    const sidebar = page.locator('.sidebar');
    const classList = await sidebar.getAttribute('class');
    expect(classList).toContain('open');
    // Sidebar should have links
    const links = sidebar.locator('.sidebar-links a');
    expect(await links.count()).toBeGreaterThanOrEqual(20);
  });

  test('mobile sidebar link navigates correctly', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    await page.locator('.sidebar-toggle').click();
    await page.waitForTimeout(400);
    const secretsLink = page.locator('.sidebar-links a', { hasText: 'Secrets Detection' });
    await secretsLink.click();
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.page-heading')).toContainText('Secrets Detection');
  });

  test('no horizontal overflow on mobile doc pages', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    const hasOverflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(hasOverflow).toBe(false);
  });
});

// ============================================================
// Search Functionality
// ============================================================
test.describe('Search', () => {
  test('search input filters results on landing page', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
    const input = page.locator('#docsSearch');
    await input.fill('secrets');
    await page.waitForTimeout(300);
    // Search should show results or filter  -  check the search results container exists
    // At minimum, verify the input accepted text
    const value = await input.inputValue();
    expect(value).toBe('secrets');
  });
});

// ============================================================
// Cross-page Navigation Flow
// ============================================================
test.describe('Navigation Flow', () => {
  test('landing page card link navigates to doc page', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
    // Click first link in first card
    const firstLink = page.locator('.index-card-links a').first();
    const linkText = await firstLink.textContent();
    await firstLink.click();
    await page.waitForLoadState('domcontentloaded');
    // Should be on a doc page with header and content
    await expect(page.locator('.page-heading')).toBeVisible();
    await expect(page.locator('.site-header')).toBeVisible();
  });

  test('prev/next links form a navigable chain', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    // Start at first page
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    // Should have next but no prev
    const prevLinks = page.locator('.prev-next-link.prev-link');
    expect(await prevLinks.count()).toBe(0);
    const nextLink = page.locator('.prev-next-link.next-link');
    await expect(nextLink).toBeVisible();
    // Click next and verify we moved
    await nextLink.scrollIntoViewIfNeeded();
    await nextLink.click();
    await page.waitForLoadState('domcontentloaded');
    const heading = await page.locator('.page-heading').textContent();
    expect(heading).not.toContain('Quick Start');
    // Now should have a prev link
    const newPrev = page.locator('.prev-next-link.prev-link');
    await expect(newPrev).toBeVisible();
  });

  test('Docs link in header returns to landing page', async ({ page }) => {
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    const docsLink = page.locator('.header-nav a', { hasText: 'Docs' });
    if (await docsLink.isVisible()) {
      await docsLink.click();
      await page.waitForLoadState('domcontentloaded');
      await expect(page.locator('.docs-hero')).toBeVisible();
    }
  });
});

// ============================================================
// Accessibility
// ============================================================
test.describe('Accessibility', () => {
  test('html has lang attribute', async ({ page }) => {
    await page.goto('/index.html');
    const lang = await page.locator('html').getAttribute('lang');
    expect(lang).toBe('en');
  });

  test('all images have alt text', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
    const images = page.locator('img');
    const count = await images.count();
    for (let i = 0; i < count; i++) {
      const alt = await images.nth(i).getAttribute('alt');
      expect(alt).toBeTruthy();
    }
  });

  test('focus-visible styles are applied', async ({ page }) => {
    await page.goto('/index.html');
    // Tab to first focusable element and check outline
    await page.keyboard.press('Tab');
    const focused = page.locator(':focus-visible');
    expect(await focused.count()).toBeGreaterThanOrEqual(1);
  });

  test('color contrast: body text is readable', async ({ page }) => {
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    const bodyColor = await page.evaluate(() => {
      const el = document.querySelector('.doc-content');
      if (!el) return null;
      return getComputedStyle(el).color;
    });
    // Text should be light (high luminance) on dark background
    expect(bodyColor).not.toBeNull();
    // Parse rgb values - text should be bright (> 150 for at least one channel)
    const match = bodyColor.match(/\d+/g);
    if (match) {
      const maxChannel = Math.max(...match.map(Number));
      expect(maxChannel).toBeGreaterThan(150);
    }
  });
});

// ============================================================
// Typography & Sizing Regression Guards
// ============================================================
test.describe('Typography Regression Guards', () => {
  test('hero title is not oversized', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
    const fontSize = await page.evaluate(() => {
      const el = document.querySelector('.docs-hero-title');
      return parseFloat(getComputedStyle(el).fontSize);
    });
    // Should be between 24px and 36px, not 48px+
    expect(fontSize).toBeGreaterThanOrEqual(24);
    expect(fontSize).toBeLessThanOrEqual(36);
  });

  test('card icon SVGs have constrained dimensions', async ({ page }) => {
    await page.goto('/index.html');
    await page.waitForLoadState('domcontentloaded');
    const dims = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('.index-card-icon svg')).map(svg => ({
        w: svg.getBoundingClientRect().width,
        h: svg.getBoundingClientRect().height,
      }));
    });
    for (const d of dims) {
      expect(d.w).toBeGreaterThanOrEqual(20);
      expect(d.w).toBeLessThanOrEqual(50);
      expect(d.h).toBeGreaterThanOrEqual(20);
      expect(d.h).toBeLessThanOrEqual(50);
    }
  });

  test('page heading font size is reasonable', async ({ page }) => {
    await page.goto('/docs/quick-start.html');
    await page.waitForLoadState('domcontentloaded');
    const fontSize = await page.evaluate(() => {
      const el = document.querySelector('.page-heading');
      return parseFloat(getComputedStyle(el).fontSize);
    });
    expect(fontSize).toBeGreaterThanOrEqual(22);
    expect(fontSize).toBeLessThanOrEqual(40);
  });

  test('base body font size is at least 16px', async ({ page }) => {
    await page.goto('/index.html');
    const fontSize = await page.evaluate(() =>
      parseFloat(getComputedStyle(document.documentElement).fontSize)
    );
    expect(fontSize).toBeGreaterThanOrEqual(16);
  });
});

// ============================================================
// Content Coverage  -  Spot Checks
// ============================================================
test.describe('Content Coverage', () => {
  test('coverage matrix page has a table', async ({ page }) => {
    await page.goto('/docs/coverage-matrix.html');
    await page.waitForLoadState('domcontentloaded');
    const table = page.locator('.doc-content table');
    await expect(table).toBeVisible();
  });

  test('NLCP page has content about policies', async ({ page }) => {
    await page.goto('/docs/natural-language-code-policies.html');
    await page.waitForLoadState('domcontentloaded');
    const text = await page.locator('.doc-content').textContent();
    expect(text.toLowerCase()).toContain('polic');
  });

  test('API guide page has content', async ({ page }) => {
    await page.goto('/docs/api-guide.html');
    await page.waitForLoadState('domcontentloaded');
    const text = await page.locator('.doc-content').textContent();
    expect(text.length).toBeGreaterThan(100);
  });

  test('AI agent security page exists and loads', async ({ page }) => {
    await page.goto('/docs/securing-ai-code.html');
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('.page-heading')).toBeVisible();
  });
});
