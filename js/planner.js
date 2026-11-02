/* "What are you planning?" on the projects page: what the work is, then where the property is.
   Both can be matched against our records, so the results show the closest examples nearest first.
   No prices: fees are discussed in person. */
(function () {
  var box = document.getElementById('planner');
  if (!box || !window.TCPProjects) return;
  // the questions start folded away under the search, and open from the button or a link to #planner
  var opener = document.getElementById('pl-open');
  function openBox(focus) {
    box.hidden = false;
    if (opener) { opener.setAttribute('aria-expanded', 'true'); opener.parentNode.hidden = true; }
    if (focus) { var t = box.querySelector('.pl-step:not([hidden]) .pl-tile'); if (t) t.focus(); }
  }
  if (opener) { opener.parentNode.hidden = false; opener.addEventListener('click', function () { openBox(true); }); }
  else box.hidden = false;

  var PLANS = JSON.parse(document.getElementById('pl-plans').textContent);
  var steps = box.querySelectorAll('.pl-step');
  var result = box.querySelector('.pl-result');
  var stepLabel = box.querySelector('[data-pl-step]');
  var back = box.querySelector('[data-pl-back]');
  var restart = box.querySelector('[data-pl-restart]');
  var placeInput = document.getElementById('pl-place');
  var hint = box.querySelector('[data-pl-hint]');
  var plan = null, place = null, now = 1;

  function go(n, focus) {
    now = n;
    steps.forEach(function (s) { s.hidden = parseInt(s.getAttribute('data-n'), 10) !== n; });
    result.hidden = n !== 3;
    back.hidden = n === 1;
    restart.hidden = n !== 3;
    stepLabel.textContent = n < 3 ? 'Step ' + n + ' of 2' : 'Your answers';
    if (n === 3) showResult();
    if (focus) {
      var target = n === 3 ? result : n === 2 ? placeInput : box.querySelector('.pl-step[data-n="1"] .pl-tile');
      if (target) target.focus();
    }
  }

  function query() { return [plan.q, place ? place.toLowerCase() : ''].join(' ').trim(); }
  function showResult() {
    var what = plan.label === 'Not sure yet' ? 'Not sure yet' : plan.label;
    box.querySelector('[data-pl-summary]').textContent = what + (place ? ' near ' + place : '');
    var n = window.TCPProjects.count({ type: plan.type, q: query() });
    box.querySelector('[data-pl-count]').textContent = plan.label === 'Not sure yet'
      ? 'A conversation is the best place to start. Browse our ' + n + ' approved projects' + (place ? ', nearest first,' : '') + ' for ideas, or talk it through with us.'
      : 'We have ' + n + ' approved projects like this' + (place ? ', and we will show you the nearest first' : '') + '. Every house is different, so the best next step is a conversation at the property.';
    var about = 'Planning: ' + plan.label + '.' + (place ? ' Property in or near ' + place + '.' : '');
    box.querySelector('[data-pl-enquire]').href = 'contact.html?type=' + encodeURIComponent(plan.label) + '&about=' + encodeURIComponent(about) + (place ? '&area=' + encodeURIComponent(place) : '');
  }

  box.querySelectorAll('.pl-tile').forEach(function (b) {
    b.addEventListener('click', function () {
      plan = PLANS[b.getAttribute('data-v')];
      box.querySelectorAll('.pl-tile').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      go(2, true);
    });
  });
  function usePlace() {
    var typed = placeInput.value.trim();
    if (!typed) { place = null; go(3, true); return; }
    // a full postcode such as "EN4 9JT": the first half is enough to find the area
    var m = typed.match(/^([a-z]{1,2}\d[a-z\d]?)\s*\d[a-z]{2}$/i);
    var found = window.TCPProjects.place(m ? m[1] : typed);
    if (!found) { hint.textContent = 'We could not find "' + typed + '" in our project records. Try a nearby town or the first half of the postcode, or skip this.'; return; }
    hint.textContent = '';
    place = found;
    go(3, true);
  }
  box.querySelector('[data-pl-where]').addEventListener('click', usePlace);
  placeInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); usePlace(); } });
  box.querySelector('[data-pl-skip]').addEventListener('click', function () { place = null; hint.textContent = ''; go(3, true); });
  back.addEventListener('click', function () { go(Math.max(1, now - 1), true); });
  restart.addEventListener('click', function () {
    plan = null; place = null; placeInput.value = ''; hint.textContent = '';
    box.querySelectorAll('.pl-tile').forEach(function (x) { x.removeAttribute('aria-pressed'); });
    window.TCPProjects.set({}); go(1, true);
  });
  box.querySelector('[data-pl-show]').addEventListener('click', function () {
    window.TCPProjects.set({ type: plan.type, q: query() });
    var list = document.querySelector('.pm-head') || document.getElementById('project-list');
    list.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  if (location.hash === '#planner') { openBox(false); box.scrollIntoView(); }
})();
