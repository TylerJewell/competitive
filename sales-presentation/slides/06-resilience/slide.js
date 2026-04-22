(function() {
  var revObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) e.target.classList.add('visible');
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('#s6 .s6-reveal').forEach(function(el) { revObs.observe(el); });
})();