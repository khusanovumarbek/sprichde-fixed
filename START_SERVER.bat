@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo SprichDe backend ishga tushirilmoqda...
where py >nul 2>nul && (py -3 backend\server.py) || (python backend\server.py)
pause
