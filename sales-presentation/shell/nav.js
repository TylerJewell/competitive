const views = [
    document.getElementById('title'),
    document.getElementById('hero-wrapper'),
    document.getElementById('st-wrapper'),
    document.getElementById('s2-wrapper'),
    document.getElementById('s4-wrapper'),
    document.getElementById('s5-wrapper'),
    document.getElementById('s6-wrapper'),
    document.getElementById('s7-problem'),
    document.getElementById('s7-answer-wrapper'),
    document.getElementById('cust-wrapper'),
    document.getElementById('pkg-wrapper'),
    document.getElementById('s9-wrapper'),
    document.getElementById('demo-wrapper'),
    document.getElementById('closing')
  ].filter(Boolean);

  function currentViewIndex() {
    var scrollY = window.scrollY || window.pageYOffset;
    var best = 0;
    for (var i = 0; i < views.length; i++) {
      if (views[i].offsetTop <= scrollY + 10) best = i;
    }
    return best;
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowRight') {
      e.preventDefault();
      var idx = currentViewIndex();
      if (idx < views.length - 1) {
        views[idx + 1].scrollIntoView({ behavior: 'smooth' });
      }
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      var idx = currentViewIndex();
      var scrollY = window.scrollY || window.pageYOffset;
      // If we're partway into the current view, go to its top first
      if (scrollY > views[idx].offsetTop + 10 && idx >= 0) {
        views[idx].scrollIntoView({ behavior: 'smooth' });
      } else if (idx > 0) {
        views[idx - 1].scrollIntoView({ behavior: 'smooth' });
      }
    }
  });
})();