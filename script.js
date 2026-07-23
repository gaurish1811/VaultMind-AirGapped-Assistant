/* ============================================================
   VaultMind — JavaScript: Particles, Scroll FX, Terminal, Nav
   ============================================================ */

// ===== PARTICLE CANVAS =====
(function initParticles() {
  const canvas = document.getElementById('particle-canvas');
  const ctx = canvas.getContext('2d');
  let width, height, particles = [];
  const PARTICLE_COUNT = 80;
  const COLORS = ['rgba(0,229,255,', 'rgba(124,58,237,', 'rgba(59,130,246,'];

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  function createParticle() {
    return {
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 1.5 + 0.3,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      alpha: Math.random() * 0.4 + 0.1,
      pulse: Math.random() * Math.PI * 2,
    };
  }

  function initParticleArray() {
    particles = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) particles.push(createParticle());
  }

  function drawConnections() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          const alpha = (1 - dist / 120) * 0.08;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0,229,255,${alpha})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  let frame = 0;
  function animate() {
    ctx.clearRect(0, 0, width, height);
    frame++;
    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;
      p.pulse += 0.01;
      const alpha = p.alpha + Math.sin(p.pulse) * 0.05;

      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `${p.color}${Math.max(0, alpha)})`;
      ctx.fill();
    });
    drawConnections();
    requestAnimationFrame(animate);
  }

  window.addEventListener('resize', () => { resize(); });
  resize();
  initParticleArray();
  animate();
})();

// ===== NAVBAR SCROLL =====
(function initNavbar() {
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }, { passive: true });
})();

// ===== HAMBURGER MENU =====
(function initHamburger() {
  const btn = document.getElementById('hamburger');
  const menu = document.getElementById('mobile-menu');
  if (!btn || !menu) return;

  btn.addEventListener('click', () => {
    menu.classList.toggle('open');
  });

  // Close on link click
  menu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => menu.classList.remove('open'));
  });
})();

// ===== SMOOTH SCROLL FOR NAV LINKS =====
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ===== INTERSECTION OBSERVER (reveal on scroll) =====
(function initReveal() {
  const elements = document.querySelectorAll(
    '.feature-card, .how-step, .tech-card, .industry-card, .arch-node, .code-block, .trust-tag'
  );

  const delays = [0, 0.1, 0.2, 0.3, 0.4];

  elements.forEach((el, i) => {
    el.classList.add('reveal');
    const siblings = el.parentElement ? [...el.parentElement.children].indexOf(el) : 0;
    el.style.transitionDelay = `${delays[Math.min(siblings, delays.length - 1)]}s`;
  });

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  elements.forEach(el => observer.observe(el));
})();

// ===== TERMINAL TYPING ANIMATION =====
(function initTerminal() {
  const terminal = document.getElementById('t-typing');
  if (!terminal) return;

  const messages = [
    { text: 'Processing 47 emails locally', color: 'var(--teal)' },
    { text: '✓ Summary generated — 1.2s, 0 bytes sent', color: '#00e5a0' },
    { text: 'Drafting reply to J. Sullivan...', color: 'var(--teal)' },
    { text: '✓ Ready. All data remains on-device.', color: '#00e5a0' },
    { text: 'Searching financial Q3 report...', color: 'var(--teal)' },
    { text: '✓ 3 relevant docs retrieved from Milvus', color: '#00e5a0' },
  ];

  let msgIndex = 0;

  function typeMessage(msg) {
    const span = terminal.querySelector('span');
    const cursor = terminal.querySelector('.cursor-blink');
    span.style.color = msg.color;
    let text = '';
    let charIndex = 0;
    const interval = setInterval(() => {
      text += msg.text[charIndex];
      span.textContent = text;
      charIndex++;
      if (charIndex >= msg.text.length) {
        clearInterval(interval);
        setTimeout(() => {
          msgIndex = (msgIndex + 1) % messages.length;
          span.textContent = '';
          typeMessage(messages[msgIndex]);
        }, 2800);
      }
    }, 45);
  }

  setTimeout(() => typeMessage(messages[0]), 3000);
})();

// ===== ARCHITECTURE DIAGRAM HOVER ANIMATIONS =====
(function initArchHover() {
  const nodes = document.querySelectorAll('.arch-node');
  nodes.forEach(node => {
    node.addEventListener('mouseenter', () => {
      const arrows = node.parentElement.querySelectorAll('.arch-arrow-line');
      arrows.forEach(a => {
        a.style.background = 'linear-gradient(180deg, #00e5ff, rgba(0,229,255,0.3))';
      });
    });
    node.addEventListener('mouseleave', () => {
      const arrows = node.parentElement.querySelectorAll('.arch-arrow-line');
      arrows.forEach(a => {
        a.style.background = '';
      });
    });
  });
})();

// ===== FEATURE CARD GLOW ON HOVER =====
(function initCardGlow() {
  document.querySelectorAll('.feature-card, .tech-card, .industry-card').forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      card.style.setProperty('--mouse-x', `${x}%`);
      card.style.setProperty('--mouse-y', `${y}%`);
    });
  });
})();

// ===== CTA FORM SUBMIT =====
function handleFormSubmit(e) {
  e.preventDefault();
  const form = document.getElementById('cta-form');
  const success = document.getElementById('cta-success');
  const name = document.getElementById('form-name').value;
  if (form && success && name) {
    form.style.display = 'none';
    success.classList.add('visible');
  }
}

// ===== COUNTER ANIMATION =====
(function initCounters() {
  const stats = document.querySelectorAll('.stat-value');
  const targets = ['7B', '0', '∞'];

  function animateValue(el, target, duration) {
    if (isNaN(parseFloat(target))) return; // skip non-numeric like ∞ or 7B
    const start = 0;
    const end = parseFloat(target);
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(start + (end - start) * eased);
      if (progress < 1) requestAnimationFrame(update);
      else el.textContent = target;
    }

    requestAnimationFrame(update);
  }

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const original = el.textContent;
        animateValue(el, original, 1200);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.5 });

  stats.forEach(el => observer.observe(el));
})();

// ===== CURSOR TRAIL =====
(function initCursorTrail() {
  if (window.matchMedia('(hover: none)').matches) return;

  let mouseX = 0, mouseY = 0;
  const trail = document.createElement('div');
  trail.style.cssText = `
    position: fixed; pointer-events: none; z-index: 9999;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(0,229,255,0.04) 0%, transparent 70%);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: opacity 0.3s;
    left: 0; top: 0;
  `;
  document.body.appendChild(trail);

  document.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    trail.style.left = mouseX + 'px';
    trail.style.top = mouseY + 'px';
  });

  document.addEventListener('mouseleave', () => { trail.style.opacity = '0'; });
  document.addEventListener('mouseenter', () => { trail.style.opacity = '1'; });
})();

// ===== ACTIVE NAV LINK HIGHLIGHT =====
(function initActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        navLinks.forEach(link => {
          link.style.color = '';
          if (link.getAttribute('href') === '#' + entry.target.id) {
            link.style.color = 'var(--teal)';
          }
        });
      }
    });
  }, { rootMargin: '-40% 0px -40% 0px' });

  sections.forEach(section => observer.observe(section));
})();
