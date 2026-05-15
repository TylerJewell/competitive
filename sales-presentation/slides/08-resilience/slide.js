(function() {
  var revObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) e.target.classList.add('visible');
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('#s6 .s6-reveal').forEach(function(el) { revObs.observe(el); });

  var frame = document.querySelector('#s6 .s6-frame-wrap');
  var toggle = document.querySelector('#s6 .s6-expand-toggle');
  if (frame && toggle) {
    toggle.addEventListener('click', function() {
      var expanded = frame.classList.toggle('s6-expanded');
      toggle.textContent = expanded ? '-' : '+';
      toggle.setAttribute('aria-label', expanded ? 'Collapse resilience tester' : 'Expand resilience tester');
      toggle.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    });
  }
})();
