#!/bin/bash
# PM2 초기 설정 스크립트

echo "⚙️ Signalcraft PM2 초기 설정..."

# 1. PM2 설치 확인
if ! command -v pm2 &> /dev/null; then
    echo "📦 PM2 설치 중..."
    npm install -g pm2
else
    echo "✅ PM2 이미 설치됨: $(pm2 --version)"
fi

# 2. PM2 로그 로테이션 모듈 설치
echo "📦 PM2 로그 로테이션 모듈 설치 중..."
pm2 install pm2-logrotate

# 3. 로그 로테이션 설정
echo "⚙️ 로그 로테이션 설정 중..."
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
pm2 set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss

# 4. PM2 자동 시작 설정
echo "🔄 PM2 자동 시작 설정 중..."
pm2 startup

# 5. 로그 디렉토리 생성
echo "📁 로그 디렉토리 생성 중..."
mkdir -p logs

# 6. 스크립트 실행 권한 설정
echo "🔐 스크립트 실행 권한 설정 중..."
chmod +x scripts/*.sh

echo "✅ PM2 초기 설정 완료!"
echo ""
echo "📋 다음 단계:"
echo "1. 서버 시작: ./scripts/pm2-start.sh"
echo "2. 서버 중지: ./scripts/pm2-stop.sh"
echo "3. 서버 재시작: ./scripts/pm2-restart.sh"
echo "4. 상태 확인: pm2 status"
echo "5. 로그 확인: pm2 logs"
echo "6. 모니터링: pm2 monit"
