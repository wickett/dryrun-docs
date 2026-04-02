"""
Unit tests for DryRun Security Documentation build system.
Run with: python3 -m pytest tests/test_build.py -v
"""
import os
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


class TestDataIntegrity:
    """Verify all page data is complete and consistent."""

    def test_pages_not_empty(self):
        assert len(build.PAGES) >= 30, f"Should have at least 30 pages, got {len(build.PAGES)}"

    def test_sections_not_empty(self):
        assert len(build.SECTIONS) >= 7, f"Should have at least 7 sections, got {len(build.SECTIONS)}"

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
            assert 'favicon.png' in content, (
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

    def test_doc_pages_use_relative_logo(self):
        for html_file in DOCS_DIR.glob("*.html"):
            content = html_file.read_text()
            assert '../assets/logo.svg' in content, (
                f"{html_file.name} should reference ../assets/logo.svg"
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
