/* ============================================================
 * SprichDe — PWA (telefonga o'rnatiladigan ilova) yordamchisi
 * Har bir sahifada <head> ichida ulanadi:
 *   <script src="pwa.js" defer></script>
 * Vazifasi:
 *   1) Service worker'ni ro'yxatdan o'tkazish (oflayn rejim)
 *   2) "Ilovani o'rnatish" tugmasi uchun hodisalarni ushlash
 * ============================================================ */
(function () {
  // ---------- 1. Service worker ----------
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('sw.js').catch(function () {
        /* HTTPS/localhost bo'lmasa jim o'tkazamiz */
      });
    });
  }

  // ---------- 2. O'rnatish (install) ----------
  var deferredPrompt = null;

  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault();
    deferredPrompt = e;
    document.dispatchEvent(new Event('pwa:installable'));
  });

  window.addEventListener('appinstalled', function () {
    deferredPrompt = null;
    document.dispatchEvent(new Event('pwa:installed'));
  });

  function isStandalone() {
    return (
      window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true
    );
  }

  function isIOS() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent);
  }

  window.SprichdePWA = {
    canInstall: function () { return !!deferredPrompt; },
    isStandalone: isStandalone,
    isIOS: isIOS,
    install: function () {
      if (!deferredPrompt) return Promise.resolve(false);
      var prompt = deferredPrompt;
      deferredPrompt = null;
      prompt.prompt();
      return prompt.userChoice
        .then(function (choice) { return choice.outcome === 'accepted'; })
        .catch(function () { return false; });
    }
  };
})();
