#!/usr/bin/env python3
"""
센서 데이터 수집 서비스
Tesla와 Nest 스타일의 실시간 센서 데이터 처리 시스템
"""

import asyncio
import json
import time
import logging
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import deque
import numpy as np
from scipy import signal
import websockets
import websockets.exceptions
# import sqlite3
import queue

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SensorReading:
    """센서 측정값 데이터 클래스"""
    device_id: str
    timestamp: float
    temperature: float
    vibration_x: float
    vibration_y: float
    vibration_z: float
    power_consumption: float
    audio_level: int
    sensor_quality: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class AnomalyDetection:
    """이상 감지 결과"""
    device_id: str
    timestamp: float
    anomaly_type: str
    severity: str  # low, medium, high, critical
    confidence: float
    description: str
    sensor_data: Dict

class SensorDataProcessor:
    """센서 데이터 처리기 (Tesla 스타일)"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_windows = {}  # device_id -> deque
        self.baseline_data = {}  # device_id -> baseline values
        self.anomaly_thresholds = {
            'temperature': {'low': -25, 'high': 5, 'critical': 10},
            'vibration': {'low': 0.5, 'high': 2.0, 'critical': 5.0},
            'power': {'low': 10, 'high': 80, 'critical': 95},
            'audio': {'low': 100, 'high': 1000, 'critical': 2000}
        }
    
    def add_reading(self, reading: SensorReading) -> List[AnomalyDetection]:
        """센서 데이터 추가 및 이상 감지"""
        device_id = reading.device_id
        
        # 데이터 윈도우 관리
        if device_id not in self.data_windows:
            self.data_windows[device_id] = deque(maxlen=self.window_size)
        
        self.data_windows[device_id].append(reading)
        
        # 이상 감지 수행
        anomalies = self._detect_anomalies(reading)
        
        return anomalies
    
    def _detect_anomalies(self, reading: SensorReading) -> List[AnomalyDetection]:
        """이상 감지 로직 (Tesla 스타일)"""
        anomalies = []
        device_id = reading.device_id
        
        # 온도 이상 감지
        temp_anomaly = self._check_temperature_anomaly(reading)
        if temp_anomaly:
            anomalies.append(temp_anomaly)
        
        # 진동 이상 감지
        vibration_anomaly = self._check_vibration_anomaly(reading)
        if vibration_anomaly:
            anomalies.append(vibration_anomaly)
        
        # 전력 이상 감지
        power_anomaly = self._check_power_anomaly(reading)
        if power_anomaly:
            anomalies.append(power_anomaly)
        
        # 오디오 이상 감지
        audio_anomaly = self._check_audio_anomaly(reading)
        if audio_anomaly:
            anomalies.append(audio_anomaly)
        
        # 패턴 기반 이상 감지
        pattern_anomaly = self._check_pattern_anomaly(reading)
        if pattern_anomaly:
            anomalies.append(pattern_anomaly)
        
        return anomalies
    
    def _check_temperature_anomaly(self, reading: SensorReading) -> Optional[AnomalyDetection]:
        """온도 이상 감지"""
        temp = reading.temperature
        thresholds = self.anomaly_thresholds['temperature']
        
        if temp > thresholds['critical']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='temperature_critical',
                severity='critical',
                confidence=0.95,
                description=f'냉동고 온도가 위험 수준입니다: {temp:.1f}°C',
                sensor_data={'temperature': temp}
            )
        elif temp > thresholds['high']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='temperature_high',
                severity='high',
                confidence=0.8,
                description=f'냉동고 온도가 높습니다: {temp:.1f}°C',
                sensor_data={'temperature': temp}
            )
        elif temp < thresholds['low']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='temperature_low',
                severity='medium',
                confidence=0.7,
                description=f'냉동고 온도가 낮습니다: {temp:.1f}°C',
                sensor_data={'temperature': temp}
            )
        
        return None
    
    def _check_vibration_anomaly(self, reading: SensorReading) -> Optional[AnomalyDetection]:
        """진동 이상 감지"""
        vibration_magnitude = np.sqrt(
            reading.vibration_x**2 + 
            reading.vibration_y**2 + 
            reading.vibration_z**2
        )
        thresholds = self.anomaly_thresholds['vibration']
        
        if vibration_magnitude > thresholds['critical']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='vibration_critical',
                severity='critical',
                confidence=0.9,
                description=f'압축기 진동이 위험 수준입니다: {vibration_magnitude:.2f}g',
                sensor_data={
                    'vibration_x': reading.vibration_x,
                    'vibration_y': reading.vibration_y,
                    'vibration_z': reading.vibration_z,
                    'magnitude': vibration_magnitude
                }
            )
        elif vibration_magnitude > thresholds['high']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='vibration_high',
                severity='high',
                confidence=0.75,
                description=f'압축기 진동이 높습니다: {vibration_magnitude:.2f}g',
                sensor_data={
                    'vibration_x': reading.vibration_x,
                    'vibration_y': reading.vibration_y,
                    'vibration_z': reading.vibration_z,
                    'magnitude': vibration_magnitude
                }
            )
        
        return None
    
    def _check_power_anomaly(self, reading: SensorReading) -> Optional[AnomalyDetection]:
        """전력 이상 감지"""
        power = reading.power_consumption
        thresholds = self.anomaly_thresholds['power']
        
        if power > thresholds['critical']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='power_critical',
                severity='critical',
                confidence=0.9,
                description=f'전력 소비가 위험 수준입니다: {power:.1f}%',
                sensor_data={'power_consumption': power}
            )
        elif power > thresholds['high']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='power_high',
                severity='high',
                confidence=0.8,
                description=f'전력 소비가 높습니다: {power:.1f}%',
                sensor_data={'power_consumption': power}
            )
        
        return None
    
    def _check_audio_anomaly(self, reading: SensorReading) -> Optional[AnomalyDetection]:
        """오디오 이상 감지"""
        audio_level = reading.audio_level
        thresholds = self.anomaly_thresholds['audio']
        
        if audio_level > thresholds['critical']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='audio_critical',
                severity='critical',
                confidence=0.85,
                description=f'압축기 소음이 위험 수준입니다: {audio_level}',
                sensor_data={'audio_level': audio_level}
            )
        elif audio_level > thresholds['high']:
            return AnomalyDetection(
                device_id=reading.device_id,
                timestamp=reading.timestamp,
                anomaly_type='audio_high',
                severity='high',
                confidence=0.7,
                description=f'압축기 소음이 높습니다: {audio_level}',
                sensor_data={'audio_level': audio_level}
            )
        
        return None
    
    def _check_pattern_anomaly(self, reading: SensorReading) -> Optional[AnomalyDetection]:
        """패턴 기반 이상 감지 (고급 분석)"""
        device_id = reading.device_id
        
        if device_id not in self.data_windows or len(self.data_windows[device_id]) < 10:
            return None
        
        # 최근 데이터 윈도우 분석
        recent_data = list(self.data_windows[device_id])[-10:]
        
        # 온도 트렌드 분석
        temperatures = [r.temperature for r in recent_data]
        temp_trend = np.polyfit(range(len(temperatures)), temperatures, 1)[0]
        
        if temp_trend > 0.5:  # 온도가 빠르게 상승
            return AnomalyDetection(
                device_id=device_id,
                timestamp=reading.timestamp,
                anomaly_type='temperature_trend',
                severity='medium',
                confidence=0.6,
                description=f'냉동고 온도가 빠르게 상승하고 있습니다: {temp_trend:.2f}°C/min',
                sensor_data={'temperature_trend': temp_trend}
            )
        
        # 진동 패턴 분석
        vibrations = [np.sqrt(r.vibration_x**2 + r.vibration_y**2 + r.vibration_z**2) for r in recent_data]
        vibration_variance = np.var(vibrations)
        
        if vibration_variance > 2.0:  # 진동이 불규칙
            return AnomalyDetection(
                device_id=device_id,
                timestamp=reading.timestamp,
                anomaly_type='vibration_pattern',
                severity='medium',
                confidence=0.65,
                description=f'압축기 진동이 불규칙합니다: 분산 {vibration_variance:.2f}',
                sensor_data={'vibration_variance': vibration_variance}
            )
        
        return None

class SensorDataService:
    """센서 데이터 수집 서비스 (Nest 스타일)"""
    
    def __init__(self):
        self.conn = None # 데이터베이스 연결 객체 (PostgreSQL)
        self.processor = SensorDataProcessor()
        self.connected_devices = {}
        self.data_queue = queue.Queue()
        self.is_running = False
        self.websocket_server = None
        self.anomaly_callbacks = []
        
        # 워커 스레드 시작
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        logger.info("센서 데이터 서비스 초기화 완료")

    def _init_database(self):
        """데이터베이스 초기화 (SQLite) - PostgreSQL로 마이그레이션 필요"""
        logger.warning("이 함수는 더 이상 사용되지 않습니다. PostgreSQL 연결을 사용해야 합니다.")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 센서 데이터 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensor_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    temperature REAL,
                    vibration_x REAL,
                    vibration_y REAL,
                    vibration_z REAL,
                    power_consumption REAL,
                    audio_level INTEGER,
                    sensor_quality REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 이상 감지 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT,
                    sensor_data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 디바이스 정보 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    device_name TEXT,
                    location TEXT,
                    firmware_version TEXT,
                    hardware_version TEXT,
                    last_seen REAL,
                    status TEXT DEFAULT 'offline',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_device ON sensor_readings(device_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomaly_timestamp ON anomalies(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomaly_device ON anomalies(device_id)')
            
            conn.commit()
            conn.close()
            
            logger.info("데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
        """
        pass

    def add_anomaly_callback(self, callback: Callable[[AnomalyDetection], None]):
        """이상 감지 콜백 추가"""
        self.anomaly_callbacks.append(callback)
    
    def start_websocket_server(self, host: str = '0.0.0.0', port: int = 8080):
        """WebSocket 서버 시작"""
        async def handle_client(websocket, path):
            client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            logger.info(f"클라이언트 연결: {client_id}")
            
            try:
                async for message in websocket:
                    await self._handle_websocket_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"클라이언트 연결 끊김: {client_id}")
            except Exception as e:
                logger.error(f"WebSocket 오류: {e}")
        
        async def start_server():
            self.websocket_server = await websockets.serve(handle_client, host, port)
            logger.info(f"WebSocket 서버 시작: {host}:{port}")
        
        # 이벤트 루프에서 서버 시작
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_server())
        loop.run_forever()
    
    async def _handle_websocket_message(self, websocket, message: str):
        """WebSocket 메시지 처리"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'sensor_data':
                await self._handle_sensor_data(websocket, data)
            elif message_type == 'device_info':
                await self._handle_device_info(websocket, data)
            elif message_type == 'heartbeat':
                await self._handle_heartbeat(websocket, data)
            else:
                logger.warning(f"알 수 없는 메시지 타입: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
    
    async def _handle_sensor_data(self, websocket, data: Dict):
        """센서 데이터 처리"""
        try:
            # 센서 데이터 객체 생성
            reading = SensorReading(
                device_id=data['device_id'],
                timestamp=data['timestamp'],
                temperature=data['temperature'],
                vibration_x=data['vibration']['x'],
                vibration_y=data['vibration']['y'],
                vibration_z=data['vibration']['z'],
                power_consumption=data['power_consumption'],
                audio_level=data['audio_level']
            )
            
            # 데이터 큐에 추가
            self.data_queue.put(('sensor_data', reading))
            
            # 실시간 응답
            response = {
                'type': 'sensor_data_received',
                'device_id': reading.device_id,
                'timestamp': reading.timestamp,
                'status': 'success'
            }
            
            await websocket.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"센서 데이터 처리 오류: {e}")
            error_response = {
                'type': 'error',
                'message': str(e)
            }
            await websocket.send(json.dumps(error_response))
    
    async def _handle_device_info(self, websocket, data: Dict):
        """디바이스 정보 처리"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            device_id = data['device_id']
            
            # 디바이스 정보 저장
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO devices 
                (device_id, device_name, firmware_version, hardware_version, last_seen, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                device_id,
                data.get('device_name', 'Unknown'),
                data.get('firmware_version', 'Unknown'),
                data.get('hardware_version', 'Unknown'),
                time.time(),
                'online'
            ))
            
            conn.commit()
            conn.close()
            
            # 연결된 디바이스에 추가
            self.connected_devices[device_id] = {
                'websocket': websocket,
                'last_seen': time.time(),
                'info': data
            }
            
            logger.info(f"디바이스 등록: {device_id}")
            
        except Exception as e:
            logger.error(f"디바이스 정보 처리 오류: {e}")
        """
        pass

    async def _handle_heartbeat(self, websocket, data: Dict):
        """하트비트 처리"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            device_id = data['device_id']
            
            if device_id in self.connected_devices:
                self.connected_devices[device_id]['last_seen'] = time.time()
                
                # 디바이스 상태 업데이트
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE devices 
                    SET last_seen = ?, status = 'online'
                    WHERE device_id = ?
                ''', (time.time(), device_id))
                
                conn.commit()
                conn.close()
            
        except Exception as e:
            logger.error(f"하트비트 처리 오류: {e}")
        """
        pass

    def _worker_loop(self):
        """데이터 처리 워커 루프"""
        self.is_running = True
        
        while self.is_running:
            try:
                # 큐에서 데이터 가져오기
                item = self.data_queue.get(timeout=1)
                data_type, data = item
                
                if data_type == 'sensor_data':
                    self._process_sensor_data(data)
                
                self.data_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"워커 루프 오류: {e}")
    
    def _process_sensor_data(self, reading: SensorReading):
        """센서 데이터 처리"""
        try:
            # 이상 감지
            anomalies = self.processor.add_reading(reading)
            
            # 데이터베이스에 저장
            self._save_sensor_reading(reading)
            
            # 이상 감지 결과 처리
            for anomaly in anomalies:
                self._save_anomaly(anomaly)
                self._notify_anomaly(anomaly)
            
        except Exception as e:
            logger.error(f"센서 데이터 처리 오류: {e}")
    
    def _save_sensor_reading(self, reading: SensorReading):
        """센서 데이터 저장"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sensor_readings 
                (device_id, timestamp, temperature, vibration_x, vibration_y, vibration_z, 
                 power_consumption, audio_level, sensor_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                reading.device_id,
                reading.timestamp,
                reading.temperature,
                reading.vibration_x,
                reading.vibration_y,
                reading.vibration_z,
                reading.power_consumption,
                reading.audio_level,
                reading.sensor_quality
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"센서 데이터 저장 오류: {e}")
        """
        pass

    def _save_anomaly(self, anomaly: AnomalyDetection):
        """이상 감지 결과 저장"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO anomalies 
                (device_id, timestamp, anomaly_type, severity, confidence, description, sensor_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                anomaly.device_id,
                anomaly.timestamp,
                anomaly.anomaly_type,
                anomaly.severity,
                anomaly.confidence,
                anomaly.description,
                json.dumps(anomaly.sensor_data)
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"이상 감지 저장: {anomaly.anomaly_type} - {anomaly.description}")
            
        except Exception as e:
            logger.error(f"이상 감지 저장 오류: {e}")
        """
        pass

    def _notify_anomaly(self, anomaly: AnomalyDetection):
        """이상 감지 알림"""
        try:
            # 콜백 함수들 호출
            for callback in self.anomaly_callbacks:
                try:
                    callback(anomaly)
                except Exception as e:
                    logger.error(f"이상 감지 콜백 오류: {e}")
            
            # 실시간 WebSocket 알림
            self._broadcast_anomaly(anomaly)
            
        except Exception as e:
            logger.error(f"이상 감지 알림 오류: {e}")
    
    def _broadcast_anomaly(self, anomaly: AnomalyDetection):
        """이상 감지 결과 브로드캐스트"""
        try:
            message = {
                'type': 'anomaly_detected',
                'data': {
                    'device_id': anomaly.device_id,
                    'timestamp': anomaly.timestamp,
                    'anomaly_type': anomaly.anomaly_type,
                    'severity': anomaly.severity,
                    'confidence': anomaly.confidence,
                    'description': anomaly.description,
                    'sensor_data': anomaly.sensor_data
                }
            }
            
            # 연결된 모든 클라이언트에 전송
            for device_id, device_info in self.connected_devices.items():
                try:
                    websocket = device_info['websocket']
                    asyncio.create_task(websocket.send(json.dumps(message)))
                except Exception as e:
                    logger.error(f"브로드캐스트 오류: {e}")
                    
        except Exception as e:
            logger.error(f"이상 감지 브로드캐스트 오류: {e}")
    
    def get_device_status(self) -> Dict:
        """디바이스 상태 조회"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT device_id, device_name, status, last_seen, firmware_version
                FROM devices
                ORDER BY last_seen DESC
            ''')
            
            devices = []
            for row in cursor.fetchall():
                devices.append({
                    'device_id': row[0],
                    'device_name': row[1],
                    'status': row[2],
                    'last_seen': row[3],
                    'firmware_version': row[4],
                    'is_online': time.time() - row[3] < 300  # 5분 이내
                })
            
            conn.close()
            
            return {
                'total_devices': len(devices),
                'online_devices': len([d for d in devices if d['is_online']]),
                'devices': devices
            }
            
        except Exception as e:
            logger.error(f"디바이스 상태 조회 오류: {e}")
            return {'error': str(e)}
        """
        return {'error': '데이터베이스 연결이 구현되지 않았습니다.'}

    def get_sensor_data(self, device_id: str, hours: int = 24) -> List[Dict]:
        """센서 데이터 조회"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_timestamp = time.time() - (hours * 3600)
            
            cursor.execute('''
                SELECT * FROM sensor_readings 
                WHERE device_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 1000
            ''', (device_id, since_timestamp))
            
            data = []
            for row in cursor.fetchall():
                data.append({
                    'id': row[0],
                    'device_id': row[1],
                    'timestamp': row[2],
                    'temperature': row[3],
                    'vibration_x': row[4],
                    'vibration_y': row[5],
                    'vibration_z': row[6],
                    'power_consumption': row[7],
                    'audio_level': row[8],
                    'sensor_quality': row[9],
                    'created_at': row[10]
                })
            
            conn.close()
            return data
            
        except Exception as e:
            logger.error(f"센서 데이터 조회 오류: {e}")
            return []
        """
        return []

    def get_anomalies(self, device_id: str = None, hours: int = 24) -> List[Dict]:
        """이상 감지 결과 조회"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_timestamp = time.time() - (hours * 3600)
            
            if device_id:
                cursor.execute('''
                    SELECT * FROM anomalies 
                    WHERE device_id = ? AND timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''', (device_id, since_timestamp))
            else:
                cursor.execute('''
                    SELECT * FROM anomalies 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                ''', (since_timestamp,))
            
            anomalies = []
            for row in cursor.fetchall():
                anomalies.append({
                    'id': row[0],
                    'device_id': row[1],
                    'timestamp': row[2],
                    'anomaly_type': row[3],
                    'severity': row[4],
                    'confidence': row[5],
                    'description': row[6],
                    'sensor_data': json.loads(row[7]) if row[7] else {},
                    'created_at': row[8]
                })
            
            conn.close()
            return anomalies
            
        except Exception as e:
            logger.error(f"이상 감지 결과 조회 오류: {e}")
            return []
        """
        return []

    def stop(self):
        """서비스 중지"""
        self.is_running = False
        if self.websocket_server:
            self.websocket_server.close()
        logger.info("센서 데이터 서비스 중지")

# 전역 서비스 인스턴스
sensor_data_service = SensorDataService()
