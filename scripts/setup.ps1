# Full setup script for Movie Argument Engine
# Usage: .\scripts\setup.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Movie Argument Engine - Setup        " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
    Write-Host "  Please install Python 3.10+ from https://python.org" -ForegroundColor Yellow
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  Found: Node.js $nodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Node.js not found!" -ForegroundColor Red
    Write-Host "  Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Setting up Backend..." -ForegroundColor Cyan
Write-Host "---------------------" -ForegroundColor Cyan

# Create virtual environment
$venvPath = "backend\venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
}

# Activate and install
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"
pip install -r backend\requirements.txt --quiet

# Create .env file if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "  NOTE: Please edit backend\.env and add your TMDB API key" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Setting up Frontend..." -ForegroundColor Cyan
Write-Host "----------------------" -ForegroundColor Cyan

Set-Location frontend
Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
npm install --silent
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!                      " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Get a free TMDB API key from: https://www.themoviedb.org/settings/api" -ForegroundColor White
Write-Host "  2. Edit backend\.env and add your API key" -ForegroundColor White
Write-Host "  3. Run the backend:  .\scripts\run_backend.ps1" -ForegroundColor White
Write-Host "  4. Run the frontend: .\scripts\run_frontend.ps1" -ForegroundColor White
Write-Host ""
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Gray
Write-Host ""
