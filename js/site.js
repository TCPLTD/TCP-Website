(function () {
  var side = document.getElementById('side');
  var btn = side && side.querySelector('.menu-btn');
  if (btn) {
    btn.addEventListener('click', function () {
      var open = side.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? 'Close' : 'Menu';
    });
  }
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
