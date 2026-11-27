@echo off
rem Builds dist\mtklogo_v1.5.exe (single file). Needs Python 3.9+, internet and windows\bin\mtklogo.exe
setlocal
cd /d "%~dp0\.."
if not exist windows\bin\mtklogo.exe ( echo Missing windows\bin\mtklogo.exe - see windows\README_WINDOWS.md & exit /b 1 )
if not exist .venv\Scripts\activate.bat ( py -3 -m venv .venv || exit /b 1 )
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip PySide6-Essentials pyinstaller || exit /b 1
python windows\assemble_bundle.py --engine windows\bin\mtklogo.exe || exit /b 1
python windows\prep_git.py || exit /b 1
pyinstaller --noconfirm --clean windows\mtklogo_v1.5.spec || exit /b 1
echo DONE: dist\mtklogo_v1.5.exe
