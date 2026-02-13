# Ollama Setup Script for ScaleGuard JARVIS Integration

Write-Host "Setting up Ollama for ScaleGuard JARVIS..." -ForegroundColor Green

# Check if Ollama is installed
$ollamaPath = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollamaPath) {
    Write-Host "Ollama not found. Installing..." -ForegroundColor Yellow
    
    # Download and install Ollama
    $url = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"
    $downloadPath = "$env:TEMP\ollama-windows-amd64.zip"
    $extractPath = "$env:LOCALAPPDATA\Programs\Ollama"
    
    Write-Host "Downloading Ollama..."
    Invoke-WebRequest -Uri $url -OutFile $downloadPath
    
    Write-Host "Extracting to $extractPath..."
    if (Test-Path $extractPath) {
        Remove-Item $extractPath -Recurse -Force
    }
    Expand-Archive -Path $downloadPath -DestinationPath $extractPath
    
    # Add to PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$extractPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$userPath;$extractPath", "User")
        $env:Path += ";$extractPath"
    }
    
    Write-Host "Ollama installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Ollama already installed at: $($ollamaPath.Source)" -ForegroundColor Green
}

# Start Ollama service in background
Write-Host "Starting Ollama service..." -ForegroundColor Yellow
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

Start-Sleep 3

# Install recommended model for ScaleGuard
Write-Host "Installing Llama2 7B model (recommended for ScaleGuard)..." -ForegroundColor Yellow
ollama pull llama2:7b

Write-Host "Setup complete! Ollama is ready for ScaleGuard JARVIS integration." -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  ollama list          - Show installed models"
Write-Host "  ollama run llama2:7b - Test the model"
Write-Host "  ollama serve         - Start Ollama service"
Write-Host ""
Write-Host "ScaleGuard will automatically use Ollama via JARVIS provider." -ForegroundColor Green