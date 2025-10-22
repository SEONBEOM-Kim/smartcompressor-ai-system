#!/usr/bin/env python3
"""
모바일 앱 API 라우트
Tesla App & Starbucks App 벤치마킹한 점주용 모바일 앱 API
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from services.mobile_push_service import mobile_push_service, PushNotification, PushNotificationType, PushPriority
from services.offline_sync_service import offline_sync_service, DataType
from services.real_time_monitoring_service import real_time_monitoring_service
from services.remote_control_service import remote_control_service, RemoteCommand, ControlCommand, CommandStatus
from services.mobile_payment_service import mobile_payment_service, PaymentTransaction, PaymentMethod, PaymentStatus

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
mobile_app_bp = Blueprint('mobile_app', __name__, url_prefix='/api/mobile_app')

# ==================== PWA 및 오프라인 기능 ====================

@mobile_app_bp.route('/pwa/install', methods=['POST'])
def install_pwa():
    """PWA 설치 요청"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        # PWA 설치 로그
        logger.info(f"PWA 설치 요청: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'PWA 설치가 완료되었습니다',
            'data': {
                'user_id': user_id,
                'installed_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"PWA 설치 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/offline/sync', methods=['POST'])
def sync_offline_data():
    """오프라인 데이터 동기화"""
    try:
        data = request.get_json()
        data_type = DataType(data.get('data_type', 'dashboard'))
        sync_data = data.get('data', {})
        
        # 오프라인 데이터 저장
        data_id = offline_sync_service.save_offline_data(
            data_type=data_type,
            data=sync_data,
            priority=data.get('priority', 1)
        )
        
        if data_id:
            return jsonify({
                'success': True,
                'message': '오프라인 데이터가 저장되었습니다',
                'data_id': data_id
            })
        else:
            return jsonify({
                'success': False,
                'error': '오프라인 데이터 저장 실패'
            }), 500
            
    except Exception as e:
        logger.error(f"오프라인 동기화 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/offline/status', methods=['GET'])
def get_offline_status():
    """오프라인 동기화 상태 조회"""
    try:
        status = offline_sync_service.get_sync_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"오프라인 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 푸시 알림 ====================

@mobile_app_bp.route('/push/register', methods=['POST'])
def register_push_subscription():
    """푸시 알림 구독 등록"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        subscription = data.get('subscription')
        
        if not user_id or not subscription:
            return jsonify({
                'success': False,
                'error': 'user_id와 subscription이 필요합니다'
            }), 400
        
        success = mobile_push_service.register_subscription(user_id, subscription)
        
        return jsonify({
            'success': success,
            'message': '푸시 알림 구독이 등록되었습니다' if success else '푸시 알림 구독 등록에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"푸시 알림 구독 등록 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/push/test', methods=['POST'])
def test_push_notification():
    """푸시 알림 테스트"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        notification_type = data.get('type', 'diagnosis')
        
        # 테스트 알림 생성
        if notification_type == 'diagnosis':
            notification = mobile_push_service.create_notification(
                title="🔍 진단 테스트",
                body="압축기 진단이 완료되었습니다",
                notification_type=PushNotificationType.DIAGNOSIS,
                priority=PushPriority.NORMAL
            )
        elif notification_type == 'payment':
            notification = mobile_push_service.create_notification(
                title="💳 결제 테스트",
                body="새로운 결제가 완료되었습니다",
                notification_type=PushNotificationType.PAYMENT,
                priority=PushPriority.NORMAL
            )
        else:
            notification = mobile_push_service.create_notification(
                title="📱 알림 테스트",
                body="푸시 알림이 정상적으로 작동합니다",
                notification_type=PushNotificationType.SYSTEM,
                priority=PushPriority.NORMAL
            )
        
        # 알림 전송
        success = mobile_push_service.send_notification(user_id, notification)
        
        return jsonify({
            'success': success,
            'message': '푸시 알림 테스트가 완료되었습니다' if success else '푸시 알림 테스트에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"푸시 알림 테스트 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/push/history', methods=['GET'])
def get_push_history():
    """푸시 알림 히스토리 조회"""
    try:
        user_id = request.args.get('user_id')
        limit = request.args.get('limit', 50, type=int)
        
        history = mobile_push_service.get_notification_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        logger.error(f"푸시 알림 히스토리 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 실시간 모니터링 ====================

@mobile_app_bp.route('/monitoring/status', methods=['GET'])
def get_monitoring_status():
    """실시간 모니터링 상태 조회"""
    try:
        status = real_time_monitoring_service.get_service_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        logger.error(f"모니터링 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/monitoring/data', methods=['GET'])
def get_monitoring_data():
    """실시간 모니터링 데이터 조회"""
    try:
        data_type = request.args.get('type', 'temperature')
        limit = request.args.get('limit', 100, type=int)
        
        # 최신 데이터 조회
        latest_data = real_time_monitoring_service.get_latest_data(data_type)
        
        if latest_data:
            return jsonify({
                'success': True,
                'data': {
                    'timestamp': latest_data.timestamp.isoformat(),
                    'data_type': latest_data.data_type.value,
                    'value': latest_data.value,
                    'unit': latest_data.unit,
                    'status': latest_data.status.value,
                    'store_id': latest_data.store_id,
                    'device_id': latest_data.device_id
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': '데이터를 찾을 수 없습니다'
            }), 404
            
    except Exception as e:
        logger.error(f"모니터링 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/monitoring/alerts', methods=['GET'])
def get_monitoring_alerts():
    """모니터링 알림 조회"""
    try:
        store_id = request.args.get('store_id')
        alerts = real_time_monitoring_service.get_active_alerts(store_id)
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': alert.id,
                    'store_id': alert.store_id,
                    'device_id': alert.device_id,
                    'alert_type': alert.alert_type,
                    'severity': alert.severity,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'resolved': alert.resolved
                }
                for alert in alerts
            ]
        })
        
    except Exception as e:
        logger.error(f"모니터링 알림 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 원격 제어 ====================

@mobile_app_bp.route('/control/devices', methods=['GET'])
def get_control_devices():
    """제어 가능한 장비 목록 조회"""
    try:
        devices = remote_control_service.get_all_devices()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'device_id': device.device_id,
                    'store_id': device.store_id,
                    'device_type': device.device_type,
                    'status': device.status.value,
                    'last_seen': device.last_seen.isoformat(),
                    'firmware_version': device.firmware_version,
                    'capabilities': device.capabilities,
                    'current_settings': device.current_settings,
                    'health_score': device.health_score
                }
                for device in devices
            ]
        })
        
    except Exception as e:
        logger.error(f"장비 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/control/command', methods=['POST'])
def execute_control_command():
    """원격 제어 명령 실행"""
    try:
        data = request.get_json()
        
        command = RemoteCommand(
            id=f"cmd_{int(datetime.now().timestamp() * 1000)}",
            command=ControlCommand(data.get('command')),
            device_id=data.get('device_id'),
            store_id=data.get('store_id'),
            parameters=data.get('parameters', {}),
            executed_by=data.get('executed_by', 'mobile_app')
        )
        
        success = remote_control_service.execute_command(command)
        
        return jsonify({
            'success': success,
            'message': '명령이 실행되었습니다' if success else '명령 실행에 실패했습니다',
            'command_id': command.id
        })
        
    except Exception as e:
        logger.error(f"원격 제어 명령 실행 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/control/command/<command_id>/status', methods=['GET'])
def get_command_status(command_id):
    """명령 실행 상태 조회"""
    try:
        status = remote_control_service.get_command_status(command_id)
        
        if status:
            return jsonify({
                'success': True,
                'data': status
            })
        else:
            return jsonify({
                'success': False,
                'error': '명령을 찾을 수 없습니다'
            }), 404
            
    except Exception as e:
        logger.error(f"명령 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/control/command/<command_id>/cancel', methods=['POST'])
def cancel_command(command_id):
    """명령 취소"""
    try:
        success = remote_control_service.cancel_command(command_id)
        
        return jsonify({
            'success': success,
            'message': '명령이 취소되었습니다' if success else '명령 취소에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"명령 취소 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 결제 관리 ====================

@mobile_app_bp.route('/payments', methods=['GET'])
def get_payments():
    """결제 내역 조회"""
    try:
        store_id = request.args.get('store_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        
        # 날짜 파싱
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        status_enum = PaymentStatus(status) if status else None
        
        transactions = mobile_payment_service.get_transactions(
            store_id=store_id,
            start_date=start_dt,
            end_date=end_dt,
            status=status_enum,
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': t.id,
                    'store_id': t.store_id,
                    'amount': t.amount,
                    'currency': t.currency,
                    'payment_method': t.payment_method.value,
                    'status': t.status.value,
                    'transaction_type': t.transaction_type.value,
                    'customer_id': t.customer_id,
                    'order_id': t.order_id,
                    'created_at': t.created_at.isoformat(),
                    'completed_at': t.completed_at.isoformat() if t.completed_at else None,
                    'error_message': t.error_message
                }
                for t in transactions
            ]
        })
        
    except Exception as e:
        logger.error(f"결제 내역 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/payments', methods=['POST'])
def create_payment():
    """결제 생성"""
    try:
        data = request.get_json()
        
        transaction = PaymentTransaction(
            id=f"pay_{int(datetime.now().timestamp() * 1000)}",
            store_id=data.get('store_id'),
            amount=data.get('amount'),
            currency=data.get('currency', 'KRW'),
            payment_method=PaymentMethod(data.get('payment_method', 'card')),
            customer_id=data.get('customer_id'),
            order_id=data.get('order_id'),
            metadata=data.get('metadata', {})
        )
        
        success = mobile_payment_service.process_payment(transaction)
        
        return jsonify({
            'success': success,
            'message': '결제가 처리되었습니다' if success else '결제 처리에 실패했습니다',
            'transaction_id': transaction.id
        })
        
    except Exception as e:
        logger.error(f"결제 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/payments/<transaction_id>/refund', methods=['POST'])
def refund_payment(transaction_id):
    """결제 환불"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        
        success = mobile_payment_service.refund_payment(transaction_id, amount)
        
        return jsonify({
            'success': success,
            'message': '환불이 처리되었습니다' if success else '환불 처리에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"결제 환불 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/payments/summary', methods=['GET'])
def get_payment_summary():
    """결제 요약 조회"""
    try:
        store_id = request.args.get('store_id')
        date = request.args.get('date')
        
        if not store_id:
            return jsonify({
                'success': False,
                'error': 'store_id가 필요합니다'
            }), 400
        
        date_obj = datetime.fromisoformat(date) if date else None
        summary = mobile_payment_service.get_payment_summary(store_id, date_obj)
        
        return jsonify({
            'success': True,
            'data': {
                'store_id': summary.store_id,
                'date': summary.date.isoformat(),
                'total_amount': summary.total_amount,
                'transaction_count': summary.transaction_count,
                'successful_count': summary.successful_count,
                'failed_count': summary.failed_count,
                'refund_count': summary.refund_count,
                'average_amount': summary.average_amount,
                'payment_methods': summary.payment_methods,
                'hourly_breakdown': summary.hourly_breakdown
            }
        })
        
    except Exception as e:
        logger.error(f"결제 요약 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/payments/analytics', methods=['GET'])
def get_payment_analytics():
    """결제 분석 데이터 조회"""
    try:
        store_id = request.args.get('store_id')
        days = request.args.get('days', 30, type=int)
        
        if not store_id:
            return jsonify({
                'success': False,
                'error': 'store_id가 필요합니다'
            }), 400
        
        analytics = mobile_payment_service.get_payment_analytics(store_id, days)
        
        return jsonify({
            'success': True,
            'data': analytics
        })
        
    except Exception as e:
        logger.error(f"결제 분석 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@mobile_app_bp.route('/payments/real-time', methods=['GET'])
def get_real_time_payment_data():
    """실시간 결제 데이터 조회"""
    try:
        data = mobile_payment_service.get_real_time_data()
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"실시간 결제 데이터 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 헬스 체크 ====================

@mobile_app_bp.route('/health', methods=['GET'])
def health_check():
    """모바일 앱 서비스 헬스 체크"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'services': {
                'push_notifications': mobile_push_service.get_service_status(),
                'offline_sync': offline_sync_service.get_sync_status(),
                'real_time_monitoring': real_time_monitoring_service.get_service_status(),
                'remote_control': remote_control_service.get_service_status(),
                'mobile_payment': mobile_payment_service.get_service_status()
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"헬스 체크 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
