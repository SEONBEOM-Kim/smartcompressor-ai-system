Answer
이 Celery 도입 실행 계획은 전반적으로 잘 구성되어 있으며 실행 가능합니다 docker-compose.yml:24-30 . 하지만 현재 SignalCraft의 실제 구조와 몇 가지 불일치가 있어 수정이 필요합니다.

✅ 잘 설계된 부분
1. Redis 인프라 활용
docker-compose.yml에 Redis 서비스가 이미 정의되어 있어 즉시 활용 가능합니다 docker-compose.yml:24-30 . 포트 6379로 노출되어 있으며, 환경 변수 REDIS_URL=redis://redis:6379로 접근할 수 있습니다 docker-compose.yml:45 .

2. Celery 설정 구조
celery_worker.py의 설정은 적절합니다. 특히 REDIS_HOST 환경 변수로 Docker와 로컬 환경을 모두 지원하는 것은 좋은 설계입니다.

3. 비동기 태스크 정의
tasks.py의 태스크 구조는 올바릅니다. 파일 정리 로직을 finally 블록에 넣어 예외 발생 시에도 임시 파일이 삭제되도록 한 것은 좋은 패턴입니다.

⚠️ 수정 필요사항
1. Flask 앱 구조 불일치 (중요)
현재 app.py는 팩토리 패턴을 사용하고 있습니다 app.py:43-50 . create_app() 함수가 Flask 앱을 생성하므로, Celery 초기화 시 이를 고려해야 합니다.

수정된 celery_worker.py:

from celery import Celery  
import os  
  
redis_host = os.getenv('REDIS_HOST', 'localhost')  
  
celery_app = Celery(  
    'signalcraft_tasks',  
    broker=f'redis://{redis_host}:6379/0',  
    backend=f'redis://{redis_host}:6379/0',  
    include=['tasks']  
)  
  
celery_app.conf.update(  
    task_serializer='json',  
    accept_content=['json'],  
    result_serializer='json',  
    timezone='Asia/Seoul',  
    enable_utc=True,  
    task_track_started=True,  
    task_time_limit=300,  
)  
  
# Flask 앱 컨텍스트 설정 (중요!)  
def init_celery(app):  
    """Flask 앱과 Celery 통합"""  
    celery_app.conf.update(app.config)  
      
    class ContextTask(celery_app.Task):  
        def __call__(self, *args, **kwargs):  
            with app.app_context():  
                return self.run(*args, **kwargs)  
      
    celery_app.Task = ContextTask  
    return celery_app
2. AI 서비스 호출 방식 불일치
ensemble_ai_service.predict_ensemble() 메서드가 존재하지 않을 수 있습니다. 실제 코드베이스를 확인한 결과, AI 서비스의 정확한 메서드명을 확인해야 합니다.

수정된 tasks.py:

import os  
from celery_worker import celery_app  
from services.ai_service import ensemble_ai_service  
  
@celery_app.task(bind=True, name='tasks.analyze_audio_task')  
def analyze_audio_task(self, file_path: str):  
    """오디오 파일을 비동기적으로 분석하는 Celery 태스크"""  
    try:  
        # 진행률 업데이트  
        self.update_state(state='PROGRESS', meta={'progress': 10})  
          
        # 실제 AI 분석 호출 (메서드명 확인 필요)  
        # ensemble_ai_service의 실제 메서드를 사용해야 함  
        result = ensemble_ai_service.analyze(file_path)  # 또는 predict()  
          
        self.update_state(state='PROGRESS', meta={'progress': 90})  
          
        return {  
            'status': 'success',  
            'result': result  
        }  
    except Exception as e:  
        self.update_state(state='FAILURE', meta={'error': str(e)})  
        raise  
    finally:  
        if os.path.exists(file_path):  
            os.remove(file_path)
3. Blueprint 등록 누락
app.py에 결과 조회 API를 위한 Blueprint 등록이 필요합니다 app.py:74-92 . 현재 여러 Blueprint가 등록되어 있으므로, 동일한 패턴으로 추가해야 합니다.

app.py 수정:

# app.py의 create_app() 함수 내부  
from routes.task_routes import task_bp  # 추가  
  
# 기존 Blueprint 등록 후  
app.register_blueprint(task_bp)  # 추가
4. PM2 설정 경로 문제
ecosystem.config.js의 Python 인터프리터 경로가 하드코딩되어 있습니다 ecosystem.config.js:1-38 . 현재 PM2는 Node.js만 관리하고 있으므로, Celery Worker를 추가할 때 환경에 맞는 경로를 사용해야 합니다.

수정된 ecosystem.config.js:

module.exports = {  
  apps: [  
    {  
      name: 'signalcraft-nodejs',  
      script: 'server.js',  
      instances: 1,  
      exec_mode: 'fork',  
      autorestart: true,  
      max_memory_restart: '512M',  
      // ... 기존 설정  
    },  
    {  
      name: 'celery-worker',  
      script: 'celery',  
      args: '-A celery_worker worker --loglevel=info --concurrency=2',  
      interpreter: 'python3',  // 시스템 Python 사용  
      cwd: '/var/www/smartcompressor',  
      instances: 1,  
      autorestart: true,  
      max_memory_restart: '1G',  
      watch: false,  
      env: {  
        REDIS_HOST: 'localhost',  // 또는 'redis' (Docker 환경)  
        FLASK_ENV: 'production'  
      },  
      log_type: 'json',  
      error_file: './logs/celery-err.log',  
      out_file: './logs/celery-out.log'  
    }  
  ]  
};
5. 프론트엔드 폴링 로직 누락
계획서에는 프론트엔드 수정이 언급되지 않았지만 필수입니다. 사용자가 결과를 받으려면 클라이언트 측에서 폴링 또는 WebSocket을 구현해야 합니다.

추가 필요 파일:

static/index.html 또는 templates/showcase.html에 폴링 로직 추가
또는 별도의 JavaScript 파일 생성 (static/js/async_analysis.js)
6. 배포 스크립트 업데이트 누락
배포 워크플로우에 Celery Worker 관리 로직이 필요합니다 restart-server.yml:26-30 . 현재 배포 스크립트는 Node.js와 Python 프로세스만 종료하고 있습니다.

.github/workflows/auto-deploy.yml 수정:

# 기존 프로세스 종료  
pm2 delete all 2>/dev/null || echo "PM2 프로세스 없음"  
pkill -f "node server.js" || true  
pkill -f "python.*app.py" || true  
pkill -f "celery.*worker" || true  # Celery Worker 종료 추가  
  
# PM2로 모든 서비스 시작  
pm2 start ecosystem.config.js  
  
# Celery Worker 상태 확인  
pm2 logs celery-worker --lines 20
7. Redis 연결 확인 로직 필요
Redis 서비스가 실행 중인지 확인하는 헬스체크가 필요합니다 docker-compose.yml:24-30 . Docker Compose에는 Redis가 있지만, 실제 EC2 배포 환경에서는 별도 설치가 필요할 수 있습니다.

추가 필요:

# 배포 스크립트에 Redis 확인 추가  
redis-cli ping || echo "❌ Redis 서버 응답 없음"
📋 수정된 실행 계획
단계 0: 사전 준비 (추가)
Redis 설치 확인:

# Docker 환경  
docker-compose up -d redis  
  
# 로컬/EC2 환경  
sudo apt-get install redis-server  
sudo systemctl start redis  
redis-cli ping  # PONG 응답 확인
현재 Flask 앱 구조 확인:

grep -n "create_app\|Flask(__name__)" app.py
단계 2 수정: Celery 앱 초기화
Flask 앱 컨텍스트 통합 로직 추가 (위 수정 사항 참고)
init_celery() 함수로 Flask와 Celery 연결
단계 4 수정: API 엔드포인트 수정
# routes/ai_routes.py  
from flask import current_app  
from tasks import analyze_audio_task  
  
@ai_bp.route('/lightweight-analyze', methods=['POST'])  
def lightweight_analyze():  
    """경량 AI 진단 (비동기 방식)"""  
    if 'audio' not in request.files:  
        return jsonify({'success': False, 'message': '오디오 파일이 필요합니다.'}), 400  
  
    audio_file = request.files['audio']  
      
    # 파일 저장  
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')  
    os.makedirs(upload_folder, exist_ok=True)  
    filename = f"temp_{int(time.time())}_{audio_file.filename}"  
    file_path = os.path.join(upload_folder, filename)  
    audio_file.save(file_path)  
  
    # 비동기 태스크 실행  
    task = analyze_audio_task.delay(file_path)  
      
    return jsonify({  
        'success': True,  
        'status': 'processing',  
        'task_id': task.id,  
        'message': 'AI 분석 작업이 시작되었습니다.'  
    }), 202
단계 7: 프론트엔드 수정 (추가)
폴링 로직 구현 (1초 간격, 최대 60초)
진행률 표시 UI 추가
에러 처리 로직 추가
단계 8: 통합 테스트 (추가)
# 1. Redis 시작  
redis-server  
  
# 2. Celery Worker 시작  
celery -A celery_worker worker --loglevel=info  
  
# 3. Flask 앱 시작  
python app.py  
  
# 4. 테스트 요청  
curl -X POST http://localhost:8000/api/lightweight-analyze \  
  -F "audio=@test_audio.wav"  
  
# 5. 결과 조회 (task_id는 위 응답에서 받음)  
curl http://localhost:8000/api/analyze/result/<task_id>
🚨 주의사항
메모리 관리: Celery Worker의 --concurrency=2는 메모리 사용량을 고려한 설정입니다 ecosystem.config.js:10 . EC2 인스턴스의 메모리가 제한적이므로 모니터링이 필요합니다.

파일 정리: 임시 파일이 제대로 삭제되지 않으면 디스크 공간이 부족해질 수 있습니다. 주기적인 정리 스크립트가 필요할 수 있습니다.

타임아웃 설정: AI 분석이 5분 이상 걸릴 경우 task_time_limit을 조정해야 합니다.

Redis 영속성: Redis 데이터가 휘발성이므로, 중요한 결과는 별도 저장소에 백업해야 합니다.