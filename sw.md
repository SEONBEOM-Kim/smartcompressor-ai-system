---

# 🐍 SignalCraft Gunicorn 도입 설계 플랜

> 작성 목적: Python 서버가 관리되지 않는 백그라운드 프로세스로 실행되고 있는 문제를 해결하고, Node.js와 함께 PM2 기반 통합 프로세스 관리 체계를 구축하기 위한 최종 설계안입니다.
> 

---

## 🎯 1. 개요 및 목표

### 🔍 현황 진단

- ✅ Node.js 서버는 `ecosystem.config.js`를 통해 **PM2로 안정적으로 관리**되고 있음
- ❌ Python 서버는 `pkill` 후 단순 백그라운드 실행(`&`) → **자동 복구, 로그 관리, 상태 모니터링 불가**

### 🎯 최종 목표

- Python 서버를 **Gunicorn + PM2**로 안정적으로 실행
- Node.js와 Python 서버를 **하나의 `ecosystem.config.js`로 통합 관리**
- GitHub Actions 배포 자동화와 연동하여 **Zero-downtime 배포** 실현

---

## 🛠️ 2. 단계별 실행 계획

### ✅ 1단계: Gunicorn 설치 및 의존성 관리

```bash
pip install gunicorn
pip freeze > requirements.txt

```

- `requirements.txt`에 `gunicorn==x.x.x` 라인 추가됨

---

### ✅ 2단계: Gunicorn 실행 설정 파일 작성

**`gunicorn.conf.py`**

```python
import multiprocessing

bind = "127.0.0.1:8001"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
accesslog = "-"
errorlog = "-"
timeout = 120
wsgi_app = "app:create_app()"

```

- 포트 충돌 방지를 위해 `8001` 포트 사용
- 로그는 표준 출력으로 → PM2가 로그 수집 가능

---

### ✅ 3단계: PM2 설정 파일 통합 (`ecosystem.config.js`)

```jsx
module.exports = {
  apps: [
    {
      name: 'signalcraft-nodejs',
      script: 'server.js',
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'signalcraft-python',
      script: 'gunicorn',
      args: '-c gunicorn.conf.py',
      interpreter: '/home/ubuntu/smartcompressor_env/bin/python',
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env_production: {
        // 필요 시 환경 변수 추가
      }
    }
  ]
};

```

- 하나의 PM2 설정 파일로 Node.js + Python 서버 통합 관리 가능

---

### ✅ 4단계: Nginx 리버스 프록시 설정 확인

```
location ~ ^/(api/ai|api/iot|api/lightweight-analyze|api/flask) {
    proxy_pass http://127.0.0.1:8001;
    # 기타 헤더 및 설정 유지
}

```

- Gunicorn 포트(`8001`)와 일치하는지 반드시 확인

---

### ✅ 5단계: GitHub Actions 배포 스크립트 수정 (`auto-deploy.yml`)

```yaml
- name: Deploy to EC2
  script: |
    # 기존 서비스 중지 및 재시작
    echo "🛑 기존 서비스 중지 및 재시작..."
    pm2 reload ecosystem.config.js --env production || pm2 start ecosystem.config.js --env production

    echo "📊 PM2 프로세스 상태 확인..."
    pm2 status

```

- 기존 `pkill` 방식 제거
- PM2 기반 재시작으로 **중단 없는 배포(Zero-downtime)** 실현

---

## ✅ 기대 효과 요약


# 🚦 SignalCraft 서버 부하 테스트 계획서

> 
> 
> 
> **작성 목적:** 시스템의 성능 한계 및 병목 지점 식별, 자동 복구 메커니즘 검증
> 

---

## 🎯 1. 테스트 목표

### 📊 정량적 목표

- **AI 분석 서버 (Python)**
→ 30개 이상의 센서가 동시에 오디오 분석 요청 시, 평균 응답 시간 **2초 미만 유지**
- **인증 서버 (Node.js)**
→ 초당 100개 이상의 인증 요청을 **99% 성공률**로 처리

### 🔍 정성적 목표

- 병목 지점 식별
- 부하 증가 시 시스템의 동작 패턴 확인 (점진적 저하 vs 급작스런 중단)
- 장애 발생 시 **PM2 자동 복구** 정상 동작 여부 검증

---

## 🧪 2. 테스트 시나리오

### ✅ 시나리오 1: AI 오디오 분석 부하 테스트 (Python/Flask)

- **엔드포인트:** `POST /api/lightweight-analyze`
- **부하 단계:**
    - 1단계: 센서 15대 (VUs: 15)
    - 2단계: 센서 30대 (VUs: 30)
- **동작:** 각 센서가 10분 동안 5초 간격으로 오디오 파일 업로드 (`multipart/form-data`)

---

### ✅ 시나리오 2: IoT 센서 데이터 수신 부하 테스트 (Python/Flask)

- **엔드포인트:** `POST /api/iot/sensors/data`
- **부하 단계:**
    - 1단계: 센서 15대 (VUs: 15)
    - 2단계: 센서 30대 (VUs: 30)
- **동작:** 각 센서가 10분 동안 10초 간격으로 JSON 페이로드 전송

---

### ✅ 시나리오 3: 사용자 인증 부하 테스트 (Node.js/Express)

- **엔드포인트:** `POST /api/auth/login`, `GET /api/auth/verify`
- **동작:**
    - 100명의 가상 사용자가 동시에 로그인
    - 로그인 후 10분간 쿠키 기반 인증 상태 확인 반복

---

### ✅ 시나리오 4: 동시 세션 관리 부하 테스트 (신규)

- **엔드포인트:** `GET /api/auth/verify`
- **동작:**
    - 100명의 사용자가 로그인된 상태로 시작
    - 10분간 3~10초 간격으로 인증 상태 확인
- **성공 기준:** 전체 요청의 **90% 이상 성공**

---

## 📐 3. 핵심 측정 지표

| 항목 | 세부 지표 |
| --- | --- |
| 응답 시간 | avg, min, max, p(95), p(99) |
| 처리량 | `reqs/s` |
| 에러율 | 1% 미만 목표 |
| 서버 리소스 | CPU 사용률, 메모리 사용량 및 증가율, 디스크 I/O |
| DB 상태 | Connection Pool 사용률 및 대기 시간 |

---

## 🧰 4. 테스트 도구

- **k6**
→ 고성능 부하 테스트 도구
→ [https://k6.io](https://k6.io/)

---

## 🧭 5. 테스트 절차

1. 사전 준비
2. 테스트 스크립트 작성
3. 테스트 환경 구성
4. 테스트 실행 및 모니터링
5. 결과 분석 및 보고서 작성

---

## 📄 k6 스크립트 예시

### 📌 시나리오 2: `test_iot_json_upload.js`

```jsx
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 15 },
    { duration: '3m', target: 15 },
    { duration: '1m', target: 0 },
  ],
};

export default function () {
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
  const params = { headers: { 'Content-Type': 'application/json' } };
  const res = http.post(url, payload, params);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(10);
}

```

---

### 📌 시나리오 4: `test_concurrent_sessions.js`

# 🛠️ SignalCraft Sentry 연동 실행 계획서

> 목적: 실시간 에러 트래킹 및 성능 모니터링을 위해 Sentry를 Flask 백엔드와 Node.js 서버에 통합하여, 프로덕션 환경에서 발생하는 문제를 신속하게 파악하고 해결
> 

---

## 🎯 1. 목표

- 실시간 에러 감지 및 알림
- API 응답 시간 및 처리량 등 성능 지표 추적
- 사용자 컨텍스트 기반 디버깅 정보 확보
- 재현이 어려운 에러에 대한 로그 및 스택 트레이스 확보

---

## 🧾 2. 사전 준비

- Sentry 계정 생성 및 로그인
- Flask, Node.js 각각에 대해 프로젝트 생성
- 각 프로젝트의 DSN 키를 `.env`에 추가

---

## 🧩 3. 단계별 실행 계획

### ✅ 1단계: 의존성 추가

**Python (`requirements.txt`)**

```
sentry-sdk[flask]==1.40.0

```

**Node.js (`package.json`)**

```json
"dependencies": {
  "@sentry/node": "^7.100.0",
  "@sentry/profiling-node": "^1.3.0"
}

```

```bash
pip install -r requirements.txt
npm install

```

---

### ✅ 2단계: 환경 변수 설정

**`.env`**

```
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
APP_VERSION=1.0.0

```

---

### ✅ 3단계: Flask 연동

**`app.py`**

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    environment=os.getenv('FLASK_ENV', 'development'),
    release=os.getenv('APP_VERSION', 'unknown')
)

```

---

### ✅ 4단계: Node.js 연동

**`server.js`**

```jsx
const Sentry = require("@sentry/node");
const { ProfilingIntegration } = require("@sentry/profiling-node");

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new ProfilingIntegration(),
  ],
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
  environment: process.env.NODE_ENV || 'development',
});

```

---

### ✅ 5단계: 중앙 에러 트래킹 서비스 생성

**`admin/services/error_tracking_service.py`**

```python
class ErrorTrackingService:
    @staticmethod
    def capture_exception(exception, context=None):
        with sentry_sdk.push_scope() as scope:
            if context:
                scope.set_context("extra_info", context)
            sentry_sdk.capture_exception(exception)

    @staticmethod
    def capture_message(message, level='info'):
        sentry_sdk.capture_message(message, level=level)

```

---

### ✅ 6단계: 에러 핸들러 적용

**`routes/ai_routes.py`**

```python
try:
    # 기존 로직
    pass
except Exception as e:
    ErrorTrackingService.capture_exception(
        e,
        context={
            'endpoint': '/api/lightweight-analyze',
            'user_id': session.get('user_id'),
        }
    )
    return jsonify({'error': 'Internal Server Error'}), 500

```

---

### ✅ 7단계: PM2 설정 업데이트

**`ecosystem.config.js`**

```jsx
env: {
  SENTRY_DSN: process.env.SENTRY_DSN
},
env_production: {
  SENTRY_DSN: process.env.SENTRY_DSN
}

```

---

### ✅ 8단계: 배포 스크립트 수정 (Sentry CLI)

```bash
export SENTRY_AUTH_TOKEN=your_sentry_auth_token
export SENTRY_ORG=your_sentry_organization
APP_VERSION=$(node -p "require('./package.json').version")

sentry-cli releases new $APP_VERSION
sentry-cli releases set-commits $APP_VERSION --auto

# 기존 배포 로직

sentry-cli releases finalize $APP_VERSION

```

---

## ✅ 4. 기대 효과

# ⚙️ SignalCraft 비동기 처리(Celery) 도입 실행 계획서

> 목적: AI 분석 로직을 Celery 기반 비동기 처리로 전환하여 UX 개선 및 서버 동시 처리 능력 향상
> 

---

## 🎯 1. 도입 목표

- 기존 `ensemble_ai_service.predict_ensemble()` 호출이 **HTTP 요청을 블로킹**하는 문제 해결
- Redis 기반 Celery 태스크 큐를 도입하여 **AI 분석을 백그라운드에서 처리**
- 사용자에게 빠른 응답을 제공하고, 분석 결과는 **비동기적으로 조회 가능**하도록 설계

---

## 🔍 2. 현황 진단

| 항목 | 상태 |
| --- | --- |
| AI 분석 방식 | 동기 처리 → HTTP 응답 지연 발생 |
| Redis 인프라 | `docker-compose.yml`에 이미 구성됨 |
| Flask 구조 | `create_app()` 팩토리 패턴 사용 중 |
| 의존성 | `celery`, `redis` 패키지 설치 필요 |

---

## 🛠️ 3. 단계별 실행 계획

### ✅ 1단계: 의존성 추가

```
celery==5.3.6
redis==5.0.1

```

```bash
pip install -r requirements.txt

```

---

### ✅ 2단계: Celery 앱 초기화

**`celery_worker.py`**

```python
from celery import Celery
from app import create_app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        include=['tasks']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

flask_app = create_app()
celery_app = make_celery(flask_app)

```

**`app.py` 설정 추가**

```python
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

```

---

### ✅ 3단계: 비동기 태스크 정의

**`tasks.py`**

```python
@celery_app.task(bind=True, name='tasks.analyze_audio_task')
def analyze_audio_task(self, file_path: str):
    try:
        self.update_state(state='PROGRESS', meta={'progress': 10})
        result = ensemble_ai_service.predict_ensemble(file_path)
        self.update_state(state='PROGRESS', meta={'progress': 90})
        return {'status': 'success', 'result': result}
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

```

---

### ✅ 4단계: API 엔드포인트 수정

**`routes/ai_routes.py`**

```python
task = analyze_audio_task.delay(file_path)
return jsonify({'task_id': task.id}), 202

```

---

### ✅ 5단계: 결과 조회 API 추가

**`routes/task_routes.py`**

```python
@task_bp.route('/analyze/result/<task_id>', methods=['GET'])
def get_analysis_result(task_id):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        if task_result.successful():
            return jsonify({'status': 'SUCCESS', 'result': task_result.get()})
        else:
            return jsonify({'status': 'FAILURE', 'error': str(task_result.info)}), 500
    else:
        return jsonify({'status': task_result.state, 'progress': task_result.info.get('progress', 0)}), 202

```

**`app.py` Blueprint 등록**

```python
from routes.task_routes import task_bp
app.register_blueprint(task_bp)

```

---

### ✅ 6단계: Celery Worker 실행 설정

**`ecosystem.config.js`**

```jsx
{
  name: 'celery-worker',
  script: 'celery',
  args: '-A celery_worker.celery_app worker --loglevel=info --concurrency=2',
  interpreter: 'python3',
  autorestart: true,
  max_memory_restart: '1G',
}

```

---

### ✅ 7단계: 프론트엔드 Polling 로직 추가

- 클라이언트에서 `task_id`를 기반으로 `/api/analyze/result/<task_id>`를 주기적으로 조회
- 진행 상태(`PROGRESS`, `SUCCESS`, `FAILURE`)에 따라 UI 업데이트

---

### ✅ 8단계: 배포 스크립트 업데이트

**`.github/workflows/auto-deploy.yml`**

```bash
pm2 restart ecosystem.config.js

```

---

### ✅ 9단계: 통합 테스트

- 오디오 업로드 → 비동기 태스크 생성 → 결과 조회까지 전체 흐름 테스트
- Redis, Celery, Flask, 프론트엔드 간 연동 확인

---

## ⚠️ 4. 주의사항

| 항목 | 설명 |
| --- | --- |
| 메모리 관리 | `--concurrency` 값은 서버 사양에 맞게 조정 |
| 파일 정리 | `finally` 블록에서 임시 파일 삭제 확인 |
| 타임아웃 | 분석 시간이 길어질 경우 Celery 태스크 타임아웃 설정 필요 |

---


# Answer

제시하신 백엔드 개선 플랜은 **전반적으로 타당하지만, 현재 프로젝트 구조를 고려할 때 일부 수정과 우선순위 조정이 필요**합니다.

## 플랜의 강점

### 1. 체계적인 단계별 접근
Gunicorn → Sentry → Celery → 부하 테스트 순서는 논리적이며, 각 단계가 명확한 목표를 가지고 있습니다.<cite />

### 2. PM2 통합 관리
Flask 서버를 PM2로 관리하는 것은 현재 가장 시급한 문제입니다. 현재 배포 스크립트에서 `pkill -f "python.*app.py"`로 Flask를 종료하고 있어[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: .github/workflows/restart-server.yml:30], 자동 복구와 모니터링이 불가능합니다.

## 수정이 필요한 부분

### 1. Flask 앱 팩토리 패턴 확인

**현재 상황:**
`app.py`는 이미 `create_app()` 팩토리 함수를 사용하고 있습니다[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: app.py:42-53]. 하지만 Gunicorn 실행 시 `app:create_app()`이 아니라 **`app:app`**을 사용해야 합니다.

`app.py`의 마지막 부분을 확인하면:
```python
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
```

따라서 Gunicorn 명령어는:
```bash
gunicorn -c gunicorn.conf.py app:app
```

### 2. 포트 충돌 문제

**플랜의 제안:** 포트 8001 사용

**현재 상황:** Flask는 포트 8000에서 실행 중이며[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: app.py:162], 서비스 모니터링도 8000 포트를 확인합니다[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: admin/services/service_monitoring_service.py:215].

**권장사항:** 
- 개발 환경: 8000 포트 유지
- 프로덕션: Gunicorn이 8000 포트 사용하도록 설정
- Nginx 프록시 설정도 8000 포트로 유지하여 기존 설정과 호환성 유지

### 3. Celery 도입 시기

**플랜의 제안:** Phase 3에서 Celery 도입

**비판적 검토:**
현재 시스템의 주요 병목은 AI 모델 추론이 아니라:
1. 단일 PM2 인스턴스 (fork 모드)[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: ecosystem.config.js:4-6]
2. SQLite 동시성 제약
3. Flask 서버가 PM2로 관리되지 않음

**권장사항:**
- Celery 도입은 **Phase 1, 2 완료 후 실제 부하 테스트 결과를 보고 결정**
- 먼저 PM2 클러스터 모드 활성화와 PostgreSQL 마이그레이션을 우선 고려
- AI 분석이 실제 병목인지 성능 모니터링으로 확인 후 도입

### 4. Sentry 통합 위치

**플랜의 제안:** `server.js`에 Sentry 초기화

**현재 구조:** `server.js`는 단순히 `server/app.js`를 로드합니다[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: server.js:3].

**권장사항:**
Sentry 초기화는 `server/app.js`의 상단에 추가해야 합니다:
```javascript
// server/app.js 상단
const Sentry = require("@sentry/node");

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  tracesSampleRate: 1.0,
  environment: process.env.NODE_ENV
});
```

## 개선된 실행 플랜

### Phase 1: Gunicorn + PM2 통합 (우선순위 1) - 1-2주

#### Step 1.1: Gunicorn 설정 (2-3일)
1. `requirements.txt`에 `gunicorn==21.2.0` 추가
2. `gunicorn.conf.py` 생성:
   - 포트: **8000** (기존 포트 유지)
   - Workers: `multiprocessing.cpu_count() * 2 + 1`
   - Timeout: 120
   - WSGI app: `app:app` (not `app:create_app()`)

#### Step 1.2: PM2 설정 통합 (2-3일)
`ecosystem.config.js` 수정:
```javascript
{
  name: 'signalcraft-python',
  script: 'gunicorn',
  args: '-c gunicorn.conf.py app:app',
  interpreter: '/home/ubuntu/smartcompressor_env/bin/python',
  exec_mode: 'fork',
  autorestart: true,
  max_memory_restart: '1G',
  env_production: {
    FLASK_ENV: 'production',
    PORT: '8000'
  }
}
```

#### Step 1.3: 배포 스크립트 수정 (1-2일)
`.github/workflows/auto-deploy.yml`에서:
- `pkill -f "python.*app.py"` 제거[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: .github/workflows/auto-deploy.yml:64]
- `pm2 reload ecosystem.config.js --env production` 사용

#### Step 1.4: Nginx 설정 확인 (1일)
기존 Nginx 설정이 Flask 엔드포인트를 어떻게 프록시하는지 확인하고, 필요시 8000 포트로 업데이트

### Phase 2: PostgreSQL 마이그레이션 (우선순위 2) - 1-2주

**이유:** SQLite는 동시성 제약이 있어 15개 이상의 동시 요청 처리에 한계가 있습니다. Celery보다 우선순위가 높습니다.

#### Step 2.1: PostgreSQL 설정 (2-3일)
1. AWS RDS PostgreSQL 인스턴스 생성 (db.t3.small)
2. 환경 변수 업데이트[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: config/database.env:12-17]
3. 연결 풀 설정 확인[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: services/database_service.js:18-21]

#### Step 2.2: 데이터 마이그레이션 (3-4일)
1. SQLite 데이터 백업
2. PostgreSQL 스키마 생성
3. 데이터 마이그레이션 스크립트 실행
4. 애플리케이션 연결 테스트

### Phase 3: Sentry 에러 트래킹 (우선순위 3) - 1주

플랜대로 진행하되, Node.js 초기화 위치를 `server/app.js`로 수정

### Phase 4: PM2 클러스터 모드 활성화 (우선순위 4) - 3-5일

Celery 도입 전에 먼저 PM2 클러스터 모드를 활성화하여 Node.js 서버의 동시 처리 능력을 향상:

```javascript
// ecosystem.config.js
{
  name: 'signalcraft-nodejs',
  script: 'server.js',
  instances: 'max',  // CPU 코어 수만큼 인스턴스 생성
  exec_mode: 'cluster',  // fork → cluster
  max_memory_restart: '1G'  // 512M → 1G
}
```

### Phase 5: 부하 테스트 및 병목 분석 (우선순위 5) - 1주

플랜대로 k6 부하 테스트 실행하여:
1. AI 분석이 실제 병목인지 확인
2. PostgreSQL 성능 검증
3. PM2 클러스터 모드 효과 측정

### Phase 6: Celery 도입 검토 (조건부) - 2-3주

**조건:** Phase 5의 부하 테스트 결과 AI 분석이 병목으로 확인된 경우에만 진행

플랜대로 진행하되, 다음 사항 추가:
1. Redis는 Docker Compose로 이미 설정되어 있음[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: docker-compose.yml:3-21]
2. Celery worker도 PM2로 관리
3. 프론트엔드 Polling 대신 WebSocket 고려 (실시간 업데이트)

## 최종 체크리스트

### Phase 1 완료 기준
- [ ] Flask 서버가 Gunicorn + PM2로 관리됨
- [ ] `pm2 status` - 2개 프로세스 모두 `online`
- [ ] `/api/lightweight-analyze` 정상 작동
- [ ] Zero-downtime 배포 확인

### Phase 2 완료 기준
- [ ] PostgreSQL RDS 인스턴스 생성
- [ ] 데이터 마이그레이션 완료
- [ ] 애플리케이션 정상 작동
- [ ] SQLite 파일 백업 및 보관

### Phase 3 완료 기준
- [ ] Sentry 대시보드에 에러 표시
- [ ] 성능 트레이싱 작동
- [ ] 배포 시 릴리즈 버전 태깅

### Phase 4 완료 기준
- [ ] PM2 클러스터 모드 활성화
- [ ] 다중 인스턴스 정상 작동
- [ ] 로드 밸런싱 확인

### Phase 5 완료 기준
- [ ] k6 부하 테스트 완료
- [ ] 병목 지점 식별
- [ ] 성능 개선 계획 수립

# Notes

제시하신 플랜은 전반적으로 좋지만, 현재 시스템의 실제 병목(단일 인스턴스, SQLite)을 먼저 해결하는 것이 더 효과적입니다. Celery는 AI 분석이 실제 병목으로 확인된 후에 도입하는 것을 권장합니다. 또한 `app:create_app()` 대신 `app:app`을 사용해야 하며, 포트는 기존 8000을 유지하는 것이 기존 설정과의 호환성을 위해 좋습니다.

Wiki pages you might want to explore:
- [Infrastructure & Deployment (SEONBEOM-Kim/smartcompressor-ai-system)](/wiki/SEONBEOM-Kim/smartcompressor-ai-system#2.1)
- [System Architecture (SEONBEOM-Kim/smartcompressor-ai-system)](/wiki/SEONBEOM-Kim/smartcompressor-ai-system#2)

Wiki pages you might want to explore:
- [System Architecture (SEONBEOM-Kim/smartcompressor-ai-system)](/wiki/SEONBEOM-Kim/smartcompressor-ai-system#2)
- [Infrastructure & Deployment (SEONBEOM-Kim/smartcompressor-ai-system)](/wiki/SEONBEOM-Kim/smartcompressor-ai-system#2.1)