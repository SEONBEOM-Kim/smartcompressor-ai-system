#!/bin/bash
# PM2 자동 시작 설정 스크립트

echo "🔧 PM2 자동 시작 설정 시작..."

# 1. PM2 설치
echo "📦 PM2 설치 중..."
npm install -g pm2

# 2. 기존 서비스 중지
echo "🛑 기존 서비스 중지..."
pkill -f "node server.js" || true

# 3. PM2로 서버 시작
echo "🚀 PM2로 서버 시작..."
pm2 start ecosystem.config.js --env production

# 4. PM2 자동 시작 설정
echo "🔄 PM2 자동 시작 설정..."
pm2 startup

# 5. PM2 설정 저장
echo "💾 PM2 설정 저장..."
pm2 save

# 6. PM2 상태 확인
echo "📊 PM2 상태 확인..."
pm2 status

echo "✅ PM2 자동 시작 설정 완료!"
echo "📋 사용법:"
echo "  - PM2 상태: pm2 status"
echo "  - PM2 로그: pm2 logs"
echo "  - PM2 재시작: pm2 restart all"
echo "  - PM2 중지: pm2 stop all"
