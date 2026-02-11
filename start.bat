@echo off
echo ====================================
echo   Starting PriceNexus Application
echo ====================================
echo.

echo [1/4] Checking MongoDB...
net start MongoDB 2>nul
if %errorlevel% equ 0 (
    echo ✓ MongoDB started successfully
) else (
    echo ! MongoDB already running or failed to start
    echo   Make sure MongoDB is installed
)
echo.

echo [2/4] Starting Backend Server...
start "PriceNexus Backend" cmd /k "cd /d %~dp0backend && echo Starting FastAPI server... && python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000"
timeout /t 5 /nobreak >nul
echo ✓ Backend started at http://localhost:8000
echo.

echo [3/4] Installing Frontend Dependencies (if needed)...
cd /d %~dp0frontend
if not exist "node_modules\" (
    echo   Installing npm packages...
    call npm install
) else (
    echo ✓ Dependencies already installed
)
echo.

echo [4/4] Starting Frontend...
echo ✓ Frontend starting at http://localhost:3000
echo.
echo ====================================
echo   Application Ready!
echo ====================================
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ====================================
echo.

start "PriceNexus Frontend" cmd /k "cd /d %~dp0frontend && npm start"

echo.
echo Press any key to stop all servers...
pause >nul

echo.
echo Stopping servers...
taskkill /FI "WindowTitle eq PriceNexus*" /F
echo Done!
