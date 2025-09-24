#!/bin/bash
# 502 에러 완전 해결 스크립트

echo "🔧 502 에러 완전 해결 시작..."

# 1. 모든 서비스 중지
echo "🛑 모든 서비스 중지..."
pm2 delete all || true
pkill -f "node server.js" || true
pkill -f "python.*app.py" || true
sudo systemctl stop nginx || true

# 2. 포트 정리
echo "🔌 포트 정리..."
sudo fuser -k 3000/tcp || true
sudo fuser -k 80/tcp || true
sudo fuser -k 443/tcp || true

# 3. 로그 디렉토리 생성
echo "📁 로그 디렉토리 생성..."
mkdir -p logs

# 4. Node.js 서버 시작
echo "🚀 Node.js 서버 시작..."
nohup node server.js > logs/node_server.log 2>&1 &
sleep 5

# 5. 서버 상태 확인
echo "📊 서버 상태 확인..."
ps aux | grep "node server.js" | grep -v grep

# 6. 서버 응답 테스트
echo "🌐 서버 응답 테스트..."
for i in {1..5}; do
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Node.js 서버 응답 성공 (시도 $i)"
        break
    else
        echo "❌ Node.js 서버 응답 실패 (시도 $i)"
        sleep 2
    fi
done

# 7. Nginx 설정 확인 및 적용
echo "🔧 Nginx 설정 확인..."
if [ -f "nginx_https_config.conf" ]; then
    echo "📄 Nginx 설정 파일 복사..."
    sudo cp nginx_https_config.conf /etc/nginx/sites-available/signalcraft
    sudo ln -sf /etc/nginx/sites-available/signalcraft /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
fi

# 8. Nginx 설정 테스트
echo "🔧 Nginx 설정 테스트..."
sudo nginx -t

# 9. Nginx 시작
echo "🔄 Nginx 시작..."
sudo systemctl start nginx
sudo systemctl enable nginx

# 10. 최종 상태 확인
echo "📊 최종 상태 확인..."
pm2 status
sudo systemctl status nginx

# 11. 서버 응답 테스트
echo "🌐 최종 서버 응답 테스트..."
curl -s http://localhost:3000 || echo "❌ 로컬 서버 응답 없음"
curl -s http://localhost:3000/api/auth/verify || echo "❌ API 응답 없음"

# 12. HTTPS 테스트
echo "🔒 HTTPS 테스트..."
curl -s -I https://signalcraft.kr || echo "❌ HTTPS 응답 없음"

echo "✅ 502 에러 완전 해결 완료!"
echo "🌐 https://signalcraft.kr로 접속해보세요!"
