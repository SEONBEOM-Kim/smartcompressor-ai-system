# 비동기 처리(Celery) 도입 실행 계획 (v2 - 검증 완료)

## 1. 목표
`routes/ai_routes.py`의 동기적 AI 분석 로직을 Celery와 Redis를 사용한 비동기 처리 방식으로 전환하여, 사용자 경험(UX)을 개선하고 서버의 동시 처리 능력을 향상시킨다.

## 2. 현황 (검증 완료)
- **문제점:** `ensemble_ai_service.predict_ensemble()` 호출이 HTTP 요청을 차단(Block)함.
- **인프라:** `docker-compose.yml`에 `redis` 서비스가 이미 준비되어 있어 즉시 활용 가능.
- **Flask 앱 구조:** `app.py`는 `create_app` 팩토리 패턴을 사용하므로 Celery 초기화 시 앱 컨텍스트 주입이 필요함.
- **의존성:** `celery` 및 `redis` Python 라이브러리 설치 필요.

---

## 3. 단계별 실행 계획

### 1단계: 의존성 추가
- **Action:** `requirements.txt` 파일에 Celery와 Redis 클라이언트 라이브러리를 추가한다.
- **`requirements.txt` (추가 내용):**
    ```
    # ... 기존 의존성 ...
    
    # 비동기 태스크 큐
    celery==5.3.6
    redis==5.0.1
    ```
- **실행:** `pip install -r requirements.txt`

### 2단계: Celery 앱 초기화
- **Action:** `celery_worker.py`를 Flask의 `create_app` 팩토리 패턴과 통합되도록 생성/수정한다.
- **`celery_worker.py` (신규 생성/수정):**
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
- **Action:** `app.py`의 `create_app` 함수에 Celery 관련 설정을 추가한다.
- **`app.py` (수정):**
    ```python
    # ... create_app() 내부 ...
    app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379/0',
        CELERY_RESULT_BACKEND='redis://localhost:6379/0'
    )
    # ...
    ```

### 3단계: 비동기 태스크 정의
- **Action:** `tasks.py` 파일을 생성하고, 실제 AI 분석을 수행할 Celery 태스크를 정의한다.
- **`tasks.py` (신규 생성):**
    ```python
    import os
    from celery_worker import celery_app
    from services.ai_service import ensemble_ai_service

    @celery_app.task(bind=True, name='tasks.analyze_audio_task')
    def analyze_audio_task(self, file_path: str):
        """오디오 파일을 비동기적으로 분석하는 Celery 태스크"""
        try:
            self.update_state(state='PROGRESS', meta={'progress': 10})
            # 검증 결과, predict_ensemble 메서드가 사용됨. 인자 확인 필요.
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

### 4단계: API 엔드포인트 수정
- **Action:** `routes/ai_routes.py`의 `lightweight_analyze` 함수를 비동기 태스크를 호출하도록 수정한다.
- **`routes/ai_routes.py` (수정):**
    ```python
    # ...
    from tasks import analyze_audio_task
    # ...
    @ai_bp.route('/lightweight-analyze', methods=['POST'])
    def lightweight_analyze():
        # ... 파일 저장 로직 ...
        task = analyze_audio_task.delay(file_path)
        return jsonify({'task_id': task.id}), 202
    ```

### 5단계: 결과 조회 API 추가 및 Blueprint 등록
- **Action:** 태스크 상태 조회를 위한 `task_routes.py`를 생성하고 Blueprint를 등록한다.
- **`routes/task_routes.py` (신규 생성):**
    ```python
    from flask import Blueprint, jsonify
    from celery.result import AsyncResult
    from celery_worker import celery_app

    task_bp = Blueprint('task_bp', __name__, url_prefix='/api')

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
- **Action:** `app.py`의 `create_app` 함수에 `task_bp` Blueprint를 등록한다.
- **`app.py` (수정):**
    ```python
    # ... create_app() 내부 ...
    from routes.task_routes import task_bp
    app.register_blueprint(task_bp)
    # ...
    ```

### 6단계: Celery Worker 실행 설정
- **Action:** `ecosystem.config.js`에 Celery Worker 설정을 추가한다.
- **`ecosystem.config.js` (수정):**
    ```javascript
    // ... 기존 apps 배열에 추가
    {
      name: 'celery-worker',
      script: 'celery',
      args: '-A celery_worker.celery_app worker --loglevel=info --concurrency=2',
      interpreter: 'python3',
      autorestart: true,
      max_memory_restart: '1G',
    }
    ```

### 7단계: 프론트엔드 수정
- **Action:** 클라이언트에서 작업 상태를 주기적으로 확인(Polling)하는 JavaScript 로직을 추가한다.

### 8단계: 배포 스크립트 업데이트
- **Action:** 배포 워크플로우에 Celery Worker 관리 로직을 추가한다. (`.github/workflows/auto-deploy.yml` 또는 관련 배포 스크립트)
- **배포 스크립트 예시:**
    ```bash
    # ...
    pm2 restart ecosystem.config.js
    # ...
    ```

### 9단계: 통합 테스트
- **Action:** 모든 구성 요소가 올바르게 작동하는지 엔드투엔드로 테스트한다.

## 4. 주의사항
- **메모리 관리:** Celery Worker의 `--concurrency` 값은 서버 사양에 맞게 조정 필요.
- **파일 정리:** `finally` 블록에서 임시 파일이 반드시 삭제되는지 확인.
- **타임아웃:** AI 분석 시간이 길어질 경우, Celery 태스크의 타임아웃 설정 조정 필요.