# Script to launch all 3 components of the Haptic-Q System

Write-Host "Starting Haptic-Q System..." -ForegroundColor Cyan

# 1. Start the FastAPI Dashboard
Write-Host "1. Launching Dashboard (FastAPI)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/c title Dashboard & uvicorn dashboard.main:app --host 127.0.0.1 --port 8000"

# Wait a moment for server to initialize
Start-Sleep -Seconds 2

# 2. Start the Surgeon Console (UI)
Write-Host "2. Launching Surgeon Console..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/c title Surgeon Console & python surgeon_console.py"

# Wait a moment for network sockets to open
Start-Sleep -Seconds 2

# 3. Start the Robot Feedback Sync
Write-Host "3. Launching Robot Feedback Sync..." -ForegroundColor Magenta
Start-Process cmd -ArgumentList "/c title Robot Feedback Sync & python feedback_sync.py"

Write-Host "All systems launched successfully!" -ForegroundColor Cyan
Write-Host "You can view the dashboard at: http://127.0.0.1:8000" -ForegroundColor White
