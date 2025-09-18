# PM2 서버 시작 PowerShell 스크립트

Write-Host "🚀 Signalcraft PM2 서버 시작..." -ForegroundColor Green

# 1. 로그 디렉토리 생성
Write-Host "📁 로그 디렉토리 생성 중..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# 2. 기존 nohup 프로세스 종료
Write-Host "🛑 기존 nohup 프로세스 종료 중..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*server.js*" } | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*app.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# 3. PM2 프로세스 정리
Write-Host "🧹 PM2 프로세스 정리 중..." -ForegroundColor Yellow
pm2 delete all 2>$null

# 4. PM2로 서버 시작
Write-Host "🚀 PM2로 서버 시작 중..." -ForegroundColor Yellow
pm2 start ecosystem.config.js --env production

# 5. PM2 상태 확인
Write-Host "📊 PM2 상태 확인:" -ForegroundColor Cyan
pm2 status

Write-Host "✅ Signalcraft PM2 서버 시작 완료!" -ForegroundColor Green
Write-Host "🌐 Node.js 서버: http://localhost:3000" -ForegroundColor White
Write-Host "🐍 Python 서버: http://localhost:8000" -ForegroundColor White
Write-Host "📝 로그 확인: npm run pm2:logs" -ForegroundColor White
Write-Host "📊 모니터링: npm run pm2:monit" -ForegroundColor White
