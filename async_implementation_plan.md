# 비동기 처리(Celery) 도입 실행 계획

## 1. 목표
`routes/ai_routes.py`의 동기적 AI 분석 로직을 Celery와 Redis를 사용한 비동기 처리 방식으로 전환하여, 사용자 경험(UX)을 개선하고 서버의 동시 처리 능력을 향상시킨다.

## 2. 현황 (검증 완료)
- **문제점:** `ensemble_ai_service.predict_ensemble()` 호출이 HTTP 요청을 차단(Block)함.
- **인프라:** `docker-compose.yml`에 `redis` 서비스가 이미 준비되어 있어 즉시 활용 가능.
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
- **Action:** 프로젝트 루트에 `celery_worker.py` 파일을 생성하여 Celery 애플리케이션을 설정한다.
- **`celery_worker.py` (신규 생성):**
    ```python
    from celery import Celery
    import os

    # Docker 환경에서는 'redis' 서비스 이름을 사용하고, 로컬에서는 'localhost'를 사용
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    
    celery_app = Celery(
        'signalcraft_tasks',
        broker=f'redis://{redis_host}:6379/0',
        backend=f'redis://{redis_host}:6379/0',
        include=['tasks'] # Celery가 비동기 작업을 찾을 모듈 목록
    )

    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Seoul',
        enable_utc=True,
    )
    ```

### 3단계: 비동기 태스크 정의
- **Action:** 프로젝트 루트에 `tasks.py` 파일을 생성하고, 실제 AI 분석을 수행할 Celery 태스크를 정의한다.
- **`tasks.py` (신규 생성):**
    ```python
    import os
    from celery_worker import celery_app
    from services.ai_service import ensemble_ai_service

    @celery_app.task(name='tasks.analyze_audio_task')
    def analyze_audio_task(file_path: str):
        """
        오디오 파일을 비동기적으로 분석하는 Celery 태스크.
        성공 시 분석 결과를, 실패 시 예외를 반환한다.
        """
        try:
            # 기존의 동기적 AI 분석 서비스 호출
            result = ensemble_ai_service.predict_ensemble(file_path)
            return result
        finally:
            # 작업 완료 후 임시 파일 정리
            if os.path.exists(file_path):
                os.remove(file_path)
    ```

### 4단계: API 엔드포인트 수정
- **Action:** `routes/ai_routes.py`의 `lightweight_analyze` 함수를 수정하여, AI 분석을 직접 호출하는 대신 Celery 태스크를 실행하도록 변경한다.
- **`routes/ai_routes.py` (수정):**
    ```python
    # ... (기존 import)
    from tasks import analyze_audio_task # 새로 만든 태스크 import

    # ...

    @ai_bp.route('/lightweight-analyze', methods=['POST'])
    def lightweight_analyze():
        """경량 AI 진단 (비동기 방식)"""
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': '오디오 파일이 필요합니다.'}), 400

        audio_file = request.files['audio']
        # ... (파일 유효성 검사) ...

        # 임시 파일 저장
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filename = f"temp_{int(time.time())}_{audio_file.filename}"
        file_path = os.path.join(upload_folder, filename)
        audio_file.save(file_path)

        # --- 변경된 핵심 로직 ---
        # 동기 호출 대신, 비동기 태스크를 큐에 추가하고 즉시 응답
        task = analyze_audio_task.delay(file_path)
        
        # 사용자에게는 작업이 시작되었음을 알리는 task_id를 반환
        return jsonify({
            'success': True,
            'status': 'processing',
            'task_id': task.id,
            'message': 'AI 분석 작업이 시작되었습니다. 잠시 후 결과를 조회해주세요.'
        }), 202 # 202 Accepted: 요청이 접수되었으며 처리가 시작됨
    ```

### 5단계: 결과 조회 API 추가
- **Action:** `suggestion.md`의 제안대로, 태스크의 진행 상태와 결과를 조회할 수 있는 API 엔드포인트를 추가한다. `routes/ai_routes.py`에 추가하거나 별도 파일로 분리한다.
- **`routes/ai_routes.py` (추가):**
    ```python
    from celery.result import AsyncResult
    from celery_worker import celery_app

    @ai_bp.route('/analyze/result/<task_id>', methods=['GET'])
    def get_analysis_result(task_id):
        """Celery 태스크의 상태와 결과를 조회"""
        task_result = AsyncResult(task_id, app=celery_app)

        if task_result.ready(): # 작업이 완료되었는가?
            if task_result.successful():
                return jsonify({
                    'status': 'SUCCESS',
                    'result': task_result.get()
                })
            else: # 작업 실패
                return jsonify({
                    'status': 'FAILURE',
                    'error': str(task_result.info) # 실패 원인 (예외 정보)
                }), 500
        else: # 작업 진행 중
            return jsonify({
                'status': 'PENDING',
                'message': 'AI 분석이 아직 진행 중입니다.'
            }), 202
    ```

### 6단계: Celery Worker 실행
- **Action:** Celery Worker 프로세스를 실행하여 큐에 들어온 작업을 처리하도록 한다.
- **로컬 실행 명령어:**
    ```bash
    celery -A celery_worker worker --loglevel=info
    ```
- **`ecosystem.config.js` (PM2 통합):**
    ```javascript
    // ... (기존 apps 배열)
    {
      name: 'celery-worker',
      script: 'celery',
      args: '-A celery_worker worker --loglevel=info --concurrency=2',
      interpreter: '/home/ubuntu/smartcompressor_env/bin/python', // **중요: 가상환경 Python 경로**
      autorestart: true,
      max_memory_restart: '1G',
    }
    // ...
    ```

## 4. 기대 효과
- **사용자:** 오디오 파일 업로드 시 즉시 응답을 받아 대기 시간이 사라짐.
- **서버:** 시간이 오래 걸리는 AI 분석 작업이 별도의 Worker 프로세스에서 처리되므로, API 서버(Flask)는 다른 요청을 더 많이, 더 빠르게 처리할 수 있게 됨.
- **확장성:** 향후 작업량이 늘어날 경우, Celery Worker의 수(`--concurrency` 또는 서버 수)만 늘려 쉽게 대응 가능.
