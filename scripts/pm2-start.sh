#!/bin/bash
# PM2 서버 시작 스크립트

echo "🚀 Signalcraft PM2 서버 시작..."

# 1. 로그 디렉토리 생성
mkdir -p logs

# 2. 기존 nohup 프로세스 종료
echo "🛑 기존 nohup 프로세스 종료 중..."
pkill -f "node server.js" || true
pkill -f "python.*app.py" || true
pkill -f "python.*integrated_web_server.py" || true

# 3. PM2 프로세스 정리
echo "🧹 PM2 프로세스 정리 중..."
pm2 delete all || true

# 4. PM2로 서버 시작
echo "🚀 PM2로 서버 시작 중..."
pm2 start ecosystem.config.js --env production

# 5. PM2 상태 확인
echo "📊 PM2 상태 확인:"
pm2 status

# 6. PM2 모니터링 시작 (선택사항)
echo "📈 PM2 모니터링 시작..."
pm2 monit &

echo "✅ Signalcraft PM2 서버 시작 완료!"
echo "🌐 Node.js 서버: http://localhost:3000"
echo "🐍 Python 서버: http://localhost:8000"
echo "📝 로그 확인: pm2 logs"
echo "📊 모니터링: pm2 monit"
