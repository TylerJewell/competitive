const closingObserver = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('#closing .closing-reveal').forEach(el => closingObserver.observe(el));

/* ── view-jump navigation (ArrowRight / ArrowLeft) ── */
(function() {