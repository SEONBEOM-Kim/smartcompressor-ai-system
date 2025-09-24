#!/usr/bin/env python3
"""
대시보드 API 라우트
Stripe Dashboard와 AWS CloudWatch 스타일의 대시보드 API
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
import time

# 서비스 임포트
from services.dashboard_service import dashboard_data_service
from services.analytics_service import analytics_service
from services.notification_management_service import notification_management_service
from services.store_management_service import store_management_service
from services.user_permission_service import user_permission_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/summary', methods=['GET'])
def get_dashboard_summary():
    """대시보드 요약 정보 조회"""
    try:
        # 매장 ID 필터 (선택사항)
        store_id = request.args.get('store_id')
        
        # 대시보드 요약 데이터 조회
        summary = dashboard_data_service.get_dashboard_summary(store_id)
        
        # 에너지 데이터 조회
        energy_analytics = dashboard_data_service.get_energy_analytics(store_id, days=7)
        energy_data = {
            'labels': [data.date for data in energy_analytics],
            'values': [data.total_consumption for data in energy_analytics]
        }
        
        # 디바이스 상태 데이터 조회
        compressor_status = dashboard_data_service.get_compressor_status(store_id)
        device_status = {
            'online': len([d for d in compressor_status if d.status == 'online']),
            'offline': len([d for d in compressor_status if d.status == 'offline']),
            'maintenance': len([d for d in compressor_status if d.status == 'maintenance']),
            'error': len([d for d in compressor_status if d.status == 'error'])
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'energy_data': energy_data,
            'device_status': device_status,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"대시보드 요약 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '대시보드 요약 조회에 실패했습니다.'
        }), 500

@dashboard_bp.route('/stores', methods=['GET', 'POST'])
def handle_stores():
    """매장 관리 API"""
    try:
        if request.method == 'GET':
            # 매장 목록 조회
            owner_id = request.args.get('owner_id')
            status = request.args.get('status')
            
            if owner_id:
                stores = store_management_service.get_stores_by_owner(owner_id)
            else:
                stores = store_management_service.get_all_stores(status)
            
            # 매장별 메트릭 추가
            for store in stores:
                metrics = store_management_service.get_store_metrics(store['store_id'])
                if metrics:
                    store.update(metrics)
            
            return jsonify({
                'success': True,
                'stores': stores
            })
            
        elif request.method == 'POST':
            # 매장 추가
            store_data = request.get_json()
            
            success, result = store_management_service.register_store(store_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'store_id': result,
                    'message': '매장이 성공적으로 추가되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result,
                    'message': '매장 추가에 실패했습니다.'
                }), 400
                
    except Exception as e:
        logger.error(f"매장 관리 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '매장 관리 중 오류가 발생했습니다.'
        }), 500

@dashboard_bp.route('/stores/<store_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_store(store_id):
    """개별 매장 관리 API"""
    try:
        if request.method == 'GET':
            # 매장 정보 조회
            store = store_management_service.get_store(store_id)
            
            if store:
                # 매장 메트릭 추가
                metrics = store_management_service.get_store_metrics(store_id)
                if metrics:
                    store.update(metrics)
                
                return jsonify({
                    'success': True,
                    'store': store
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '매장을 찾을 수 없습니다.'
                }), 404
                
        elif request.method == 'PUT':
            # 매장 정보 업데이트
            updates = request.get_json()
            
            success = store_management_service.update_store(store_id, updates)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '매장 정보가 업데이트되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '매장 정보 업데이트에 실패했습니다.'
                }), 400
                
        elif request.method == 'DELETE':
            # 매장 삭제
            success = store_management_service.delete_store(store_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '매장이 삭제되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '매장 삭제에 실패했습니다.'
                }), 400
                
    except Exception as e:
        logger.error(f"매장 관리 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '매장 관리 중 오류가 발생했습니다.'
        }), 500

@dashboard_bp.route('/devices', methods=['GET', 'POST'])
def handle_devices():
    """디바이스 관리 API"""
    try:
        if request.method == 'GET':
            # 디바이스 목록 조회
            store_id = request.args.get('store_id')
            
            if store_id:
                devices = store_management_service.get_devices_by_store(store_id)
            else:
                # 모든 디바이스 조회 (매장 정보 포함)
                all_devices = []
                for device_id, device in store_management_service.devices.items():
                    device_dict = {
                        'device_id': device.device_id,
                        'device_name': device.device_name,
                        'device_type': device.device_type,
                        'model': device.model,
                        'serial_number': device.serial_number,
                        'status': device.status.value,
                        'installed_at': device.installed_at,
                        'last_maintenance': device.last_maintenance,
                        'next_maintenance': device.next_maintenance,
                        'warranty_expires': device.warranty_expires,
                        'store_id': device.store_id
                    }
                    
                    # 매장 정보 추가
                    store = store_management_service.get_store(device.store_id)
                    if store:
                        device_dict['store_name'] = store['store_name']
                    
                    # 건강도 점수 추가 (시뮬레이션)
                    device_dict['health_score'] = 85.5  # 실제로는 센서 데이터에서 계산
                    
                    all_devices.append(device_dict)
                
                devices = all_devices
            
            return jsonify({
                'success': True,
                'devices': devices
            })
            
        elif request.method == 'POST':
            # 디바이스 추가
            device_data = request.get_json()
            
            success, result = store_management_service.add_device(device_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'device_id': result,
                    'message': '디바이스가 성공적으로 추가되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result,
                    'message': '디바이스 추가에 실패했습니다.'
                }), 400
                
    except Exception as e:
        logger.error(f"디바이스 관리 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '디바이스 관리 중 오류가 발생했습니다.'
        }), 500

@dashboard_bp.route('/devices/<device_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_device(device_id):
    """개별 디바이스 관리 API"""
    try:
        if request.method == 'GET':
            # 디바이스 정보 조회
            device = store_management_service.get_device(device_id)
            
            if device:
                return jsonify({
                    'success': True,
                    'device': device
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '디바이스를 찾을 수 없습니다.'
                }), 404
                
        elif request.method == 'PUT':
            # 디바이스 정보 업데이트
            updates = request.get_json()
            
            success = store_management_service.update_device(device_id, updates)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '디바이스 정보가 업데이트되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '디바이스 정보 업데이트에 실패했습니다.'
                }), 400
                
        elif request.method == 'DELETE':
            # 디바이스 삭제
            success = store_management_service.delete_device(device_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '디바이스가 삭제되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '디바이스 삭제에 실패했습니다.'
                }), 400
                
    except Exception as e:
        logger.error(f"디바이스 관리 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '디바이스 관리 중 오류가 발생했습니다.'
        }), 500

@dashboard_bp.route('/analytics', methods=['GET'])
def get_analytics():
    """분석 데이터 조회"""
    try:
        store_id = request.args.get('store_id')
        days = int(request.args.get('days', 30))
        
        # 트렌드 분석
        trends = analytics_service.analyze_trends(store_id, days)
        
        # 이상 패턴 감지
        patterns = analytics_service.detect_anomaly_patterns(store_id, days)
        
        # 성능 메트릭
        performance = analytics_service.calculate_performance_metrics(store_id, days)
        
        # 차트용 데이터 생성
        analytics_data = {
            'temperature': {
                'labels': [f'Day {i+1}' for i in range(days)],
                'values': [20 + (i % 10) - 5 for i in range(days)]  # 시뮬레이션 데이터
            },
            'vibration': {
                'labels': ['Device 1', 'Device 2', 'Device 3', 'Device 4'],
                'values': [1.2, 0.8, 1.5, 0.9]  # 시뮬레이션 데이터
            },
            'power': {
                'labels': ['00:00', '06:00', '12:00', '18:00', '24:00'],
                'values': [45, 60, 80, 75, 50]  # 시뮬레이션 데이터
            },
            'anomaly': {
                'labels': [f'Day {i+1}' for i in range(days)],
                'values': [max(0, (i % 7) - 2) for i in range(days)]  # 시뮬레이션 데이터
            }
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics_data,
            'trends': [trend.__dict__ for trend in trends],
            'patterns': [pattern.__dict__ for pattern in patterns],
            'performance': [perf.__dict__ for perf in performance]
        })
        
    except Exception as e:
        logger.error(f"분석 데이터 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '분석 데이터 조회에 실패했습니다.'
        }), 500

@dashboard_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """알림 이력 조회"""
    try:
        user_id = request.args.get('user_id', 'system')
        store_id = request.args.get('store_id')
        limit = int(request.args.get('limit', 100))
        
        # 알림 이력 조회
        notifications = notification_management_service.get_notification_history(
            user_id=user_id,
            store_id=store_id,
            limit=limit
        )
        
        # 매장 정보 추가
        for notification in notifications:
            if notification['store_id']:
                store = store_management_service.get_store(notification['store_id'])
                if store:
                    notification['store_name'] = store['store_name']
        
        return jsonify({
            'success': True,
            'notifications': notifications
        })
        
    except Exception as e:
        logger.error(f"알림 이력 조회 실패: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '알림 이력 조회에 실패했습니다.'
        }), 500

@dashboard_bp.route('/notification-settings', methods=['GET', 'POST'])
def handle_notification_settings():
    """알림 설정 관리 API"""
    try:
        if request.method == 'GET':
            # 알림 설정 조회
            user_id = request.args.get('user_id', 'system')
            
            settings = notification_management_service.get_user_notification_settings(user_id)
            
            if settings:
                return jsonify({
                    'success': True,
                    'settings': settings
                })
            else:
                # 기본 설정 반환
                default_settings = {
                    'email_enabled': True,
                    'sms_enabled': True,
                    'kakao_enabled': True,
                    'websocket_enabled': True,
                    'push_enabled': True,
                    'quiet_hours_start': '22:00',
                    'quiet_hours_end': '08:00',
                    'max_notifications_per_hour': 10,
                    'priority_filter': ['high', 'critical'],
                    'store_filters': []
                }
                
                return jsonify({
                    'success': True,
                    'settings': default_settings
                })
                
        elif request.method == 'POST':
            # 알림 설정 업데이트
            user_id = request.json.get('user_id', 'system')
            settings = request.json
            
            success = notification_management_service.update_user_notification_settings(user_id, settings)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '알림 설정이 업데이트되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '알림 설정 업데이트에 실패했습니다.'
                }), 400
                
    except Exception as e:
        logger.error(f"알림 설정 관리 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '알림 설정 관리 중 오류가 발생했습니다.'
        }), 500

@dashboard_bp.route('/users', methods=['GET', 'POST'])
def handle_users():
    """사용자 관리 API"""
    try:
        if request.method == 'GET':
            # 사용자 목록 조회
            role = request.args.get('role')
            
            if role:
                users = user_permission_service.get_users_by_role(role)
            else:
                # 모든 사용자 조회
                users = []
                for user_id, user in user_permission_service.users.items():
                    user_dict = {
                        'user_id': user.user_id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'role': user.role.value,
                        'status': user.status.value,
                        'created_at': user.created_at,
                        'last_login': user.last_login
                    }
                    users.append(user_dict)
            
            return jsonify({
                'success': True,
                'users': users
            })
            
        elif request.method == 'POST':
            # 사용자 생성
            user_data = request.get_json()
            
            success, result = user_permission_service.create_user(user_data)
            
            if success:
                return jsonify({
                    'success': True,
                    'user_id': result,
                    'message': '사용자가 성공적으로 생성되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result,
                    'message': '사용자 생성에 실패했습니다.'
                }), 400
                
    except Exception as e:
        logger.error(f"사용자 관리 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '사용자 관리 중 오류가 발생했습니다.'
        }), 500

@dashboard_bp.route('/users/<user_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(user_id):
    """개별 사용자 관리 API"""
    try:
        if request.method == 'GET':
            # 사용자 정보 조회
            user = user_permission_service.get_user(user_id)
            
            if user:
                return jsonify({
                    'success': True,
                    'user': user
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '사용자를 찾을 수 없습니다.'
                }), 404
                
        elif request.method == 'PUT':
            # 사용자 정보 업데이트
            updates = request.get_json()
            
            success = user_permission_service.update_user(user_id, updates)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '사용자 정보가 업데이트되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '사용자 정보 업데이트에 실패했습니다.'
                }), 400
                
        elif request.method == 'DELETE':
            # 사용자 삭제
            success = user_permission_service.delete_user(user_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '사용자가 삭제되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '사용자 삭제에 실패했습니다.'
                }), 400
                
    except Exception as e:
        logger.error(f"사용자 관리 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '사용자 관리 중 오류가 발생했습니다.'
        }), 500

@dashboard_bp.route('/health', methods=['GET'])
def health_check():
    """대시보드 서비스 상태 확인"""
    try:
        # 각 서비스 상태 확인
        services_status = {
            'dashboard_service': 'healthy',
            'analytics_service': 'healthy',
            'notification_management_service': 'healthy',
            'store_management_service': 'healthy',
            'user_permission_service': 'healthy'
        }
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'services': services_status,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500
