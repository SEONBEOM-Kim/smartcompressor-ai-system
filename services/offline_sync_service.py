#!/usr/bin/env python3
"""
오프라인 데이터 동기화 서비스
Starbucks App을 벤치마킹한 오프라인 데이터 관리 및 동기화
"""

import json
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading
import queue
import time
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """동기화 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DataType(Enum):
    """데이터 타입"""
    DASHBOARD = "dashboard"
    DIAGNOSIS = "diagnosis"
    PAYMENT = "payment"
    NOTIFICATION = "notification"
    SETTINGS = "settings"
    ANALYTICS = "analytics"

@dataclass
class OfflineData:
    """오프라인 데이터 클래스"""
    id: str
    data_type: DataType
    data: Dict[str, Any]
    created_at: datetime
    synced_at: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    priority: int = 1  # 1: 높음, 2: 보통, 3: 낮음
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'id': self.id,
            'data_type': self.data_type.value,
            'data': self.data,
            'created_at': self.created_at.isoformat(),
            'synced_at': self.synced_at.isoformat() if self.synced_at else None,
            'sync_status': self.sync_status.value,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'priority': self.priority
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OfflineData':
        """딕셔너리에서 생성"""
        return cls(
            id=data['id'],
            data_type=DataType(data['data_type']),
            data=data['data'],
            created_at=datetime.fromisoformat(data['created_at']),
            synced_at=datetime.fromisoformat(data['synced_at']) if data['synced_at'] else None,
            sync_status=SyncStatus(data['sync_status']),
            retry_count=data['retry_count'],
            max_retries=data['max_retries'],
            priority=data['priority']
        )

class OfflineDatabase:
    """오프라인 데이터베이스 관리"""
    
    def __init__(self, db_path: str = "offline_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 오프라인 데이터 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS offline_data (
                        id TEXT PRIMARY KEY,
                        data_type TEXT NOT NULL,
                        data TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        synced_at TEXT,
                        sync_status TEXT NOT NULL,
                        retry_count INTEGER DEFAULT 0,
                        max_retries INTEGER DEFAULT 3,
                        priority INTEGER DEFAULT 1
                    )
                ''')
                
                # 동기화 히스토리 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sync_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data_id TEXT NOT NULL,
                        sync_attempted_at TEXT NOT NULL,
                        sync_status TEXT NOT NULL,
                        error_message TEXT,
                        FOREIGN KEY (data_id) REFERENCES offline_data (id)
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sync_status ON offline_data (sync_status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_type ON offline_data (data_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON offline_data (priority)')
                
                conn.commit()
                logger.info("오프라인 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def save_offline_data(self, offline_data: OfflineData) -> bool:
        """오프라인 데이터 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO offline_data 
                    (id, data_type, data, created_at, synced_at, sync_status, retry_count, max_retries, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    offline_data.id,
                    offline_data.data_type.value,
                    json.dumps(offline_data.data),
                    offline_data.created_at.isoformat(),
                    offline_data.synced_at.isoformat() if offline_data.synced_at else None,
                    offline_data.sync_status.value,
                    offline_data.retry_count,
                    offline_data.max_retries,
                    offline_data.priority
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"오프라인 데이터 저장 실패: {e}")
            return False
    
    def get_pending_data(self, limit: int = 100) -> List[OfflineData]:
        """동기화 대기 중인 데이터 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM offline_data 
                    WHERE sync_status = ? 
                    ORDER BY priority ASC, created_at ASC 
                    LIMIT ?
                ''', (SyncStatus.PENDING.value, limit))
                
                rows = cursor.fetchall()
                offline_data_list = []
                
                for row in rows:
                    offline_data = OfflineData(
                        id=row[0],
                        data_type=DataType(row[1]),
                        data=json.loads(row[2]),
                        created_at=datetime.fromisoformat(row[3]),
                        synced_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        sync_status=SyncStatus(row[5]),
                        retry_count=row[6],
                        max_retries=row[7],
                        priority=row[8]
                    )
                    offline_data_list.append(offline_data)
                
                return offline_data_list
                
        except Exception as e:
            logger.error(f"대기 중인 데이터 조회 실패: {e}")
            return []
    
    def update_sync_status(self, data_id: str, status: SyncStatus, error_message: str = None) -> bool:
        """동기화 상태 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 상태 업데이트
                synced_at = datetime.now().isoformat() if status == SyncStatus.COMPLETED else None
                
                cursor.execute('''
                    UPDATE offline_data 
                    SET sync_status = ?, synced_at = ?, retry_count = retry_count + 1
                    WHERE id = ?
                ''', (status.value, synced_at, data_id))
                
                # 히스토리 기록
                cursor.execute('''
                    INSERT INTO sync_history (data_id, sync_attempted_at, sync_status, error_message)
                    VALUES (?, ?, ?, ?)
                ''', (data_id, datetime.now().isoformat(), status.value, error_message))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"동기화 상태 업데이트 실패: {e}")
            return False
    
    def delete_synced_data(self, older_than_days: int = 7) -> int:
        """동기화된 오래된 데이터 삭제"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
                
                cursor.execute('''
                    DELETE FROM offline_data 
                    WHERE sync_status = ? AND synced_at < ?
                ''', (SyncStatus.COMPLETED.value, cutoff_date))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"동기화된 오래된 데이터 {deleted_count}개 삭제")
                return deleted_count
                
        except Exception as e:
            logger.error(f"오래된 데이터 삭제 실패: {e}")
            return 0
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """동기화 통계 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 전체 통계
                cursor.execute('SELECT COUNT(*) FROM offline_data')
                total_count = cursor.fetchone()[0]
                
                # 상태별 통계
                cursor.execute('''
                    SELECT sync_status, COUNT(*) 
                    FROM offline_data 
                    GROUP BY sync_status
                ''')
                status_counts = dict(cursor.fetchall())
                
                # 타입별 통계
                cursor.execute('''
                    SELECT data_type, COUNT(*) 
                    FROM offline_data 
                    GROUP BY data_type
                ''')
                type_counts = dict(cursor.fetchall())
                
                return {
                    'total_count': total_count,
                    'status_counts': status_counts,
                    'type_counts': type_counts,
                    'pending_count': status_counts.get(SyncStatus.PENDING.value, 0),
                    'completed_count': status_counts.get(SyncStatus.COMPLETED.value, 0),
                    'failed_count': status_counts.get(SyncStatus.FAILED.value, 0)
                }
                
        except Exception as e:
            logger.error(f"동기화 통계 조회 실패: {e}")
            return {}

class OfflineSyncService:
    """오프라인 동기화 서비스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.db = OfflineDatabase()
        self.sync_queue = queue.PriorityQueue()
        self.sync_thread = None
        self.is_running = False
        self.sync_interval = 30  # 30초마다 동기화 시도
        self.max_concurrent_syncs = 3
        
        # API 엔드포인트 매핑
        self.api_endpoints = {
            DataType.DASHBOARD: '/api/dashboard/summary',
            DataType.DIAGNOSIS: '/api/ai/analyze',
            DataType.PAYMENT: '/api/payment/process',
            DataType.NOTIFICATION: '/api/notifications/send',
            DataType.SETTINGS: '/api/settings/update',
            DataType.ANALYTICS: '/api/analytics/track-event'
        }
    
    def start_sync_service(self):
        """동기화 서비스 시작"""
        if self.is_running:
            logger.warning("동기화 서비스가 이미 실행 중입니다")
            return
        
        self.is_running = True
        self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
        self.sync_thread.start()
        logger.info("오프라인 동기화 서비스 시작")
    
    def stop_sync_service(self):
        """동기화 서비스 중지"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("오프라인 동기화 서비스 중지")
    
    def _sync_worker(self):
        """동기화 워커 스레드"""
        while self.is_running:
            try:
                # 대기 중인 데이터 조회
                pending_data = self.db.get_pending_data(limit=50)
                
                if pending_data:
                    logger.info(f"동기화 대기 중인 데이터 {len(pending_data)}개 발견")
                    
                    # 동기화 실행
                    asyncio.run(self._sync_data_batch(pending_data))
                
                # 다음 동기화까지 대기
                time.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"동기화 워커 오류: {e}")
                time.sleep(5)  # 오류 시 5초 대기
    
    async def _sync_data_batch(self, data_list: List[OfflineData]):
        """데이터 배치 동기화"""
        tasks = []
        
        for data in data_list:
            if data.retry_count >= data.max_retries:
                logger.warning(f"최대 재시도 횟수 초과: {data.id}")
                self.db.update_sync_status(data.id, SyncStatus.FAILED, "최대 재시도 횟수 초과")
                continue
            
            task = asyncio.create_task(self._sync_single_data(data))
            tasks.append(task)
            
            # 동시 동기화 수 제한
            if len(tasks) >= self.max_concurrent_syncs:
                await asyncio.gather(*tasks, return_exceptions=True)
                tasks = []
        
        # 남은 작업 처리
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _sync_single_data(self, offline_data: OfflineData) -> bool:
        """단일 데이터 동기화"""
        try:
            # 상태를 진행 중으로 변경
            self.db.update_sync_status(offline_data.id, SyncStatus.IN_PROGRESS)
            
            # API 엔드포인트 확인
            endpoint = self.api_endpoints.get(offline_data.data_type)
            if not endpoint:
                raise ValueError(f"지원하지 않는 데이터 타입: {offline_data.data_type}")
            
            # API 호출
            url = f"{self.base_url}{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=offline_data.data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status in [200, 201]:
                        # 성공
                        self.db.update_sync_status(offline_data.id, SyncStatus.COMPLETED)
                        logger.info(f"데이터 동기화 성공: {offline_data.id}")
                        return True
                    else:
                        # 실패
                        error_text = await response.text()
                        self.db.update_sync_status(
                            offline_data.id, 
                            SyncStatus.FAILED, 
                            f"HTTP {response.status}: {error_text}"
                        )
                        logger.error(f"데이터 동기화 실패: {offline_data.id} - {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            self.db.update_sync_status(offline_data.id, SyncStatus.FAILED, "요청 시간 초과")
            logger.error(f"데이터 동기화 시간 초과: {offline_data.id}")
            return False
        except Exception as e:
            self.db.update_sync_status(offline_data.id, SyncStatus.FAILED, str(e))
            logger.error(f"데이터 동기화 오류: {offline_data.id} - {e}")
            return False
    
    def save_offline_data(self, 
                         data_type: DataType, 
                         data: Dict[str, Any], 
                         priority: int = 1) -> str:
        """오프라인 데이터 저장"""
        try:
            data_id = f"offline_{int(datetime.now().timestamp() * 1000)}_{data_type.value}"
            
            offline_data = OfflineData(
                id=data_id,
                data_type=data_type,
                data=data,
                created_at=datetime.now(),
                priority=priority
            )
            
            success = self.db.save_offline_data(offline_data)
            
            if success:
                logger.info(f"오프라인 데이터 저장 완료: {data_id}")
                return data_id
            else:
                logger.error(f"오프라인 데이터 저장 실패: {data_id}")
                return None
                
        except Exception as e:
            logger.error(f"오프라인 데이터 저장 오류: {e}")
            return None
    
    def get_offline_data(self, data_type: DataType = None) -> List[OfflineData]:
        """오프라인 데이터 조회"""
        try:
            with sqlite3.connect(self.db.db_path) as conn:
                cursor = conn.cursor()
                
                if data_type:
                    cursor.execute('''
                        SELECT * FROM offline_data 
                        WHERE data_type = ? 
                        ORDER BY created_at DESC
                    ''', (data_type.value,))
                else:
                    cursor.execute('''
                        SELECT * FROM offline_data 
                        ORDER BY created_at DESC
                    ''')
                
                rows = cursor.fetchall()
                offline_data_list = []
                
                for row in rows:
                    offline_data = OfflineData(
                        id=row[0],
                        data_type=DataType(row[1]),
                        data=json.loads(row[2]),
                        created_at=datetime.fromisoformat(row[3]),
                        synced_at=datetime.fromisoformat(row[4]) if row[4] else None,
                        sync_status=SyncStatus(row[5]),
                        retry_count=row[6],
                        max_retries=row[7],
                        priority=row[8]
                    )
                    offline_data_list.append(offline_data)
                
                return offline_data_list
                
        except Exception as e:
            logger.error(f"오프라인 데이터 조회 실패: {e}")
            return []
    
    def force_sync(self) -> Dict[str, Any]:
        """강제 동기화 실행"""
        try:
            pending_data = self.db.get_pending_data(limit=100)
            
            if not pending_data:
                return {
                    'success': True,
                    'message': '동기화할 데이터가 없습니다',
                    'synced_count': 0
                }
            
            # 동기화 실행
            asyncio.run(self._sync_data_batch(pending_data))
            
            # 결과 조회
            stats = self.db.get_sync_statistics()
            
            return {
                'success': True,
                'message': f'{len(pending_data)}개 데이터 동기화 완료',
                'synced_count': len(pending_data),
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"강제 동기화 실패: {e}")
            return {
                'success': False,
                'message': f'동기화 실패: {str(e)}',
                'synced_count': 0
            }
    
    def clear_old_data(self, older_than_days: int = 7) -> int:
        """오래된 데이터 정리"""
        return self.db.delete_synced_data(older_than_days)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """동기화 상태 조회"""
        stats = self.db.get_sync_statistics()
        
        return {
            'is_running': self.is_running,
            'sync_interval': self.sync_interval,
            'max_concurrent_syncs': self.max_concurrent_syncs,
            'statistics': stats
        }

# 전역 인스턴스
offline_sync_service = OfflineSyncService()
