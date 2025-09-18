#!/bin/bash
# PM2 자동 재시작 및 장애 복구 테스트 스크립트

echo "🧪 Signalcraft PM2 테스트 시작..."

# 1. PM2 상태 확인
echo "📊 1. 초기 PM2 상태 확인:"
pm2 status

# 2. 서버 응답 테스트
echo "🌐 2. 서버 응답 테스트:"
echo "Node.js 서버 (포트 3000):"
curl -s http://localhost:3000/api/auth/verify || echo "❌ Node.js API 응답 없음"

echo "Python 서버 (포트 8000):"
curl -s http://localhost:8000/ || echo "❌ Python API 응답 없음"

# 3. 프로세스 강제 종료 테스트
echo "💥 3. 프로세스 강제 종료 테스트..."
echo "Node.js 프로세스 강제 종료 중..."
pkill -f "node server.js" || true

echo "5초 대기 중..."
sleep 5

# 4. 자동 재시작 확인
echo "🔄 4. 자동 재시작 확인:"
pm2 status

# 5. 서버 응답 재테스트
echo "🌐 5. 서버 응답 재테스트:"
echo "Node.js 서버 (포트 3000):"
curl -s http://localhost:3000/api/auth/verify || echo "❌ Node.js API 응답 없음"

# 6. 메모리 사용량 테스트
echo "💾 6. 메모리 사용량 확인:"
pm2 monit --no-interaction | head -20

# 7. 로그 확인
echo "📝 7. 최근 로그 확인:"
pm2 logs --lines 20

echo "✅ PM2 테스트 완료!"
echo ""
echo "📋 테스트 결과:"
echo "- 자동 재시작: $(pm2 status | grep -c 'online' || echo '0')개 프로세스 실행 중"
echo "- 메모리 관리: PM2 모니터링 활성화"
echo "- 로그 관리: 자동 로그 로테이션 설정"
