# validate-submission.ps1 — Smart Customer Support Environment Validator
#
# Checks that your HF Space is live, Docker image builds, and openenv validate passes.
#
# Prerequisites:
#   - Docker:       https://docs.docker.com/get-docker/
#   - openenv-core: pip install openenv-core
#   - curl (usually pre-installed)
#
# Run:
#   .\validate-submission.ps1 -PingUrl "https://your-space.hf.space"
#
# Arguments:
#   PingUrl   Your HuggingFace Space URL (e.g. https://your-space.hf.space)
#
# Examples:
#   .\validate-submission.ps1 -PingUrl "https://my-support-env.hf.space"

param(
    [Parameter(Mandatory=$true)]
    [string]$PingUrl
)

$ErrorActionPreference = "Stop"

# Color functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$ForegroundColor = "White"
    )
    Write-Host $Message -ForegroundColor $ForegroundColor
}

function Write-Success($Message) {
    Write-ColorOutput Green "PASSED -- $Message"
    $global:PassCount++
}

function Write-Failure($Message) {
    Write-ColorOutput Red "FAILED -- $Message"
}

function Write-Hint($Message) {
    Write-ColorOutput Yellow "  Hint: $Message"
}

function Write-Step($Message) {
    Write-Host ""
    Write-ColorOutput Cyan "Step $StepCounter/3: $Message"
    $StepCounter++
}

# Initialize counters
$StepCounter = 1
$PassCount = 0
$PingUrl = $PingUrl.TrimEnd('/')

Write-Host ""
Write-Host "========================================" -ForegroundColor White
Write-Host "  Smart Customer Support Environment" -ForegroundColor White
Write-Host "  OpenEnv Submission Validator" -ForegroundColor White
Write-Host "========================================" -ForegroundColor White
Write-Host "Ping URL: $PingUrl" -ForegroundColor White
Write-Host ""

# Step 1: Ping HF Space
Write-Step "Pinging HF Space ($PingUrl/reset)..."

try {
    $response = Invoke-RestMethod -Uri "$PingUrl/reset" -Method POST -ContentType "application/json" -Body "{}" -TimeoutSec 30
    $httpCode = $response.StatusCode
    
    if ($httpCode -eq 200) {
        Write-Success "HF Space is live and responds to /reset"
    } else {
        Write-Failure "HF Space /reset returned HTTP $httpCode (expected 200)"
        Write-Hint "Make sure your Space is running and URL is correct."
        Write-Hint "Try opening $PingUrl in your browser first."
        exit 1
    }
} catch {
    Write-Failure "HF Space not reachable (connection failed or timed out)"
    Write-Hint "Check your network connection and that the Space is running."
    Write-Hint "Try: curl -s -o /dev/null -w '%{http_code}' -X POST $PingUrl/reset"
    exit 1
}

# Step 2: Check Docker build
Write-Step "Running docker build..."

if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Failure "docker command not found"
    Write-Hint "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
}

if (Test-Path "Dockerfile") {
    $dockerContext = "."
} elseif (Test-Path "envs/support_env/server/Dockerfile") {
    $dockerContext = "envs/support_env/server"
} else {
    Write-Failure "No Dockerfile found in repo root or envs/support_env/server/ directory"
    exit 1
}

Write-Host "  Found Dockerfile in $dockerContext" -ForegroundColor Gray

$buildOk = $false
$buildOutput = ""
try {
    $buildOutput = docker build $dockerContext 2>&1
    if ($LASTEXITCODE -eq 0) {
        $buildOk = $true
    }
} catch {
    $buildOutput = $_.Exception.Message
}

if ($buildOk) {
    Write-Success "Docker build succeeded"
} else {
    Write-Failure "Docker build failed"
    if ($buildOutput) {
        Write-Host "Build output:" -ForegroundColor Gray
        Write-Host ($buildOutput | Select-Object -Last 20) -ForegroundColor Gray
    }
    exit 1
}

# Step 3: Run openenv validate
Write-Step "Running openenv validate..."

if (!(Get-Command openenv -ErrorAction SilentlyContinue)) {
    Write-Failure "openenv command not found"
    Write-Hint "Install it: pip install openenv-core"
    exit 1
}

$validateOk = $false
$validateOutput = ""
try {
    $validateOutput = openenv validate 2>&1
    if ($LASTEXITCODE -eq 0) {
        $validateOk = $true
    }
} catch {
    $validateOutput = $_.Exception.Message
}

if ($validateOk) {
    Write-Success "openenv validate passed"
    if ($validateOutput) {
        Write-Host "  $validateOutput" -ForegroundColor Gray
    }
} else {
    Write-Failure "openenv validate failed"
    if ($validateOutput) {
        Write-Host $validateOutput -ForegroundColor Gray
    }
    exit 1
}

# Final results
Write-Host ""
Write-Host "========================================" -ForegroundColor White
Write-Host " All 3/3 checks passed!" -ForegroundColor Green
Write-Host " Your Smart Customer Support Environment is ready to submit." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor White
Write-Host ""

exit 0
