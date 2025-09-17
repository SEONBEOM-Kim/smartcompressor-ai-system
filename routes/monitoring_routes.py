#!/usr/bin/env python3
"""
실시간 모니터링 라우트
24시간 무인 냉동고 관리 시스템 API
"""

from flask import Blueprint, jsonify, request
import logging
from services.realtime_monitoring import monitoring_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 모니터링 라우트 블루프린트 생성
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/monitoring')

@monitoring_bp.route('/start', methods=['POST'])
def start_monitoring():
    """모니터링 시작"""
    try:
        monitoring_service.start_monitoring()
        return jsonify({
            'success': True,
            'message': '24시간 모니터링 서비스가 시작되었습니다.'
        })
    except Exception as e:
        logger.error(f"모니터링 시작 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '모니터링 시작에 실패했습니다.'
        }), 500

@monitoring_bp.route('/stop', methods=['POST'])
def stop_monitoring():
    """모니터링 중지"""
    try:
        monitoring_service.stop_monitoring()
        return jsonify({
            'success': True,
            'message': '24시간 모니터링 서비스가 중지되었습니다.'
        })
    except Exception as e:
        logger.error(f"모니터링 중지 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '모니터링 중지에 실패했습니다.'
        }), 500

@monitoring_bp.route('/status', methods=['GET'])
def get_monitoring_status():
    """모니터링 상태 조회"""
    try:
        return jsonify({
            'success': True,
            'is_running': monitoring_service.is_running,
            'check_interval': monitoring_service.check_interval,
            'alert_threshold': monitoring_service.alert_threshold,
            'warning_threshold': monitoring_service.warning_threshold
        })
    except Exception as e:
        logger.error(f"모니터링 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '모니터링 상태 조회에 실패했습니다.'
        }), 500

@monitoring_bp.route('/stats', methods=['GET'])
def get_monitoring_stats():
    """모니터링 통계 조회"""
    try:
        hours = request.args.get('hours', 24, type=int)
        stats = monitoring_service.get_monitoring_stats(hours)
        
        return jsonify({
            'success': True,
            'stats': stats,
            'message': f'{hours}시간 모니터링 통계'
        })
    except Exception as e:
        logger.error(f"모니터링 통계 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '모니터링 통계 조회에 실패했습니다.'
        }), 500

@monitoring_bp.route('/alerts', methods=['GET'])
def get_recent_alerts():
    """최근 알림 조회"""
    try:
        limit = request.args.get('limit', 10, type=int)
        alerts = monitoring_service.get_recent_alerts(limit)
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'message': f'최근 {len(alerts)}개 알림'
        })
    except Exception as e:
        logger.error(f"알림 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '알림 조회에 실패했습니다.'
        }), 500
