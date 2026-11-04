/* Carousels: reviews (one at a time, fading) and featured projects (a sideways track).
   Both move on by themselves, pause on hover, focus or the pause button, and stay still
   for visitors who have asked their device for reduced motion. */
(function () {
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setup(root) {
    var kind = root.getAttribute('data-carousel');
    var wait = parseInt(root.getAttribute('data-interval') || '7000', 10);
    var pauseBtn = root.querySelector('[data-pause]');
    var countEl = root.querySelector('[data-count]');
    var live = root.querySelector('[aria-live]');
    var userPaused = still, hovering = false, timer = null;

    var slides, track, at = 0;
    if (kind === 'fade') slides = root.querySelectorAll('.rv-slide');
    else { track = root.querySelector('.fp-track'); slides = track.children; }
    var total = slides.length;
    if (total < 2) return;

    function step() { return slides[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap || 0); }
    function perView() { return Math.max(1, Math.round(track.clientWidth / step())); }
    function lastStart() { return Math.max(0, total - perView()); }

    function show(i, fromUser) {
      if (kind === 'fade') {
        at = (i + total) % total;
        for (var k = 0; k < total; k++) {
          var on = k === at;
          slides[k].classList.toggle('is-on', on);
        }
        root.querySelectorAll('.dot').forEach(function (d, k) {
          if (k === at) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current');
        });
      } else {
        var max = lastStart();
        at = i > max ? 0 : i < 0 ? max : i;
        track.scrollTo({ left: at * step(), behavior: still ? 'auto' : 'smooth' });
      }
      if (countEl) countEl.textContent = (at + 1) + ' / ' + total;
      if (fromUser) restart();
    }

    function running() { return !userPaused && !hovering; }
    function restart() {
      clearInterval(timer);
      if (live) live.setAttribute('aria-live', running() ? 'off' : 'polite');
      if (running()) timer = setInterval(function () { show(at + 1); }, wait);
    }
    function setPaused(p) {
      userPaused = p;
      if (pauseBtn) {
        pauseBtn.classList.toggle('is-paused', p);
        var what = kind === 'fade' ? 'reviews' : 'featured projects';
        pauseBtn.setAttribute('aria-label', (p ? 'Play ' : 'Pause ') + what);
      }
      restart();
    }

    root.querySelector('[data-prev]').addEventListener('click', function () { show(at - 1, true); });
    root.querySelector('[data-next]').addEventListener('click', function () { show(at + 1, true); });
    if (pauseBtn) pauseBtn.addEventListener('click', function () { setPaused(!userPaused); });
    root.querySelectorAll('.dot').forEach(function (d) {
      d.addEventListener('click', function () { show(parseInt(d.getAttribute('data-go'), 10), true); });
    });
    root.addEventListener('mouseenter', function () { hovering = true; restart(); });
    root.addEventListener('mouseleave', function () { hovering = false; restart(); });
    root.addEventListener('focusin', function () { hovering = true; restart(); });
    root.addEventListener('focusout', function (e) { if (!root.contains(e.relatedTarget)) { hovering = false; restart(); } });

    if (track) {
      // keep the counter right when someone swipes or scrolls the track by hand
      var t;
      track.addEventListener('scroll', function () {
        clearTimeout(t);
        t = setTimeout(function () {
          at = Math.min(total - 1, Math.round(track.scrollLeft / step()));
          if (countEl) countEl.textContent = (at + 1) + ' / ' + total;
        }, 120);
      });
      track.addEventListener('pointerdown', function () { setPaused(true); });
      track.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); show(at + 1, true); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); show(at - 1, true); }
      });
    }
    setPaused(userPaused);
  }

  document.querySelectorAll('[data-carousel]').forEach(setup);
})();
