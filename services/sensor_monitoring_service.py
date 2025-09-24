#!/usr/bin/env python3
"""
센서 상태 모니터링 서비스
Tesla 스타일의 실시간 센서 상태 모니터링 및 이상 감지
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, deque
import numpy as np
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorStatus(Enum):
    """센서 상태 열거형"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"
    ERROR = "error"

class AnomalySeverity(Enum):
    """이상 심각도 열거형"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SensorHealth:
    """센서 건강 상태"""
    device_id: str
    status: SensorStatus
    last_seen: float
    uptime: float
    data_quality: float
    anomaly_count: int
    temperature_status: SensorStatus
    vibration_status: SensorStatus
    power_status: SensorStatus
    audio_status: SensorStatus
    overall_health: float  # 0-100

@dataclass
class MonitoringAlert:
    """모니터링 알림"""
    device_id: str
    alert_type: str
    severity: AnomalySeverity
    message: str
    timestamp: float
    sensor_data: Dict
    auto_resolved: bool = False

class SensorMonitoringService:
    """센서 상태 모니터링 서비스 (Tesla 스타일)"""
    
    def __init__(self):
        self.device_health = {}  # device_id -> SensorHealth
        self.alert_history = defaultdict(deque)  # device_id -> deque of alerts
        self.monitoring_rules = self._init_monitoring_rules()
        self.alert_callbacks = []
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 모니터링 설정
        self.health_check_interval = 30  # 30초마다
        self.offline_threshold = 300  # 5분
        self.data_quality_threshold = 0.8
        self.anomaly_thresholds = {
            'temperature': {'warning': 0, 'critical': 5},
            'vibration': {'warning': 1.0, 'critical': 2.0},
            'power': {'warning': 80, 'critical': 95},
            'audio': {'warning': 500, 'critical': 1000}
        }
        
        logger.info("센서 모니터링 서비스 초기화 완료")
    
    def _init_monitoring_rules(self) -> Dict:
        """모니터링 규칙 초기화"""
        return {
            'temperature': {
                'normal_range': (-25, -15),
                'warning_range': (-15, -10),
                'critical_range': (-10, 10)
            },
            'vibration': {
                'normal_max': 0.5,
                'warning_max': 1.0,
                'critical_max': 2.0
            },
            'power': {
                'normal_max': 70,
                'warning_max': 80,
                'critical_max': 95
            },
            'audio': {
                'normal_max': 200,
                'warning_max': 500,
                'critical_max': 1000
            }
        }
    
    def start_monitoring(self):
        """모니터링 시작"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("센서 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("센서 모니터링 중지")
    
    def add_alert_callback(self, callback: Callable[[MonitoringAlert], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    def update_sensor_data(self, device_id: str, sensor_data: Dict):
        """센서 데이터 업데이트"""
        try:
            current_time = time.time()
            
            # 디바이스 건강 상태 업데이트
            if device_id not in self.device_health:
                self.device_health[device_id] = SensorHealth(
                    device_id=device_id,
                    status=SensorStatus.NORMAL,
                    last_seen=current_time,
                    uptime=0,
                    data_quality=1.0,
                    anomaly_count=0,
                    temperature_status=SensorStatus.NORMAL,
                    vibration_status=SensorStatus.NORMAL,
                    power_status=SensorStatus.NORMAL,
                    audio_status=SensorStatus.NORMAL,
                    overall_health=100.0
                )
            
            health = self.device_health[device_id]
            health.last_seen = current_time
            
            # 개별 센서 상태 평가
            temp_status = self._evaluate_temperature_status(sensor_data.get('temperature', 0))
            vib_status = self._evaluate_vibration_status(sensor_data)
            power_status = self._evaluate_power_status(sensor_data.get('power_consumption', 0))
            audio_status = self._evaluate_audio_status(sensor_data.get('audio_level', 0))
            
            # 상태 업데이트
            health.temperature_status = temp_status
            health.vibration_status = vib_status
            health.power_status = power_status
            health.audio_status = audio_status
            
            # 전체 상태 평가
            health.status = self._evaluate_overall_status([temp_status, vib_status, power_status, audio_status])
            health.overall_health = self._calculate_overall_health(health)
            
            # 알림 생성
            self._check_for_alerts(device_id, sensor_data, health)
            
        except Exception as e:
            logger.error(f"센서 데이터 업데이트 실패: {e}")
    
    def _evaluate_temperature_status(self, temperature: float) -> SensorStatus:
        """온도 상태 평가"""
        rules = self.monitoring_rules['temperature']
        
        if temperature <= rules['normal_range'][1]:
            return SensorStatus.NORMAL
        elif temperature <= rules['warning_range'][1]:
            return SensorStatus.WARNING
        else:
            return SensorStatus.CRITICAL
    
    def _evaluate_vibration_status(self, sensor_data: Dict) -> SensorStatus:
        """진동 상태 평가"""
        vibration_magnitude = np.sqrt(
            sensor_data.get('vibration_x', 0)**2 +
            sensor_data.get('vibration_y', 0)**2 +
            sensor_data.get('vibration_z', 0)**2
        )
        
        rules = self.monitoring_rules['vibration']
        
        if vibration_magnitude <= rules['normal_max']:
            return SensorStatus.NORMAL
        elif vibration_magnitude <= rules['warning_max']:
            return SensorStatus.WARNING
        else:
            return SensorStatus.CRITICAL
    
    def _evaluate_power_status(self, power_consumption: float) -> SensorStatus:
        """전력 상태 평가"""
        rules = self.monitoring_rules['power']
        
        if power_consumption <= rules['normal_max']:
            return SensorStatus.NORMAL
        elif power_consumption <= rules['warning_max']:
            return SensorStatus.WARNING
        else:
            return SensorStatus.CRITICAL
    
    def _evaluate_audio_status(self, audio_level: int) -> SensorStatus:
        """오디오 상태 평가"""
        rules = self.monitoring_rules['audio']
        
        if audio_level <= rules['normal_max']:
            return SensorStatus.NORMAL
        elif audio_level <= rules['warning_max']:
            return SensorStatus.WARNING
        else:
            return SensorStatus.CRITICAL
    
    def _evaluate_overall_status(self, statuses: List[SensorStatus]) -> SensorStatus:
        """전체 상태 평가"""
        if SensorStatus.CRITICAL in statuses:
            return SensorStatus.CRITICAL
        elif SensorStatus.WARNING in statuses:
            return SensorStatus.WARNING
        elif SensorStatus.ERROR in statuses:
            return SensorStatus.ERROR
        else:
            return SensorStatus.NORMAL
    
    def _calculate_overall_health(self, health: SensorHealth) -> float:
        """전체 건강도 계산 (0-100)"""
        try:
            # 개별 센서 건강도 계산
            temp_health = self._sensor_health_score(health.temperature_status)
            vib_health = self._sensor_health_score(health.vibration_status)
            power_health = self._sensor_health_score(health.power_status)
            audio_health = self._sensor_health_score(health.audio_status)
            
            # 가중 평균 (온도와 진동에 더 높은 가중치)
            overall_health = (
                temp_health * 0.3 +
                vib_health * 0.3 +
                power_health * 0.2 +
                audio_health * 0.2
            )
            
            # 데이터 품질 반영
            overall_health *= health.data_quality
            
            # 이상 감지 수에 따른 감점
            if health.anomaly_count > 0:
                anomaly_penalty = min(health.anomaly_count * 5, 20)  # 최대 20점 감점
                overall_health -= anomaly_penalty
            
            return max(0, min(100, overall_health))
            
        except Exception as e:
            logger.error(f"전체 건강도 계산 실패: {e}")
            return 50.0
    
    def _sensor_health_score(self, status: SensorStatus) -> float:
        """센서 상태별 건강도 점수"""
        status_scores = {
            SensorStatus.NORMAL: 100.0,
            SensorStatus.WARNING: 70.0,
            SensorStatus.CRITICAL: 30.0,
            SensorStatus.ERROR: 0.0,
            SensorStatus.OFFLINE: 0.0
        }
        return status_scores.get(status, 50.0)
    
    def _check_for_alerts(self, device_id: str, sensor_data: Dict, health: SensorHealth):
        """알림 확인"""
        try:
            current_time = time.time()
            
            # 온도 알림
            if health.temperature_status in [SensorStatus.WARNING, SensorStatus.CRITICAL]:
                self._create_alert(
                    device_id=device_id,
                    alert_type='temperature_alert',
                    severity=AnomalySeverity.HIGH if health.temperature_status == SensorStatus.CRITICAL else AnomalySeverity.MEDIUM,
                    message=f'냉동고 온도 이상: {sensor_data.get("temperature", 0):.1f}°C',
                    sensor_data=sensor_data
                )
            
            # 진동 알림
            if health.vibration_status in [SensorStatus.WARNING, SensorStatus.CRITICAL]:
                vibration_magnitude = np.sqrt(
                    sensor_data.get('vibration_x', 0)**2 +
                    sensor_data.get('vibration_y', 0)**2 +
                    sensor_data.get('vibration_z', 0)**2
                )
                self._create_alert(
                    device_id=device_id,
                    alert_type='vibration_alert',
                    severity=AnomalySeverity.HIGH if health.vibration_status == SensorStatus.CRITICAL else AnomalySeverity.MEDIUM,
                    message=f'압축기 진동 이상: {vibration_magnitude:.2f}g',
                    sensor_data=sensor_data
                )
            
            # 전력 알림
            if health.power_status in [SensorStatus.WARNING, SensorStatus.CRITICAL]:
                self._create_alert(
                    device_id=device_id,
                    alert_type='power_alert',
                    severity=AnomalySeverity.HIGH if health.power_status == SensorStatus.CRITICAL else AnomalySeverity.MEDIUM,
                    message=f'전력 소비 이상: {sensor_data.get("power_consumption", 0):.1f}%',
                    sensor_data=sensor_data
                )
            
            # 오디오 알림
            if health.audio_status in [SensorStatus.WARNING, SensorStatus.CRITICAL]:
                self._create_alert(
                    device_id=device_id,
                    alert_type='audio_alert',
                    severity=AnomalySeverity.HIGH if health.audio_status == SensorStatus.CRITICAL else AnomalySeverity.MEDIUM,
                    message=f'압축기 소음 이상: {sensor_data.get("audio_level", 0)}',
                    sensor_data=sensor_data
                )
            
            # 전체 건강도 알림
            if health.overall_health < 50:
                self._create_alert(
                    device_id=device_id,
                    alert_type='health_alert',
                    severity=AnomalySeverity.CRITICAL if health.overall_health < 30 else AnomalySeverity.HIGH,
                    message=f'센서 전체 건강도 저하: {health.overall_health:.1f}%',
                    sensor_data=sensor_data
                )
            
        except Exception as e:
            logger.error(f"알림 확인 실패: {e}")
    
    def _create_alert(self, device_id: str, alert_type: str, severity: AnomalySeverity, 
                     message: str, sensor_data: Dict):
        """알림 생성"""
        try:
            alert = MonitoringAlert(
                device_id=device_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                timestamp=time.time(),
                sensor_data=sensor_data
            )
            
            # 알림 히스토리에 추가
            self.alert_history[device_id].append(alert)
            
            # 최대 100개 알림만 유지
            if len(self.alert_history[device_id]) > 100:
                self.alert_history[device_id].popleft()
            
            # 콜백 함수들 호출
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    logger.error(f"알림 콜백 오류: {e}")
            
            logger.info(f"알림 생성: {device_id} - {alert_type} - {severity.value}")
            
        except Exception as e:
            logger.error(f"알림 생성 실패: {e}")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                current_time = time.time()
                
                # 오프라인 디바이스 확인
                for device_id, health in self.device_health.items():
                    if current_time - health.last_seen > self.offline_threshold:
                        if health.status != SensorStatus.OFFLINE:
                            health.status = SensorStatus.OFFLINE
                            self._create_alert(
                                device_id=device_id,
                                alert_type='offline_alert',
                                severity=AnomalySeverity.HIGH,
                                message=f'디바이스 {device_id} 오프라인',
                                sensor_data={}
                            )
                
                # 데이터 품질 확인
                self._check_data_quality()
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(5)
    
    def _check_data_quality(self):
        """데이터 품질 확인"""
        try:
            for device_id, health in self.device_health.items():
                # 최근 데이터 품질 평가 (간단한 구현)
                if health.data_quality < self.data_quality_threshold:
                    self._create_alert(
                        device_id=device_id,
                        alert_type='data_quality_alert',
                        severity=AnomalySeverity.MEDIUM,
                        message=f'데이터 품질 저하: {health.data_quality:.2f}',
                        sensor_data={}
                    )
                
        except Exception as e:
            logger.error(f"데이터 품질 확인 실패: {e}")
    
    def get_device_health(self, device_id: str) -> Optional[SensorHealth]:
        """디바이스 건강 상태 조회"""
        return self.device_health.get(device_id)
    
    def get_all_device_health(self) -> Dict[str, SensorHealth]:
        """모든 디바이스 건강 상태 조회"""
        return self.device_health.copy()
    
    def get_device_alerts(self, device_id: str, limit: int = 50) -> List[MonitoringAlert]:
        """디바이스 알림 조회"""
        if device_id in self.alert_history:
            return list(self.alert_history[device_id])[-limit:]
        return []
    
    def get_all_alerts(self, limit: int = 100) -> List[MonitoringAlert]:
        """모든 알림 조회"""
        all_alerts = []
        for device_alerts in self.alert_history.values():
            all_alerts.extend(device_alerts)
        
        # 시간순 정렬
        all_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        return all_alerts[:limit]
    
    def resolve_alert(self, device_id: str, alert_type: str):
        """알림 해결"""
        try:
            if device_id in self.alert_history:
                for alert in self.alert_history[device_id]:
                    if alert.alert_type == alert_type and not alert.auto_resolved:
                        alert.auto_resolved = True
                        logger.info(f"알림 해결: {device_id} - {alert_type}")
                        break
                        
        except Exception as e:
            logger.error(f"알림 해결 실패: {e}")
    
    def get_monitoring_status(self) -> Dict:
        """모니터링 상태 조회"""
        try:
            total_devices = len(self.device_health)
            online_devices = len([h for h in self.device_health.values() if h.status != SensorStatus.OFFLINE])
            critical_devices = len([h for h in self.device_health.values() if h.status == SensorStatus.CRITICAL])
            warning_devices = len([h for h in self.device_health.values() if h.status == SensorStatus.WARNING])
            
            total_alerts = sum(len(alerts) for alerts in self.alert_history.values())
            unresolved_alerts = sum(
                len([a for a in alerts if not a.auto_resolved]) 
                for alerts in self.alert_history.values()
            )
            
            return {
                'is_monitoring': self.is_monitoring,
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': total_devices - online_devices,
                'critical_devices': critical_devices,
                'warning_devices': warning_devices,
                'normal_devices': total_devices - critical_devices - warning_devices - (total_devices - online_devices),
                'total_alerts': total_alerts,
                'unresolved_alerts': unresolved_alerts,
                'health_check_interval': self.health_check_interval,
                'offline_threshold': self.offline_threshold
            }
            
        except Exception as e:
            logger.error(f"모니터링 상태 조회 실패: {e}")
            return {}

# 전역 서비스 인스턴스
sensor_monitoring_service = SensorMonitoringService()
