# Run the Movie Argument Engine backend
# Usage: .\scripts\run_backend.ps1

Write-Host "Movie Argument Engine - Backend" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if virtual environment exists
$venvPath = "backend\venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r backend\requirements.txt

# Check for TMDB API key
if (-not $env:TMDB_API_KEY) {
    Write-Host ""
    Write-Host "WARNING: TMDB_API_KEY not set!" -ForegroundColor Red
    Write-Host "Get your free API key at: https://www.themoviedb.org/settings/api" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Set it with: `$env:TMDB_API_KEY = 'your_api_key'" -ForegroundColor Yellow
    Write-Host ""
}

# Run the server
Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "API docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

Set-Location backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
