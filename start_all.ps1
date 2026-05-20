# Start both SmartID backend (FastAPI) and frontend (Streamlit)
Write-Host "Starting SmartID (API + UI)..." -ForegroundColor Green

# Set PYTHONPATH for src package
$env:PYTHONPATH = "$PWD\src"
Write-Host "Set PYTHONPATH to: $env:PYTHONPATH" -ForegroundColor Yellow

# Set Tesseract path (Windows default)
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    $env:TESSERACT_CMD = $tesseractPath
    Write-Host "Set TESSERACT_CMD to: $tesseractPath" -ForegroundColor Yellow
} else {
    Write-Host "Warning: Tesseract not found at default location. OCR may not work." -ForegroundColor Red
    Write-Host "Run install_tesseract.ps1 first to install Tesseract." -ForegroundColor Yellow
}

# Activate venv if present (helps ensure uvicorn/streamlit are available)
$venvActivate = Join-Path $PWD ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    . $venvActivate
    Write-Host "Activated virtual environment: .venv" -ForegroundColor Yellow
}

# Start backend in a new PowerShell window
Write-Host "Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd `"$PWD`"; `$env:PYTHONPATH=`"$env:PYTHONPATH`"; `$env:TESSERACT_CMD=`"$env:TESSERACT_CMD`"; python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"
)

# Start frontend in this window
Write-Host "Starting Streamlit UI on http://localhost:8501 ..." -ForegroundColor Green
python -m streamlit run frontend/app.py --server.port 8501

