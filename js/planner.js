/* "What are you planning?" on the projects page: three picture questions, then the matching
   approved projects and a way to talk it through. No prices: fees are discussed in person. */
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
  var answers = {}, labels = {}, now = 1;
  var PROPERTY_WORDS = { detached: ['detached house', 'detached'], semi: ['semi-detached', 'semi detached'], terraced: ['terrace'], bungalow: ['bungalow'],
                         flat: ['maisonette', 'ground floor flat', 'first floor flat', 'apartment'], commercial: ['commercial', 'shop', 'office', 'retail'] };
  var FLOOR_WORDS = { f1: ['single storey', 'bungalow'], f2: ['two storey', 'first floor'], f3: ['second floor', 'three storey', 'third floor'] };

  function go(n, focus) {
    now = n;
    steps.forEach(function (s) { s.hidden = parseInt(s.getAttribute('data-n'), 10) !== n; });
    result.hidden = n !== 4;
    back.hidden = n === 1;
    restart.hidden = n !== 4;
    stepLabel.textContent = n < 4 ? 'Step ' + n + ' of 3' : 'Your answers';
    if (n === 3) {
      // only offer what suits the property, e.g. no loft conversion for a flat
      box.querySelectorAll('[data-step="plan"]').forEach(function (b) {
        var not = (b.getAttribute('data-not') || '').split(' ');
        b.hidden = not.indexOf(answers.property) !== -1;
      });
    }
    if (n === 4) showResult();
    if (focus) {
      var target = n === 4 ? result : box.querySelector('.pl-step[data-n="' + n + '"] .pl-tile:not([hidden])');
      if (target) target.focus();
    }
  }

  function article(s) { return /^[aeiou]/i.test(s) ? 'an ' : 'a '; }
  function showResult() {
    var plan = PLANS[answers.plan] || PLANS.unsure;
    var prop = (labels.property || '').toLowerCase();
    var floors = (labels.floors || '').toLowerCase();
    var what = answers.plan === 'unsure' ? 'Not sure yet what to do with ' + article(prop) + prop
                                         : plan.label + ' to ' + article(prop) + prop;
    box.querySelector('[data-pl-summary]').textContent = what + (floors ? ' (' + floors + ' now)' : '');
    var n = window.TCPProjects.count(plan);
    box.querySelector('[data-pl-count]').textContent = answers.plan === 'unsure'
      ? 'That is a good place to start a conversation. Browse all ' + n + ' approved projects for ideas, or talk it through with us.'
      : 'We have ' + n + ' approved projects like this. Every house is different, so the best next step is a conversation at the property.';
    var about = 'Property: ' + labels.property + ', ' + floors + '. Planning: ' + plan.label + '.';
    box.querySelector('[data-pl-enquire]').href = 'contact.html?type=' + encodeURIComponent(plan.label) + '&about=' + encodeURIComponent(about);
  }

  box.querySelectorAll('.pl-tile').forEach(function (b) {
    b.addEventListener('click', function () {
      var key = b.getAttribute('data-step');
      answers[key] = b.getAttribute('data-v');
      labels[key] = b.getAttribute('data-label');
      box.querySelectorAll('[data-step="' + key + '"]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      go(now + 1, true);
    });
  });
  back.addEventListener('click', function () { go(Math.max(1, now - 1), true); });
  restart.addEventListener('click', function () { answers = {}; labels = {}; box.querySelectorAll('.pl-tile').forEach(function (x) { x.removeAttribute('aria-pressed'); }); window.TCPProjects.set({}); go(1, true); });
  box.querySelector('[data-pl-show]').addEventListener('click', function () {
    var plan = PLANS[answers.plan] || {};
    // the property and floors answers don't remove projects; they lift the closest examples to the top
    var boost = (PROPERTY_WORDS[answers.property] || []).concat(FLOOR_WORDS[answers.floors] || []);
    window.TCPProjects.set({ type: plan.type, q: plan.q, boost: boost });
    var list = document.querySelector('.pm-head') || document.getElementById('project-list');
    list.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  // arriving from a property picture on the home page: skip to the next question
  try {
    var p = new URLSearchParams(location.search).get('property');
    var tile = p && box.querySelector('[data-step="property"][data-v="' + p + '"]');
    if (tile) { answers.property = p; labels.property = tile.getAttribute('data-label'); tile.setAttribute('aria-pressed', 'true'); go(2, false); }
    if (tile || location.hash === '#planner') { openBox(false); box.scrollIntoView(); }
  } catch (e) {}
})();
