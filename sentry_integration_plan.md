# Sentry 연동 실행 계획 (검증 완료)

## 1. 목표
실시간 에러 트래킹 및 성능 모니터링을 위해 Sentry를 Flask 백엔드와 Node.js 서버에 통합한다. 이를 통해 프로덕션 환경에서 발생하는 문제를 신속하게 파악하고 해결한다.

## 2. 사전 준비
- **Sentry 프로젝트 생성:**
  1. sentry.io에서 계정 생성 및 로그인
  2. Flask, Node.js 각각에 대한 신규 프로젝트 생성
  3. 각 프로젝트의 DSN (Data Source Name) 키를 복사하여 `.env` 파일에 추가할 준비

---

## 3. 단계별 실행 계획

### 1단계: 의존성 추가
- **Action:** `requirements.txt` (Python)와 `package.json` (Node.js)에 Sentry SDK를 추가한다.
- **`requirements.txt` (추가):**
    ```
    # 에러 트래킹
    sentry-sdk[flask]==1.40.0
    ```
- **`package.json` (추가):**
    ```json
    {
      "dependencies": {
        "@sentry/node": "^7.100.0",
        "@sentry/profiling-node": "^1.3.0"
      }
    }
    ```
- **실행:**
    ```bash
    pip install -r requirements.txt
    npm install
    ```

### 2단계: 환경 변수 설정
- **Action:** `.env` 파일에 Sentry DSN과 앱 버전을 추가한다.
- **`.env` (추가):**
    ```
    # Sentry 설정
    SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
    APP_VERSION=1.0.0
    ```

### 3단계: 백엔드(Flask) 연동
- **Action:** `app.py`의 `create_app` 함수 상단에 Sentry SDK 초기화 코드를 추가한다.
- **`app.py` (수정):**
    ```python
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    import os

    def create_app():
        # Sentry 초기화 (Flask 앱 생성 전 또는 초기에)
        sentry_sdk.init(
            dsn=os.getenv('SENTRY_DSN'),
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=os.getenv('FLASK_ENV', 'development'),
            release=os.getenv('APP_VERSION', 'unknown')
        )
        app = Flask(__name__)
        # ... (기존 앱 설정)
        return app
    ```

### 4단계: Node.js 서버 연동
- **Action:** `server.js` 상단에 Sentry SDK 초기화 코드를 추가한다.
- **`server.js` (수정):**
    ```javascript
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

    // ... (기존 서버 코드)
    ```

### 5단계: 중앙 에러 트래킹 서비스 생성
- **Action:** Sentry로 에러를 전송하는 중앙 관리 서비스를 생성한다.
- **`admin/services/error_tracking_service.py` (신규 생성):**
    ```python
    import sentry_sdk
    from typing import Dict, Any, Optional

    class ErrorTrackingService:
        @staticmethod
        def capture_exception(exception: Exception, context: Optional[Dict[str, Any]] = None):
            with sentry_sdk.push_scope() as scope:
                if context:
                    scope.set_context("extra_info", context)
                sentry_sdk.capture_exception(exception)

        @staticmethod
        def capture_message(message: str, level: str = 'info'):
            sentry_sdk.capture_message(message, level=level)
    ```

### 6단계: 에러 핸들러에 Sentry 적용
- **Action:** `routes/ai_routes.py`의 `lightweight_analyze` 함수에 `try...except` 블록을 추가하고 `ErrorTrackingService`를 호출한다.
- **`routes/ai_routes.py` (수정 예시):**
    ```python
    from admin.services.error_tracking_service import ErrorTrackingService

    @ai_bp.route('/lightweight-analyze', methods=['POST'])
    def lightweight_analyze():
        try:
            # ... 기존 로직 ...
            pass
        except Exception as e:
            # Sentry에 에러 전송
            ErrorTrackingService.capture_exception(
                e,
                context={
                    'endpoint': '/api/lightweight-analyze',
                    'user_id': session.get('user_id'),
                }
            )
            return jsonify({'error': 'Internal Server Error'}), 500
    ```

### 7단계: PM2 설정 업데이트
- **Action:** `ecosystem.config.js`에 Sentry 관련 환경 변수를 전달하도록 수정한다.
- **`ecosystem.config.js` (수정):**
    ```javascript
    // ... apps 배열 내부 ...
    {
      name: 'signalcraft-nodejs',
      // ...
      env: {
        // ... 기존 env
        SENTRY_DSN: process.env.SENTRY_DSN
      },
      env_production: {
        // ... 기존 env_production
        SENTRY_DSN: process.env.SENTRY_DSN
      }
    }
    ```

### 8단계: 배포 스크립트 수정
- **Action:** 배포 시 Sentry에 릴리스 정보를 자동으로 등록하도록 스크립트를 수정한다. (Sentry CLI 필요)
- **배포 스크립트 (예시):**
    ```bash
    # 1. Sentry CLI 설치 (최초 1회)
    # curl -sL https://sentry.io/get-cli/ | bash

    # 2. 배포 스크립트에 릴리스 추적 추가
    export SENTRY_AUTH_TOKEN=your_sentry_auth_token
    export SENTRY_ORG=your_sentry_organization
    APP_VERSION=$(node -p "require('./package.json').version") # package.json에서 버전 읽기

    # 릴리스 생성 및 커밋 설정
    sentry-cli releases new $APP_VERSION
    sentry-cli releases set-commits $APP_VERSION --auto

    # ... 기존 배포 로직 (git pull, npm install, pm2 restart 등) ...

    # 릴리스 완료
    sentry-cli releases finalize $APP_VERSION
    ```

## 4. 기대 효과
- **실시간 에러 알림:** 프로덕션에서 발생하는 모든 예외를 실시간으로 Sentry 대시보드와 알림 채널(Slack, 이메일 등)에서 확인 가능.
- **상세한 컨텍스트:** 에러 발생 시점의 사용자 정보, 요청 데이터, 환경 변수 등 디버깅에 필요한 상세 정보를 자동으로 수집.
- **성능 모니터링:** API 엔드포인트별 응답 시간, 처리량 등 성능 지표(Transaction)를 추적하여 병목 구간 식별.
- **신속한 문제 해결:** 재현하기 어려운 에러도 Sentry에 기록된 로그와 스택 트레이스를 통해 빠르게 원인을 분석하고 해결 가능.
