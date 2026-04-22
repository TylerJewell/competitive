/* ── KIOSK MODE (?kiosk in URL) ── */
(function() {
  if (!new URLSearchParams(location.search).has('kiosk')) return;

  var kioskParam = new URLSearchParams(location.search).get('kiosk');
  var SLIDE_MS = (kioskParam && !isNaN(kioskParam) ? parseInt(kioskParam) : 30) * 1000;
  var TAB_MS   = Math.round(SLIDE_MS / 6);

  const SECTION_IDS = [
    'hero-wrapper','st-wrapper','s2-wrapper','s4-wrapper',
    's5-wrapper','s6-wrapper','s7-problem','cust-wrapper',
    'pkg-wrapper','s9-wrapper'
  ];

  function scrollMid(el) {
    return el.offsetTop + Math.max(0, (el.offsetHeight - window.innerHeight) * 0.4);
  }

  window.addEventListener('load', function() {
    setTimeout(function() {

      /* Build ordered stop list */
      var stops = [];
      SECTION_IDS.forEach(function(id) {
        var el = document.getElementById(id);
        if (el) stops.push({ type: 'slide', el: el });
      });
      var demoEl    = document.getElementById('demo-section');
      var closingEl = document.getElementById('closing');
      if (demoEl)    stops.push({ type: 'demo',  el: demoEl });
      if (closingEl) stops.push({ type: 'slide', el: closingEl });
      stops.sort(function(a,b){ return a.el.offsetTop - b.el.offsetTop; });

      /* Progress bar */
      var bar = document.createElement('div');
      bar.style.cssText = 'position:fixed;bottom:0;left:0;right:0;height:3px;z-index:99999;background:#111;pointer-events:none';
      var fill = document.createElement('div');
      fill.style.cssText = 'height:100%;width:0%;background:#F5C518';
      bar.appendChild(fill);
      document.body.appendChild(bar);

      var badge = document.createElement('div');
      badge.textContent = '⏵ KIOSK';
      badge.style.cssText = 'position:fixed;bottom:8px;right:14px;z-index:99999;font-family:monospace;font-size:10px;color:#444;letter-spacing:2px;pointer-events:none';
      document.body.appendChild(badge);

      var idx = 0, timer = null;

      function startFill(ms) {
        fill.style.transition = 'none';
        fill.style.width = '0%';
        requestAnimationFrame(function() {
          fill.style.transition = 'width ' + ms + 'ms linear';
          fill.style.width = '100%';
        });
      }

      function advance() {
        idx = (idx + 1) % stops.length;
        if (idx === 0) {
          window.scrollTo({ top: 0, behavior: 'smooth' });
          timer = setTimeout(function(){ show(0); }, 2000);
        } else {
          show(idx);
        }
      }

      function show(i) {
        idx = i;
        var stop = stops[i];
        var y = stop.type === 'demo' ? stop.el.offsetTop : scrollMid(stop.el);
        window.scrollTo({ top: y, behavior: 'smooth' });

        if (stop.type === 'demo') {
          var tabs = document.querySelectorAll('#demo-section .tab-btn');
          if (!tabs.length) { startFill(SLIDE_MS); timer = setTimeout(advance, SLIDE_MS); return; }
          var t = 0;
          tabs[0].click();
          startFill(TAB_MS * tabs.length);
          function nextTab() {
            t++;
            if (t < tabs.length) { tabs[t].click(); timer = setTimeout(nextTab, TAB_MS); }
            else { timer = setTimeout(advance, TAB_MS); }
          }
          timer = setTimeout(nextTab, TAB_MS);
        } else {
          startFill(SLIDE_MS);
          timer = setTimeout(advance, SLIDE_MS);
        }
      }

      /* Pause/resume on click */
      var paused = false;
      document.addEventListener('click', function() {
        if (!paused) {
          clearTimeout(timer);
          fill.style.transition = 'none';
          badge.textContent = '⏸ KIOSK';
          paused = true;
        } else {
          badge.textContent = '⏵ KIOSK';
          paused = false;
          advance();
        }
      });

      show(0);

    }, 800);
  });
})();