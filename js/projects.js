(function () {
  var list = document.getElementById('project-list');
  if (!list) return;
  var all = window.TCP_PROJECTS || [];
  var limit = parseInt(list.getAttribute('data-limit') || '0', 10);
  var fixedBorough = list.getAttribute('data-borough') || '';
  if (fixedBorough) all = all.filter(function (p) { return p.borough === fixedBorough; });
  var search = document.getElementById('project-search');
  var areaSel = document.getElementById('project-area');
  var yearSel = document.getElementById('project-year');
  var typesBox = document.getElementById('project-types');
  var clear = document.getElementById('project-clear');
  var count = document.getElementById('project-count');
  var state = { type: '', q: '', area: '', year: '' };

  function uniq(key) { return all.map(function (p) { return p[key]; }).filter(function (v, i, a) { return v && a.indexOf(v) === i; }); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function fill(sel, values) { if (!sel) return; values.forEach(function (v) { var o = document.createElement('option'); o.value = v; o.textContent = v; sel.appendChild(o); }); }

  fill(areaSel, uniq('borough').sort());
  fill(yearSel, uniq('year').sort(function (a, b) { return b - a; }));

  var chips = [];
  if (typesBox) {
    var types = uniq('type').sort();
    [''].concat(types).forEach(function (t) {
      var b = el('button', 'chip');
      b.type = 'button';
      b.setAttribute('aria-pressed', t === '' ? 'true' : 'false');
      b.appendChild(document.createTextNode(t || 'All types'));
      var n = t ? all.filter(function (p) { return p.type === t; }).length : all.length;
      b.appendChild(el('span', 'count', '(' + n + ')'));
      b.addEventListener('click', function () { state.type = t; render(); });
      b._type = t;
      typesBox.appendChild(b);
      chips.push(b);
    });
  }

  if (search) search.addEventListener('input', function () { state.q = search.value.trim().toLowerCase(); render(); });
  if (areaSel) areaSel.addEventListener('change', function () { state.area = areaSel.value; render(); });
  if (yearSel) yearSel.addEventListener('change', function () { state.year = yearSel.value; render(); });
  if (clear) clear.addEventListener('click', function () {
    state = { type: '', q: '', area: '', year: '' };
    if (search) search.value = '';
    if (areaSel) areaSel.value = '';
    if (yearSel) yearSel.value = '';
    render();
  });

  function matches(p) {
    if (state.type && p.type !== state.type) return false;
    if (state.area && p.borough !== state.area) return false;
    if (state.year && String(p.year) !== state.year) return false;
    if (state.q) {
      var hay = [p.type, p.street, p.town, p.borough, p.summary, String(p.year)].join(' ').toLowerCase();
      if (hay.indexOf(state.q) === -1) return false;
    }
    return true;
  }

  function render() {
    chips.forEach(function (c) { c.setAttribute('aria-pressed', c._type === state.type ? 'true' : 'false'); });
    var filtering = !!(state.type || state.q || state.area || state.year);
    if (clear) clear.hidden = !filtering;
    var found = all.filter(matches);
    var shown = limit ? found.slice(0, limit) : found;
    if (count) count.textContent = filtering ? 'Showing ' + found.length + ' of ' + all.length + ' projects' : all.length + ' approved projects';
    list.innerHTML = '';
    if (!shown.length) {
      list.appendChild(el('p', 'empty', !all.length && fixedBorough ? 'Projects in ' + fixedBorough + ' are being added. Call 07843 561129 to hear about our work nearby.' : 'No projects match those filters. Try a nearby town or another type of work.'));
      return;
    }
    shown.forEach(function (p) {
      var card = el(p.councilLink ? 'a' : 'div', 'card');
      if (p.councilLink) { card.href = p.councilLink; card.target = '_blank'; card.rel = 'noopener'; }
      var ph = el('div', 'ph'); ph.appendChild(el('span', '', 'Photo to come')); card.appendChild(ph);
      var body = el('div', 'card-body');
      body.appendChild(el('span', 'card-type', p.type));
      body.appendChild(el('span', 'card-title', p.street + ', ' + p.town));
      body.appendChild(el('span', 'card-text', p.summary));
      var tags = el('div', 'tags');
      tags.appendChild(el('span', 'tag', 'Approved ' + p.year));
      tags.appendChild(el('span', 'tag', p.borough));
      if (p.tour) tags.appendChild(el('span', 'tag', '3D tour'));
      body.appendChild(tags);
      card.appendChild(body);
      list.appendChild(card);
    });
  }
  render();
})();
