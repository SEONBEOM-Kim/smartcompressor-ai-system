#!/bin/bash
# systemd 서비스 설정 스크립트

echo "🔧 systemd 서비스 설정 시작..."

# 1. 서비스 파일 생성
echo "📄 서비스 파일 생성 중..."
sudo tee /etc/systemd/system/signalcraft.service > /dev/null <<EOF
[Unit]
Description=Signalcraft Node.js Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/var/www/smartcompressor
ExecStart=/usr/bin/node server.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production
Environment=PORT=3000

# 로그 설정
StandardOutput=append:/var/www/smartcompressor/logs/server.log
StandardError=append:/var/www/smartcompressor/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

# 2. 서비스 파일 권한 설정
echo "🔐 서비스 파일 권한 설정..."
sudo chmod 644 /etc/systemd/system/signalcraft.service

# 3. systemd 데몬 리로드
echo "🔄 systemd 데몬 리로드..."
sudo systemctl daemon-reload

# 4. 서비스 활성화
echo "✅ 서비스 활성화..."
sudo systemctl enable signalcraft.service

# 5. 서비스 시작
echo "🚀 서비스 시작..."
sudo systemctl start signalcraft.service

# 6. 서비스 상태 확인
echo "📊 서비스 상태 확인..."
sudo systemctl status signalcraft.service --no-pager

echo "✅ systemd 서비스 설정 완료!"
echo "📋 사용법:"
echo "  - 서비스 시작: sudo systemctl start signalcraft"
echo "  - 서비스 중지: sudo systemctl stop signalcraft"
echo "  - 서비스 재시작: sudo systemctl restart signalcraft"
echo "  - 서비스 상태: sudo systemctl status signalcraft"
echo "  - 로그 확인: sudo journalctl -u signalcraft -f"
