#!/usr/bin/env python3
"""
펌웨어 OTA 업데이트 서비스
Tesla 스타일의 하드웨어 펌웨어 OTA 업데이트 시스템
"""

import os
import json
import time
import logging
import hashlib
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
import requests
import zipfile
import tempfile

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FirmwareVersion:
    """펌웨어 버전 정보"""
    version: str
    build_number: int
    release_date: str
    file_path: str
    file_size: int
    checksum: str
    changelog: str
    is_stable: bool
    min_hardware_version: str
    max_hardware_version: str

@dataclass
class DeviceUpdateStatus:
    """디바이스 업데이트 상태"""
    device_id: str
    current_version: str
    target_version: str
    update_status: str  # pending, downloading, installing, completed, failed
    progress: float  # 0-100
    error_message: str
    started_at: float
    completed_at: float

class FirmwareOTAService:
    """펌웨어 OTA 업데이트 서비스 (Tesla 스타일)"""
    
    def __init__(self, firmware_dir: str = 'data/firmware'):
        self.firmware_dir = Path(firmware_dir)
        self.firmware_dir.mkdir(parents=True, exist_ok=True)
        
        self.firmware_versions = {}  # version -> FirmwareVersion
        self.device_updates = {}  # device_id -> DeviceUpdateStatus
        self.update_callbacks = []
        
        # 업데이트 설정
        self.max_concurrent_updates = 5
        self.update_timeout = 1800  # 30분
        self.rollback_enabled = True
        
        # 펌웨어 로드
        self._load_firmware_versions()
        
        logger.info("펌웨어 OTA 업데이트 서비스 초기화 완료")
    
    def _load_firmware_versions(self):
        """펌웨어 버전 로드"""
        try:
            # 펌웨어 디렉토리에서 버전 정보 로드
            version_file = self.firmware_dir / 'versions.json'
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    versions_data = json.load(f)
                    
                for version_info in versions_data:
                    version = FirmwareVersion(**version_info)
                    self.firmware_versions[version.version] = version
                    
                logger.info(f"펌웨어 버전 로드 완료: {len(self.firmware_versions)}개")
            else:
                # 기본 펌웨어 버전 생성
                self._create_default_firmware()
                
        except Exception as e:
            logger.error(f"펌웨어 버전 로드 실패: {e}")
    
    def _create_default_firmware(self):
        """기본 펌웨어 버전 생성"""
        try:
            default_version = FirmwareVersion(
                version="1.0.0",
                build_number=1,
                release_date=datetime.now().strftime('%Y-%m-%d'),
                file_path=str(self.firmware_dir / 'firmware_v1.0.0.bin'),
                file_size=0,
                checksum="",
                changelog="Initial firmware release",
                is_stable=True,
                min_hardware_version="ESP32_v1",
                max_hardware_version="ESP32_v1"
            )
            
            self.firmware_versions[default_version.version] = default_version
            self._save_firmware_versions()
            
        except Exception as e:
            logger.error(f"기본 펌웨어 생성 실패: {e}")
    
    def _save_firmware_versions(self):
        """펌웨어 버전 정보 저장"""
        try:
            version_file = self.firmware_dir / 'versions.json'
            versions_data = [asdict(version) for version in self.firmware_versions.values()]
            
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(versions_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"펌웨어 버전 저장 실패: {e}")
    
    def add_firmware(self, version: str, file_path: str, changelog: str = "", 
                    is_stable: bool = True) -> bool:
        """새 펌웨어 추가"""
        try:
            if version in self.firmware_versions:
                logger.warning(f"펌웨어 버전 {version}이 이미 존재합니다")
                return False
            
            # 파일 검증
            if not os.path.exists(file_path):
                logger.error(f"펌웨어 파일을 찾을 수 없습니다: {file_path}")
                return False
            
            # 파일 크기 및 체크섬 계산
            file_size = os.path.getsize(file_path)
            checksum = self._calculate_checksum(file_path)
            
            # 펌웨어 버전 생성
            firmware = FirmwareVersion(
                version=version,
                build_number=len(self.firmware_versions) + 1,
                release_date=datetime.now().strftime('%Y-%m-%d'),
                file_path=file_path,
                file_size=file_size,
                checksum=checksum,
                changelog=changelog,
                is_stable=is_stable,
                min_hardware_version="ESP32_v1",
                max_hardware_version="ESP32_v1"
            )
            
            self.firmware_versions[version] = firmware
            self._save_firmware_versions()
            
            logger.info(f"펌웨어 추가 완료: {version}")
            return True
            
        except Exception as e:
            logger.error(f"펌웨어 추가 실패: {e}")
            return False
    
    def _calculate_checksum(self, file_path: str) -> str:
        """파일 체크섬 계산"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"체크섬 계산 실패: {e}")
            return ""
    
    def get_available_versions(self, device_id: str = None) -> List[Dict]:
        """사용 가능한 펌웨어 버전 조회"""
        try:
            versions = []
            for version in self.firmware_versions.values():
                versions.append({
                    'version': version.version,
                    'build_number': version.build_number,
                    'release_date': version.release_date,
                    'file_size': version.file_size,
                    'changelog': version.changelog,
                    'is_stable': version.is_stable,
                    'min_hardware_version': version.min_hardware_version,
                    'max_hardware_version': version.max_hardware_version
                })
            
            # 버전순 정렬 (최신순)
            versions.sort(key=lambda x: x['build_number'], reverse=True)
            return versions
            
        except Exception as e:
            logger.error(f"펌웨어 버전 조회 실패: {e}")
            return []
    
    def get_latest_stable_version(self) -> Optional[str]:
        """최신 안정 버전 조회"""
        try:
            stable_versions = [
                v for v in self.firmware_versions.values() 
                if v.is_stable
            ]
            
            if not stable_versions:
                return None
            
            latest = max(stable_versions, key=lambda x: x.build_number)
            return latest.version
            
        except Exception as e:
            logger.error(f"최신 안정 버전 조회 실패: {e}")
            return None
    
    def start_update(self, device_id: str, target_version: str, 
                    current_version: str = None) -> bool:
        """펌웨어 업데이트 시작"""
        try:
            if device_id in self.device_updates:
                logger.warning(f"디바이스 {device_id}의 업데이트가 이미 진행 중입니다")
                return False
            
            if target_version not in self.firmware_versions:
                logger.error(f"펌웨어 버전 {target_version}을 찾을 수 없습니다")
                return False
            
            # 업데이트 상태 생성
            update_status = DeviceUpdateStatus(
                device_id=device_id,
                current_version=current_version or "unknown",
                target_version=target_version,
                update_status="pending",
                progress=0.0,
                error_message="",
                started_at=time.time(),
                completed_at=0.0
            )
            
            self.device_updates[device_id] = update_status
            
            # 업데이트 스레드 시작
            update_thread = threading.Thread(
                target=self._update_device_firmware,
                args=(device_id, target_version),
                daemon=True
            )
            update_thread.start()
            
            logger.info(f"펌웨어 업데이트 시작: {device_id} -> {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"펌웨어 업데이트 시작 실패: {e}")
            return False
    
    def _update_device_firmware(self, device_id: str, target_version: str):
        """디바이스 펌웨어 업데이트 실행"""
        try:
            update_status = self.device_updates[device_id]
            firmware = self.firmware_versions[target_version]
            
            # 1. 다운로드 단계
            update_status.update_status = "downloading"
            update_status.progress = 10.0
            self._notify_update_progress(device_id)
            
            # 펌웨어 파일 다운로드 (실제로는 디바이스에 전송)
            if not self._download_firmware_to_device(device_id, firmware):
                update_status.update_status = "failed"
                update_status.error_message = "펌웨어 다운로드 실패"
                update_status.completed_at = time.time()
                self._notify_update_completed(device_id)
                return
            
            # 2. 설치 단계
            update_status.update_status = "installing"
            update_status.progress = 50.0
            self._notify_update_progress(device_id)
            
            # 펌웨어 설치 (실제로는 디바이스에 설치 명령 전송)
            if not self._install_firmware_on_device(device_id, firmware):
                update_status.update_status = "failed"
                update_status.error_message = "펌웨어 설치 실패"
                update_status.completed_at = time.time()
                self._notify_update_completed(device_id)
                return
            
            # 3. 검증 단계
            update_status.progress = 80.0
            self._notify_update_progress(device_id)
            
            # 펌웨어 검증
            if not self._verify_firmware_installation(device_id, target_version):
                update_status.update_status = "failed"
                update_status.error_message = "펌웨어 검증 실패"
                update_status.completed_at = time.time()
                self._notify_update_completed(device_id)
                return
            
            # 4. 완료
            update_status.update_status = "completed"
            update_status.progress = 100.0
            update_status.completed_at = time.time()
            self._notify_update_completed(device_id)
            
            logger.info(f"펌웨어 업데이트 완료: {device_id} -> {target_version}")
            
        except Exception as e:
            logger.error(f"펌웨어 업데이트 실행 실패: {e}")
            if device_id in self.device_updates:
                self.device_updates[device_id].update_status = "failed"
                self.device_updates[device_id].error_message = str(e)
                self.device_updates[device_id].completed_at = time.time()
                self._notify_update_completed(device_id)
    
    def _download_firmware_to_device(self, device_id: str, firmware: FirmwareVersion) -> bool:
        """디바이스에 펌웨어 다운로드"""
        try:
            # 실제로는 WebSocket을 통해 디바이스에 펌웨어 전송
            # 여기서는 시뮬레이션
            logger.info(f"디바이스 {device_id}에 펌웨어 다운로드 중...")
            
            # 다운로드 진행률 시뮬레이션
            for progress in range(10, 50, 10):
                time.sleep(1)  # 실제로는 네트워크 전송 시간
                if device_id in self.device_updates:
                    self.device_updates[device_id].progress = progress
                    self._notify_update_progress(device_id)
            
            return True
            
        except Exception as e:
            logger.error(f"펌웨어 다운로드 실패: {e}")
            return False
    
    def _install_firmware_on_device(self, device_id: str, firmware: FirmwareVersion) -> bool:
        """디바이스에 펌웨어 설치"""
        try:
            # 실제로는 디바이스에 설치 명령 전송
            logger.info(f"디바이스 {device_id}에 펌웨어 설치 중...")
            
            # 설치 진행률 시뮬레이션
            for progress in range(50, 80, 10):
                time.sleep(2)  # 실제로는 설치 시간
                if device_id in self.device_updates:
                    self.device_updates[device_id].progress = progress
                    self._notify_update_progress(device_id)
            
            return True
            
        except Exception as e:
            logger.error(f"펌웨어 설치 실패: {e}")
            return False
    
    def _verify_firmware_installation(self, device_id: str, target_version: str) -> bool:
        """펌웨어 설치 검증"""
        try:
            # 실제로는 디바이스에서 버전 확인
            logger.info(f"디바이스 {device_id} 펌웨어 검증 중...")
            
            # 검증 진행률 시뮬레이션
            for progress in range(80, 100, 10):
                time.sleep(1)
                if device_id in self.device_updates:
                    self.device_updates[device_id].progress = progress
                    self._notify_update_progress(device_id)
            
            return True
            
        except Exception as e:
            logger.error(f"펌웨어 검증 실패: {e}")
            return False
    
    def rollback_firmware(self, device_id: str, target_version: str) -> bool:
        """펌웨어 롤백"""
        try:
            if not self.rollback_enabled:
                logger.warning("롤백이 비활성화되어 있습니다")
                return False
            
            if target_version not in self.firmware_versions:
                logger.error(f"롤백 대상 펌웨어 버전 {target_version}을 찾을 수 없습니다")
                return False
            
            logger.info(f"펌웨어 롤백 시작: {device_id} -> {target_version}")
            return self.start_update(device_id, target_version)
            
        except Exception as e:
            logger.error(f"펌웨어 롤백 실패: {e}")
            return False
    
    def get_update_status(self, device_id: str) -> Optional[Dict]:
        """업데이트 상태 조회"""
        if device_id not in self.device_updates:
            return None
        
        update_status = self.device_updates[device_id]
        return {
            'device_id': update_status.device_id,
            'current_version': update_status.current_version,
            'target_version': update_status.target_version,
            'update_status': update_status.update_status,
            'progress': update_status.progress,
            'error_message': update_status.error_message,
            'started_at': update_status.started_at,
            'completed_at': update_status.completed_at,
            'duration': update_status.completed_at - update_status.started_at if update_status.completed_at > 0 else 0
        }
    
    def get_all_update_status(self) -> List[Dict]:
        """모든 업데이트 상태 조회"""
        return [self.get_update_status(device_id) for device_id in self.device_updates.keys()]
    
    def cancel_update(self, device_id: str) -> bool:
        """업데이트 취소"""
        try:
            if device_id not in self.device_updates:
                logger.warning(f"디바이스 {device_id}의 업데이트를 찾을 수 없습니다")
                return False
            
            update_status = self.device_updates[device_id]
            if update_status.update_status in ["completed", "failed"]:
                logger.warning(f"디바이스 {device_id}의 업데이트가 이미 완료되었습니다")
                return False
            
            update_status.update_status = "cancelled"
            update_status.completed_at = time.time()
            self._notify_update_completed(device_id)
            
            logger.info(f"업데이트 취소: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"업데이트 취소 실패: {e}")
            return False
    
    def add_update_callback(self, callback: Callable[[str, Dict], None]):
        """업데이트 콜백 추가"""
        self.update_callbacks.append(callback)
    
    def _notify_update_progress(self, device_id: str):
        """업데이트 진행률 알림"""
        try:
            status = self.get_update_status(device_id)
            if status:
                for callback in self.update_callbacks:
                    try:
                        callback(device_id, status)
                    except Exception as e:
                        logger.error(f"업데이트 콜백 오류: {e}")
        except Exception as e:
            logger.error(f"업데이트 진행률 알림 실패: {e}")
    
    def _notify_update_completed(self, device_id: str):
        """업데이트 완료 알림"""
        try:
            status = self.get_update_status(device_id)
            if status:
                for callback in self.update_callbacks:
                    try:
                        callback(device_id, status)
                    except Exception as e:
                        logger.error(f"업데이트 콜백 오류: {e}")
        except Exception as e:
            logger.error(f"업데이트 완료 알림 실패: {e}")
    
    def cleanup_completed_updates(self, hours: int = 24):
        """완료된 업데이트 정리"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            completed_devices = []
            
            for device_id, update_status in self.device_updates.items():
                if (update_status.update_status in ["completed", "failed", "cancelled"] and
                    update_status.completed_at > 0 and
                    update_status.completed_at < cutoff_time):
                    completed_devices.append(device_id)
            
            for device_id in completed_devices:
                del self.device_updates[device_id]
            
            logger.info(f"완료된 업데이트 정리: {len(completed_devices)}개")
            
        except Exception as e:
            logger.error(f"업데이트 정리 실패: {e}")
    
    def get_service_status(self) -> Dict:
        """서비스 상태 조회"""
        try:
            total_updates = len(self.device_updates)
            active_updates = len([u for u in self.device_updates.values() 
                                if u.update_status in ["pending", "downloading", "installing"]])
            completed_updates = len([u for u in self.device_updates.values() 
                                   if u.update_status == "completed"])
            failed_updates = len([u for u in self.device_updates.values() 
                                if u.update_status == "failed"])
            
            return {
                'total_firmware_versions': len(self.firmware_versions),
                'total_updates': total_updates,
                'active_updates': active_updates,
                'completed_updates': completed_updates,
                'failed_updates': failed_updates,
                'rollback_enabled': self.rollback_enabled,
                'max_concurrent_updates': self.max_concurrent_updates,
                'update_timeout': self.update_timeout
            }
            
        except Exception as e:
            logger.error(f"서비스 상태 조회 실패: {e}")
            return {}

# 전역 서비스 인스턴스
firmware_ota_service = FirmwareOTAService()
