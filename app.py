#!/usr/bin/env python3


import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from routes.kakao_auth_routes import kakao_auth_bp

# .env 파일 로드
load_dotenv()

# 라우트 블루프린트 임포트
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from routes.monitoring_routes import monitoring_bp
from routes.ai_routes import ai_bp
from routes.esp32_routes import esp32_bp
from routes.notification_routes import notification_bp
from routes.kakao_notification_routes import kakao_notification_bp
from routes.enhanced_auth_routes import enhanced_auth_bp
from routes.iot_sensor_routes import iot_sensor_bp
from routes.dashboard_routes import dashboard_bp
from routes.mobile_app_routes import mobile_app_bp
from routes.analytics_routes import analytics_bp
from admin.routes.admin_routes import admin_bp
from models.database import init_db

# AI 훈련 모듈 import (올바른 경로)
from services.ai_service import ensemble_ai_service

# IoT 센서 서비스 import
from services.sensor_data_service import sensor_data_service
from services.realtime_streaming_service import realtime_streaming_service
from services.sensor_monitoring_service import sensor_monitoring_service
from services.firmware_ota_service import firmware_ota_service

def create_app():
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "signalcraft_secret_key_2024_very_secure_12345")
    app.register_blueprint(kakao_auth_bp)
    # 업로드 폴더 설정
    app.config['UPLOAD_FOLDER'] = 'uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # 데이터베이스 초기화
    init_db()

    # Sentry 초기화
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            FlaskIntegration(),
            RedisIntegration(),  # Celery 사용 시 필요
        ],
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment=os.getenv('FLASK_ENV', 'production'),
        release=os.getenv('APP_VERSION', 'unknown')
    )

    # CORS 설정
    # origins를 명확히 지정하여 보안 강화
    CORS(app,
         origins=['https://signalcraft.kr', 'https://www.signalcraft.kr'],
         allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         supports_credentials=True)

    # CORS preflight 요청 처리
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({})
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin"))
            response.headers.add('Access-Control-Allow-Headers', request.headers.get("Access-Control-Request-Headers"))
            response.headers.add('Access-Control-Allow-Methods', request.headers.get("Access-Control-Request-Method"))
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response

    # 라우트 블루프린트 등록
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(monitoring_bp)
    # AI 라우트 등록 (기존 코드를 ai_routes.py로 통일)
    app.register_blueprint(ai_bp)
    # ESP32 통합 라우트 등록
    app.register_blueprint(esp32_bp)
    # 알림 라우트 등록
    app.register_blueprint(notification_bp)
    # 카카오톡 알림 라우트 등록
    app.register_blueprint(kakao_notification_bp)
    # 향상된 인증 라우트 등록
    app.register_blueprint(enhanced_auth_bp)
    # IoT 센서 시스템 라우트 등록
    app.register_blueprint(iot_sensor_bp)
    # 대시보드 라우트 등록 # NEW
    app.register_blueprint(dashboard_bp)
    # 모바일 앱 라우트 등록 # NEW
    app.register_blueprint(mobile_app_bp)
    # 분석 시스템 라우트 등록 # NEW
    app.register_blueprint(analytics_bp)

    # 정적 파일 서빙을 위한 라우트 추가 (dashboard-components)
    @app.route('/static/dashboard-components/<path:filename>')
    def serve_dashboard_components(filename):
        return send_from_directory(os.path.join(app.root_path, 'static', 'dashboard-components'), filename)
    
    # IoT 센서 서비스 초기화
sensor_monitoring_service.start_monitoring()
    
    # API 라우트 추가 (프론트엔드 호환성)
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    from routes.auth_routes import login
    return login()
    
@app.route('/api/auth/register', methods=['POST'])
def api_register():
    from routes.auth_routes import register
    return register()
    
@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    from routes.auth_routes import logout
    return logout()
    
@app.route('/api/auth/verify', methods=['GET'])
def api_verify():
    from routes.auth_routes import auth_status
    return auth_status()
    
customer-dashboard
@app.route('/api/lightweight-analyze', methods=['POST'])
def api_lightweight_analyze():
    from routes.ai_routes import lightweight_analyze
    return lightweight_analyze()

@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    from flask import render_template
    return render_template('dashboard.html')

    @app.route('/mobile_app')
    def mobile_app():
        """모바일 앱 페이지"""
        from flask import render_template
        return render_template('mobile_app.html')

    @app.route('/notifications')
    def notification_dashboard():
        """알림 관리 대시보드 페이지"""
        from flask import render_template
        return render_template('notification_dashboard.html')

    @app.route('/dashboard')
    def dashboard():
        """메인 대시보드 페이지"""
        from flask import render_template
        return render_template('customer/refactored-dashboard.html')

    @app.route('/original-dashboard')
    def original_dashboard():
        """원래 대시보드 페이지"""
        from flask import render_template
        return render_template('customer/dashboard.html')

    @app.route('/mobile_friendly_dashboard')
    def mobile_friendly_dashboard():
        """모바일 친화적 대시보드 페이지"""
        from flask import render_template
        return render_template('customer/mobile_friendly_dashboard.html')

    @app.route('/admin')
    def admin_dashboard():
        """관리자 대시보드 페이지"""
        from flask import render_template
        return render_template('admin_dashboard.html')

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/admin')
def admin_dashboard():
    """관리자 대시보드 페이지"""
    from flask import render_template
    return render_template('admin_dashboard.html')

if __name__ == '__main__':
    import os
    
    app = create_app()
    
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    print("=== 🚀 모듈화된 Flask 서버 시작 ===")
    print(f"포트: {port}, 디버그: {debug}")
    print("라우트 목록:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {list(rule.methods)}")
    print("=" * 50)

    # 개발 환경에서는 디버그 모드 활성화
    if debug:
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        app.run(host='0.0.0.0', port=port, debug=False)
