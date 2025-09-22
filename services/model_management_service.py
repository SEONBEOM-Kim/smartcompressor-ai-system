#!/usr/bin/env python3
"""
AI 모델 관리 서비스
OTA 업데이트, 버전 관리, 롤백 기능을 제공하는 모델 관리 시스템
"""

import os
import json
import time
import hashlib
import logging
import threading
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import tempfile
import zipfile

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelVersion:
    """모델 버전 정보"""
    
    def __init__(self, model_name: str, version: str, file_path: str, 
                 metadata: Dict = None):
        self.model_name = model_name
        self.version = version
        self.file_path = file_path
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.is_active = False
        self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """파일 체크섬 계산"""
        try:
            with open(self.file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"체크섬 계산 실패: {e}")
            return ""
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return {
            'model_name': self.model_name,
            'version': self.version,
            'file_path': self.file_path,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'checksum': self.checksum
        }

class ModelUpdateSource:
    """모델 업데이트 소스 추상 클래스"""
    
    def __init__(self, name: str):
        self.name = name
    
    def check_for_updates(self) -> List[Dict]:
        """업데이트 확인"""
        raise NotImplementedError
    
    def download_model(self, model_info: Dict) -> str:
        """모델 다운로드"""
        raise NotImplementedError

class LocalFileSource(ModelUpdateSource):
    """로컬 파일 시스템 소스"""
    
    def __init__(self, watch_directory: str):
        super().__init__("local_file")
        self.watch_directory = Path(watch_directory)
        self.watch_directory.mkdir(parents=True, exist_ok=True)
    
    def check_for_updates(self) -> List[Dict]:
        """로컬 디렉토리에서 업데이트 확인"""
        updates = []
        
        try:
            for file_path in self.watch_directory.glob("*.pkl"):
                if file_path.is_file():
                    updates.append({
                        'model_name': file_path.stem,
                        'version': self._extract_version_from_filename(file_path.name),
                        'file_path': str(file_path),
                        'source': 'local_file',
                        'size': file_path.stat().st_size,
                        'modified_time': file_path.stat().st_mtime
                    })
        except Exception as e:
            logger.error(f"로컬 파일 업데이트 확인 실패: {e}")
        
        return updates
    
    def download_model(self, model_info: Dict) -> str:
        """로컬 파일 복사"""
        source_path = model_info['file_path']
        return source_path
    
    def _extract_version_from_filename(self, filename: str) -> str:
        """파일명에서 버전 추출"""
        # 예: model_v1.2.3.pkl -> 1.2.3
        import re
        match = re.search(r'v(\d+\.\d+\.\d+)', filename)
        return match.group(1) if match else "1.0.0"

class RemoteAPISource(ModelUpdateSource):
    """원격 API 소스"""
    
    def __init__(self, api_url: str, api_key: str = None):
        super().__init__("remote_api")
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json'
        }
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
    
    def check_for_updates(self) -> List[Dict]:
        """원격 API에서 업데이트 확인"""
        updates = []
        
        try:
            response = requests.get(
                f"{self.api_url}/models/updates",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                updates = data.get('updates', [])
            else:
                logger.error(f"원격 API 업데이트 확인 실패: {response.status_code}")
                
        except Exception as e:
            logger.error(f"원격 API 업데이트 확인 실패: {e}")
        
        return updates
    
    def download_model(self, model_info: Dict) -> str:
        """원격에서 모델 다운로드"""
        try:
            download_url = model_info.get('download_url')
            if not download_url:
                raise ValueError("다운로드 URL이 없습니다")
            
            # 임시 파일로 다운로드
            response = requests.get(download_url, timeout=300)
            response.raise_for_status()
            
            # 임시 파일 생성
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix='.pkl',
                prefix=f"{model_info['model_name']}_"
            )
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            logger.error(f"모델 다운로드 실패: {e}")
            raise

class ModelManagementService:
    """AI 모델 관리 서비스"""
    
    def __init__(self, models_dir: str = 'data/models'):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # 모델 버전 관리
        self.model_versions = {}  # {model_name: [ModelVersion]}
        self.active_versions = {}  # {model_name: version}
        
        # 업데이트 소스
        self.update_sources = []
        self._initialize_sources()
        
        # 모니터링 설정
        self.check_interval = 300  # 5분
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 롤백 설정
        self.max_versions_per_model = 5
        
        # 모델 로드
        self._load_existing_models()
        
        logger.info("AI 모델 관리 서비스 초기화 완료")
    
    def _initialize_sources(self):
        """업데이트 소스 초기화"""
        try:
            # 로컬 파일 소스
            local_watch_dir = os.getenv('MODEL_WATCH_DIR', 'data/model_updates')
            self.update_sources.append(LocalFileSource(local_watch_dir))
            
            # 원격 API 소스 (환경변수가 설정된 경우)
            remote_api_url = os.getenv('MODEL_UPDATE_API_URL')
            remote_api_key = os.getenv('MODEL_UPDATE_API_KEY')
            
            if remote_api_url:
                self.update_sources.append(RemoteAPISource(remote_api_url, remote_api_key))
            
            logger.info(f"업데이트 소스 초기화 완료: {len(self.update_sources)}개")
            
        except Exception as e:
            logger.error(f"업데이트 소스 초기화 실패: {e}")
    
    def _load_existing_models(self):
        """기존 모델 로드"""
        try:
            # 모델 디렉토리에서 기존 모델들 스캔
            for model_file in self.models_dir.glob("*.pkl"):
                model_name = model_file.stem
                version = "1.0.0"  # 기본 버전
                
                # 버전 정보 파일 확인
                version_file = self.models_dir / f"{model_name}_version.json"
                if version_file.exists():
                    with open(version_file, 'r', encoding='utf-8') as f:
                        version_data = json.load(f)
                        version = version_data.get('version', version)
                
                # 모델 버전 추가
                model_version = ModelVersion(
                    model_name=model_name,
                    version=version,
                    file_path=str(model_file)
                )
                model_version.is_active = True
                
                if model_name not in self.model_versions:
                    self.model_versions[model_name] = []
                
                self.model_versions[model_name].append(model_version)
                self.active_versions[model_name] = version
                
            logger.info(f"기존 모델 로드 완료: {len(self.active_versions)}개 모델")
            
        except Exception as e:
            logger.error(f"기존 모델 로드 실패: {e}")
    
    def start_monitoring(self):
        """모델 업데이트 모니터링 시작"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("모델 업데이트 모니터링 시작")
    
    def stop_monitoring(self):
        """모델 업데이트 모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("모델 업데이트 모니터링 중지")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                self.check_and_update_models()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def check_and_update_models(self) -> List[Dict]:
        """모든 소스에서 업데이트 확인 및 적용"""
        updates_applied = []
        
        try:
            for source in self.update_sources:
                updates = source.check_for_updates()
                
                for update_info in updates:
                    try:
                        if self._should_update_model(update_info):
                            result = self.update_model(update_info, source)
                            if result['success']:
                                updates_applied.append(result)
                    except Exception as e:
                        logger.error(f"모델 업데이트 실패: {e}")
            
            if updates_applied:
                logger.info(f"모델 업데이트 완료: {len(updates_applied)}개")
            
        except Exception as e:
            logger.error(f"모델 업데이트 확인 실패: {e}")
        
        return updates_applied
    
    def _should_update_model(self, update_info: Dict) -> bool:
        """모델 업데이트 여부 판단"""
        model_name = update_info['model_name']
        version = update_info['version']
        
        # 기존 모델이 없는 경우
        if model_name not in self.active_versions:
            return True
        
        # 버전 비교
        current_version = self.active_versions[model_name]
        return self._compare_versions(version, current_version) > 0
    
    def _compare_versions(self, version1: str, version2: str) -> int:
        """버전 비교 (1: version1 > version2, 0: 같음, -1: version1 < version2)"""
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # 길이 맞추기
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for i in range(max_len):
                if v1_parts[i] > v2_parts[i]:
                    return 1
                elif v1_parts[i] < v2_parts[i]:
                    return -1
            
            return 0
            
        except Exception as e:
            logger.error(f"버전 비교 실패: {e}")
            return 0
    
    def update_model(self, update_info: Dict, source: ModelUpdateSource) -> Dict:
        """모델 업데이트"""
        try:
            model_name = update_info['model_name']
            version = update_info['version']
            
            logger.info(f"모델 업데이트 시작: {model_name} v{version}")
            
            # 모델 다운로드
            temp_file_path = source.download_model(update_info)
            
            # 기존 모델 백업
            self._backup_current_model(model_name)
            
            # 새 모델 설치
            new_model_path = self._install_model(model_name, version, temp_file_path)
            
            # 모델 버전 등록
            model_version = ModelVersion(
                model_name=model_name,
                version=version,
                file_path=new_model_path,
                metadata=update_info
            )
            
            if model_name not in self.model_versions:
                self.model_versions[model_name] = []
            
            self.model_versions[model_name].append(model_version)
            self.active_versions[model_name] = version
            
            # 이전 버전 비활성화
            for mv in self.model_versions[model_name]:
                if mv.version != version:
                    mv.is_active = False
            
            # 버전 정보 저장
            self._save_version_info(model_name, version)
            
            # AI 서비스에 모델 업데이트 알림
            self._notify_ai_service(model_name, version, new_model_path)
            
            # 오래된 버전 정리
            self._cleanup_old_versions(model_name)
            
            # 임시 파일 삭제
            if temp_file_path != new_model_path:
                os.unlink(temp_file_path)
            
            logger.info(f"모델 업데이트 완료: {model_name} v{version}")
            
            return {
                'success': True,
                'model_name': model_name,
                'version': version,
                'message': f'모델 {model_name}이 v{version}으로 업데이트되었습니다'
            }
            
        except Exception as e:
            logger.error(f"모델 업데이트 실패: {e}")
            return {
                'success': False,
                'model_name': update_info.get('model_name', 'unknown'),
                'version': update_info.get('version', 'unknown'),
                'error': str(e)
            }
    
    def _backup_current_model(self, model_name: str):
        """현재 모델 백업"""
        try:
            current_model_path = self.models_dir / f"{model_name}.pkl"
            if current_model_path.exists():
                backup_path = self.models_dir / f"{model_name}_backup_{int(time.time())}.pkl"
                shutil.copy2(current_model_path, backup_path)
                logger.info(f"모델 백업 완료: {backup_path}")
        except Exception as e:
            logger.error(f"모델 백업 실패: {e}")
    
    def _install_model(self, model_name: str, version: str, source_path: str) -> str:
        """모델 설치"""
        try:
            # 최종 모델 경로
            final_path = self.models_dir / f"{model_name}.pkl"
            
            # 모델 파일 복사
            shutil.copy2(source_path, final_path)
            
            # 스케일러 파일도 확인
            scaler_name = f"{model_name}_scaler"
            scaler_source = source_path.replace('.pkl', '_scaler.pkl')
            if os.path.exists(scaler_source):
                scaler_dest = self.models_dir / f"{scaler_name}.pkl"
                shutil.copy2(scaler_source, scaler_dest)
                logger.info(f"스케일러 파일 설치: {scaler_dest}")
            
            logger.info(f"모델 설치 완료: {final_path}")
            return str(final_path)
            
        except Exception as e:
            logger.error(f"모델 설치 실패: {e}")
            raise
    
    def _save_version_info(self, model_name: str, version: str):
        """버전 정보 저장"""
        try:
            version_file = self.models_dir / f"{model_name}_version.json"
            version_data = {
                'model_name': model_name,
                'version': version,
                'updated_at': datetime.now().isoformat(),
                'file_path': str(self.models_dir / f"{model_name}.pkl")
            }
            
            with open(version_file, 'w', encoding='utf-8') as f:
                json.dump(version_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"버전 정보 저장 실패: {e}")
    
    def _notify_ai_service(self, model_name: str, version: str, model_path: str):
        """AI 서비스에 모델 업데이트 알림"""
        try:
            from services.ai_service import unified_ai_service
            
            # AI 서비스에 모델 업데이트 알림
            logger.info(f"AI 서비스에 모델 업데이트 알림: {model_name} v{version}")
            
            # 실제로는 AI 서비스의 모델 리로드 메서드 호출
            # unified_ai_service.reload_model(model_name, model_path)
            
        except Exception as e:
            logger.error(f"AI 서비스 알림 실패: {e}")
    
    def _cleanup_old_versions(self, model_name: str):
        """오래된 버전 정리"""
        try:
            if model_name not in self.model_versions:
                return
            
            versions = self.model_versions[model_name]
            if len(versions) <= self.max_versions_per_model:
                return
            
            # 버전별로 정렬 (최신순)
            versions.sort(key=lambda x: x.created_at, reverse=True)
            
            # 오래된 버전들 삭제
            for old_version in versions[self.max_versions_per_model:]:
                try:
                    if os.path.exists(old_version.file_path):
                        os.unlink(old_version.file_path)
                    versions.remove(old_version)
                    logger.info(f"오래된 버전 삭제: {old_version.model_name} v{old_version.version}")
                except Exception as e:
                    logger.error(f"오래된 버전 삭제 실패: {e}")
                    
        except Exception as e:
            logger.error(f"버전 정리 실패: {e}")
    
    def rollback_model(self, model_name: str, target_version: str = None) -> Dict:
        """모델 롤백"""
        try:
            if model_name not in self.model_versions:
                return {
                    'success': False,
                    'error': f'모델 {model_name}을 찾을 수 없습니다'
                }
            
            versions = self.model_versions[model_name]
            
            if target_version:
                # 특정 버전으로 롤백
                target_model = None
                for version in versions:
                    if version.version == target_version:
                        target_model = version
                        break
                
                if not target_model:
                    return {
                        'success': False,
                        'error': f'버전 {target_version}을 찾을 수 없습니다'
                    }
            else:
                # 이전 버전으로 롤백
                active_versions = [v for v in versions if v.is_active]
                if len(active_versions) < 2:
                    return {
                        'success': False,
                        'error': '롤백할 이전 버전이 없습니다'
                    }
                
                # 현재 활성 버전을 비활성화하고 이전 버전을 활성화
                current_version = active_versions[0]
                current_version.is_active = False
                
                # 이전 버전 찾기
                target_model = None
                for version in versions:
                    if version.version != current_version.version and not version.is_active:
                        target_model = version
                        break
                
                if not target_model:
                    return {
                        'success': False,
                        'error': '롤백할 이전 버전을 찾을 수 없습니다'
                    }
            
            # 롤백 실행
            target_model.is_active = True
            self.active_versions[model_name] = target_model.version
            
            # 모델 파일 복사
            current_model_path = self.models_dir / f"{model_name}.pkl"
            shutil.copy2(target_model.file_path, current_model_path)
            
            # 버전 정보 저장
            self._save_version_info(model_name, target_model.version)
            
            # AI 서비스에 알림
            self._notify_ai_service(model_name, target_model.version, str(current_model_path))
            
            logger.info(f"모델 롤백 완료: {model_name} -> v{target_model.version}")
            
            return {
                'success': True,
                'model_name': model_name,
                'version': target_model.version,
                'message': f'모델 {model_name}이 v{target_model.version}으로 롤백되었습니다'
            }
            
        except Exception as e:
            logger.error(f"모델 롤백 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_model_status(self) -> Dict:
        """모델 상태 조회"""
        return {
            'monitoring': self.is_monitoring,
            'sources': [source.name for source in self.update_sources],
            'models': {
                name: {
                    'active_version': version,
                    'total_versions': len(versions),
                    'versions': [v.to_dict() for v in versions]
                }
                for name, version in self.active_versions.items()
                for versions in [self.model_versions.get(name, [])]
            }
        }
    
    def get_service_status(self) -> Dict:
        """서비스 상태 확인"""
        return {
            'status': 'running' if self.is_monitoring else 'stopped',
            'monitoring': self.is_monitoring,
            'sources_count': len(self.update_sources),
            'models_count': len(self.active_versions),
            'check_interval': self.check_interval
        }

# 전역 서비스 인스턴스
model_management_service = ModelManagementService()
