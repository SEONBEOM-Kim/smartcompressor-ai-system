"""
데이터 백업 및 복구 서비스 - Stripe & AWS 보안 시스템 벤치마킹
자동 백업, 암호화, 복구, 재해 복구 시스템
"""

import os
import shutil
import gzip
import tarfile
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import threading
import schedule
import time
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import psutil

logger = logging.getLogger(__name__)

class BackupType(Enum):
    """백업 유형"""
    FULL = "full"           # 전체 백업
    INCREMENTAL = "incremental"  # 증분 백업
    DIFFERENTIAL = "differential"  # 차등 백업
    SNAPSHOT = "snapshot"   # 스냅샷

class BackupStatus(Enum):
    """백업 상태"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StorageType(Enum):
    """저장소 유형"""
    LOCAL = "local"
    S3 = "s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"

@dataclass
class BackupConfig:
    """백업 설정"""
    backup_id: str
    name: str
    backup_type: BackupType
    source_paths: List[str]
    destination: str
    storage_type: StorageType
    schedule: str  # cron expression
    retention_days: int
    encryption_enabled: bool = True
    compression_enabled: bool = True
    is_active: bool = True

@dataclass
class BackupJob:
    """백업 작업"""
    job_id: str
    config_id: str
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    backup_size: int = 0
    file_count: int = 0
    error_message: Optional[str] = None
    backup_path: Optional[str] = None

@dataclass
class RecoveryJob:
    """복구 작업"""
    recovery_id: str
    backup_job_id: str
    target_path: str
    status: BackupStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class BackupRecoveryService:
    """
    Stripe & AWS 보안 시스템을 벤치마킹한 백업 및 복구 서비스
    """
    
    def __init__(self):
        # 백업 설정
        self.backup_configs: Dict[str, BackupConfig] = {}
        self.backup_jobs: Dict[str, BackupJob] = {}
        self.recovery_jobs: Dict[str, RecoveryJob] = {}
        
        # 백업 스케줄러
        self.scheduler_thread = None
        self.is_scheduling = False
        
        # AWS S3 클라이언트 (실제 환경에서 설정)
        self.s3_client = None
        self._initialize_s3_client()
        
        # 백업 디렉토리
        self.backup_root = Path("backups")
        self.backup_root.mkdir(exist_ok=True)
        
        # 기본 설정
        self.default_retention_days = 30
        self.max_backup_size = 10 * 1024 * 1024 * 1024  # 10GB
        self.compression_level = 6
        
        logger.info("BackupRecoveryService 초기화 완료")

    def _initialize_s3_client(self):
        """S3 클라이언트 초기화"""
        try:
            # 실제 환경에서는 AWS 자격 증명 설정
            access_key = os.getenv('AWS_ACCESS_KEY_ID')
            secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
            region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            
            if access_key and secret_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    region_name=region
                )
                logger.info("S3 클라이언트 초기화 완료")
            else:
                logger.warning("AWS 자격 증명이 설정되지 않았습니다. S3 백업이 비활성화됩니다.")
        except Exception as e:
            logger.error(f"S3 클라이언트 초기화 실패: {e}")

    def create_backup_config(self, name: str, backup_type: BackupType,
                           source_paths: List[str], destination: str,
                           storage_type: StorageType, schedule: str,
                           retention_days: int = None,
                           encryption_enabled: bool = True,
                           compression_enabled: bool = True) -> str:
        """백업 설정 생성"""
        config_id = self._generate_config_id()
        
        config = BackupConfig(
            backup_id=config_id,
            name=name,
            backup_type=backup_type,
            source_paths=source_paths,
            destination=destination,
            storage_type=storage_type,
            schedule=schedule,
            retention_days=retention_days or self.default_retention_days,
            encryption_enabled=encryption_enabled,
            compression_enabled=compression_enabled
        )
        
        self.backup_configs[config_id] = config
        
        # 스케줄 등록
        if schedule != "manual":
            self._schedule_backup(config)
        
        logger.info(f"백업 설정 생성 완료: {name} ({config_id})")
        return config_id

    def _schedule_backup(self, config: BackupConfig):
        """백업 스케줄 등록"""
        def backup_job():
            self.run_backup(config.backup_id)
        
        schedule.every().day.at("02:00").do(backup_job)  # 매일 새벽 2시
        
        if not self.is_scheduling:
            self.start_scheduler()

    def start_scheduler(self):
        """스케줄러 시작"""
        if self.is_scheduling:
            return
        
        self.is_scheduling = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        logger.info("백업 스케줄러 시작")

    def stop_scheduler(self):
        """스케줄러 중지"""
        self.is_scheduling = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        logger.info("백업 스케줄러 중지")

    def _scheduler_loop(self):
        """스케줄러 루프"""
        while self.is_scheduling:
            try:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.error(f"스케줄러 루프 오류: {e}")

    def run_backup(self, config_id: str) -> str:
        """백업 실행"""
        if config_id not in self.backup_configs:
            raise ValueError(f"백업 설정을 찾을 수 없습니다: {config_id}")
        
        config = self.backup_configs[config_id]
        job_id = self._generate_job_id()
        
        job = BackupJob(
            job_id=job_id,
            config_id=config_id,
            status=BackupStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self.backup_jobs[job_id] = job
        
        # 백업 실행 (별도 스레드에서)
        backup_thread = threading.Thread(
            target=self._execute_backup,
            args=(job_id, config),
            daemon=True
        )
        backup_thread.start()
        
        logger.info(f"백업 작업 시작: {job_id} ({config.name})")
        return job_id

    def _execute_backup(self, job_id: str, config: BackupConfig):
        """백업 실행"""
        job = self.backup_jobs[job_id]
        
        try:
            # 백업 디렉토리 생성
            backup_dir = self.backup_root / f"{config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 파일 수집
            files_to_backup = self._collect_files(config.source_paths)
            job.file_count = len(files_to_backup)
            
            # 백업 실행
            if config.backup_type == BackupType.FULL:
                backup_path = self._create_full_backup(files_to_backup, backup_dir, config)
            elif config.backup_type == BackupType.INCREMENTAL:
                backup_path = self._create_incremental_backup(files_to_backup, backup_dir, config)
            else:
                backup_path = self._create_full_backup(files_to_backup, backup_dir, config)
            
            # 압축
            if config.compression_enabled:
                backup_path = self._compress_backup(backup_path)
            
            # 암호화
            if config.encryption_enabled:
                backup_path = self._encrypt_backup(backup_path)
            
            # 원격 저장소에 업로드
            if config.storage_type != StorageType.LOCAL:
                self._upload_to_remote_storage(backup_path, config)
            
            # 백업 크기 계산
            job.backup_size = self._get_file_size(backup_path)
            job.backup_path = str(backup_path)
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.now()
            
            logger.info(f"백업 작업 완료: {job_id} (크기: {job.backup_size} bytes)")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            logger.error(f"백업 작업 실패: {job_id} - {e}")

    def _collect_files(self, source_paths: List[str]) -> List[Path]:
        """백업할 파일 수집"""
        files = []
        
        for source_path in source_paths:
            path = Path(source_path)
            
            if path.is_file():
                files.append(path)
            elif path.is_dir():
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        files.append(file_path)
        
        return files

    def _create_full_backup(self, files: List[Path], backup_dir: Path, config: BackupConfig) -> Path:
        """전체 백업 생성"""
        backup_file = backup_dir / f"{config.name}_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar"
        
        with tarfile.open(backup_file, 'w') as tar:
            for file_path in files:
                try:
                    tar.add(file_path, arcname=file_path.name)
                except Exception as e:
                    logger.warning(f"파일 백업 실패: {file_path} - {e}")
        
        return backup_file

    def _create_incremental_backup(self, files: List[Path], backup_dir: Path, config: BackupConfig) -> Path:
        """증분 백업 생성"""
        # 마지막 백업 시간 확인
        last_backup_time = self._get_last_backup_time(config.backup_id)
        
        # 변경된 파일만 필터링
        changed_files = []
        for file_path in files:
            if file_path.stat().st_mtime > last_backup_time:
                changed_files.append(file_path)
        
        backup_file = backup_dir / f"{config.name}_incremental_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar"
        
        with tarfile.open(backup_file, 'w') as tar:
            for file_path in changed_files:
                try:
                    tar.add(file_path, arcname=file_path.name)
                except Exception as e:
                    logger.warning(f"파일 백업 실패: {file_path} - {e}")
        
        return backup_file

    def _get_last_backup_time(self, config_id: str) -> float:
        """마지막 백업 시간 조회"""
        # 실제 환경에서는 DB에서 조회
        return 0.0

    def _compress_backup(self, backup_path: Path) -> Path:
        """백업 압축"""
        compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
        
        with open(backup_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=self.compression_level) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 원본 파일 삭제
        backup_path.unlink()
        
        return compressed_path

    def _encrypt_backup(self, backup_path: Path) -> Path:
        """백업 암호화"""
        from security.services.encryption_service import encryption_service
        
        # 파일 읽기
        with open(backup_path, 'rb') as f:
            data = f.read()
        
        # 암호화
        encrypted_data = encryption_service.encrypt_data(data, "backup_key")
        
        # 암호화된 파일 저장
        encrypted_path = backup_path.with_suffix(backup_path.suffix + '.enc')
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data.data)
        
        # 원본 파일 삭제
        backup_path.unlink()
        
        return encrypted_path

    def _upload_to_remote_storage(self, backup_path: Path, config: BackupConfig):
        """원격 저장소에 업로드"""
        if config.storage_type == StorageType.S3:
            self._upload_to_s3(backup_path, config)
        elif config.storage_type == StorageType.AZURE_BLOB:
            self._upload_to_azure_blob(backup_path, config)
        elif config.storage_type == StorageType.GOOGLE_CLOUD:
            self._upload_to_google_cloud(backup_path, config)

    def _upload_to_s3(self, backup_path: Path, config: BackupConfig):
        """S3에 업로드"""
        if not self.s3_client:
            raise ValueError("S3 클라이언트가 초기화되지 않았습니다.")
        
        try:
            bucket_name = config.destination
            key = f"backups/{config.name}/{backup_path.name}"
            
            self.s3_client.upload_file(
                str(backup_path),
                bucket_name,
                key
            )
            
            logger.info(f"S3 업로드 완료: s3://{bucket_name}/{key}")
            
        except ClientError as e:
            logger.error(f"S3 업로드 실패: {e}")
            raise

    def _upload_to_azure_blob(self, backup_path: Path, config: BackupConfig):
        """Azure Blob Storage에 업로드"""
        # 실제 환경에서는 Azure SDK 사용
        logger.info(f"Azure Blob Storage 업로드: {backup_path}")

    def _upload_to_google_cloud(self, backup_path: Path, config: BackupConfig):
        """Google Cloud Storage에 업로드"""
        # 실제 환경에서는 Google Cloud SDK 사용
        logger.info(f"Google Cloud Storage 업로드: {backup_path}")

    def restore_backup(self, job_id: str, target_path: str) -> str:
        """백업 복구"""
        if job_id not in self.backup_jobs:
            raise ValueError(f"백업 작업을 찾을 수 없습니다: {job_id}")
        
        job = self.backup_jobs[job_id]
        if job.status != BackupStatus.COMPLETED:
            raise ValueError(f"백업이 완료되지 않았습니다: {job_id}")
        
        recovery_id = self._generate_recovery_id()
        
        recovery = RecoveryJob(
            recovery_id=recovery_id,
            backup_job_id=job_id,
            target_path=target_path,
            status=BackupStatus.IN_PROGRESS,
            started_at=datetime.now()
        )
        
        self.recovery_jobs[recovery_id] = recovery
        
        # 복구 실행 (별도 스레드에서)
        recovery_thread = threading.Thread(
            target=self._execute_recovery,
            args=(recovery_id, job, target_path),
            daemon=True
        )
        recovery_thread.start()
        
        logger.info(f"복구 작업 시작: {recovery_id}")
        return recovery_id

    def _execute_recovery(self, recovery_id: str, job: BackupJob, target_path: str):
        """복구 실행"""
        recovery = self.recovery_jobs[recovery_id]
        
        try:
            target_dir = Path(target_path)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            backup_path = Path(job.backup_path)
            
            # 암호화된 파일 복호화
            if backup_path.suffix == '.enc':
                backup_path = self._decrypt_backup(backup_path)
            
            # 압축된 파일 압축 해제
            if backup_path.suffix == '.gz':
                backup_path = self._decompress_backup(backup_path)
            
            # 백업 파일 추출
            with tarfile.open(backup_path, 'r') as tar:
                tar.extractall(target_dir)
            
            recovery.status = BackupStatus.COMPLETED
            recovery.completed_at = datetime.now()
            
            logger.info(f"복구 작업 완료: {recovery_id}")
            
        except Exception as e:
            recovery.status = BackupStatus.FAILED
            recovery.error_message = str(e)
            recovery.completed_at = datetime.now()
            logger.error(f"복구 작업 실패: {recovery_id} - {e}")

    def _decrypt_backup(self, backup_path: Path) -> Path:
        """백업 복호화"""
        from security.services.encryption_service import encryption_service
        
        # 암호화된 파일 읽기
        with open(backup_path, 'rb') as f:
            encrypted_data = f.read()
        
        # 복호화
        decrypted_data = encryption_service.decrypt_data(
            type('EncryptedData', (), {
                'data': encrypted_data,
                'key_id': 'backup_key',
                'encryption_type': 'aes_256_gcm',
                'iv': None,
                'tag': None
            })()
        )
        
        # 복호화된 파일 저장
        decrypted_path = backup_path.with_suffix('')
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_data)
        
        return decrypted_path

    def _decompress_backup(self, backup_path: Path) -> Path:
        """백업 압축 해제"""
        decompressed_path = backup_path.with_suffix('')
        
        with gzip.open(backup_path, 'rb') as f_in:
            with open(decompressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return decompressed_path

    def cleanup_old_backups(self) -> int:
        """오래된 백업 정리"""
        cleaned_count = 0
        cutoff_date = datetime.now() - timedelta(days=self.default_retention_days)
        
        for job in self.backup_jobs.values():
            if (job.status == BackupStatus.COMPLETED and 
                job.completed_at and 
                job.completed_at < cutoff_date):
                
                if job.backup_path and Path(job.backup_path).exists():
                    Path(job.backup_path).unlink()
                    cleaned_count += 1
        
        logger.info(f"오래된 백업 {cleaned_count}개 정리 완료")
        return cleaned_count

    def get_backup_status(self, job_id: str) -> Optional[Dict]:
        """백업 상태 조회"""
        if job_id not in self.backup_jobs:
            return None
        
        job = self.backup_jobs[job_id]
        return asdict(job)

    def get_recovery_status(self, recovery_id: str) -> Optional[Dict]:
        """복구 상태 조회"""
        if recovery_id not in self.recovery_jobs:
            return None
        
        recovery = self.recovery_jobs[recovery_id]
        return asdict(recovery)

    def list_backups(self, config_id: Optional[str] = None) -> List[Dict]:
        """백업 목록 조회"""
        backups = []
        
        for job in self.backup_jobs.values():
            if config_id and job.config_id != config_id:
                continue
            
            if job.status == BackupStatus.COMPLETED:
                backups.append(asdict(job))
        
        # 시간순 정렬 (최신순)
        backups.sort(key=lambda x: x['started_at'], reverse=True)
        
        return backups

    def get_backup_statistics(self) -> Dict:
        """백업 통계 조회"""
        total_jobs = len(self.backup_jobs)
        completed_jobs = len([j for j in self.backup_jobs.values() if j.status == BackupStatus.COMPLETED])
        failed_jobs = len([j for j in self.backup_jobs.values() if j.status == BackupStatus.FAILED])
        
        total_size = sum(j.backup_size for j in self.backup_jobs.values() if j.status == BackupStatus.COMPLETED)
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0,
            "total_size": total_size,
            "active_configs": len([c for c in self.backup_configs.values() if c.is_active])
        }

    def _get_file_size(self, file_path: Path) -> int:
        """파일 크기 조회"""
        try:
            return file_path.stat().st_size
        except:
            return 0

    def _generate_config_id(self) -> str:
        """설정 ID 생성"""
        return f"config_{int(time.time() * 1000)}_{hash(str(time.time()))[:8]}"

    def _generate_job_id(self) -> str:
        """작업 ID 생성"""
        return f"job_{int(time.time() * 1000)}_{hash(str(time.time()))[:8]}"

    def _generate_recovery_id(self) -> str:
        """복구 ID 생성"""
        return f"recovery_{int(time.time() * 1000)}_{hash(str(time.time()))[:8]}"

# 싱글톤 인스턴스
backup_recovery_service = BackupRecoveryService()
