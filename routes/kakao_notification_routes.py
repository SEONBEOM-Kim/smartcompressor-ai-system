#!/usr/bin/env python3
"""
카카오톡 알림 관련 API 라우트
카카오톡 알림 테스트 및 관리를 위한 API를 제공합니다.
"""

from flask import Blueprint, request, jsonify
import logging
from services.kakao_notification_service import kakao_notification_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 카카오톡 알림 라우트 블루프린트 생성
kakao_notification_bp = Blueprint('kakao_notifications', __name__, url_prefix='/api/kakao')

@kakao_notification_bp.route('/test', methods=['POST'])
def test_kakao_notification():
    """카카오톡 알림 테스트"""
    try:
        data = request.get_json()
        
        phone_number = data.get('phone_number')
        if not phone_number:
            return jsonify({
                'success': False,
                'message': '전화번호가 필요합니다.'
            }), 400
        
        # 테스트 알림 전송
        success = kakao_notification_service.test_notification(phone_number)
        
        if success:
            return jsonify({
                'success': True,
                'message': '카카오톡 테스트 알림이 전송되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '카카오톡 테스트 알림 전송에 실패했습니다.'
            }), 500
            
    except Exception as e:
        logger.error(f"카카오톡 테스트 알림 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'카카오톡 테스트 알림 오류: {str(e)}'
        }), 500

@kakao_notification_bp.route('/send', methods=['POST'])
def send_kakao_notification():
    """카카오톡 알림 전송"""
    try:
        data = request.get_json()
        
        phone_number = data.get('phone_number')
        alert_type = data.get('alert_type', 'general_alert')
        device_id = data.get('device_id', 'UNKNOWN')
        severity = data.get('severity', 'medium')
        message = data.get('message', '카카오톡 알림입니다.')
        
        if not phone_number:
            return jsonify({
                'success': False,
                'message': '전화번호가 필요합니다.'
            }), 400
        
        # 카카오톡 알림 전송
        success = kakao_notification_service.send_notification(
            phone_number=phone_number,
            alert_type=alert_type,
            device_id=device_id,
            severity=severity,
            message=message
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '카카오톡 알림이 전송되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '카카오톡 알림 전송에 실패했습니다.'
            }), 500
            
    except Exception as e:
        logger.error(f"카카오톡 알림 전송 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'카카오톡 알림 전송 오류: {str(e)}'
        }), 500

@kakao_notification_bp.route('/templates', methods=['GET'])
def get_kakao_templates():
    """카카오톡 알림 템플릿 목록 조회"""
    try:
        templates = kakao_notification_service.get_template_list()
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"카카오톡 템플릿 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'카카오톡 템플릿 조회 오류: {str(e)}'
        }), 500

@kakao_notification_bp.route('/status', methods=['GET'])
def get_kakao_status():
    """카카오톡 서비스 상태 조회"""
    try:
        import os
        
        access_token = os.getenv('KAKAO_ACCESS_TOKEN', '')
        phone_numbers = os.getenv('KAKAO_PHONE_NUMBERS', '').split(',')
        
        status = {
            'access_token_configured': bool(access_token),
            'phone_numbers_configured': len(phone_numbers) > 0 and phone_numbers[0] != '',
            'phone_count': len([p for p in phone_numbers if p.strip()]),
            'service_ready': bool(access_token) and len(phone_numbers) > 0 and phone_numbers[0] != ''
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"카카오톡 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'카카오톡 상태 조회 오류: {str(e)}'
        }), 500
