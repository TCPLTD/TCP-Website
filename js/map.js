(function () {
  var box = document.getElementById('map');
  if (!box || !window.L) return;
  var borough = box.getAttribute('data-borough') || '';
  var projects = (window.TCP_PROJECTS || []).filter(function (p) { return typeof p.lat === 'number' && typeof p.lng === 'number' && (!borough || p.borough === borough); });
  var map = L.map(box, { scrollWheelZoom: false }).setView([51.67, -0.2], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);
  var pin = L.divIcon({ className: '', html: '<span style="display:block;width:18px;height:18px;border-radius:50%;background:#173B53;border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.35)"></span>', iconSize: [18, 18], iconAnchor: [9, 9], popupAnchor: [0, -10] });

  function esc(s) { return String(s || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var bounds = [];
  projects.forEach(function (p) {
    var html = '<div class="pin-card"><div class="pin-ph">Photos to come</div>' +
      '<strong>' + esc(p.street) + ', ' + esc(p.town) + '</strong>' +
      '<div class="meta">' + esc(p.type) + ' · Approved ' + esc(p.year) + '</div>' +
      '<p style="margin:6px 0 8px">' + esc(p.summary) + '</p>' +
      (p.councilLink ? '<a href="' + esc(p.councilLink) + '" target="_blank" rel="noopener">See the approved plans</a>' : '') +
      '</div>';
    L.marker([p.lat, p.lng], { icon: pin, title: p.street + ', ' + p.town }).addTo(map).bindPopup(html);
    bounds.push([p.lat, p.lng]);
  });
  if (bounds.length > 1) map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
  else if (bounds.length === 1) map.setView(bounds[0], 13);
})();
