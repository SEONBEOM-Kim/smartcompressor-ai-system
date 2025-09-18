#!/bin/bash
# PM2 서버 재시작 스크립트

echo "🔄 Signalcraft PM2 서버 재시작..."

# 1. PM2 프로세스 재시작
echo "🔄 PM2 프로세스 재시작 중..."
pm2 restart all

# 2. PM2 상태 확인
echo "📊 PM2 상태 확인:"
pm2 status

# 3. 로그 확인
echo "📝 최근 로그 확인:"
pm2 logs --lines 10

echo "✅ Signalcraft PM2 서버 재시작 완료!"
