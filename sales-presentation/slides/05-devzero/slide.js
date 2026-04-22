(function() {
  var script = [
    { type:'cmd', text:'/akka:specify "Customer loyalty program with points, tiers, and rewards"', phase:'specify' },
    { type:'ai',  text:'How should points expire? Fixed calendar window, rolling from last activity, or never?' },
    { type:'ok',  text:'[specify] spec.md written \u2714  Branch: 001-loyalty-service' },
    { type:'blank' },

    { type:'cmd', text:'/akka:clarify "Rolling 12-month expiry. Grace period before tier downgrade."', phase:'specify' },
    { type:'ok',  text:'[clarify] spec.md updated \u2714  2 decisions captured', trigger:'spec' },
    { type:'blank' },

    { type:'cmd', text:'/akka:plan "High-perf APIs, read data in views. Host client app in backend."', phase:'specify' },
    { type:'ok',  text:'[plan] plan.md written \u2714  Event Sourced Entities, Views, Endpoints + SPA' },
    { type:'blank' },

    { type:'cmd', text:'/akka:tasks && /akka:implement && /akka:build', phase:'implement' },
    { type:'lines', items: [
      { text:'[tasks] 6 tasks generated, dependency-ordered \u2714', cls:'ok' },
      { text:'[implement] Writing LoyaltyAccount entity...', cls:'ai' },
      { text:'[implement] Writing RewardsProgram entity...', cls:'ai' },
      { text:'[implement] Writing REST endpoints + views...', cls:'ai' },
      { text:'[implement] Writing RedemptionWorkflow...', cls:'ai' },
      { text:'[implement] Generating 50 unit tests...', cls:'ai' },
      { text:'[implement] 989 lines across 12 files \u2714  50/50 tests passing', cls:'ok' },
      { text:'[build] mvn compile \u2714  mvn test \u2714  service running on :8080', cls:'ok' },
    ], trigger:'arch'},
    { type:'blank' },

    { type:'cmd', text:'/akka:review && /akka:analyze && /akka:deploy', phase:'deploy' },
    { type:'lines', items: [
      { text:'[review] Spec compliance 100% \u2714  Coverage 94%', cls:'ok' },
      { text:'[analyze] Full cross-artifact traceability \u2714', cls:'ok' },
      { text:'[deploy] git commit \u2714  git push \u2714', cls:'ai' },
      { text:'[deploy] Container image built \u2714  Pushed to registry', cls:'ai' },
      { text:'[deploy] Routes configured \u2714  loyalty.acme.akka.app', cls:'ai' },
      { text:'[deploy] Deploying to your private Akka cloud \u2714  Active-active HA, 3 replicas', cls:'ok' },
    ]},
    { type:'blank' },
    { type:'warn', text:'\u2728 loyalty-service is live. Spec to production in 2 hours, 14 minutes.' },
  ];

  var body = document.getElementById('s5TermBody');
  var specCard = document.getElementById('s5Spec');
  var archCard = document.getElementById('s5Arch');
  var props = document.querySelectorAll('.s5-prop');
  var currentPhase = null;
  var cursorEl = null;

  var CMD_CHAR_MS  = 24;
  var AI_CHAR_MS   = 20;
  var OK_CHAR_MS   = 18;
  var LINE_DELAY   = 280;
  var PAUSE_AFTER_CMD = 500;
  var PAUSE_AFTER_STEP = 400;

  function scroll() { body.scrollTop = body.scrollHeight; }

  function removeCursor() {
    if (cursorEl) { cursorEl.remove(); cursorEl = null; }
  }

  function addCursor(parent) {
    removeCursor();
    cursorEl = document.createElement('span');
    cursorEl.className = 's5-cursor';
    parent.appendChild(cursorEl);
  }

  function highlightProp(phase) {
    if (phase && phase !== currentPhase) {
      currentPhase = phase;
      props.forEach(function(p) {
        p.classList.toggle('active', p.getAttribute('data-phase') === phase);
      });
    }
  }

  /* Artifact reveal + terminal reset logic */
  var revealQueue = [specCard, archCard];
  var revealIdx = 0;
  var s5Anchored = false;
  var s5Running = false;
  var s5DownCount = 0;
  var s5WrapperEl = document.getElementById('s5-wrapper');

  var s5UpCount = 0;
  var s5State = 'idle'; /* idle | forward | reverse | done */

  function fillTerminalFull() {
    body.innerHTML = '';
    removeCursor();
    for (var i = 0; i < script.length; i++) {
      var step = script[i];
      if (step.type === 'cmd') {
        var d = document.createElement('div');
        d.className = 's5-tline';
        d.innerHTML = '<span class="prompt">$ </span><span class="cmd">' + step.text + '</span>';
        body.appendChild(d);
      } else if (step.type === 'blank') {
        var d = document.createElement('div');
        d.className = 's5-tline';
        d.innerHTML = '&nbsp;';
        body.appendChild(d);
      } else if (step.type === 'lines') {
        for (var j = 0; j < step.items.length; j++) {
          var item = step.items[j];
          var ld = document.createElement('div');
          ld.className = 's5-tline';
          var c = item.cls === 'ok' ? 'success' : 'ai';
          ld.innerHTML = '<span class="' + c + '">' + item.text + '</span>';
          body.appendChild(ld);
        }
      } else {
        var cls = step.type === 'ok' ? 'success' : (step.type === 'warn' ? 'warn' : step.type);
        var d = document.createElement('div');
        d.className = 's5-tline';
        d.innerHTML = '<span class="' + cls + '">' + step.text + '</span>';
        body.appendChild(d);
      }
    }
    var end = document.createElement('div');
    end.className = 's5-tline';
    end.innerHTML = '<span class="prompt">$ </span>';
    body.appendChild(end);
    addCursor(end);
  }

  function resetS5() {
    body.innerHTML = '';
    removeCursor();
    specCard.classList.remove('show');
    archCard.classList.remove('show');
    revealIdx = 0;
    s5DownCount = 0;
    s5UpCount = 0;
    currentPhase = null;
    props.forEach(function(p) { p.classList.remove('active'); });
    s5Running = false;
    s5Anchored = false;
    s5State = 'idle';
  }

  function checkS5() {
    var wTop = s5WrapperEl.offsetTop;
    var wHeight = s5WrapperEl.offsetHeight;
    var wBottom = wTop + wHeight;
    var scrollY = window.scrollY;
    var viewBottom = scrollY + window.innerHeight;

    var progress = (scrollY - wTop) / (wHeight - window.innerHeight);

    var pastBelow = scrollY > wBottom;
    var pastAbove = viewBottom < wTop;
    var inView = !pastAbove && !pastBelow;
    var anchored = progress >= 0 && progress <= 1;

    if (pastAbove || pastBelow) {
      if (s5State !== 'idle') resetS5();
      return;
    }

    if (s5State === 'idle' && inView) {
      /* Wrapper just entered viewport — determine direction */
      if (viewBottom > wBottom - 10) {
        /* Bottom of wrapper is near bottom of viewport = scrolling up from below */
        s5State = 'reverse';
        s5Running = true;
        s5Anchored = true;
        fillTerminalFull();
        specCard.classList.add('show');
        archCard.classList.add('show');
        revealIdx = 2;
        s5UpCount = 0;
      } else {
        /* Forward entry — section in view (nav jump or scroll-in from above) */
        s5State = 'forward';
        s5Anchored = true;
        s5Running = true;
        setTimeout(function() { run(0); }, 600);
      }
    }

    /* Forward: detect when we first anchor */
    if (s5State === 'forward' && anchored && !s5Anchored) {
      s5Anchored = true;
      if (!s5Running) {
        s5Running = true;
        setTimeout(function() { run(0); }, 600);
      }
    }

    /* Forward: also reveal cards by scroll progress so fast scrollers see them */
    if (s5State === 'forward' && anchored) {
      if (progress >= 0.35 && !specCard.classList.contains('show')) {
        specCard.classList.add('show');
        if (revealIdx < 1) revealIdx = 1;
      }
      if (progress >= 0.65 && !archCard.classList.contains('show')) {
        archCard.classList.add('show');
        if (revealIdx < 2) revealIdx = 2;
      }
    }

    /* Reverse: peel off artifacts based on scroll progress toward top */
    if (s5State === 'reverse' && anchored) {
      /* progress 1 = bottom of wrapper, 0 = top. As we scroll up, progress decreases */
      if (progress < 0.55 && archCard.classList.contains('show')) {
        archCard.classList.remove('show');
      }
      if (progress < 0.25 && specCard.classList.contains('show')) {
        specCard.classList.remove('show');
      }
    }
  }
  window.addEventListener('scroll', checkS5, { passive: true });

  document.addEventListener('keydown', function(e) {
    if (!s5Anchored) return;

    if (e.key === 'ArrowDown') {
      s5DownCount++;
      if (s5DownCount % 3 === 0 && revealIdx < revealQueue.length) {
        revealQueue[revealIdx].classList.add('show');
        revealIdx++;
      }
    }

  });

  function fireTrigger(t) {
    if (t === 'spec' && !specCard.classList.contains('show')) {
      specCard.classList.add('show');
      if (revealIdx < 1) revealIdx = 1;
    }
    if (t === 'arch' && !archCard.classList.contains('show')) {
      archCard.classList.add('show');
      if (revealIdx < 2) revealIdx = 2;
    }
  }

  function typeText(span, text, charMs, cb) {
    var i = 0;
    function tick() {
      if (i < text.length) {
        span.textContent += text[i]; i++;
        scroll();
        setTimeout(tick, charMs);
      } else { if (cb) cb(); }
    }
    tick();
  }

  function makeLine(cls) {
    var div = document.createElement('div');
    div.className = 's5-tline';
    var span = document.createElement('span');
    span.className = cls;
    div.appendChild(span);
    body.appendChild(div);
    return span;
  }

  function playLines(items, idx, cb) {
    if (idx >= items.length) { if (cb) cb(); return; }
    var item = items[idx];
    var clsMap = { ok:'success', ai:'ai' };
    var span = makeLine(clsMap[item.cls] || 'success');
    addCursor(span.parentNode);
    typeText(span, item.text, OK_CHAR_MS, function() {
      setTimeout(function() { playLines(items, idx + 1, cb); }, LINE_DELAY);
    });
  }

  function run(idx) {
    if (idx >= script.length) {
      removeCursor();
      var end = document.createElement('div');
      end.className = 's5-tline';
      end.innerHTML = '<span class="prompt">$ </span>';
      body.appendChild(end);
      addCursor(end);
      scroll();
      props.forEach(function(p) { p.classList.remove('active'); });
      return;
    }

    var step = script[idx];
    if (step.phase) highlightProp(step.phase);

    if (step.type === 'blank') {
      var bl = document.createElement('div');
      bl.className = 's5-tline';
      bl.innerHTML = '&nbsp;';
      body.appendChild(bl);
      scroll();
      setTimeout(function() { run(idx + 1); }, 120);

    } else if (step.type === 'cmd') {
      var line = document.createElement('div');
      line.className = 's5-tline';
      line.innerHTML = '<span class="prompt">$ </span>';
      var cmdSpan = document.createElement('span');
      cmdSpan.className = 'cmd';
      line.appendChild(cmdSpan);
      body.appendChild(line);
      addCursor(line);
      scroll();
      typeText(cmdSpan, step.text, CMD_CHAR_MS, function() {
        setTimeout(function() { removeCursor(); run(idx + 1); }, PAUSE_AFTER_CMD);
      });

    } else if (step.type === 'ai') {
      var span = makeLine('ai');
      addCursor(span.parentNode);
      typeText(span, step.text, AI_CHAR_MS, function() {

        setTimeout(function() { run(idx + 1); }, PAUSE_AFTER_STEP);
      });

    } else if (step.type === 'ok') {
      var span = makeLine('success');
      addCursor(span.parentNode);
      typeText(span, step.text, OK_CHAR_MS, function() {
        if (step.trigger) fireTrigger(step.trigger);
        setTimeout(function() { run(idx + 1); }, PAUSE_AFTER_STEP);
      });

    } else if (step.type === 'warn') {
      var span = makeLine('warn');
      addCursor(span.parentNode);
      typeText(span, step.text, AI_CHAR_MS, function() {
        removeCursor();
        if (step.trigger) fireTrigger(step.trigger);
        setTimeout(function() { run(idx + 1); }, PAUSE_AFTER_STEP);
      });

    } else if (step.type === 'lines') {
      playLines(step.items, 0, function() {
        if (step.trigger) fireTrigger(step.trigger);
        setTimeout(function() { run(idx + 1); }, PAUSE_AFTER_STEP);
      });
    }
  }

  var revObs = new IntersectionObserver(function(entries) {
    entries.forEach(function(e) {
      if (e.isIntersecting) e.target.classList.add('visible');
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('#s5 .s5-reveal').forEach(function(el) { revObs.observe(el); });
})();