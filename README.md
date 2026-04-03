# DryRun Security Docs

Source for the [DryRun Security documentation site](https://docs.dryrun.security) — a static site built with vanilla HTML/CSS/JS and a Python generator.

## How it works

All page content is defined as Python data structures in [`build.py`](./build.py). Running the generator produces every HTML file in the repo — nothing is hand-edited in `docs/`.

```
build.py          # Site generator — all page content and structure lives here
style.css         # Brand styles (dark theme, #C8FF09 accent, Inter + JetBrains Mono)
app.js            # Mobile sidebar, TOC scroll tracking, search, copy buttons
index.html        # Landing page (generated)
docs/*.html       # Individual documentation pages (generated)
assets/           # Logo SVG, favicon, and screenshot images
tests/            # Unit tests and Playwright visual tests
```

### Page structure

Pages are organized into sections (Getting Started, Scanning, AI & Intelligence, etc.). Each page is a dict with four fields:

```python
PAGES['my-page'] = {
    'title': 'Page Title',
    'description': 'One-sentence description for meta tags and the page subtitle.',
    'section': 'Section Name',
    'content': '''
<h2 id="overview">Overview</h2>
<p>Content goes here as raw HTML.</p>
''',
}
```

The slug must also be added to the appropriate section in `SECTIONS` to appear in the sidebar and navigation.

## Local development

**Prerequisites:** Python 3.12+, Node.js 20+

```bash
# Regenerate all HTML pages
python3 build.py

# Run unit tests
pip install pytest
python3 -m pytest tests/ -v

# Run Playwright visual tests
npm install
npx playwright install chromium
npx playwright test
```

The generated files (`index.html`, `docs/*.html`, `sitemap.xml`, `robots.txt`) are committed to the repo and served directly by GitHub Pages. Always run `python3 build.py` and commit the output alongside any changes to `build.py`.

## Contributing

### Adding a new page

1. Add a new entry to `PAGES` in `build.py` with `title`, `description`, `section`, and `content`.
2. Add the slug to the correct section's `pages` list in `SECTIONS`.
3. Run `python3 build.py` to regenerate.
4. Run `python3 -m pytest tests/ -v` to verify data integrity and structure.
5. Open a PR — DryRun Security will automatically review it.

### Editing existing content

All content is in the `PAGES` dict in `build.py`. Find the relevant slug, edit the `content` string, then re-run `python3 build.py`.

### Coding conventions

- All string values interpolated into HTML **must** use the `esc()` helper — never interpolate raw strings directly.
- Internal links use relative paths (`./`, `../`). No hardcoded domain names.
- External links use full URLs with `target="_blank" rel="noopener noreferrer"`.
- The brand name is **DryRun Security** (no space between Dry and Run).
- CSS custom properties follow the established pattern (`--bg-primary`, `--accent`, `--green`, etc.) — don't introduce new ones without updating both `style.css` and the existing pages.

### CI checks

Every PR runs four automated checks:

| Check | What it does |
|---|---|
| **Lint** | Ruff (Python), stylelint (CSS), node --check (JS), htmlhint (generated HTML) |
| **Unit Tests** | Data integrity, HTML escaping, sidebar/TOC/nav structure |
| **Visual & UI Tests** | Playwright tests at desktop (1440×900) and mobile (390×844) |
| **Link Check** | Verifies all internal links resolve to real pages |

All checks must pass before merging. If DryRun Security flags a security finding on the PR, address it before merge — see [AGENTS.md](./AGENTS.md) for the remediation workflow.

## Security

This repo is monitored by [DryRun Security](https://dryrun.security). Every PR is automatically reviewed by the full analyzer suite including XSS, injection, secrets detection, and custom code policies. See [AGENTS.md](./AGENTS.md) for details on how findings are surfaced and how to resolve them.
