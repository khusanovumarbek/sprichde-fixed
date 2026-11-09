# SprichDe — Nemis tili loyihasi (PWA + lokal backend)

Ishlaydigan versiya: **PWA** (`admin-panel/` papkasi) — HTML/CSS/JS + **Python stdlib backend** (`backend/server.py`, SQLite). Haqiqiy ma’lumotlar bazasi ishlatiladi; `lib/` papkasidagi Flutter skeleti hali tugallanmagan.

## 1. O‘quvchi ilovasi

Ochilishi: `index.html` → kirish → `app.html` (kabinet)

- `index.html` — **Kirish** (email + parol)
- `register.html` — **Ro‘yxatdan o‘tish** (ism, telefon, email, daraja, parol)
- `app.html` — **O‘quvchi kabineti** (91 kunlik sayohat, darslar, lug‘at, mashq, to‘lov)
- `journey.html` / `trial.html` / `invite.html` — sayohat, sinov darsi, taklif

Ro‘yxatdan o‘tgan har bir o‘quvchi backend bazasiga (`backend/data/sprichde.db`) qo‘shiladi va **Admin panel → O‘quvchilar** bo‘limida darhol ko‘rinadi.

## 2. Admin panel

Ochilishi: `PyCharm` → `run_app.py` yoki `run_admin.py` → ▶ Play (yoki `http://127.0.0.1:8000/admin.html`)

- `admin.html` — **Admin panel** (Umumiy ko‘rinish, Darslar, O‘quvchilar)
- `app.js` / `styles.css` — panel kodi
- **Kirish talab qilinmaydi** (kompyuterda demo uchun to‘g‘ridan-to‘g‘ri ochiladi)

Admin panel **O‘quvchilar** bo‘limida har bir o‘quvchi uchun ko‘rsatiladi: ism/email, daraja, **parol**, telefon, holati, **to‘lov holati** (To‘langan / To‘lamagan / Kutilmoqda / Rad etilgan) va premium kunlari. Admin to‘lovlarni tasdiqlashi, rad etishi, o‘quvchini bloklab/o‘chirishi yoki premium qo‘lda berishi mumkin.

> ⚠️ **DIQQAT:** parollar admin panelda oddiy matn ko‘rinishida ko‘rsatiladi (majburiy lokal demo talabi). Buni haqiqiy jonli loyihada ishlatmang — faqat mahalliy foydalaning.

## Ishga tushirish

- **Ilova (backend + brauzerni ochadi)**: PyCharm → `run_app.py` → ▶ Play → http://127.0.0.1:8000/
- **Faqat server**: PyCharm → `run_admin.py` (yoki `backend/server.py`) → ▶ Play
- Server `127.0.0.1` (localhost), port 8000 da ishlaydi.

## PWA (telefonga o‘rnatish)

PWA faqat **http://localhost** yoki **https://** orqali ishlaydi.

**Android (Chrome):** `run_app.py` orqali oching → Chrome menyusi → **“Ilovani o‘rnatish”**.
**iPhone (Safari):** Safari’da oching → **“Ulashish” ⬆️ → “Bosh ekranga qo‘shish”**.

**Telefonda kompyuterdagi serverni ochish:** telefon va kompyuter bir Wi-Fi’da bo‘lsin, `run_app.py` chiqargan `http://<kompyuter-IP>:8000/` manzilini oching (telefon uchun SW/HTTPS cheklovlari bo‘lishi mumkin — `ngrok http 8000` tavsiya etiladi).

### PWA fayllari

| Fayl | Vazifasi |
|------|----------|
| `manifest.json` | Ilova nomi, ikonkalar, `standalone` rejim |
| `sw.js` | Service worker: oflayn kesh (`sprichde-static-v8`) |
| `pwa.js` | SW ro‘yxatdan o‘tkazish + o‘rnatish tugmasi API |
| `icons/` | 192/512/maskable ikonkalar va Apple touch icon |

> Yangilanish chiqarganda `sw.js` dagi `CACHE_VERSION` ni oshiring — eski kesh avtomatik tozalanadi.

## Eslatmalar

- Ma’lumotlar `backend/data/sprichde.db` (SQLite) da — barcha admin harakatlari (to‘lov tasdiqlash, premium berish, o‘quvchi o‘chirish) shu yerda saqlanadi.
- Kirish sessiyalari `sessions` jadvalida (7 kun) saqlanadi.
- Bu loyiha **lokal demo** sifatida mo‘ljallangan; internetga joylashtirishdan oldin admin paroli, to‘lov ma’lumotlari va parol ko‘rsatish rejimini qayta ko‘rib chiqing.
