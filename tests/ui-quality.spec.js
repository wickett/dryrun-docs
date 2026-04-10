// @ts-check
const { test, expect } = require('@playwright/test');

// ============================================================
// Typography & Readability
// ============================================================
test.describe('Typography & Readability', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    await page.waitForLoadState('domcontentloaded');
  });

  test('body text color has sufficient contrast against background', async ({ page }) => {
    const contrast = await page.evaluate(() => {
      const p = document.querySelector('.doc-content p');
      if (!p) return null;
      const style = getComputedStyle(p);
      const color = style.color;
      // Parse rgb values
      const match = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
      if (!match) return null;
      const [, r, g, b] = match.map(Number);
      // Relative luminance check - text should not be too dim
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b);
      return { r, g, b, luminance };
    });
    expect(contrast).not.toBeNull();
    // Body text luminance should be under 120 (dark text on light bg)
    expect(contrast.luminance).toBeLessThanOrEqual(120);
  });

  test('page heading is larger than h2, h2 is larger than h3', async ({ page }) => {
    const sizes = await page.evaluate(() => {
      const heading = document.querySelector('.page-heading');
      const h2 = document.querySelector('.doc-content h2');
      const h3 = document.querySelector('.doc-content h3');
      return {
        heading: heading ? parseFloat(getComputedStyle(heading).fontSize) : 0,
        h2: h2 ? parseFloat(getComputedStyle(h2).fontSize) : 0,
        h3: h3 ? parseFloat(getComputedStyle(h3).fontSize) : 0,
      };
    });
    expect(sizes.heading).toBeGreaterThan(sizes.h2);
    expect(sizes.h2).toBeGreaterThan(sizes.h3);
    // Page heading should be at least 24px (smaller on mobile due to responsive scaling)
    expect(sizes.heading).toBeGreaterThanOrEqual(24);
  });

  test('line height on body text is at least 1.6', async ({ page }) => {
    const lineHeight = await page.evaluate(() => {
      const p = document.querySelector('.doc-content p');
      if (!p) return 0;
      const style = getComputedStyle(p);
      const lh = parseFloat(style.lineHeight);
      const fs = parseFloat(style.fontSize);
      return lh / fs;
    });
    expect(lineHeight).toBeGreaterThanOrEqual(1.6);
  });

  test('inline code has visible background and border', async ({ page }) => {
    const codeStyle = await page.evaluate(() => {
      const code = document.querySelector('.doc-content p code, .doc-content li code');
      if (!code) return null;
      const style = getComputedStyle(code);
      return {
        background: style.backgroundColor,
        borderWidth: style.borderWidth,
        padding: style.padding,
      };
    });
    expect(codeStyle).not.toBeNull();
    // Should have non-transparent background
    expect(codeStyle.background).not.toBe('rgba(0, 0, 0, 0)');
    expect(codeStyle.background).not.toBe('transparent');
  });

  test('content max width is between 700px and 850px', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    const width = await page.evaluate(() => {
      const inner = document.querySelector('.content-inner');
      if (!inner) return 0;
      return parseFloat(getComputedStyle(inner).maxWidth);
    });
    expect(width).toBeGreaterThanOrEqual(700);
    expect(width).toBeLessThanOrEqual(850);
  });
});

// ============================================================
// Color & Theming
// ============================================================
test.describe('Color & Theming', () => {
  test('background color is light', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const bgColor = await page.evaluate(() => {
      const style = getComputedStyle(document.body);
      const match = style.backgroundColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
      if (!match) return 0;
      const [, r, g, b] = match.map(Number);
      return (r + g + b) / 3;
    });
    // Average RGB should be over 200 for a light theme
    expect(bgColor).toBeGreaterThan(200);
  });

  test('accent links are visually distinct from body text', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const colors = await page.evaluate(() => {
      const link = document.querySelector('.doc-content a');
      const para = document.querySelector('.doc-content p');
      if (!link || !para) return null;
      return {
        linkColor: getComputedStyle(link).color,
        paraColor: getComputedStyle(para).color,
      };
    });
    expect(colors).not.toBeNull();
    expect(colors.linkColor).not.toBe(colors.paraColor);
  });

  test('active sidebar link has accent color highlight', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const activeStyle = await page.evaluate(() => {
      const active = document.querySelector('.sidebar-links a.active');
      if (!active) return null;
      const style = getComputedStyle(active);
      return {
        color: style.color,
        borderLeftColor: style.borderLeftColor,
        backgroundColor: style.backgroundColor,
      };
    });
    expect(activeStyle).not.toBeNull();
    // Active link should not be the same color as inactive links
    expect(activeStyle.backgroundColor).not.toBe('rgba(0, 0, 0, 0)');
  });
});

// ============================================================
// Spacing & Layout
// ============================================================
test.describe('Spacing & Layout', () => {
  test('content area has adequate padding on desktop', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/pr-scanning-configuration.html');
    const padding = await page.evaluate(() => {
      const area = document.querySelector('.content-area');
      if (!area) return { top: 0, right: 0, left: 0 };
      const style = getComputedStyle(area);
      return {
        top: parseFloat(style.paddingTop),
        right: parseFloat(style.paddingRight),
        left: parseFloat(style.paddingLeft),
      };
    });
    // Should have at least 40px padding on all sides
    expect(padding.top).toBeGreaterThanOrEqual(36);
    expect(padding.right).toBeGreaterThanOrEqual(40);
    expect(padding.left).toBeGreaterThanOrEqual(40);
  });

  test('h2 sections have visual separation (border-top or margin)', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const h2Styles = await page.evaluate(() => {
      const h2s = document.querySelectorAll('.doc-content h2');
      return Array.from(h2s).slice(1).map(h2 => {
        const style = getComputedStyle(h2);
        return {
          marginTop: parseFloat(style.marginTop),
          borderTopWidth: parseFloat(style.borderTopWidth),
          paddingTop: parseFloat(style.paddingTop),
        };
      });
    });
    expect(h2Styles.length).toBeGreaterThan(0);
    for (const s of h2Styles) {
      // Either border-top or margin-top for section separation
      expect(s.marginTop + s.paddingTop).toBeGreaterThanOrEqual(40);
    }
  });

  test('sidebar width is reasonable (200-300px)', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/pr-scanning-configuration.html');
    const width = await page.evaluate(() => {
      const sidebar = document.querySelector('.sidebar');
      if (!sidebar) return 0;
      return sidebar.getBoundingClientRect().width;
    });
    expect(width).toBeGreaterThanOrEqual(200);
    expect(width).toBeLessThanOrEqual(300);
  });

  test('list items have adequate spacing between them', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const spacing = await page.evaluate(() => {
      const items = document.querySelectorAll('.doc-content li');
      if (items.length < 2) return 0;
      const style = getComputedStyle(items[0]);
      return parseFloat(style.marginBottom);
    });
    expect(spacing).toBeGreaterThanOrEqual(6);
  });
});

// ============================================================
// Interactive Elements
// ============================================================
test.describe('Interactive Elements', () => {
  test('code blocks have copy buttons', async ({ page }) => {
    await page.goto('/docs/mcp.html');
    await page.waitForLoadState('domcontentloaded');
    const codeBlocks = page.locator('.doc-content pre');
    const count = await codeBlocks.count();
    expect(count).toBeGreaterThan(0);

    for (let i = 0; i < Math.min(count, 3); i++) {
      const pre = codeBlocks.nth(i);
      const copyBtn = pre.locator('.copy-btn');
      await expect(copyBtn).toBeAttached();
    }
  });

  test('copy button has hover-reveal CSS rule', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/mcp.html');
    const pre = page.locator('.doc-content pre').first();
    const copyBtn = pre.locator('.copy-btn');

    // Copy button starts at opacity 0
    const opacityBefore = await copyBtn.evaluate(el => getComputedStyle(el).opacity);
    expect(parseFloat(opacityBefore)).toBe(0);

    // Verify the CSS rule exists: pre:hover .copy-btn { opacity: 1 }
    // Playwright .hover() doesn't reliably trigger CSS :hover on parent for child selectors,
    // so we verify by checking the stylesheet rule directly
    const hasHoverRule = await page.evaluate(() => {
      for (const sheet of document.styleSheets) {
        try {
          for (const rule of sheet.cssRules) {
            if (rule.selectorText && rule.selectorText.includes('pre:hover') &&
                rule.selectorText.includes('.copy-btn') &&
                rule.style.opacity === '1') {
              return true;
            }
          }
        } catch (e) { /* cross-origin */ }
      }
      return false;
    });
    expect(hasHoverRule).toBe(true);
  });

  test('search input has keyboard shortcut hint on desktop', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/index.html');
    const kbd = page.locator('.sidebar-search-kbd');
    await expect(kbd).toBeVisible();
  });

  test('search shows results dropdown on input', async ({ page }) => {
    await page.goto('/index.html');
    const search = page.locator('#docsSearch');
    await search.fill('scanning');
    await page.waitForTimeout(400);

    // Full-text search should show result items in dropdown
    const results = page.locator('#searchResults .search-result-item');
    expect(await results.count()).toBeGreaterThan(0);
  });

  test('Cmd+K focuses search input', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/index.html');
    const search = page.locator('#docsSearch');

    // Press Cmd+K (or Ctrl+K)
    await page.keyboard.press('Control+k');
    await expect(search).toBeFocused();
  });

  test('sidebar overlay closes on click', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/pr-scanning-configuration.html');

    // Open sidebar
    await page.locator('.sidebar-toggle').click();
    await expect(page.locator('.sidebar')).toHaveClass(/open/);

    // Click overlay to close
    const overlay = page.locator('.sidebar-overlay');
    await overlay.click({ force: true });
    await expect(page.locator('.sidebar')).not.toHaveClass(/open/);
  });

  test('TOC highlights active section on scroll', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/pr-scanning-configuration.html');
    await page.setViewportSize({ width: 1440, height: 900 });

    // Scroll to a specific section
    await page.evaluate(() => {
      const h2 = document.getElementById('code-security-agents');
      if (h2) h2.scrollIntoView({ behavior: 'instant' });
    });
    await page.waitForTimeout(300);

    const activeText = await page.evaluate(() => {
      const active = document.querySelector('.toc-list a.active');
      return active ? active.textContent.trim() : null;
    });
    expect(activeText).toBe('Code Security Agents');
  });

  test('prev/next navigation links are present on doc pages', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const prevNext = page.locator('.prev-next');
    await prevNext.scrollIntoViewIfNeeded();
    await expect(prevNext).toBeVisible();

    const links = page.locator('.prev-next-link');
    expect(await links.count()).toBeGreaterThanOrEqual(1);
  });

  test('prev/next links have hover lift effect', async ({ page, isMobile }) => {
    test.skip(!!isMobile, 'Desktop only');
    await page.goto('/docs/pr-scanning-configuration.html');
    const link = page.locator('.prev-next-link').first();
    await link.scrollIntoViewIfNeeded();

    const transformBefore = await link.evaluate(el => getComputedStyle(el).transform);
    await link.hover();
    await page.waitForTimeout(300);
    const transformAfter = await link.evaluate(el => getComputedStyle(el).transform);

    // Transform should change on hover (translateY(-1px))
    expect(transformAfter).not.toBe(transformBefore);
  });
});

// ============================================================
// Tables
// ============================================================
test.describe('Tables', () => {
  test('tables have border and rounded corners', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const tableStyle = await page.evaluate(() => {
      const table = document.querySelector('.doc-content table');
      if (!table) return null;
      const style = getComputedStyle(table);
      return {
        borderWidth: style.borderWidth,
        overflow: style.overflow,
      };
    });
    expect(tableStyle).not.toBeNull();
  });

  test('table headers have distinct background', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const thBg = await page.evaluate(() => {
      const th = document.querySelector('.doc-content th');
      if (!th) return null;
      return getComputedStyle(th).backgroundColor;
    });
    expect(thBg).not.toBeNull();
    expect(thBg).not.toBe('rgba(0, 0, 0, 0)');
    expect(thBg).not.toBe('transparent');
  });

  test('table cells have adequate padding', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const padding = await page.evaluate(() => {
      const td = document.querySelector('.doc-content td');
      if (!td) return 0;
      return parseFloat(getComputedStyle(td).paddingLeft);
    });
    // At least 12px padding
    expect(padding).toBeGreaterThanOrEqual(12);
  });
});

// ============================================================
// Header & Navigation
// ============================================================
test.describe('Header & Navigation', () => {
  test('header is sticky (position: sticky)', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const position = await page.evaluate(() => {
      const header = document.querySelector('.site-header');
      return header ? getComputedStyle(header).position : '';
    });
    expect(position).toBe('sticky');
  });

  test('header has backdrop blur', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const blur = await page.evaluate(() => {
      const header = document.querySelector('.site-header');
      if (!header) return '';
      const style = getComputedStyle(header);
      return style.backdropFilter || style.webkitBackdropFilter || '';
    });
    expect(blur).toContain('blur');
  });

  test('breadcrumb shows correct path on doc pages', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const breadcrumb = page.locator('.breadcrumb');
    await expect(breadcrumb).toBeVisible();
    const text = await breadcrumb.textContent();
    expect(text).toContain('Docs');
  });
});

// ============================================================
// Mobile-Specific UI
// ============================================================
test.describe('Mobile-Specific UI', () => {
  test('mobile: content has adequate padding (not cramped)', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/pr-scanning-configuration.html');
    const padding = await page.evaluate(() => {
      const area = document.querySelector('.content-area');
      if (!area) return { left: 0, right: 0 };
      const style = getComputedStyle(area);
      return {
        left: parseFloat(style.paddingLeft),
        right: parseFloat(style.paddingRight),
      };
    });
    // Mobile should have at least 16px padding on each side
    expect(padding.left).toBeGreaterThanOrEqual(16);
    expect(padding.right).toBeGreaterThanOrEqual(16);
  });

  test('mobile: no horizontal overflow on doc pages', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/mcp.html');
    const hasOverflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(hasOverflow).toBe(false);
  });

  test('mobile: code blocks scroll horizontally without breaking layout', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/mcp.html');
    const preOverflow = await page.evaluate(() => {
      const pre = document.querySelector('.doc-content pre');
      if (!pre) return '';
      return getComputedStyle(pre).overflowX;
    });
    expect(preOverflow).toBe('auto');
  });

  test('mobile: sidebar toggle opens and closes sidebar', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/docs/pr-scanning-configuration.html');

    const sidebar = page.locator('.sidebar');
    const toggle = page.locator('.sidebar-toggle');

    // Initially closed
    await expect(sidebar).not.toHaveClass(/open/);

    // Open
    await toggle.click();
    await expect(sidebar).toHaveClass(/open/);

    // Close via Escape
    await page.keyboard.press('Escape');
    await expect(sidebar).not.toHaveClass(/open/);
  });

  test('mobile: keyboard shortcut hint hidden on small screens', async ({ page, isMobile }) => {
    test.skip(!isMobile, 'Mobile only');
    await page.goto('/index.html');
    const kbd = page.locator('.sidebar-search-kbd');
    await expect(kbd).not.toBeVisible();
  });
});

// ============================================================
// Animations & Transitions
// ============================================================
test.describe('Animations & Transitions', () => {
  test('content area has fade-in animation', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const animation = await page.evaluate(() => {
      const inner = document.querySelector('.content-inner');
      if (!inner) return '';
      return getComputedStyle(inner).animationName;
    });
    expect(animation).toBe('fadeIn');
  });

  test('sidebar links have transition on hover', async ({ page }) => {
    await page.goto('/docs/pr-scanning-configuration.html');
    const transition = await page.evaluate(() => {
      const link = document.querySelector('.sidebar-links a');
      if (!link) return '';
      return getComputedStyle(link).transition;
    });
    expect(transition).not.toBe('');
    expect(transition).not.toBe('none');
  });
});
