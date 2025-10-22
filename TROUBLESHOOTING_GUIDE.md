# 🔧 Signalcraft AI 문제 해결 가이드

## 🚨 긴급 상황 대응

### ESP32 센서가 작동하지 않을 때

#### 1. 전원 확인
```bash
# LED 상태 확인
- 파란색 LED: 업로드 활성화
- 빨간색 LED: WiFi 연결 상태
- LED가 안 켜짐: 전원 문제
```

**해결 방법:**
1. USB 케이블 재연결
2. 5V 어댑터 확인
3. 콘센트 전원 확인

#### 2. WiFi 연결 문제
```cpp
// 시리얼 모니터에서 확인:
WiFi connecting...
WiFi failed!
```

**해결 방법:**
1. **WiFi 신호 강도** 확인 (가까이 이동)
2. **비밀번호** 정확성 확인
3. **2.4GHz 대역** 사용 확인
4. **부트 버튼 3초** 누르기 (WiFi 재연결)

#### 3. 서버 업로드 실패
```cpp
// 시리얼 모니터에서 확인:
❌ FAILED: 404
❌ FAILED: 500
```

**해결 방법:**
1. **서버 상태** 확인: `curl http://localhost:3000/api/esp32/status`
2. **네트워크 연결** 확인
3. **ESP32 재부팅**

### 서버가 응답하지 않을 때

#### 1. PM2 서버 상태 확인
```bash
pm2 status
# 결과가 stopped이면:
pm2 restart signalcraft-nodejs
```

#### 2. 서버 로그 확인
```bash
pm2 logs signalcraft-nodejs --lines 20
# 오류 메시지 확인
```

#### 3. 포트 사용 확인
```bash
sudo lsof -i :3000
# 포트가 사용 중이면 프로세스 종료
```

## 🔍 일반적인 문제들

### ESP32 관련 문제

#### 문제: 시리얼 모니터에 아무것도 안 나옴
**원인:** USB 드라이버 문제 또는 포트 설정 오류

**해결 방법:**
1. **USB 케이블** 교체
2. **포트 설정** 확인 (Tools → Port)
3. **Baud Rate** 115200 설정
4. **ESP32 재부팅** (전원 뽑았다가 다시 연결)

#### 문제: WiFi 연결은 되는데 업로드 실패
**원인:** 서버 연결 문제 또는 API 오류

**해결 방법:**
1. **서버 상태** 확인
2. **방화벽 설정** 확인
3. **ESP32 코드**에서 서버 URL 확인
4. **네트워크 연결** 테스트

#### 문제: 부트 버튼이 작동하지 않음
**원인:** GPIO 핀 설정 오류

**해결 방법:**
1. **GPIO 0** 핀 연결 확인
2. **풀업 저항** 확인
3. **코드 재업로드**

### 서버 관련 문제

#### 문제: PM2 서버가 계속 중지됨
**원인:** 메모리 부족 또는 코드 오류

**해결 방법:**
```bash
# 메모리 사용량 확인
free -h

# 서버 로그 확인
pm2 logs signalcraft-nodejs --lines 50

# 서버 재시작
pm2 restart signalcraft-nodejs

# 메모리 부족 시
pm2 delete signalcraft-nodejs
pm2 start server.js --name signalcraft-nodejs
```

#### 문제: 데이터베이스 오류
**원인:** SQLite 파일 손상 또는 권한 문제

**해결 방법:**
```bash
# 데이터베이스 파일 확인
ls -la /var/www/smartcompressor/database/

# 권한 수정
sudo chown ubuntu:ubuntu /var/www/smartcompressor/database/smartcompressor.db

# 데이터베이스 재생성
rm /var/www/smartcompressor/database/smartcompressor.db
pm2 restart signalcraft-nodejs
```

#### 문제: 디스크 공간 부족
**원인:** 로그 파일이나 데이터 파일이 너무 많음

**해결 방법:**
```bash
# 디스크 사용량 확인
df -h

# 오래된 로그 파일 삭제
find /var/www/smartcompressor/logs -name "*.log" -mtime +7 -delete

# 오래된 데이터 파일 삭제
find /var/www/smartcompressor/data -name "*.json" -mtime +30 -delete
```

### 네트워크 관련 문제

#### 문제: ESP32가 WiFi에 연결되지 않음
**원인:** WiFi 설정 오류 또는 신호 문제

**해결 방법:**
1. **WiFi 신호 강도** 확인 (ESP32 근처로 이동)
2. **비밀번호** 정확성 확인
3. **2.4GHz 대역** 사용 확인
4. **WiFi 공유기** 재부팅

#### 문제: 서버에 접속할 수 없음
**원인:** 방화벽 또는 네트워크 설정 문제

**해결 방법:**
```bash
# 방화벽 상태 확인
sudo ufw status

# 포트 3000 열기
sudo ufw allow 3000

# 서버 프로세스 확인
sudo lsof -i :3000
```

## 📊 성능 문제

### 데이터 전송이 느릴 때

#### 원인 분석
1. **WiFi 신호** 약함
2. **서버 응답** 느림
3. **네트워크 대역폭** 부족

#### 해결 방법
```cpp
// ESP32 코드에서 전송 주기 조정
#define UPLOAD_MS 15000  // 15초로 증가

// 또는 데이터 크기 줄이기
#define WINDOW_MS 500    // 0.5초로 감소
```

### 메모리 사용량이 많을 때

#### 원인 분석
1. **버퍼 오버플로우**
2. **메모리 누수**
3. **데이터 쌓임**

#### 해결 방법
```cpp
// ESP32 코드에서 메모리 관리
void loop() {
    // 정기적으로 가비지 컬렉션
    if (millis() % 60000 == 0) {
        // 1분마다 메모리 정리
    }
}
```

## 🔄 복구 방법

### ESP32 완전 초기화

#### 1. 하드웨어 리셋
1. **전원** 뽑기
2. **10초** 대기
3. **전원** 다시 연결

#### 2. 펌웨어 재설치
1. **Arduino IDE**에서 코드 열기
2. **WiFi 설정** 확인
3. **업로드** 실행
4. **시리얼 모니터**로 확인

### 서버 완전 초기화

#### 1. PM2 서비스 중지
```bash
pm2 stop signalcraft-nodejs
pm2 delete signalcraft-nodejs
```

#### 2. 데이터 정리
```bash
# 데이터베이스 삭제
rm /var/www/smartcompressor/database/smartcompressor.db

# 로그 파일 정리
rm -rf /var/www/smartcompressor/logs/*

# 업로드 파일 정리
rm -rf /var/www/smartcompressor/uploads/*
```

#### 3. 서버 재시작
```bash
pm2 start server.js --name signalcraft-nodejs
pm2 save
pm2 startup
```

## 📞 지원 요청 시 필요한 정보

### ESP32 관련
1. **시리얼 모니터** 로그 (최근 50줄)
2. **LED 상태** 설명
3. **부트 버튼** 동작 여부
4. **WiFi 연결** 상태

### 서버 관련
1. **PM2 상태**: `pm2 status`
2. **서버 로그**: `pm2 logs signalcraft-nodejs --lines 50`
3. **시스템 상태**: `free -h`, `df -h`
4. **네트워크 상태**: `curl http://localhost:3000/api/esp32/status`

### 네트워크 관련
1. **WiFi 신호 강도**
2. **인터넷 연결** 상태
3. **방화벽 설정**
4. **포트 사용** 상태

## 🚨 긴급 복구 체크리스트

### 1단계: 기본 확인
- [ ] ESP32 전원 확인
- [ ] WiFi 연결 확인
- [ ] 서버 상태 확인
- [ ] 네트워크 연결 확인

### 2단계: 재시작
- [ ] ESP32 재부팅
- [ ] 서버 재시작 (`pm2 restart signalcraft-nodejs`)
- [ ] WiFi 공유기 재부팅

### 3단계: 설정 확인
- [ ] WiFi 비밀번호 확인
- [ ] 서버 URL 확인
- [ ] 포트 설정 확인

### 4단계: 로그 분석
- [ ] ESP32 시리얼 로그 확인
- [ ] 서버 PM2 로그 확인
- [ ] 시스템 로그 확인

---

**💡 팁: 문제가 지속되면 로그를 수집하여 개발팀에 문의하세요!**

문제 해결이 어려울 때는 위의 정보를 수집하여 지원팀에 연락하시기 바랍니다. 🆘
