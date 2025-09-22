#!/usr/bin/env python3
"""
성능 모니터링 및 알림 시스템
AWS CloudWatch를 벤치마킹한 성능 모니터링 시스템
"""

import asyncio
import json
import logging
import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import statistics
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """메트릭 타입"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    CONCURRENT_USERS = "concurrent_users"
    DATABASE_CONNECTIONS = "database_connections"

class AlertLevel(Enum):
    """알림 레벨"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class PerformanceStatus(Enum):
    """성능 상태"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"

@dataclass
class PerformanceMetric:
    """성능 메트릭 클래스"""
    id: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    service_name: str
    instance_id: str = "default"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PerformanceAlert:
    """성능 알림 클래스"""
    id: str
    metric_type: MetricType
    alert_level: AlertLevel
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime
    service_name: str
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PerformanceReport:
    """성능 리포트 클래스"""
    id: str
    report_type: str
    start_time: datetime
    end_time: datetime
    service_name: str
    overall_status: PerformanceStatus
    metrics_summary: Dict[str, Any]
    alerts_summary: Dict[str, Any]
    recommendations: List[str]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class PerformanceMonitoringService:
    """성능 모니터링 서비스"""
    
    def __init__(self):
        self.metrics: Dict[str, deque] = {}
        self.active_alerts: Dict[str, PerformanceAlert] = {}
        self.performance_reports: List[PerformanceReport] = []
        self.monitoring_callbacks: List[Callable] = []
        
        # 모니터링 설정
        self.monitoring_interval = 30  # 30초
        self.metric_retention_hours = 24  # 24시간
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # 임계값 설정
        self.thresholds = {
            MetricType.CPU_USAGE: {
                'warning': 70.0,
                'error': 85.0,
                'critical': 95.0
            },
            MetricType.MEMORY_USAGE: {
                'warning': 80.0,
                'error': 90.0,
                'critical': 95.0
            },
            MetricType.DISK_USAGE: {
                'warning': 85.0,
                'error': 90.0,
                'critical': 95.0
            },
            MetricType.RESPONSE_TIME: {
                'warning': 2000.0,  # 2초
                'error': 5000.0,    # 5초
                'critical': 10000.0 # 10초
            },
            MetricType.ERROR_RATE: {
                'warning': 5.0,     # 5%
                'error': 10.0,      # 10%
                'critical': 20.0    # 20%
            },
            MetricType.REQUEST_RATE: {
                'warning': 1000.0,  # 1000 req/min
                'error': 2000.0,    # 2000 req/min
                'critical': 5000.0  # 5000 req/min
            }
        }
        
        # 모니터링할 서비스들
        self.monitored_services = [
            'flask_app',
            'database',
            'redis',
            'nginx',
            'ai_service',
            'payment_service'
        ]
        
        # 메트릭 히스토리 초기화
        for service in self.monitored_services:
            self.metrics[service] = deque(maxlen=2880)  # 24시간 * 30초 간격
        
        # 모니터링 시작
        self._start_monitoring()
    
    def _start_monitoring(self):
        """모니터링 시작"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        logger.info("성능 모니터링 시작")
    
    def _monitoring_worker(self):
        """모니터링 워커"""
        while self.is_monitoring:
            try:
                for service in self.monitored_services:
                    self._collect_service_metrics(service)
                
                # 알림 확인
                self._check_performance_alerts()
                
                # 오래된 데이터 정리
                self._cleanup_old_metrics()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"성능 모니터링 워커 오류: {e}")
                time.sleep(60)
    
    def _collect_service_metrics(self, service_name: str):
        """서비스 메트릭 수집"""
        try:
            current_time = datetime.now()
            
            if service_name == 'flask_app':
                self._collect_flask_metrics(service_name, current_time)
            elif service_name == 'database':
                self._collect_database_metrics(service_name, current_time)
            elif service_name == 'redis':
                self._collect_redis_metrics(service_name, current_time)
            elif service_name == 'nginx':
                self._collect_nginx_metrics(service_name, current_time)
            else:
                self._collect_generic_metrics(service_name, current_time)
                
        except Exception as e:
            logger.error(f"서비스 메트릭 수집 오류 ({service_name}): {e}")
    
    def _collect_flask_metrics(self, service_name: str, timestamp: datetime):
        """Flask 앱 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_usage = psutil.cpu_percent(interval=1)
            self._add_metric(service_name, MetricType.CPU_USAGE, cpu_usage, '%', timestamp)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            self._add_metric(service_name, MetricType.MEMORY_USAGE, memory_usage, '%', timestamp)
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            self._add_metric(service_name, MetricType.DISK_USAGE, disk_usage, '%', timestamp)
            
            # 네트워크 I/O
            network = psutil.net_io_counters()
            network_io = network.bytes_sent + network.bytes_recv
            self._add_metric(service_name, MetricType.NETWORK_IO, network_io, 'bytes', timestamp)
            
            # 응답 시간 (시뮬레이션)
            response_time = self._measure_response_time('http://localhost:8000/health')
            self._add_metric(service_name, MetricType.RESPONSE_TIME, response_time, 'ms', timestamp)
            
            # 요청률 (시뮬레이션)
            request_rate = self._calculate_request_rate(service_name)
            self._add_metric(service_name, MetricType.REQUEST_RATE, request_rate, 'req/min', timestamp)
            
        except Exception as e:
            logger.error(f"Flask 메트릭 수집 오류: {e}")
    
    def _collect_database_metrics(self, service_name: str, timestamp: datetime):
        """데이터베이스 메트릭 수집"""
        try:
            # 데이터베이스 파일 크기
            db_file = 'instance/smartcompressor.db'
            if os.path.exists(db_file):
                file_size = os.path.getsize(db_file)
                self._add_metric(service_name, MetricType.DISK_USAGE, file_size, 'bytes', timestamp)
            
            # 연결 수 (시뮬레이션)
            connections = self._get_database_connections()
            self._add_metric(service_name, MetricType.DATABASE_CONNECTIONS, connections, 'count', timestamp)
            
        except Exception as e:
            logger.error(f"데이터베이스 메트릭 수집 오류: {e}")
    
    def _collect_redis_metrics(self, service_name: str, timestamp: datetime):
        """Redis 메트릭 수집"""
        try:
            # Redis 프로세스 확인
            redis_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'redis' in proc.info['name'].lower():
                        redis_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            process_count = len(redis_processes)
            self._add_metric(service_name, MetricType.CONCURRENT_USERS, process_count, 'count', timestamp)
            
        except Exception as e:
            logger.error(f"Redis 메트릭 수집 오류: {e}")
    
    def _collect_nginx_metrics(self, service_name: str, timestamp: datetime):
        """Nginx 메트릭 수집"""
        try:
            # Nginx 프로세스 확인
            nginx_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'nginx' in proc.info['name'].lower():
                        nginx_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            process_count = len(nginx_processes)
            self._add_metric(service_name, MetricType.CONCURRENT_USERS, process_count, 'count', timestamp)
            
        except Exception as e:
            logger.error(f"Nginx 메트릭 수집 오류: {e}")
    
    def _collect_generic_metrics(self, service_name: str, timestamp: datetime):
        """일반 서비스 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_usage = psutil.cpu_percent(interval=1)
            self._add_metric(service_name, MetricType.CPU_USAGE, cpu_usage, '%', timestamp)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            self._add_metric(service_name, MetricType.MEMORY_USAGE, memory_usage, '%', timestamp)
            
        except Exception as e:
            logger.error(f"일반 서비스 메트릭 수집 오류 ({service_name}): {e}")
    
    def _add_metric(self, service_name: str, metric_type: MetricType, value: float, 
                   unit: str, timestamp: datetime):
        """메트릭 추가"""
        metric_id = f"metric_{int(time.time() * 1000000)}"
        
        metric = PerformanceMetric(
            id=metric_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            timestamp=timestamp,
            service_name=service_name
        )
        
        self.metrics[service_name].append(metric)
    
    def _measure_response_time(self, url: str) -> float:
        """응답 시간 측정"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            end_time = time.time()
            
            if response.status_code == 200:
                return (end_time - start_time) * 1000  # ms
            else:
                return 5000.0  # 오류 시 5초로 설정
        except:
            return 10000.0  # 연결 실패 시 10초로 설정
    
    def _calculate_request_rate(self, service_name: str) -> float:
        """요청률 계산 (시뮬레이션)"""
        # 실제로는 로그나 메트릭에서 계산
        import random
        return random.uniform(100, 1000)  # 100-1000 req/min
    
    def _get_database_connections(self) -> int:
        """데이터베이스 연결 수 조회 (시뮬레이션)"""
        # 실제로는 데이터베이스에서 조회
        import random
        return random.randint(1, 10)
    
    def _check_performance_alerts(self):
        """성능 알림 확인"""
        for service_name, metrics in self.metrics.items():
            if not metrics:
                continue
            
            # 최근 메트릭들 확인
            recent_metrics = list(metrics)[-10:]  # 최근 10개
            
            for metric in recent_metrics:
                self._check_metric_alert(service_name, metric)
    
    def _check_metric_alert(self, service_name: str, metric: PerformanceMetric):
        """메트릭 알림 확인"""
        thresholds = self.thresholds.get(metric.metric_type)
        if not thresholds:
            return
        
        # 알림 레벨 결정
        alert_level = None
        if metric.value >= thresholds['critical']:
            alert_level = AlertLevel.CRITICAL
        elif metric.value >= thresholds['error']:
            alert_level = AlertLevel.ERROR
        elif metric.value >= thresholds['warning']:
            alert_level = AlertLevel.WARNING
        
        if alert_level:
            self._create_performance_alert(service_name, metric, alert_level)
    
    def _create_performance_alert(self, service_name: str, metric: PerformanceMetric, 
                                 alert_level: AlertLevel):
        """성능 알림 생성"""
        alert_id = f"alert_{int(time.time() * 1000)}"
        
        # 기존 알림 확인
        existing_alert = self._find_existing_alert(service_name, metric.metric_type, alert_level)
        if existing_alert:
            return  # 이미 존재하는 알림
        
        thresholds = self.thresholds.get(metric.metric_type, {})
        threshold_value = thresholds.get(alert_level.value, 0)
        
        alert = PerformanceAlert(
            id=alert_id,
            metric_type=metric.metric_type,
            alert_level=alert_level,
            current_value=metric.value,
            threshold_value=threshold_value,
            message=f"{service_name} {metric.metric_type.value}이 {alert_level.value} 수준에 도달했습니다: {metric.value:.2f}{metric.unit}",
            timestamp=datetime.now(),
            service_name=service_name
        )
        
        self.active_alerts[alert_id] = alert
        
        # 콜백 실행
        self._notify_performance_alert(alert)
        
        logger.warning(f"성능 알림 생성: {alert_id} - {service_name} - {metric.metric_type.value}")
    
    def _find_existing_alert(self, service_name: str, metric_type: MetricType, 
                            alert_level: AlertLevel) -> Optional[PerformanceAlert]:
        """기존 알림 찾기"""
        for alert in self.active_alerts.values():
            if (alert.service_name == service_name and 
                alert.metric_type == metric_type and 
                alert.alert_level == alert_level and 
                not alert.resolved):
                return alert
        return None
    
    def _notify_performance_alert(self, alert: PerformanceAlert):
        """성능 알림 알림"""
        for callback in self.monitoring_callbacks:
            try:
                callback({
                    'type': 'performance_alert',
                    'alert': asdict(alert)
                })
            except Exception as e:
                logger.error(f"성능 알림 알림 오류: {e}")
    
    def _cleanup_old_metrics(self):
        """오래된 메트릭 정리"""
        cutoff_time = datetime.now() - timedelta(hours=self.metric_retention_hours)
        
        for service_name, metrics in self.metrics.items():
            while metrics and metrics[0].timestamp < cutoff_time:
                metrics.popleft()
    
    def get_metrics(self, service_name: str, metric_type: MetricType = None, 
                   hours: int = 24) -> List[PerformanceMetric]:
        """메트릭 조회"""
        metrics = list(self.metrics.get(service_name, []))
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        # 시간 필터링
        cutoff_time = datetime.now() - timedelta(hours=hours)
        metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        return metrics
    
    def get_performance_summary(self, service_name: str, hours: int = 24) -> Dict[str, Any]:
        """성능 요약 조회"""
        metrics = self.get_metrics(service_name, hours=hours)
        
        if not metrics:
            return {}
        
        # 메트릭 타입별 통계
        metric_stats = {}
        for metric_type in MetricType:
            type_metrics = [m for m in metrics if m.metric_type == metric_type]
            if type_metrics:
                values = [m.value for m in type_metrics]
                metric_stats[metric_type.value] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': statistics.mean(values),
                    'latest': values[-1] if values else 0
                }
        
        # 전체 성능 상태 계산
        overall_status = self._calculate_overall_status(metrics)
        
        return {
            'service_name': service_name,
            'overall_status': overall_status.value,
            'metric_stats': metric_stats,
            'total_metrics': len(metrics),
            'time_range_hours': hours
        }
    
    def _calculate_overall_status(self, metrics: List[PerformanceMetric]) -> PerformanceStatus:
        """전체 성능 상태 계산"""
        if not metrics:
            return PerformanceStatus.GOOD
        
        # 최근 메트릭들의 평균 상태 계산
        recent_metrics = metrics[-10:]  # 최근 10개
        
        critical_count = 0
        error_count = 0
        warning_count = 0
        
        for metric in recent_metrics:
            thresholds = self.thresholds.get(metric.metric_type, {})
            if metric.value >= thresholds.get('critical', 100):
                critical_count += 1
            elif metric.value >= thresholds.get('error', 100):
                error_count += 1
            elif metric.value >= thresholds.get('warning', 100):
                warning_count += 1
        
        if critical_count > 0:
            return PerformanceStatus.CRITICAL
        elif error_count > 2:
            return PerformanceStatus.POOR
        elif warning_count > 3:
            return PerformanceStatus.FAIR
        elif warning_count > 0:
            return PerformanceStatus.GOOD
        else:
            return PerformanceStatus.EXCELLENT
    
    def get_active_alerts(self, service_name: str = None, alert_level: AlertLevel = None) -> List[PerformanceAlert]:
        """활성 알림 조회"""
        alerts = [alert for alert in self.active_alerts.values() if not alert.resolved]
        
        if service_name:
            alerts = [alert for alert in alerts if alert.service_name == service_name]
        
        if alert_level:
            alerts = [alert for alert in alerts if alert.alert_level == alert_level]
        
        return alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """알림 해결"""
        alert = self.active_alerts.get(alert_id)
        if not alert:
            return False
        
        alert.resolved = True
        alert.resolved_at = datetime.now()
        
        logger.info(f"성능 알림 해결: {alert_id}")
        return True
    
    def generate_performance_report(self, service_name: str, hours: int = 24) -> PerformanceReport:
        """성능 리포트 생성"""
        metrics = self.get_metrics(service_name, hours=hours)
        alerts = self.get_active_alerts(service_name)
        
        start_time = datetime.now() - timedelta(hours=hours)
        end_time = datetime.now()
        
        # 메트릭 요약
        metrics_summary = {}
        for metric_type in MetricType:
            type_metrics = [m for m in metrics if m.metric_type == metric_type]
            if type_metrics:
                values = [m.value for m in type_metrics]
                metrics_summary[metric_type.value] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': statistics.mean(values),
                    'latest': values[-1] if values else 0
                }
        
        # 알림 요약
        alerts_summary = {
            'total_alerts': len(alerts),
            'critical_alerts': len([a for a in alerts if a.alert_level == AlertLevel.CRITICAL]),
            'error_alerts': len([a for a in alerts if a.alert_level == AlertLevel.ERROR]),
            'warning_alerts': len([a for a in alerts if a.alert_level == AlertLevel.WARNING])
        }
        
        # 전체 상태
        overall_status = self._calculate_overall_status(metrics)
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(metrics, alerts)
        
        # 리포트 생성
        report = PerformanceReport(
            id=f"report_{int(time.time() * 1000)}",
            report_type="performance_analysis",
            start_time=start_time,
            end_time=end_time,
            service_name=service_name,
            overall_status=overall_status,
            metrics_summary=metrics_summary,
            alerts_summary=alerts_summary,
            recommendations=recommendations
        )
        
        self.performance_reports.append(report)
        
        return report
    
    def _generate_recommendations(self, metrics: List[PerformanceMetric], 
                                 alerts: List[PerformanceAlert]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # CPU 사용률 확인
        cpu_metrics = [m for m in metrics if m.metric_type == MetricType.CPU_USAGE]
        if cpu_metrics:
            avg_cpu = statistics.mean([m.value for m in cpu_metrics])
            if avg_cpu > 80:
                recommendations.append("CPU 사용률이 높습니다. 서버 리소스를 확장하거나 최적화를 고려하세요.")
        
        # 메모리 사용률 확인
        memory_metrics = [m for m in metrics if m.metric_type == MetricType.MEMORY_USAGE]
        if memory_metrics:
            avg_memory = statistics.mean([m.value for m in memory_metrics])
            if avg_memory > 85:
                recommendations.append("메모리 사용률이 높습니다. 메모리 증설이나 메모리 누수 점검을 고려하세요.")
        
        # 응답 시간 확인
        response_metrics = [m for m in metrics if m.metric_type == MetricType.RESPONSE_TIME]
        if response_metrics:
            avg_response = statistics.mean([m.value for m in response_metrics])
            if avg_response > 3000:
                recommendations.append("응답 시간이 느립니다. 데이터베이스 쿼리 최적화나 캐싱을 고려하세요.")
        
        # 에러율 확인
        error_metrics = [m for m in metrics if m.metric_type == MetricType.ERROR_RATE]
        if error_metrics:
            avg_error = statistics.mean([m.value for m in error_metrics])
            if avg_error > 5:
                recommendations.append("에러율이 높습니다. 애플리케이션 로그를 확인하고 버그를 수정하세요.")
        
        # 알림 기반 권장사항
        critical_alerts = [a for a in alerts if a.alert_level == AlertLevel.CRITICAL]
        if critical_alerts:
            recommendations.append("심각한 성능 문제가 발생했습니다. 즉시 조치가 필요합니다.")
        
        if not recommendations:
            recommendations.append("시스템이 정상적으로 작동하고 있습니다.")
        
        return recommendations
    
    def add_monitoring_callback(self, callback: Callable):
        """모니터링 콜백 함수 추가"""
        self.monitoring_callbacks.append(callback)
    
    def remove_monitoring_callback(self, callback: Callable):
        """모니터링 콜백 함수 제거"""
        if callback in self.monitoring_callbacks:
            self.monitoring_callbacks.remove(callback)
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'is_monitoring': self.is_monitoring,
            'monitoring_interval': self.monitoring_interval,
            'monitored_services': self.monitored_services,
            'total_metrics': sum(len(metrics) for metrics in self.metrics.values()),
            'active_alerts': len([a for a in self.active_alerts.values() if not a.resolved]),
            'performance_reports': len(self.performance_reports)
        }
    
    def stop_service(self):
        """서비스 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("성능 모니터링 서비스 중지")

# 전역 인스턴스
performance_monitoring_service = PerformanceMonitoringService()
