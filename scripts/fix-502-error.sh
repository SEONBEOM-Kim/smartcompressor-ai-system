#!/bin/bash
# 502 오류 해결 스크립트

echo "🔧 502 오류 해결 시작..."

# 프로젝트 디렉토리로 이동
cd /var/www/smartcompressor

echo "📊 현재 PM2 상태 확인..."
pm2 status

echo "🛑 모든 PM2 프로세스 중지..."
pm2 delete all || true

echo "📥 최신 코드 가져오기..."
git pull origin main

echo "📦 의존성 설치..."
npm install

echo "🚀 PM2 프로세스 재시작..."
pm2 start ecosystem.config.js --env production

echo "⏳ 서버 시작 대기 (5초)..."
sleep 5

echo "📊 PM2 상태 확인..."
pm2 status

echo "🌐 서버 응답 테스트..."
curl -s http://localhost:3000 || echo "❌ 로컬 서버 응답 없음"

echo "✅ 502 오류 해결 완료!"
echo "🌐 이제 https://signalcraft.kr로 접속해보세요!"
