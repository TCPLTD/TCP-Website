/* Featured project pages: the photo slideshow (swipe, arrows, moves on by itself),
   the before and after tabs, and the drag slider between existing and approved drawings.
   Nothing moves by itself for visitors who have asked their device for reduced motion. */
(function () {
  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Slideshow
  document.querySelectorAll('[data-slideshow]').forEach(function (root) {
    var track = root.querySelector('.ss-track'), slides = track.children, total = slides.length;
    var count = root.querySelector('[data-count]'), pause = root.querySelector('[data-pause]');
    var at = 0, timer = null, paused = still, hover = false;
    function go(i) {
      at = (i + total) % total;
      track.scrollTo({ left: at * track.clientWidth, behavior: still ? 'auto' : 'smooth' });
      count.textContent = (at + 1) + ' / ' + total;
    }
    function restart() {
      clearInterval(timer);
      if (!paused && !hover) timer = setInterval(function () { go(at + 1); }, 5000);
    }
    function setPaused(p) {
      paused = p; pause.classList.toggle('is-paused', p);
      pause.setAttribute('aria-label', (p ? 'Play' : 'Pause') + ' slideshow'); restart();
    }
    root.querySelector('[data-prev]').addEventListener('click', function () { go(at - 1); restart(); });
    root.querySelector('[data-next]').addEventListener('click', function () { go(at + 1); restart(); });
    pause.addEventListener('click', function () { setPaused(!paused); });
    track.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); go(at + 1); restart(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); go(at - 1); restart(); }
    });
    root.addEventListener('mouseenter', function () { hover = true; restart(); });
    root.addEventListener('mouseleave', function () { hover = false; restart(); });
    root.addEventListener('focusin', function () { hover = true; restart(); });
    root.addEventListener('focusout', function (e) { if (!root.contains(e.relatedTarget)) { hover = false; restart(); } });
    var t;
    track.addEventListener('scroll', function () {   // keep the count right after a swipe
      clearTimeout(t);
      t = setTimeout(function () {
        var i = Math.round(track.scrollLeft / track.clientWidth);
        if (i !== at) { at = i; count.textContent = (at + 1) + ' / ' + total; restart(); }
      }, 120);
    });
    setPaused(paused);
  });

  // Tabs (before and after, drawings); before and after also moves on by itself until someone picks a tab
  document.querySelectorAll('[data-tabs]').forEach(function (root) {
    var tabs = [].slice.call(root.querySelectorAll('[role="tab"]'));
    var at = 0, timer = null, wait = parseInt(root.getAttribute('data-autoplay') || '0', 10);
    function pick(i, focus) {
      at = (i + tabs.length) % tabs.length;
      tabs.forEach(function (t, k) {
        var on = k === at;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        var pane = document.getElementById(t.getAttribute('aria-controls'));
        pane.hidden = !on;
        if (on) pane.dispatchEvent(new CustomEvent('paneshown'));
      });
      if (focus) tabs[at].focus();
    }
    function stop() { clearInterval(timer); timer = null; }
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { stop(); pick(k); });
      t.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); stop(); pick(at + 1, true); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); stop(); pick(at - 1, true); }
      });
    });
    if (wait && !still) {
      timer = setInterval(function () { pick(at + 1); }, wait);
      root.addEventListener('pointerdown', stop);
      root.addEventListener('focusin', stop);
    }
  });

  // Drag slider between two drawings. It sweeps across once by itself (to one side, to the other,
  // then back to the middle) when it first comes into view and each time its tab is picked.
  // Grabbing it stops the sweep straight away.
  function sweep(box, range) {
    if (still || !box.offsetParent) return;
    var run = (box._run || 0) + 1; box._run = run;
    var keys = [50, 85, 15, 50], seg = 1100, t0 = null;
    function set(v) { box.style.setProperty('--pos', v + '%'); range.value = Math.round(v); }
    function frame(ts) {
      if (box._run !== run) return;
      if (t0 === null) t0 = ts;
      var e = ts - t0, i = Math.floor(e / seg);
      if (i >= keys.length - 1) { set(50); return; }
      var f = (e % seg) / seg; f = f < .5 ? 2 * f * f : 1 - Math.pow(-2 * f + 2, 2) / 2;
      set(keys[i] + (keys[i + 1] - keys[i]) * f);
      requestAnimationFrame(frame);
    }
    setTimeout(function () { if (box._run === run) requestAnimationFrame(frame); }, 350);
  }
  document.querySelectorAll('[data-compare]').forEach(function (box) {
    var range = box.querySelector('input[type="range"]');
    function grab() {
      box._run = (box._run || 0) + 1;   // stop any sweep
      document.querySelectorAll('.cmp').forEach(function (b) { b.classList.add('cmp-used'); });
    }
    range.addEventListener('input', function () { box.style.setProperty('--pos', range.value + '%'); });
    ['pointerdown', 'touchstart', 'keydown'].forEach(function (ev) { range.addEventListener(ev, grab, { passive: true }); });
    if ('IntersectionObserver' in window) {
      var seen = false;
      new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (!seen && e.isIntersecting && e.intersectionRatio > .5 && box.offsetParent) { seen = true; sweep(box, range); } });
      }, { threshold: [0, .5, .6] }).observe(box);
    }
    var pane = box.closest('[role="tabpanel"]');
    if (pane) pane.addEventListener('paneshown', function () { setTimeout(function () { sweep(box, range); }, 30); });
  });
})();
