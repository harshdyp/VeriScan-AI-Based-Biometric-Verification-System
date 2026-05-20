# Start SmartID Application with proper environment setup
Write-Host "Starting SmartID Application..." -ForegroundColor Green

# Set PYTHONPATH for src package
$env:PYTHONPATH = "$PWD\src"
Write-Host "Set PYTHONPATH to: $env:PYTHONPATH" -ForegroundColor Yellow

# Set Tesseract path
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    $env:TESSERACT_CMD = $tesseractPath
    Write-Host "Set TESSERACT_CMD to: $tesseractPath" -ForegroundColor Yellow
} else {
    Write-Host "Warning: Tesseract not found at default location. OCR may not work." -ForegroundColor Red
    Write-Host "Run install_tesseract.ps1 first to install Tesseract." -ForegroundColor Yellow
}

# Start the backend server
Write-Host "Starting FastAPI backend on http://localhost:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
