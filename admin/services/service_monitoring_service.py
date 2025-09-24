#!/usr/bin/env python3
"""
서비스 상태 모니터링 시스템
AWS Management Console을 벤치마킹한 서비스 모니터링
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque
import psutil
import requests
import subprocess
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """서비스 상태"""
    HEALTHY = "healthy"           # 정상
    WARNING = "warning"           # 경고
    CRITICAL = "critical"         # 위험
    DOWN = "down"                 # 다운
    MAINTENANCE = "maintenance"   # 유지보수

class MetricType(Enum):
    """메트릭 타입"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_IO = "network_io"
    REQUEST_COUNT = "request_count"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    ACTIVE_CONNECTIONS = "active_connections"

class AlertSeverity(Enum):
    """알림 심각도"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ServiceMetric:
    """서비스 메트릭 클래스"""
    service_name: str
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    status: ServiceStatus
    threshold_warning: float = None
    threshold_critical: float = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ServiceAlert:
    """서비스 알림 클래스"""
    id: str
    service_name: str
    metric_type: MetricType
    severity: AlertSeverity
    message: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ServiceHealth:
    """서비스 건강 상태 클래스"""
    service_name: str
    status: ServiceStatus
    last_check: datetime
    uptime: float
    response_time: float
    error_rate: float
    metrics: Dict[str, float]
    alerts: List[ServiceAlert]
    dependencies: List[str]
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ServiceMonitoringService:
    """서비스 모니터링 서비스"""
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.metrics_history: Dict[str, deque] = {}
        self.active_alerts: Dict[str, ServiceAlert] = {}
        self.monitoring_callbacks: List[Callable] = []
        
        # 모니터링 설정
        self.monitoring_interval = 30  # 30초
        self.metric_retention_hours = 24  # 24시간
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # 임계값 설정
        self.thresholds = {
            MetricType.CPU_USAGE: {'warning': 70.0, 'critical': 90.0},
            MetricType.MEMORY_USAGE: {'warning': 80.0, 'critical': 95.0},
            MetricType.DISK_USAGE: {'warning': 85.0, 'critical': 95.0},
            MetricType.RESPONSE_TIME: {'warning': 2000.0, 'critical': 5000.0},
            MetricType.ERROR_RATE: {'warning': 5.0, 'critical': 10.0}
        }
        
        # 모니터링할 서비스 목록
        self.monitored_services = [
            'flask_app',
            'database',
            'redis',
            'nginx',
            'ai_service',
            'payment_service',
            'notification_service'
        ]
        
        # 메트릭 히스토리 초기화
        for service in self.monitored_services:
            self.metrics_history[service] = deque(maxlen=2880)  # 24시간 * 30초 간격
        
        # 모니터링 시작
        self._start_monitoring()
    
    def _start_monitoring(self):
        """모니터링 시작"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        logger.info("서비스 모니터링 시작")
    
    def _monitoring_worker(self):
        """모니터링 워커"""
        while self.is_monitoring:
            try:
                for service_name in self.monitored_services:
                    self._check_service_health(service_name)
                
                # 오래된 메트릭 정리
                self._cleanup_old_metrics()
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"모니터링 워커 오류: {e}")
                time.sleep(60)
    
    def _check_service_health(self, service_name: str):
        """서비스 건강 상태 확인"""
        try:
            # 서비스별 체크 로직
            if service_name == 'flask_app':
                health = self._check_flask_app()
            elif service_name == 'database':
                health = self._check_database()
            elif service_name == 'redis':
                health = self._check_redis()
            elif service_name == 'nginx':
                health = self._check_nginx()
            else:
                health = self._check_generic_service(service_name)
            
            # 서비스 상태 업데이트
            self.services[service_name] = health
            
            # 메트릭 저장
            self._store_metrics(service_name, health)
            
            # 알림 확인
            self._check_alerts(service_name, health)
            
        except Exception as e:
            logger.error(f"서비스 건강 상태 확인 오류 ({service_name}): {e}")
            # 오류 발생 시 다운 상태로 설정
            self.services[service_name] = ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.DOWN,
                last_check=datetime.now(),
                uptime=0.0,
                response_time=0.0,
                error_rate=100.0,
                metrics={},
                alerts=[],
                dependencies=[]
            )
    
    def _check_flask_app(self) -> ServiceHealth:
        """Flask 앱 상태 확인"""
        try:
            start_time = time.time()
            response = requests.get('http://localhost:8000/health', timeout=5)
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                status = ServiceStatus.HEALTHY
                error_rate = 0.0
            else:
                status = ServiceStatus.WARNING
                error_rate = 10.0
            
            # 시스템 리소스 확인
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_usage = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            return ServiceHealth(
                service_name='flask_app',
                status=status,
                last_check=datetime.now(),
                uptime=self._get_uptime('flask_app'),
                response_time=response_time,
                error_rate=error_rate,
                metrics={
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'disk_usage': disk_usage,
                    'response_time': response_time
                },
                alerts=[],
                dependencies=['database', 'redis']
            )
            
        except Exception as e:
            logger.error(f"Flask 앱 상태 확인 오류: {e}")
            return ServiceHealth(
                service_name='flask_app',
                status=ServiceStatus.DOWN,
                last_check=datetime.now(),
                uptime=0.0,
                response_time=0.0,
                error_rate=100.0,
                metrics={},
                alerts=[],
                dependencies=['database', 'redis']
            )
    
    def _check_database(self) -> ServiceHealth:
        """데이터베이스 상태 확인"""
        try:
            # SQLite 데이터베이스 파일 확인
            db_file = 'instance/smartcompressor.db'
            if os.path.exists(db_file):
                file_size = os.path.getsize(db_file)
                status = ServiceStatus.HEALTHY
                error_rate = 0.0
            else:
                status = ServiceStatus.DOWN
                error_rate = 100.0
                file_size = 0
            
            return ServiceHealth(
                service_name='database',
                status=status,
                last_check=datetime.now(),
                uptime=self._get_uptime('database'),
                response_time=0.0,
                error_rate=error_rate,
                metrics={
                    'file_size': file_size,
                    'disk_usage': psutil.disk_usage('/').percent
                },
                alerts=[],
                dependencies=[]
            )
            
        except Exception as e:
            logger.error(f"데이터베이스 상태 확인 오류: {e}")
            return ServiceHealth(
                service_name='database',
                status=ServiceStatus.DOWN,
                last_check=datetime.now(),
                uptime=0.0,
                response_time=0.0,
                error_rate=100.0,
                metrics={},
                alerts=[],
                dependencies=[]
            )
    
    def _check_redis(self) -> ServiceHealth:
        """Redis 상태 확인"""
        try:
            # Redis 프로세스 확인
            redis_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'redis' in proc.info['name'].lower():
                        redis_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if redis_processes:
                status = ServiceStatus.HEALTHY
                error_rate = 0.0
            else:
                status = ServiceStatus.DOWN
                error_rate = 100.0
            
            return ServiceHealth(
                service_name='redis',
                status=status,
                last_check=datetime.now(),
                uptime=self._get_uptime('redis'),
                response_time=0.0,
                error_rate=error_rate,
                metrics={
                    'process_count': len(redis_processes),
                    'memory_usage': psutil.virtual_memory().percent
                },
                alerts=[],
                dependencies=[]
            )
            
        except Exception as e:
            logger.error(f"Redis 상태 확인 오류: {e}")
            return ServiceHealth(
                service_name='redis',
                status=ServiceStatus.DOWN,
                last_check=datetime.now(),
                uptime=0.0,
                response_time=0.0,
                error_rate=100.0,
                metrics={},
                alerts=[],
                dependencies=[]
            )
    
    def _check_nginx(self) -> ServiceHealth:
        """Nginx 상태 확인"""
        try:
            # Nginx 프로세스 확인
            nginx_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'nginx' in proc.info['name'].lower():
                        nginx_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if nginx_processes:
                status = ServiceStatus.HEALTHY
                error_rate = 0.0
            else:
                status = ServiceStatus.DOWN
                error_rate = 100.0
            
            return ServiceHealth(
                service_name='nginx',
                status=status,
                last_check=datetime.now(),
                uptime=self._get_uptime('nginx'),
                response_time=0.0,
                error_rate=error_rate,
                metrics={
                    'process_count': len(nginx_processes),
                    'memory_usage': psutil.virtual_memory().percent
                },
                alerts=[],
                dependencies=[]
            )
            
        except Exception as e:
            logger.error(f"Nginx 상태 확인 오류: {e}")
            return ServiceHealth(
                service_name='nginx',
                status=ServiceStatus.DOWN,
                last_check=datetime.now(),
                uptime=0.0,
                response_time=0.0,
                error_rate=100.0,
                metrics={},
                dependencies=[]
            )
    
    def _check_generic_service(self, service_name: str) -> ServiceHealth:
        """일반 서비스 상태 확인"""
        try:
            # 프로세스 확인
            service_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if service_name in proc.info['name'].lower():
                        service_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if service_processes:
                status = ServiceStatus.HEALTHY
                error_rate = 0.0
            else:
                status = ServiceStatus.DOWN
                error_rate = 100.0
            
            return ServiceHealth(
                service_name=service_name,
                status=status,
                last_check=datetime.now(),
                uptime=self._get_uptime(service_name),
                response_time=0.0,
                error_rate=error_rate,
                metrics={
                    'process_count': len(service_processes),
                    'memory_usage': psutil.virtual_memory().percent
                },
                alerts=[],
                dependencies=[]
            )
            
        except Exception as e:
            logger.error(f"일반 서비스 상태 확인 오류 ({service_name}): {e}")
            return ServiceHealth(
                service_name=service_name,
                status=ServiceStatus.DOWN,
                last_check=datetime.now(),
                uptime=0.0,
                response_time=0.0,
                error_rate=100.0,
                metrics={},
                alerts=[],
                dependencies=[]
            )
    
    def _get_uptime(self, service_name: str) -> float:
        """서비스 가동 시간 계산"""
        # 실제로는 서비스 시작 시간을 추적해야 함
        # 여기서는 시뮬레이션
        return 3600.0  # 1시간
    
    def _store_metrics(self, service_name: str, health: ServiceHealth):
        """메트릭 저장"""
        for metric_type, value in health.metrics.items():
            metric = ServiceMetric(
                service_name=service_name,
                metric_type=MetricType(metric_type),
                value=value,
                unit=self._get_metric_unit(metric_type),
                timestamp=datetime.now(),
                status=health.status,
                threshold_warning=self.thresholds.get(MetricType(metric_type), {}).get('warning'),
                threshold_critical=self.thresholds.get(MetricType(metric_type), {}).get('critical')
            )
            
            self.metrics_history[service_name].append(metric)
    
    def _get_metric_unit(self, metric_type: str) -> str:
        """메트릭 단위 반환"""
        units = {
            'cpu_usage': '%',
            'memory_usage': '%',
            'disk_usage': '%',
            'response_time': 'ms',
            'error_rate': '%',
            'file_size': 'bytes',
            'process_count': 'count'
        }
        return units.get(metric_type, '')
    
    def _check_alerts(self, service_name: str, health: ServiceHealth):
        """알림 확인"""
        for metric_type, value in health.metrics.items():
            if metric_type in ['cpu_usage', 'memory_usage', 'disk_usage', 'response_time', 'error_rate']:
                self._check_metric_alert(service_name, MetricType(metric_type), value)
    
    def _check_metric_alert(self, service_name: str, metric_type: MetricType, value: float):
        """메트릭 알림 확인"""
        thresholds = self.thresholds.get(metric_type, {})
        warning_threshold = thresholds.get('warning')
        critical_threshold = thresholds.get('critical')
        
        if not warning_threshold or not critical_threshold:
            return
        
        alert_id = f"{service_name}_{metric_type.value}_{int(time.time())}"
        
        # 위험 상태 확인
        if value >= critical_threshold:
            if not self._has_active_alert(service_name, metric_type, AlertSeverity.CRITICAL):
                self._create_alert(
                    alert_id=alert_id,
                    service_name=service_name,
                    metric_type=metric_type,
                    severity=AlertSeverity.CRITICAL,
                    message=f"{service_name} {metric_type.value}이 위험 수준에 도달했습니다: {value:.2f}%",
                    value=value,
                    threshold=critical_threshold
                )
        
        # 경고 상태 확인
        elif value >= warning_threshold:
            if not self._has_active_alert(service_name, metric_type, AlertSeverity.WARNING):
                self._create_alert(
                    alert_id=alert_id,
                    service_name=service_name,
                    metric_type=metric_type,
                    severity=AlertSeverity.WARNING,
                    message=f"{service_name} {metric_type.value}이 경고 수준에 도달했습니다: {value:.2f}%",
                    value=value,
                    threshold=warning_threshold
                )
    
    def _has_active_alert(self, service_name: str, metric_type: MetricType, severity: AlertSeverity) -> bool:
        """활성 알림 확인"""
        for alert in self.active_alerts.values():
            if (alert.service_name == service_name and 
                alert.metric_type == metric_type and 
                alert.severity == severity and 
                not alert.resolved):
                return True
        return False
    
    def _create_alert(self, alert_id: str, service_name: str, metric_type: MetricType, 
                     severity: AlertSeverity, message: str, value: float, threshold: float):
        """알림 생성"""
        alert = ServiceAlert(
            id=alert_id,
            service_name=service_name,
            metric_type=metric_type,
            severity=severity,
            message=message,
            value=value,
            threshold=threshold,
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_id] = alert
        
        # 콜백 실행
        self._notify_alert_created(alert)
        
        logger.warning(f"서비스 알림 생성: {service_name} - {message}")
    
    def _notify_alert_created(self, alert: ServiceAlert):
        """알림 생성 알림"""
        for callback in self.monitoring_callbacks:
            try:
                callback({
                    'type': 'alert_created',
                    'alert': asdict(alert)
                })
            except Exception as e:
                logger.error(f"알림 생성 알림 오류: {e}")
    
    def _cleanup_old_metrics(self):
        """오래된 메트릭 정리"""
        cutoff_time = datetime.now() - timedelta(hours=self.metric_retention_hours)
        
        for service_name, metrics in self.metrics_history.items():
            while metrics and metrics[0].timestamp < cutoff_time:
                metrics.popleft()
    
    def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """서비스 건강 상태 조회"""
        return self.services.get(service_name)
    
    def get_all_services_health(self) -> Dict[str, ServiceHealth]:
        """모든 서비스 건강 상태 조회"""
        return dict(self.services)
    
    def get_metrics_history(self, service_name: str, metric_type: MetricType = None, 
                           hours: int = 24) -> List[ServiceMetric]:
        """메트릭 히스토리 조회"""
        metrics = list(self.metrics_history.get(service_name, []))
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        # 시간 필터링
        cutoff_time = datetime.now() - timedelta(hours=hours)
        metrics = [m for m in metrics if m.timestamp >= cutoff_time]
        
        return metrics
    
    def get_active_alerts(self, service_name: str = None, severity: AlertSeverity = None) -> List[ServiceAlert]:
        """활성 알림 조회"""
        alerts = [alert for alert in self.active_alerts.values() if not alert.resolved]
        
        if service_name:
            alerts = [alert for alert in alerts if alert.service_name == service_name]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """알림 해결"""
        alert = self.active_alerts.get(alert_id)
        if not alert:
            return False
        
        alert.resolved = True
        alert.resolved_at = datetime.now()
        alert.resolved_by = resolved_by
        
        logger.info(f"알림 해결: {alert_id} - {resolved_by}")
        return True
    
    def get_service_summary(self) -> Dict[str, Any]:
        """서비스 요약 조회"""
        total_services = len(self.services)
        healthy_services = len([s for s in self.services.values() if s.status == ServiceStatus.HEALTHY])
        warning_services = len([s for s in self.services.values() if s.status == ServiceStatus.WARNING])
        critical_services = len([s for s in self.services.values() if s.status == ServiceStatus.CRITICAL])
        down_services = len([s for s in self.services.values() if s.status == ServiceStatus.DOWN])
        
        active_alerts = len([a for a in self.active_alerts.values() if not a.resolved])
        critical_alerts = len([a for a in self.active_alerts.values() 
                              if not a.resolved and a.severity == AlertSeverity.CRITICAL])
        
        return {
            'total_services': total_services,
            'healthy_services': healthy_services,
            'warning_services': warning_services,
            'critical_services': critical_services,
            'down_services': down_services,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'overall_status': self._get_overall_status()
        }
    
    def _get_overall_status(self) -> ServiceStatus:
        """전체 상태 계산"""
        if not self.services:
            return ServiceStatus.DOWN
        
        statuses = [service.status for service in self.services.values()]
        
        if ServiceStatus.DOWN in statuses:
            return ServiceStatus.DOWN
        elif ServiceStatus.CRITICAL in statuses:
            return ServiceStatus.CRITICAL
        elif ServiceStatus.WARNING in statuses:
            return ServiceStatus.WARNING
        else:
            return ServiceStatus.HEALTHY
    
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
            'total_services': len(self.services),
            'active_alerts': len([a for a in self.active_alerts.values() if not a.resolved]),
            'total_metrics': sum(len(metrics) for metrics in self.metrics_history.values())
        }
    
    def stop_service(self):
        """서비스 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("서비스 모니터링 중지")

# 전역 인스턴스
service_monitoring_service = ServiceMonitoringService()
