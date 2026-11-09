/* ============================================================
 * SprichDe — admin panel (backend + SQLite)
 * ============================================================ */

const names = {
  overview: 'Umumiy ko‘rinish',
  lessons: 'Darslar',
  students: 'O‘quvchilar',
};

const API = location.origin.startsWith('http') ? '' : 'http://127.0.0.1:8000';

let students = [];
let page = 'overview';
let toastTimer;

function authHeaders(extra) {
  const auth = typeof getAuth === 'function' ? getAuth() : null;
  const h = { ...(extra || {}) };
  if (auth) h.Authorization = 'Bearer ' + auth.token;
  return h;
}

/* ======== PAROLSIZ ADMIN REJIMI (faqat kompyuterda/demo) ======== */
/* Admin panel ochilishi bilan demo admin hisobi orqali sessiya */
/* avtomatik olinadi — kirish oynasi yo'q. DIQQAT: himoyasiz rejim. */
const DEMO_ADMIN = { email: 'admin@sprichde.uz', password: 'admin123' };

async function api(path, options = {}) {
  const doFetch = () => fetch(API + path, { ...options, headers: authHeaders(options.headers) });
  let res = await doFetch();
  if (res.status === 401) {
    // Sessiya eskirgan bo'lsa — parolsiz qayta kiramiz
    try { clearAuth(); } catch {}
    try { await ensureAdminSession(); } catch { /* quyida xato qaytariladi */ }
    res = await doFetch();
    if (res.status === 401) throw new Error('Ruxsat yo‘q. Backend admin hisobini tekshiring.');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Server xatosi');
  return data;
}

/* ---------------------------- Darslar ---------------------------- */

const seedLessons = [
  { title: 'Salomlashish', level: 'Anfänger', duration: 8, description: 'Tanishish va salomlashish iboralari', status: 'Nashr qilingan' },
  { title: 'Kundalik tanishuv', level: 'Anfänger', duration: 12, description: 'O‘zingiz haqingizda gapirish', status: 'Nashr qilingan' },
  { title: 'Kafe va buyurtma', level: 'Anfänger', duration: 10, description: 'Kafeda kerak bo‘ladigan iboralar', status: 'Qoralama' },
  { title: 'Safar va yo‘nalishlar', level: 'Grundkenntnisse', duration: 15, description: 'Yo‘l so‘rash va transport', status: 'Nashr qilingan' },
];

function read(key, fallback) {
  try {
    const value = JSON.parse(localStorage.getItem(key));
    return Array.isArray(value) ? value : fallback;
  } catch {
    return fallback;
  }
}

const levelNames = [
  { value: 'Anfänger', label: 'Anfänger - Boshlang‘ich' },
  { value: 'Grundkenntnisse', label: 'Grundkenntnisse - Asosiy bilimlar' },
  { value: 'Erweiterte Grundkenntnisse', label: 'Erweiterte Grundkenntnisse - Kengaytirilgan boshlang‘ich bilimlar' },
  { value: 'Mittelstufe', label: 'Mittelstufe - O‘rta daraja' },
  { value: 'Obere Mittelstufe', label: 'Obere Mittelstufe - Yuqori o‘rta daraja' },
  { value: 'Prüfungsvorbereitung', label: 'Prüfungsvorbereitung - Imtihonga tayyorgarlik' },
];
const levelLabels = Object.fromEntries(levelNames.map((level) => [level.value, level.label]));
function levelLabel(value) {
  return levelLabels[value] || value;
}

const oldLevels = { A1: 'Anfänger', A2: 'Grundkenntnisse', B1: 'Mittelstufe', B2: 'Obere Mittelstufe' };
let lessons = read('deutschAdminLessons', seedLessons).map((x) => ({ ...x, level: oldLevels[x.level] || x.level }));

const content = document.querySelector('#pageContent');
const form = document.querySelector('#contentForm');
const modal = document.querySelector('#modalBackdrop');
const toast = document.querySelector('#toast');

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function save() {
  localStorage.setItem('deutschAdminLessons', JSON.stringify(lessons));
}

function notify(text) {
  toast.textContent = text;
  toast.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
}

function heading(k, t, d, button = '') {
  return `<div class="heading"><div><span class="eyebrow">${k}</span><h1>${t}</h1><p>${d}</p></div>${button}</div>`;
}

function addButton(text) {
  return `<button class="button primary" data-add>${text} <span>↗</span></button>`;
}

function stat(label, value, icon, foot) {
  return `<article class="stat"><div class="stat-top"><span>${label}</span><span class="stat-icon">${icon}</span></div><div class="stat-value">${value}</div><div class="stat-foot">${foot}</div></article>`;
}

/* --------------------------- Umumiy ko‘rinish --------------------------- */

function overview() {
  const date = new Intl.DateTimeFormat('uz-UZ', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date());
  const recent = lessons.slice(0, 4).map((x, i) => `
    <div class="lesson-row">
      <div class="lesson-title">
        <span class="thumb">${String(i + 1).padStart(2, '0')}</span>
        <div>
          <div class="lesson-name">${esc(x.title)}</div>
          <div class="sub">${esc(levelLabel(x.level))} · ${esc(x.duration)} daqiqa</div>
        </div>
      </div>
      <span class="tag">${esc(levelLabel(x.level))}</span>
      <span class="tag ${x.status === 'Qoralama' ? 'draft' : 'ok'}">${esc(x.status)}</span>
      <button class="row-action" data-delete="${i}" aria-label="Darsni o‘chirish">🗑</button>
    </div>`).join('') || '<div class="empty">Hali dars qo‘shilmagan.</div>';

  return `
    ${heading('BOSHQARUV PANELI', 'Xush kelibsiz, Admin 👋', 'Nemis tili kurslaringiz va o‘quv kontentingiz holati.', addButton('Yangi dars'))}
    <section class="stats">
      ${stat('Jami darslar', String(lessons.length).padStart(2, '0'), '📚', '<span class="up">+2</span> shu oy qo‘shildi')}
      ${stat('To‘lov qilganlar', '<span id="statPaid">—</span>', '💳', '<span class="up" id="statPaidFoot">Yuklanmoqda…</span>')}
      ${stat('Faol o‘quvchilar', '<span id="statStudents">—</span>', '👥', '<span class="up" id="statNew">+ 0</span> yangi shu hafta')}
      ${stat('Kutilayotgan to‘lovlar', '<span id="statPending">—</span>', '⏳', 'Admin tasdig‘ini kutmoqda')}
    </section>
    <section class="grid">
      <article class="panel">
        <div class="panel-head"><h2>Oxirgi darslar</h2><button class="text-link" data-go="lessons">Barchasini ko‘rish →</button></div>
        <div class="lesson-list">${recent}</div>
      </article>
      <article class="panel">
        <div class="panel-head"><h2>To‘lovlar holati</h2><button class="text-link" data-go="students">O‘quvchilar →</button></div>
        <p class="pay-overview" id="payOverview">To‘lovlar bo‘yicha ma’lumot yuklanmoqda…</p>
        <div class="note"><b>${date}</b><br>To‘lovlar 9860170110162592 kartasiga tushadi. Har bir to‘lovni admin qo‘lda tasdiqlaydi.</div>
      </article>
    </section>`;
}

/* ------------------------------ Darslar ------------------------------ */

function tableRows(items) {
  return items.map((x, i) => `
    <tr>
      <td><div class="table-primary">${esc(x.title)}</div><div class="table-secondary">${esc(x.description || 'Yangi o‘quv materiali')}</div></td>
      <td><span class="tag">${esc(levelLabel(x.level))}</span></td>
      <td>${esc(x.duration)} daqiqa</td>
      <td><span class="tag ${x.status === 'Qoralama' ? 'draft' : 'ok'}">${esc(x.status)}</span></td>
      <td><button class="row-action" data-delete="${x.originalIndex ?? i}" aria-label="Darsni o‘chirish">🗑</button></td>
    </tr>`).join('') || '<tr><td colspan="5" class="empty">Dars topilmadi.</td></tr>';
}

function lessonsPage() {
  return `
    ${heading('KONTENT BOSHQARUVI', 'Darslar', 'Kurs darslarini yarating va ularning holatini boshqaring.', addButton('Yangi dars'))}
    <section class="panel">
      <div class="toolbar">
        <label class="search">🔍 <input id="search" placeholder="Darslarni qidirish…"></label>
        <select class="filter" id="levelFilter">
          <option value="">Barcha darajalar</option>
          ${levelNames.map((x) => `<option value="${x.value}">${x.label}</option>`).join('')}
        </select>
      </div>
      <div class="table-wrap">
        <table class="table">
          <thead><tr><th>DARS NOMI</th><th>DARAJA</th><th>DAVOMIYLIGI</th><th>HOLATI</th><th></th></tr></thead>
          <tbody id="lessonRows">${tableRows(lessons)}</tbody>
        </table>
      </div>
    </section>`;
}

/* ----------------------------- O‘quvchilar ----------------------------- */

function studentsPage() {
  return `
    ${heading('O‘QUVCHI FAOLLIGI', 'O‘quvchilar', 'Ilovada ro‘yxatdan o‘tgan o‘quvchilar shu yerda avtomatik paydo bo‘ladi.')}
    <section class="panel">
      <div class="toolbar">
        <label class="search">🔍 <input id="studentSearch" placeholder="Ism yoki email bo‘yicha qidirish…"></label>
        <button class="button quiet" id="studentReload" type="button">↻ Yangilash</button>
      </div>
      <div class="table-wrap">
        <table class="table students-table">
          <thead>
            <tr>
              <th>O‘QUVCHI</th>
              <th>DARAJA</th>
              <th>PAROL</th>
              <th>TELEFON</th>
              <th>HOLATI</th>
              <th>TO‘LOV HOLATI</th>
              <th>RO‘YXATDAN O‘TGAN</th>
              <th></th>
            </tr>
          </thead>
          <tbody id="studentRows"><tr><td colspan="8" class="empty">Yuklanmoqda…</td></tr></tbody>
        </table>
      </div>
    </section>`;
}

function studentStatusTag(status) {
  return status === 'blocked'
    ? '<span class="tag draft">Bloklangan</span>'
    : '<span class="tag ok">Faol</span>';
}

function formatStudentDate(value) {
  const d = new Date(value);
  return Number.isNaN(d.getTime())
    ? '—'
    : new Intl.DateTimeFormat('uz-UZ', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(d);
}

function paymentCell(x) {
  const p = x.payment;
  const days = Number(x.premiumDaysLeft || 0);
  const premiumLine = days > 0
    ? `<div class="table-secondary">Premium: ${days} kun</div>`
    : '<div class="table-secondary">Premium yo‘q</div>';

  if (!p) {
    return `<span class="tag">To‘lamagan</span>${premiumLine}
      <div class="pay-actions">
        <button class="mini" data-premium="${x.id}">Qo‘lda</button>
      </div>`;
  }

  if (p.status === 'pending') {
    return `<span class="tag draft">Kutilmoqda</span>
      <div class="table-secondary">${p.months} oylik · ${esc(methodLabel(p.method))}</div>
      <div class="pay-actions">
        <button class="mini ok" data-pay-confirm="${p.id}">Tasdiqlash</button>
        <button class="mini bad" data-pay-reject="${p.id}">Rad etish</button>
      </div>`;
  }

  if (p.status === 'rejected') {
    return `<span class="tag bad">Rad etilgan</span>${premiumLine}
      <div class="pay-actions">
        <button class="mini" data-premium="${x.id}">Qo‘lda</button>
      </div>`;
  }

  // paid
  const when = p.reviewedAt || p.createdAt;
  return `<span class="tag ok">To‘langan</span>
    <div class="table-secondary">${p.months} oylik · ${esc(methodLabel(p.method))}</div>
    ${premiumLine}
    ${when ? `<div class="table-secondary">${formatStudentDate(when)}</div>` : ''}
    <div class="pay-actions">
      <button class="mini" data-premium="${x.id}">Uzaytirish</button>
    </div>`;
}

function methodLabel(method) {
  return { uzcard: 'Uzcard', humo: 'Humo', visa: 'Visa', manual: 'Qo‘lda' }[method] || method || '—';
}

function studentRows(items) {
  return items.map((x) => `
    <tr>
      <td>
        <div class="table-primary">${esc(x.fullName)}</div>
        <div class="table-secondary">${esc(x.email)}</div>
      </td>
      <td><span class="tag">${esc(levelLabel(x.level))}</span></td>
      <td><span class="table-secondary" style="font-family:monospace;font-size:12px">${esc(x.password ?? '—')}</span></td>
      <td>${esc(x.phone || '—')}</td>
      <td>${studentStatusTag(x.status)}</td>
      <td class="pay-cell">${paymentCell(x)}</td>
      <td>${formatStudentDate(x.createdAt)}</td>
      <td><button class="row-action" data-student-delete="${x.id}" title="O‘chirish" aria-label="O‘quvchini o‘chirish">🗑</button></td>
    </tr>`).join('') || '<tr><td colspan="8" class="empty">O‘quvchi topilmadi.</td></tr>';
}

function bindPaymentActions(box) {
  box.querySelectorAll('[data-pay-confirm]').forEach((btn) => btn.addEventListener('click', async () => {
    const id = Number(btn.dataset.payConfirm);
    if (!confirm('To‘lovni tasdiqlaysizmi? Premium muddati avtomatik uzaytiriladi.')) return;
    btn.disabled = true;
    try {
      await api('/api/payments/' + id, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'paid' }),
      });
      notify('To‘lov tasdiqlandi — premium faollashtirildi.');
      await loadStudents();
      refreshStats();
    } catch (err) {
      btn.disabled = false;
      notify(err.message);
    }
  }));

  box.querySelectorAll('[data-pay-reject]').forEach((btn) => btn.addEventListener('click', async () => {
    const id = Number(btn.dataset.payReject);
    if (!confirm('To‘lovni rad etasizmi?')) return;
    btn.disabled = true;
    try {
      await api('/api/payments/' + id, {
        method: 'PATCH',
        body: JSON.stringify({ status: 'rejected' }),
      });
      notify('To‘lov rad etildi.');
      await loadStudents();
      refreshStats();
    } catch (err) {
      btn.disabled = false;
      notify(err.message);
    }
  }));

  box.querySelectorAll('[data-premium]').forEach((btn) => btn.addEventListener('click', async () => {
    const id = Number(btn.dataset.premium);
    const answer = prompt('Premium muddatini tanlang: 3, 6 yoki 12 oy', '3');
    if (answer === null) return;
    const months = Number(answer);
    if (![3, 6, 12].includes(months)) {
      notify('Faqat 3, 6 yoki 12 oyni tanlash mumkin.');
      return;
    }
    btn.disabled = true;
    try {
      await api('/api/students/' + id + '/premium', {
        method: 'POST',
        body: JSON.stringify({ months }),
      });
      notify(`${months} oylik premium qo‘lda qo‘shildi.`);
      await loadStudents();
      refreshStats();
    } catch (err) {
      btn.disabled = false;
      notify(err.message);
    }
  }));
}

function paintStudents() {
  const box = document.querySelector('#studentRows');
  if (!box) return;
  const q = (document.querySelector('#studentSearch')?.value || '').toLocaleLowerCase('uz');
  const found = students.filter((x) =>
    !q ||
    String(x.fullName).toLocaleLowerCase('uz').includes(q) ||
    String(x.email).toLocaleLowerCase('uz').includes(q)
  );
  box.innerHTML = studentRows(found);

  box.querySelectorAll('[data-student-delete]').forEach((b) => b.addEventListener('click', async () => {
    const id = Number(b.dataset.studentDelete);
    const target = students.find((x) => x.id === id);
    if (!confirm(`«${target?.fullName || 'O‘quvchi'}» ro‘yxatdan o‘chirilsinmi?`)) return;
    try {
      await api('/api/students/' + id, { method: 'DELETE' });
      students = students.filter((x) => x.id !== id);
      paintStudents();
      notify('O‘quvchi o‘chirildi.');
      refreshStats();
    } catch (err) {
      notify(err.message);
    }
  }));

  bindPaymentActions(box);
}

async function loadStudents() {
  const box = document.querySelector('#studentRows');
  if (box) box.innerHTML = '<tr><td colspan="8" class="empty">Yuklanmoqda…</td></tr>';
  try {
    const data = await api('/api/students');
    students = data.students || [];
    paintStudents();
  } catch (err) {
    if (box) box.innerHTML = `<tr><td colspan="8" class="empty">Serverga ulanib bo‘lmadi: ${esc(err.message)}</td></tr>`;
  }
}

async function refreshStats() {
  try {
    const s = await api('/api/stats');
    const paid = document.querySelector('#statPaid');
    if (paid) paid.textContent = String(s.paidStudents ?? 0);
    const paidFoot = document.querySelector('#statPaidFoot');
    if (paidFoot) paidFoot.textContent = `${s.totalStudents ?? 0} ta o‘quvchidan`;
    const studentsEl = document.querySelector('#statStudents');
    if (studentsEl) studentsEl.textContent = String(s.totalStudents ?? 0);
    const newEl = document.querySelector('#statNew');
    if (newEl) newEl.textContent = `+ ${s.newThisWeek ?? 0}`;
    const pending = document.querySelector('#statPending');
    if (pending) pending.textContent = String(s.pendingPayments ?? 0);
    const overview = document.querySelector('#payOverview');
    if (overview) {
      overview.textContent = `${s.paidStudents ?? 0} o‘quvchi to‘lov qilgan, ${s.pendingPayments ?? 0} ta to‘lov tasdiqlashni kutmoqda.`;
    }
  } catch {}
}

/* ------------------------------ Render ------------------------------ */

const views = { overview, lessons: lessonsPage, students: studentsPage };

function render() {
  content.innerHTML = (views[page] || overview)();
  document.querySelector('#lessonCount').textContent = String(lessons.length).padStart(2, '0');

  content.querySelector('[data-add]')?.addEventListener('click', openModal);
  content.querySelector('[data-go]')?.addEventListener('click', (e) => setPage(e.currentTarget.dataset.go));

  content.querySelectorAll('[data-delete]').forEach((b) => b.addEventListener('click', () => {
    const item = lessons.splice(Number(b.dataset.delete), 1)[0];
    save();
    render();
    notify(`«${item.title}» darsi o‘chirildi.`);
  }));

  document.querySelector('#search')?.addEventListener('input', filter);
  document.querySelector('#levelFilter')?.addEventListener('change', filter);

  if (page === 'students') loadStudents();
  else if (page === 'overview') refreshStats();
}

function filter() {
  const q = (document.querySelector('#search')?.value || '').toLocaleLowerCase('uz');
  const level = document.querySelector('#levelFilter')?.value || '';
  const found = lessons
    .map((x, i) => ({ ...x, originalIndex: i }))
    .filter((x) => String(x.title).toLocaleLowerCase('uz').includes(q) && (!level || x.level === level));
  document.querySelector('#lessonRows').innerHTML = tableRows(found);
  document.querySelectorAll('[data-delete]').forEach((b) => b.addEventListener('click', () => {
    const item = lessons.splice(Number(b.dataset.delete), 1)[0];
    save();
    render();
    notify(`«${item.title}» darsi o‘chirildi.`);
  }));
}

function setPage(next) {
  page = names[next] ? next : 'overview';
  document.querySelectorAll('.nav-item').forEach((b) => b.classList.toggle('active', b.dataset.page === page));
  document.querySelector('#breadcrumbCurrent').textContent = names[page];
  render();
  document.querySelector('#sidebar').classList.remove('open');
}

/* ------------------------------- Modal ------------------------------- */

function openModal() {
  form.dataset.kind = 'lesson';
  document.querySelector('#modalEyebrow').textContent = 'YANGI KONTENT';
  document.querySelector('#modalTitle').textContent = 'Yangi dars';
  document.querySelector('#itemTitle').placeholder = 'Masalan, Kundalik salomlashuv';
  document.querySelector('#itemDescription').placeholder = 'Qisqacha ma’lumot...';
  modal.hidden = false;
  document.querySelector('#itemTitle').focus();
}

function closeModal() {
  modal.hidden = true;
  form.reset();
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const data = new FormData(form);
  const title = String(data.get('title') || '').trim();
  if (!title) return;
  lessons.unshift({
    title,
    level: String(data.get('level')),
    duration: Math.max(1, Number(data.get('duration')) || 10),
    description: String(data.get('description') || '').trim() || 'Yangi o‘quv materiali',
    status: 'Qoralama',
  });
  save();
  closeModal();
  render();
  notify('Yangi dars qoralama sifatida saqlandi.');
});

document.querySelectorAll('.nav-item').forEach((b) => b.addEventListener('click', () => setPage(b.dataset.page)));
document.querySelector('#modalClose').addEventListener('click', closeModal);
document.querySelector('#cancelModal').addEventListener('click', closeModal);
modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !modal.hidden) closeModal(); });
document.querySelector('#menuToggle').addEventListener('click', () => document.querySelector('#sidebar').classList.toggle('open'));
document.querySelector('#notificationButton').addEventListener('click', () => notify('Hozircha yangi bildirishnoma yo‘q.'));
document.querySelector('#helpButton').addEventListener('click', () => notify('Dars bo‘limidan yangi kontent qo‘shing, o‘quvchilar bo‘limida to‘lovlarni tasdiqlang.'));
document.querySelector('#todayDate').textContent = new Intl.DateTimeFormat('uz-UZ', { weekday: 'short', day: 'numeric', month: 'short' }).format(new Date());

/* ---------------------- Admin autentifikatsiyasi (parolsiz rejim) ---------------------- */

function showAdminApp(profile) {
  const appEl = document.querySelector('#adminApp');
  if (appEl) appEl.hidden = false;
  const name = profile?.fullName || 'Admin';
  const ini = typeof initials === 'function' ? initials(name) : 'AS';
  const a = document.querySelector('#adminName');
  if (a) a.textContent = name;
  const b = document.querySelector('#adminAvatar');
  if (b) b.textContent = ini;
  const t = document.querySelector('#topAvatar');
  if (t) t.textContent = ini;
  render();
}

/** Saqlangan sessiya yoki demo admin bilan avtomatik kirish. */
async function ensureAdminSession() {
  try {
    const auth = getAuth();
    if (auth && auth.role === 'admin') {
      const me = await authFetch('/api/me');
      if (me.role === 'admin') {
        setAuth({ token: auth.token, role: me.role, profile: me.profile });
        return me.profile;
      }
    }
  } catch {
    /* saqlangan sessiya yaroqsiz — avtomatik kirishga o'tamiz */
  }
  const data = await authFetch('/api/admin/login', {
    method: 'POST',
    body: JSON.stringify(DEMO_ADMIN),
  });
  setAuth({ token: data.token, role: data.role, profile: data.profile });
  return data.profile;
}

(async () => {
  const appEl = document.querySelector('#adminApp');
  if (appEl) appEl.hidden = false; // panel darhol ochiladi
  try {
    const profile = await ensureAdminSession();
    showAdminApp(profile);
  } catch (err) {
    const box = document.querySelector('#pageContent');
    if (box) {
      box.innerHTML = `<div class="empty" style="display:block"><b>Serverga ulanib bo‘lmadi</b><small>${esc(err.message)}<br>Backend ishga tushirilganiga ishonch hosil qiling (python run_app.py yoki PyCharm ▶).</small></div>`;
    }
  }
})();
