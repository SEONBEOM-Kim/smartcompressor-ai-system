# EC2 서버에 PM2로 배포하는 PowerShell 스크립트

Write-Host "🚀 Signalcraft EC2 PM2 배포 시작..." -ForegroundColor Green

# 1. EC2 서버 정보
$EC2_HOST = "3.39.124.0"
$EC2_USER = "ubuntu"
$PROJECT_DIR = "/var/www/smartcompressor"

Write-Host "📋 배포 정보:" -ForegroundColor Cyan
Write-Host "  - 서버: $EC2_HOST" -ForegroundColor White
Write-Host "  - 사용자: $EC2_USER" -ForegroundColor White
Write-Host "  - 프로젝트 디렉토리: $PROJECT_DIR" -ForegroundColor White

# 2. SSH 키 파일 확인
$SSH_KEY = "C:\Users\user\.ssh\id_rsa"
if (-not (Test-Path $SSH_KEY)) {
    Write-Host "❌ SSH 키 파일을 찾을 수 없습니다: $SSH_KEY" -ForegroundColor Red
    Write-Host "SSH 키 파일 경로를 확인해주세요." -ForegroundColor Yellow
    exit 1
}

# 3. EC2 서버에 SSH 접속하여 배포 실행
Write-Host "🔗 EC2 서버에 접속하여 배포 실행 중..." -ForegroundColor Yellow

$deployScript = @"
cd $PROJECT_DIR
echo "📥 최신 코드 가져오기..."
git pull origin main

echo "📦 Node.js 의존성 설치..."
npm install

echo "📦 PM2 설치 확인..."
if ! command -v pm2 &> /dev/null; then
    echo "📦 PM2 설치 중..."
    npm install -g pm2
else
    echo "✅ PM2 이미 설치됨: \$(pm2 --version)"
fi

echo "🛑 기존 서비스 종료..."
pm2 delete all || true
pkill -f "node server.js" || true
pkill -f "python.*app.py" || true

echo "📁 로그 디렉토리 생성..."
mkdir -p logs

echo "🚀 PM2로 서버 시작..."
pm2 start ecosystem.config.js --env production

echo "🔄 PM2 자동 시작 설정..."
pm2 startup
pm2 save

echo "📊 PM2 상태 확인..."
pm2 status

echo "🌐 서버 응답 테스트..."
sleep 5
curl -s http://localhost:3000/api/auth/verify || echo "❌ API 응답 없음"

echo "✅ EC2 PM2 배포 완료!"
echo "🌐 서버 URL: http://3.39.124.0:3000"
echo "📝 로그 확인: pm2 logs"
echo "📊 모니터링: pm2 monit"
"@

# SSH 명령 실행
ssh -i $SSH_KEY -o StrictHostKeyChecking=no $EC2_USER@$EC2_HOST $deployScript

Write-Host "🎉 EC2 배포 스크립트 실행 완료!" -ForegroundColor Green
Write-Host "🌐 서버 접속: http://3.39.124.0:3000" -ForegroundColor White
Write-Host "🌐 도메인 접속: http://signalcraft.kr" -ForegroundColor White
