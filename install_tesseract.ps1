# Install Tesseract OCR and set up environment
Write-Host "Installing Tesseract OCR..." -ForegroundColor Green

# Check if already installed
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    Write-Host "Tesseract already installed at: $tesseractPath" -ForegroundColor Yellow
} else {
    # Install Tesseract silently
    Write-Host "Running Tesseract installer..." -ForegroundColor Yellow
    Start-Process -FilePath ".\tesseract-ocr-w64-setup-5.5.0.20241111.exe" -ArgumentList "/S" -Wait
    Write-Host "Tesseract installation completed!" -ForegroundColor Green
}

# Add to PATH if not already there
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$tesseractDir = "C:\Program Files\Tesseract-OCR"
if ($currentPath -notlike "*$tesseractDir*") {
    Write-Host "Adding Tesseract to PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$tesseractDir", "User")
    Write-Host "Tesseract added to PATH!" -ForegroundColor Green
}

# Set environment variable for the current session
$env:TESSERACT_CMD = $tesseractPath
Write-Host "Set TESSERACT_CMD environment variable" -ForegroundColor Green

# Test installation
Write-Host "Testing Tesseract installation..." -ForegroundColor Yellow
try {
    & $tesseractPath --version
    Write-Host "Tesseract is working correctly!" -ForegroundColor Green
} catch {
    Write-Host "Error testing Tesseract: $_" -ForegroundColor Red
}

Write-Host "Setup complete! You can now run your SmartID application." -ForegroundColor Green
