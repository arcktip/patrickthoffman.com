/* Shared site nav behaviour. Injects its own hamburger styles AND a toggle
   button into any .top-nav that has a .nav-links list — so it works on every
   page whether or not that page links css/shared.css. Pages only need to
   include this one script. */
(function () {
  function injectStyles() {
    if (document.getElementById('pth-nav-css')) return;
    var css =
      '.nav-toggle{display:none;background:none;border:none;cursor:pointer;padding:6px;color:#fff;align-items:center;justify-content:center}' +
      '.nav-toggle svg{width:26px;height:26px;display:block}' +
      '.nav-toggle .icon-close{display:none}' +
      '.nav-toggle[aria-expanded="true"] .icon-open{display:none}' +
      '.nav-toggle[aria-expanded="true"] .icon-close{display:block}' +
      '@media (max-width:768px){' +
        '.nav-toggle{display:inline-flex}' +
        '.top-nav .nav-links{display:none;position:absolute;top:100%;left:0;right:0;flex-direction:column;gap:0;background:rgba(10,20,40,0.97);-webkit-backdrop-filter:blur(12px);backdrop-filter:blur(12px);padding:.4rem 0;box-shadow:0 10px 28px rgba(0,0,0,.35);border-top:1px solid rgba(255,255,255,.08)}' +
        '.top-nav .nav-links.open{display:flex}' +
        '.top-nav .nav-links li{width:100%}' +
        '.top-nav .nav-links a{display:block;padding:.85rem 2rem;font-size:.95rem;color:rgba(255,255,255,.82)}' +
      '}';
    var st = document.createElement('style');
    st.id = 'pth-nav-css';
    st.textContent = css;
    (document.head || document.documentElement).appendChild(st);
  }

  function init() {
    injectStyles();
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
