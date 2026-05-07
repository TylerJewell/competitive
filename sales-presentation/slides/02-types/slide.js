/* ── Type data ─────────────────────────────────────── */
// si = simple-icons slug (https://simpleicons.org) — blank = CSS text fallback
const TYPE_SOURCE = [
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

/* Ordered by visual reveal: top/bottom within each column, then next column. */
const TYPES = [0, 4, 1, 5, 2, 6, 3, 7].map((sourceIndex, i) => ({
  ...TYPE_SOURCE[sourceIndex],
  n: String(i + 1).padStart(2, '0')
}));

/* ── Build grid ────────────────────────────────────── */
const stGrid   = document.getElementById('stGrid');
const stDotsEl = document.getElementById('stDots');


TYPES.forEach((t, i) => {
  const col = Math.floor(i / 2);
  const row = i % 2;

  const card = document.createElement('div');
  card.className = 'st-card';
  card.dataset.col = col;
  card.dataset.row = row;
  card.style.gridColumn = String(col + 1);
  card.style.gridRow = String(row + 1);

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

/* 8 progress dots, one per proof box */
for (let i = 0; i < TYPES.length; i++) {
  const d = document.createElement('div');
  d.className = 'st-dot';
  stDotsEl.appendChild(d);
}

/* ── Column reveal — time-based, one-shot ──── */
const stWrapper = document.getElementById('st-wrapper');
const cards   = document.querySelectorAll('.st-card');
const stDots  = document.querySelectorAll('.st-dot');

let stTriggered = false;

function triggerStBoxes() {
  if (stTriggered) return;
  stTriggered = true;
  cards.forEach((card, i) => {
    setTimeout(() => {
      card.classList.add('visible');
      if (stDots[i]) stDots[i].classList.add('lit');
    }, i * 500);
  });
}

new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) triggerStBoxes();
}, { threshold: 0 }).observe(document.getElementById('st-sticky'));
