#!/bin/bash
# 간단한 배포 스크립트 (502 에러 해결)

echo "🚀 Signalcraft 간단 배포 시작..."

# 1. 현재 상태 확인
echo "📊 현재 상태 확인..."
whoami
pwd
ls -la

# 2. 프로젝트 디렉토리 확인
if [ ! -d "/var/www/smartcompressor" ]; then
    echo "📁 프로젝트 디렉토리 생성..."
    sudo mkdir -p /var/www/smartcompressor
    sudo chown ubuntu:ubuntu /var/www/smartcompressor
fi

cd /var/www/smartcompressor

# 3. Git 상태 확인
echo "📋 Git 상태 확인..."
git status

# 4. 최신 코드 가져오기
echo "📥 최신 코드 가져오기..."
git pull origin main

# 5. 의존성 설치
echo "📦 의존성 설치..."
npm install

# 6. 기존 서비스 중지
echo "🛑 기존 서비스 중지..."
pm2 delete all || true
pkill -f "node server.js" || true

# 7. 서버 시작
echo "🚀 서버 시작..."
nohup node server.js > logs/server.log 2>&1 &

# 8. 서버 응답 확인
echo "⏳ 서버 시작 대기..."
sleep 10

echo "🌐 서버 응답 테스트..."
curl -s http://localhost:3000 && echo "✅ 서버 응답 성공" || echo "❌ 서버 응답 실패"

# 9. Nginx 재시작
echo "🔧 Nginx 재시작..."
sudo systemctl restart nginx

echo "✅ 배포 완료!"
