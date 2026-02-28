@echo off
REM Quick start script for Voice Assistant (Windows)
REM This script sets up and runs both frontend and backend

echo.
echo ========================================
echo Voice Assistant - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Please install Node.js 18+
    exit /b 1
)

REM Setup Backend
echo.
echo [1/4] Setting up backend...
cd backend

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

if not exist ..\.env (
    echo.
    echo ERROR: .env file not found in project root
    echo Please copy .env.example to .env and configure it
    echo.
    pause
    exit /b 1
)

REM Start Backend in new window
echo Starting backend...
start "Voice Assistant Backend" cmd /k "cd /d %cd% && python -m uvicorn src.main:app --reload --port 8000"
timeout /t 3 /nobreak

cd ..

REM Setup Frontend
echo.
echo [2/4] Setting up frontend...
cd frontend-next

echo Installing dependencies...
call npm install

if not exist .env.local (
    echo Creating .env.local...
    (
        echo NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws/voice
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
    ) > .env.local
)

REM Start Frontend in new window
echo Starting frontend...
start "Voice Assistant Frontend" cmd /k "cd /d %cd% && npm run dev"

cd ..

REM All done
echo.
echo ========================================
echo ✅ Setup complete!
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit this window...
echo ========================================
pause
