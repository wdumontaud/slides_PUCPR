@echo off
rem Rebuilds only main.html from the sources in this folder
rem   main.html  working copy (pictures and videos are read from assets\)
setlocal
cd /d "%~dp0"

set "PY=python"
python -c "import sys" >nul 2>nul || set "PY=py -3"

echo [1/2] Check Python packages (playwright)
%PY% -c "import playwright" >nul 2>nul || %PY% -m pip install --quiet playwright || goto :fail

echo [2/2] main.html
%PY% config\build.py || goto :fail

echo.
echo Done: main.html
pause
exit /b 0

:fail
echo.
echo *** Failed: read the message above. ***
pause
exit /b 1