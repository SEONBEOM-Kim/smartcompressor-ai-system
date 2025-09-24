#!/usr/bin/env python3
"""
백업 및 복구 시스템
AWS Management Console을 벤치마킹한 백업 및 복구 시스템
"""

import asyncio
import json
import logging
import time
import os
import shutil
import gzip
import tarfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque
import sqlite3
import subprocess
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackupType(Enum):
    """백업 타입"""
    FULL = "full"                 # 전체 백업
    INCREMENTAL = "incremental"   # 증분 백업
    DIFFERENTIAL = "differential" # 차등 백업
    MANUAL = "manual"             # 수동 백업

class BackupStatus(Enum):
    """백업 상태"""
    PENDING = "pending"           # 대기 중
    RUNNING = "running"           # 실행 중
    COMPLETED = "completed"       # 완료
    FAILED = "failed"             # 실패
    CANCELLED = "cancelled"       # 취소됨

class RestoreStatus(Enum):
    """복구 상태"""
    PENDING = "pending"           # 대기 중
    RUNNING = "running"           # 실행 중
    COMPLETED = "completed"       # 완료
    FAILED = "failed"             # 실패
    CANCELLED = "cancelled"       # 취소됨

@dataclass
class BackupJob:
    """백업 작업 클래스"""
    id: str
    name: str
    backup_type: BackupType
    status: BackupStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    file_size: int = 0
    compression_ratio: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RestoreJob:
    """복구 작업 클래스"""
    id: str
    backup_id: str
    status: RestoreStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    target_path: str = ""
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class BackupSchedule:
    """백업 스케줄 클래스"""
    id: str
    name: str
    backup_type: BackupType
    schedule_cron: str
    retention_days: int
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class BackupRecoveryService:
    """백업 및 복구 서비스"""
    
    def __init__(self):
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.restore_jobs: Dict[str, RestoreJob] = {}
        self.backup_schedules: Dict[str, BackupSchedule] = {}
        self.backup_callbacks: List[Callable] = []
        
        # 백업 설정
        self.backup_directory = Path("backups")
        self.backup_directory.mkdir(exist_ok=True)
        
        self.temp_directory = Path("temp")
        self.temp_directory.mkdir(exist_ok=True)
        
        # 백업할 디렉토리 및 파일
        self.backup_targets = {
            'database': 'instance/smartcompressor.db',
            'logs': 'logs/',
            'uploads': 'uploads/',
            'config': 'config/',
            'models': 'models/',
            'services': 'services/',
            'admin': 'admin/'
        }
        
        # 백업 설정
        self.max_backup_files = 10
        self.compression_enabled = True
        self.encryption_enabled = False
        self.retention_days = 30
        
        # 스케줄러 설정
        self.is_scheduler_running = False
        self.scheduler_thread = None
        
        # 초기화
        self._initialize_default_schedules()
        self._start_scheduler()
    
    def _initialize_default_schedules(self):
        """기본 백업 스케줄 초기화"""
        # 일일 전체 백업
        self.backup_schedules["daily_full"] = BackupSchedule(
            id="daily_full",
            name="일일 전체 백업",
            backup_type=BackupType.FULL,
            schedule_cron="0 2 * * *",  # 매일 오전 2시
            retention_days=7
        )
        
        # 주간 전체 백업
        self.backup_schedules["weekly_full"] = BackupSchedule(
            id="weekly_full",
            name="주간 전체 백업",
            backup_type=BackupType.FULL,
            schedule_cron="0 3 * * 0",  # 매주 일요일 오전 3시
            retention_days=30
        )
        
        # 시간별 증분 백업
        self.backup_schedules["hourly_incremental"] = BackupSchedule(
            id="hourly_incremental",
            name="시간별 증분 백업",
            backup_type=BackupType.INCREMENTAL,
            schedule_cron="0 * * * *",  # 매시간
            retention_days=3
        )
    
    def _start_scheduler(self):
        """백업 스케줄러 시작"""
        self.is_scheduler_running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        logger.info("백업 스케줄러 시작")
    
    def _scheduler_worker(self):
        """스케줄러 워커"""
        while self.is_scheduler_running:
            try:
                current_time = datetime.now()
                
                for schedule in self.backup_schedules.values():
                    if not schedule.is_active:
                        continue
                    
                    # 다음 실행 시간 계산 (간단한 구현)
                    if self._should_run_schedule(schedule, current_time):
                        self._execute_scheduled_backup(schedule)
                        schedule.last_run = current_time
                        schedule.next_run = self._calculate_next_run(schedule, current_time)
                
                time.sleep(60)  # 1분마다 체크
                
            except Exception as e:
                logger.error(f"백업 스케줄러 오류: {e}")
                time.sleep(60)
    
    def _should_run_schedule(self, schedule: BackupSchedule, current_time: datetime) -> bool:
        """스케줄 실행 여부 확인"""
        if not schedule.last_run:
            return True
        
        # 간단한 시간 기반 실행 (실제로는 cron 파싱 필요)
        if schedule.schedule_cron == "0 2 * * *":  # 매일 오전 2시
            return (current_time.hour == 2 and 
                    current_time.minute == 0 and 
                    schedule.last_run.date() != current_time.date())
        elif schedule.schedule_cron == "0 3 * * 0":  # 매주 일요일 오전 3시
            return (current_time.weekday() == 6 and 
                    current_time.hour == 3 and 
                    current_time.minute == 0 and
                    schedule.last_run.date() != current_time.date())
        elif schedule.schedule_cron == "0 * * * *":  # 매시간
            return (current_time.minute == 0 and 
                    schedule.last_run.hour != current_time.hour)
        
        return False
    
    def _calculate_next_run(self, schedule: BackupSchedule, current_time: datetime) -> datetime:
        """다음 실행 시간 계산"""
        if schedule.schedule_cron == "0 2 * * *":  # 매일 오전 2시
            return current_time.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif schedule.schedule_cron == "0 3 * * 0":  # 매주 일요일 오전 3시
            days_ahead = 6 - current_time.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return current_time.replace(hour=3, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
        elif schedule.schedule_cron == "0 * * * *":  # 매시간
            return current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        return current_time + timedelta(hours=1)
    
    def _execute_scheduled_backup(self, schedule: BackupSchedule):
        """스케줄된 백업 실행"""
        try:
            backup_name = f"{schedule.name}_{current_time.strftime('%Y%m%d_%H%M%S')}"
            self.create_backup(backup_name, schedule.backup_type)
        except Exception as e:
            logger.error(f"스케줄된 백업 실행 오류: {e}")
    
    def create_backup(self, name: str, backup_type: BackupType, 
                     description: str = None) -> str:
        """백업 생성"""
        try:
            backup_id = f"backup_{int(time.time() * 1000)}"
            
            # 백업 작업 생성
            backup_job = BackupJob(
                id=backup_id,
                name=name,
                backup_type=backup_type,
                status=BackupStatus.PENDING,
                created_at=datetime.now(),
                metadata={
                    'description': description or f"{backup_type.value} 백업",
                    'created_by': 'system'
                }
            )
            
            self.backup_jobs[backup_id] = backup_job
            
            # 백업 실행
            self._execute_backup(backup_job)
            
            return backup_id
            
        except Exception as e:
            logger.error(f"백업 생성 오류: {e}")
            return None
    
    def _execute_backup(self, backup_job: BackupJob):
        """백업 실행"""
        try:
            backup_job.status = BackupStatus.RUNNING
            backup_job.started_at = datetime.now()
            
            # 백업 파일 경로 생성
            timestamp = backup_job.created_at.strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{backup_job.name}_{timestamp}"
            
            if self.compression_enabled:
                backup_filename += ".tar.gz"
            else:
                backup_filename += ".tar"
            
            backup_path = self.backup_directory / backup_filename
            
            # 백업 실행
            if backup_job.backup_type == BackupType.FULL:
                self._create_full_backup(backup_path, backup_job)
            elif backup_job.backup_type == BackupType.INCREMENTAL:
                self._create_incremental_backup(backup_path, backup_job)
            elif backup_job.backup_type == BackupType.DIFFERENTIAL:
                self._create_differential_backup(backup_path, backup_job)
            
            # 백업 완료 처리
            backup_job.status = BackupStatus.COMPLETED
            backup_job.completed_at = datetime.now()
            backup_job.file_path = str(backup_path)
            backup_job.file_size = backup_path.stat().st_size if backup_path.exists() else 0
            
            # 압축률 계산
            if self.compression_enabled:
                original_size = self._calculate_original_size()
                backup_job.compression_ratio = (1 - backup_job.file_size / original_size) * 100 if original_size > 0 else 0
            
            # 콜백 실행
            self._notify_backup_completed(backup_job)
            
            logger.info(f"백업 완료: {backup_job.id} - {backup_job.name}")
            
        except Exception as e:
            backup_job.status = BackupStatus.FAILED
            backup_job.error_message = str(e)
            backup_job.completed_at = datetime.now()
            
            logger.error(f"백업 실행 오류: {e}")
    
    def _create_full_backup(self, backup_path: Path, backup_job: BackupJob):
        """전체 백업 생성"""
        with tarfile.open(backup_path, 'w:gz' if self.compression_enabled else 'w') as tar:
            for target_name, target_path in self.backup_targets.items():
                if os.path.exists(target_path):
                    tar.add(target_path, arcname=target_name)
                    logger.info(f"백업 대상 추가: {target_path}")
    
    def _create_incremental_backup(self, backup_path: Path, backup_job: BackupJob):
        """증분 백업 생성"""
        # 마지막 백업 이후 변경된 파일만 백업
        last_backup_time = self._get_last_backup_time()
        
        with tarfile.open(backup_path, 'w:gz' if self.compression_enabled else 'w') as tar:
            for target_name, target_path in self.backup_targets.items():
                if os.path.exists(target_path):
                    if os.path.isfile(target_path):
                        if os.path.getmtime(target_path) > last_backup_time:
                            tar.add(target_path, arcname=target_name)
                    else:
                        # 디렉토리의 경우 하위 파일들 확인
                        for root, dirs, files in os.walk(target_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                if os.path.getmtime(file_path) > last_backup_time:
                                    tar.add(file_path, arcname=os.path.relpath(file_path, target_path))
    
    def _create_differential_backup(self, backup_path: Path, backup_job: BackupJob):
        """차등 백업 생성"""
        # 마지막 전체 백업 이후 변경된 파일만 백업
        last_full_backup_time = self._get_last_full_backup_time()
        
        with tarfile.open(backup_path, 'w:gz' if self.compression_enabled else 'w') as tar:
            for target_name, target_path in self.backup_targets.items():
                if os.path.exists(target_path):
                    if os.path.isfile(target_path):
                        if os.path.getmtime(target_path) > last_full_backup_time:
                            tar.add(target_path, arcname=target_name)
                    else:
                        # 디렉토리의 경우 하위 파일들 확인
                        for root, dirs, files in os.walk(target_path):
                            for file in files:
                                file_path = os.path.join(root, file)
                                if os.path.getmtime(file_path) > last_full_backup_time:
                                    tar.add(file_path, arcname=os.path.relpath(file_path, target_path))
    
    def _get_last_backup_time(self) -> float:
        """마지막 백업 시간 조회"""
        last_backup = None
        for backup in self.backup_jobs.values():
            if backup.status == BackupStatus.COMPLETED and backup.completed_at:
                if not last_backup or backup.completed_at > last_backup:
                    last_backup = backup.completed_at
        
        return last_backup.timestamp() if last_backup else 0
    
    def _get_last_full_backup_time(self) -> float:
        """마지막 전체 백업 시간 조회"""
        last_full_backup = None
        for backup in self.backup_jobs.values():
            if (backup.backup_type == BackupType.FULL and 
                backup.status == BackupStatus.COMPLETED and 
                backup.completed_at):
                if not last_full_backup or backup.completed_at > last_full_backup:
                    last_full_backup = backup.completed_at
        
        return last_full_backup.timestamp() if last_full_backup else 0
    
    def _calculate_original_size(self) -> int:
        """원본 크기 계산"""
        total_size = 0
        for target_path in self.backup_targets.values():
            if os.path.exists(target_path):
                if os.path.isfile(target_path):
                    total_size += os.path.getsize(target_path)
                else:
                    for root, dirs, files in os.walk(target_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
        return total_size
    
    def _notify_backup_completed(self, backup_job: BackupJob):
        """백업 완료 알림"""
        for callback in self.backup_callbacks:
            try:
                callback({
                    'type': 'backup_completed',
                    'backup': asdict(backup_job)
                })
            except Exception as e:
                logger.error(f"백업 완료 알림 오류: {e}")
    
    def restore_backup(self, backup_id: str, target_path: str = None) -> str:
        """백업 복구"""
        try:
            backup_job = self.backup_jobs.get(backup_id)
            if not backup_job or not backup_job.file_path:
                return None
            
            restore_id = f"restore_{int(time.time() * 1000)}"
            
            # 복구 작업 생성
            restore_job = RestoreJob(
                id=restore_id,
                backup_id=backup_id,
                status=RestoreStatus.PENDING,
                created_at=datetime.now(),
                target_path=target_path or ".",
                metadata={
                    'backup_name': backup_job.name,
                    'restored_by': 'system'
                }
            )
            
            self.restore_jobs[restore_id] = restore_job
            
            # 복구 실행
            self._execute_restore(restore_job)
            
            return restore_id
            
        except Exception as e:
            logger.error(f"백업 복구 오류: {e}")
            return None
    
    def _execute_restore(self, restore_job: RestoreJob):
        """복구 실행"""
        try:
            restore_job.status = RestoreStatus.RUNNING
            restore_job.started_at = datetime.now()
            
            backup_job = self.backup_jobs[restore_job.backup_id]
            backup_path = Path(backup_job.file_path)
            
            if not backup_path.exists():
                raise FileNotFoundError(f"백업 파일을 찾을 수 없습니다: {backup_path}")
            
            # 복구 실행
            with tarfile.open(backup_path, 'r:gz' if backup_path.suffix == '.gz' else 'r') as tar:
                tar.extractall(path=restore_job.target_path)
            
            # 복구 완료 처리
            restore_job.status = RestoreStatus.COMPLETED
            restore_job.completed_at = datetime.now()
            
            # 콜백 실행
            self._notify_restore_completed(restore_job)
            
            logger.info(f"복구 완료: {restore_job.id} - {backup_job.name}")
            
        except Exception as e:
            restore_job.status = RestoreStatus.FAILED
            restore_job.error_message = str(e)
            restore_job.completed_at = datetime.now()
            
            logger.error(f"복구 실행 오류: {e}")
    
    def _notify_restore_completed(self, restore_job: RestoreJob):
        """복구 완료 알림"""
        for callback in self.backup_callbacks:
            try:
                callback({
                    'type': 'restore_completed',
                    'restore': asdict(restore_job)
                })
            except Exception as e:
                logger.error(f"복구 완료 알림 오류: {e}")
    
    def get_backup_jobs(self, status: BackupStatus = None, limit: int = 100) -> List[BackupJob]:
        """백업 작업 조회"""
        jobs = list(self.backup_jobs.values())
        
        if status:
            jobs = [job for job in jobs if job.status == status]
        
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        return jobs[:limit]
    
    def get_restore_jobs(self, status: RestoreStatus = None, limit: int = 100) -> List[RestoreJob]:
        """복구 작업 조회"""
        jobs = list(self.restore_jobs.values())
        
        if status:
            jobs = [job for job in jobs if job.status == status]
        
        jobs.sort(key=lambda x: x.created_at, reverse=True)
        return jobs[:limit]
    
    def cleanup_old_backups(self, days: int = None):
        """오래된 백업 정리"""
        try:
            retention_days = days or self.retention_days
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            # 오래된 백업 파일 삭제
            for backup_job in self.backup_jobs.values():
                if (backup_job.status == BackupStatus.COMPLETED and 
                    backup_job.completed_at and 
                    backup_job.completed_at < cutoff_time and
                    backup_job.file_path):
                    
                    backup_path = Path(backup_job.file_path)
                    if backup_path.exists():
                        backup_path.unlink()
                        logger.info(f"오래된 백업 파일 삭제: {backup_path}")
            
            # 오래된 백업 작업 기록 정리
            old_jobs = [
                job_id for job_id, job in self.backup_jobs.items()
                if job.completed_at and job.completed_at < cutoff_time
            ]
            
            for job_id in old_jobs:
                del self.backup_jobs[job_id]
            
            logger.info(f"오래된 백업 정리 완료: {len(old_jobs)}개 작업")
            
        except Exception as e:
            logger.error(f"백업 정리 오류: {e}")
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """백업 통계 조회"""
        total_backups = len(self.backup_jobs)
        completed_backups = len([job for job in self.backup_jobs.values() if job.status == BackupStatus.COMPLETED])
        failed_backups = len([job for job in self.backup_jobs.values() if job.status == BackupStatus.FAILED])
        
        total_size = sum(job.file_size for job in self.backup_jobs.values() if job.file_size)
        
        # 백업 타입별 통계
        type_stats = {}
        for backup_type in BackupType:
            type_stats[backup_type.value] = len([
                job for job in self.backup_jobs.values() 
                if job.backup_type == backup_type
            ])
        
        # 최근 7일간 백업 통계
        week_ago = datetime.now() - timedelta(days=7)
        recent_backups = [
            job for job in self.backup_jobs.values()
            if job.created_at >= week_ago
        ]
        
        return {
            'total_backups': total_backups,
            'completed_backups': completed_backups,
            'failed_backups': failed_backups,
            'success_rate': (completed_backups / total_backups * 100) if total_backups > 0 else 0,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'type_stats': type_stats,
            'recent_backups_7days': len(recent_backups),
            'active_schedules': len([s for s in self.backup_schedules.values() if s.is_active])
        }
    
    def add_backup_callback(self, callback: Callable):
        """백업 콜백 함수 추가"""
        self.backup_callbacks.append(callback)
    
    def remove_backup_callback(self, callback: Callable):
        """백업 콜백 함수 제거"""
        if callback in self.backup_callbacks:
            self.backup_callbacks.remove(callback)
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'is_scheduler_running': self.is_scheduler_running,
            'total_backup_jobs': len(self.backup_jobs),
            'total_restore_jobs': len(self.restore_jobs),
            'active_schedules': len([s for s in self.backup_schedules.values() if s.is_active]),
            'backup_directory': str(self.backup_directory),
            'compression_enabled': self.compression_enabled,
            'encryption_enabled': self.encryption_enabled,
            'retention_days': self.retention_days
        }
    
    def stop_service(self):
        """서비스 중지"""
        self.is_scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("백업 및 복구 서비스 중지")

# 전역 인스턴스
backup_recovery_service = BackupRecoveryService()
