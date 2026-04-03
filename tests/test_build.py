"""
Unit tests for DryRun Security Documentation build system.
Run with: python3 -m pytest tests/test_build.py -v
"""
import re
import importlib.util
from pathlib import Path

# Load build.py as a module
BUILD_PATH = Path(__file__).parent.parent / "build.py"
spec = importlib.util.spec_from_file_location("build", BUILD_PATH)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"
CSS_PATH = ROOT / "style.css"
INDEX_PATH = ROOT / "index.html"


class TestDataIntegrity:
    """Verify all page data is complete and consistent."""

    def test_pages_not_empty(self):
        assert len(build.PAGES) >= 25, f"Should have at least 25 pages, got {len(build.PAGES)}"

    def test_sections_not_empty(self):
        assert len(build.SECTIONS) >= 5, f"Should have at least 5 sections, got {len(build.SECTIONS)}"

    def test_all_pages_have_required_fields(self):
        required = {"title", "description", "section", "content"}
        for slug, page in build.PAGES.items():
            missing = required - set(page.keys())
            assert not missing, f"Page '{slug}' missing fields: {missing}"

    def test_all_pages_have_nonempty_content(self):
        for slug, page in build.PAGES.items():
            assert len(page["content"].strip()) > 100, (
                f"Page '{slug}' has suspiciously short content ({len(page['content'])} chars)"
            )

    def test_all_section_slugs_exist_in_pages(self):
        for section in build.SECTIONS:
            for slug in section["pages"]:
                assert slug in build.PAGES, (
                    f"Section '{section['name']}' references slug '{slug}' not in PAGES"
                )

    def test_all_pages_belong_to_a_section(self):
        all_section_slugs = set()
        for section in build.SECTIONS:
            all_section_slugs.update(section["pages"])
        for slug in build.PAGES:
            assert slug in all_section_slugs, (
                f"Page '{slug}' is in PAGES but not in any SECTION"
            )

    def test_no_duplicate_slugs_in_sections(self):
        all_slugs = []
        for section in build.SECTIONS:
            for slug in section["pages"]:
                assert slug not in all_slugs, (
                    f"Duplicate slug '{slug}' found in section '{section['name']}'"
                )
                all_slugs.append(slug)

    def test_page_slugs_are_url_safe(self):
        for slug in build.PAGES:
            assert re.match(r'^[a-z0-9\-]+$', slug), (
                f"Slug '{slug}' is not URL-safe (use lowercase letters, numbers, hyphens)"
            )


class TestEscaping:
    """Verify HTML escaping is properly applied."""

    def test_esc_function_exists(self):
        assert hasattr(build, 'esc'), "build.py must define esc() function"

    def test_esc_escapes_html_chars(self):
        assert build.esc('<script>') == '&lt;script&gt;'
        assert build.esc('"hello"') == '&quot;hello&quot;'
        assert build.esc("it's") == "it&#x27;s"
        assert build.esc('a & b') == 'a &amp; b'

    def test_esc_handles_non_strings(self):
        assert build.esc(42) == '42'
        assert build.esc(None) == 'None'


class TestGeneratedFiles:
    """Verify generated HTML files have correct structure."""

    def test_index_exists(self):
        assert (ROOT / "index.html").exists()

    def test_all_doc_pages_exist(self):
        for slug in build.PAGES:
            page = DOCS_DIR / f"{slug}.html"
            assert page.exists(), f"Missing doc page: {page}"

    def test_sitemap_exists(self):
        assert (ROOT / "sitemap.xml").exists()

    def test_robots_txt_exists(self):
        assert (ROOT / "robots.txt").exists()

    def test_doc_pages_have_doctype(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert content.strip().startswith("<!DOCTYPE html"), (
                f"{html_file.name} missing DOCTYPE"
            )

    def test_doc_pages_have_favicon(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert 'favicon.ico' in content, (
                f"{html_file.name} missing favicon reference"
            )

    def test_doc_pages_have_header(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert 'site-header' in content, (
                f"{html_file.name} missing header"
            )

    def test_doc_pages_have_footer(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert 'site-footer' in content, (
                f"{html_file.name} missing footer"
            )

    def test_doc_pages_have_sidebar(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert 'sidebar' in content, (
                f"{html_file.name} missing sidebar"
            )

    def test_doc_pages_have_toc(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert 'toc-sidebar' in content, (
                f"{html_file.name} missing TOC sidebar"
            )

    def test_index_has_section_cards(self):
        content = (ROOT / "index.html").read_text()
        assert 'index-card' in content, "index.html missing section cards"

    def test_index_has_search_input(self):
        content = (ROOT / "index.html").read_text()
        assert 'search' in content.lower(), "index.html missing search"


class TestRelativePaths:
    """Verify no hardcoded domains in internal links."""

    def test_no_hardcoded_github_pages_url_in_html(self):
        for html_file in ROOT.glob("**/*.html"):
            content = html_file.read_text()
            assert 'wickett.github.io' not in content, (
                f"{html_file} contains hardcoded GitHub Pages URL"
            )

    def test_doc_pages_use_relative_css(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert '../style.css' in content, (
                f"{html_file.name} should reference ../style.css"
            )

    def test_doc_pages_have_inline_logo_svg(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert 'class="logo" viewBox="0 0 450 119"' in content, (
                f"{html_file.name} should contain inline logo SVG"
            )

    def test_root_page_uses_relative_css(self):
        content = (ROOT / "index.html").read_text()
        assert 'style.css' in content, "index.html should reference style.css"

    def test_external_links_have_target_blank(self):
        for html_file in ROOT.glob("**/*.html"):
            content = html_file.read_text()
            for match in re.finditer(r'<a\s+([^>]*href="https?://[^"]*"[^>]*)>', content):
                attrs = match.group(1)
                if 'dryrun.security' in attrs or 'g2.com' in attrs or 'linkedin.com' in attrs:
                    assert 'target="_blank"' in attrs, (
                        f"{html_file.name}: external link missing target=_blank: {attrs[:80]}"
                    )


class TestAccessibility:
    """Enforce accessibility standards."""

    @staticmethod
    def _parse_css():
        return (ROOT / "style.css").read_text()

    def test_base_font_size_at_least_16px(self):
        css = self._parse_css()
        match = re.search(r'html\s*\{[^}]*font-size:\s*(\d+)px', css)
        assert match, "Could not find html base font-size"
        base_px = int(match.group(1))
        assert base_px >= 16, f"Base font-size is {base_px}px, must be >= 16px"

    def test_muted_text_contrast(self):
        css = self._parse_css()
        match = re.search(r'--text-muted:\s*(#[0-9a-fA-F]{6})', css)
        assert match, "Could not find --text-muted CSS variable"
        hex_color = match.group(1).lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        avg = (r + g + b) / 3
        assert avg >= 140, (
            f"--text-muted color {match.group(1)} is too dark for accessibility. "
            f"Average channel brightness is {avg:.0f}, need >= 140."
        )

    def test_focus_visible_styles_exist(self):
        css = self._parse_css()
        assert 'focus-visible' in css, (
            "CSS must include :focus-visible styles for keyboard accessibility"
        )

    def test_all_images_have_alt_text(self):
        for html_file in ROOT.glob("**/*.html"):
            content = html_file.read_text()
            for match in re.finditer(r'<img\s+([^>]*)>', content):
                attrs = match.group(1)
                assert 'alt=' in attrs, (
                    f"{html_file.name}: <img> missing alt attribute: {attrs[:60]}"
                )

    def test_html_has_lang_attribute(self):
        content = (ROOT / "index.html").read_text()
        assert '<html lang=' in content.lower(), (
            "index.html missing lang attribute on <html> element"
        )

    def test_no_font_size_below_minimum(self):
        """No font-size in desktop CSS should be below 0.72rem (11.5px at 16px base).
        Mobile breakpoint is exempt."""
        css = self._parse_css()
        mobile_start = css.find('@media')
        desktop_css = css[:mobile_start] if mobile_start != -1 else css
        min_rem = 0.72
        violations = []
        for match in re.finditer(r'font-size:\s*([\d.]+)rem', desktop_css):
            val = float(match.group(1))
            if val < min_rem:
                start = max(0, match.start() - 80)
                context = desktop_css[start:match.start()].strip().split('\n')[-1]
                violations.append(f"{val}rem (near: ...{context})")
        assert not violations, (
            f"Font sizes below {min_rem}rem found in desktop CSS:\n" +
            "\n".join(f"  - {v}" for v in violations)
        )


class TestResponsiveCSS:
    """Regression guards for responsive layout issues."""

    @staticmethod
    def _parse_css():
        return (ROOT / "style.css").read_text()

    def test_card_icons_have_size_constraint(self):
        """Card SVG icons must have explicit size rules to prevent blow-up."""
        css = self._parse_css()
        assert '.index-card-icon svg' in css, (
            "CSS must constrain .index-card-icon svg dimensions"
        )
        # The SVG rule should set width and height
        svg_rule = css[css.index('.index-card-icon svg'):]
        svg_block = svg_rule[:svg_rule.index('}') + 1]
        assert 'width:' in svg_block, "icon SVG rule must set width"
        assert 'height:' in svg_block, "icon SVG rule must set height"

    def test_card_icon_size_is_reasonable(self):
        """Card icons should be 24-50px, not 300px+."""
        css = self._parse_css()
        svg_start = css.index('.index-card-icon svg')
        svg_block = css[svg_start:css.index('}', svg_start) + 1]
        width_match = re.search(r'width:\s*(\d+)px', svg_block)
        assert width_match, "Could not find icon SVG width in px"
        width = int(width_match.group(1))
        assert 24 <= width <= 50, f"Icon width is {width}px, should be 24-50px"

    def test_grid_uses_explicit_columns(self):
        """Card grid must use explicit column counts, not unbounded auto-fill."""
        css = self._parse_css()
        # Find the .index-cards-inner block
        idx = css.index('.index-cards-inner')
        block = css[idx:css.index('}', idx) + 1]
        # Should NOT use auto-fill (which caused oversized cards)
        assert 'auto-fill' not in block, (
            "Card grid should use explicit repeat() counts, not auto-fill"
        )

    def test_mobile_breakpoint_exists(self):
        """CSS must define mobile responsive rules."""
        css = self._parse_css()
        assert '@media (max-width: 600px)' in css, (
            "Missing mobile breakpoint at 600px"
        )
        assert '@media (max-width: 900px)' in css, (
            "Missing tablet breakpoint at 900px"
        )

    def test_sidebar_toggle_hidden_by_default(self):
        """Hamburger menu must be hidden at desktop widths."""
        css = self._parse_css()
        toggle_idx = css.index('.sidebar-toggle')
        toggle_block = css[toggle_idx:css.index('}', toggle_idx) + 1]
        assert 'display: none' in toggle_block or 'display:none' in toggle_block, (
            "Sidebar toggle (hamburger) must be display:none by default"
        )

    def test_header_nav_visible_by_default(self):
        """Desktop nav links must be visible by default."""
        css = self._parse_css()
        nav_idx = css.index('.header-nav')
        nav_block = css[nav_idx:css.index('}', nav_idx) + 1]
        assert 'display: flex' in nav_block or 'display:flex' in nav_block, (
            "Header nav must be display:flex by default for desktop"
        )


class TestSidebarNavigation:
    """Verify sidebar navigation is consistent across pages."""

    def test_every_page_has_active_link_in_sidebar(self):
        for slug in build.PAGES:
            page_file = DOCS_DIR / f"{slug}.html"
            content = page_file.read_text()
            assert 'class="active"' in content, (
                f"{slug}.html has no active sidebar link"
            )

    def test_prev_next_links_form_chain(self):
        """First page should have no prev, last page should have no next."""
        all_slugs = []
        for section in build.SECTIONS:
            all_slugs.extend(section["pages"])

        first_page = DOCS_DIR / f"{all_slugs[0]}.html"
        first_content = first_page.read_text()
        assert 'class="prev-next-link prev-link"' not in first_content, (
            f"First page '{all_slugs[0]}' should not have a previous link"
        )

        last_page = DOCS_DIR / f"{all_slugs[-1]}.html"
        last_content = last_page.read_text()
        assert 'class="prev-next-link next-link"' not in last_content, (
            f"Last page '{all_slugs[-1]}' should not have a next link"
        )


class TestUIQualityCSS:
    """CSS guards for UI quality - prevent regressions in typography, contrast, spacing."""

    def test_body_text_uses_readable_color_token(self):
        """Body text (--text-body) should be distinct from --text-muted."""
        css = CSS_PATH.read_text()
        assert '--text-body:' in css, "CSS must define --text-body token for readable body text"
        assert '--text-muted:' in css, "CSS must define --text-muted token"
        # Extract hex values
        import re
        body_match = re.search(r'--text-body:\s*(#[0-9a-fA-F]+)', css)
        muted_match = re.search(r'--text-muted:\s*(#[0-9a-fA-F]+)', css)
        assert body_match and muted_match
        assert body_match.group(1) != muted_match.group(1), (
            "--text-body and --text-muted must be different colors"
        )

    def test_page_heading_size_is_authoritative(self):
        """Page heading should be at least 2rem."""
        css = CSS_PATH.read_text()
        import re
        match = re.search(r'\.page-heading\s*\{[^}]*font-size:\s*([\d.]+)rem', css)
        assert match, ".page-heading must have a font-size in rem"
        size = float(match.group(1))
        assert size >= 2.0, f".page-heading font-size should be >= 2rem, got {size}rem"

    def test_h2_size_hierarchy(self):
        """h2 should be at least 1.4rem."""
        css = CSS_PATH.read_text()
        import re
        match = re.search(r'\.doc-content h2\s*\{[^}]*font-size:\s*([\d.]+)rem', css)
        assert match, ".doc-content h2 must have a font-size in rem"
        size = float(match.group(1))
        assert size >= 1.4, f"h2 font-size should be >= 1.4rem, got {size}rem"

    def test_content_area_has_generous_padding(self):
        """Content area should have at least 40px horizontal padding."""
        css = CSS_PATH.read_text()
        import re
        match = re.search(r'\.content-area\s*\{[^}]*padding:\s*([^;]+)', css)
        assert match, ".content-area must have padding defined"
        # padding shorthand: top right bottom left or top horizontal bottom
        padding_val = match.group(1).strip()
        parts = padding_val.replace('px', '').split()
        if len(parts) >= 2:
            horizontal = float(parts[1])
        else:
            horizontal = float(parts[0])
        assert horizontal >= 40, f"Content horizontal padding should be >= 40px, got {horizontal}px"

    def test_copy_button_is_styled(self):
        """Copy button should have proper CSS styling."""
        css = CSS_PATH.read_text()
        assert '.copy-btn' in css, "CSS must style .copy-btn"
        assert 'position: absolute' in css or 'position:absolute' in css, (
            "Copy button should be absolutely positioned"
        )

    def test_sidebar_link_padding_is_adequate(self):
        """Sidebar links should have at least 6px vertical padding for tap targets."""
        css = CSS_PATH.read_text()
        import re
        match = re.search(r'\.sidebar-links a\s*\{[^}]*padding:\s*([^;]+)', css)
        assert match, ".sidebar-links a must have padding"
        padding_val = match.group(1).strip()
        parts = padding_val.replace('px', '').split()
        top_padding = float(parts[0])
        assert top_padding >= 6, f"Sidebar link vertical padding should be >= 6px, got {top_padding}px"

    def test_table_has_border_styling(self):
        """Tables should have border for visual definition."""
        css = CSS_PATH.read_text()
        import re
        match = re.search(r'\.doc-content table\s*\{[^}]*border:', css)
        assert match, ".doc-content table should have border styling"

    def test_no_em_dashes_in_css(self):
        """CSS should not contain em dashes."""
        css = CSS_PATH.read_text()
        assert '\u2014' not in css, "CSS should not contain em dashes"

    def test_keyboard_shortcut_hint_exists(self):
        """Index page should have keyboard shortcut hint on search."""
        index = INDEX_PATH.read_text()
        assert 'docs-search-kbd' in index, "Index should have keyboard shortcut hint on search"
