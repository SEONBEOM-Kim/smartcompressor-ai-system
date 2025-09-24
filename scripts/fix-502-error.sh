#!/bin/bash
# 502 에러 해결 스크립트

echo "🔧 Signalcraft 502 에러 해결 시작..."

# 1. 현재 상태 확인
echo "📊 현재 서비스 상태 확인..."
pm2 status
sudo systemctl status nginx

# 2. 포트 사용 상태 확인
echo "🌐 포트 사용 상태:"
sudo netstat -tlnp | grep -E ":(3000|80|443)" || echo "포트 확인 권한 없음"

# 3. PM2 프로세스 재시작
echo "🔄 PM2 프로세스 재시작..."
pm2 restart all

# 4. Nginx 설정 테스트
echo "🔧 Nginx 설정 테스트..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx 설정 정상"
    # Nginx 재시작
    echo "🔄 Nginx 재시작..."
    sudo systemctl restart nginx
else
    echo "❌ Nginx 설정 오류 발견"
    echo "🔧 Nginx 설정 파일 확인 중..."
    sudo cat /etc/nginx/sites-available/signalcraft
fi

# 5. 서버 응답 테스트
echo "⏳ 서버 시작 대기 (10초)..."
sleep 10

echo "🌐 서버 응답 테스트..."
curl -s http://localhost:3000 || echo "❌ 로컬 서버 응답 없음"
curl -s http://localhost:3000/api/auth/verify || echo "❌ API 응답 없음"

# 6. HTTPS 테스트
echo "🔒 HTTPS 테스트..."
curl -s -I https://signalcraft.kr || echo "❌ HTTPS 응답 없음"

# 7. 최종 상태 확인
echo "📊 최종 상태 확인..."
pm2 status
sudo systemctl status nginx

echo "✅ 502 에러 해결 완료!"
echo "🌐 https://signalcraft.kr로 접속해보세요!"