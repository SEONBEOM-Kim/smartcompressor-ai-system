#!/bin/bash
# 502 에러 디버깅 스크립트

echo "🔍 502 에러 디버깅 시작..."

# 1. 현재 디렉토리 확인
echo "📁 현재 디렉토리: $(pwd)"
echo "📋 파일 목록:"
ls -la

# 2. PM2 상태 확인
echo ""
echo "📊 PM2 상태:"
pm2 status

# 3. 포트 사용 상태 확인
echo ""
echo "🔌 포트 사용 상태:"
sudo netstat -tlnp | grep -E ":(3000|80|443)" || echo "포트 확인 권한 없음"

# 4. Node.js 프로세스 확인
echo ""
echo "🟢 Node.js 프로세스:"
ps aux | grep node | grep -v grep

# 5. Nginx 상태 확인
echo ""
echo "🔧 Nginx 상태:"
sudo systemctl status nginx

# 6. Nginx 설정 테스트
echo ""
echo "🔧 Nginx 설정 테스트:"
sudo nginx -t

# 7. Nginx 설정 파일 확인
echo ""
echo "📄 Nginx 설정 파일:"
sudo cat /etc/nginx/sites-available/signalcraft || echo "Nginx 설정 파일 없음"

# 8. 서버 응답 테스트
echo ""
echo "🌐 서버 응답 테스트:"
curl -s http://localhost:3000 || echo "❌ 로컬 서버 응답 없음"
curl -s http://localhost:3000/api/auth/verify || echo "❌ API 응답 없음"

# 9. 로그 확인
echo ""
echo "📝 최근 로그:"
tail -20 /var/log/nginx/error.log || echo "Nginx 에러 로그 없음"
tail -20 logs/err.log || echo "PM2 에러 로그 없음"

# 10. 메모리 및 CPU 사용량
echo ""
echo "💾 시스템 리소스:"
free -h
df -h

echo ""
echo "✅ 502 에러 디버깅 완료!"
