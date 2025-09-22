# IoT 센서 시스템 문서

## 개요

Tesla와 Nest 스타일의 무인 아이스크림 매장용 실시간 센서 데이터 수집 시스템입니다.

## 주요 기능

### 1. ESP32 기반 센서 데이터 수집
- **마이크로폰 (I2S)**: 압축기 소음 수집
- **온도 센서 (DS18B20)**: 냉동고 온도 모니터링
- **진동 센서 (ADXL345)**: 압축기 진동 감지
- **전력 센서 (ACS712)**: 전력 소비량 측정

### 2. 실시간 데이터 스트리밍
- **WebSocket 기반**: 실시간 데이터 전송
- **자동 재연결**: 네트워크 장애 시 자동 복구
- **데이터 버퍼링**: 네트워크 지연 대응

### 3. 센서 데이터 저장소
- **SQLite 데이터베이스**: 시계열 데이터 저장
- **배치 처리**: 효율적인 데이터 저장
- **자동 정리**: 오래된 데이터 자동 삭제

### 4. 센서 상태 모니터링
- **실시간 건강도 평가**: 0-100점 건강도 점수
- **이상 감지**: 온도, 진동, 전력, 소음 이상 감지
- **알림 시스템**: 이상 상황 실시간 알림

### 5. 펌웨어 OTA 업데이트
- **원격 업데이트**: Tesla 스타일 OTA 업데이트
- **버전 관리**: 펌웨어 버전 추적
- **롤백 기능**: 문제 발생 시 이전 버전으로 복구

## 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ESP32 센서    │    │   Flask 서버    │    │   웹 대시보드   │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ 마이크로폰  │ │    │ │ 센서 데이터 │ │    │ │ 실시간 모니터│ │
│ │ 온도 센서   │ │───▶│ │ 서비스      │ │───▶│ │ 이상 감지   │ │
│ │ 진동 센서   │ │    │ │             │ │    │ │ 펌웨어 관리 │ │
│ │ 전력 센서   │ │    │ └─────────────┘ │    │ └─────────────┘ │
│ └─────────────┘ │    │ ┌─────────────┐ │    └─────────────────┘
└─────────────────┘    │ │ 실시간 스트림│ │
                       │ │ 서비스      │ │
                       │ └─────────────┘ │
                       │ ┌─────────────┐ │
                       │ │ 모니터링    │ │
                       │ │ 서비스      │ │
                       │ └─────────────┘ │
                       │ ┌─────────────┐ │
                       │ │ OTA 업데이트│ │
                       │ │ 서비스      │ │
                       │ └─────────────┘ │
                       └─────────────────┘
```

## API 엔드포인트

### 센서 데이터
- `POST /api/iot/sensors/data` - 센서 데이터 수신
- `GET /api/iot/sensors/data/<device_id>` - 센서 데이터 조회
- `GET /api/iot/sensors/health/<device_id>` - 디바이스 건강 상태
- `GET /api/iot/sensors/anomalies` - 이상 감지 결과 조회

### 펌웨어 관리
- `GET /api/iot/firmware/versions` - 펌웨어 버전 조회
- `POST /api/iot/firmware/update` - 펌웨어 업데이트 시작
- `GET /api/iot/firmware/update/<device_id>` - 업데이트 상태 조회
- `POST /api/iot/firmware/rollback` - 펌웨어 롤백

### 시스템 상태
- `GET /api/iot/sensors/status` - 센서 시스템 상태
- `GET /api/iot/devices` - 디바이스 목록
- `POST /api/iot/cleanup` - 오래된 데이터 정리

## 사용법

### 1. 서버 시작
```bash
python app.py
```

### 2. ESP32 펌웨어 업로드
```bash
# Arduino IDE에서 signalcraft_sensor_firmware.ino 업로드
# WiFi 설정 수정 후 업로드
```

### 3. 센서 데이터 전송
```python
import requests

data = {
    "device_id": "ESP32_001",
    "timestamp": 1640995200.0,
    "temperature": -18.5,
    "vibration": {"x": 0.2, "y": 0.1, "z": 0.3},
    "power_consumption": 45.2,
    "audio_level": 150
}

response = requests.post("http://localhost:8000/api/iot/sensors/data", json=data)
```

### 4. 디바이스 상태 조회
```python
response = requests.get("http://localhost:8000/api/iot/sensors/health/ESP32_001")
health = response.json()['health']
print(f"건강도: {health['overall_health']:.1f}%")
```

### 5. 펌웨어 업데이트
```python
update_data = {
    "device_id": "ESP32_001",
    "target_version": "1.1.0"
}

response = requests.post("http://localhost:8000/api/iot/firmware/update", json=update_data)
```

## 설정

### ESP32 설정
```cpp
// WiFi 설정
const char* ssid = "Signalcraft_IoT";
const char* password = "signalcraft2024";

// 서버 설정
const char* server_host = "signalcraft.kr";
const int server_port = 8080;
```

### 서버 설정
```python
# 데이터베이스 경로
DB_PATH = 'data/sensor_data.db'

# 펌웨어 디렉토리
FIRMWARE_DIR = 'data/firmware'

# 모니터링 설정
HEALTH_CHECK_INTERVAL = 30  # 초
OFFLINE_THRESHOLD = 300     # 초
```

## 모니터링 지표

### 디바이스 건강도
- **0-30**: 위험 (빨간색)
- **31-50**: 경고 (주황색)
- **51-70**: 주의 (노란색)
- **71-100**: 정상 (초록색)

### 이상 감지 임계값
- **온도**: -25°C ~ 5°C (정상), 5°C ~ 10°C (경고), 10°C+ (위험)
- **진동**: 0.5g 이하 (정상), 1.0g 이하 (경고), 2.0g+ (위험)
- **전력**: 70% 이하 (정상), 80% 이하 (경고), 95%+ (위험)
- **소음**: 200 이하 (정상), 500 이하 (경고), 1000+ (위험)

## 문제 해결

### 일반적인 문제
1. **센서 데이터가 수신되지 않음**
   - ESP32 WiFi 연결 확인
   - 서버 주소 및 포트 확인
   - 방화벽 설정 확인

2. **이상 감지가 작동하지 않음**
   - 센서 데이터 품질 확인
   - 임계값 설정 확인
   - 모니터링 서비스 상태 확인

3. **펌웨어 업데이트 실패**
   - 디바이스 연결 상태 확인
   - 펌웨어 파일 무결성 확인
   - 충분한 저장 공간 확인

### 로그 확인
```bash
# 서버 로그
tail -f logs/sensor_system.log

# 디바이스 로그 (Serial Monitor)
# Arduino IDE에서 Serial Monitor 열기
```

## 성능 최적화

### 데이터베이스 최적화
- 인덱스 활용
- 배치 처리
- 정기적인 데이터 정리

### 네트워크 최적화
- 데이터 압축
- 배치 전송
- 연결 풀링

### 메모리 최적화
- 데이터 버퍼 크기 조정
- 가비지 컬렉션 최적화
- 불필요한 데이터 정리

## 보안 고려사항

### 데이터 보안
- HTTPS 사용
- 데이터 암호화
- 접근 제어

### 디바이스 보안
- 펌웨어 서명 검증
- 안전한 업데이트
- 접근 인증

## 확장성

### 수평적 확장
- 여러 ESP32 디바이스 지원
- 로드 밸런싱
- 분산 데이터베이스

### 수직적 확장
- 더 많은 센서 타입 지원
- 고급 분석 기능
- 머신러닝 통합

## 라이선스

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.

## 지원

기술 지원이나 문의사항이 있으시면 다음으로 연락해주세요:
- 이메일: support@signalcraft.kr
- 문서: https://docs.signalcraft.kr
- 이슈 트래커: https://github.com/signalcraft/iot-sensor-system/issues
