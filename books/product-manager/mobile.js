(function () {
  'use strict';

  function isMobile() { return window.innerWidth <= 768; }

  function init() {
    var book = document.querySelector('.book');
    if (!book) return;

    // ── 1. Start with sidebar closed on mobile ──────────────
    if (isMobile()) {
      book.classList.remove('with-summary');
      book.classList.add('without-summary');
    }

    // ── 2. Inject our own hamburger button ──────────────────
    if (!document.getElementById('pth-menu-btn')) {
      var btn = document.createElement('button');
      btn.id = 'pth-menu-btn';
      btn.setAttribute('aria-label', 'Toggle navigation');
      btn.innerHTML = '&#9776; Contents';
      document.body.appendChild(btn);

      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var open = book.classList.contains('mobile-sidebar-open');
        if (open) {
          book.classList.remove('mobile-sidebar-open');
        } else {
          book.classList.add('mobile-sidebar-open');
        }
      });
    }

    // ── 3. Tap outside sidebar (backdrop) to close ──────────
    document.addEventListener('click', function (e) {
      if (!isMobile()) return;
      if (!book.classList.contains('mobile-sidebar-open')) return;
      if (e.target.id === 'pth-menu-btn') return;
      var sidebar = document.querySelector('.book-summary');
      if (sidebar && !sidebar.contains(e.target)) {
        book.classList.remove('mobile-sidebar-open');
      }
    });

    // ── 4. Closing sidebar links navigates + closes ─────────
    var summary = document.querySelector('.book-summary');
    if (summary) {
      summary.addEventListener('click', function (e) {
        if (isMobile() && e.target.closest('a')) {
          book.classList.remove('mobile-sidebar-open');
        }
      });
    }

    // ── 5. Restore on resize to desktop ─────────────────────
    window.addEventListener('resize', function () {
      if (!isMobile()) {
        book.classList.remove('mobile-sidebar-open');
        book.classList.add('with-summary');
        book.classList.remove('without-summary');
        var b = document.getElementById('pth-menu-btn');
        if (b) b.style.display = 'none';
      } else {
        var b = document.getElementById('pth-menu-btn');
        if (b) b.style.display = '';
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
