#!/usr/bin/env python3
"""
분석 API 라우트
Google Analytics와 Mixpanel을 벤치마킹한 매장 운영 데이터 분석 API
"""

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta
from services.advanced_analytics_service import advanced_analytics_service
from services.predictive_maintenance_service import predictive_maintenance_service, MaintenanceRecord, MaintenanceType, EquipmentStatus
from services.ab_testing_service import ab_testing_service, ABTest, TestStatus, VariantType, MetricType
from services.automated_reporting_service import automated_reporting_service, ReportConfig, ReportType, ReportFormat

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 블루프린트 생성
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

# ==================== 매장 성능 분석 ====================

@analytics_bp.route('/performance/<store_id>', methods=['GET'])
def get_store_performance(store_id):
    """매장별 성능 지표 대시보드"""
    try:
        days = request.args.get('days', 30, type=int)
        
        result = advanced_analytics_service.get_store_performance_dashboard(store_id, days)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"매장 성능 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/efficiency/<store_id>', methods=['GET'])
def analyze_compressor_efficiency(store_id):
    """압축기 효율성 분석"""
    try:
        days = request.args.get('days', 30, type=int)
        
        result = advanced_analytics_service.analyze_compressor_efficiency(store_id, days)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"압축기 효율성 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/power-optimization/<store_id>', methods=['GET'])
def analyze_power_optimization(store_id):
    """전력 사용량 최적화 분석"""
    try:
        days = request.args.get('days', 30, type=int)
        
        result = advanced_analytics_service.analyze_power_optimization(store_id, days)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"전력 최적화 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 이벤트 추적 ====================

@analytics_bp.route('/track-event', methods=['POST'])
def track_event():
    """이벤트 추적 (Mixpanel 스타일)"""
    try:
        data = request.get_json()
        
        event_name = data.get('event_name')
        store_id = data.get('store_id')
        user_id = data.get('user_id')
        properties = data.get('properties', {})
        
        if not event_name:
            return jsonify({
                'success': False,
                'error': 'event_name이 필요합니다'
            }), 400
        
        success = advanced_analytics_service.track_event(
            event_name=event_name,
            store_id=store_id,
            user_id=user_id,
            properties=properties
        )
        
        return jsonify({
            'success': success,
            'message': '이벤트가 추적되었습니다' if success else '이벤트 추적에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"이벤트 추적 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/store-metrics', methods=['POST'])
def store_metrics():
    """매장 지표 저장"""
    try:
        data = request.get_json()
        
        from services.advanced_analytics_service import StoreMetrics
        
        metrics = StoreMetrics(
            store_id=data.get('store_id'),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            revenue=data.get('revenue', 0),
            power_consumption=data.get('power_consumption', 0),
            compressor_efficiency=data.get('compressor_efficiency', 0),
            temperature=data.get('temperature', 0),
            customer_count=data.get('customer_count', 0),
            order_count=data.get('order_count', 0),
            maintenance_cost=data.get('maintenance_cost', 0),
            energy_cost=data.get('energy_cost', 0)
        )
        
        success = advanced_analytics_service.store_metrics(metrics)
        
        return jsonify({
            'success': success,
            'message': '매장 지표가 저장되었습니다' if success else '매장 지표 저장에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"매장 지표 저장 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 예측 유지보수 ====================

@analytics_bp.route('/maintenance/predict/<equipment_id>', methods=['GET'])
def predict_maintenance(equipment_id):
    """유지보수 예측"""
    try:
        days_ahead = request.args.get('days_ahead', 30, type=int)
        
        prediction = predictive_maintenance_service.predict_maintenance(equipment_id, days_ahead)
        
        return jsonify({
            'success': True,
            'data': {
                'equipment_id': prediction.equipment_id,
                'predicted_failure_date': prediction.predicted_failure_date.isoformat(),
                'confidence': prediction.confidence,
                'maintenance_type': prediction.maintenance_type.value,
                'recommended_actions': prediction.recommended_actions,
                'estimated_cost': prediction.estimated_cost,
                'priority': prediction.priority
            }
        })
        
    except Exception as e:
        logger.error(f"유지보수 예측 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/maintenance/schedule', methods=['GET'])
def get_maintenance_schedule():
    """유지보수 스케줄 조회"""
    try:
        store_id = request.args.get('store_id')
        days_ahead = request.args.get('days_ahead', 30, type=int)
        
        schedule = predictive_maintenance_service.get_maintenance_schedule(store_id, days_ahead)
        
        return jsonify({
            'success': True,
            'data': schedule
        })
        
    except Exception as e:
        logger.error(f"유지보수 스케줄 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/maintenance/record', methods=['POST'])
def record_maintenance():
    """유지보수 기록 저장"""
    try:
        data = request.get_json()
        
        record = MaintenanceRecord(
            equipment_id=data.get('equipment_id'),
            maintenance_type=MaintenanceType(data.get('maintenance_type', 'preventive')),
            description=data.get('description', ''),
            cost=data.get('cost', 0),
            duration_hours=data.get('duration_hours', 0),
            technician=data.get('technician', ''),
            timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
            status=EquipmentStatus(data.get('status', 'normal'))
        )
        
        success = predictive_maintenance_service.record_maintenance(record)
        
        return jsonify({
            'success': success,
            'message': '유지보수 기록이 저장되었습니다' if success else '유지보수 기록 저장에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"유지보수 기록 저장 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/maintenance/status', methods=['POST'])
def update_equipment_status():
    """장비 상태 업데이트"""
    try:
        data = request.get_json()
        
        success = predictive_maintenance_service.update_equipment_status(
            equipment_id=data.get('equipment_id'),
            status=EquipmentStatus(data.get('status', 'normal')),
            temperature=data.get('temperature'),
            vibration=data.get('vibration'),
            power_consumption=data.get('power_consumption'),
            efficiency=data.get('efficiency')
        )
        
        return jsonify({
            'success': success,
            'message': '장비 상태가 업데이트되었습니다' if success else '장비 상태 업데이트에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"장비 상태 업데이트 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/maintenance/costs', methods=['GET'])
def analyze_maintenance_costs():
    """유지보수 비용 분석"""
    try:
        store_id = request.args.get('store_id')
        months = request.args.get('months', 12, type=int)
        
        analysis = predictive_maintenance_service.analyze_maintenance_costs(store_id, months)
        
        if 'error' in analysis:
            return jsonify({
                'success': False,
                'error': analysis['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': analysis
        })
        
    except Exception as e:
        logger.error(f"유지보수 비용 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== A/B 테스트 ====================

@analytics_bp.route('/ab-tests', methods=['POST'])
def create_ab_test():
    """A/B 테스트 생성"""
    try:
        data = request.get_json()
        
        test = ABTest(
            test_id=data.get('test_id'),
            test_name=data.get('test_name'),
            description=data.get('description', ''),
            store_id=data.get('store_id'),
            start_date=datetime.fromisoformat(data.get('start_date', datetime.now().isoformat())),
            end_date=datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else None,
            status=TestStatus(data.get('status', 'draft')),
            variants=data.get('variants', []),
            primary_metric=MetricType(data.get('primary_metric', 'conversion')),
            secondary_metrics=[MetricType(m) for m in data.get('secondary_metrics', [])],
            target_sample_size=data.get('target_sample_size', 1000),
            confidence_level=data.get('confidence_level', 0.95),
            minimum_effect_size=data.get('minimum_effect_size', 0.1)
        )
        
        success = ab_testing_service.create_test(test)
        
        return jsonify({
            'success': success,
            'message': 'A/B 테스트가 생성되었습니다' if success else 'A/B 테스트 생성에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"A/B 테스트 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ab-tests/<test_id>/start', methods=['POST'])
def start_ab_test(test_id):
    """A/B 테스트 시작"""
    try:
        success = ab_testing_service.start_test(test_id)
        
        return jsonify({
            'success': success,
            'message': 'A/B 테스트가 시작되었습니다' if success else 'A/B 테스트 시작에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"A/B 테스트 시작 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ab-tests/<test_id>/stop', methods=['POST'])
def stop_ab_test(test_id):
    """A/B 테스트 중지"""
    try:
        success = ab_testing_service.stop_test(test_id)
        
        return jsonify({
            'success': success,
            'message': 'A/B 테스트가 중지되었습니다' if success else 'A/B 테스트 중지에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"A/B 테스트 중지 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ab-tests/<test_id>/assign', methods=['POST'])
def assign_user_to_variant(test_id):
    """사용자를 변형에 할당"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id가 필요합니다'
            }), 400
        
        variant = ab_testing_service.assign_user_to_variant(test_id, user_id)
        
        return jsonify({
            'success': True,
            'variant': variant
        })
        
    except Exception as e:
        logger.error(f"사용자 할당 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ab-tests/<test_id>/track', methods=['POST'])
def track_ab_test_event(test_id):
    """A/B 테스트 이벤트 추적"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id')
        event_name = data.get('event_name')
        event_value = data.get('event_value', 1.0)
        
        if not user_id or not event_name:
            return jsonify({
                'success': False,
                'error': 'user_id와 event_name이 필요합니다'
            }), 400
        
        success = ab_testing_service.track_event(test_id, user_id, event_name, event_value)
        
        return jsonify({
            'success': success,
            'message': '이벤트가 추적되었습니다' if success else '이벤트 추적에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"A/B 테스트 이벤트 추적 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ab-tests/<test_id>/results', methods=['GET'])
def get_ab_test_results(test_id):
    """A/B 테스트 결과 조회"""
    try:
        results = ab_testing_service.get_test_results(test_id)
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'variant': r.variant,
                    'sample_size': r.sample_size,
                    'conversion_rate': r.conversion_rate,
                    'revenue_per_user': r.revenue_per_user,
                    'confidence_interval': r.confidence_interval,
                    'p_value': r.p_value,
                    'is_significant': r.is_significant,
                    'effect_size': r.effect_size,
                    'power': r.power
                }
                for r in results
            ]
        })
        
    except Exception as e:
        logger.error(f"A/B 테스트 결과 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ab-tests/<test_id>/calculate', methods=['POST'])
def calculate_ab_test_results(test_id):
    """A/B 테스트 결과 계산"""
    try:
        results = ab_testing_service.calculate_test_results(test_id)
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'variant': r.variant,
                    'sample_size': r.sample_size,
                    'conversion_rate': r.conversion_rate,
                    'revenue_per_user': r.revenue_per_user,
                    'confidence_interval': r.confidence_interval,
                    'p_value': r.p_value,
                    'is_significant': r.is_significant,
                    'effect_size': r.effect_size,
                    'power': r.power
                }
                for r in results
            ]
        })
        
    except Exception as e:
        logger.error(f"A/B 테스트 결과 계산 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ab-tests/active', methods=['GET'])
def get_active_ab_tests():
    """활성 A/B 테스트 목록 조회"""
    try:
        tests = ab_testing_service.get_active_tests()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'test_id': t.test_id,
                    'test_name': t.test_name,
                    'description': t.description,
                    'store_id': t.store_id,
                    'status': t.status.value,
                    'start_date': t.start_date.isoformat(),
                    'end_date': t.end_date.isoformat() if t.end_date else None,
                    'primary_metric': t.primary_metric.value
                }
                for t in tests
            ]
        })
        
    except Exception as e:
        logger.error(f"활성 A/B 테스트 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ab-tests/<test_id>/summary', methods=['GET'])
def get_ab_test_summary(test_id):
    """A/B 테스트 요약 정보 조회"""
    try:
        summary = ab_testing_service.get_test_summary(test_id)
        
        if 'error' in summary:
            return jsonify({
                'success': False,
                'error': summary['error']
            }), 400
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"A/B 테스트 요약 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 자동 리포트 ====================

@analytics_bp.route('/reports/config', methods=['POST'])
def create_report_config():
    """리포트 설정 생성"""
    try:
        data = request.get_json()
        
        config = ReportConfig(
            report_id=data.get('report_id'),
            report_name=data.get('report_name'),
            report_type=ReportType(data.get('report_type', 'daily')),
            store_ids=data.get('store_ids', []),
            metrics=data.get('metrics', []),
            recipients=data.get('recipients', []),
            schedule=data.get('schedule', 'daily'),
            format=ReportFormat(data.get('format', 'html')),
            is_active=data.get('is_active', True)
        )
        
        success = automated_reporting_service.create_report_config(config)
        
        return jsonify({
            'success': success,
            'message': '리포트 설정이 생성되었습니다' if success else '리포트 설정 생성에 실패했습니다'
        })
        
    except Exception as e:
        logger.error(f"리포트 설정 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/reports/<report_id>/generate', methods=['POST'])
def generate_report(report_id):
    """리포트 생성"""
    try:
        report_data = automated_reporting_service.generate_report(report_id)
        
        if not report_data:
            return jsonify({
                'success': False,
                'error': '리포트 생성에 실패했습니다'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'report_id': report_data.report_id,
                'generated_at': report_data.generated_at.isoformat(),
                'insights': report_data.insights,
                'recommendations': report_data.recommendations
            }
        })
        
    except Exception as e:
        logger.error(f"리포트 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/reports/scheduler/start', methods=['POST'])
def start_report_scheduler():
    """리포트 스케줄러 시작"""
    try:
        automated_reporting_service.start_scheduler()
        
        return jsonify({
            'success': True,
            'message': '리포트 스케줄러가 시작되었습니다'
        })
        
    except Exception as e:
        logger.error(f"리포트 스케줄러 시작 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/reports/scheduler/stop', methods=['POST'])
def stop_report_scheduler():
    """리포트 스케줄러 중지"""
    try:
        automated_reporting_service.stop_scheduler()
        
        return jsonify({
            'success': True,
            'message': '리포트 스케줄러가 중지되었습니다'
        })
        
    except Exception as e:
        logger.error(f"리포트 스케줄러 중지 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== 헬스 체크 ====================

@analytics_bp.route('/health', methods=['GET'])
def health_check():
    """분석 서비스 헬스 체크"""
    try:
        return jsonify({
            'success': True,
            'status': 'healthy',
            'services': {
                'advanced_analytics': 'active',
                'predictive_maintenance': 'active',
                'ab_testing': 'active',
                'automated_reporting': 'active'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"헬스 체크 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500