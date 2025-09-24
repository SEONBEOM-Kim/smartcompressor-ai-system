# 🚀 수동 배포 가이드 (502 에러 해결)

## 1. EC2 서버에 SSH 접속

```bash
# SSH 키가 있는 경우
ssh -i your-key.pem ubuntu@3.39.124.0

# 또는 패스워드 인증
ssh ubuntu@3.39.124.0
```

## 2. 서버 상태 확인

```bash
# 프로젝트 디렉토리로 이동
cd /var/www/smartcompressor

# 현재 상태 확인
pm2 status
sudo systemctl status nginx
```

## 3. 502 에러 해결

```bash
# 1. 모든 서비스 중지
pm2 delete all
sudo systemctl stop nginx

# 2. 포트 정리
sudo fuser -k 3000/tcp
sudo fuser -k 80/tcp
sudo fuser -k 443/tcp

# 3. 최신 코드 가져오기
git pull origin main

# 4. 의존성 설치
npm install

# 5. Node.js 서버 시작
nohup node server.js > logs/node_server.log 2>&1 &

# 6. 서버 응답 확인
sleep 5
curl http://localhost:3000

# 7. Nginx 설정 적용
sudo cp nginx_https_config.conf /etc/nginx/sites-available/signalcraft
sudo ln -sf /etc/nginx/sites-available/signalcraft /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 8. Nginx 시작
sudo nginx -t
sudo systemctl start nginx

# 9. 최종 확인
curl -I https://signalcraft.kr
```

## 4. 문제 해결

### PM2 사용하는 경우:
```bash
# PM2로 서버 시작
pm2 start ecosystem.config.js --env production
pm2 save
```

### 로그 확인:
```bash
# PM2 로그
pm2 logs

# Nginx 로그
sudo tail -f /var/log/nginx/error.log

# 시스템 로그
sudo journalctl -u nginx -f
```
