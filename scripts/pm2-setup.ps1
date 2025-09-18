# PM2 초기 설정 PowerShell 스크립트

Write-Host "⚙️ Signalcraft PM2 초기 설정..." -ForegroundColor Green

# 1. PM2 설치 확인
Write-Host "📦 PM2 설치 확인 중..." -ForegroundColor Yellow
try {
    $pm2Version = pm2 --version
    Write-Host "✅ PM2 이미 설치됨: $pm2Version" -ForegroundColor Green
} catch {
    Write-Host "📦 PM2 설치 중..." -ForegroundColor Yellow
    npm install -g pm2
}

# 2. PM2 로그 로테이션 모듈 설치
Write-Host "📦 PM2 로그 로테이션 모듈 설치 중..." -ForegroundColor Yellow
pm2 install pm2-logrotate

# 3. 로그 로테이션 설정
Write-Host "⚙️ 로그 로테이션 설정 중..." -ForegroundColor Yellow
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
pm2 set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss

# 4. PM2 자동 시작 설정
Write-Host "🔄 PM2 자동 시작 설정 중..." -ForegroundColor Yellow
pm2 startup

# 5. 로그 디렉토리 생성
Write-Host "📁 로그 디렉토리 생성 중..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host "✅ PM2 초기 설정 완료!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 다음 단계:" -ForegroundColor Cyan
Write-Host "1. 서버 시작: npm run pm2:start" -ForegroundColor White
Write-Host "2. 서버 중지: npm run pm2:stop" -ForegroundColor White
Write-Host "3. 서버 재시작: npm run pm2:restart" -ForegroundColor White
Write-Host "4. 상태 확인: npm run pm2:status" -ForegroundColor White
Write-Host "5. 로그 확인: npm run pm2:logs" -ForegroundColor White
Write-Host "6. 모니터링: npm run pm2:monit" -ForegroundColor White
