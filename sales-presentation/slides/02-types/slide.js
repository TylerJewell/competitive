/* ── Type data ─────────────────────────────────────── */
/* Ordered: 0-3 = top row (col 0-3), 4-7 = bottom row (col 0-3) */
// si = simple-icons slug (https://simpleicons.org) — blank = CSS text fallback
const TYPES = [
  { n:'01', name:'transact & reason', desc:'Process operational data',
    context:'Every payment, order, and decision — at sub-millisecond speed with zero data loss.',
    imgs:['capitalone','ING','westpac','bookingdotcom','gebit'] },
  { n:'02', name:'analytics', desc:'Analyze real-time data',
    context:'AI-powered analytics acting on data as it arrives — decisions before the moment passes.',
    imgs:['verizon','swiggy','dream11','HPE','usaacredit'] },
  { n:'03', name:'memory', desc:'Track & replay shared state',
    context:'Durable sub-10ms memory that survives failures and enables time-travel debugging.',
    imgs:['adobe','verizon','dream11'] },
  { n:'04', name:'digital twins', desc:'Converge replicated data',
    context:'Live replicas of physical systems — vehicles, factories, ports — in real time.',
    imgs:['vw','norwegian','bsh'] },
  { n:'05', name:'streaming', desc:'Process continuous data',
    context:'Millions of events per second with exactly-once delivery at global scale.',
    imgs:['disney','tubi','sky','webex','reflek'] },
  { n:'06', name:'workflows', desc:'Orchestrate long-term processes',
    context:'Business processes spanning days, surviving restarts, never losing state.',
    imgs:['walmart','tesco','workday','bp'] },
  { n:'07', name:'edge relays', desc:'Daisy chain device-to-cloud',
    context:'Reliable coordination across thousands of distributed devices — zero message loss.',
    imgs:['vw','johndeere','gm','tesla','bsh'] },
  { n:'08', name:'model inference', desc:'Agent & tool execution',
    context:'Autonomous agents making real decisions in production — not demos, not prototypes.',
    imgs:['ciena','amprion','lloyds','RBC','tubi'] },
];

/* ── Build grid ────────────────────────────────────── */
const stGrid   = document.getElementById('stGrid');
const stDotsEl = document.getElementById('stDots');


TYPES.forEach((t, i) => {
  const col = i % 4;
  const row = i < 4 ? 0 : 1;

  const card = document.createElement('div');
  card.className = 'st-card';
  card.dataset.col = col;
  card.dataset.row = row;

  const pills = t.imgs.map(name =>
    `<img class="logo-tile-img" src="logos/${name}.png" alt="${name}" loading="lazy">`
  ).join('');

  card.innerHTML = `
    <div class="st-card-content">
      <div class="st-num">${t.n}</div>
      <div class="st-name">${t.name}</div>
      <div class="st-desc">${t.desc}</div>
      <div class="st-context">${t.context}</div>
      <div class="st-divider"></div>
      <div class="st-logos">${pills}</div>
    </div>
  `;
  stGrid.appendChild(card);
});

/* 4 progress dots */
for (let i = 0; i < 4; i++) {
  const d = document.createElement('div');
  d.className = 'st-dot';
  stDotsEl.appendChild(d);
}

/* ── Column reveal — time-based, one-shot ──── */
const stWrapper = document.getElementById('st-wrapper');
const cards   = document.querySelectorAll('.st-card');
const stDots  = document.querySelectorAll('.st-dot');

let stTriggered = false;

function triggerStCols() {
  if (stTriggered) return;
  stTriggered = true;
  for (let col = 0; col < 4; col++) {
    setTimeout(() => {
      cards.forEach(card => {
        if (+card.dataset.col === col) card.classList.add('visible');
      });
      if (stDots[col]) stDots[col].classList.add('lit');
    }, col * 1000);
  }
}

new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) triggerStCols();
}, { threshold: 0 }).observe(document.getElementById('st-sticky'));