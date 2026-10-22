(function () {
  var box = document.getElementById('map');
  if (!box || !window.L) return;
  var borough = box.getAttribute('data-borough') || '';
  var projects = (window.TCP_PROJECTS || []).filter(function (p) { return typeof p.lat === 'number' && typeof p.lng === 'number' && (!borough || p.borough === borough); });
  var map = L.map(box, { scrollWheelZoom: false, maxZoom: 17 }).setView([51.67, -0.2], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 17,
    className: 'map-tiles',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
  // let the page scroll past the map until someone clicks into it
  map.on('focus click', function () { map.scrollWheelZoom.enable(); });
  map.on('blur mouseout', function () { map.scrollWheelZoom.disable(); });

  var pin = L.divIcon({ className: 'tcp-pin', html: '<span></span>', iconSize: [22, 22], iconAnchor: [11, 11], popupAnchor: [0, -12] });
  var group = L.markerClusterGroup ? L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 48,
    spiderfyOnMaxZoom: true,
    iconCreateFunction: function (c) {
      var n = c.getChildCount();
      var size = n < 10 ? 36 : n < 50 ? 44 : 54;
      return L.divIcon({ className: 'tcp-cluster', html: '<span>' + n + '</span>', iconSize: [size, size] });
    }
  }) : L.featureGroup();
  map.addLayer(group);

  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function place(p) { return p.street ? p.street + ', ' + p.town : p.town; }

  function popup(p) {
    var img = p.photos && p.photos.length ? '<img class="pin-img" src="' + esc(p.photos[0]) + '" alt="">' : '';
    var items = (p.approvals || []).slice().reverse().map(function (a) {
      return '<li><span class="pin-year">' + esc(a.year || '') + '</span><span>' + esc(a.summary || a.route) +
        '<em>' + (a.summary ? esc(a.route) : '') + (a.ref ? (a.summary ? ' · ' : '') + 'Ref ' + esc(a.ref) : '') + '</em>' +
        (a.link ? '<a href="' + esc(a.link) + '" target="_blank" rel="noopener">See the approved plans</a>' : '') + '</span></li>';
    }).join('');
    return '<div class="pin-card">' + img +
      '<span class="pin-type">' + esc(p.type === 'Other approvals' ? 'Planning approval' : p.type) + '</span>' +
      '<strong>' + esc(place(p)) + '</strong>' +
      '<div class="meta">' + esc(p.borough === 'Other' ? 'Further afield' : p.borough) + (p.tour ? ' · <a href="' + esc(p.tour) + '" target="_blank" rel="noopener">3D tour</a>' : '') + '</div>' +
      '<ul class="pin-list">' + items + '</ul></div>';
  }

  var markers = projects.map(function (p) {
    var m = L.marker([p.lat, p.lng], { icon: pin, title: place(p), alt: place(p) });
    m.bindPopup(popup(p), { maxWidth: 300 });
    m._p = p;
    return m;
  });

  // optional filter controls (full map page)
  var search = document.getElementById('map-search');
  var typeSel = document.getElementById('map-type');
  var areaSel = document.getElementById('map-area');
  var count = document.getElementById('map-count');
  var reset = document.getElementById('map-reset');
  function fill(sel, values) { if (!sel) return; values.forEach(function (v) { var o = document.createElement('option'); o.value = v; o.textContent = v === 'Other approvals' ? 'Other planning approvals' : v; sel.appendChild(o); }); }
  function tally(key) { var c = {}; projects.forEach(function (p) { c[p[key]] = (c[p[key]] || 0) + 1; }); return Object.keys(c).sort(function (a, b) { return c[b] - c[a]; }); }
  fill(typeSel, tally('type'));
  fill(areaSel, tally('borough').filter(function (b) { return b !== 'Other'; }));

  function matches(p) {
    if (typeSel && typeSel.value && p.type !== typeSel.value) return false;
    if (areaSel && areaSel.value && p.borough !== areaSel.value) return false;
    var q = search ? search.value.trim().toLowerCase() : '';
    if (q) {
      var hay = [p.street, p.town, p.district, p.borough, p.type].concat((p.approvals || []).map(function (a) { return a.summary || a.route; })).join(' ').toLowerCase();
      var words = q.split(/\s+/);
      for (var i = 0; i < words.length; i++) if (hay.indexOf(words[i]) === -1) return false;
    }
    return true;
  }

  function draw(fit) {
    var shown = markers.filter(function (m) { return matches(m._p); });
    group.clearLayers();
    if (group.addLayers) group.addLayers(shown); else shown.forEach(function (m) { group.addLayer(m); });
    var filtering = (search && search.value) || (typeSel && typeSel.value) || (areaSel && areaSel.value);
    if (count) count.textContent = filtering ? shown.length + ' of ' + markers.length + ' projects shown' : markers.length + ' approved projects on the map';
    if (reset) reset.hidden = !filtering;
    if (fit && shown.length) {
      var b = L.latLngBounds(shown.map(function (m) { return m.getLatLng(); }));
      if (filtering || borough) map.fitBounds(b, { padding: [40, 40], maxZoom: 15 });
      else map.setView([51.67, -0.2], 11); // home patch; projects further afield sit in clusters outside it
    }
  }

  var timer;
  if (search) search.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(function () { draw(true); }, 250); });
  [typeSel, areaSel].forEach(function (s) { if (s) s.addEventListener('change', function () { draw(true); }); });
  if (reset) reset.addEventListener('click', function () { [search, typeSel, areaSel].forEach(function (f) { if (f) f.value = ''; }); draw(true); });
  draw(true);

  // map.html#p012 opens that project
  function openHash() {
    var id = location.hash.replace('#', '');
    if (!/^p\d+$/.test(id)) return;
    var m = markers.filter(function (x) { return x._p.id === id; })[0];
    if (!m) return;
    if (!group.hasLayer(m)) { [search, typeSel, areaSel].forEach(function (f) { if (f) f.value = ''; }); draw(false); }
    if (group.zoomToShowLayer) group.zoomToShowLayer(m, function () { m.openPopup(); });
    else { map.setView(m.getLatLng(), 15); m.openPopup(); }
  }
  openHash();
  window.addEventListener('hashchange', openHash);
})();
