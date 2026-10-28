(function () {
  var list = document.getElementById('project-list');
  if (!list) return;
  var all = window.TCP_PROJECTS || [];
  var limit = parseInt(list.getAttribute('data-limit') || '0', 10);
  var fixedBorough = list.getAttribute('data-borough') || '';
  if (fixedBorough) all = all.filter(function (p) { return p.borough === fixedBorough; });
  // short lists (home page) show described projects first
  if (limit) all = all.filter(function (p) { return p.described; }).concat(all.filter(function (p) { return !p.described; }));
  var PAGE = 24;
  var featured = {};
  (window.TCP_FEATURED || []).forEach(function (f) { featured[f.id] = true; });
  var search = document.getElementById('project-search');
  var areaSel = document.getElementById('project-area');
  var yearSel = document.getElementById('project-year');
  var routeSel = document.getElementById('project-route');
  var typesBox = document.getElementById('project-types');
  var clear = document.getElementById('project-clear');
  var count = document.getElementById('project-count');
  var more = document.getElementById('project-more');
  var state = { type: '', q: '', area: '', year: '', route: '' };
  var shownCount = PAGE;
  var TYPE_ORDER = ['Extension', 'Loft conversion', 'Extension and loft', 'New homes', 'Flats and change of use', 'Outbuildings and garages', 'Porch and front', 'Other works', 'Other approvals'];

  function routes(p) { return (p.approvals || []).map(function (a) { return a.route; }); }
  function uniq(values) { return values.filter(function (v, i, a) { return v && a.indexOf(v) === i; }); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function fill(sel, values) { if (!sel) return; values.forEach(function (v) { var o = document.createElement('option'); o.value = v; o.textContent = v; sel.appendChild(o); }); }
  function place(p) { return p.street ? p.street + ', ' + p.town : p.town; }

  var boroughCounts = {};
  all.forEach(function (p) { boroughCounts[p.borough] = (boroughCounts[p.borough] || 0) + 1; });
  fill(areaSel, Object.keys(boroughCounts).filter(function (b) { return b !== 'Other'; }).sort(function (a, b) { return boroughCounts[b] - boroughCounts[a]; }).concat(boroughCounts.Other ? ['Other'] : []));
  fill(yearSel, uniq(all.map(function (p) { return p.year; })).sort(function (a, b) { return b - a; }));
  fill(routeSel, uniq([].concat.apply([], all.map(routes))).sort());

  var chips = [];
  if (typesBox) {
    var present = uniq(all.map(function (p) { return p.type; }));
    var types = TYPE_ORDER.filter(function (t) { return present.indexOf(t) !== -1; });
    [''].concat(types).forEach(function (t) {
      var n = t ? all.filter(function (p) { return p.type === t; }).length : all.length;
      var b = el('button', 'chip');
      b.type = 'button';
      b.appendChild(document.createTextNode(t || 'All types'));
      b.appendChild(el('span', 'count', '(' + n + ')'));
      b.addEventListener('click', function () { state.type = t; reset(); });
      b._type = t;
      typesBox.appendChild(b);
      chips.push(b);
    });
  }

  function reset() { shownCount = PAGE; render(); }
  if (search) search.addEventListener('input', function () { state.q = search.value.trim().toLowerCase(); reset(); });
  [[areaSel, 'area'], [yearSel, 'year'], [routeSel, 'route']].forEach(function (pair) {
    if (pair[0]) pair[0].addEventListener('change', function () { state[pair[1]] = pair[0].value; reset(); });
  });
  if (clear) clear.addEventListener('click', function () {
    state = { type: '', q: '', area: '', year: '', route: '' };
    [search, areaSel, yearSel, routeSel].forEach(function (f) { if (f) f.value = ''; });
    reset();
  });
  if (more) more.addEventListener('click', function () { shownCount += PAGE; render(); });

  // allow links such as projects.html?area=Hertsmere or ?q=loft
  try {
    var params = new URLSearchParams(location.search);
    if (params.get('area') && areaSel) { areaSel.value = params.get('area'); state.area = areaSel.value; }
    if (params.get('q') && search) { search.value = params.get('q'); state.q = search.value.toLowerCase(); }
  } catch (e) {}

  function matches(p) {
    if (state.type && p.type !== state.type) return false;
    if (state.area && p.borough !== state.area) return false;
    if (state.year && String(p.year) !== state.year) return false;
    if (state.route && routes(p).indexOf(state.route) === -1) return false;
    if (state.q) {
      var hay = [p.type, p.street, p.town, p.district, p.borough, p.year].concat((p.approvals || []).map(function (a) { return (a.summary || '') + ' ' + a.route + ' ' + (a.ref || ''); })).join(' ').toLowerCase();
      var words = state.q.split(/\s+/);
      for (var i = 0; i < words.length; i++) if (hay.indexOf(words[i]) === -1) return false;
    }
    return true;
  }

  function card(p) {
    var c = el('article', 'card project-card');
    if (p.photos && p.photos.length) {
      var img = el('img', 'card-img');
      img.src = p.photos[0]; img.alt = p.type + ' in ' + p.town; img.loading = 'lazy';
      c.appendChild(img);
    } else {
      var head = el('div', 'card-head');
      head.appendChild(el('span', 'card-type', p.type === 'Other approvals' ? 'Planning approval' : p.type));
      if (p.year) head.appendChild(el('span', 'card-year', p.year));
      c.appendChild(head);
    }
    var body = el('div', 'card-body');
    if (p.photos && p.photos.length) body.appendChild(el('span', 'card-type', p.type));
    body.appendChild(el('h3', 'card-title', place(p)));
    body.appendChild(el('p', 'card-text', p.summary));
    var tags = el('div', 'tags');
    tags.appendChild(el('span', 'tag', p.borough === 'Other' ? 'Further afield' : p.borough));
    var n = (p.approvals || []).length;
    if (n > 1) tags.appendChild(el('span', 'tag', n + ' approvals'));
    if (p.tour) tags.appendChild(el('span', 'tag', '3D tour'));
    body.appendChild(tags);
    var links = el('div', 'card-links');
    if (featured[p.id]) { var f = el('a', '', 'Read more'); f.href = 'project-' + p.id + '.html'; links.appendChild(f); }
    var m = el('a', '', 'View on map'); m.href = 'map.html#' + p.id; links.appendChild(m);
    var withLink = (p.approvals || []).filter(function (a) { return a.link; }).pop();
    if (withLink) {
      var r = el('a', '', 'Council record'); r.href = withLink.link; r.target = '_blank'; r.rel = 'noopener';
      r.setAttribute('aria-label', 'Council planning record for ' + place(p) + ' (opens in a new tab)');
      links.appendChild(r);
    }
    body.appendChild(links);
    c.appendChild(body);
    return c;
  }

  function render() {
    chips.forEach(function (c) { c.setAttribute('aria-pressed', c._type === state.type ? 'true' : 'false'); });
    var filtering = !!(state.type || state.q || state.area || state.year || state.route);
    if (clear) clear.hidden = !filtering;
    var found = all.filter(matches);
    var cap = limit || shownCount;
    var shown = found.slice(0, cap);
    if (count) count.textContent = filtering ? found.length + ' of ' + all.length + ' approved projects match' : all.length + ' approved projects';
    if (more) more.hidden = !!limit || found.length <= cap;
    list.innerHTML = '';
    if (!shown.length) {
      list.appendChild(el('p', 'empty', !all.length && fixedBorough ? 'Projects in ' + fixedBorough + ' are being added. Call 07843 561129 to hear about our work nearby.' : 'No projects match those filters. Try a nearby town or another type of work.'));
      return;
    }
    shown.forEach(function (p) { list.appendChild(card(p)); });
  }
  render();
})();
