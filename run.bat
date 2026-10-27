@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title CropGuard - AI Crop Disease & Outbreak Prevention System
cd /d "%~dp0"
:: Load GEMINI_API_KEY from .env if not already exported
if "%GEMINI_API_KEY%"=="" (
    if exist ".env" (
        for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
            if "%%A"=="GEMINI_API_KEY" set "GEMINI_API_KEY=%%B"
        )
    )
)

echo =================================================================
echo   CropGuard: AI Crop Disease & Outbreak Prevention System
echo   Prototype v0.2 Working Model
echo =================================================================
echo.

:: Detect which Python installation has FastAPI
set "PY_CMD=python"
python -c "import fastapi" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "C:\Users\ASUS\anaconda3\python.exe" (
        set "PY_CMD=C:\Users\ASUS\anaconda3\python.exe"
    )
)

echo   Using Python: %PY_CMD%
echo   Starting server on: http://127.0.0.1:8000
echo   API Documentation:  http://127.0.0.1:8000/docs
echo.
echo   Opening web app in your default browser...
echo   (Press Ctrl+C in this window to stop the server)
echo =================================================================
echo.

:: Automatically open default browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

:: Start the Python backend server
"%PY_CMD%" run.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] CropGuard server exited with code %ERRORLEVEL%.
    pause
)
