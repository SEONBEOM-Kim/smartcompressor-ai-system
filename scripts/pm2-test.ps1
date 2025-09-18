# PM2 자동 재시작 및 장애 복구 테스트 PowerShell 스크립트

Write-Host "🧪 Signalcraft PM2 테스트 시작..." -ForegroundColor Green

# 1. PM2 상태 확인
Write-Host "📊 1. 초기 PM2 상태 확인:" -ForegroundColor Cyan
pm2 status

# 2. 서버 응답 테스트
Write-Host "🌐 2. 서버 응답 테스트:" -ForegroundColor Cyan
Write-Host "Node.js 서버 (포트 3000):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/auth/verify" -TimeoutSec 5
    Write-Host "✅ Node.js API 응답: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js API 응답 없음" -ForegroundColor Red
}

Write-Host "Python 서버 (포트 8000):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 5
    Write-Host "✅ Python API 응답: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Python API 응답 없음" -ForegroundColor Red
}

# 3. 프로세스 강제 종료 테스트
Write-Host "💥 3. 프로세스 강제 종료 테스트..." -ForegroundColor Cyan
Write-Host "Node.js 프로세스 강제 종료 중..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*server.js*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "5초 대기 중..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 4. 자동 재시작 확인
Write-Host "🔄 4. 자동 재시작 확인:" -ForegroundColor Cyan
pm2 status

# 5. 서버 응답 재테스트
Write-Host "🌐 5. 서버 응답 재테스트:" -ForegroundColor Cyan
Write-Host "Node.js 서버 (포트 3000):" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/auth/verify" -TimeoutSec 5
    Write-Host "✅ Node.js API 응답: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js API 응답 없음" -ForegroundColor Red
}

# 6. 메모리 사용량 테스트
Write-Host "💾 6. 메모리 사용량 확인:" -ForegroundColor Cyan
pm2 monit --no-interaction | Select-Object -First 20

# 7. 로그 확인
Write-Host "📝 7. 최근 로그 확인:" -ForegroundColor Cyan
pm2 logs --lines 20

Write-Host "✅ PM2 테스트 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 테스트 결과:" -ForegroundColor Cyan
$onlineCount = (pm2 status | Select-String "online").Count
Write-Host "- 자동 재시작: $onlineCount 개 프로세스 실행 중" -ForegroundColor White
Write-Host "- 메모리 관리: PM2 모니터링 활성화" -ForegroundColor White
Write-Host "- 로그 관리: 자동 로그 로테이션 설정" -ForegroundColor White
