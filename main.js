/* ============================================================
   MediSmart AI — Global UI: Navbar, Search Autocomplete,
   Hamburger, Scroll effects
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Hamburger / Mobile nav ──────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const mobileNav = document.getElementById('mobileNav');

  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
      const open = mobileNav.classList.toggle('open');
      hamburger.setAttribute('aria-expanded', open);
      // Animate bars
      const spans = hamburger.querySelectorAll('span');
      if (open) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity   = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
      }
    });
    // Close on outside click
    document.addEventListener('click', e => {
      if (!hamburger.contains(e.target) && !mobileNav.contains(e.target)) {
        mobileNav.classList.remove('open');
        hamburger.querySelectorAll('span').forEach(s => {
          s.style.transform = ''; s.style.opacity = '';
        });
      }
    });
  }

  // ── Navbar scroll shadow ────────────────────────────────────
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.style.boxShadow = window.scrollY > 10
        ? '0 4px 20px rgba(0,0,0,.12)'
        : '0 2px 12px rgba(0,0,0,.08)';
    }, { passive: true });
  }

  // ── Search autocomplete ─────────────────────────────────────
  const searchInput    = document.getElementById('navSearchInput');
  const searchDropdown = document.getElementById('searchDropdown');

  if (searchInput && searchDropdown) {
    let debounceTimer;

    searchInput.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      const q = this.value.trim();
      if (q.length < 2) {
        searchDropdown.classList.remove('active');
        searchDropdown.innerHTML = '';
        return;
      }
      debounceTimer = setTimeout(() => fetchSuggestions(q), 250);
    });

    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') submitSearch();
      if (e.key === 'Escape') {
        searchDropdown.classList.remove('active');
        searchDropdown.innerHTML = '';
      }
    });

    // Close dropdown on outside click
    document.addEventListener('click', e => {
      if (!searchInput.closest('.nav-search').contains(e.target)) {
        searchDropdown.classList.remove('active');
        searchDropdown.innerHTML = '';
      }
    });
  }

  // ── Highlight active nav link ───────────────────────────────
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === path || (href !== '/' && path.startsWith(href))) {
      a.classList.add('active');
    }
  });

});

// ── Search API fetch ──────────────────────────────────────────
function fetchSuggestions(q) {
  const dropdown = document.getElementById('searchDropdown');
  if (!dropdown) return;

  fetch('/api/search?q=' + encodeURIComponent(q))
    .then(r => r.json())
    .then(data => {
      if (!data.length) {
        dropdown.classList.remove('active');
        return;
      }
      dropdown.innerHTML = data.map(m => `
        <div class="search-item" onclick="location.href='/medicine/${m.id}'">
          <div>
            <div class="name">${m.name}</div>
            <div class="brand">${m.brand} · ${m.category}</div>
          </div>
          <div class="price">₹${m.price}</div>
        </div>
      `).join('') + `
        <div class="search-item" style="justify-content:center;color:var(--primary);font-weight:600;"
             onclick="submitSearch()">
          🔍 See all results for "${q}"
        </div>
      `;
      dropdown.classList.add('active');
    })
    .catch(() => {
      dropdown.classList.remove('active');
    });
}

// ── Submit search (used by navbar + hero) ─────────────────────
function submitSearch() {
  const input = document.getElementById('navSearchInput')
             || document.getElementById('heroSearch');
  if (!input) return;
  const q = input.value.trim();
  if (q) window.location.href = '/medicines?search=' + encodeURIComponent(q);
}

// ── User dropdown menu ────────────────────────────────────────
function toggleUserMenu() {
  const dd = document.getElementById('userDropdown');
  if (dd) dd.classList.toggle('open');
}
document.addEventListener('click', function(e) {
  const wrap = document.querySelector('.user-menu-wrap');
  const dd   = document.getElementById('userDropdown');
  if (wrap && dd && !wrap.contains(e.target)) {
    dd.classList.remove('open');
  }
});
// Auto-dismiss flash messages after 4s
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(() => {
    const fw = document.getElementById('flashWrap');
    if (fw) { fw.style.opacity='0'; fw.style.transition='opacity .5s'; setTimeout(()=>fw.remove(),500); }
  }, 4000);
});
