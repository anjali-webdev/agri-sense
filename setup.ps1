# AgriSense AI Setup Script
Write-Host "==================================" -ForegroundColor Green
Write-Host "  AgriSense AI - Setup" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Cyan
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
}

if (-not $pythonCmd) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from python.org" -ForegroundColor Yellow
    exit 1
}

$version = & $pythonCmd --version
Write-Host "Found: $version" -ForegroundColor Green
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Cyan
& $pythonCmd -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    exit 1
}
Write-Host "Virtual environment created" -ForegroundColor Green
Write-Host ""

# Activate and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed" -ForegroundColor Green
Write-Host ""

# Train model
Write-Host "Training machine learning model..." -ForegroundColor Cyan
& $pythonCmd scripts\train_model.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Model training failed" -ForegroundColor Yellow
} else {
    Write-Host "Model trained successfully" -ForegroundColor Green
}
Write-Host ""

Write-Host "==================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Cyan
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "  streamlit run app.py" -ForegroundColor Yellow
Write-Host ""
