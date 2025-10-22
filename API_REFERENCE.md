# 📚 Signalcraft AI API 레퍼런스

## 🌐 기본 정보

- **Base URL**: `https://signalcraft.kr`
- **API Version**: v1
- **Content-Type**: `application/json`

## 🔌 ESP32 센서 API

### 1. 상태 확인

#### GET `/api/esp32/status`
ESP32 센서의 현재 상태를 확인합니다.

**요청:**
```bash
curl https://signalcraft.kr/api/esp32/status
```

**응답:**
```json
{
  "status": "online",
  "timestamp": "2025-10-19T02:00:34.590Z",
  "message": "ESP32 API is working"
}
```

### 2. 특징 데이터 업로드

#### POST `/api/esp32/features`
ESP32에서 추출한 오디오 특징 데이터를 업로드합니다.

**요청:**
```bash
curl -X POST https://signalcraft.kr/api/esp32/features \
  -H "Content-Type: application/json" \
  -H "X-Device-ID: ICE_STORE_001" \
  -H "X-Store-Type: ice_cream_24h" \
  -d '{
    "device_id": "ICE_STORE_001",
    "timestamp": 1234567890,
    "rms_energy": 1250.5,
    "spectral_centroid": 0.45,
    "spectral_rolloff": 0.78,
    "zero_crossing_rate": 0.12,
    "compressor_state": 1.0,
    "anomaly_score": 0.15,
    "temperature_estimate": 23.5,
    "efficiency_score": 0.85,
    "mfcc": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
  }'
```

**응답:**
```json
{
  "success": true,
  "message": "특징 데이터 저장 완료",
  "device_id": "ICE_STORE_001",
  "timestamp": 1234567890,
  "data_size": 1024
}
```

### 3. 특징 데이터 조회

#### GET `/api/esp32/features/{deviceId}`
특정 디바이스의 특징 데이터 파일 목록을 조회합니다.

**요청:**
```bash
curl https://signalcraft.kr/api/esp32/features/ICE_STORE_001
```

**응답:**
```json
[
  {
    "filename": "features_ICE_STORE_001_1234567890.json",
    "size": 1024,
    "modified": "2025-10-19T02:00:34.590Z"
  }
]
```

### 4. 압축기 상태 변화 조회

#### GET `/api/esp32/state-changes/{deviceId}`
특정 디바이스의 압축기 상태 변화 로그를 조회합니다.

**요청:**
```bash
curl https://signalcraft.kr/api/esp32/state-changes/ICE_STORE_001
```

**응답:**
```json
[
  {
    "device_id": "ICE_STORE_001",
    "timestamp": 1234567890,
    "from_state": "OFF",
    "to_state": "ON",
    "rms_energy": 1250.5,
    "anomaly_score": 0.15,
    "efficiency_score": 0.85
  }
]
```

### 5. 이상 패턴 조회

#### GET `/api/esp32/anomalies/{deviceId}`
특정 디바이스의 이상 패턴 감지 로그를 조회합니다.

**요청:**
```bash
curl https://signalcraft.kr/api/esp32/anomalies/ICE_STORE_001
```

**응답:**
```json
[
  {
    "device_id": "ICE_STORE_001",
    "timestamp": 1234567890,
    "anomaly_score": 0.85,
    "rms_energy": 5000.0,
    "compressor_state": "ON",
    "efficiency_score": 0.25,
    "temperature_estimate": 35.5,
    "detected_at": "2025-10-19T02:00:34.590Z"
  }
]
```

## 🎵 오디오 파일 API

### 1. 오디오 파일 목록

#### GET `/api/esp32/files`
업로드된 오디오 파일 목록을 조회합니다.

**요청:**
```bash
curl https://signalcraft.kr/api/esp32/files
```

**응답:**
```json
[
  {
    "name": "esp32_ICE_STORE_001_1234567890.raw",
    "size": 40000,
    "modified": "2025-10-19T02:00:34.590Z",
    "deviceId": "ICE_STORE_001",
    "timestamp": "1234567890",
    "analysis": {
      "is_overload": false,
      "confidence": 0.85,
      "message": "정상 작동 중입니다",
      "processing_time_ms": 25.5
    }
  }
]
```

### 2. 오디오 파일 다운로드

#### GET `/api/esp32/download/{filename}`
특정 오디오 파일을 다운로드합니다.

**요청:**
```bash
curl -O https://signalcraft.kr/api/esp32/download/esp32_ICE_STORE_001_1234567890.raw
```

**응답:**
- 파일 다운로드 (binary)

### 3. 오디오 파일 삭제

#### DELETE `/api/esp32/delete/{filename}`
특정 오디오 파일을 삭제합니다.

**요청:**
```bash
curl -X DELETE https://signalcraft.kr/api/esp32/delete/esp32_ICE_STORE_001_1234567890.raw
```

**응답:**
```json
{
  "success": true,
  "message": "파일이 삭제되었습니다."
}
```

## 🌐 웹 대시보드

### 1. 오디오 연구 페이지

#### GET `/audio-research`
웹 기반 오디오 분석 대시보드에 접속합니다.

**URL:** `https://signalcraft.kr/audio-research`

**기능:**
- 업로드된 오디오 파일 목록
- 실시간 오디오 재생
- 웨이브폼 시각화
- 분석 결과 표시
- 통계 차트

### 2. 파일 직접 접근

#### GET `/uploads/esp32/{filename}`
ESP32 업로드 파일에 직접 접근합니다.

**URL:** `https://signalcraft.kr/uploads/esp32/esp32_ICE_STORE_001_1234567890.raw`

## 📊 데이터 구조

### 특징 데이터 (AudioFeatures)

| 필드 | 타입 | 설명 |
|------|------|------|
| `device_id` | string | 디바이스 고유 ID |
| `timestamp` | number | 타임스탬프 (밀리초) |
| `rms_energy` | number | RMS 에너지 (소음 강도) |
| `spectral_centroid` | number | 스펙트럼 중심 (0-1) |
| `spectral_rolloff` | number | 스펙트럼 롤오프 (0-1) |
| `zero_crossing_rate` | number | 제로 크로싱 비율 (0-1) |
| `compressor_state` | number | 압축기 상태 (0=OFF, 1=ON) |
| `anomaly_score` | number | 이상 점수 (0-1) |
| `temperature_estimate` | number | 추정 온도 (°C) |
| `efficiency_score` | number | 효율성 점수 (0-1) |
| `mfcc` | array | MFCC 특징 (13차원) |

### 압축기 상태 변화 (CompressorStateChange)

| 필드 | 타입 | 설명 |
|------|------|------|
| `device_id` | string | 디바이스 고유 ID |
| `timestamp` | number | 타임스탬프 |
| `from_state` | string | 이전 상태 ("ON" 또는 "OFF") |
| `to_state` | string | 현재 상태 ("ON" 또는 "OFF") |
| `rms_energy` | number | RMS 에너지 |
| `anomaly_score` | number | 이상 점수 |
| `efficiency_score` | number | 효율성 점수 |

### 이상 패턴 (Anomaly)

| 필드 | 타입 | 설명 |
|------|------|------|
| `device_id` | string | 디바이스 고유 ID |
| `timestamp` | number | 타임스탬프 |
| `anomaly_score` | number | 이상 점수 (0-1) |
| `rms_energy` | number | RMS 에너지 |
| `compressor_state` | string | 압축기 상태 |
| `efficiency_score` | number | 효율성 점수 |
| `temperature_estimate` | number | 추정 온도 |
| `detected_at` | string | 감지 시간 (ISO 8601) |

## 🔒 인증 및 보안

### 헤더 요구사항

모든 API 요청에는 다음 헤더가 필요합니다:

```http
Content-Type: application/json
X-Device-ID: {device_id}
```

### CORS 설정

웹 브라우저에서 API 호출 시 CORS가 설정되어 있습니다.

### Rate Limiting

현재 Rate Limiting은 적용되지 않습니다. 향후 추가 예정입니다.

## 📈 성능 정보

### 데이터 전송량
- **특징 데이터**: 약 1KB/회
- **전송 주기**: 10초마다
- **일일 전송량**: 약 8.6MB/일

### 응답 시간
- **상태 확인**: < 100ms
- **특징 업로드**: < 500ms
- **데이터 조회**: < 200ms

### 저장 공간
- **특징 데이터**: 1KB/회
- **상태 변화 로그**: 200B/회
- **이상 패턴 로그**: 300B/회

## 🚨 오류 코드

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 요청 성공 |
| 400 | Bad Request | 잘못된 요청 |
| 404 | Not Found | 리소스를 찾을 수 없음 |
| 500 | Internal Server Error | 서버 내부 오류 |

### 오류 응답 형식

```json
{
  "success": false,
  "message": "오류 메시지",
  "error": "상세 오류 정보"
}
```

## 📞 지원

API 사용 중 문제가 발생하면 다음 정보와 함께 문의하세요:

1. **요청 URL**
2. **요청 헤더**
3. **요청 본문**
4. **응답 코드**
5. **오류 메시지**

---

**📚 이 API 레퍼런스를 참고하여 Signalcraft AI 시스템을 효과적으로 활용하세요!**
