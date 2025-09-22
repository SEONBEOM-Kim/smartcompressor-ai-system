#!/usr/bin/env python3
"""
실시간 매장 상태 모니터링 서비스
Tesla App을 벤치마킹한 실시간 모니터링 시스템
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
import threading
from collections import deque
import statistics

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringStatus(Enum):
    """모니터링 상태"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"

class DataType(Enum):
    """데이터 타입"""
    TEMPERATURE = "temperature"
    EFFICIENCY = "efficiency"
    POWER = "power"
    VIBRATION = "vibration"
    PRESSURE = "pressure"
    HUMIDITY = "humidity"

@dataclass
class SensorData:
    """센서 데이터 클래스"""
    timestamp: datetime
    data_type: DataType
    value: float
    unit: str
    status: MonitoringStatus
    store_id: str
    device_id: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class MonitoringAlert:
    """모니터링 알림 클래스"""
    id: str
    store_id: str
    device_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class RealTimeMonitoringService:
    """실시간 모니터링 서비스"""
    
    def __init__(self):
        self.connected_clients: List[WebSocketServerProtocol] = []
        self.sensor_data_history: Dict[str, deque] = {}
        self.active_alerts: Dict[str, MonitoringAlert] = {}
        self.monitoring_rules: Dict[str, Dict[str, Any]] = {}
        self.data_callbacks: List[Callable] = []
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # 데이터 저장소 (최대 1000개 데이터 포인트)
        self.max_history_size = 1000
        
        # 모니터링 규칙 초기화
        self._initialize_monitoring_rules()
        
        # 데이터 타입별 히스토리 초기화
        for data_type in DataType:
            self.sensor_data_history[data_type.value] = deque(maxlen=self.max_history_size)
    
    def _initialize_monitoring_rules(self):
        """모니터링 규칙 초기화"""
        self.monitoring_rules = {
            DataType.TEMPERATURE.value: {
                'normal_range': (15, 30),
                'warning_range': (10, 35),
                'critical_range': (5, 40),
                'unit': '°C'
            },
            DataType.EFFICIENCY.value: {
                'normal_range': (0.8, 1.0),
                'warning_range': (0.6, 0.8),
                'critical_range': (0.0, 0.6),
                'unit': '%'
            },
            DataType.POWER.value: {
                'normal_range': (500, 1000),
                'warning_range': (1000, 1500),
                'critical_range': (1500, 2000),
                'unit': 'W'
            },
            DataType.VIBRATION.value: {
                'normal_range': (0, 5),
                'warning_range': (5, 10),
                'critical_range': (10, 20),
                'unit': 'mm/s'
            },
            DataType.PRESSURE.value: {
                'normal_range': (1.0, 3.0),
                'warning_range': (0.5, 1.0),
                'critical_range': (0.0, 0.5),
                'unit': 'bar'
            },
            DataType.HUMIDITY.value: {
                'normal_range': (30, 70),
                'warning_range': (20, 80),
                'critical_range': (0, 90),
                'unit': '%'
            }
        }
    
    async def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring:
            logger.warning("모니터링이 이미 실행 중입니다")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("실시간 모니터링 서비스 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("실시간 모니터링 서비스 중지")
    
    def _monitoring_worker(self):
        """모니터링 워커 스레드"""
        while self.is_monitoring:
            try:
                # 센서 데이터 수집 (실제로는 IoT 센서에서 받아옴)
                self._collect_sensor_data()
                
                # 데이터 분석 및 알림 생성
                self._analyze_data()
                
                # 연결된 클라이언트에게 데이터 전송
                asyncio.run(self._broadcast_data())
                
                time.sleep(1)  # 1초마다 업데이트
                
            except Exception as e:
                logger.error(f"모니터링 워커 오류: {e}")
                time.sleep(5)
    
    def _collect_sensor_data(self):
        """센서 데이터 수집 (시뮬레이션)"""
        store_id = "store_001"
        device_id = "compressor_001"
        
        # 실제로는 IoT 센서에서 데이터를 받아옴
        current_time = datetime.now()
        
        # 온도 데이터 (정상 범위 내에서 약간의 변동)
        temp_value = 25 + (time.time() % 10 - 5) * 0.5
        temp_data = SensorData(
            timestamp=current_time,
            data_type=DataType.TEMPERATURE,
            value=temp_value,
            unit="°C",
            status=self._evaluate_status(DataType.TEMPERATURE, temp_value),
            store_id=store_id,
            device_id=device_id
        )
        self._add_sensor_data(temp_data)
        
        # 효율성 데이터
        efficiency_value = 0.9 + (time.time() % 20 - 10) * 0.01
        efficiency_data = SensorData(
            timestamp=current_time,
            data_type=DataType.EFFICIENCY,
            value=efficiency_value,
            unit="%",
            status=self._evaluate_status(DataType.EFFICIENCY, efficiency_value),
            store_id=store_id,
            device_id=device_id
        )
        self._add_sensor_data(efficiency_data)
        
        # 전력 데이터
        power_value = 800 + (time.time() % 15 - 7.5) * 20
        power_data = SensorData(
            timestamp=current_time,
            data_type=DataType.POWER,
            value=power_value,
            unit="W",
            status=self._evaluate_status(DataType.POWER, power_value),
            store_id=store_id,
            device_id=device_id
        )
        self._add_sensor_data(power_data)
        
        # 진동 데이터
        vibration_value = 2 + (time.time() % 8 - 4) * 0.5
        vibration_data = SensorData(
            timestamp=current_time,
            data_type=DataType.VIBRATION,
            value=vibration_value,
            unit="mm/s",
            status=self._evaluate_status(DataType.VIBRATION, vibration_value),
            store_id=store_id,
            device_id=device_id
        )
        self._add_sensor_data(vibration_data)
    
    def _evaluate_status(self, data_type: DataType, value: float) -> MonitoringStatus:
        """데이터 값에 따른 상태 평가"""
        rules = self.monitoring_rules.get(data_type.value, {})
        
        if not rules:
            return MonitoringStatus.NORMAL
        
        normal_range = rules.get('normal_range', (0, 100))
        warning_range = rules.get('warning_range', (0, 100))
        critical_range = rules.get('critical_range', (0, 100))
        
        if normal_range[0] <= value <= normal_range[1]:
            return MonitoringStatus.NORMAL
        elif warning_range[0] <= value <= warning_range[1]:
            return MonitoringStatus.WARNING
        else:
            return MonitoringStatus.CRITICAL
    
    def _add_sensor_data(self, data: SensorData):
        """센서 데이터 추가"""
        self.sensor_data_history[data.data_type.value].append(data)
        
        # 콜백 함수들 실행
        for callback in self.data_callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"데이터 콜백 실행 오류: {e}")
    
    def _analyze_data(self):
        """데이터 분석 및 알림 생성"""
        for data_type, history in self.sensor_data_history.items():
            if len(history) < 10:  # 충분한 데이터가 없으면 스킵
                continue
            
            recent_data = list(history)[-10:]  # 최근 10개 데이터
            
            # 이상 패턴 감지
            self._detect_anomalies(data_type, recent_data)
            
            # 트렌드 분석
            self._analyze_trends(data_type, recent_data)
    
    def _detect_anomalies(self, data_type: str, data_list: List[SensorData]):
        """이상 패턴 감지"""
        if len(data_list) < 5:
            return
        
        values = [d.value for d in data_list]
        mean_value = statistics.mean(values)
        std_value = statistics.stdev(values) if len(values) > 1 else 0
        
        # 최근 값이 평균에서 2 표준편차 이상 벗어나면 이상으로 판단
        latest_value = values[-1]
        if abs(latest_value - mean_value) > 2 * std_value and std_value > 0:
            self._create_alert(
                store_id=data_list[-1].store_id,
                device_id=data_list[-1].device_id,
                alert_type="anomaly",
                severity="warning",
                message=f"{data_type} 값이 비정상적으로 변동했습니다: {latest_value:.2f}"
            )
    
    def _analyze_trends(self, data_type: str, data_list: List[SensorData]):
        """트렌드 분석"""
        if len(data_list) < 10:
            return
        
        values = [d.value for d in data_list]
        
        # 단순 선형 회귀로 트렌드 계산
        n = len(values)
        x = list(range(n))
        y = values
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # 트렌드가 심각하게 나쁘면 알림
        if slope < -0.1:  # 하락 트렌드
            self._create_alert(
                store_id=data_list[-1].store_id,
                device_id=data_list[-1].device_id,
                alert_type="trend",
                severity="warning",
                message=f"{data_type} 값이 지속적으로 하락하고 있습니다"
            )
    
    def _create_alert(self, store_id: str, device_id: str, alert_type: str, 
                     severity: str, message: str):
        """알림 생성"""
        alert_id = f"alert_{int(time.time() * 1000)}"
        
        alert = MonitoringAlert(
            id=alert_id,
            store_id=store_id,
            device_id=device_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=datetime.now()
        )
        
        self.active_alerts[alert_id] = alert
        logger.warning(f"모니터링 알림 생성: {message}")
    
    async def _broadcast_data(self):
        """연결된 클라이언트에게 데이터 브로드캐스트"""
        if not self.connected_clients:
            return
        
        # 최근 데이터 수집
        recent_data = {}
        for data_type, history in self.sensor_data_history.items():
            if history:
                recent_data[data_type] = asdict(history[-1])
        
        # 활성 알림 수집
        active_alerts = [asdict(alert) for alert in self.active_alerts.values() 
                        if not alert.resolved]
        
        # 브로드캐스트 메시지 구성
        message = {
            'type': 'sensor_data',
            'timestamp': datetime.now().isoformat(),
            'data': recent_data,
            'alerts': active_alerts
        }
        
        # 연결된 모든 클라이언트에게 전송
        disconnected_clients = []
        for client in self.connected_clients:
            try:
                await client.send(json.dumps(message, default=str))
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
            except Exception as e:
                logger.error(f"클라이언트 데이터 전송 오류: {e}")
                disconnected_clients.append(client)
        
        # 연결이 끊어진 클라이언트 제거
        for client in disconnected_clients:
            self.connected_clients.remove(client)
    
    async def handle_websocket_connection(self, websocket: WebSocketServerProtocol, path: str):
        """WebSocket 연결 처리"""
        logger.info(f"새로운 WebSocket 연결: {websocket.remote_address}")
        self.connected_clients.append(websocket)
        
        try:
            # 초기 데이터 전송
            await self._send_initial_data(websocket)
            
            # 클라이언트 메시지 처리
            async for message in websocket:
                await self._handle_client_message(websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"WebSocket 연결 종료: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"WebSocket 처리 오류: {e}")
        finally:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
    
    async def _send_initial_data(self, websocket: WebSocketServerProtocol):
        """초기 데이터 전송"""
        # 최근 센서 데이터
        recent_data = {}
        for data_type, history in self.sensor_data_history.items():
            if history:
                recent_data[data_type] = asdict(history[-1])
        
        # 활성 알림
        active_alerts = [asdict(alert) for alert in self.active_alerts.values() 
                        if not alert.resolved]
        
        # 통계 데이터
        statistics_data = self._get_statistics()
        
        initial_message = {
            'type': 'initial_data',
            'timestamp': datetime.now().isoformat(),
            'data': recent_data,
            'alerts': active_alerts,
            'statistics': statistics_data
        }
        
        await websocket.send(json.dumps(initial_message, default=str))
    
    async def _handle_client_message(self, websocket: WebSocketServerProtocol, message: str):
        """클라이언트 메시지 처리"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # 특정 데이터 타입 구독
                data_types = data.get('data_types', [])
                logger.info(f"클라이언트 구독: {data_types}")
                
            elif message_type == 'unsubscribe':
                # 구독 해제
                data_types = data.get('data_types', [])
                logger.info(f"클라이언트 구독 해제: {data_types}")
                
            elif message_type == 'get_history':
                # 히스토리 데이터 요청
                data_type = data.get('data_type')
                limit = data.get('limit', 100)
                history_data = self._get_history_data(data_type, limit)
                
                response = {
                    'type': 'history_data',
                    'data_type': data_type,
                    'data': history_data
                }
                
                await websocket.send(json.dumps(response, default=str))
                
        except json.JSONDecodeError:
            logger.error("잘못된 JSON 메시지")
        except Exception as e:
            logger.error(f"클라이언트 메시지 처리 오류: {e}")
    
    def _get_history_data(self, data_type: str, limit: int) -> List[Dict[str, Any]]:
        """히스토리 데이터 조회"""
        history = self.sensor_data_history.get(data_type, deque())
        recent_data = list(history)[-limit:]
        return [asdict(data) for data in recent_data]
    
    def _get_statistics(self) -> Dict[str, Any]:
        """통계 데이터 조회"""
        statistics_data = {}
        
        for data_type, history in self.sensor_data_history.items():
            if not history:
                continue
            
            values = [d.value for d in history]
            
            statistics_data[data_type] = {
                'count': len(values),
                'mean': statistics.mean(values),
                'min': min(values),
                'max': max(values),
                'std': statistics.stdev(values) if len(values) > 1 else 0,
                'latest': values[-1] if values else None
            }
        
        return statistics_data
    
    def add_data_callback(self, callback: Callable):
        """데이터 콜백 함수 추가"""
        self.data_callbacks.append(callback)
    
    def remove_data_callback(self, callback: Callable):
        """데이터 콜백 함수 제거"""
        if callback in self.data_callbacks:
            self.data_callbacks.remove(callback)
    
    def get_latest_data(self, data_type: str) -> Optional[SensorData]:
        """최신 데이터 조회"""
        history = self.sensor_data_history.get(data_type)
        return history[-1] if history else None
    
    def get_active_alerts(self, store_id: str = None) -> List[MonitoringAlert]:
        """활성 알림 조회"""
        alerts = [alert for alert in self.active_alerts.values() if not alert.resolved]
        
        if store_id:
            alerts = [alert for alert in alerts if alert.store_id == store_id]
        
        return alerts
    
    def resolve_alert(self, alert_id: str) -> bool:
        """알림 해결"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            self.active_alerts[alert_id].resolved_at = datetime.now()
            logger.info(f"알림 해결됨: {alert_id}")
            return True
        return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'is_monitoring': self.is_monitoring,
            'connected_clients': len(self.connected_clients),
            'data_types': list(self.sensor_data_history.keys()),
            'active_alerts': len([a for a in self.active_alerts.values() if not a.resolved]),
            'total_data_points': sum(len(history) for history in self.sensor_data_history.values())
        }

# 전역 인스턴스
real_time_monitoring_service = RealTimeMonitoringService()
