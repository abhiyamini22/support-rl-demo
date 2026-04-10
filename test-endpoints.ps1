# Simple endpoint test for OpenEnv validation

param(
    [Parameter(Mandatory=$true)]
    [string]$PingUrl
)

$PingUrl = $PingUrl.TrimEnd('/')

Write-Host "Testing OpenEnv endpoints at: $PingUrl" -ForegroundColor Cyan
Write-Host ""

# Test 1: Reset endpoint
Write-Host "Testing /reset endpoint..." -ForegroundColor Yellow
try {
    $resetResponse = Invoke-RestMethod -Uri "$PingUrl/reset" -Method POST -ContentType "application/json" -Body "{}" -TimeoutSec 10
    Write-Host "✅ Reset endpoint: HTTP $($resetResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($resetResponse.Content | ConvertFrom-Json | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Reset endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 2: Health endpoint
Write-Host "Testing /health endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "$PingUrl/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Health endpoint: HTTP $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($healthResponse.Content | ConvertFrom-Json | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Health endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test 3: State endpoint
Write-Host "Testing /state endpoint..." -ForegroundColor Yellow
try {
    $stateResponse = Invoke-RestMethod -Uri "$PingUrl/state" -Method GET -TimeoutSec 10
    Write-Host "✅ State endpoint: HTTP $($stateResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($stateResponse.Content | ConvertFrom-Json | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "❌ State endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Test completed. Check results above." -ForegroundColor Cyan
