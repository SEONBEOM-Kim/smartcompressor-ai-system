# 카카오톡 알림 설정 가이드

## 🚀 카카오톡 알림 설정 방법

### 1. 카카오 개발자 계정 생성
1. [카카오 개발자 사이트](https://developers.kakao.com/) 접속
2. 카카오 계정으로 로그인
3. "내 애플리케이션" → "애플리케이션 추가"

### 2. 애플리케이션 등록
```
애플리케이션 이름: Signalcraft 알림 서비스
사업자명: (회사명)
카테고리: 기타
```

### 3. 플랫폼 설정
- **Web 플랫폼 추가**
  - 사이트 도메인: `https://signalcraft.kr`
  - Redirect URI: `https://signalcraft.kr/auth/kakao/callback`

### 4. 동의항목 설정
- **선택 동의항목**
  - 카카오톡 메시지 전송: `동의`
  - 전화번호: `동의`

### 5. REST API 키 발급
1. "앱 설정" → "앱 키" 탭
2. **REST API 키** 복사

### 6. 액세스 토큰 발급
```bash
# 카카오 API로 액세스 토큰 발급
curl -X POST "https://kauth.kakao.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_REST_API_KEY" \
  -d "redirect_uri=https://signalcraft.kr/auth/kakao/callback" \
  -d "code=AUTHORIZATION_CODE"
```

### 7. 환경변수 설정
```bash
# .env 파일에 추가
KAKAO_ACCESS_TOKEN=your_access_token_here
KAKAO_PHONE_NUMBERS=01012345678,01087654321
```

### 8. 테스트
```bash
# 카카오톡 알림 테스트
curl -X POST "http://localhost:8000/api/kakao/test" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "01012345678"}'
```

## 📱 알림 템플릿

### 압축기 이상 감지
```
🚨 압축기 이상 감지

압축기에서 비정상적인 소음이 감지되었습니다.

디바이스: ESP32_MIC_1234
시간: 2024-01-15 14:30:25
심각도: high

[상세보기] 버튼
```

### 온도 이상 감지
```
🌡️ 온도 이상 감지

냉동고 온도가 설정값을 벗어났습니다.

디바이스: ESP32_MIC_1234
시간: 2024-01-15 14:30:25
심각도: medium

[온도 확인] 버튼
```

### 연결 끊김
```
📡 연결 끊김

ESP32 디바이스 연결이 끊어졌습니다.

디바이스: ESP32_MIC_1234
시간: 2024-01-15 14:30:25

[연결 상태 확인] 버튼
```

## 🔧 API 엔드포인트

### 테스트 알림 전송
```http
POST /api/kakao/test
Content-Type: application/json

{
  "phone_number": "01012345678"
}
```

### 일반 알림 전송
```http
POST /api/kakao/send
Content-Type: application/json

{
  "phone_number": "01012345678",
  "alert_type": "compressor_anomaly",
  "device_id": "ESP32_MIC_1234",
  "severity": "high",
  "message": "압축기 이상이 감지되었습니다."
}
```

### 서비스 상태 확인
```http
GET /api/kakao/status
```

### 템플릿 목록 조회
```http
GET /api/kakao/templates
```

## 💡 장점

1. **즉시성**: 카카오톡은 실시간으로 수신
2. **높은 도달률**: 한국인 99%가 사용
3. **무료**: API 사용료 없음
4. **간편함**: 별도 앱 설치 불필요
5. **안정성**: 카카오의 안정적인 인프라

## ⚠️ 주의사항

1. **동의 필요**: 사용자가 카카오톡 메시지 수신에 동의해야 함
2. **토큰 갱신**: 액세스 토큰은 만료되므로 주기적 갱신 필요
3. **전화번호 형식**: 01012345678 형식으로 입력
4. **발송 제한**: 하루 1,000건 제한 (무료 계정)

## 🚀 자동화 설정

### ESP32에서 자동 알림
```cpp
// ESP32 펌웨어에서 이상 감지 시
void sendKakaoAlert(String message) {
    HTTPClient http;
    http.begin("http://3.39.124.0:8000/api/esp32/alert");
    http.addHeader("Content-Type", "application/json");
    
    String json = "{\"device_id\":\"" + deviceID + 
                  "\",\"alert_type\":\"compressor_anomaly\"," +
                  "\"severity\":\"high\"," +
                  "\"message\":\"" + message + "\"}";
    http.POST(json);
    http.end();
}
```

이제 ESP32에서 이상이 감지되면 자동으로 카카오톡으로 알림이 전송됩니다! 🎉
