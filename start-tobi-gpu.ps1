# Start Tobi with GPU acceleration
Write-Host "Starting Tobi's Restaurant with GPU acceleration..." -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "Working in: $scriptPath" -ForegroundColor Yellow

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check for NVIDIA Docker support
Write-Host "Checking NVIDIA Docker support..." -ForegroundColor Yellow
$hasNvidiaDocker = docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi 2>&1 | Select-String "NVIDIA-SMI"
if (-not $hasNvidiaDocker) {
    Write-Host "WARNING: NVIDIA Docker support not detected. Install NVIDIA Container Toolkit:" -ForegroundColor Yellow
    Write-Host "  https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Falling back to CPU-only mode..." -ForegroundColor Yellow
    & "$scriptPath\start-tobi.ps1"
    exit
}

Write-Host "GPU support detected!" -ForegroundColor Green

# Stop any existing containers on port 8000
Write-Host "Stopping any existing containers..." -ForegroundColor Yellow
docker ps -a --filter "publish=8000" -q | ForEach-Object { docker stop $_ 2>&1 | Out-Null }

# Build the GPU-enabled image
Write-Host "Building Tobi's Restaurant API (GPU-enabled)..." -ForegroundColor Yellow
docker build -f Dockerfile.gpu -t tobi-restaurant-gpu .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed. Check your code for errors." -ForegroundColor Red
    exit 1
}

# Start container with GPU support
$timestamp = Get-Date -Format "MMdd-HHmm"
$containerName = "tobi-gpu-$timestamp"

Write-Host "Starting Tobi's API container (GPU-accelerated)..." -ForegroundColor Yellow
docker run -d `
    --gpus all `
    -p 8000:8000 `
    -v "${scriptPath}/models:/app/models" `
    --name $containerName `
    tobi-restaurant-gpu

# Wait for server to be ready
Write-Host "Waiting for Tobi to wake up..." -ForegroundColor Yellow
$maxAttempts = 60
$attempt = 0
while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 1 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "Tobi is ready! 🏄‍♂️" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "." -NoNewline
        Start-Sleep -Seconds 1
        $attempt++
    }
}

if ($attempt -ge $maxAttempts) {
    Write-Host ""
    Write-Host "ERROR: Tobi failed to start within 60 seconds." -ForegroundColor Red
    Write-Host "Check container logs:" -ForegroundColor Yellow
    docker logs $containerName
    exit 1
}

Write-Host ""
Write-Host "Opening chat interface..." -ForegroundColor Green
Start-Process "$scriptPath\restaurant_chat.html"

Write-Host ""
Write-Host "Tobi is running with GPU acceleration! 🚀" -ForegroundColor Green
Write-Host "API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Container: $containerName" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop streaming logs" -ForegroundColor Yellow
docker logs -f $containerName
