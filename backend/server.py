"""
SprichDe backend.

Tashqi kutubxonalarsiz (faqat Python stdlib) ishlaydi:
    python backend/server.py

Sahifalar:
    /                -> foydalanuvchi uchun kirish (sign in)
    /register.html     -> ro'yxatdan o'tish (sign up)
    /app.html          -> foydalanuvchi kabineti (ilova)
    /admin.html        -> admin panel (faqat adminlar uchun)

API:
    POST /api/register       ochiq  - ro'yxatdan o'tish
    POST /api/login          ochiq  - o'quvchi kirishi
    POST /api/admin/login    ochiq  - admin kirishi
    GET  /api/me             token  - joriy profil
    POST /api/logout         token  - chiqish
    GET  /api/students       admin  - o'quvchilar ro'yxati
    ...
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sqlite3
import sys
import webbrowser
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent
ADMIN_DIR = BASE_DIR.parent / "admin-panel"
DB_PATH = BASE_DIR / "data" / "sprichde.db"

HOST = os.environ.get("SPRICHDE_HOST", "127.0.0.1")
PORT = int(os.environ.get("SPRICHDE_PORT") or os.environ.get("PORT") or "8000")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

LEVELS = [
    "Anfänger",
    "Grundkenntnisse",
    "Erweiterte Grundkenntnisse",
    "Mittelstufe",
    "Obere Mittelstufe",
    "Prüfungsvorbereitung",
]

SEED_STUDENTS = [
    ("Aziza Karimova", "aziza@example.com", "Anfänger", "+998 90 111 22 33"),
    ("Bekzod Tursunov", "bekzod@example.com", "Grundkenntnisse", "+998 91 222 33 44"),
    ("Dilnoza Yusupova", "dilnoza@example.com", "Mittelstufe", "+998 93 333 44 55"),
]

SEED_ADMIN = ("Admin", "admin@sprichde.uz", "admin123")

SESSION_DAYS = 7

# To'lov (demo): barcha to'lovlar shu kartaga tushadi
PAYMENT_CARD = "9860170110162592"
PAYMENT_HOLDER = "SprichDe"
PAYMENT_WINDOW_PERIODS = {3: 91, 6: 182, 12: 365}
DEFAULT_PREMIUM_DAYS = 91
PAYMENT_METHODS = ("uzcard", "humo", "visa")


# --------------------------------------------------------------------------- #
# Parollar
# --------------------------------------------------------------------------- #

def hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), 120_000
    ).hex()


def verify_password(password: str, salt: str, expected: str) -> bool:
    if secrets.compare_digest(hash_password(password, salt), expected):
        return True
    # Eski (pbkdf2'dan oldingi) hash'lar bilan moslik
    legacy = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return secrets.compare_digest(legacy, expected)


# --------------------------------------------------------------------------- #
# Baza
# --------------------------------------------------------------------------- #

def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(conn: sqlite3.Connection, table: str, column: str, decl: str) -> None:
    """Eski bazalarga yangi ustunlarni xavfsiz qo'shadi."""
    columns = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")


def init_db() -> None:
    with db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name     TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                password_salt TEXT    NOT NULL,
                password_hash TEXT    NOT NULL,
                level         TEXT    NOT NULL DEFAULT 'Anfänger',
                phone         TEXT    DEFAULT '',
                status        TEXT    NOT NULL DEFAULT 'active',
                created_at    TEXT    NOT NULL
            )
            """
        )
        # Yangi ustunlar (eski bazalar uchun migratsiya)
        ensure_column(conn, "students", "premium_until", "TEXT DEFAULT ''")
        ensure_column(conn, "students", "plain_password", "TEXT DEFAULT ''")

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS admins (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name     TEXT    NOT NULL,
                email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                password_salt TEXT    NOT NULL,
                password_hash TEXT    NOT NULL,
                created_at    TEXT    NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token      TEXT PRIMARY KEY,
                role       TEXT NOT NULL,
                ref_id     INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                student_id     INTEGER PRIMARY KEY,
                completed_days TEXT    NOT NULL DEFAULT '[]',
                trial_done     INTEGER NOT NULL DEFAULT 0,
                updated_at     TEXT    NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id  INTEGER NOT NULL,
                plan_months INTEGER NOT NULL,
                amount      INTEGER NOT NULL DEFAULT 0,
                method      TEXT    NOT NULL DEFAULT 'uzcard',
                payer_card  TEXT    DEFAULT '',
                status      TEXT    NOT NULL DEFAULT 'pending',
                created_at  TEXT    NOT NULL,
                reviewed_at TEXT    DEFAULT '',
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            )
            """
        )

        now = datetime.now(timezone.utc).isoformat()
        default_until = (datetime.now(timezone.utc) + timedelta(days=DEFAULT_PREMIUM_DAYS)).isoformat()

        if conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            for name, email, level, phone in SEED_STUDENTS:
                salt = secrets.token_hex(8)
                conn.execute(
                    "INSERT INTO students (full_name, email, password_salt, password_hash,"
                    " level, phone, status, created_at, premium_until, plain_password) VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (name, email, salt, hash_password("demo1234", salt), level, phone, "active", now, default_until, "demo1234"),
                )

        # Premium muddati kiritilmagan o'quvchilarga 91 kunlik boshlang'ich muddat
        conn.execute(
            "UPDATE students SET premium_until = ? WHERE premium_until IS NULL OR premium_until = ''",
            (default_until,),
        )

        # Demo urug' (seed) o'quvchilarining paroli ma'lum — admin panelida ko'rinsin
        conn.execute(
            "UPDATE students SET plain_password = 'demo1234'"
            " WHERE email IN ('aziza@example.com','bekzod@example.com','dilnoza@example.com')"
            " AND (plain_password IS NULL OR plain_password = '')"
        )

        if conn.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
            name, email, password = SEED_ADMIN
            salt = secrets.token_hex(8)
            conn.execute(
                "INSERT INTO admins (full_name, email, password_salt, password_hash, created_at)"
                " VALUES (?,?,?,?,?)",
                (name, email, salt, hash_password(password, salt), now),
            )


def days_left(until: str) -> int:
    """Premium tugashiga qolgan kunlar (yuqoriga yaxlitlanadi)."""
    if not until:
        return 0
    try:
        end = datetime.fromisoformat(until)
    except ValueError:
        return 0
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    seconds = (end - datetime.now(timezone.utc)).total_seconds()
    return max(0, int((seconds + 86399) // 86400))


def payment_public(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "studentId": row["student_id"],
        "months": row["plan_months"],
        "amount": row["amount"],
        "method": row["method"],
        "status": row["status"],
        "createdAt": row["created_at"],
        "reviewedAt": row["reviewed_at"],
    }


def student_public(row: sqlite3.Row, payment: sqlite3.Row | None = None) -> dict:
    """Parol maydonlarini tashqariga chiqarmaydi."""
    return {
        "id": row["id"],
        "fullName": row["full_name"],
        "email": row["email"],
        "level": row["level"],
        "phone": row["phone"],
        "status": row["status"],
        "createdAt": row["created_at"],
        "premiumUntil": row["premium_until"] or "",
        "premiumDaysLeft": days_left(row["premium_until"]),
        "payment": payment_public(payment) if payment is not None else None,
    }


def admin_public(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "fullName": row["full_name"], "email": row["email"]}


# --------------------------------------------------------------------------- #
# Sessiyalar
# --------------------------------------------------------------------------- #

def create_session(role: str, ref_id: int) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    with db() as conn:
        conn.execute(
            "INSERT INTO sessions (token, role, ref_id, created_at, expires_at)"
            " VALUES (?,?,?,?,?)",
            (token, role, ref_id, now.isoformat(), (now + timedelta(days=SESSION_DAYS)).isoformat()),
        )
        # eskirgan sessiyalarni tozalash
        conn.execute("DELETE FROM sessions WHERE datetime(expires_at) < datetime('now')")
    return token


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #

class Handler(SimpleHTTPRequestHandler):
    server_version = "SprichDe/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ADMIN_DIR), **kwargs)

    def end_headers(self) -> None:
        # Brauzer (ayniqsa Chrome) hech narsani keshlamasin — doim serverdan yangisini olsin.
        # Bu buzilgan/vaqtinchalik keshdagi bo'sh sahifalar muammosini yo'qotadi.
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Expires", "0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

    # ---------------------------- yordamchilar ---------------------------- #

    def send_json(self, payload, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def bearer_token(self) -> str:
        header = self.headers.get("Authorization") or ""
        if header.lower().startswith("bearer "):
            return header[7:].strip()
        return ""

    def session(self) -> sqlite3.Row | None:
        token = self.bearer_token()
        if not token:
            return None
        with db() as conn:
            row = conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
        if row is None:
            return None
        try:
            expires = datetime.fromisoformat(row["expires_at"])
        except ValueError:
            return None
        if expires < datetime.now(timezone.utc):
            return None
        return row

    def require_admin(self) -> sqlite3.Row | None:
        session = self.session()
        if session is None or session["role"] != "admin":
            self.send_json({"error": "Ruxsat yo‘q. Admin sifatida kiring."}, HTTPStatus.UNAUTHORIZED)
            return None
        return session

    def require_student(self) -> sqlite3.Row | None:
        session = self.session()
        if session is None or session["role"] != "student":
            self.send_json({"error": "Ruxsat yo‘q. O‘quvchi sifatida kiring."}, HTTPStatus.UNAUTHORIZED)
            return None
        return session

    def log_message(self, fmt: str, *args) -> None:
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))

    # ------------------------------ routing ------------------------------- #

    def do_OPTIONS(self) -> None:
        self.send_json({}, HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/students":
            return self.api_list_students()
        if path == "/api/stats":
            return self.api_stats()
        if path == "/api/me":
            return self.api_me()
        if path == "/api/payment-info":
            return self.api_payment_info()
        if path == "/api/progress":
            return self.api_get_progress()
        if path == "/api/payments/me":
            return self.api_my_payments()
        if path == "/api/payments":
            return self.api_list_payments()
        if path == "/api/health":
            return self.send_json({"ok": True})
        return super().do_GET()

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/register":
            return self.api_register()
        if path == "/api/login":
            return self.api_login("student")
        if path == "/api/admin/login":
            return self.api_login("admin")
        if path == "/api/logout":
            return self.api_logout()
        if path == "/api/students":
            return self.api_create_student()
        if path == "/api/progress/complete":
            return self.api_complete_day()
        if path == "/api/payments":
            return self.api_create_payment()
        if path == "/api/me/password":
            return self.api_change_password()
        match = re.fullmatch(r"/api/students/(\d+)/premium", path)
        if match:
            return self.api_manual_premium(int(match.group(1)))
        return self.send_json({"error": "Topilmadi"}, HTTPStatus.NOT_FOUND)

    def do_PATCH(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/me":
            return self.api_update_me()
        match = re.fullmatch(r"/api/students/(\d+)", path)
        if match:
            return self.api_update_student(int(match.group(1)))
        match = re.fullmatch(r"/api/payments/(\d+)", path)
        if match:
            return self.api_review_payment(int(match.group(1)))
        return self.send_json({"error": "Topilmadi"}, HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        match = re.fullmatch(r"/api/students/(\d+)", path)
        if match:
            return self.api_delete_student(int(match.group(1)))
        return self.send_json({"error": "Topilmadi"}, HTTPStatus.NOT_FOUND)

    # --------------------------- autentifikatsiya -------------------------- #

    def api_login(self, role: str) -> None:
        data = self.read_json()
        email = str(data.get("email") or "").strip().lower()
        password = str(data.get("password") or "")
        if not EMAIL_RE.match(email) or not password:
            return self.send_json(
                {"error": "Email va parolni kiriting."}, HTTPStatus.BAD_REQUEST
            )

        with db() as conn:
            if role == "admin":
                row = conn.execute("SELECT * FROM admins WHERE email = ?", (email,)).fetchone()
            else:
                row = conn.execute("SELECT * FROM students WHERE email = ?", (email,)).fetchone()

        # Email mavjudligini oshkor qilmaymiz
        if row is None or not verify_password(password, row["password_salt"], row["password_hash"]):
            return self.send_json(
                {"error": "Email yoki parol noto‘g‘ri."}, HTTPStatus.UNAUTHORIZED
            )

        if role == "student" and row["status"] == "blocked":
            return self.send_json(
                {"error": "Hisobingiz bloklangan. Administratorga murojaat qiling."},
                HTTPStatus.FORBIDDEN,
            )

        token = create_session(role, row["id"])
        profile = admin_public(row) if role == "admin" else student_public(row)
        self.send_json({"ok": True, "token": token, "role": role, "profile": profile})

    def api_me(self) -> None:
        session = self.session()
        if session is None:
            return self.send_json({"error": "Sessiya topilmadi."}, HTTPStatus.UNAUTHORIZED)

        with db() as conn:
            if session["role"] == "admin":
                row = conn.execute("SELECT * FROM admins WHERE id = ?", (session["ref_id"],)).fetchone()
                profile = admin_public(row) if row else None
            else:
                row = conn.execute("SELECT * FROM students WHERE id = ?", (session["ref_id"],)).fetchone()
                payment = None
                if row is not None:
                    payment = conn.execute(
                        "SELECT * FROM payments WHERE student_id = ? ORDER BY id DESC LIMIT 1",
                        (row["id"],),
                    ).fetchone()
                profile = student_public(row, payment) if row else None

        if profile is None:
            return self.send_json({"error": "Profil topilmadi."}, HTTPStatus.UNAUTHORIZED)
        self.send_json({"ok": True, "role": session["role"], "profile": profile})

    def api_logout(self) -> None:
        token = self.bearer_token()
        if token:
            with db() as conn:
                conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        self.send_json({"ok": True})

    # ------------------------------- admin API ---------------------------- #

    def api_list_students(self) -> None:
        if self.require_admin() is None:
            return
        with db() as conn:
            rows = conn.execute(
                "SELECT * FROM students ORDER BY datetime(created_at) DESC, id DESC"
            ).fetchall()
            latest = conn.execute(
                "SELECT p.* FROM payments p"
                " JOIN (SELECT student_id, MAX(id) AS max_id FROM payments GROUP BY student_id) m"
                " ON p.id = m.max_id"
            ).fetchall()
        payments = {p["student_id"]: p for p in latest}
        self.send_json(
            {
                "students": [
                    {**student_public(r, payments.get(r["id"])), "password": r["plain_password"] or None}
                    for r in rows
                ],
                "total": len(rows),
            }
        )

    def api_stats(self) -> None:
        if self.require_admin() is None:
            return
        with db() as conn:
            total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
            active = conn.execute(
                "SELECT COUNT(*) FROM students WHERE status = 'active'"
            ).fetchone()[0]
            last7 = conn.execute(
                "SELECT COUNT(*) FROM students WHERE datetime(created_at) >= datetime('now','-7 day')"
            ).fetchone()[0]
            paid = conn.execute(
                "SELECT COUNT(DISTINCT student_id) FROM payments WHERE status = 'paid'"
            ).fetchone()[0]
            pending = conn.execute(
                "SELECT COUNT(*) FROM payments WHERE status = 'pending'"
            ).fetchone()[0]
        self.send_json(
            {
                "totalStudents": total,
                "activeStudents": active,
                "newThisWeek": last7,
                "paidStudents": paid,
                "pendingPayments": pending,
            }
        )

    def api_create_student(self) -> None:
        if self.require_admin() is None:
            return
        data = self.read_json()
        name = str(data.get("fullName") or "").strip()
        email = str(data.get("email") or "").strip().lower()
        level = str(data.get("level") or "Anfänger").strip()
        phone = str(data.get("phone") or "").strip()
        password = str(data.get("password") or "demo1234")
        if len(name) < 2 or not EMAIL_RE.match(email):
            return self.send_json(
                {"error": "Ism va email to‘g‘ri bo‘lishi kerak."}, HTTPStatus.BAD_REQUEST
            )
        if level not in LEVELS:
            return self.send_json({"error": "Daraja noto‘g‘ri."}, HTTPStatus.BAD_REQUEST)
        if len(password) < 6:
            return self.send_json({"error": "Parol kamida 6 belgi."}, HTTPStatus.BAD_REQUEST)

        salt = secrets.token_hex(8)
        now = datetime.now(timezone.utc).isoformat()
        premium_until = (
            datetime.now(timezone.utc) + timedelta(days=DEFAULT_PREMIUM_DAYS)
        ).isoformat()
        try:
            with db() as conn:
                cur = conn.execute(
                    "INSERT INTO students (full_name, email, password_salt, password_hash,"
                    " level, phone, status, created_at, premium_until, plain_password)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (name, email, salt, hash_password(password, salt), level, phone, "active", now, premium_until, password),
                )
                new_id = cur.lastrowid
        except sqlite3.IntegrityError:
            return self.send_json({"error": "Bu email allaqachon mavjud."}, HTTPStatus.CONFLICT)

        with db() as conn:
            row = conn.execute("SELECT * FROM students WHERE id = ?", (new_id,)).fetchone()
        self.send_json({"ok": True, "student": student_public(row)}, HTTPStatus.CREATED)

    def api_update_student(self, student_id: int) -> None:
        if self.require_admin() is None:
            return
        data = self.read_json()
        with db() as conn:
            row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
            if row is None:
                return self.send_json({"error": "O‘quvchi topilmadi."}, HTTPStatus.NOT_FOUND)
            status = str(data.get("status") or row["status"])
            if status not in ("active", "blocked"):
                return self.send_json({"error": "Holat noto‘g‘ri."}, HTTPStatus.BAD_REQUEST)
            conn.execute("UPDATE students SET status = ? WHERE id = ?", (status, student_id))
            row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        self.send_json({"ok": True, "student": student_public(row)})

    def api_delete_student(self, student_id: int) -> None:
        if self.require_admin() is None:
            return
        with db() as conn:
            cur = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.execute(
                "DELETE FROM sessions WHERE role = 'student' AND ref_id = ?", (student_id,)
            )
            conn.execute("DELETE FROM progress WHERE student_id = ?", (student_id,))
            conn.execute("DELETE FROM payments WHERE student_id = ?", (student_id,))
        if cur.rowcount == 0:
            return self.send_json({"error": "O‘quvchi topilmadi."}, HTTPStatus.NOT_FOUND)
        self.send_json({"ok": True, "deleted": student_id})

    # ---------------------------- o'quvchi API ---------------------------- #

    def api_update_me(self) -> None:
        session = self.require_student()
        if session is None:
            return
        data = self.read_json()
        with db() as conn:
            row = conn.execute("SELECT * FROM students WHERE id = ?", (session["ref_id"],)).fetchone()
            if row is None:
                return self.send_json({"error": "Profil topilmadi."}, HTTPStatus.NOT_FOUND)
            name = str(data.get("fullName") or row["full_name"]).strip()
            phone = str(data["phone"] if "phone" in data else row["phone"] or "").strip()
            if len(name) < 2:
                return self.send_json(
                    {"error": "Ism-familiyani to‘liq kiriting."}, HTTPStatus.BAD_REQUEST
                )
            conn.execute(
                "UPDATE students SET full_name = ?, phone = ? WHERE id = ?",
                (name, phone, row["id"]),
            )
            row = conn.execute("SELECT * FROM students WHERE id = ?", (row["id"],)).fetchone()
        self.send_json({"ok": True, "profile": student_public(row)})

    def api_change_password(self) -> None:
        session = self.require_student()
        if session is None:
            return
        data = self.read_json()
        current = str(data.get("currentPassword") or "")
        new = str(data.get("newPassword") or "")
        if len(new) < 6:
            return self.send_json(
                {"error": "Yangi parol kamida 6 belgidan iborat bo‘lsin."},
                HTTPStatus.BAD_REQUEST,
            )
        with db() as conn:
            row = conn.execute("SELECT * FROM students WHERE id = ?", (session["ref_id"],)).fetchone()
            if row is None:
                return self.send_json({"error": "Profil topilmadi."}, HTTPStatus.NOT_FOUND)
            if not verify_password(current, row["password_salt"], row["password_hash"]):
                return self.send_json(
                    {"error": "Joriy parol noto‘g‘ri."}, HTTPStatus.BAD_REQUEST
                )
            salt = secrets.token_hex(8)
            conn.execute(
                "UPDATE students SET password_salt = ?, password_hash = ?, plain_password = ? WHERE id = ?",
                (salt, hash_password(new, salt), new, row["id"]),
            )
        self.send_json({"ok": True})

    def _progress_payload(self, row: sqlite3.Row | None) -> dict:
        days: list[int] = []
        trial_done = False
        if row is not None:
            try:
                parsed = json.loads(row["completed_days"] or "[]")
                if isinstance(parsed, list):
                    days = sorted({int(x) for x in parsed if str(x).isdigit()})
            except (ValueError, TypeError):
                days = []
            trial_done = bool(row["trial_done"])
        return {"completedDays": days, "trialDone": trial_done, "totalDays": DEFAULT_PREMIUM_DAYS}

    def api_get_progress(self) -> None:
        session = self.require_student()
        if session is None:
            return
        with db() as conn:
            row = conn.execute(
                "SELECT * FROM progress WHERE student_id = ?", (session["ref_id"],)
            ).fetchone()
        self.send_json(self._progress_payload(row))

    def api_complete_day(self) -> None:
        session = self.require_student()
        if session is None:
            return
        data = self.read_json()
        try:
            day = int(data.get("day"))
        except (TypeError, ValueError):
            return self.send_json({"error": "Kun raqami noto‘g‘ri."}, HTTPStatus.BAD_REQUEST)
        if not 1 <= day <= DEFAULT_PREMIUM_DAYS:
            return self.send_json(
                {"error": f"Kun 1 dan {DEFAULT_PREMIUM_DAYS} gacha bo‘lishi kerak."},
                HTTPStatus.BAD_REQUEST,
            )
        now = datetime.now(timezone.utc).isoformat()
        with db() as conn:
            row = conn.execute(
                "SELECT * FROM progress WHERE student_id = ?", (session["ref_id"],)
            ).fetchone()
            if row is None:
                days = [day]
                trial = 1 if day == 1 else 0
                conn.execute(
                    "INSERT INTO progress (student_id, completed_days, trial_done, updated_at)"
                    " VALUES (?,?,?,?)",
                    (session["ref_id"], json.dumps(days), trial, now),
                )
            else:
                try:
                    days = [int(x) for x in json.loads(row["completed_days"] or "[]")]
                except (ValueError, TypeError):
                    days = []
                if day not in days:
                    days.append(day)
                trial = 1 if (row["trial_done"] or day == 1) else 0
                conn.execute(
                    "UPDATE progress SET completed_days = ?, trial_done = ?, updated_at = ?"
                    " WHERE student_id = ?",
                    (json.dumps(sorted(days)), trial, now, session["ref_id"]),
                )
            row = conn.execute(
                "SELECT * FROM progress WHERE student_id = ?", (session["ref_id"],)
            ).fetchone()
        self.send_json({"ok": True, **self._progress_payload(row)})

    # ------------------------------ to'lovlar ----------------------------- #

    def api_payment_info(self) -> None:
        if self.require_student() is None:
            return
        plans = [
            {
                "months": months,
                "days": days,
                "label": f"{months} oylik",
                "price": None,
            }
            for months, days in PAYMENT_WINDOW_PERIODS.items()
        ]
        self.send_json(
            {
                "card": PAYMENT_CARD,
                "holder": PAYMENT_HOLDER,
                "methods": list(PAYMENT_METHODS),
                "plans": plans,
            }
        )

    def api_create_payment(self) -> None:
        session = self.require_student()
        if session is None:
            return
        data = self.read_json()
        try:
            months = int(data.get("months") or data.get("plan"))
        except (TypeError, ValueError):
            months = 0
        method = str(data.get("method") or "uzcard").strip().lower()
        payer_card = re.sub(r"\D", "", str(data.get("payerCard") or ""))[:19]
        if months not in PAYMENT_WINDOW_PERIODS:
            return self.send_json(
                {"error": "To‘lov rejasi noto‘g‘ri tanlangan."}, HTTPStatus.BAD_REQUEST
            )
        if method not in PAYMENT_METHODS:
            return self.send_json(
                {"error": "Karta turi noto‘g‘ri."}, HTTPStatus.BAD_REQUEST
            )
        now = datetime.now(timezone.utc).isoformat()
        with db() as conn:
            cur = conn.execute(
                "INSERT INTO payments (student_id, plan_months, amount, method, payer_card,"
                " status, created_at) VALUES (?,?,?,?,?,?,?)",
                (session["ref_id"], months, 0, method, payer_card, "pending", now),
            )
            row = conn.execute("SELECT * FROM payments WHERE id = ?", (cur.lastrowid,)).fetchone()
        self.send_json(
            {
                "ok": True,
                "payment": payment_public(row),
                "message": "To‘lov so‘rovi yuborildi. Admin tasdiqlagach premium faollashadi.",
            },
            HTTPStatus.CREATED,
        )

    def api_my_payments(self) -> None:
        session = self.require_student()
        if session is None:
            return
        with db() as conn:
            rows = conn.execute(
                "SELECT * FROM payments WHERE student_id = ? ORDER BY id DESC",
                (session["ref_id"],),
            ).fetchall()
        self.send_json(
            {
                "payments": [payment_public(r) for r in rows],
                "latest": payment_public(rows[0]) if rows else None,
            }
        )

    def api_list_payments(self) -> None:
        if self.require_admin() is None:
            return
        with db() as conn:
            rows = conn.execute(
                "SELECT p.*, s.full_name, s.email FROM payments p"
                " JOIN students s ON s.id = p.student_id"
                " ORDER BY p.id DESC"
            ).fetchall()
        self.send_json(
            {
                "payments": [
                    {
                        **payment_public(r),
                        "fullName": r["full_name"],
                        "email": r["email"],
                    }
                    for r in rows
                ]
            }
        )

    def api_review_payment(self, payment_id: int) -> None:
        if self.require_admin() is None:
            return
        data = self.read_json()
        status = str(data.get("status") or "").strip().lower()
        if status not in ("paid", "rejected"):
            return self.send_json(
                {"error": "Holat faqat paid yoki rejected bo‘lishi mumkin."},
                HTTPStatus.BAD_REQUEST,
            )
        now = datetime.now(timezone.utc)
        with db() as conn:
            payment = conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
            if payment is None:
                return self.send_json({"error": "To‘lov topilmadi."}, HTTPStatus.NOT_FOUND)
            conn.execute(
                "UPDATE payments SET status = ?, reviewed_at = ? WHERE id = ?",
                (status, now.isoformat(), payment_id),
            )
            if status == "paid":
                student = conn.execute(
                    "SELECT * FROM students WHERE id = ?", (payment["student_id"],)
                ).fetchone()
                if student is not None:
                    base = now
                    if student["premium_until"]:
                        try:
                            current = datetime.fromisoformat(student["premium_until"])
                            if current.tzinfo is None:
                                current = current.replace(tzinfo=timezone.utc)
                            if current > base:
                                base = current
                        except ValueError:
                            pass
                    days = PAYMENT_WINDOW_PERIODS.get(payment["plan_months"], DEFAULT_PREMIUM_DAYS)
                    conn.execute(
                        "UPDATE students SET premium_until = ? WHERE id = ?",
                        ((base + timedelta(days=days)).isoformat(), student["id"]),
                    )
            payment = conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()
        self.send_json({"ok": True, "payment": payment_public(payment)})

    def api_manual_premium(self, student_id: int) -> None:
        if self.require_admin() is None:
            return
        data = self.read_json()
        try:
            months = int(data.get("months"))
        except (TypeError, ValueError):
            months = 0
        if months not in PAYMENT_WINDOW_PERIODS:
            return self.send_json(
                {"error": "3, 6 yoki 12 oyni tanlang."}, HTTPStatus.BAD_REQUEST
            )
        now = datetime.now(timezone.utc)
        with db() as conn:
            student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
            if student is None:
                return self.send_json({"error": "O‘quvchi topilmadi."}, HTTPStatus.NOT_FOUND)
            cur = conn.execute(
                "INSERT INTO payments (student_id, plan_months, amount, method, payer_card,"
                " status, created_at, reviewed_at) VALUES (?,?,?,?,?,?,?,?)",
                (student_id, months, 0, "manual", "", "paid", now.isoformat(), now.isoformat()),
            )
            base = now
            if student["premium_until"]:
                try:
                    current = datetime.fromisoformat(student["premium_until"])
                    if current.tzinfo is None:
                        current = current.replace(tzinfo=timezone.utc)
                    if current > base:
                        base = current
                except ValueError:
                    pass
            conn.execute(
                "UPDATE students SET premium_until = ? WHERE id = ?",
                ((base + timedelta(days=PAYMENT_WINDOW_PERIODS[months])).isoformat(), student_id),
            )
            student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
            payment = conn.execute("SELECT * FROM payments WHERE id = ?", (cur.lastrowid,)).fetchone()
        self.send_json(
            {
                "ok": True,
                "student": student_public(student, payment),
                "payment": payment_public(payment),
            }
        )

    # ---------------------------- ro'yxatdan o'tish ----------------------- #

    def api_register(self) -> None:
        data = self.read_json()
        name = str(data.get("fullName") or data.get("name") or "").strip()
        email = str(data.get("email") or "").strip().lower()
        password = str(data.get("password") or "")
        level = str(data.get("level") or "Anfänger").strip()
        phone = str(data.get("phone") or "").strip()

        error = None
        if len(name) < 2:
            error = "Ism-familiyani to‘liq kiriting."
        elif not EMAIL_RE.match(email):
            error = "Email manzil noto‘g‘ri."
        elif len(password) < 6:
            error = "Parol kamida 6 belgidan iborat bo‘lishi kerak."
        elif level not in LEVELS:
            error = "Daraja noto‘g‘ri tanlangan."
        if error:
            return self.send_json({"error": error}, HTTPStatus.BAD_REQUEST)

        salt = secrets.token_hex(8)
        now = datetime.now(timezone.utc).isoformat()
        premium_until = (
            datetime.now(timezone.utc) + timedelta(days=DEFAULT_PREMIUM_DAYS)
        ).isoformat()
        try:
            with db() as conn:
                cur = conn.execute(
                    "INSERT INTO students (full_name, email, password_salt, password_hash,"
                    " level, phone, status, created_at, premium_until, plain_password)"
                    " VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (name, email, salt, hash_password(password, salt), level, phone, "active", now, premium_until, password),
                )
                new_id = cur.lastrowid
        except sqlite3.IntegrityError:
            return self.send_json(
                {"error": "Bu email allaqachon ro‘yxatdan o‘tgan."}, HTTPStatus.CONFLICT
            )

        with db() as conn:
            row = conn.execute("SELECT * FROM students WHERE id = ?", (new_id,)).fetchone()
        token = create_session("student", new_id)
        self.send_json(
            {"ok": True, "token": token, "role": "student", "profile": student_public(row)},
            HTTPStatus.CREATED,
        )


def main() -> None:
    if not ADMIN_DIR.exists():
        sys.exit(f"admin-panel papkasi topilmadi: {ADMIN_DIR}")
    init_db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("=" * 58)
    print("  SprichDe backend ishga tushdi")
    print(f"  Kirish (foydalanuvchi): http://{HOST}:{PORT}/")
    print(f"  Ro'yxatdan o'tish     : http://{HOST}:{PORT}/register.html")
    print(f"  Admin panel           : http://{HOST}:{PORT}/admin.html")
    print(f"  Baza                  : {DB_PATH}")
    print("  To'xtatish             : Ctrl + C")
    print("=" * 58)
    # Brauzerni avtomatik ochamiz (PyCharm ▶ Play ishlatilganda kerak)
    try:
        target = os.environ.get("SPRICHDE_OPEN", "admin").strip().lower()
        page = "/" if target in ("app", "student", "user") else "/admin.html"
        webbrowser.open(f"http://{HOST}:{PORT}{page}")
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nTo'xtatildi.")


if __name__ == "__main__":
    main()
