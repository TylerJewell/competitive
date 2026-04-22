/* ── Phase 1: scroll-driven problem reveals ── */
const s7wrapper = document.getElementById('s7-problem');
const s7els     = document.querySelectorAll('[data-s7]');

function updateS7() {
  const y       = window.scrollY;
  const wTop    = s7wrapper.offsetTop;
  const wScroll = s7wrapper.offsetHeight - window.innerHeight;
  const scrolled = y - wTop;
  const p = wScroll > 0 ? Math.min(scrolled / wScroll, 1) : 0;

  s7els.forEach(el => {
    const step = +el.dataset.s7;
    const threshold = Math.max(0, (step - 1) / 5);
    el.classList.toggle('visible', p >= threshold);
  });
}
window.addEventListener('scroll', updateS7, { passive: true });
updateS7();

/* ── Phase 2: IntersectionObserver reveals ── */
const s7observer = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('#s7-answer .s7-reveal').forEach(el => s7observer.observe(el));

/* ── Carousel ── */
let s7idx = 0;
const s7track = document.getElementById('s7Track');
const s7slides = s7track ? s7track.children : [];
const s7dotsEl = document.getElementById('s7Dots');

function s7BuildDots() {
  if (!s7dotsEl) return;
  for (let i = 0; i < s7slides.length; i++) {
    const d = document.createElement('button');
    d.className = 's7-carousel-dot' + (i === 0 ? ' active' : '');
    d.onclick = () => s7GoTo(i);
    s7dotsEl.appendChild(d);
  }
}
function s7GoTo(i) {
  s7idx = Math.max(0, Math.min(i, s7slides.length - 1));
  if (s7track) s7track.style.transform = `translateX(-${s7idx * 100}%)`;
  s7dotsEl.querySelectorAll('.s7-carousel-dot').forEach((d, j) => d.classList.toggle('active', j === s7idx));
}
function s7Next() { s7GoTo(s7idx + 1); }
function s7Prev() { s7GoTo(s7idx - 1); }
s7BuildDots();