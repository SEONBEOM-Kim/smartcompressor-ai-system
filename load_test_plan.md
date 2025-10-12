# SignalCraft 서버 부하 테스트 계획서 (코드 분석 기반 v2)

## 1. 테스트 목표 (v1과 동일)
본 부하 테스트는 `signalcraft.kr`에서 운영 중인 시스템이 실제 운영 환경에서 발생할 수 있는 최대 부하 상황을 감당할 수 있는지 검증하고, 시스템의 한계점과 병목 지점을 사전에 파악하여 안정성을 확보하는 것을 목표로 한다.

- **정량적 목표:**
    - **AI 분석 서버(Python):** 최소 30개 이상의 센서가 동시에 오디오 파일 분석을 요청하는 상황에서, 평균 응답 시간을 2초 미만으로 유지한다.
    - **인증/API 서버(Python):** 초당 100개 이상의 일반 API 요청(인증, 데이터 조회 등)을 99% 성공률로 처리한다.
- **정성적 목표:**
    - 시스템의 병목 지점(CPU, Memory, I/O, Database 등)을 명확히 식별한다.
    - 부하가 증가함에 따라 시스템 성능이 점진적으로 저하(Graceful Degradation)되는지, 아니면 급작스럽게 중단(Crash)되는지 확인한다.

## 2. 테스트 시나리오 (코드 분석 기반 수정)
**핵심 변경사항:** `overview.md`와 달리 실제 코드에서는 **인증을 포함한 대부분의 API가 Python(Flask) 서버에서 처리**됨을 확인했다. 따라서 시나리오를 Flask 서버에 집중하여 재구성한다.

### 시나리오 1: AI 오디오 분석 부하 테스트 (핵심 시나리오)
- **근거:** `app.py`에서 `/api/lightweight-analyze` 라우트를 확인했고, `routes/ai_routes.py`에서 `request.files['audio']` 코드를 통해 파일 필드명이 'audio'임을 확인함.
- **설명:** 다수의 가상 사용자가 동시에 오디오 파일을 업로드하고 AI 분석 결과를 요청하는, 시스템에서 가장 CPU 집약적인 작업을 테스트한다.
- **대상 엔드포인트:** `POST /api/lightweight-analyze` (Python/Flask)
- **부하 단계:**
    - **1단계 (Baseline):** 가상 사용자(VUs) 15명, 10분간 테스트
    - **2단계 (Target):** 가상 사용자(VUs) 30명, 10분간 테스트
    - **3단계 (Stress):** 가상 사용자(VUs) 50명, 10분간 테스트
- **요청 간격:** 각 사용자는 5초마다 한 번씩 오디오 파일(약 100KB ~ 500KB)을 `audio` 필드에 담아 `multipart/form-data` 형식으로 요청한다.

### 시나리오 2: IoT 센서 데이터 수신 부하 테스트
- **근거:** `routes/esp32_routes.py`에서 `/api/esp32/audio/upload` 엔드포인트와 `request.data`, `request.headers.get('X-Device-ID')` 코드를 확인함.
- **설명:** 다수의 ESP32 기기에서 주기적으로 센서 데이터를 서버로 전송하는 상황을 시뮬레이션한다.
- **대상 엔드포인트:** `POST /api/esp32/audio/upload` (Python/Flask)
- **부하 단계:**
    - 초당 요청 수(RPS)를 50, 100, 200으로 늘려가며 테스트
- **요청 형식:**
    - **Body:** 순수 바이너리 오디오 데이터 (Raw binary)
    - **Headers:** `X-Device-ID`, `X-Sample-Rate` 등 필수 헤더를 포함하여 전송한다.

### 시나리오 3: 사용자 인증 흐름 부하 테스트
- **근거:** `app.py`에서 `/api/auth/login`, `/api/auth/verify` 라우트가 Flask 내에 정의되어 있음을 확인함.
- **설명:** 다수의 사용자가 동시에 로그인하고, 세션/토큰을 발급받아 자신의 인증 상태를 확인하는 흐름을 테스트한다.
- **대상 엔드포인트:**
    - `POST /api/auth/login` (Python/Flask)
    - `GET /api/auth/verify` (Python/Flask)
- **부하 시나리오:**
    1.  가상 사용자 100명이 동시에 `/api/auth/login`으로 로그인을 요청한다.
    2.  로그인 성공 후 받은 쿠키(세션 정보)를 저장한다.
    3.  저장한 쿠키를 이용해 10분 동안 주기적으로 `/api/auth/verify`를 호출하여 세션 유효성을 검증한다.

## 3. 핵심 측정 지표 (v1과 동일)
- **응답 시간 (Response Time):** avg, min, max, p(95), p(99)
- **처리량 (Throughput):** `reqs/s`
- **에러율 (Error Rate):** 1% 미만 목표
- **서버 리소스 사용량:** CPU, Memory

## 4. 테스트 도구 (v1과 동일)
- **k6 (https://k6.io):** JavaScript 기반 스크립트로 복잡한 시나리오(파일 업로드, 헤더 커스터마이징, 인증 흐름) 구현에 유리.

## 5. 테스트 절차 (v1과 동일)
1.  **사전 준비:** 테스트용 오디오 파일, 사용자 계정 준비, k6 설치.
2.  **테스트 스크립트 작성:** 아래의 **코드 기반 예시**를 참고하여 각 시나리오별 스크립트 작성.
3.  **테스트 환경 구성:** Staging 서버 구성 또는 저부하 시간대 운영 서버 테스트.
4.  **테스트 실행 및 모니터링:** 낮은 부하부터 시작, 단계적으로 증강하며 결과 및 서버 리소스 기록.
5.  **결과 분석 및 보고서 작성:** 병목 지점 식별 및 개선 과제 도출.

---

### k6 스크립트 예시 (코드 분석 기반 v2)

#### 시나리오 1: `test_ai_analysis.js`
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

// 실제 파일 경로로 수정 필요
const audioFile = open('./sample_audio.wav', 'b');

export const options = {
  stages: [
    { duration: '2m', target: 15 },
    { duration: '6m', target: 15 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<2000'], // 95%의 요청이 2초 안에
    'http_req_failed': ['rate<0.01'],   // 에러율 1% 미만
  },
};

export default function () {
  const url = 'https://signalcraft.kr/api/lightweight-analyze';

  // 'routes/ai_routes.py' 분석 결과, 필드명은 'audio'임
  const data = {
    audio: http.file(audioFile, 'test.wav', 'audio/wav'),
  };

  // 인증이 필요하다면, 시나리오 3의 로그인 로직을 결합하여
  // 받은 쿠키나 토큰을 여기에 포함시켜야 함
  const res = http.post(url, data);

  check(res, {
    'is status 200': (r) => r.status === 200,
  });

  sleep(5);
}
```

#### 시나리오 2: `test_iot_upload.js`
```javascript
import http from 'k6/http';
import { check } from 'k6';

// 실제 바이너리 오디오 데이터
const audioData = open('./sample_audio.raw', 'b');

export const options = {
  scenarios: {
    iot_upload: {
      executor: 'constant-arrival-rate',
      rate: 100, // 초당 100회 요청
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 50,
      maxVUs: 200,
    },
  },
};

export default function () {
  const url = 'https://signalcraft.kr/api/esp32/audio/upload';

  // 'routes/esp32_routes.py' 분석 결과, 커스텀 헤더 사용
  const params = {
    headers: {
      'Content-Type': 'application/octet-stream',
      'X-Device-ID': `test-device-${__VU}`, // 가상 사용자별로 다른 ID 부여
      'X-Sample-Rate': '16000',
    },
  };

  const res = http.post(url, audioData, params);

  check(res, {
    'is status 200': (r) => r.status === 200,
  });
}
```