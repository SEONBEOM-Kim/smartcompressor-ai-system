#!/bin/bash

echo "🔄 Signalcraft 서버 재시작 스크립트"
echo "=================================="

# 프로젝트 디렉토리로 이동
cd /var/www/smartcompressor

echo "📁 현재 디렉토리: $(pwd)"
echo "📋 파일 목록:"
ls -la

# 기존 프로세스 종료
echo "🛑 기존 프로세스 종료..."
pm2 delete all || true

# 로그 디렉토리 생성
mkdir -p logs

# Node.js 의존성 확인
echo "📦 Node.js 의존성 확인..."
npm install

# PM2 설치 확인
if ! command -v pm2 &> /dev/null; then
  echo "📦 PM2 설치 중..."
  npm install -g pm2
fi

# PM2로 서버 시작
echo "🚀 PM2로 서버 시작..."
pm2 start ecosystem.config.js --env production

# PM2 상태 확인
echo "📊 PM2 상태 확인..."
pm2 status

# 서버 시작 대기
echo "⏳ 서버 시작 대기 (10초)..."
sleep 10

# 포트 확인
echo "🌐 포트 사용 상태:"
sudo netstat -tlnp | grep -E ":(3000|8000)" || echo "포트 확인 권한 없음"

# 서버 응답 테스트
echo "🌐 서버 응답 테스트..."
curl -s http://localhost:3000 || echo "❌ 로컬 서버 응답 없음"
curl -s http://localhost:3000/api/auth/verify || echo "❌ API 응답 없음"

# Nginx 재시작
echo "🔄 Nginx 재시작..."
sudo systemctl restart nginx

echo "✅ 서버 재시작 완료!"
