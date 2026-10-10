@echo off
rem Rebuilds the three files of the talk from the sources in this folder:
rem   main.html         working copy (pictures and videos are read from assets\)
rem   main_export.html  one self-contained file: copy it to a USB key or send it, it works offline
rem   main.pdf          one page per step, videos shown as still frames
setlocal
cd /d "%~dp0"

set "PY=python"
python -c "import sys" >nul 2>nul || set "PY=py -3"

echo [1/4] Python packages (playwright, pypdf)
%PY% -c "import playwright, pypdf" >nul 2>nul || %PY% -m pip install --quiet playwright pypdf || goto :fail

echo [2/4] main.html
%PY% config\build.py || goto :fail

echo [3/4] main_export.html
%PY% config\build.py --standalone || goto :fail

echo [4/4] main.pdf (about a minute)
%PY% config\export_pdf.py || goto :fail

echo.
echo Done: main.html, main_export.html, main.pdf
pause
exit /b 0

:fail
echo.
echo *** Failed: read the message above. ***
pause
exit /b 1
