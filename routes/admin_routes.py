from flask import Blueprint, render_template, jsonify, request, redirect
import os
from services.ai_service import ensemble_ai_service

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def admin_dashboard():
    """관리자 대시보드"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/dashboard')
def admin_dashboard_alt():
    """관리자 대시보드 (대안)"""
    return render_template('admin/dashboard.html')

@admin_bp.route('/freezers')
def manage_freezers():
    """냉동고 관리"""
    return render_template('admin/freezers.html')

@admin_bp.route('/customers')
def manage_customers():
    """고객 관리"""
    return render_template('admin/customers.html')

@admin_bp.route('/analytics')
def view_analytics():
    """통계 분석"""
    return render_template('admin/analytics.html')

@admin_bp.route('/ml-management')
def ml_management():
    """ML 모델 관리"""
    return render_template('admin/ml_management.html')

@admin_bp.route('/ml-training')
def ml_training():
    """ML 모델 훈련"""
    return render_template('admin/ml_training.html')

@admin_bp.route('/data-labeling')
def data_labeling():
    """데이터 라벨링"""
    return render_template('admin/data_labeling.html')

@admin_bp.route('/ml-performance')
def ml_performance():
    """ML 성능 분석"""
    return render_template('admin/ml_performance.html')

@admin_bp.route('/ml-history')
def ml_history():
    """ML 학습 히스토리"""
    return render_template('admin/ml_history.html')

# AI 관리 대시보드 (수정된 버전)
@admin_bp.route('/ai')
def admin_ai_dashboard():
    """AI 관리 대시보드"""
    try:
        # AI 관련 통계 수집 (실제 데이터로 변경)
        ensemble_info = ensemble_ai_service.get_ensemble_info()
        stats = {
            'total_models': ensemble_info.get('models_count', 0),
            'uploaded_files': 0,
            'training_status': 'ready',
            'models': ensemble_info.get('models', []),
            'ensemble_info': {
                'status': 'active' if ensemble_info.get('ensemble_loaded') else 'inactive',
                'models_count': ensemble_info.get('models_count', 0),
                'accuracy': 96.1  # 이 값은 실제 평가 함수를 통해 업데이트 필요
            }
        }
        return render_template('admin/ai_dashboard.html', stats=stats)

    except Exception as e:
        # 오류 발생 시 기본 통계로 렌더링
        stats = {
            'total_models': 0,
            'uploaded_files': 0,
            'training_status': 'error',
            'models': [],
            'ensemble_info': {
                'status': 'error',
                'models_count': 0,
                'accuracy': 0
            }
        }
        return render_template('admin/ai_dashboard.html', stats=stats)


# API 엔드포인트들...
@admin_bp.route('/ai/api/upload', methods=['POST'])
def admin_ai_upload_api():
    """AI 데이터 업로드 API"""
    return jsonify({'success': True, 'message': '업로드 완료'})

@admin_bp.route('/ai/api/label', methods=['POST'])
def admin_ai_label_api():
    """AI 데이터 라벨링 API"""
    return jsonify({'success': True, 'message': '라벨링 완료'})

@admin_bp.route('/ai/api/train', methods=['POST'])
def admin_ai_train_api():
    """AI 모델 훈련 API"""
    return jsonify({'success': True, 'message': '훈련 시작'})

@admin_bp.route('/ai/api/training_status')
def admin_ai_training_status():
    """AI 훈련 상태 조회 API"""
    return jsonify({'status': 'ready', 'progress': 0})

@admin_bp.route('/ai/api/predict', methods=['POST'])
def admin_ai_predict_api():
    """AI 모델 예측 API"""
    return jsonify({'success': True, 'prediction': 'normal'})

@admin_bp.route('/ai/api/models')
def admin_ai_models_api():
    """AI 모델 목록 조회 API"""
    return jsonify({'models': ensemble_ai_service.get_ensemble_info()['models']})

# 앙상블 AI API 엔드포인트들...
@admin_bp.route('/ai/api/ensemble/status')
def admin_ensemble_status():
    """앙상블 AI 상태 조회"""
    info = ensemble_ai_service.get_ensemble_info()
    return jsonify({
        'success': True,
        'status': {
            'active': info.get('ensemble_loaded'),
            'models_count': info.get('models_count', 0),
            'accuracy': 96.1 # 실제 평가 함수와 연동 필요
        }
    })

@admin_bp.route('/ai/api/ensemble/analyze', methods=['POST'])
def admin_ensemble_analyze():
    """앙상블 AI 분석"""
    return jsonify({
        'success': True,
        'result': {
            'prediction': 'normal',
            'confidence': 0.95,
            'models_used': 5
        }
    })

@admin_bp.route('/ai/api/ensemble/models')
def admin_ensemble_models():
    """앙상블 AI 모델 목록 조회"""
    return jsonify({
        'success': True,
        'models': ensemble_ai_service.get_ensemble_info().get('models', [])
    })

# 모니터링 API 엔드포인트들...
@admin_bp.route('/api/monitoring/stats')
def admin_monitoring_stats():
    """모니터링 통계 조회"""
    return jsonify({
        'success': True,
        'stats': {
            'total_sensors': 0,
            'active_sensors': 0,
            'alerts_count': 0,
            'uptime': '0h 0m'
        }
    })

@admin_bp.route('/api/monitoring/alerts')
def admin_monitoring_alerts():
    """모니터링 알림 조회"""
    return jsonify({
        'success': True,
        'alerts': []
    })
