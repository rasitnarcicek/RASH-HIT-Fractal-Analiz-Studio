@echo off
chcp 65001 >nul
title RASH-HIT Fractal Studio - System Launcher
cd /d "%~dp0"

:: Auto-create virtual environment if none exists
if not exist ".venv\Scripts\activate.bat" (
    if not exist "venv\Scripts\activate.bat" (
        echo [INFO] Virtual environment not found. Creating .venv and installing requirements...
        python -m venv .venv
        if not errorlevel 1 (
            call ".venv\Scripts\activate.bat"
            python -m pip install --upgrade pip
            python -m pip install -r requirements.txt
        )
    )
)

:: Check and activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    set "PYCMD=python"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    set "PYCMD=python"
) else (
    set "PYCMD=python"
)

%PYCMD% launcher.py
if errorlevel 1 (
    echo.
    echo [ERROR] RASH-HIT launcher failed to start.
    echo         Make sure the dependencies are installed, then run:
    echo         start.bat  (or: python launcher.py)
    echo.
)
pause