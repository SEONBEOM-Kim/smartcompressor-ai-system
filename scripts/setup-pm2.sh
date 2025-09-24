#!/bin/bash
# PM2 설정 스크립트

echo "🔧 PM2 설정 시작..."

# 1. PM2 설치
echo "📦 PM2 설치 중..."
npm install -g pm2

# 2. PM2 버전 확인
echo "📋 PM2 버전:"
pm2 --version

# 3. 기존 Node.js 프로세스 중지
echo "🛑 기존 Node.js 프로세스 중지..."
pkill -f "node server.js" || true

# 4. PM2로 서버 시작
echo "🚀 PM2로 서버 시작..."
pm2 start ecosystem.config.js --env production

# 5. PM2 자동 시작 설정
echo "🔄 PM2 자동 시작 설정..."
pm2 startup
pm2 save

# 6. PM2 상태 확인
echo "📊 PM2 상태:"
pm2 status

echo "✅ PM2 설정 완료!"
