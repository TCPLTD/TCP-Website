(function () {
  var list = document.getElementById('project-list');
  if (!list) return;
  var all = window.TCP_PROJECTS || [];
  var limit = parseInt(list.getAttribute('data-limit') || '0', 10);
  var fixedBorough = list.getAttribute('data-borough') || '';
  var search = document.getElementById('project-search');
  var areaSel = document.getElementById('project-area');
  var chips = Array.prototype.slice.call(document.querySelectorAll('[data-type-filter]'));
  var count = document.getElementById('project-count');
  var state = { type: 'All', q: '', area: '' };

  if (areaSel) {
    var boroughs = all.map(function (p) { return p.borough; }).filter(function (b, i, a) { return b && a.indexOf(b) === i; }).sort();
    boroughs.forEach(function (b) { var o = document.createElement('option'); o.value = b; o.textContent = b; areaSel.appendChild(o); });
    areaSel.addEventListener('change', function () { state.area = areaSel.value; render(); });
  }
  if (search) search.addEventListener('input', function () { state.q = search.value.trim().toLowerCase(); render(); });
  chips.forEach(function (c) {
    c.addEventListener('click', function () {
      state.type = c.getAttribute('data-type-filter');
      chips.forEach(function (o) { o.setAttribute('aria-pressed', o === c ? 'true' : 'false'); });
      render();
    });
  });

  function matches(p) {
    if (state.type !== 'All' && p.type.toLowerCase().indexOf(state.type.toLowerCase()) === -1) return false;
    if (fixedBorough && p.borough !== fixedBorough) return false;
    if (state.area && p.borough !== state.area) return false;
    if (state.q) {
      var hay = [p.type, p.street, p.town, p.borough, p.summary, String(p.year)].join(' ').toLowerCase();
      if (hay.indexOf(state.q) === -1) return false;
    }
    return true;
  }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }

  function render() {
    var shown = all.filter(matches);
    if (limit) shown = shown.slice(0, limit);
    list.innerHTML = '';
    if (count) count.textContent = shown.length === 1 ? '1 project' : shown.length + ' projects';
    if (!shown.length) { list.appendChild(el('p', 'empty', fixedBorough ? 'Projects in ' + fixedBorough + ' are being added. Call 07843 561129 to hear about our work nearby.' : 'No projects match that search yet. Try another area or type, or call us on 07843 561129.')); return; }
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
