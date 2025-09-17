# SIGNALCRAFT HTTPS 설정 가이드

## 🚀 **EC2 서버에서 실행할 명령어:**

### 1단계: 최신 코드 가져오기
```bash
cd /var/www/smartcompressor
git pull origin main
```

### 2단계: SSL 인증서 발급
```bash
chmod +x setup_ssl.sh
./setup_ssl.sh
```

### 3단계: HTTPS 설정 적용
```bash
chmod +x setup_https.sh
./setup_https.sh
```

### 4단계: 테스트
```bash
# HTTP 리다이렉트 테스트
curl -I http://signalcraft.kr

# HTTPS 접속 테스트
curl -I https://signalcraft.kr
```

## 🔧 **수동 설정 (자동 스크립트 실패 시):**

### SSL 인증서 발급
```bash
sudo certbot --nginx -d signalcraft.kr -d www.signalcraft.kr
```

### Nginx 설정 수정
```bash
sudo nano /etc/nginx/sites-available/signalcraft
```

### Nginx 재시작
```bash
sudo nginx -t
sudo systemctl restart nginx
```

## 🌐 **최종 결과:**
- **HTTP**: `http://signalcraft.kr` → `https://signalcraft.kr`로 리다이렉트
- **HTTPS**: `https://signalcraft.kr` → 정상 접속
- **WWW**: `https://www.signalcraft.kr` → 정상 접속

## 🔍 **문제 해결:**
- **502 오류**: Node.js 서버 상태 확인
- **SSL 오류**: 인증서 발급 상태 확인
- **리다이렉트 안됨**: Nginx 설정 확인
