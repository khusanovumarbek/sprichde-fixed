"""
SprichDe — o'quvchi ilovasini ishga tushirish (REAL backend bilan).

Ishlatish (PyCharm ▶ yoki terminal):
    python run_app.py

Bu backend/server.py ni ishga tushiradi (SQLite + API).
O'quvchi kirishi: http://localhost:8000/
Admin panel:      http://localhost:8000/admin.html
To'xtatish: Ctrl+C yoki PyCharm'dagi qizil ⏹ tugma
"""

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

os.environ.setdefault("SPRICHDE_OPEN", "app")
runpy.run_path(os.path.join(ROOT, "backend", "server.py"), run_name="__main__")
