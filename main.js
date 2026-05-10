
// NEYO FARMS — MAIN JS

// Nav scroll effect
const nav = document.getElementById('mainNav');
if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 50);
  });
}

// Mobile burger
const burger = document.getElementById('navBurger');
const links = document.getElementById('navLinks');
if (burger && links) {
  burger.addEventListener('click', () => {
    links.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!nav.contains(e.target)) links.classList.remove('open');
  });
}

// Scroll reveal
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.service-card, .product-card, .blog-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(30px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});

// Shop category filter
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const cat = btn.dataset.cat;
    window.location.href = cat ? `/shop?category=${cat}` : '/shop';
  });
});

// Auto-dismiss flashes
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(f => {
    f.style.opacity = '0';
    f.style.transition = 'opacity 0.5s';
    setTimeout(() => f.remove(), 500);
  });
}, 5000);

// Counter animation
function animateCounter(el) {
  const target = parseInt(el.dataset.target);
  const duration = 1500;
  const step = target / (duration / 16);
  let current = 0;
  const timer = setInterval(() => {
    current += step;
    if (current >= target) { current = target; clearInterval(timer); }
    el.textContent = Math.floor(current).toLocaleString() + (el.dataset.suffix || '');
  }, 16);
}
document.querySelectorAll('[data-target]').forEach(el => {
  const obs = new IntersectionObserver(([e]) => {
    if (e.isIntersecting) { animateCounter(el); obs.disconnect(); }
  });
  obs.observe(el);
});
