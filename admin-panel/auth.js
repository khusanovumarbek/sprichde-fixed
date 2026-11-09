/* Foydalanuvchi sessiyasi bilan ishlash uchun yordamchi funksiyalar. */

const AUTH_KEY = /admin/i.test(location.pathname || '')
  ? 'sprichdeAdminAuth'   // admin panel sessiyasi
  : 'sprichdeAuth';        // o‘quvchi ilovasi sessiyasi

// Eski bitta kalitli sessiyani mos kalitga ko'chiramiz (admin bo'lsa)
try {
  const raw = localStorage.getItem('sprichdeAuth');
  if (raw) {
    const legacy = JSON.parse(raw);
    if (legacy && legacy.role === 'admin') {
      if (!localStorage.getItem('sprichdeAdminAuth')) {
        localStorage.setItem('sprichdeAdminAuth', JSON.stringify(legacy));
      }
      localStorage.removeItem('sprichdeAuth');
    }
  }
} catch {}

function apiBase() {
  // index.html ni PyCharm/har qanday static serverdan ochganda ham
  // backend API odatda 8000-portda ishlaydi (backend/server.py).
  try {
    const { protocol, hostname, port } = location;
    if (protocol === 'file:') return 'http://127.0.0.1:8000';
    if ((hostname === 'localhost' || hostname === '127.0.0.1') && port && port !== '8000') {
      return 'http://127.0.0.1:8000';
    }
  } catch {}
  return location.origin && location.origin.startsWith('http') ? '' : 'http://127.0.0.1:8000';
}

function getAuth() {
  try {
    const raw = JSON.parse(localStorage.getItem(AUTH_KEY));
    return raw && raw.token ? raw : null;
  } catch {
    return null;
  }
}

function setAuth(data) {
  localStorage.setItem(AUTH_KEY, JSON.stringify(data));
}

function clearAuth() {
  localStorage.removeItem(AUTH_KEY);
}

async function authFetch(path, options = {}) {
  const auth = getAuth();
  const headers = { ...(options.headers || {}) };
  if (options.body) headers['Content-Type'] = 'application/json';
  if (auth) headers['Authorization'] = 'Bearer ' + auth.token;

  let response;
  try {
    response = await fetch(apiBase() + path, { ...options, headers });
  } catch (e) {
    throw new Error(
      "Backend bilan aloqa yo‘q. PyCharm’da backend/server.py ni Run qiling, so‘ng http://localhost:8000/ dan oching."
    );
  }

  if (response.status === 401) {
    clearAuth();
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || 'Server xatosi (' + response.status + ').');
  }
  return data;
}

async function logout() {
  try {
    await authFetch('/api/logout', { method: 'POST' });
  } catch {
    /* server javob bermasa ham mahalliy sessiyani tozalaymiz */
  }
  clearAuth();
  location.href = /admin\.html/.test(location.pathname) ? 'admin.html' : 'index.html';
}

/** Sahifa ochilishida sessiyani tekshiradi. */
async function guard(role) {
  const auth = getAuth();
  if (!auth) {
    location.replace('index.html');
    return null;
  }
  if (role && auth.role !== role) {
    location.replace(auth.role === 'admin' ? 'admin.html' : 'app.html');
    return null;
  }
  try {
    const me = await authFetch('/api/me');
    setAuth({ token: auth.token, role: me.role, profile: me.profile });
    return me;
  } catch {
    location.replace('index.html');
    return null;
  }
}

function initials(name) {
  return String(name || '?')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('');
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat('uz-UZ', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(date);
}
