# SprichDe — Demo deploy (Render.com, bepul)

Loyiha bitta Render **Web Service** sifatida joylashtiriladi: `backend/server.py` statik sahifalarni ham, `/api/*` ni ham beradi, SQLite esa service ichida yashaydi (bepul rejimda vaqtinchalik — har yangilanishda demo baza qayta yaratiladi, bu demo uchun yaxshi).

> **Netlify ishlamaydi** — u Python serverini o'rnatmaydi va SQLite'ni saqlamaydi. Agar albatta Netlify kerak bo'lsa: backend'ni Node.js/TypeScript (Netlify Functions) ga o'tkazib, bazani Neon/Supabase'ga ko'chirish kerak bo'ladi.

## 1. GitHub'ga yuklash

```powershell
cd "C:\Users\user\Desktop\adminpanel\PythonProject3"
git init
git add .
git commit -m "SprichDe demo"
git branch -M main
git remote add origin https://github.com/<username>/sprichde-demo.git
git push -u origin main
```

`backend/data/*.db` `.gitignore` da — repo'ga gitti bo'lmaydi, Render'da bo'sh baza avtomatik demo foydalanuvchilar bilan to'ladi (Aziza/Bekzod/Dilnoza/`admin@sprichde.uz`/`admin123`).

## 2. Render.com'da xizmat yaratish (bepul, karta talab qilinmaydi)

1. [render.com](https://render.com) → **New → Web Service** → GitHub hisobingizni ulang → `sprichde-demo` reponi tanlang.
2. Sozlamalar (yoki `render.yaml` avtomatik aniqlanadi):
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend/server.py`
   - **Instance Type**: Free
3. **Environment** (muhim):
   - `SPRICHDE_HOST` = `0.0.0.0`
   - `SPRICHDE_PORT` = `10000` (Render web service'ga 0.0.0.0:10000 da lokal qo'ngakni yo'naltiradi; `PORT` ham bo'ladi, lekin aniq qo'ygan yaxshi)
   - `SPRICHDE_OPEN` = `none` (brauzer ochilishini o'chiradi)
4. **Create Web Service** → build va deploy ~1–3 daqiqa. URL: `https://sprichde-demo.onrender.com`

Demo manzillari:
- Kirish: `https://sprichde-demo.onrender.com/`
- Admin: `https://sprichde-demo.onrender.com/admin.html`
- O‘quvchi: `aziza@example.com` / `demo1234` · Admin: `admin@sprichde.uz` / `admin123`

## Muhim ogohlantirishlar (ochiq internetga chiqish oldidan)

1. **Admin panel parolsiz** — hozirgi rejimda internetdagi har kim `/admin.html` ochib o‘quvchi ma’lumotlarini va parollarni ko‘radi, o‘quvchilarni o‘chiradi/bloklaydi. Jonli demo qilishdan oldin **admin himoyasini qayta yoqing** (kompyuterdagi demo uchun parolsiz qolishi mumkin, lekin ochiq URL uchun yo‘q).
2. **Demo bazada haqiqiy o‘quvchilar bo‘lmasin** — faqat demo seed foydalanuvchilar bo‘lsin (repo'da `.db` yo‘qligi buni ta'minlaydi).
3. **Bepul Render** 15 daqiqa faoliyatsizlikdan keyin “uxlaydi” — birinchi ochilish 30–60 s vaqt olishi mumkin (bu demo uchun normal).
4. **Ma’lumot vaqtinchalik** — har deploy/restart'da o‘quvchilar va to‘lovlar asl demo holatiga qaytadi. Demo uchun bu yaxshi; real mijozlarga ma’lumot kerak bo‘lsa — paid disk yoki Postgres.
5. **PWA HTTPS** ostida telefonda o‘rnatiladi — Render manzili bunga mos (Chrome → “Ilovani o‘rnatish”).

## Railway (alternativ)

[railway.app](https://railway.app) → New Project → Deploy from GitHub → reponi tanlang → Start command: `python backend/server.py` → env: `SPRICHDE_HOST=0.0.0.0` va `SPRICHDE_PORT=$PORT` (Railway `PORT` ni beradi — loyiha endi uni ham o‘qiydi) → URL oling. Railway bazaning vaqtinchalikligini xuddi shunday talab qiladi; bepul trial cheklangan.

## Nima qilingan (fayllar)

- `backend/server.py` — endi `SPRICHDE_PORT` yoki `PORT` env o‘zgaruvchisini o‘qiydi (Render/Railway mosligi).
- `requirements.txt`, `render.yaml`, `.gitignore`, `DEPLOY.md` — deploy uchun tayyor.
