/* Suggestions under the search boxes: type a letter or two and pick a town, postcode area, street,
   council or type of work. They narrow as you type and allow for small spelling mistakes. */
(function () {
  if (!window.TCPProjects || !window.TCPProjects.places) return;
  var WORK = ['Loft conversion', 'Rear extension', 'Side extension', 'Single storey extension', 'Two storey extension', 'Rear dormer',
              'Hip to gable', 'Garage conversion', 'Porch', 'Outhouse', 'Rooflights', 'Juliet balcony', 'Front extension', 'New home', 'Flats', 'Basement'];
  var PLACES = window.TCPProjects.places();

  // how many single-letter changes turn a into b (for spelling mistakes)
  function dist(a, b) {
    var m = [], i, j;
    for (i = 0; i <= a.length; i++) m[i] = [i];
    for (j = 0; j <= b.length; j++) m[0][j] = j;
    for (i = 1; i <= a.length; i++) for (j = 1; j <= b.length; j++)
      m[i][j] = Math.min(m[i - 1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
    return m[a.length][b.length];
  }
  function clean(x) { return x.toLowerCase().replace(/'/g, '').replace(/-/g, ' '); }

  // rank items against what has been typed: whole name starts with it, then a word in it does, then near misses
  function find(frag, items) {
    var f = clean(frag), out = [];
    if (!f) return out;
    items.forEach(function (it) {
      var name = clean(it.label), sc = null, whole = false;
      if (name.indexOf(f) === 0) { sc = 0; whole = true; }
      else if (f.length >= 2 && (' ' + name).indexOf(' ' + f) !== -1) sc = 1;
      else if (f.length >= 4) {
        // allow a spelling mistake or two, against the start of the name or of a later word in it
        var allow = f.length >= 7 ? 2 : 1, starts = [0];
        for (var i = 0; i < name.length; i++) if (name[i] === ' ') starts.push(i + 1);
        starts.forEach(function (st, w) {
          var d = dist(f, name.slice(st, st + f.length));
          if (d > allow) return;
          var v = 2 + d + (w ? 1 : 0);
          if (sc === null || v < sc) { sc = v; whole = w === 0; }
        });
      }
      if (sc !== null) out.push({ it: it, sc: sc, whole: whole });
    });
    out.sort(function (a, b) { return a.sc - b.sc || (b.it.n || 0) - (a.it.n || 0) || a.it.label.length - b.it.label.length; });
    return out.slice(0, 8);
  }

  function attach(input, opts) {
    var items = opts.work ? WORK.map(function (w) { return { label: w, kind: 'Type of work' }; }).concat(PLACES) : PLACES;
    var wrap = input.parentNode;
    wrap.classList.add('sg-wrap');
    var list = document.createElement('ul');
    list.className = 'sg-list'; list.id = input.id + '-sg'; list.setAttribute('role', 'listbox'); list.hidden = true;
    wrap.appendChild(list);
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-autocomplete', 'list');
    input.setAttribute('aria-expanded', 'false');
    input.setAttribute('aria-controls', list.id);
    input.setAttribute('autocomplete', 'off');
    var shown = [], active = -1, cut = 0;

    // the part being typed: the last word, or the last few words if together they start a name
    function fragment() {
      var v = input.value.slice(0, input.selectionStart == null ? input.value.length : input.selectionStart);
      var toks = v.split(/[\s,]+/), best = null;
      if (/[\s,]$/.test(v)) return null;
      for (var k = Math.min(4, toks.length); k >= 1; k--) {
        var frag = toks.slice(toks.length - k).join(' ');
        var r = find(frag, items);
        // several words only count when they match a name from its start (allowing for typos)
        if (k > 1) r = r.filter(function (o) { return o.whole; });
        if (r.length) { best = { frag: frag, res: r.map(function (o) { return o.it; }) }; break; }
      }
      return best;
    }
    function close() { list.hidden = true; input.setAttribute('aria-expanded', 'false'); input.removeAttribute('aria-activedescendant'); active = -1; }
    function open() {
      var f = fragment();
      if (!f) { close(); return; }
      shown = f.res; cut = f.frag.length; list.innerHTML = '';
      shown.forEach(function (it, i) {
        var li = document.createElement('li');
        li.id = list.id + '-' + i; li.setAttribute('role', 'option'); li.className = 'sg-item';
        var a = document.createElement('span'); a.className = 'sg-label'; a.textContent = it.label;
        var b = document.createElement('span'); b.className = 'sg-kind'; b.textContent = it.kind + (it.n && it.kind !== 'Type of work' ? ' · ' + it.n + (it.n === 1 ? ' project' : ' projects') : '');
        li.appendChild(a); li.appendChild(b);
        li.addEventListener('mousedown', function (e) { e.preventDefault(); choose(i); });
        list.appendChild(li);
      });
      list.hidden = !shown.length;
      input.setAttribute('aria-expanded', shown.length ? 'true' : 'false');
    }
    function highlight(i) {
      active = i;
      [].forEach.call(list.children, function (li, k) { li.setAttribute('aria-selected', k === i ? 'true' : 'false'); });
      if (i >= 0) input.setAttribute('aria-activedescendant', list.id + '-' + i); else input.removeAttribute('aria-activedescendant');
    }
    function choose(i) {
      var it = shown[i]; if (!it) return;
      var end = input.selectionStart == null ? input.value.length : input.selectionStart;
      var before = input.value.slice(0, end - cut), after = input.value.slice(end);
      input.value = (before + it.label + ' ' + after.replace(/^\s+/, '')).replace(/\s+$/, ' ');
      close();
      input.focus();
      input.dispatchEvent(new Event('input', { bubbles: true }));
      if (opts.onPick) opts.onPick(it);
    }
    input.addEventListener('input', function (e) { if (e.isTrusted !== false) open(); });
    input.addEventListener('focus', open);
    input.addEventListener('blur', function () { setTimeout(close, 100); });
    input.addEventListener('keydown', function (e) {
      if (list.hidden) return;
      if (e.key === 'ArrowDown') { e.preventDefault(); highlight(Math.min(shown.length - 1, active + 1)); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); highlight(Math.max(-1, active - 1)); }
      else if (e.key === 'Enter' && active >= 0) { e.preventDefault(); e.stopImmediatePropagation(); choose(active); }
      else if (e.key === 'Escape') { close(); }
    });
  }

  var s = document.getElementById('project-search');
  if (s) attach(s, { work: true });
  var p = document.getElementById('pl-place');
  if (p) attach(p, { work: false });
})();
