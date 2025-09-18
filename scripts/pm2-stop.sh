#!/bin/bash
# PM2 서버 중지 스크립트

echo "🛑 Signalcraft PM2 서버 중지..."

# 1. PM2 프로세스 중지
echo "🛑 PM2 프로세스 중지 중..."
pm2 stop all

# 2. PM2 프로세스 삭제
echo "🗑️ PM2 프로세스 삭제 중..."
pm2 delete all

# 3. PM2 상태 확인
echo "📊 PM2 상태 확인:"
pm2 status

echo "✅ Signalcraft PM2 서버 중지 완료!"
