/* Shared mobile nav. Auto-injects a hamburger toggle into any .top-nav that has
   a .nav-links list, then wires open/close. Pages only need to include this
   script; no per-page button markup required. Pairs with the .nav-toggle /
   mobile styles in css/shared.css. */
(function () {
  function init() {
    var nav = document.querySelector('.top-nav');
    var links = nav && nav.querySelector('.nav-links');
    if (!nav || !links) return;
    if (!links.id) links.id = 'navLinks';

    var toggle = nav.querySelector('.nav-toggle');
    if (!toggle) {
      toggle = document.createElement('button');
      toggle.className = 'nav-toggle';
      toggle.setAttribute('aria-label', 'Menu');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-controls', links.id);
      toggle.innerHTML =
        '<svg class="icon-open" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>' +
        '<svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
      links.parentNode.insertBefore(toggle, links);
    }

    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    Array.prototype.forEach.call(links.querySelectorAll('a'), function (a) {
      a.addEventListener('click', function () {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
