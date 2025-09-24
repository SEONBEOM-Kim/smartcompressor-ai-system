#!/bin/bash
# 서버 상태 간단 확인 스크립트

echo "🔍 Signalcraft 서버 상태 확인..."

# 1. 현재 시간
echo "⏰ 현재 시간: $(date)"

# 2. 현재 디렉토리
echo "📁 현재 디렉토리: $(pwd)"

# 3. PM2 상태
echo "📊 PM2 상태:"
pm2 status 2>/dev/null || echo "PM2가 실행되지 않음"

# 4. Node.js 프로세스
echo "🟢 Node.js 프로세스:"
ps aux | grep "node server.js" | grep -v grep || echo "Node.js 서버가 실행되지 않음"

# 5. 포트 사용 상태
echo "🔌 포트 사용 상태:"
sudo netstat -tlnp | grep -E ":(3000|80|443)" 2>/dev/null || echo "포트 확인 권한 없음"

# 6. Nginx 상태
echo "🔧 Nginx 상태:"
sudo systemctl status nginx --no-pager 2>/dev/null || echo "Nginx 상태 확인 실패"

# 7. 서버 응답 테스트
echo "🌐 서버 응답 테스트:"
curl -s http://localhost:3000 > /dev/null && echo "✅ 로컬 서버 응답 성공" || echo "❌ 로컬 서버 응답 실패"

# 8. 최근 로그 (마지막 10줄)
echo "📝 최근 PM2 로그:"
pm2 logs --lines 10 2>/dev/null || echo "PM2 로그 없음"

echo "✅ 서버 상태 확인 완료!"
