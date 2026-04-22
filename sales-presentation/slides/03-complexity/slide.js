/* ── Section 3 ──────────────────────── */
const s2wrapper = document.getElementById('s2-wrapper');
const tcoEl = document.querySelector('.s2-tco');
const s2diagram = document.querySelector('.s2-diagram');
let diagramDrawing = false;

/* Eyebrow, headline, and blocks fade in via IntersectionObserver as section scrolls up */
const s2RevealObs = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('[data-s2="0"], [data-s2="1"]:not(.s2-diagram), .s2-tco').forEach(el => s2RevealObs.observe(el));

/* Diagram starts drawing only when sticky section is anchored (fully in view) */
const s2DiagramObs = new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) {
    s2diagram.classList.add('visible');
    diagramDrawing = true;
  }
}, { threshold: 0.8 });
s2DiagramObs.observe(document.getElementById('s2-sticky'));