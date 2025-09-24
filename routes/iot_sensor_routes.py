#!/usr/bin/env python3
"""
IoT 센서 시스템 API 라우트
Tesla와 Nest 스타일의 통합 센서 데이터 API
"""

from flask import Blueprint, request, jsonify, Response
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 서비스 임포트
from services.sensor_data_service import sensor_data_service
from services.realtime_streaming_service import realtime_streaming_service
from services.sensor_database_service import sensor_database_service
from services.sensor_monitoring_service import sensor_monitoring_service
from services.firmware_ota_service import firmware_ota_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
iot_sensor_bp = Blueprint('iot_sensor', __name__, url_prefix='/api/iot')

@iot_sensor_bp.route('/sensors/data', methods=['POST'])
def receive_sensor_data():
    """센서 데이터 수신 (ESP32에서 전송)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # 필수 필드 검증
        required_fields = ['device_id', 'timestamp', 'temperature', 'vibration', 'power_consumption', 'audio_level']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 센서 데이터 처리
        sensor_reading = {
            'device_id': data['device_id'],
            'timestamp': data['timestamp'],
            'temperature': data['temperature'],
            'vibration_x': data['vibration']['x'],
            'vibration_y': data['vibration']['y'],
            'vibration_z': data['vibration']['z'],
            'power_consumption': data['power_consumption'],
            'audio_level': data['audio_level'],
            'sensor_quality': data.get('sensor_quality', 1.0)
        }
        
        # 데이터베이스에 저장
        sensor_database_service.add_sensor_reading(sensor_reading)
        
        # 모니터링 서비스에 전달
        sensor_monitoring_service.update_sensor_data(data['device_id'], data)
        
        # 실시간 스트리밍에 전달
        realtime_streaming_service.add_sensor_data(data['device_id'], data)
        
        return jsonify({
            'success': True,
            'message': 'Sensor data received',
            'timestamp': time.time()
        })
        
    except Exception as e:
        logger.error(f"Sensor data reception error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/sensors/data/<device_id>', methods=['GET'])
def get_sensor_data(device_id: str):
    """센서 데이터 조회"""
    try:
        # 쿼리 파라미터
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 1000, type=int)
        
        # 시간 범위 계산
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        # 데이터 조회
        data = sensor_database_service.get_sensor_data(device_id, start_time, end_time, limit)
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'data': data,
            'count': len(data),
            'time_range': {
                'start': start_time,
                'end': end_time,
                'hours': hours
            }
        })
        
    except Exception as e:
        logger.error(f"Sensor data retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/sensors/health/<device_id>', methods=['GET'])
def get_device_health(device_id: str):
    """디바이스 건강 상태 조회"""
    try:
        health = sensor_monitoring_service.get_device_health(device_id)
        
        if not health:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'health': {
                'status': health.status.value,
                'last_seen': health.last_seen,
                'uptime': health.uptime,
                'data_quality': health.data_quality,
                'anomaly_count': health.anomaly_count,
                'temperature_status': health.temperature_status.value,
                'vibration_status': health.vibration_status.value,
                'power_status': health.power_status.value,
                'audio_status': health.audio_status.value,
                'overall_health': health.overall_health
            }
        })
        
    except Exception as e:
        logger.error(f"Device health retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/sensors/health', methods=['GET'])
def get_all_device_health():
    """모든 디바이스 건강 상태 조회"""
    try:
        all_health = sensor_monitoring_service.get_all_device_health()
        
        health_data = {}
        for device_id, health in all_health.items():
            health_data[device_id] = {
                'status': health.status.value,
                'last_seen': health.last_seen,
                'uptime': health.uptime,
                'data_quality': health.data_quality,
                'anomaly_count': health.anomaly_count,
                'temperature_status': health.temperature_status.value,
                'vibration_status': health.vibration_status.value,
                'power_status': health.power_status.value,
                'audio_status': health.audio_status.value,
                'overall_health': health.overall_health
            }
        
        return jsonify({
            'success': True,
            'devices': health_data,
            'count': len(health_data)
        })
        
    except Exception as e:
        logger.error(f"All device health retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/sensors/anomalies', methods=['GET'])
def get_anomalies():
    """이상 감지 결과 조회"""
    try:
        # 쿼리 파라미터
        device_id = request.args.get('device_id')
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        # 시간 범위 계산
        end_time = time.time()
        start_time = end_time - (hours * 3600)
        
        # 데이터 조회
        anomalies = sensor_database_service.get_anomalies(device_id, start_time, end_time, limit)
        
        return jsonify({
            'success': True,
            'anomalies': anomalies,
            'count': len(anomalies),
            'filters': {
                'device_id': device_id,
                'hours': hours,
                'limit': limit
            }
        })
        
    except Exception as e:
        logger.error(f"Anomalies retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/sensors/statistics/<device_id>', methods=['GET'])
def get_device_statistics(device_id: str):
    """디바이스 통계 조회"""
    try:
        # 쿼리 파라미터
        date = request.args.get('date')
        
        # 통계 조회
        stats = sensor_database_service.get_statistics(device_id, date)
        
        if not stats:
            return jsonify({
                'success': False,
                'error': 'No statistics found'
            }), 404
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Device statistics retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/sensors/status', methods=['GET'])
def get_sensor_system_status():
    """센서 시스템 상태 조회"""
    try:
        # 각 서비스 상태 조회
        monitoring_status = sensor_monitoring_service.get_monitoring_status()
        database_status = sensor_database_service.get_database_status()
        streaming_status = realtime_streaming_service.get_status()
        
        return jsonify({
            'success': True,
            'system_status': {
                'monitoring': monitoring_status,
                'database': database_status,
                'streaming': streaming_status,
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        logger.error(f"Sensor system status retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/firmware/versions', methods=['GET'])
def get_firmware_versions():
    """펌웨어 버전 조회"""
    try:
        device_id = request.args.get('device_id')
        versions = firmware_ota_service.get_available_versions(device_id)
        
        return jsonify({
            'success': True,
            'versions': versions,
            'count': len(versions)
        })
        
    except Exception as e:
        logger.error(f"Firmware versions retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/firmware/update', methods=['POST'])
def start_firmware_update():
    """펌웨어 업데이트 시작"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        device_id = data.get('device_id')
        target_version = data.get('target_version')
        current_version = data.get('current_version')
        
        if not device_id or not target_version:
            return jsonify({'error': 'device_id and target_version are required'}), 400
        
        # 업데이트 시작
        success = firmware_ota_service.start_update(device_id, target_version, current_version)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Firmware update started',
                'device_id': device_id,
                'target_version': target_version
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start firmware update'
            }), 400
        
    except Exception as e:
        logger.error(f"Firmware update start error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/firmware/update/<device_id>', methods=['GET'])
def get_firmware_update_status(device_id: str):
    """펌웨어 업데이트 상태 조회"""
    try:
        status = firmware_ota_service.get_update_status(device_id)
        
        if not status:
            return jsonify({
                'success': False,
                'error': 'No update found for device'
            }), 404
        
        return jsonify({
            'success': True,
            'device_id': device_id,
            'update_status': status
        })
        
    except Exception as e:
        logger.error(f"Firmware update status retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/firmware/update/<device_id>', methods=['DELETE'])
def cancel_firmware_update(device_id: str):
    """펌웨어 업데이트 취소"""
    try:
        success = firmware_ota_service.cancel_update(device_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Firmware update cancelled',
                'device_id': device_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to cancel firmware update'
            }), 400
        
    except Exception as e:
        logger.error(f"Firmware update cancellation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/firmware/rollback', methods=['POST'])
def rollback_firmware():
    """펌웨어 롤백"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        device_id = data.get('device_id')
        target_version = data.get('target_version')
        
        if not device_id or not target_version:
            return jsonify({'error': 'device_id and target_version are required'}), 400
        
        # 롤백 시작
        success = firmware_ota_service.rollback_firmware(device_id, target_version)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Firmware rollback started',
                'device_id': device_id,
                'target_version': target_version
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start firmware rollback'
            }), 400
        
    except Exception as e:
        logger.error(f"Firmware rollback error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/firmware/status', methods=['GET'])
def get_firmware_service_status():
    """펌웨어 서비스 상태 조회"""
    try:
        status = firmware_ota_service.get_service_status()
        
        return jsonify({
            'success': True,
            'firmware_service': status
        })
        
    except Exception as e:
        logger.error(f"Firmware service status retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/streaming/status', methods=['GET'])
def get_streaming_status():
    """실시간 스트리밍 상태 조회"""
    try:
        status = realtime_streaming_service.get_status()
        
        return jsonify({
            'success': True,
            'streaming_service': status
        })
        
    except Exception as e:
        logger.error(f"Streaming status retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/devices', methods=['GET'])
def get_devices():
    """디바이스 목록 조회"""
    try:
        devices = sensor_database_service.get_device_status()
        
        return jsonify({
            'success': True,
            'devices': devices
        })
        
    except Exception as e:
        logger.error(f"Devices retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@iot_sensor_bp.route('/cleanup', methods=['POST'])
def cleanup_old_data():
    """오래된 데이터 정리"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        
        # 데이터베이스 정리
        sensor_database_service.cleanup_old_data(days)
        
        # 펌웨어 업데이트 정리
        firmware_ota_service.cleanup_completed_updates(days)
        
        return jsonify({
            'success': True,
            'message': f'Old data cleaned up (older than {days} days)'
        })
        
    except Exception as e:
        logger.error(f"Data cleanup error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
