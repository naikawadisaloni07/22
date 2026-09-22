/* ============================================================
   MediSmart AI — Image fallback handler
   Fires on every img onerror to show a styled placeholder
   ============================================================ */
(function() {
  const COLORS = {
    "Pain Relief":    ["#e8f5e9","#2e7d32"],
    "Antibiotics":    ["#e3f2fd","#1565c0"],
    "Allergy":        ["#fff3e0","#e65100"],
    "Diabetes":       ["#fce4ec","#880e4f"],
    "Gastric":        ["#f3e5f5","#6a1b9a"],
    "Cardiac":        ["#e8eaf6","#283593"],
    "Vitamins":       ["#fffde7","#f57f17"],
    "Respiratory":    ["#e0f7fa","#006064"],
    "Skin Care":      ["#fdf2f8","#c026d3"],
    "Mental Health":  ["#f0fdf4","#16a34a"],
    "Thyroid":        ["#fff7ed","#ea580c"],
    "Women's Health": ["#fdf4ff","#a855f7"],
    "Eye Care":       ["#ecfeff","#06b6d4"],
    "Neurological":   ["#f0f4ff","#6366f1"],
    "Oral Care":      ["#f0fdf4","#22c55e"],
    "First Aid":      ["#fff1f2","#f43f5e"],
  };

  function svgPlaceholder(name, category) {
    const colors  = COLORS[category] || ["#f4f7f9","#0a6e6e"];
    const bg      = colors[0];
    const fg      = colors[1];
    const short   = name.split(' ').slice(0,2).join(' ');
    const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>
      <rect width='300' height='300' fill='${bg}'/>
      <circle cx='150' cy='105' r='55' fill='${fg}' opacity='0.15'/>
      <text x='150' y='100' font-family='Arial,sans-serif' font-size='48'
            text-anchor='middle' dominant-baseline='middle' fill='${fg}'>💊</text>
      <text x='150' y='175' font-family='Arial,sans-serif' font-size='16'
            font-weight='bold' text-anchor='middle' fill='${fg}'>${short}</text>
      <text x='150' y='198' font-family='Arial,sans-serif' font-size='12'
            text-anchor='middle' fill='${fg}' opacity='0.7'>${category}</text>
    </svg>`;
    return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
  }

  window.handleImgError = function(img) {
    const name     = img.getAttribute('data-name')     || img.alt || 'Medicine';
    const category = img.getAttribute('data-category') || 'Medicine';
    img.src = svgPlaceholder(name, category);
    img.onerror = null; // prevent infinite loop
  };

  // Apply to all medicine images on load
  document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('img.med-img, img.med-card-img, img.detail-img-main, img.rec-img, img.cart-item-img').forEach(function(img) {
      img.onerror = function() { window.handleImgError(this); };
      // Trigger check for already-broken images
      if (img.complete && img.naturalWidth === 0) {
        window.handleImgError(img);
      }
    });
  });
})();
