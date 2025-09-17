from flask import Blueprint, render_template, send_from_directory, jsonify, request
import os
import time
import logging

# 로거 설정
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/contact')
def contact():
    """고객 문의 페이지"""
    return render_template('customer/contact.html')

@main_bp.route('/faq')
def faq():
    """FAQ 페이지"""
    return render_template('faq.html')

@main_bp.route('/api/contact', methods=['POST'])
def api_contact():
    """고객 문의 API"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone', '')
        subject = data.get('subject')
        category = data.get('category')
        message = data.get('message')

        # 필수 필드 검증
        if not all([name, email, subject, category, message]):
            return jsonify({
                'success': False,
                'message': '필수 항목을 모두 입력해주세요.'
            })

        logger.info(f"문의 접수: {name} ({email}) - {subject} [{category}]")
        logger.info(f"문의 내용: {message}")

        return jsonify({
            'success': True,
            'message': '문의가 접수되었습니다. 빠른 시일 내에 답변드리겠습니다.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'문의 접수 중 오류가 발생했습니다: {str(e)}'
        })

@main_bp.route('/ai-test')
def ai_test():
    """AI 정확도 테스트 페이지"""
    return render_template('ai_test.html')

@main_bp.route('/diagnosis-report')
def diagnosis_report():
    """진단 리포트 페이지"""
    return render_template('diagnosis_report.html')

@main_bp.route('/simple-demo')
def simple_demo():
    """간단한 AI 진단 데모 페이지"""
    return render_template('simple_ai_demo.html')

@main_bp.route('/')
def home():
    """홈페이지"""
    return render_template('index.html')

@main_bp.route('/static/<path:filename>')
def static_files(filename):
    """정적 파일 서빙"""
    return send_from_directory('static', filename)


@main_bp.route('/pricing')
def pricing():
    return jsonify({
        "plans": [
            {
                "name": "기본 플랜",
                "price": "월 29,000원",
                "features": ["실시간 모니터링", "기본 알림"]
            },
            {
                "name": "프리미엄 플랜",
                "price": "월 59,000원",
                "features": ["실시간 모니터링", "고급 알림", "AI 분석"]
            }
        ]
    })

@main_bp.route('/favicon.ico')
def favicon():
    """파비콘"""
    return send_from_directory('static', 'favicon.ico')

@main_bp.route('/debug/routes')
def debug_routes():
    """디버그: 라우트 목록"""
    from flask import current_app
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'rule': rule.rule,
            'methods': list(rule.methods),
            'endpoint': rule.endpoint
        })
    return jsonify(routes)

@main_bp.route('/api/lightweight-analyze', methods=['POST'])
def api_lightweight_analyze():
    """경량화된 압축기 과부하음 분석 API"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        timestamp = request.form.get('timestamp')

        # 경량화 AI 모델 호출 로직을 여기에 구현
        # 현재는 임시 결과 반환
        result = {
            'overall_status': 'normal',  # 또는 'overload'
            'average_confidence': 0.9,
            'total_processing_time_ms': 500
        }

        # 단순화된 응답
        return jsonify({
            "is_overload": result.get('overall_status') == 'overload',
            "confidence": result.get('average_confidence', 0.0),
            "processing_time_ms": result.get('total_processing_time_ms', 0.0),
            "message": "과부하음 감지됨" if result.get('overall_status') == 'overload' else "정상 작동 중",
            "timestamp": time.time(),
            "status": "success"
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error",
            "is_overload": False,
            "confidence": 0.0,
            "message": "분석 중 오류가 발생했습니다."
        }), 500

@main_bp.route('/ai-demo')
def ai_demo():
    """AI 진단 데모 페이지"""
    return render_template('ai_demo.html')
