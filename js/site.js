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
})();
