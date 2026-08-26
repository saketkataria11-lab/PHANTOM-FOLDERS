@echo off
echo ========================================
echo   PHANTOM FOLDERS - Encrypted Vault
echo ========================================
echo.

REM Try python from PATH
where python >nul 2>nul
if %ERRORLEVEL% == 0 (
    python main.py %*
    exit /b
)

REM Try py launcher
where py >nul 2>nul
if %ERRORLEVEL% == 0 (
    py main.py %*
    exit /b
)

REM Try common venv locations
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe main.py %*
    exit /b
)

if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe main.py %*
    exit /b
)

echo [ERROR] Python not found. Please install Python 3.10+ and add it to PATH.
echo         https://www.python.org/downloads/
pause
