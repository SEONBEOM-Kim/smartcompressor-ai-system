#!/bin/bash
# crontab 자동 시작 설정 스크립트

echo "🔧 crontab 자동 시작 설정 시작..."

# 1. 시작 스크립트 생성
echo "📄 시작 스크립트 생성..."
cat > /var/www/smartcompressor/start-server.sh << 'EOF'
#!/bin/bash
cd /var/www/smartcompressor
nohup node server.js > logs/server.log 2>&1 &
EOF

# 2. 실행 권한 부여
chmod +x /var/www/smartcompressor/start-server.sh

# 3. crontab 설정
echo "⏰ crontab 설정..."
(crontab -l 2>/dev/null; echo "@reboot /var/www/smartcompressor/start-server.sh") | crontab -

# 4. crontab 확인
echo "📋 crontab 설정 확인..."
crontab -l

echo "✅ crontab 자동 시작 설정 완료!"
