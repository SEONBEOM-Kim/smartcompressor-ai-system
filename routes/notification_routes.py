#!/usr/bin/env python3
"""
알림 관련 API 라우트
실시간 알림 스트림과 알림 관리를 위한 API를 제공합니다.
"""

from flask import Blueprint, request, jsonify, Response, stream_with_context
import json
import time
import logging
from services.notification_service import notification_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 알림 라우트 블루프린트 생성
notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

@notification_bp.route('/stream')
def notification_stream():
    """실시간 알림 스트림 (Server-Sent Events)"""
    
    def generate_notifications():
        """알림 스트림 생성"""
        # 연결 확인 메시지
        yield f"data: {json.dumps({'type': 'connected', 'message': '알림 스트림 연결됨'})}\n\n"
        
        # 구독자 콜백 함수
        def on_notification(alert):
            try:
                notification_data = {
                    'type': 'notification',
                    'alert_id': alert.alert_id,
                    'device_id': alert.device_id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'message': alert.message,
                    'timestamp': alert.timestamp,
                    'data': alert.data,
                    'read': False
                }
                yield f"data: {json.dumps(notification_data)}\n\n"
            except Exception as e:
                logger.error(f"알림 스트림 오류: {e}")
        
        # 구독자 등록
        notification_service.subscribe(on_notification)
        
        # 연결 유지
        while True:
            try:
                yield f"data: {json.dumps({'type': 'ping', 'timestamp': time.time()})}\n\n"
                time.sleep(30)  # 30초마다 ping
            except GeneratorExit:
                logger.info("알림 스트림 연결 종료")
                break
            except Exception as e:
                logger.error(f"알림 스트림 오류: {e}")
                break
    
    return Response(
        stream_with_context(generate_notifications()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )

@notification_bp.route('/', methods=['GET'])
def get_notifications():
    """알림 목록 조회"""
    try:
        device_id = request.args.get('device_id')
        limit = int(request.args.get('limit', 100))
        severity = request.args.get('severity')
        
        # 알림 이력 조회
        alerts = notification_service.get_alert_history(device_id, limit)
        
        # 심각도 필터링
        if severity:
            alerts = [alert for alert in alerts if alert['severity'] == severity]
        
        # 읽음 상태 추가
        for alert in alerts:
            alert['read'] = False  # 기본값
        
        return jsonify({
            'success': True,
            'notifications': alerts,
            'total_count': len(alerts)
        })
        
    except Exception as e:
        logger.error(f"알림 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 목록 조회 오류: {str(e)}'
        }), 500

@notification_bp.route('/<alert_id>/read', methods=['POST'])
def mark_as_read(alert_id):
    """알림 읽음 처리"""
    try:
        # 실제로는 데이터베이스에서 읽음 상태 업데이트
        # 여기서는 간단히 성공 응답
        return jsonify({
            'success': True,
            'message': '알림을 읽음으로 처리했습니다.'
        })
        
    except Exception as e:
        logger.error(f"알림 읽음 처리 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 읽음 처리 오류: {str(e)}'
        }), 500

@notification_bp.route('/read-all', methods=['POST'])
def mark_all_as_read():
    """모든 알림 읽음 처리"""
    try:
        # 실제로는 데이터베이스에서 모든 알림을 읽음으로 처리
        return jsonify({
            'success': True,
            'message': '모든 알림을 읽음으로 처리했습니다.'
        })
        
    except Exception as e:
        logger.error(f"모든 알림 읽음 처리 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'모든 알림 읽음 처리 오류: {str(e)}'
        }), 500

@notification_bp.route('/test', methods=['POST'])
def test_notification():
    """테스트 알림 전송"""
    try:
        data = request.get_json()
        
        device_id = data.get('device_id', 'TEST_DEVICE')
        alert_type = data.get('alert_type', 'test_alert')
        severity = data.get('severity', 'medium')
        message = data.get('message', '테스트 알림입니다.')
        
        # 테스트 알림 전송
        success = notification_service.send_alert(
            device_id=device_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            data={'test': True}
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '테스트 알림이 전송되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': '테스트 알림 전송에 실패했습니다.'
            }), 500
            
    except Exception as e:
        logger.error(f"테스트 알림 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'테스트 알림 오류: {str(e)}'
        }), 500

@notification_bp.route('/channels', methods=['GET'])
def get_notification_channels():
    """알림 채널 목록 조회"""
    try:
        channels = []
        for channel in notification_service.channels:
            channels.append({
                'type': channel.channel_type,
                'enabled': channel.enabled,
                'priority': channel.priority
            })
        
        return jsonify({
            'success': True,
            'channels': channels
        })
        
    except Exception as e:
        logger.error(f"알림 채널 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 채널 조회 오류: {str(e)}'
        }), 500

@notification_bp.route('/channels', methods=['POST'])
def add_notification_channel():
    """알림 채널 추가"""
    try:
        data = request.get_json()
        
        channel_type = data.get('type')
        config = data.get('config', {})
        enabled = data.get('enabled', True)
        priority = data.get('priority', 1)
        
        if not channel_type:
            return jsonify({
                'success': False,
                'message': '채널 타입이 필요합니다.'
            }), 400
        
        # 새 채널 생성
        from services.notification_service import NotificationChannel
        new_channel = NotificationChannel(
            channel_type=channel_type,
            config=config,
            enabled=enabled,
            priority=priority
        )
        
        # 채널 추가
        notification_service.add_channel(new_channel)
        
        return jsonify({
            'success': True,
            'message': '알림 채널이 추가되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"알림 채널 추가 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 채널 추가 오류: {str(e)}'
        }), 500
