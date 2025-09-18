#!/usr/bin/env python3
"""
ESP32 통합 API 라우트
ESP32 디바이스와의 통신을 위한 최적화된 API를 제공합니다.
"""

from flask import Blueprint, request, jsonify, current_app
import os
import time
import logging
import json
from services.esp32_optimizer import esp32_optimizer
from services.notification_service import notification_service
from services.ai_service import ensemble_ai_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ESP32 라우트 블루프린트 생성
esp32_bp = Blueprint('esp32', __name__, url_prefix='/api/esp32')

@esp32_bp.route('/register', methods=['POST'])
def register_device():
    """ESP32 디바이스 등록"""
    try:
        data = request.get_json()
        
        device_id = data.get('device_id')
        ip_address = request.remote_addr
        sample_rate = data.get('sample_rate', 16000)
        
        if not device_id:
            return jsonify({
                'success': False,
                'message': 'device_id가 필요합니다.'
            }), 400
        
        # 디바이스 등록
        success = esp32_optimizer.register_device(device_id, ip_address, sample_rate)
        
        if success:
            return jsonify({
                'success': True,
                'message': '디바이스 등록 성공',
                'device_id': device_id,
                'server_time': time.time()
            })
        else:
            return jsonify({
                'success': False,
                'message': '디바이스 등록 실패'
            }), 500
            
    except Exception as e:
        logger.error(f"디바이스 등록 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'디바이스 등록 오류: {str(e)}'
        }), 500

@esp32_bp.route('/audio/upload', methods=['POST'])
def upload_audio():
    """ESP32에서 오디오 데이터 업로드"""
    try:
        # 헤더에서 디바이스 정보 추출
        device_id = request.headers.get('X-Device-ID', 'unknown')
        sample_rate = int(request.headers.get('X-Sample-Rate', '16000'))
        bits_per_sample = int(request.headers.get('X-Bits-Per-Sample', '16'))
        
        # 오디오 데이터 수신
        audio_data = request.data
        
        if not audio_data:
            return jsonify({
                'success': False,
                'message': '오디오 데이터가 없습니다.'
            }), 400
        
        # 우선순위 결정 (디바이스 상태에 따라)
        priority = 1  # 기본 우선순위
        if request.headers.get('X-Priority') == 'high':
            priority = 3
        elif request.headers.get('X-Priority') == 'urgent':
            priority = 4
        
        # 오디오 데이터를 최적화 서비스에 추가
        esp32_optimizer.add_audio_chunk(device_id, audio_data, sample_rate, priority)
        
        # 즉시 응답 (비동기 처리)
        return jsonify({
            'success': True,
            'message': '오디오 데이터 수신 완료',
            'device_id': device_id,
            'timestamp': time.time(),
            'processing_status': 'queued'
        })
        
    except Exception as e:
        logger.error(f"오디오 업로드 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'오디오 업로드 오류: {str(e)}'
        }), 500

@esp32_bp.route('/status', methods=['GET'])
def get_device_status():
    """디바이스 상태 조회"""
    try:
        device_id = request.args.get('device_id')
        
        if device_id:
            # 특정 디바이스 상태
            status = esp32_optimizer.get_device_status(device_id)
            if status:
                return jsonify({
                    'success': True,
                    'device_status': status
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '디바이스를 찾을 수 없습니다.'
                }), 404
        else:
            # 모든 디바이스 상태
            devices = {}
            for device_id in esp32_optimizer.devices:
                devices[device_id] = esp32_optimizer.get_device_status(device_id)
            
            return jsonify({
                'success': True,
                'devices': devices,
                'total_devices': len(devices)
            })
            
    except Exception as e:
        logger.error(f"디바이스 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'상태 조회 오류: {str(e)}'
        }), 500

@esp32_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """성능 메트릭 조회"""
    try:
        metrics = esp32_optimizer.get_metrics()
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"메트릭 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'메트릭 조회 오류: {str(e)}'
        }), 500

@esp32_bp.route('/alert', methods=['POST'])
def send_alert():
    """ESP32에서 직접 알림 전송"""
    try:
        data = request.get_json()
        
        device_id = data.get('device_id')
        alert_type = data.get('alert_type', 'device_alert')
        severity = data.get('severity', 'medium')
        message = data.get('message', '디바이스에서 알림이 발생했습니다.')
        alert_data = data.get('data', {})
        
        if not device_id:
            return jsonify({
                'success': False,
                'message': 'device_id가 필요합니다.'
            }), 400
        
        # 알림 전송
        success = notification_service.send_alert(
            device_id=device_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            data=alert_data
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '알림 전송 성공'
            })
        else:
            return jsonify({
                'success': False,
                'message': '알림 전송 실패'
            }), 500
            
    except Exception as e:
        logger.error(f"알림 전송 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 전송 오류: {str(e)}'
        }), 500

@esp32_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """알림 이력 조회"""
    try:
        device_id = request.args.get('device_id')
        limit = int(request.args.get('limit', 100))
        
        alerts = notification_service.get_alert_history(device_id, limit)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'total_count': len(alerts)
        })
        
    except Exception as e:
        logger.error(f"알림 이력 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 이력 조회 오류: {str(e)}'
        }), 500

@esp32_bp.route('/config', methods=['GET'])
def get_device_config():
    """ESP32 디바이스 설정 조회"""
    try:
        device_id = request.args.get('device_id')
        
        if not device_id:
            return jsonify({
                'success': False,
                'message': 'device_id가 필요합니다.'
            }), 400
        
        # 디바이스별 설정 반환
        config = {
            'upload_interval': 30,  # 30초마다 업로드
            'sample_rate': 16000,
            'buffer_size': 1024,
            'max_retries': 3,
            'timeout': 10,
            'server_url': request.url_root + 'api/esp32/audio/upload',
            'status_url': request.url_root + 'api/esp32/status',
            'alert_url': request.url_root + 'api/esp32/alert'
        }
        
        return jsonify({
            'success': True,
            'config': config,
            'device_id': device_id
        })
        
    except Exception as e:
        logger.error(f"설정 조회 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'설정 조회 오류: {str(e)}'
        }), 500

@esp32_bp.route('/health', methods=['GET'])
def health_check():
    """ESP32 API 헬스 체크"""
    try:
        # 시스템 상태 확인
        metrics = esp32_optimizer.get_metrics()
        
        health_status = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '1.0.0',
            'metrics': {
                'active_devices': metrics.get('active_devices', 0),
                'queue_size': metrics.get('queue_size', 0),
                'processed_chunks': metrics.get('processed_chunks', 0),
                'failed_chunks': metrics.get('failed_chunks', 0)
            }
        }
        
        # 시스템 상태 판단
        if metrics.get('failed_chunks', 0) > metrics.get('processed_chunks', 1) * 0.1:
            health_status['status'] = 'degraded'
        elif metrics.get('queue_size', 0) > 100:
            health_status['status'] = 'overloaded'
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"헬스 체크 오류: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500
