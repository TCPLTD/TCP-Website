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
  var featuredIds = {};
  (window.TCP_FEATURED || []).forEach(function (f) { featuredIds[f.id] = true; });
  var search = document.getElementById('project-search');
  var areaSel = document.getElementById('project-area');
  var yearSel = document.getElementById('project-year');
  var routeSel = document.getElementById('project-route');
  var typesBox = document.getElementById('project-types');
  var typeSel = document.getElementById('project-type');
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

  if (typeSel) {
    TYPE_ORDER.forEach(function (t) {
      var n = all.filter(function (p) { return p.type === t; }).length;
      if (!n) return;
      var o = document.createElement('option'); o.value = t;
      o.textContent = (t === 'Other approvals' ? 'Other planning approvals' : t) + ' (' + n + ')';
      typeSel.appendChild(o);
    });
  }

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
  [[typeSel, 'type'], [areaSel, 'area'], [yearSel, 'year'], [routeSel, 'route']].forEach(function (pair) {
    if (pair[0]) pair[0].addEventListener('change', function () { state[pair[1]] = pair[0].value; reset(); });
  });
  if (clear) clear.addEventListener('click', function () {
    state = { type: '', q: '', area: '', year: '', route: '' };
    [search, typeSel, areaSel, yearSel, routeSel].forEach(function (f) { if (f) f.value = ''; });
    reset();
  });
  if (more) more.addEventListener('click', function () { shownCount += PAGE; render(); });

  // allow links such as projects.html?area=Hertsmere or ?q=loft
  try {
    var params = new URLSearchParams(location.search);
    if (params.get('area') && areaSel) { areaSel.value = params.get('area'); state.area = areaSel.value; }
    if (params.get('q') && search) { search.value = params.get('q'); state.q = search.value.toLowerCase(); }
    if (params.get('type') && typeSel) { typeSel.value = params.get('type'); state.type = typeSel.value; }
  } catch (e) {}

  // used by the "What are you planning?" questions on the projects page
  window.TCPProjects = {
    count: function (o) {
      var keep = state; state = { type: o.type || '', q: (o.q || '').toLowerCase(), area: '', year: '', route: '' };
      parseQuery(); var n = all.filter(matches).length; state = keep; parseQuery(); return n;
    },
    // the name of a place in our records that matches what was typed, or null
    // how many projects a planner choice would show that also mention any of these words
    countWith: function (o, alts) {
      var keep = state; state = { type: o.type || '', q: (o.q || '').toLowerCase(), area: '', year: '', route: '' };
      parseQuery(); var n = all.filter(function (p) { return matches(p) && alts.some(function (x) { return text(p).indexOf(x) !== -1; }); }).length;
      state = keep; parseQuery(); return n;
    },
    // every place in our records, for the suggestions under the search boxes
    places: function () {
      var KIND = ['Town', 'Postcode area', 'Street', 'Council'];
      return Object.keys(PLACES).map(function (k) { var e = PLACES[k]; return { label: e.name, kind: KIND[e.rank], n: e.n }; });
    },
    place: function (text) { var k = (text || '').toLowerCase().replace(/'/g, '').trim(); return PLACES[k] ? PLACES[k].name : null; },
    set: function (o) {
      state = { type: o.type || '', q: (o.q || '').toLowerCase(), area: '', year: '', route: '', boost: o.boost || [] };
      if (search) search.value = o.q || '';
      if (typeSel) typeSel.value = o.type || '';
      [areaSel, yearSel, routeSel].forEach(function (f) { if (f) f.value = ''; });
      reset();
    }
  };

  // ---- Ranking: best match first, and nearest first when a place is typed ----
  // Places people might type: towns, postcode districts, councils and streets, each with a centre point.
  var PLACES = {};
  (window.TCP_PROJECTS || []).forEach(function (p) {
    if (typeof p.lat !== 'number') return;
    // when one name is several things (Barnet the town and Barnet the council), the town wins
    [p.town, p.district, p.street, p.borough].forEach(function (n, rank) {
      if (!n || n === 'Other' || n === 'London') return;
      var k = n.toLowerCase().replace(/'/g, '');
      var e = PLACES[k];
      if (!e || rank < e.rank) e = PLACES[k] = { name: n, lat: 0, lng: 0, n: 0, rank: rank };
      else if (rank > e.rank) return;
      e.lat += p.lat; e.lng += p.lng; e.n++;
    });
  });
  var parsed = { words: [], place: null };
  // split the search into a place (if one is named) and the words describing the work
  function parseQuery() {
    // a full postcode is looked up as a whole
    var q0 = norm(state.q), pcode = null;
    q0 = q0.replace(/\b([a-z]{1,2}\d[a-z\d]?)\s*(\d[a-z]{2})\b/, function (m, a, b) { pcode = (a + ' ' + b).toUpperCase(); return ' '; });
    var toks = q0.replace(/'/g, '').replace(/,/g, ' ').split(/\s+/).filter(function (t) { return t && STOP.indexOf(t) === -1; }), words = [], place = null;
    for (var i = 0; i < toks.length;) {
      var hit = 0;
      for (var n = Math.min(4, toks.length - i); n >= 1; n--) {
        var k = toks.slice(i, i + n).join(' ');
        if (PLACES[k] && !(n === 1 && WORK_WORDS.indexOf(k) !== -1)) { place = PLACES[k]; hit = n; break; }
      }
      if (hit) i += hit; else { words.push(toks[i]); i++; }
    }
    // Words that describe no work in our records (a street we haven't worked on, a full postcode)
    // are treated as somewhere to measure from, looked up on a map service.
    // An unknown word counts as part of a street only when a street word (road, avenue...) follows it;
    // otherwise it stays a work word, and the search falls back to the closest matches.
    var work = [], where = [];
    words.forEach(function (w, j) {
      if (STREET_WORDS.indexOf(w) !== -1 && where.length) { where.push(w); return; }
      var nextIsStreet = words.slice(j + 1).some(function (x, k) { return STREET_WORDS.indexOf(x) !== -1 && words.slice(j + 1, j + 1 + k).every(function (y) { return !has(vocab(), y); }); });
      if (!has(vocab(), w) && nextIsStreet) where.push(w); else work.push(w);
    });
    if (pcode) { where = [pcode]; place = null; }
    var lookup = null, note = '';
    if (where.length) {
      var phrase = where.join(' ') + (place && !pcode ? ', ' + place.name : '');
      var g = GEO[phrase];
      if (g) place = g;
      else if (g === null) note = 'We could not find \u201c' + where.join(' ') + '\u201d on the map';
      else { lookup = phrase; note = 'Finding \u201c' + where.join(' ') + '\u201d on the map\u2026'; }
    }
    parsed = { words: work, place: place, lookup: lookup, note: note };
    if (lookup) geocode(lookup);
  }
  var STOP = ['in', 'near', 'at', 'on', 'the', 'a', 'an', 'for', 'of', 'my', 'i', 'want', 'and', 'with', 'around', 'by', 'nearby', 'like', 'similar', 'please'];
  var STREET_WORDS = ['road', 'rd', 'avenue', 'ave', 'close', 'lane', 'way', 'drive', 'gardens', 'crescent', 'street', 'st', 'grove', 'park', 'hill', 'place', 'court', 'walk', 'rise', 'mews', 'green', 'row', 'terrace', 'view', 'end', 'gate', 'square'];
  var VOCAB = null;
  function vocab() { return VOCAB || (VOCAB = all.map(text).join(' ')); }
  // Map lookups for places we have no projects in: postcodes via postcodes.io, streets via OpenStreetMap.
  var GEO = {}, geoTimer = null, geoBusy = {};
  function geocode(phrase) {
    if (geoBusy[phrase]) return;
    clearTimeout(geoTimer);
    geoTimer = setTimeout(function () {
      geoBusy[phrase] = true;
      var pc = phrase.replace(/,.*$/, '').replace(/\s+/g, '').toUpperCase();
      var url, pick;
      if (/^[A-Z]{1,2}\d[A-Z\d]?\d[A-Z]{2}$/.test(pc)) {
        url = 'https://api.postcodes.io/postcodes/' + pc;
        pick = function (j) { return j && j.result ? { lat: j.result.latitude, lng: j.result.longitude } : null; };
      } else if (/^[A-Z]{1,2}\d[A-Z\d]?$/.test(pc)) {
        url = 'https://api.postcodes.io/outcodes/' + pc;
        pick = function (j) { return j && j.result ? { lat: j.result.latitude, lng: j.result.longitude } : null; };
      } else {
        url = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&countrycodes=gb&viewbox=-0.75,52.05,0.35,51.35&q=' + encodeURIComponent(phrase);
        pick = function (j) { return j && j[0] ? { lat: parseFloat(j[0].lat), lng: parseFloat(j[0].lon) } : null; };
      }
      fetch(url).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (j) {
        var c = pick(j);
        var name = phrase.replace(/,.*$/, '');
        if (!/^[A-Z]{1,2}\d/.test(name)) name = name.replace(/\b\w/g, function (m) { return m.toUpperCase(); });
        GEO[phrase] = c ? { name: name, lat: c.lat, lng: c.lng, n: 1, exact: true } : null;
        render();
      });
    }, 600);
  }
  var WORK_WORDS = ['loft', 'rear', 'side', 'front', 'garage', 'porch', 'extension', 'conversion', 'dormer', 'garden', 'flat', 'flats'];
  function text(p) {
    if (!p._t) p._t = norm([p.type].concat((p.approvals || []).map(function (a) { return (a.summary || '') + ' ' + a.route + ' ' + (a.ref || ''); })).join(' '));
    return p._t;
  }
  function norm(x) { return String(x || '').toLowerCase().replace(/[-\/]/g, ' ').replace(/\bstory\b/g, 'storey').replace(/\bstories\b/g, 'storey'); }
  // other ways people describe the same work, as council descriptions word it
  var SYN = {
    velux: ['velux', 'rooflight', 'roof light', 'skylight'], rooflight: ['rooflight', 'roof light', 'velux', 'skylight'], skylight: ['skylight', 'rooflight', 'roof light', 'velux'],
    wraparound: ['wrap', 'side and rear'], wrap: ['wrap', 'side and rear'], double: ['two storey', 'double'], kitchen: ['rear extension', 'kitchen'],
    outhouse: ['outhouse', 'outbuilding'], outbuilding: ['outbuilding', 'outhouse'], studio: ['outhouse', 'outbuilding', 'studio'], office: ['office', 'outhouse', 'outbuilding'],
    annexe: ['annex', 'outhouse', 'outbuilding'], annex: ['annex', 'outhouse', 'outbuilding'], attic: ['loft', 'attic'], dormer: ['dormer'], balcony: ['balcony', 'juliet'],
    bungalow: ['bungalow', 'single storey'], driveway: ['driveway', 'crossover', 'parking'], conservatory: ['conservatory', 'rear extension']
  };
  // does the text contain this search word, a plural or singular of it, or another way of saying it?
  function has(t, w) {
    var alts = SYN[w] || [w];
    if (w.length > 3 && /s$/.test(w)) alts = alts.concat([w.slice(0, -1)]);
    for (var i = 0; i < alts.length; i++) if (t.indexOf(alts[i]) !== -1) return true;
    return false;
  }
  function km(p, c) {
    if (typeof p.lat !== 'number') return 99;
    var dy = (p.lat - c.lat / c.n) * 111, dx = (p.lng - c.lng / c.n) * 69;
    return Math.sqrt(dx * dx + dy * dy);
  }
  function score(p) {
    var t = text(p), s = 0, w = parsed.words, boost = state.boost || [], why = { words: [], details: [], clear: false };
    w.forEach(function (x) { if (has(t, x)) { s += 2; why.words.push(x); } });
    if (w.length > 1 && t.indexOf(w.join(' ')) !== -1) { s += 4; why.phrase = w.join(' '); }
    // boost entries are the planner's detail choices: { label, words } (or a plain list of words)
    boost.forEach(function (b) {
      var alts = b.words || [].concat(b);
      if (alts.some(function (x) { return t.indexOf(x) !== -1; })) { s += 6; why.details.push((b.label || alts[0]).toLowerCase()); }
    });
    // a short description that is mostly the thing searched for is a clearer example
    (p.approvals || []).some(function (a) {
      var d = (a.summary || '').toLowerCase();
      d = norm(d);
      if (d && d.length < 70 && w.length && w.every(function (x) { return has(d, x); })) { s += 2; why.clear = true; return true; }
    });
    p._why = why;
    if (p.described) s += 0.5;
    s += Math.max(0, (p.year || 2000) - 2000) / 25;
    if (parsed.place) s -= km(p, parsed.place) * 0.6;
    p._s = s;
    return s;
  }
  function ranked() { return parsed.words.length || (state.boost || []).length || parsed.place; }

  function matches(p) {
    if (state.type && p.type !== state.type) return false;
    if (state.area && p.borough !== state.area) return false;
    if (state.year && String(p.year) !== state.year) return false;
    if (state.route && routes(p).indexOf(state.route) === -1) return false;
    if (parsed.words.length) {
      var hay = norm([p.street, p.town, p.district, p.borough, p.year].join(' ')) + ' ' + text(p);
      for (var i = 0; i < parsed.words.length; i++) if (!has(hay, parsed.words[i])) return false;
    }
    return true;
  }

  function yearsOf(p) {
    var ys = (p.approvals || []).map(function (a) { return a.year; }).filter(Boolean);
    if (!ys.length) return p.year || '';
    var lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
    return lo === hi ? String(lo) : lo + '–' + hi;
  }
  function typeLabel(p) {
    var n = (p.approvals || []).length;
    if (n > 1) return n + ' approved jobs';
    return p.type === 'Other approvals' ? 'Planning approval' : p.type;
  }

  function card(p) {
    var c = el('article', 'card project-card');
    var many = (p.approvals || []).length > 1;
    if (p.photos && p.photos.length) {
      var img = el('img', 'card-img');
      img.src = p.photos[0]; img.alt = p.type + ' in ' + p.town; img.loading = 'lazy';
      c.appendChild(img);
    } else {
      var head = el('div', 'card-head');
      head.appendChild(el('span', 'card-type', typeLabel(p)));
      head.appendChild(el('span', 'card-year', yearsOf(p)));
      c.appendChild(head);
    }
    var body = el('div', 'card-body');
    if (p.photos && p.photos.length) body.appendChild(el('span', 'card-type', typeLabel(p)));
    body.appendChild(el('h3', 'card-title', place(p)));
    if (!many) body.appendChild(el('p', 'card-text', p.summary));
    var tags = el('div', 'tags');
    tags.appendChild(el('span', 'tag', p.borough === 'Other' ? 'Further afield' : p.borough));
    if (p.tour) tags.appendChild(el('span', 'tag', '3D tour'));
    body.appendChild(tags);
    var links = el('div', 'card-links');
    var m = el('a', '', 'Show on map'); m.href = (document.getElementById('map') ? '#' : 'projects.html#') + p.id;
    m.addEventListener('click', function (e) { if (window.TCPMap && window.TCPMap.focus(p.id)) { e.preventDefault(); history.replaceState(null, '', '#' + p.id); } });
    links.appendChild(m);
    if (featuredIds[p.id]) { var v = el('a', '', 'View project'); v.href = 'project-' + p.id + '.html'; links.appendChild(v); }
    if (!many) {
      var one = (p.approvals || [])[0];
      if (one && one.link) {
        var r = el('a', '', 'Council record'); r.href = one.link; r.target = '_blank'; r.rel = 'noopener';
        r.setAttribute('aria-label', 'Council planning record for ' + place(p) + ' (opens in a new tab)');
        links.appendChild(r);
      }
    } else {
      // a house with several approvals: each job gets its own date, description and council link
      var ul = el('ul', 'approval-list');
      // jobs that match the search come first, then newest first
      var hit = function (a) { var d = norm((a.summary || '') + ' ' + a.route); return parsed.words.length && parsed.words.every(function (w) { return has(d, w); }) ? 0 : 1; };
      p.approvals.slice().reverse().sort(function (a, b) { return hit(a) - hit(b); }).forEach(function (a) {
        var li = el('li');
        var top = el('div', 'approval-top');
        top.appendChild(el('span', 'approval-year', a.year || ''));
        top.appendChild(el('span', 'approval-desc', a.summary || a.route));
        li.appendChild(top);
        li.appendChild(el('div', 'approval-meta', a.route + (a.ref ? ' · Ref ' + a.ref : '')));
        if (a.link) {
          var l = el('a', 'approval-link', 'Council record for this job');
          l.href = a.link; l.target = '_blank'; l.rel = 'noopener';
          l.setAttribute('aria-label', 'Council record for the ' + (a.year || '') + ' job at ' + place(p) + (a.ref ? ', ' + a.ref : '') + ' (opens in a new tab)');
          li.appendChild(l);
        }
        ul.appendChild(li);
      });
      body.appendChild(ul);
    }
    body.appendChild(links);
    c.appendChild(body);
    return c;
  }

  function render() {
    chips.forEach(function (c) { c.setAttribute('aria-pressed', c._type === state.type ? 'true' : 'false'); });
    var filtering = !!(state.type || state.q || state.area || state.year || state.route);
    if (clear) clear.hidden = !filtering;
    parseQuery();
    var found = all.filter(matches), relaxed = false;
    if (!found.length && parsed.words.length > 1) {
      // nothing has every word: show the projects with the most of them instead
      var keep = parsed.words;
      parsed.words = [];
      found = all.filter(matches).filter(function (p) { return keep.some(function (w) { return has(text(p), w); }); });
      parsed.words = keep; relaxed = true;
    }
    if (ranked()) {
      found.forEach(score);
      found.sort(function (a, b) { return b._s - a._s; });
    }
    // keep the map on this page showing the same projects as the list
    var ids = null;
    if (filtering) { ids = {}; found.forEach(function (p) { ids[p.id] = true; }); }
    window.TCPFilterIds = ids;
    if (window.TCPMap && !fixedBorough) {
      window.TCPMap.setOnly(ids);
      if (parsed.place && window.TCPMap.centre) window.TCPMap.centre(parsed.place.lat / parsed.place.n, parsed.place.lng / parsed.place.n);
    }
    var cap = limit || shownCount;
    var shown = found.slice(0, cap);
    var order = parsed.place ? ', closest to ' + parsed.place.name + ' first' : ranked() ? ', best matches first' : '';
    if (relaxed) order += '. Nothing matched every word, so these are the closest';
    if (parsed.note) order += '. ' + parsed.note;
    if (count) count.textContent = (filtering && found.length < all.length ? found.length + ' of ' + all.length + ' approved projects match' : all.length + ' approved projects') + order;
    if (more) more.hidden = !!limit || found.length <= cap;
    list.innerHTML = '';
    if (!shown.length) {
      list.appendChild(el('p', 'empty', !all.length && fixedBorough ? 'Projects in ' + fixedBorough + ' are being added. Call 07843 561129 to hear about our work nearby.' : 'No projects match those filters. Try a nearby town or another type of work.'));
      return;
    }
    // the nearest project that has everything asked for, to explain a far-away best match
    var nearestFull = null;
    if (parsed.place) found.forEach(function (p) {
      var wy = p._why || {};
      var full = wy.words && wy.words.length === parsed.words.length && wy.details.length === (state.boost || []).length;
      if (full && (!nearestFull || km(p, parsed.place) < km(nearestFull, parsed.place))) nearestFull = p;
    });
    function milesText(p) {
      var m = km(p, parsed.place) / 1.609;
      return m < 0.3 ? (parsed.place.exact ? 'very close to ' : 'in ') + parsed.place.name : m.toFixed(1) + ' miles from ' + parsed.place.name;
    }
    // one line saying why a top result was picked
    function reason(p) {
      var wy = p._why || { words: [], details: [] }, bits = [];
      var said = wy.words.filter(function (x) { return x !== 'to'; });
      if (wy.phrase) bits.push('includes \u201c' + wy.phrase + '\u201d');
      else if (said.length) bits.push('includes ' + said.map(function (x) { return '\u201c' + x + '\u201d'; }).join(' and '));
      if (wy.details.length) bits.push(wy.details.join(', '));
      if (parsed.place) {
        var m = km(p, parsed.place) / 1.609;
        if (m < 1) bits.push('very close: ' + milesText(p));
        else if (m < 3) bits.push('close by: ' + milesText(p));
        else if (p === nearestFull) bits.push('nothing closer has all of this: ' + milesText(p));
        else bits.push(milesText(p));
      }
      if (wy.clear) bits.push('a clear example of this work');
      if (!bits.length) bits.push('recent and fully described');
      var out = bits.join(' · ');
      return out.charAt(0).toUpperCase() + out.slice(1);
    }
    var showBest = ranked() && found.length > 1;
    shown.forEach(function (p, i) {
      var c = card(p), tags = c.querySelector('.tags');
      if (showBest && i < 3) {
        c.classList.add('is-best');
        var head = c.querySelector('.card-body');
        head.insertBefore(el('span', 'best-badge', 'Best match ' + (i + 1)), head.firstChild);
      }
      if (parsed.place) tags.insertBefore(el('span', 'tag tag-near', milesText(p).replace(/^./, function (x) { return x.toUpperCase(); })), tags.firstChild);
      list.appendChild(c);
    });
  }
  render();
})();
