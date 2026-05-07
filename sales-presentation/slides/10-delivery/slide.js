(function() {
  var revObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) e.target.classList.add('visible');
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('#s10-delivery .s10d-reveal').forEach(function(el) { revObs.observe(el); });

  var wrapper = document.getElementById('s10-delivery-wrapper');
  var phaseIds = ['s10d-frame', 's10d-govern', 's10d-specify', 's10d-ship', 's10d-improve'];

  function isDeliveryActive() {
    if (!wrapper) return false;
    var rect = wrapper.getBoundingClientRect();
    var midpoint = window.innerHeight / 2;
    return rect.top <= midpoint && rect.bottom >= midpoint;
  }

  function currentPhaseIndex() {
    for (var i = 0; i < phaseIds.length; i++) {
      var input = document.getElementById(phaseIds[i]);
      if (input && input.checked) return i;
    }
    return 0;
  }

  function setPhase(idx) {
    var bounded = Math.max(0, Math.min(idx, phaseIds.length - 1));
    var input = document.getElementById(phaseIds[bounded]);
    if (input) input.checked = true;
  }

  document.addEventListener('keydown', function(e) {
    if (!isDeliveryActive()) return;
    if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
    e.preventDefault();
    var delta = e.key === 'ArrowDown' ? 1 : -1;
    setPhase(currentPhaseIndex() + delta);
  });
})();
