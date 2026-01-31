# Run the Movie Argument Engine frontend
# Usage: .\scripts\run_frontend.ps1

Write-Host "Movie Argument Engine - Frontend" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

Set-Location frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Run the dev server
Write-Host ""
Write-Host "Starting Vite dev server..." -ForegroundColor Green
Write-Host "Frontend available at: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

npm run dev
