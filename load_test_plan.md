# SignalCraft 서버 부하 테스트 계획서 (v4 - suggestion.md 반영)

## 1. 테스트 목표 (v3과 동일)
- **정량적 목표:**
    - **AI 분석 서버(Python):** 최소 30개 이상의 센서가 동시에 오디오 파일 분석을 요청하는 상황에서, 평균 응답 시간을 2초 미만으로 유지한다. (`test_security_load.py`의 heavy load 기준과 부합)
    - **인증 서버(Node.js):** 초당 100개 이상의 인증 요청을 99% 성공률로 처리한다.
- **정성적 목표:**
    - 시스템의 병목 지점을 명확히 식별한다.
    - 부하 증가에 따른 시스템의 동작(점진적 저하 또는 급작스런 중단)을 확인한다.
    - 502 에러 등 장애 발생 시 PM2를 통한 자동 복구 메커니즘이 정상 동작하는지 검증한다.

## 2. 테스트 시나리오 (`suggestion.md` 기반 전면 수정)

### 시나리오 1: AI 오디오 분석 부하 테스트 (Python/Flask)
- **설명:** 웹 대시보드에서 다수의 사용자가 동시에 오디오 파일을 업로드하는 상황을 시뮬레이션한다.
- **대상 엔드포인트:** `POST /api/lightweight-analyze`
- **부하 단계 (센서 수 기준):**
    - **1단계 (Baseline):** 센서 15대 (VUs: 15)
    - **2단계 (Target):** 센서 30대 (VUs: 30)
- **동작:** 각 센서(VU)는 10분 동안 5초마다 오디오 파일을 `multipart/form-data` 형식으로 요청한다.

### 시나리오 2: IoT 센서 데이터 수신 부하 테스트 (Python/Flask)
- **설명:** **(수정)** 실제 IoT 센서가 전송하는 것과 동일한 **JSON 형식**의 데이터를 주기적으로 전송하는 상황을 시뮬레이션한다.
- **대상 엔드포인트:** **(수정)** `POST /api/iot/sensors/data`
- **부하 단계 (센서 수 기준):**
    - **1단계 (Baseline):** 센서 15대 (VUs: 15)
    - **2단계 (Target):** 센서 30대 (VUs: 30)
- **동작:** 각 센서(VU)는 10분 동안 10초마다 `test_iot_system.py`에서 확인된 JSON 페이로드를 전송한다.

### 시나리오 3: 사용자 인증 부하 테스트 (Node.js/Express)
- **설명:** **(명확화)** 듀얼 백엔드 아키텍처의 메인 인증 서버인 **Node.js Express 서버**의 성능을 테스트한다.
- **대상 엔드포인트:** `POST /api/auth/login`, `GET /api/auth/verify`
- **부하 시나리오:** 가상 사용자 100명이 동시에 로그인 후, 발급받은 쿠키를 이용해 10분간 주기적으로 인증 상태를 확인한다.

### 시나리오 4: 동시 세션 관리 부하 테스트 (신규 추가)
- **설명:** 다수의 사용자가 로그인 상태를 유지하며 시스템을 동시에 사용하는 상황을 시뮬레이션한다.
- **대상 엔드포인트:** `GET /api/auth/verify` (Node.js/Express)
- **부하 시나리오:**
    - 가상 사용자 100명이 테스트 시작과 동시에 모두 로그인된 상태(쿠키 보유)로 시작한다.
    - 10분 동안 각 사용자는 3~10초 사이의 임의 간격으로 자신의 인증 상태를 지속적으로 확인한다.
- **성공 기준:** 전체 요청의 90% 이상 성공.

## 3. 핵심 측정 지표 (보완)
- **응답 시간 (Response Time):** avg, min, max, p(95), p(99)
- **처리량 (Throughput):** `reqs/s`
- **에러율 (Error Rate):** 1% 미만 목표
- **서버 리소스 사용량:**
    - CPU 사용률 (%)
    - **(추가)** 메모리 사용량 및 증가율 (Memory Growth Rate)
    - **(추가)** 디스크 I/O
- **(추가) 데이터베이스 상태:**
    - DB 연결 풀(Connection Pool) 사용률 및 대기 시간

## 4. 테스트 도구 (v3과 동일)
- **k6 (https://k6.io)**

## 5. 테스트 절차 (v3과 동일)
1. 사전 준비
2. 테스트 스크립트 작성 (아래 v4 예시 참고)
3. 테스트 환경 구성
4. 테스트 실행 및 모니터링
5. 결과 분석 및 보고서 작성

---

### k6 스크립트 예시 (v4 - suggestion.md 반영)

#### 시나리오 2 수정: `test_iot_json_upload.js`
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 15 }, // 1분간 15대까지 증가 (테스트 시간 단축)
    { duration: '3m', target: 15 }, // 3분간 유지
    { duration: '1m', target: 0 },
  ],
};

export default function () {
  // suggestion.md에서 제안된 실제 엔드포인트와 페이로드
  const url = 'https://signalcraft.kr/api/iot/sensors/data';
  const payload = JSON.stringify({
    device_id: `test-device-${__VU}`,
    timestamp: Date.now() / 1000,
    temperature: -18.5 + (Math.random() * 2),
    vibration: { x: 0.2, y: 0.1, z: 0.3 },
    power_consumption: 45.2,
    audio_level: 150,
    sensor_quality: 0.95
  });
  const params = {
    headers: { 'Content-Type': 'application/json' }
  };

  const res = http.post(url, payload, params);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(10);
}
```

#### 시나리오 4 신규: `test_concurrent_sessions.js`
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    concurrent_sessions: {
      executor: 'per-vu-iterations',
      vus: 100, // 100명의 동시 사용자
      iterations: 30, // 각 사용자가 30회 반복
      maxDuration: '10m',
    },
  },
  thresholds: {
    'http_req_failed': ['rate<0.1'], // 실패율 10% 미만
  },
};

// setup 함수를 통해 테스트 시작 전 미리 로그인하여 쿠키를 확보해야 함
// export function setup() { ... 로그인 로직 ... return { cookies }; }

export default function (data) {
  const url = 'https://signalcraft.kr/api/auth/verify';
  
  // TODO: setup 단계에서 얻은 실제 로그인 쿠키를 여기에 전달해야 함
  // const jar = http.cookieJar();
  // jar.set(url, 'session', data.cookies[__VU]); // 사용자별 쿠키 설정

  const res = http.get(url);
  check(res, { 'status is 200': (r) => r.status === 200 });

  // 3~10초 사이 랜덤 대기
  sleep(Math.random() * 7 + 3);
}
```