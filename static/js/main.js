/**
 * Mohammed Eidab For Plastic Products — Core Application Script
 * Optimized for mobile performance, accessibility, and dynamic state management.
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbarScroll();
  initCartBadge();
  initIntersectionObservers();
  initAlertDismissal();
  initAdminSidebar();
  initSmoothScroll();
});

// ── NOTE on the public mobile menu ──
// There used to be an initMobileMenu() here targeting `.nav-hamburger` /
// `.mobile-menu`. Those classes don't exist in base.html — the real markup
// uses `.eidab-hamburger` / `.eidab-mobile-menu`, and base.html already has
// its own working toggleMobileMenu() inline <script> wired via onclick.
// That function was always a silent no-op (querySelector returned null,
// so it returned early every time). Removed it so nobody "fixes" the
// selectors later and accidentally double-toggles the menu (one click
// would open it via the inline script AND close it again via this one,
// cancelling out). The public hamburger lives entirely in base.html now.

// ── Navbar Scroll Effects (Performance Throttled) ──
function initNavbarScroll() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        navbar.classList.toggle('scrolled', window.scrollY > 40);
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

// ── Dynamic Asynchronous Cart Lifecycle ──
function updateCartBadge() {
  // FIX BUG-9: this was querying `.cart-badge`, but base.html's actual
  // markup uses `.eidab-cart-badge`. Since `.cart-badge` never matched
  // anything, this function returned early on every page load and the
  // badge was permanently stuck at its hardcoded "0" from the HTML,
  // no matter how many items were really in the cart.
  const badge = document.querySelector('.eidab-cart-badge');
  if (!badge) return;

  fetch('/cart/count')
    .then(response => {
      if (!response.ok) throw new Error('Network status mismatch');
      return response.json();
    })
    .then(data => {
      if (typeof data.count !== 'undefined') {
        badge.textContent = data.count;
        badge.classList.toggle('show', data.count > 0);
      }
    })
    .catch(err => console.warn('Cart count tracking sync paused:', err));
}

function initCartBadge() {
  updateCartBadge();
}

// ── Element Intersections & Numerical Counter Tweens ──
function initIntersectionObservers() {
  // Reveal animations on entry
  const generalObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        generalObserver.unobserve(entry.target); // Optimize processing overhead
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.animate-on-scroll').forEach(el => generalObserver.observe(el));

  // Running total statistics counters
  const counterObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.counted) {
        entry.target.dataset.counted = 'true';
        animateCounter(entry.target);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.counter').forEach(counter => counterObserver.observe(counter));
}

function animateCounter(el) {
  const target = parseInt(el.dataset.target, 10) || 0;
  const duration = 1800;
  const startTime = performance.now();

  const step = (now) => {
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Cubic easing out curve transformation
    const easeOutCubic = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(easeOutCubic * target).toLocaleString();

    if (progress < 1) {
      requestAnimationFrame(step);
    }
  };
  requestAnimationFrame(step);
}

// ── Global Quantity Adjustments (Supports Detail View & Cart Summary) ──
function changeQty(identifier, delta) {
  // Resolves target field directly or attempts item prefix strings
  const input = document.getElementById(identifier) || document.getElementById('qty-' + identifier);
  if (!input) return;

  const currentVal = parseInt(input.value, 10) || 1;
  const minLimit = parseInt(input.min, 10) || 1;
  const maxLimit = parseInt(input.max, 10) || 999;

  const cleanVal = Math.max(minLimit, Math.min(maxLimit, currentVal + delta));
  input.value = cleanVal;

  // Emits change events to let server synchronization hooks auto-fire
  input.dispatchEvent(new Event('change', { bubbles: true }));
}

// ── Flash System Notification Management ──
function initAlertDismissal() {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-8px)';
      alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });
}

// ── Admin Panel Context Toggles ──
function initAdminSidebar() {
  const adminToggle = document.querySelector('.admin-mobile-toggle');
  const adminSidebar = document.querySelector('.admin-sidebar');
  if (!adminToggle || !adminSidebar) return;

  adminToggle.addEventListener('click', () => {
    const isExpanded = adminSidebar.classList.toggle('open');
    adminToggle.setAttribute('aria-expanded', isExpanded);
  });
}

// ── Presentation Mapping Constants ──
const CATEGORY_EMOJIS = {
  'Plastic Chairs': '🪑',
  'Plastic Tables': '🪵',
  'Plastic Buckets': '🪣',
  'Plastic Containers': '📦',
  'Storage Products': '🗄️',
  'Household Products': '🏠',
  'Industrial Products': '🏭',
};

function getCategoryEmoji(category) {
  return CATEGORY_EMOJIS[category] || '📦';
}

// ── Hardware Accelerated Structural Internal Anchor Traversal ──
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const hash = this.getAttribute('href');
      if (hash === '#') return;

      const targetElement = document.querySelector(hash);
      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}