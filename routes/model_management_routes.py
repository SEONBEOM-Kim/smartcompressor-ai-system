#!/usr/bin/env python3
"""
모델 관리 API 라우트
AI 모델 OTA 업데이트, 버전 관리, 롤백 기능을 제공하는 API
"""

from flask import Blueprint, request, jsonify
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

model_mgmt_bp = Blueprint('model_management', __name__, url_prefix='/api/model-management')

@model_mgmt_bp.route('/status', methods=['GET'])
def get_model_status():
    """모델 상태 조회"""
    try:
        from services.model_management_service import model_management_service
        status = model_management_service.get_model_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"모델 상태 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@model_mgmt_bp.route('/check-updates', methods=['POST'])
def check_updates():
    """모델 업데이트 확인 및 적용"""
    try:
        from services.model_management_service import model_management_service
        
        # 업데이트 확인 및 적용
        updates = model_management_service.check_and_update_models()
        
        return jsonify({
            'success': True,
            'updates_applied': len(updates),
            'updates': updates
        })
        
    except Exception as e:
        logger.error(f"모델 업데이트 확인 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@model_mgmt_bp.route('/rollback', methods=['POST'])
def rollback_model():
    """모델 롤백"""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        target_version = data.get('target_version')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': '모델 이름이 필요합니다'
            }), 400
        
        from services.model_management_service import model_management_service
        result = model_management_service.rollback_model(model_name, target_version)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"모델 롤백 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@model_mgmt_bp.route('/start-monitoring', methods=['POST'])
def start_monitoring():
    """모델 업데이트 모니터링 시작"""
    try:
        from services.model_management_service import model_management_service
        model_management_service.start_monitoring()
        
        return jsonify({
            'success': True,
            'message': '모델 업데이트 모니터링이 시작되었습니다'
        })
        
    except Exception as e:
        logger.error(f"모니터링 시작 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@model_mgmt_bp.route('/stop-monitoring', methods=['POST'])
def stop_monitoring():
    """모델 업데이트 모니터링 중지"""
    try:
        from services.model_management_service import model_management_service
        model_management_service.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': '모델 업데이트 모니터링이 중지되었습니다'
        })
        
    except Exception as e:
        logger.error(f"모니터링 중지 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@model_mgmt_bp.route('/upload-model', methods=['POST'])
def upload_model():
    """모델 파일 업로드"""
    try:
        if 'model_file' not in request.files:
            return jsonify({
                'success': False,
                'error': '모델 파일이 필요합니다'
            }), 400
        
        model_file = request.files['model_file']
        model_name = request.form.get('model_name')
        version = request.form.get('version', '1.0.0')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': '모델 이름이 필요합니다'
            }), 400
        
        # 임시 파일로 저장
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
            model_file.save(tmp_file.name)
            
            # 모델 업데이트 정보 생성
            update_info = {
                'model_name': model_name,
                'version': version,
                'file_path': tmp_file.name,
                'source': 'upload',
                'size': len(model_file.read()),
                'uploaded_at': __import__('datetime').datetime.now().isoformat()
            }
            
            # 모델 업데이트 적용
            from services.model_management_service import model_management_service
            from services.model_management_service import LocalFileSource
            
            local_source = LocalFileSource('data/model_updates')
            result = model_management_service.update_model(update_info, local_source)
            
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"모델 업로드 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@model_mgmt_bp.route('/models/<model_name>/versions', methods=['GET'])
def get_model_versions(model_name):
    """특정 모델의 버전 목록 조회"""
    try:
        from services.model_management_service import model_management_service
        
        if model_name not in model_management_service.model_versions:
            return jsonify({
                'success': False,
                'error': f'모델 {model_name}을 찾을 수 없습니다'
            }), 404
        
        versions = model_management_service.model_versions[model_name]
        active_version = model_management_service.active_versions.get(model_name)
        
        return jsonify({
            'success': True,
            'model_name': model_name,
            'active_version': active_version,
            'versions': [v.to_dict() for v in versions]
        })
        
    except Exception as e:
        logger.error(f"모델 버전 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@model_mgmt_bp.route('/health', methods=['GET'])
def health_check():
    """서비스 상태 확인"""
    try:
        from services.model_management_service import model_management_service
        status = model_management_service.get_service_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"서비스 상태 확인 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
