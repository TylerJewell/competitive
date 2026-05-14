const custWrapper = document.getElementById('cust-wrapper');
const slides  = document.querySelectorAll('.cust-slide');
const dotsEl  = document.getElementById('custDots');
const counter = document.getElementById('custCurrent');
const N       = slides.length;

// Build dots
for (let i = 0; i < N; i++) {
  const d = document.createElement('div');
  d.className = 'cust-dot';
  dotsEl.appendChild(d);
}
const dots = dotsEl.querySelectorAll('.cust-dot');

function updateSlides() {
  const y       = window.scrollY;
  const wTop    = custWrapper.offsetTop;
  const wScroll = custWrapper.offsetHeight - window.innerHeight;
  const p       = wScroll > 0 ? Math.max(0, Math.min((y - wTop) / wScroll, 1)) : 0;

  // Map progress 0–1 to slide index 0–(N-1)
  const idx = Math.min(Math.floor(p * N), N - 1);

  slides.forEach((s, i) => s.classList.toggle('active', i === idx));
  dots.forEach((d, i) => d.classList.toggle('active', i === idx));
  counter.textContent = String(idx + 1).padStart(2, '0');
}

window.addEventListener('scroll', updateSlides, { passive: true });
updateSlides();