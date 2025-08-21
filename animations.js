// app.js - robust, triggers when in view, interactive stats
(function () {
  'use strict';

  // helper: create ripple effect
  function createRipple(event, element) {
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    const ripple = document.createElement('div');
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: radial-gradient(circle, rgba(255,156,201,0.6) 0%, transparent 70%);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s ease-out;
      pointer-events: none;
      z-index: 1000;
    `;
    
    element.style.position = 'relative';
    element.appendChild(ripple);
    
    setTimeout(() => {
      if (ripple.parentNode) ripple.parentNode.removeChild(ripple);
    }, 600);
  }

  // helper: animate numeric count
  function animateCounter(el, target, suffix = '', duration = 1300) {
    const start = performance.now();
    const starting = 0;
    function step(now) {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic
      const value = target * eased;
      // display integer unless suffix is 'x' => show one decimal
      const text = (suffix === 'x') ? (Math.round(value * 10) / 10).toFixed(1) + suffix
                                    : Math.round(value) + suffix;
      el.textContent = text;
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  // Start when DOM ready
  document.addEventListener('DOMContentLoaded', function () {
    const statsCard = document.getElementById('statsCard');
    const countEls = Array.from(document.querySelectorAll('.count'));
    const statEls = Array.from(document.querySelectorAll('.stat'));
    const dots = Array.from(document.querySelectorAll('.stats-indicator .dot'));

    // click a stat to set active with enhanced effects
    statEls.forEach((s, i) => {
      s.addEventListener('click', (e) => {
        // Remove active from all stats
        statEls.forEach(x => x.classList.remove('active'));
        dots.forEach(d => d.classList.remove('active'));
        
        // Add active to clicked stat
        s.classList.add('active');
        if (dots[i]) dots[i].classList.add('active');
        
        // Add ripple effect
        createRipple(e, s);
        
        // Shake animation for impact
        s.style.animation = 'statClick 0.6s ease';
        setTimeout(() => s.style.animation = '', 600);
      });
      
      // Add double-click for extra effect
      s.addEventListener('dblclick', () => {
        s.style.animation = 'statBounce 0.8s ease';
        setTimeout(() => s.style.animation = '', 800);
      });
    });

    // IntersectionObserver to trigger count animations once
    let didAnimate = false;
    if ('IntersectionObserver' in window && statsCard) {
      const obs = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && !didAnimate) {
            didAnimate = true;
            // animate each counter
            countEls.forEach(el => {
              const t = parseFloat(el.getAttribute('data-target')) || 0;
              const suffix = el.getAttribute('data-suffix') || '';
              animateCounter(el, t, suffix, 1200);
            });
            obs.disconnect();
          }
        });
      }, { threshold: 0.3 });
      obs.observe(statsCard);
    } else {
      // fallback: animate immediately
      countEls.forEach(el => {
        const t = parseFloat(el.getAttribute('data-target')) || 0;
        const suffix = el.getAttribute('data-suffix') || '';
        animateCounter(el, t, suffix, 1200);
      });
    }

    // Nice scroll fade-in for features & stats using IntersectionObserver
    const animTargets = document.querySelectorAll('.stats-card, .feature, .hero-title, .hero-sub, .cta-button');
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.forEach(e => {
          if (e.isIntersecting) {
            e.target.classList.add('in-view');
            io.unobserve(e.target);
          }
        });
      }, { threshold: 0.15 });

      animTargets.forEach(t => io.observe(t));
    } else {
      animTargets.forEach(t => t.classList.add('in-view'));
    }

    // small safety: if user opens file locally and scripts didn't run previously,
    // ensure counts show target values (prevents stuck zero)
    window.addEventListener('load', () => {
      // if animation never ran after 2s, fill values
      setTimeout(() => {
        if (!didAnimate) {
          countEls.forEach(el => {
            const t = el.getAttribute('data-target') || '0';
            const suffix = el.getAttribute('data-suffix') || '';
            el.textContent = suffix === 'x' ? parseFloat(t).toFixed(1) + suffix : t + suffix;
          });
        }
      }, 2000);
    });

    // Add interactive features to other elements
    const featureEls = document.querySelectorAll('.feature');
    const ctaButton = document.getElementById('startBtn');
    const logo = document.querySelector('.logo-bubble');

    // Add click effects to features
    featureEls.forEach((feature, index) => {
      feature.addEventListener('click', (e) => {
        createRipple(e, feature);
        feature.style.animation = `statBounce 0.8s ease`;
        setTimeout(() => feature.style.animation = '', 800);
      });
    });

    // Add enhanced CTA button interaction
    if (ctaButton) {
      ctaButton.addEventListener('click', (e) => {
        createRipple(e, ctaButton);
        ctaButton.style.animation = 'statBounce 1s ease';
        setTimeout(() => ctaButton.style.animation = '', 1000);
        
        // Simulate action feedback
        const originalText = ctaButton.querySelector('.cta-title').textContent;
        ctaButton.querySelector('.cta-title').textContent = 'Loading...';
        setTimeout(() => {
          ctaButton.querySelector('.cta-title').textContent = '✓ Started!';
          setTimeout(() => {
            ctaButton.querySelector('.cta-title').textContent = originalText;
          }, 2000);
        }, 1000);
      });
    }

    // Add logo interaction
    if (logo) {
      logo.addEventListener('click', () => {
        logo.style.animation = 'statBounce 0.8s ease';
        setTimeout(() => logo.style.animation = '', 800);
      });
    }

    // Add keyboard navigation support
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        const focusedEl = document.activeElement;
        if (focusedEl.classList.contains('stat') || 
            focusedEl.classList.contains('feature') || 
            focusedEl.classList.contains('cta-button')) {
          e.preventDefault();
          focusedEl.click();
        }
      }
    });

    // Automatic cycling through stats on page load
    let currentStatIndex = 0;
    const totalStats = statEls.length;
    
    function cycleToNextStat() {
      // Remove active from all stats and dots
      statEls.forEach(s => s.classList.remove('active'));
      dots.forEach(d => d.classList.remove('active'));
      
      // Add active to current stat and dot
      if (statEls[currentStatIndex]) {
        statEls[currentStatIndex].classList.add('active');
      }
      if (dots[currentStatIndex]) {
        dots[currentStatIndex].classList.add('active');
      }
      
      // Move to next stat
      currentStatIndex = (currentStatIndex + 1) % totalStats;
    }
    
    // Start automatic cycling after page loads
    setTimeout(() => {
      // Initial activation
      cycleToNextStat();
      
      // Continue cycling every 2.5 seconds
      setInterval(cycleToNextStat, 2500);
    }, 1000); // Wait 1 second after page load before starting

    // Add mouse trail effect (subtle)
    let mouseTrail = [];
    document.addEventListener('mousemove', (e) => {
      if (mouseTrail.length > 5) mouseTrail.shift();
      
      mouseTrail.push({
        x: e.clientX,
        y: e.clientY,
        time: Date.now()
      });
      
      // Clean up old trail points
      mouseTrail = mouseTrail.filter(point => Date.now() - point.time < 500);
    });

  }); // DOMContentLoaded
})();
