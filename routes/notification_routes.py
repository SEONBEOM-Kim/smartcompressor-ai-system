#!/usr/bin/env python3
"""
알림 관리 API 라우트
Slack과 Discord 스타일의 실시간 커뮤니케이션 API
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from services.notification_service import unified_notification_service
from services.kakao_business_service import kakao_business_service
from services.sms_notification_service import sms_notification_service
from services.email_template_service import email_template_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')

@notification_bp.route('/status', methods=['GET'])
def get_notification_status():
    """알림 서비스 상태 조회"""
    try:
        status = unified_notification_service.get_service_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"알림 서비스 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/channels', methods=['GET'])
def get_channels():
    """지원하는 알림 채널 목록 조회"""
    try:
        channels = unified_notification_service.get_channel_statistics()
        return jsonify({
            'success': True,
            'channels': channels
        })
    except Exception as e:
        logger.error(f"알림 채널 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/test/<channel_name>', methods=['POST'])
def test_channel(channel_name):
    """특정 채널 테스트"""
    try:
        result = unified_notification_service.test_channel(channel_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"채널 테스트 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/send', methods=['POST'])
def send_notification():
    """알림 전송"""
    try:
        data = request.get_json()
        
        notification_type = data.get('type', 'general')
        message_data = data.get('data', {})
        channels = data.get('channels', ['websocket'])
        priority = data.get('priority', 'normal')
        recipient = data.get('recipient')
        
        success = unified_notification_service.send_notification(
            notification_type=notification_type,
            data=message_data,
            channels=channels,
            recipient=recipient,
            priority=priority
        )
        
        return jsonify({
            'success': success,
            'message': '알림이 전송되었습니다' if success else '알림 전송에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"알림 전송 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/emergency', methods=['POST'])
def send_emergency_alert():
    """긴급 알림 전송"""
    try:
        data = request.get_json()
        
        alert_data = data.get('alert_data', {})
        channels = data.get('channels', ['websocket', 'slack', 'discord'])
        
        success = unified_notification_service.send_emergency_alert(
            alert_data=alert_data,
            channels=channels
        )
        
        return jsonify({
            'success': success,
            'message': '긴급 알림이 전송되었습니다' if success else '긴급 알림 전송에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"긴급 알림 전송 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/equipment', methods=['POST'])
def send_equipment_alert():
    """장비 상태 알림 전송"""
    try:
        data = request.get_json()
        
        equipment_data = data.get('equipment_data', {})
        user_email = data.get('user_email')
        user_kakao_id = data.get('user_kakao_id')
        
        success = unified_notification_service.send_equipment_alert(
            equipment_data=equipment_data,
            user_email=user_email,
            user_kakao_id=user_kakao_id
        )
        
        return jsonify({
            'success': success,
            'message': '장비 알림이 전송되었습니다' if success else '장비 알림 전송에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"장비 알림 전송 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/order', methods=['POST'])
def send_order_notification():
    """주문 알림 전송"""
    try:
        data = request.get_json()
        
        order_data = data.get('order_data', {})
        user_email = data.get('user_email')
        user_kakao_id = data.get('user_kakao_id')
        
        success = unified_notification_service.send_order_notification(
            order_data=order_data,
            user_email=user_email,
            user_kakao_id=user_kakao_id
        )
        
        return jsonify({
            'success': success,
            'message': '주문 알림이 전송되었습니다' if success else '주문 알림 전송에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"주문 알림 전송 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/history', methods=['GET'])
def get_notification_history():
    """알림 히스토리 조회"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        history = unified_notification_service.get_notification_history(limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'total_count': len(history)
        })
        
    except Exception as e:
        logger.error(f"알림 히스토리 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 카카오톡 비즈니스 API
@notification_bp.route('/kakao/register', methods=['POST'])
def register_kakao_user():
    """카카오톡 사용자 등록"""
    try:
        data = request.get_json()
        
        from services.kakao_business_service import KakaoUser
        
        user = KakaoUser(
            user_id=data.get('user_id'),
            kakao_id=data.get('kakao_id'),
            nickname=data.get('nickname'),
            phone=data.get('phone'),
            email=data.get('email')
        )
        
        result = kakao_business_service.register_user(user)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"카카오톡 사용자 등록 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/kakao/send', methods=['POST'])
def send_kakao_message():
    """카카오톡 메시지 전송"""
    try:
        data = request.get_json()
        
        from services.kakao_business_service import KakaoMessage, MessageType, Priority
        
        message = KakaoMessage(
            message_type=MessageType(data.get('message_type', 'text')),
            content=data.get('content'),
            priority=Priority(data.get('priority', 'normal'))
        )
        
        user_id = data.get('user_id')
        result = kakao_business_service.send_message(user_id, message)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"카카오톡 메시지 전송 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/kakao/template', methods=['POST'])
def create_kakao_template():
    """카카오톡 메시지 템플릿 생성"""
    try:
        data = request.get_json()
        
        result = kakao_business_service.create_message_template(
            template_id=data.get('template_id'),
            template=data.get('template')
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"카카오톡 템플릿 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# SMS 알림 API
@notification_bp.route('/sms/send', methods=['POST'])
def send_sms():
    """SMS 전송"""
    try:
        data = request.get_json()
        
        from services.sms_notification_service import SMSMessage, SMSProvider
        
        message = SMSMessage(
            to=data.get('to'),
            content=data.get('content'),
            provider=SMSProvider(data.get('provider', 'twilio')),
            priority=data.get('priority', 'normal')
        )
        
        result = sms_notification_service.send_sms(message)
        
        return jsonify({
            'success': result.status.value == 'sent',
            'message_id': result.message_id,
            'status': result.status.value,
            'error': result.error_message
        })
        
    except Exception as e:
        logger.error(f"SMS 전송 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/sms/template', methods=['POST'])
def create_sms_template():
    """SMS 템플릿 생성"""
    try:
        data = request.get_json()
        
        success = sms_notification_service.create_template(
            template_id=data.get('template_id'),
            content=data.get('content'),
            variables=data.get('variables', [])
        )
        
        return jsonify({
            'success': success,
            'message': 'SMS 템플릿이 생성되었습니다' if success else 'SMS 템플릿 생성에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"SMS 템플릿 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/sms/history', methods=['GET'])
def get_sms_history():
    """SMS 히스토리 조회"""
    try:
        limit = request.args.get('limit', 100, type=int)
        status = request.args.get('status')
        
        from services.sms_notification_service import SMSStatus
        
        history = sms_notification_service.get_message_history(
            limit=limit,
            status=SMSStatus(status) if status else None
        )
        
        return jsonify({
            'success': True,
            'history': history,
            'total_count': len(history)
        })
        
    except Exception as e:
        logger.error(f"SMS 히스토리 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/sms/statistics', methods=['GET'])
def get_sms_statistics():
    """SMS 통계 조회"""
    try:
        stats = sms_notification_service.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"SMS 통계 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 이메일 템플릿 API
@notification_bp.route('/email/templates', methods=['GET'])
def get_email_templates():
    """이메일 템플릿 목록 조회"""
    try:
        templates = email_template_service.get_template_list()
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        logger.error(f"이메일 템플릿 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/email/templates', methods=['POST'])
def create_email_template():
    """이메일 템플릿 생성"""
    try:
        data = request.get_json()
        
        success = email_template_service.create_template(
            template_id=data.get('template_id'),
            name=data.get('name'),
            subject=data.get('subject'),
            html_content=data.get('html_content'),
            text_content=data.get('text_content'),
            variables=data.get('variables', []),
            category=data.get('category', 'general')
        )
        
        return jsonify({
            'success': success,
            'message': '이메일 템플릿이 생성되었습니다' if success else '이메일 템플릿 생성에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"이메일 템플릿 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/email/templates/<template_id>', methods=['GET'])
def get_email_template(template_id):
    """이메일 템플릿 조회"""
    try:
        template = email_template_service.get_template(template_id)
        
        if template:
            return jsonify({
                'success': True,
                'template': {
                    'template_id': template.template_id,
                    'name': template.name,
                    'subject': template.subject,
                    'html_content': template.html_content,
                    'text_content': template.text_content,
                    'variables': template.variables,
                    'category': template.category,
                    'is_active': template.is_active,
                    'created_at': template.created_at.isoformat() if template.created_at else None,
                    'updated_at': template.updated_at.isoformat() if template.updated_at else None
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '템플릿을 찾을 수 없습니다'
            }), 404
        
    except Exception as e:
        logger.error(f"이메일 템플릿 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/email/templates/<template_id>/render', methods=['POST'])
def render_email_template(template_id):
    """이메일 템플릿 렌더링"""
    try:
        data = request.get_json()
        
        variables = data.get('variables', {})
        rendered = email_template_service.render_template(template_id, variables)
        
        if rendered:
            return jsonify({
                'success': True,
                'rendered': {
                    'subject': rendered.subject,
                    'content': rendered.content,
                    'html_content': rendered.html_content
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '템플릿 렌더링에 실패했습니다'
            }), 400
        
    except Exception as e:
        logger.error(f"이메일 템플릿 렌더링 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/email/templates/<template_id>/validate', methods=['POST'])
def validate_email_template(template_id):
    """이메일 템플릿 유효성 검사"""
    try:
        data = request.get_json()
        
        variables = data.get('variables', {})
        validation = email_template_service.validate_template(template_id, variables)
        
        return jsonify(validation)
        
    except Exception as e:
        logger.error(f"이메일 템플릿 유효성 검사 오류: {e}")
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500

@notification_bp.route('/email/templates/<template_id>', methods=['PUT'])
def update_email_template(template_id):
    """이메일 템플릿 업데이트"""
    try:
        data = request.get_json()
        
        success = email_template_service.update_template(template_id, **data)
        
        return jsonify({
            'success': success,
            'message': '이메일 템플릿이 업데이트되었습니다' if success else '이메일 템플릿 업데이트에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"이메일 템플릿 업데이트 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@notification_bp.route('/email/templates/<template_id>', methods=['DELETE'])
def delete_email_template(template_id):
    """이메일 템플릿 삭제"""
    try:
        success = email_template_service.delete_template(template_id)
        
        return jsonify({
            'success': success,
            'message': '이메일 템플릿이 삭제되었습니다' if success else '이메일 템플릿 삭제에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"이메일 템플릿 삭제 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500