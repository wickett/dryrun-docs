/**
 * DryRun Security Docs - app.js
 * Handles: mobile sidebar toggle, TOC active state on scroll, smooth scroll,
 * docs search (index page), keyboard shortcuts, and copy buttons.
 */

(function () {
  'use strict';

  // -------------------------------------------------------------------------
  // Mobile sidebar toggle
  // -------------------------------------------------------------------------
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', function () {
      const isOpen = sidebar.classList.toggle('open');
      if (sidebarOverlay) {
        sidebarOverlay.style.display = isOpen ? 'block' : 'none';
      }
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', function () {
      if (sidebar) sidebar.classList.remove('open');
      sidebarOverlay.style.display = 'none';
    });
  }

  // Close sidebar on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
      sidebar.classList.remove('open');
      if (sidebarOverlay) sidebarOverlay.style.display = 'none';
    }
  });

  // -------------------------------------------------------------------------
  // TOC active state tracking on scroll
  // -------------------------------------------------------------------------
  const tocLinks = document.querySelectorAll('.toc-list a');
  const headings = document.querySelectorAll('.doc-content h2, .doc-content h3');

  if (tocLinks.length > 0 && headings.length > 0) {
    let activeLink = null;

    function setActiveLink(link) {
      if (activeLink === link) return;
      if (activeLink) activeLink.classList.remove('active');
      activeLink = link;
      if (activeLink) activeLink.classList.add('active');
    }

    function updateActiveToc() {
      const scrollY = window.scrollY + 100; // offset for header
      let current = null;

      for (let i = headings.length - 1; i >= 0; i--) {
        const heading = headings[i];
        if (heading.offsetTop <= scrollY) {
          current = heading;
          break;
        }
      }

      if (current) {
        const id = current.getAttribute('id');
        if (id) {
          const matchingLink = document.querySelector('.toc-list a[href="#' + CSS.escape(id) + '"]');
          if (matchingLink) {
            setActiveLink(matchingLink);
          }
        }
      } else if (tocLinks.length > 0) {
        setActiveLink(tocLinks[0]);
      }
    }

    // Throttled scroll handler
    let scrollTicking = false;
    window.addEventListener('scroll', function () {
      if (!scrollTicking) {
        requestAnimationFrame(function () {
          updateActiveToc();
          scrollTicking = false;
        });
        scrollTicking = true;
      }
    }, { passive: true });

    // Initial state
    updateActiveToc();
  }

  // -------------------------------------------------------------------------
  // Smooth scroll for anchor links
  // -------------------------------------------------------------------------
  document.addEventListener('click', function (e) {
    const target = e.target.closest('a[href^="#"]');
    if (!target) return;
    const href = target.getAttribute('href');
    if (!href || href === '#') return;

    const id = href.slice(1);
    const el = document.getElementById(id);
    if (!el) return;

    e.preventDefault();
    const headerHeight = document.querySelector('.site-header')
      ? document.querySelector('.site-header').offsetHeight
      : 56;
    const top = el.getBoundingClientRect().top + window.scrollY - headerHeight - 16;
    window.scrollTo({ top: Math.max(0, top), behavior: 'smooth' });

    // Update URL without triggering scroll
    history.pushState(null, '', href);
  });

  // -------------------------------------------------------------------------
  // Docs index search (index.html only) + keyboard shortcut
  // -------------------------------------------------------------------------
  const docsSearch = document.getElementById('docsSearch');
  if (docsSearch) {
    const cards = document.querySelectorAll('.index-card');

    docsSearch.addEventListener('input', function () {
      const query = this.value.trim().toLowerCase();

      cards.forEach(function (card) {
        if (!query) {
          card.style.display = '';
          // Reset all links visibility
          card.querySelectorAll('.index-card-links li').forEach(function (li) {
            li.style.display = '';
          });
          return;
        }

        // Check card title and description
        const cardTitle = (card.querySelector('.index-card-title') || {}).textContent || '';
        const cardDesc = (card.querySelector('.index-card-desc') || {}).textContent || '';
        let cardMatches = cardTitle.toLowerCase().includes(query) || cardDesc.toLowerCase().includes(query);

        // Check individual links
        let anyLinkVisible = false;
        card.querySelectorAll('.index-card-links li').forEach(function (li) {
          const linkText = li.textContent.toLowerCase();
          const linkMatches = linkText.includes(query);
          li.style.display = (cardMatches || linkMatches) ? '' : 'none';
          if (linkMatches) anyLinkVisible = true;
        });

        card.style.display = (cardMatches || anyLinkVisible) ? '' : 'none';
      });
    });

    // Clear search on Escape
    docsSearch.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        this.value = '';
        this.dispatchEvent(new Event('input'));
        this.blur();
      }
    });

    // Cmd/Ctrl+K to focus search
    document.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        docsSearch.focus();
        docsSearch.select();
      }
    });
  }

  // -------------------------------------------------------------------------
  // Sidebar active link scroll into view
  // -------------------------------------------------------------------------
  const activeNavLink = document.querySelector('.sidebar-links .active');
  if (activeNavLink) {
    activeNavLink.scrollIntoView({ block: 'nearest', behavior: 'auto' });
  }

  // -------------------------------------------------------------------------
  // Code block copy button
  // -------------------------------------------------------------------------
  document.querySelectorAll('.doc-content pre').forEach(function (pre) {
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = 'Copy';
    btn.setAttribute('aria-label', 'Copy code to clipboard');
    pre.appendChild(btn);

    btn.addEventListener('click', function () {
      const code = pre.querySelector('code');
      const text = code ? code.textContent : pre.textContent;
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = 'Copied';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 2000);
      }).catch(function () {
        btn.textContent = 'Error';
        setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
      });
    });
  });

})();
