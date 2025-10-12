Answer
이 Gunicorn 도입 설계 플랜은 전반적으로 잘 구성되어 있으며 실행 가능합니다. 하지만 현재 SignalCraft의 실제 구조와 몇 가지 불일치가 있어 수정이 필요합니다.

✅ 잘 설계된 부분
1. 최소 변경 원칙
Node.js 서버를 그대로 두고 Python만 변경하는 전략은 올바릅니다 ecosystem.config.js:1-10 . 현재 PM2는 Node.js만 관리하고 있으므로 ecosystem.config.js:3-6 , Flask를 추가하는 방식이 안전합니다.

2. Gunicorn 설정 파일
gunicorn.conf.py의 설정은 대부분 적절합니다. 특히 타임아웃 120초는 AI 분석 작업에 적합하며, 로그를 표준 출력으로 보내는 것은 PM2 로그 관리와 잘 통합됩니다 ecosystem.config.js:24-30 .

3. Nginx 프록시 설정
Nginx 설정 수정 방향은 정확합니다. 현재 배포 스크립트에서 Nginx 설정을 /etc/nginx/sites-available/signalcraft에 복사하고 있으므로 fix-502-complete.sh:44-50 , 해당 파일을 수정하는 것이 맞습니다.

⚠️ 수정 필요사항
1. Flask 앱 구조 불일치 (중요)
wsgi_app = "app:create_app()"는 작동하지 않습니다. 현재 SignalCraft의 Flask 앱은 팩토리 패턴을 사용하지 않습니다 .

올바른 설정:

# gunicorn.conf.py에서 wsgi_app 제거하고, 명령줄에서 직접 지정  
# 또는 app.py가 이미 app 객체를 생성하므로:  
# wsgi_app = "app:app"  # app.py 모듈의 app 객체
실제로 app.py는 다음과 같이 Flask 앱을 직접 생성합니다 :

app = Flask(__name__)  
CORS(app, ...)
따라서 Gunicorn 실행 시 app:app을 사용해야 합니다.

2. PM2 설정의 현실적 문제
현재 ecosystem.config.js에는 Python 앱이 정의되어 있지 않습니다 ecosystem.config.js:1-37 . 단계 3에서 signalcraft-python 앱을 수정한다고 했지만, 실제로는 새로 추가해야 합니다.

올바른 ecosystem.config.js 수정:

module.exports = {  
  apps: [  
    {  
      name: 'signalcraft-nodejs',  
      script: 'server.js',  
      instances: 1,  
      exec_mode: 'fork',  
      autorestart: true,  
      max_memory_restart: '512M',  
      // ... 기존 설정 유지  
    },  
    // --- 새로 추가 ---  
    {  
      name: 'signalcraft-flask',  
      script: 'gunicorn',  
      args: '-c gunicorn.conf.py app:app',  // app:app 명시  
      interpreter: 'python3',  
      instances: 1,  
      autorestart: true,  
      max_memory_restart: '1G',  
      watch: false,  
      env: {  
        FLASK_ENV: 'production',  
        PORT: 8001  
      },  
      log_type: 'json',  
      error_file: './logs/flask-err.log',  
      out_file: './logs/flask-out.log'  
    }  
  ]  
};
3. 워커 수 계산 문제
workers = multiprocessing.cpu_count() * 2 + 1은 메모리 부족을 유발할 수 있습니다. 현재 Node.js 프로세스는 512MB로 제한되어 있으며 ecosystem.config.js:10 , EC2 인스턴스의 총 메모리가 제한적일 가능성이 높습니다.

권장 수정:

# gunicorn.conf.py  
import multiprocessing  
import os  
  
# 환경 변수로 워커 수 제어 가능하도록  
workers = int(os.getenv('GUNICORN_WORKERS', '2'))  # 기본값 2  
worker_class = "sync"
4. 포트 충돌 가능성
Flask가 현재 어떤 포트를 사용하는지 확인이 필요합니다. app.py를 보면 포트가 명시되어 있지 않아 , 기본 포트 5000을 사용할 가능성이 있습니다. 8001로 변경하기 전에 기존 프로세스를 확실히 종료해야 합니다 fix-502-complete.sh:7-10 .

5. 배포 스크립트 업데이트 누락
기존 배포 스크립트들도 수정이 필요합니다. 현재 배포 워크플로우는 Python 프로세스를 pkill -f "python.*app.py"로 종료하고 있습니다 auto-deploy.yml:60-64 . Gunicorn 도입 후에는 이 명령이 작동하지 않을 수 있습니다.

필요한 스크립트 수정:

# .github/workflows/auto-deploy.yml  
# 기존 프로세스 종료 부분 수정  
pm2 delete all 2>/dev/null || echo "PM2 프로세스 없음"  
pkill -f "gunicorn" || true  # Gunicorn 프로세스 종료 추가  
pkill -f "python.*app.py" || true
6. Health Check 엔드포인트 필요
Gunicorn 시작 후 상태 확인을 위한 헬스체크 엔드포인트가 필요합니다. 현재 배포 스크립트는 curl http://localhost:3000으로 Node.js만 확인합니다 auto-deploy.yml:94-97 .

추가 필요:

# 배포 스크립트에 Flask 헬스체크 추가  
curl -s http://localhost:8001/health || echo "❌ Flask 서버 응답 없음"
그리고 app.py에 헬스체크 엔드포인트 추가:

@app.route('/health')  
def health_check():  
    return {'status': 'ok'}, 200
📋 수정된 실행 계획
단계 0: 사전 준비 (추가)
현재 Flask 프로세스 확인: ps aux | grep python
사용 중인 포트 확인: sudo netstat -tlnp | grep python
메모리 상태 확인: free -h
단계 2 수정: Gunicorn 설정
# gunicorn.conf.py  
import multiprocessing  
import os  
  
bind = "127.0.0.1:8001"  
workers = int(os.getenv('GUNICORN_WORKERS', '2'))  # 메모리 고려  
worker_class = "sync"  
accesslog = "-"  
errorlog = "-"  
timeout = 120  
keepalive = 5  
max_requests = 1000  
max_requests_jitter = 50  
# wsgi_app 제거 - 명령줄에서 지정
단계 3 수정: PM2 설정
{  
  name: 'signalcraft-flask',  
  script: 'gunicorn',  
  args: '-c gunicorn.conf.py app:app',  // app:app 명시  
  interpreter: 'python3',  
  cwd: '/var/www/smartcompressor',  // 작업 디렉토리 명시  
  instances: 1,  
  autorestart: true,  
  max_memory_restart: '1G',  
  watch: false,  
  env: {  
    FLASK_ENV: 'production',  
    GUNICORN_WORKERS: '2'  
  }  
}
단계 5 수정: 배포 및 검증
# 1. 로컬 테스트  
gunicorn -c gunicorn.conf.py app:app  
  
# 2. 기존 프로세스 완전 종료  
pm2 delete all  
pkill -f "gunicorn" || true  
pkill -f "python.*app.py" || true  
  
# 3. 의존성 설치  
pip install gunicorn  
  
# 4. PM2로 시작  
pm2 start ecosystem.config.js  
  
# 5. 상태 확인  
pm2 status  
pm2 logs signalcraft-flask --lines 50  
  
# 6. 헬스체크  
curl http://localhost:8001/health  
curl http://localhost:3000/api/auth/verify  
  
# 7. Nginx 재시작  
sudo nginx -t  
sudo systemctl restart nginx  
  
# 8. 최종 확인  
curl -I https://signalcraft.kr
🚨 주의사항
메모리 모니터링: Gunicorn 워커 2개 + Node.js = 약 1.5GB 메모리 필요
점진적 배포: 먼저 워커 1개로 시작하여 안정성 확인 후 증가
롤백 계획: 문제 발생 시 pm2 delete signalcraft-flask && python app.py 실행
로그 모니터링: pm2 logs signalcraft-flask로 Gunicorn 워커 상태 지속 확인 ecosystem.config.js:24-35
Notes
현재 SignalCraft는 Flask를 직접 실행하는 방식이므로, PM2 설정에 Flask 앱이 없습니다 ecosystem.config.js:1-37
배포 워크플로우는 systemd 서비스를 사용하고 있어 auto-deploy.yml:77-84 , PM2와 systemd 간 충돌 가능성을 고려해야 합니다
Nginx 설정 파일은 저장소에 없지만, 배포 시 nginx_https_config.conf를 사용합니다 fix-502-complete.sh:46-50