#!/bin/bash

# ESP32 AI 기능 배포 스크립트
# 실제 서버(signalcraft.kr)에 AI 기능을 배포합니다.

echo "🚀 ESP32 AI 기능 배포 시작..."

# 1. 서버에 AI 관련 파일들 복사
echo "📁 AI 관련 파일들 복사 중..."

# Python AI 서비스 파일들
scp services/esp32_data_processor.py ubuntu@signalcraft.kr:/var/www/smartcompressor/services/
scp services/anomaly_detector.py ubuntu@signalcraft.kr:/var/www/smartcompressor/services/
scp services/ai_inference_service.py ubuntu@signalcraft.kr:/var/www/smartcompressor/services/
scp services/ai_training_service.py ubuntu@signalcraft.kr:/var/www/smartcompressor/services/

# Node.js AI API 라우트
scp server/routes/esp32AiApi.js ubuntu@signalcraft.kr:/var/www/smartcompressor/server/routes/

# JavaScript AI 대시보드 모듈
scp static/js/esp32_ai_dashboard.js ubuntu@signalcraft.kr:/var/www/smartcompressor/static/js/

# 업데이트된 대시보드 HTML
scp static/pages/esp32_dashboard.html ubuntu@signalcraft.kr:/var/www/smartcompressor/static/pages/

# 업데이트된 CSS
scp static/css/esp32_dashboard.css ubuntu@signalcraft.kr:/var/www/smartcompressor/static/css/

# 업데이트된 메인 대시보드 JavaScript
scp static/js/esp32_dashboard.js ubuntu@signalcraft.kr:/var/www/smartcompressor/static/js/

echo "✅ 파일 복사 완료"

# 2. 서버에서 필요한 디렉토리 생성 및 의존성 설치
echo "🔧 서버 설정 중..."

ssh ubuntu@signalcraft.kr << 'EOF'
cd /var/www/smartcompressor

# AI 모델 디렉토리 생성
mkdir -p data/ai_models
mkdir -p data/ai_analysis

# Python 의존성 설치 (필요한 경우)
pip3 install scikit-learn pandas numpy joblib

# Node.js 서버에 AI 라우트 추가
if ! grep -q "esp32AiApi" server/app.js; then
    echo "AI 라우트 추가 중..."
    # server/app.js에 AI 라우트 추가하는 로직
    sed -i '/const esp32DashboardApi = require/a\\nconst esp32AiApi = require("./routes/esp32AiApi");' server/app.js
    sed -i '/app.use.*esp32DashboardApi/a\\napp.use("/api/esp32", esp32AiApi);' server/app.js
fi

# 파일 권한 설정
chmod +x services/ai_inference_service.py
chmod +x services/ai_training_service.py

echo "✅ 서버 설정 완료"
EOF

# 3. 서버 재시작
echo "🔄 서버 재시작 중..."

ssh ubuntu@signalcraft.kr << 'EOF'
cd /var/www/smartcompressor

# PM2로 서버 재시작
pm2 restart smartcompressor || pm2 start server.js --name smartcompressor

# 서버 상태 확인
pm2 status

echo "✅ 서버 재시작 완료"
EOF

echo "🎉 ESP32 AI 기능 배포 완료!"
echo "🌐 대시보드: https://signalcraft.kr/esp32-dashboard"
echo "🤖 AI 상태: https://signalcraft.kr/api/esp32/ai/status"
