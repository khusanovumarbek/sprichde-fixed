/* ============================================================
 * SprichDe — Yorug'/Tungi rejim (light / dark theme)
 * Barcha sahifalarda bir xil ishlaydi va tanlov eslab qolinadi.
 * Foydalanish: sahifa <head> ichida (CSS'dan OLDIN) chaqiriladi:
 *   <script src="theme.js"></script>
 *   <script>SolTheme.apply();</script>
 * ============================================================ */
(function () {
  const KEY = 'sprichdeTheme';
  const LIGHT = 'light';
  const DARK = 'dark';

  // Brauzer/telefon manzil qatorining rangi (PWA'da ham ishlatiladi)
  const THEME_COLORS = { light: '#f7f8fc', dark: '#0f1b33' };

  function current() {
    try { return localStorage.getItem(KEY) || LIGHT; } catch { return LIGHT; }
  }

  // <meta name="theme-color"> ni tanlangan rejimga moslaymiz
  function syncThemeColor(mode) {
    try {
      let meta = document.querySelector('meta[name="theme-color"]');
      if (!meta) {
        meta = document.createElement('meta');
        meta.setAttribute('name', 'theme-color');
        document.head.appendChild(meta);
      }
      meta.setAttribute('content', THEME_COLORS[mode] || THEME_COLORS.light);
    } catch {}
  }

  function apply() {
    const mode = current();
    document.documentElement.setAttribute('data-theme', mode);
    syncThemeColor(mode);
    // Mana shu joyda tanlovni localStorage'da saqlaymiz
    return mode;
  }

  function set(mode) {
    try { localStorage.setItem(KEY, mode); } catch {}
    document.documentElement.setAttribute('data-theme', mode);
    syncThemeColor(mode);
  }

  function toggle() {
    const next = current() === DARK ? LIGHT : DARK;
    set(next);
    return next;
  }

  // Sahifa ochilganda darhol qo'llaymiz (miltillashning oldini olish uchun
  // HTML'ga class qo'yiladi; CSS ham shu atributga tayanadi)
  apply();

  window.SolTheme = { apply, set, toggle, current, KEY };
})();
