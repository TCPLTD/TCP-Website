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
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();

// Homepage photo slideshow: crossfades every 6 seconds, with dots and a pause button.
(function () {
  var hero = document.querySelector('.hero-slides');
  if (!hero) return;
  var slides = hero.querySelectorAll('.slide');
  var dots = hero.querySelectorAll('.dot');
  var caption = hero.querySelector('.slide-caption');
  var pauseBtn = hero.querySelector('.slide-pause');
  if (slides.length < 2) { if (pauseBtn) pauseBtn.hidden = true; return; }
  var i = 0, timer = null;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var paused = reduce;
  function show(n) {
    slides[i].classList.remove('is-on'); dots[i].removeAttribute('aria-current');
    i = (n + slides.length) % slides.length;
    slides[i].classList.add('is-on'); dots[i].setAttribute('aria-current', 'true');
    if (caption) caption.textContent = slides[i].getAttribute('data-caption') || '';
  }
  function start() { stop(); if (!paused) timer = setInterval(function () { show(i + 1); }, 6000); }
  function stop() { if (timer) clearInterval(timer); timer = null; }
  function setPaused(p) { paused = p; pauseBtn.textContent = p ? 'Play' : 'Pause'; pauseBtn.setAttribute('aria-pressed', p ? 'true' : 'false'); start(); }
  dots.forEach(function (d, n) { d.addEventListener('click', function () { show(n); start(); }); });
  pauseBtn.addEventListener('click', function () { setPaused(!paused); });
  document.addEventListener('visibilitychange', function () { if (document.hidden) stop(); else start(); });
  setPaused(paused);
})();
