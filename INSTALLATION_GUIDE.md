# 🚀 Signalcraft AI 설치 가이드

## 📋 설치 전 준비사항

### 하드웨어
- ESP32 개발 보드
- I2S 마이크 모듈
- USB 케이블
- 5V 어댑터 (현장 설치용)

### 소프트웨어
- Arduino IDE (최신 버전)
- ESP32 보드 패키지
- 필요한 라이브러리

## 🔧 단계별 설치 가이드

### 1단계: Arduino IDE 설정

#### 1.1 Arduino IDE 설치
1. [Arduino IDE 다운로드](https://www.arduino.cc/en/software)
2. 설치 후 실행

#### 1.2 ESP32 보드 패키지 설치
1. **File** → **Preferences**
2. **Additional Board Manager URLs**에 추가:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. **Tools** → **Board** → **Boards Manager**
4. "esp32" 검색 후 **esp32 by Espressif Systems** 설치

#### 1.3 필요한 라이브러리 설치
1. **Tools** → **Manage Libraries**
2. 다음 라이브러리 설치:
   - **ArduinoJson** (by Benoit Blanchon)
   - **HTTPClient** (ESP32 내장)

### 2단계: ESP32 코드 설정

#### 2.1 코드 다운로드
```bash
# 프로젝트 클론
git clone [repository-url]
cd smartcompressor-ai-system
```

#### 2.2 WiFi 설정 변경
`optimized_ice_cream_sensor.ino` 파일에서 다음 부분 수정:

```cpp
// WiFi 설정 (현장에서 변경 필요)
const char* ssid = "가게_WiFi_이름";        // ← 여기 변경
const char* password = "가게_WiFi_비밀번호";  // ← 여기 변경
```

#### 2.3 디바이스 ID 설정
```cpp
String deviceID = "ICE_STORE_001"; // ← 가게별 고유 ID로 변경
```

### 3단계: ESP32 업로드

#### 3.1 보드 설정
1. **Tools** → **Board** → **ESP32 Arduino** → **ESP32 Dev Module**
2. **Tools** → **Port** → [ESP32 연결된 포트 선택]
3. **Tools** → **Upload Speed** → **115200**

#### 3.2 코드 업로드
1. **Sketch** → **Upload** (Ctrl+U)
2. 업로드 완료 후 **Tools** → **Serial Monitor** (Ctrl+Shift+M)
3. **Baud Rate**: 115200 설정

#### 3.3 동작 확인
시리얼 모니터에서 다음 메시지 확인:
```
=== 24시간 무인 아이스크림 가게 모니터링 시스템 ===
Device: ICE_STORE_001
특징 기반 데이터 전송 모드
압축기 On/Off 시계열 분석
WiFi connecting...
WiFi connected! IP: 192.168.1.100
I2S ready
System ready
```

### 4단계: 서버 설정

#### 4.1 서버 접속
```bash
ssh -i signalcraft-new.pem ubuntu@3.39.124.0
cd /var/www/smartcompressor
```

#### 4.2 서버 상태 확인
```bash
pm2 status
curl http://localhost:3000/api/esp32/status
```

#### 4.3 새로운 API 추가 (이미 완료됨)
```bash
# ESP32 특징 API가 이미 추가되어 있음
# 확인: curl http://localhost:3000/api/esp32/status
```

### 5단계: 현장 설치

#### 5.1 하드웨어 연결
```
ESP32 핀 연결:
- GPIO 26 → I2S 데이터 입력 (마이크)
- GPIO 25 → I2S 워드 클럭
- GPIO 27 → I2S 비트 클럭
- GPIO 0 → 부트 버튼 (제어용)
- GPIO 2 → 상태 LED
- GPIO 4 → 상태 LED 2
```

#### 5.2 전원 연결
1. **USB 어댑터** 연결
2. **220V 콘센트**에 연결
3. **LED 상태** 확인

#### 5.3 WiFi 연결 확인
1. **시리얼 모니터**로 연결 상태 확인
2. **LED 패턴**으로 상태 확인
3. **웹 대시보드**에서 데이터 수신 확인

## 🔍 테스트 및 검증

### 1. ESP32 테스트
```cpp
// 시리얼 모니터에서 확인할 내용:
=== AUDIO FEATURES ===
RMS: 1250.50
Spectral Centroid: 0.450
Compressor State: ON
Anomaly Score: 0.150
Temperature Est: 23.5°C
Efficiency: 0.850
```

### 2. 서버 테스트
```bash
# 서버 상태 확인
curl http://localhost:3000/api/esp32/status

# 특징 데이터 수신 확인
tail -f /var/www/smartcompressor/logs/nodejs_out.log | grep "ESP32 특징"
```

### 3. 웹 대시보드 테스트
- **URL**: `https://signalcraft.kr/audio-research`
- **기능**: 실시간 데이터 확인

## 🚨 문제 해결

### ESP32 연결 문제

#### WiFi 연결 실패
```cpp
// 해결 방법:
1. WiFi 신호 강도 확인
2. 비밀번호 정확성 확인
3. 2.4GHz 대역 사용 확인
4. 방화벽 설정 확인
```

#### 업로드 실패
```cpp
// 해결 방법:
1. 서버 상태 확인: curl http://localhost:3000/api/esp32/status
2. 네트워크 연결 확인
3. ESP32 재부팅
```

### 서버 문제

#### PM2 서버 중지
```bash
pm2 restart signalcraft-nodejs
pm2 logs signalcraft-nodejs --lines 20
```

#### 데이터베이스 오류
```bash
# SQLite 데이터베이스 확인
sqlite3 /var/www/smartcompressor/database/smartcompressor.db
.tables
.quit
```

## 📊 성능 모니터링

### 데이터 전송량
- **전송 주기**: 10초마다
- **데이터 크기**: 약 1KB/회
- **일일 전송량**: 약 8.6MB/일

### 메모리 사용량
- **ESP32 RAM**: 약 200KB
- **서버 메모리**: 특징 데이터당 1KB

### 저장 공간
- **24시간 기준**: 8.6MB/일
- **월간 사용량**: 약 260MB/월

## 🔄 유지보수

### 정기 점검 (주 1회)
1. **서버 상태** 확인
2. **데이터 수신** 확인
3. **디스크 공간** 확인
4. **로그 파일** 정리

### 데이터 정리 (월 1회)
```bash
# 30일 이상 된 데이터 삭제
find /var/www/smartcompressor/data/features -name "*.json" -mtime +30 -delete
```

### 펌웨어 업데이트
1. **새 코드** 다운로드
2. **WiFi 설정** 확인
3. **업로드** 및 **테스트**

## 📞 지원

### 긴급 상황
- **ESP32 재부팅**: 전원 뽑았다가 다시 연결
- **서버 재시작**: `pm2 restart signalcraft-nodejs`
- **WiFi 재연결**: ESP32 부트 버튼 3초 이상 누르기

### 로그 수집
문제 발생 시 다음 로그 수집:
```bash
# ESP32 시리얼 로그
# 서버 PM2 로그
pm2 logs signalcraft-nodejs --lines 100 > server_logs.txt

# 시스템 상태
pm2 status > system_status.txt
df -h > disk_usage.txt
```

---

**🎉 설치 완료!**

이제 24시간 무인 아이스크림 가게의 냉동고를 안전하게 모니터링할 수 있습니다! 🍦
