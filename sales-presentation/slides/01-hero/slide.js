/* ── Hero counters ─────────────────────────────────── */
function animateCount(el, target) {
  const dur = 1600, t0 = performance.now();
  (function tick(now) {
    const p = Math.min((now - t0) / dur, 1);
    el.textContent = Math.floor((1 - Math.pow(1 - p, 3)) * target);
    if (p < 1) requestAnimationFrame(tick); else el.textContent = target;
  })(t0);
}
new IntersectionObserver(entries => {
  if (entries[0].isIntersecting)
    document.querySelectorAll('.stat-num').forEach(el => animateCount(el, +el.dataset.target));
}, { threshold: 0.6 }).observe(document.querySelector('.hero-stats'));