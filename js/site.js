(function () {
  var side = document.getElementById('side');
  var btn = side && side.querySelector('.menu-btn');
  if (btn) {
    btn.addEventListener('click', function () {
      var open = side.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Close' : 'Menu';
    });
  }
  var slides = document.querySelectorAll('.hero-slide');
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (slides.length > 1 && !still) {
    var at = 0;
    setInterval(function () {
      slides[at].classList.remove('is-on');
      at = (at + 1) % slides.length;
      slides[at].classList.add('is-on');
    }, 6000);
  }
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
  // Home always opens at the top of the page
  if (!location.hash && 'scrollRestoration' in history) history.scrollRestoration = 'manual';
  document.querySelectorAll('a[href="index.html"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      if (/(^|\/)(index\.html)?$/.test(location.pathname) && !location.hash) { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); }
    });
  });
})();
