/* ============================================================
   MediSmart AI — Cart Logic (localStorage-based)
   Shared across all pages via base.html
   ============================================================ */

const CART_KEY = 'medismart_cart';

// ── Read / Write ──────────────────────────────────────────────
function getCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch { return []; }
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  updateNavCartCount();
}

// ── Core operations ───────────────────────────────────────────
function addToCart(id, name, price, image) {
  const cart = getCart();
  const idx  = cart.findIndex(i => i.id === id);
  if (idx > -1) {
    cart[idx].qty += 1;
  } else {
    cart.push({ id, name, price, image, qty: 1 });
  }
  saveCart(cart);
  showToast('✅ ' + name + ' added to cart!', 'success');
  markCartBtn(id, true);
}

function removeFromCart(id) {
  const cart = getCart().filter(i => i.id !== id);
  saveCart(cart);
  markCartBtn(id, false);
}

function updateQty(id, qty) {
  const cart = getCart();
  const idx  = cart.findIndex(i => i.id === id);
  if (idx === -1) return;
  if (qty < 1) { removeFromCart(id); return; }
  if (qty > 20) qty = 20;
  cart[idx].qty = qty;
  saveCart(cart);
}

function clearCart() {
  localStorage.removeItem(CART_KEY);
  updateNavCartCount();
}

function getCartCount() {
  return getCart().reduce((sum, i) => sum + i.qty, 0);
}

function getCartTotal() {
  return getCart().reduce((sum, i) => sum + i.price * i.qty, 0);
}

// ── Navbar badge ──────────────────────────────────────────────
function updateNavCartCount() {
  const badge = document.getElementById('navCartCount');
  if (!badge) return;
  const count = getCartCount();
  if (count > 0) {
    badge.textContent = count > 99 ? '99+' : count;
    badge.classList.remove('hidden');
  } else {
    badge.classList.add('hidden');
  }
  // Mark any "Add to Cart" buttons for items already in cart
  const cart = getCart();
  cart.forEach(item => markCartBtn(item.id, true));
}

function markCartBtn(id, inCart) {
  const btn = document.getElementById('cartBtn-' + id);
  if (!btn) return;
  if (inCart) {
    btn.innerHTML = '✅ Added';
    btn.classList.add('in-cart');
  } else {
    btn.innerHTML = '🛒 Add to Cart';
    btn.classList.remove('in-cart');
  }
}

// ── Toast notification ────────────────────────────────────────
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
    <span>${message}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all .3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ── Init on every page load ───────────────────────────────────
document.addEventListener('DOMContentLoaded', updateNavCartCount);
