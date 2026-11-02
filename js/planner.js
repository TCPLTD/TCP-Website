/* "What are you planning?" on the projects page: what the work is, any details, and where the property is.
   Everything asked can be matched against the council descriptions in our records, so the results show
   the closest examples first, nearest first. No prices: fees are discussed in person. */
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

  // Details people can pick for each kind of work, worded as council descriptions word them.
  var DETAILS = {
    rear: [['Single storey', ['single storey']], ['Two storey', ['two storey', 'first floor rear']], ['Wraps round the side', ['side and rear', 'wrap']], ['Front extension too', ['front']], ['With a loft conversion', ['loft', 'dormer']]],
    side: [['Single storey', ['single storey']], ['Two storey', ['two storey', 'first floor side']], ['Wraps round the back', ['side and rear', 'wrap']], ['Garage conversion too', ['garage conversion']]],
    twostorey: [['Side', ['two storey side', 'first floor side']], ['Rear', ['two storey rear', 'first floor rear']], ['Side and rear', ['side and rear']], ['With a loft conversion', ['loft', 'dormer']]],
    loft: [['Rear dormer', ['rear dormer', 'dormer']], ['Hip to gable', ['hip to gable']], ['Rooflights', ['rooflight', 'roof light', 'velux', 'skylight']], ['Juliet balcony', ['juliet', 'balcony']], ['With an extension', ['extension']]],
    garage: [['With an extension', ['extension']], ['New window to the front', ['window']]],
    garden: [['Garden room or outhouse', ['outhouse', 'outbuilding']], ['Gym or office', ['gym', 'office']], ['Pool', ['pool', 'swimming']]],
    porch: [['Porch', ['porch']], ['Front extension', ['front extension']]]
  };

  var PLANS = JSON.parse(document.getElementById('pl-plans').textContent);
  var result = box.querySelector('.pl-result');
  var stepLabel = box.querySelector('[data-pl-step]');
  var back = box.querySelector('[data-pl-back]');
  var restart = box.querySelector('[data-pl-restart]');
  var placeInput = document.getElementById('pl-place');
  var hint = box.querySelector('[data-pl-hint]');
  var detailBox = box.querySelector('[data-pl-details]');
  var planKey = null, plan = null, picked = [], place = null, now = 'plan';

  function order() { return DETAILS[planKey] ? ['plan', 'details', 'where'] : ['plan', 'where']; }
  function go(name, focus) {
    now = name;
    box.querySelectorAll('.pl-step').forEach(function (s) { s.hidden = s.getAttribute('data-n') !== name; });
    result.hidden = name !== 'result';
    back.hidden = name === 'plan';
    restart.hidden = name !== 'result';
    var steps = order(), i = steps.indexOf(name);
    stepLabel.textContent = name === 'result' ? 'Your answers' : 'Step ' + (i + 1) + ' of ' + steps.length;
    if (name === 'details') buildDetails();
    if (name === 'result') showResult();
    if (focus) {
      var target = name === 'result' ? result : name === 'where' ? placeInput : box.querySelector('.pl-step[data-n="' + name + '"] button');
      if (target) target.focus();
    }
  }
  function next() { var s = order(); go(s[s.indexOf(now) + 1] || 'result', true); }

  function buildDetails() {
    detailBox.innerHTML = '';
    DETAILS[planKey].forEach(function (d) {
      var n = window.TCPProjects.countWith({ type: plan.type, q: plan.q }, d[1]);
      if (!n) return;
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'chip';
      b.setAttribute('aria-pressed', picked.indexOf(d) !== -1 ? 'true' : 'false');
      b.appendChild(document.createTextNode(d[0]));
      var c = document.createElement('span'); c.className = 'count'; c.textContent = '(' + n + ')'; b.appendChild(c);
      // one press picks the detail and moves straight on to the next question
      b.addEventListener('click', function () { picked = [d]; next(); });
      detailBox.appendChild(b);
    });
  }

  function query() { return [plan.q, place ? place.toLowerCase() : ''].join(' ').trim(); }
  function showResult() {
    var extra = picked.map(function (d) { return d[0].toLowerCase(); }).join(', ');
    var what = plan.label === 'Not sure yet' ? 'Not sure yet' : plan.label + (extra ? ': ' + extra : '');
    box.querySelector('[data-pl-summary]').textContent = what + (place ? ', near ' + place : '');
    var n = window.TCPProjects.count({ type: plan.type, q: query() });
    var order = picked.length && place ? 'the closest matches and nearest first' : picked.length ? 'the closest matches first' : place ? 'the nearest first' : '';
    box.querySelector('[data-pl-count]').textContent = plan.label === 'Not sure yet'
      ? 'A conversation is the best place to start. Browse our ' + n + ' approved projects' + (place ? ', nearest first,' : '') + ' for ideas, or talk it through with us.'
      : 'We have ' + n + ' approved projects like this' + (order ? ', and we will show you ' + order : '') + '. Every house is different, so the best next step is a conversation at the property.';
    var about = 'Planning: ' + plan.label + (extra ? ' (' + extra + ')' : '') + '.' + (place ? ' Property in or near ' + place + '.' : '');
    box.querySelector('[data-pl-enquire]').href = 'contact.html?type=' + encodeURIComponent(plan.label) + '&about=' + encodeURIComponent(about) + (place ? '&area=' + encodeURIComponent(place) : '');
  }

  box.querySelectorAll('.pl-tile').forEach(function (b) {
    b.addEventListener('click', function () {
      var k = b.getAttribute('data-v');
      if (k !== planKey) picked = [];
      planKey = k; plan = PLANS[k];
      box.querySelectorAll('.pl-tile').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      next();
    });
  });
  box.querySelector('[data-pl-next]').addEventListener('click', function () { picked = []; next(); });
  function usePlace() {
    var typed = placeInput.value.trim();
    if (!typed) { place = null; next(); return; }
    // a full postcode such as "EN4 9JT": the first half is enough to find the area
    var m = typed.match(/^([a-z]{1,2}\d[a-z\d]?)\s*\d[a-z]{2}$/i);
    var found = window.TCPProjects.place(m ? m[1] : typed);
    if (!found) { hint.textContent = 'We could not find "' + typed + '" in our project records. Try a nearby town or the first half of the postcode, or skip this.'; return; }
    hint.textContent = '';
    place = found;
    next();
  }
  box.querySelector('[data-pl-where]').addEventListener('click', usePlace);
  placeInput.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !placeInput.getAttribute('aria-activedescendant')) { e.preventDefault(); usePlace(); } });
  box.querySelector('[data-pl-skip]').addEventListener('click', function () { place = null; hint.textContent = ''; next(); });
  back.addEventListener('click', function () {
    var s = order(), i = now === 'result' ? s.length : s.indexOf(now);
    go(s[Math.max(0, i - 1)], true);
  });
  restart.addEventListener('click', function () {
    planKey = null; plan = null; picked = []; place = null; placeInput.value = ''; hint.textContent = '';
    box.querySelectorAll('.pl-tile').forEach(function (x) { x.removeAttribute('aria-pressed'); });
    window.TCPProjects.set({}); go('plan', true);
  });
  box.querySelector('[data-pl-show]').addEventListener('click', function () {
    window.TCPProjects.set({ type: plan.type, q: query(), boost: picked.map(function (d) { return { label: d[0], words: d[1] }; }) });
    var list = document.querySelector('.pm-head') || document.getElementById('project-list');
    list.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  if (location.hash === '#planner') { openBox(false); box.scrollIntoView(); }
})();
