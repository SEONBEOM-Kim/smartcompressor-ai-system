#!/bin/bash

echo "🔧 Signalcraft systemd 서비스 설정 시작..."

# systemd 서비스 파일 생성
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

[Install]
WantedBy=multi-user.target
EOF

# 서비스 활성화
sudo systemctl daemon-reload
sudo systemctl enable signalcraft.service
sudo systemctl start signalcraft.service

# 상태 확인
sudo systemctl status signalcraft.service

echo "✅ Signalcraft systemd 서비스 설정 완료!"
echo "📊 서비스 상태:"
sudo systemctl is-active signalcraft.service
sudo systemctl is-enabled signalcraft.service