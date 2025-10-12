Answer
이 아이디어는 매우 실용적이며 현재 SignalCraft에 부분적으로 구현되어 있습니다 performance_monitoring_service.py:1-36 . 하지만 Sentry 같은 외부 에러 트래킹 툴은 아직 연동되어 있지 않으므로, 추가 구현이 필요합니다.

현재 모니터링 시스템 상태
SignalCraft는 이미 기본적인 모니터링 시스템을 갖추고 있습니다 service_monitoring_service.py:107-147 :

1. 성능 모니터링 서비스
CPU, 메모리, 디스크 사용량을 실시간으로 수집하는 시스템이 이미 구현되어 있습니다 performance_monitoring_service.py:217-248 . 이 서비스는 30초 간격으로 다음 메트릭을 수집합니다:

CPU 사용률: psutil.cpu_percent()로 측정 performance_monitoring_service.py:221-222
메모리 사용률: psutil.virtual_memory().percent로 측정 performance_monitoring_service.py:225-227
디스크 사용률: psutil.disk_usage('/')로 측정 performance_monitoring_service.py:230-232
네트워크 I/O: psutil.net_io_counters()로 측정 performance_monitoring_service.py:235-237
2. 서비스 헬스 체크
각 서비스의 상태를 주기적으로 확인하는 시스템도 구현되어 있습니다 service_monitoring_service.py:172-209 :

Flask 앱 상태 확인 (http://localhost:8000/health) service_monitoring_service.py:211-259
데이터베이스 상태 확인 service_monitoring_service.py:261-302
Redis, Nginx 등 다른 서비스 모니터링 service_monitoring_service.py:132-140
3. 알림 시스템
임계값 기반 알림 시스템이 구현되어 있습니다 service_monitoring_service.py:482-523 :

CPU 사용률: 경고 70%, 위험 90% service_monitoring_service.py:124
메모리 사용률: 경고 80%, 위험 95% service_monitoring_service.py:125
응답 시간: 경고 2초, 위험 5초 service_monitoring_service.py:127
4. 대시보드 UI
관리자 대시보드가 이미 구현되어 있습니다 admin_dashboard.js:1-25 . 이 대시보드는 Chart.js를 사용하여 실시간 메트릭을 시각화합니다 admin_dashboard.js:460-490 :

서비스 상태 차트 (도넛 차트) admin_dashboard.js:467-490
리소스 사용률 차트 (막대 차트) admin_dashboard.js:493-518
CPU/메모리 시계열 차트 admin_dashboard.js:521-578
Sentry 연동을 위한 수정 파일
1. requirements.txt (수정)
Sentry SDK를 추가해야 합니다:

# 에러 트래킹  
sentry-sdk[flask]==1.40.0
2. app.py (수정)
Flask 앱 초기화 시 Sentry를 설정해야 합니다 :

import sentry_sdk  
from sentry_sdk.integrations.flask import FlaskIntegration  
  
# Sentry 초기화  
sentry_sdk.init(  
    dsn=os.getenv('SENTRY_DSN'),  # 환경 변수로 관리  
    integrations=[FlaskIntegration()],  
    traces_sample_rate=1.0,  # 100% 트랜잭션 추적  
    profiles_sample_rate=1.0,  # 100% 프로파일링  
    environment=os.getenv('FLASK_ENV', 'development'),  
    release=os.getenv('APP_VERSION', 'unknown')  
)  
  
app = Flask(__name__)
3. server.js (Node.js 서버 수정)
Node.js 서버에도 Sentry를 추가해야 합니다:

// package.json에 추가  
{  
  "dependencies": {  
    "@sentry/node": "^7.100.0",  
    "@sentry/profiling-node": "^1.3.0"  
  }  
}  
  
// server.js 상단에 추가  
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
4. admin/services/error_tracking_service.py (신규 생성)
Sentry와 통합된 에러 트래킹 서비스를 생성해야 합니다:

import sentry_sdk  
from typing import Dict, Any, Optional  
import logging  
  
logger = logging.getLogger(__name__)  
  
class ErrorTrackingService:  
    """에러 트래킹 서비스 (Sentry 통합)"""  
      
    @staticmethod  
    def capture_exception(  
        exception: Exception,  
        context: Optional[Dict[str, Any]] = None,  
        level: str = 'error'  
    ):  
        """예외를 Sentry에 전송"""  
        with sentry_sdk.push_scope() as scope:  
            if context:  
                for key, value in context.items():  
                    scope.set_context(key, value)  
              
            scope.level = level  
            sentry_sdk.capture_exception(exception)  
            logger.error(f"Exception captured: {exception}", exc_info=True)  
      
    @staticmethod  
    def capture_message(  
        message: str,  
        level: str = 'info',  
        context: Optional[Dict[str, Any]] = None  
    ):  
        """메시지를 Sentry에 전송"""  
        with sentry_sdk.push_scope() as scope:  
            if context:  
                for key, value in context.items():  
                    scope.set_context(key, value)  
              
            scope.level = level  
            sentry_sdk.capture_message(message)
5. routes/ai_routes.py (수정)
기존 에러 처리 로직에 Sentry 연동을 추가해야 합니다 :

from admin.services.error_tracking_service import ErrorTrackingService  
  
@ai_bp.route('/lightweight-analyze', methods=['POST'])  
def lightweight_analyze():  
    try:  
        # 기존 로직  
        pass  
    except Exception as e:  
        # Sentry에 에러 전송  
        ErrorTrackingService.capture_exception(  
            e,  
            context={  
                'endpoint': '/api/lightweight-analyze',  
                'user_id': session.get('user_id'),  
                'file_size': request.files['audio'].content_length  
            }  
        )  
        return jsonify({'error': str(e)}), 500
6. .env (수정)
환경 변수에 Sentry DSN을 추가해야 합니다:

# Sentry 설정  
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id  
APP_VERSION=1.0.0
7. admin/templates/monitoring_dashboard.html (신규 생성)
Sentry 이벤트를 표시하는 대시보드 페이지를 추가할 수 있습니다 dashboard.html:1-80 :

<!-- 기존 대시보드에 Sentry 섹션 추가 -->  
<div class="card">  
    <div class="card-header">  
        <h5>최근 에러 (Sentry)</h5>  
    </div>  
    <div class="card-body">  
        <div id="sentry-errors"></div>  
    </div>  
</div>
8. ecosystem.config.js (수정)
PM2 설정에 Sentry 환경 변수를 추가해야 합니다 :

module.exports = {  
  apps: [  
    {  
      name: 'signalcraft-nodejs',  
      script: 'server.js',  
      env: {  
        NODE_ENV: 'development',  
        PORT: 3000,  
        SENTRY_DSN: process.env.SENTRY_DSN  // 추가  
      },  
      env_production: {  
        NODE_ENV: 'production',  
        PORT: 3000,  
        SENTRY_DSN: process.env.SENTRY_DSN  // 추가  
      }  
    }  
  ]  
};
대시보드 강화 방안
1. 실시간 업데이트
현재 대시보드는 30초마다 업데이트됩니다 admin_dashboard.js:661-669 . 이를 유지하면서 Sentry 데이터를 추가로 표시할 수 있습니다.

2. 메트릭 히스토리
24시간 메트릭 히스토리가 이미 저장되고 있습니다 performance_monitoring_service.py:165-167 . 이를 활용하여 트렌드 분석이 가능합니다.

3. 권장사항 생성
시스템이 자동으로 권장사항을 생성합니다 performance_monitoring_service.py:605-646 . CPU 사용률이 80% 이상이면 리소스 확장을 권장하는 등의 기능이 구현되어 있습니다.

배포 시 추가 작업
1. Sentry 프로젝트 생성
sentry.io에서 무료 계정 생성
새 프로젝트 생성 (Flask, Node.js 각각)
DSN 복사하여 환경 변수에 설정
2. 배포 스크립트 수정
배포 워크플로우에 Sentry 릴리스 추적을 추가해야 합니다 :

# Sentry 릴리스 생성  
sentry-cli releases new $APP_VERSION  
sentry-cli releases set-commits $APP_VERSION --auto  
sentry-cli releases finalize $APP_VERSION
기대 효과
실시간 에러 추적: 프로