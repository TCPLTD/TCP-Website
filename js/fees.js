/* Design fee estimator. Set prices in PRICES (pounds) once agreed; null shows "We'll quote by phone".
   Key: project|package. Property type adjusts with FLAT_FACTOR and COMMERCIAL_FACTOR. */
(function () {
  var PRICES = {
    'Rear or side extension|Planning drawings': null,
    'Rear or side extension|Planning and building control': null,
    'Loft conversion|Planning drawings': null,
    'Loft conversion|Planning and building control': null,
    'Extension and loft|Planning drawings': null,
    'Extension and loft|Planning and building control': null,
    'Garage or garden room|Planning drawings': null,
    'Garage or garden room|Planning and building control': null,
    'New build|Planning drawings': null,
    'New build|Planning and building control': null
  };
  var FLAT_FACTOR = 1, COMMERCIAL_FACTOR = 1;

  var root = document.getElementById('fee-calc');
  if (!root) return;
  var state = { property: 'House', project: 'Loft conversion', pack: 'Planning drawings' };
  var priceEl = document.getElementById('fee-price');
  var sumEl = document.getElementById('fee-summary');
  var bcItem = document.getElementById('fee-bc');

  root.querySelectorAll('[data-q]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var q = btn.getAttribute('data-q');
      state[q] = btn.getAttribute('data-v');
      root.querySelectorAll('[data-q="' + q + '"]').forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      update();
    });
  });
  function update() {
    var base = PRICES[state.project + '|' + state.pack];
    var factor = state.property === 'Flat' ? FLAT_FACTOR : state.property === 'Commercial' ? COMMERCIAL_FACTOR : 1;
    priceEl.textContent = (base == null || state.project === 'Not sure yet') ? 'We’ll quote by phone' : 'From £' + Math.round(base * factor).toLocaleString('en-GB');
    sumEl.textContent = state.project + ' · ' + state.property + ' · ' + state.pack;
    bcItem.hidden = state.pack !== 'Planning and building control';
  }
  update();
})();
