"""
SprichDe — admin panelni ishga tushirish (REAL backend bilan).

Ishlatish (PyCharm ▶ yoki terminal):
    python run_admin.py

Bu backend/server.py ni ishga tushiradi (SQLite + API).
To'xtatish: Ctrl+C yoki PyCharm'dagi qizil ⏹ tugma
"""

import os
import runpy
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

# Admin sahifasini ochish uchun backend o'zini ishga tushiradi (8000-port).
# Agar brauzer admin.html ochilishini xohlasangiz, SPRICHDE_OPEN=admin qiling.
os.environ.setdefault("SPRICHDE_OPEN", "admin")
runpy.run_path(os.path.join(ROOT, "backend", "server.py"), run_name="__main__")
