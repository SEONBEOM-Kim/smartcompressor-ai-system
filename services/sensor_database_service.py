#!/usr/bin/env python3
"""
센서 데이터베이스 서비스
Nest 스타일의 시계열 데이터 저장 및 관리
"""

import os
import json
import time
import logging
import sqlite3
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict
import queue

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorDatabaseService:
    """센서 데이터베이스 서비스 (Nest 스타일)"""
    
    def __init__(self, db_path: str = 'data/sensor_data.db'):
        self.db_path = db_path
        self.db_lock = threading.Lock()
        self.batch_queue = queue.Queue()
        self.batch_size = 100
        self.batch_timeout = 5.0  # 5초
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 배치 처리 스레드 시작
        self.batch_thread = threading.Thread(target=self._batch_processor, daemon=True)
        self.batch_thread.start()
        
        logger.info("센서 데이터베이스 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 센서 데이터 테이블 (시계열 데이터)
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
                
                # 센서 통계 테이블 (집계 데이터)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sensor_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        device_id TEXT NOT NULL,
                        date TEXT NOT NULL,
                        hour INTEGER NOT NULL,
                        avg_temperature REAL,
                        max_temperature REAL,
                        min_temperature REAL,
                        avg_vibration REAL,
                        max_vibration REAL,
                        avg_power_consumption REAL,
                        max_power_consumption REAL,
                        anomaly_count INTEGER DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(device_id, date, hour)
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_device ON sensor_readings(device_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sensor_device_timestamp ON sensor_readings(device_id, timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomaly_timestamp ON anomalies(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomaly_device ON anomalies(device_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_anomaly_type ON anomalies(anomaly_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_statistics_device_date ON sensor_statistics(device_id, date)')
                
                conn.commit()
                conn.close()
                
                logger.info("데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def add_sensor_reading(self, reading_data: Dict):
        """센서 데이터 추가 (배치 처리)"""
        try:
            self.batch_queue.put(('sensor_reading', reading_data))
        except Exception as e:
            logger.error(f"센서 데이터 추가 실패: {e}")
    
    def add_anomaly(self, anomaly_data: Dict):
        """이상 감지 결과 추가 (즉시 처리)"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO anomalies 
                    (device_id, timestamp, anomaly_type, severity, confidence, description, sensor_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    anomaly_data['device_id'],
                    anomaly_data['timestamp'],
                    anomaly_data['anomaly_type'],
                    anomaly_data['severity'],
                    anomaly_data['confidence'],
                    anomaly_data['description'],
                    json.dumps(anomaly_data['sensor_data'])
                ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"이상 감지 결과 저장: {anomaly_data['anomaly_type']}")
                
        except Exception as e:
            logger.error(f"이상 감지 결과 저장 실패: {e}")
    
    def update_device_info(self, device_info: Dict):
        """디바이스 정보 업데이트"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO devices 
                    (device_id, device_name, location, firmware_version, hardware_version, last_seen, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device_info['device_id'],
                    device_info.get('device_name', 'Unknown'),
                    device_info.get('location', 'Unknown'),
                    device_info.get('firmware_version', 'Unknown'),
                    device_info.get('hardware_version', 'Unknown'),
                    device_info.get('last_seen', time.time()),
                    device_info.get('status', 'online')
                ))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            logger.error(f"디바이스 정보 업데이트 실패: {e}")
    
    def _batch_processor(self):
        """배치 처리 스레드"""
        batch_data = []
        last_process_time = time.time()
        
        while True:
            try:
                # 큐에서 데이터 가져오기
                try:
                    item = self.batch_queue.get(timeout=1)
                    batch_data.append(item)
                except queue.Empty:
                    pass
                
                current_time = time.time()
                
                # 배치 크기 또는 시간 초과 시 처리
                if (len(batch_data) >= self.batch_size or 
                    (batch_data and current_time - last_process_time >= self.batch_timeout)):
                    
                    if batch_data:
                        self._process_batch(batch_data)
                        batch_data = []
                        last_process_time = current_time
                
            except Exception as e:
                logger.error(f"배치 처리 오류: {e}")
                time.sleep(1)
    
    def _process_batch(self, batch_data: List[Tuple]):
        """배치 데이터 처리"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                for item_type, data in batch_data:
                    if item_type == 'sensor_reading':
                        cursor.execute('''
                            INSERT INTO sensor_readings 
                            (device_id, timestamp, temperature, vibration_x, vibration_y, vibration_z, 
                             power_consumption, audio_level, sensor_quality)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            data['device_id'],
                            data['timestamp'],
                            data['temperature'],
                            data['vibration_x'],
                            data['vibration_y'],
                            data['vibration_z'],
                            data['power_consumption'],
                            data['audio_level'],
                            data.get('sensor_quality', 1.0)
                        ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"배치 처리 완료: {len(batch_data)}개 항목")
                
        except Exception as e:
            logger.error(f"배치 처리 실패: {e}")
    
    def get_sensor_data(self, device_id: str, start_time: float = None, 
                       end_time: float = None, limit: int = 1000) -> List[Dict]:
        """센서 데이터 조회"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 기본 시간 범위 설정
                if start_time is None:
                    start_time = time.time() - (24 * 3600)  # 24시간 전
                if end_time is None:
                    end_time = time.time()
                
                cursor.execute('''
                    SELECT * FROM sensor_readings 
                    WHERE device_id = ? AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (device_id, start_time, end_time, limit))
                
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
            logger.error(f"센서 데이터 조회 실패: {e}")
            return []
    
    def get_anomalies(self, device_id: str = None, start_time: float = None, 
                     end_time: float = None, limit: int = 100) -> List[Dict]:
        """이상 감지 결과 조회"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 기본 시간 범위 설정
                if start_time is None:
                    start_time = time.time() - (24 * 3600)  # 24시간 전
                if end_time is None:
                    end_time = time.time()
                
                if device_id:
                    cursor.execute('''
                        SELECT * FROM anomalies 
                        WHERE device_id = ? AND timestamp BETWEEN ? AND ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (device_id, start_time, end_time, limit))
                else:
                    cursor.execute('''
                        SELECT * FROM anomalies 
                        WHERE timestamp BETWEEN ? AND ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (start_time, end_time, limit))
                
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
            logger.error(f"이상 감지 결과 조회 실패: {e}")
            return []
    
    def get_device_status(self) -> List[Dict]:
        """디바이스 상태 조회"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT device_id, device_name, status, last_seen, firmware_version
                    FROM devices
                    ORDER BY last_seen DESC
                ''')
                
                devices = []
                current_time = time.time()
                
                for row in cursor.fetchall():
                    devices.append({
                        'device_id': row[0],
                        'device_name': row[1],
                        'status': row[2],
                        'last_seen': row[3],
                        'firmware_version': row[4],
                        'is_online': current_time - row[3] < 300  # 5분 이내
                    })
                
                conn.close()
                return devices
                
        except Exception as e:
            logger.error(f"디바이스 상태 조회 실패: {e}")
            return []
    
    def get_statistics(self, device_id: str, date: str = None) -> Dict:
        """센서 통계 조회"""
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 일별 통계 조회
                cursor.execute('''
                    SELECT 
                        AVG(temperature) as avg_temp,
                        MAX(temperature) as max_temp,
                        MIN(temperature) as min_temp,
                        AVG(SQRT(vibration_x*vibration_x + vibration_y*vibration_y + vibration_z*vibration_z)) as avg_vibration,
                        MAX(SQRT(vibration_x*vibration_x + vibration_y*vibration_y + vibration_z*vibration_z)) as max_vibration,
                        AVG(power_consumption) as avg_power,
                        MAX(power_consumption) as max_power,
                        COUNT(*) as total_readings
                    FROM sensor_readings 
                    WHERE device_id = ? AND DATE(datetime(timestamp, 'unixepoch')) = ?
                ''', (device_id, date))
                
                stats = cursor.fetchone()
                
                # 이상 감지 수 조회
                cursor.execute('''
                    SELECT COUNT(*) as anomaly_count
                    FROM anomalies 
                    WHERE device_id = ? AND DATE(datetime(timestamp, 'unixepoch')) = ?
                ''', (device_id, date))
                
                anomaly_count = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'device_id': device_id,
                    'date': date,
                    'avg_temperature': stats[0] if stats[0] else 0,
                    'max_temperature': stats[1] if stats[1] else 0,
                    'min_temperature': stats[2] if stats[2] else 0,
                    'avg_vibration': stats[3] if stats[3] else 0,
                    'max_vibration': stats[4] if stats[4] else 0,
                    'avg_power_consumption': stats[5] if stats[5] else 0,
                    'max_power_consumption': stats[6] if stats[6] else 0,
                    'total_readings': stats[7] if stats[7] else 0,
                    'anomaly_count': anomaly_count
                }
                
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}
    
    def generate_hourly_statistics(self, device_id: str, date: str = None):
        """시간별 통계 생성"""
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 시간별 통계 생성
                for hour in range(24):
                    start_timestamp = datetime.strptime(f"{date} {hour:02d}:00:00", '%Y-%m-%d %H:%M:%S').timestamp()
                    end_timestamp = start_timestamp + 3600
                    
                    # 센서 데이터 통계
                    cursor.execute('''
                        SELECT 
                            AVG(temperature) as avg_temp,
                            MAX(temperature) as max_temp,
                            MIN(temperature) as min_temp,
                            AVG(SQRT(vibration_x*vibration_x + vibration_y*vibration_y + vibration_z*vibration_z)) as avg_vibration,
                            MAX(SQRT(vibration_x*vibration_x + vibration_y*vibration_y + vibration_z*vibration_z)) as max_vibration,
                            AVG(power_consumption) as avg_power,
                            MAX(power_consumption) as max_power
                        FROM sensor_readings 
                        WHERE device_id = ? AND timestamp BETWEEN ? AND ?
                    ''', (device_id, start_timestamp, end_timestamp))
                    
                    stats = cursor.fetchone()
                    
                    # 이상 감지 수
                    cursor.execute('''
                        SELECT COUNT(*) as anomaly_count
                        FROM anomalies 
                        WHERE device_id = ? AND timestamp BETWEEN ? AND ?
                    ''', (device_id, start_timestamp, end_timestamp))
                    
                    anomaly_count = cursor.fetchone()[0]
                    
                    # 통계 저장
                    cursor.execute('''
                        INSERT OR REPLACE INTO sensor_statistics 
                        (device_id, date, hour, avg_temperature, max_temperature, min_temperature,
                         avg_vibration, max_vibration, avg_power_consumption, max_power_consumption, anomaly_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        device_id, date, hour,
                        stats[0] if stats[0] else 0,
                        stats[1] if stats[1] else 0,
                        stats[2] if stats[2] else 0,
                        stats[3] if stats[3] else 0,
                        stats[4] if stats[4] else 0,
                        stats[5] if stats[5] else 0,
                        stats[6] if stats[6] else 0,
                        anomaly_count
                    ))
                
                conn.commit()
                conn.close()
                
                logger.info(f"시간별 통계 생성 완료: {device_id} - {date}")
                
        except Exception as e:
            logger.error(f"시간별 통계 생성 실패: {e}")
    
    def cleanup_old_data(self, days: int = 30):
        """오래된 데이터 정리"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 오래된 센서 데이터 삭제
                cursor.execute('DELETE FROM sensor_readings WHERE timestamp < ?', (cutoff_time,))
                sensor_deleted = cursor.rowcount
                
                # 오래된 이상 감지 데이터 삭제
                cursor.execute('DELETE FROM anomalies WHERE timestamp < ?', (cutoff_time,))
                anomaly_deleted = cursor.rowcount
                
                conn.commit()
                conn.close()
                
                logger.info(f"데이터 정리 완료: 센서 {sensor_deleted}개, 이상 {anomaly_deleted}개 삭제")
                
        except Exception as e:
            logger.error(f"데이터 정리 실패: {e}")
    
    def get_database_status(self) -> Dict:
        """데이터베이스 상태 조회"""
        try:
            with self.db_lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # 테이블별 레코드 수
                cursor.execute('SELECT COUNT(*) FROM sensor_readings')
                sensor_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM anomalies')
                anomaly_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM devices')
                device_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM sensor_statistics')
                stats_count = cursor.fetchone()[0]
                
                # 데이터베이스 크기
                cursor.execute('SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()')
                db_size = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    'sensor_readings': sensor_count,
                    'anomalies': anomaly_count,
                    'devices': device_count,
                    'statistics': stats_count,
                    'database_size_bytes': db_size,
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'queue_size': self.batch_queue.qsize()
                }
                
        except Exception as e:
            logger.error(f"데이터베이스 상태 조회 실패: {e}")
            return {}

# 전역 서비스 인스턴스
sensor_database_service = SensorDatabaseService()
