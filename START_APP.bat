@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo SprichDe ilovasi (backend bilan) ishga tushirilmoqda...
where py >nul 2>nul && (py -3 run_app.py) || (python run_app.py)
pause
