# SIGNALCRAFT EC2 배포 스크립트
# GitHub에서 최신 코드를 가져와서 EC2에 배포합니다.

param(
    [string]$EC2_HOST = "3.39.124.0",
    [string]$EC2_USER = "ubuntu",
    [string]$EC2_KEY_PATH = "~/.ssh/signalcraft-key.pem",
    [string]$PROJECT_PATH = "/home/ubuntu/smartcompressor-ai-system"
)

Write-Host "🚀 SIGNALCRAFT EC2 배포 시작..." -ForegroundColor Green

# 1. EC2 서버에 연결하여 최신 코드 pull
Write-Host "📥 EC2에서 최신 코드 가져오는 중..." -ForegroundColor Yellow
$pullCommand = @"
cd $PROJECT_PATH
git pull origin main
echo "✅ Git pull 완료"
"@

ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST $pullCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Git pull 성공" -ForegroundColor Green
} else {
    Write-Host "❌ Git pull 실패" -ForegroundColor Red
    exit 1
}

# 2. Node.js 의존성 설치
Write-Host "📦 Node.js 의존성 설치 중..." -ForegroundColor Yellow
$installCommand = @"
cd $PROJECT_PATH
npm install
echo "✅ npm install 완료"
"@

ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST $installCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 의존성 설치 성공" -ForegroundColor Green
} else {
    Write-Host "❌ 의존성 설치 실패" -ForegroundColor Red
    exit 1
}

# 3. 기존 프로세스 종료
Write-Host "🛑 기존 서비스 종료 중..." -ForegroundColor Yellow
$stopCommand = @"
cd $PROJECT_PATH
pkill -f "node server.js" || true
pkill -f "node app.js" || true
echo "✅ 기존 프로세스 종료 완료"
"@

ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST $stopCommand

# 4. 새 서비스 시작
Write-Host "🚀 새 서비스 시작 중..." -ForegroundColor Yellow
$startCommand = @"
cd $PROJECT_PATH
nohup node server.js > server.log 2>&1 &
echo "✅ 서비스 시작 완료"
sleep 3
ps aux | grep "node server.js" | grep -v grep
"@

ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST $startCommand

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 서비스 시작 성공" -ForegroundColor Green
} else {
    Write-Host "❌ 서비스 시작 실패" -ForegroundColor Red
    exit 1
}

# 5. 서비스 상태 확인
Write-Host "🔍 서비스 상태 확인 중..." -ForegroundColor Yellow
$statusCommand = @"
cd $PROJECT_PATH
curl -s http://localhost:3000/api/auth/verify || echo "API 테스트 실패"
echo "서비스 로그 (마지막 10줄):"
tail -10 server.log
"@

ssh -i $EC2_KEY_PATH $EC2_USER@$EC2_HOST $statusCommand

Write-Host "🎉 SIGNALCRAFT EC2 배포 완료!" -ForegroundColor Green
Write-Host "🌐 서버 URL: http://$EC2_HOST:3000" -ForegroundColor Cyan
Write-Host "📊 관리자 대시보드: http://$EC2_HOST:3000/admin" -ForegroundColor Cyan
Write-Host "🔗 API 엔드포인트: http://$EC2_HOST:3000/api/*" -ForegroundColor Cyan
