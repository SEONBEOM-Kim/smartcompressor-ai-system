#!/usr/bin/env python3
"""
자동 라벨링 파이프라인
데이터 증강 → 라벨링 서버 자동 업로드
"""

import os
import sys
import json
import time
import requests
import hashlib
from datetime import datetime
from pathlib import Path
import logging
from typing import List, Dict, Optional
import argparse

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_labeling_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoLabelingPipeline:
    """자동 라벨링 파이프라인"""
    
    def __init__(self, 
                 labeling_server_url: str = "http://localhost:3000",
                 augmented_data_dir: str = "data/augmented_audio",
                 labeling_ready_dir: str = "data/labeling_ready"):
        
        self.labeling_server_url = labeling_server_url
        self.augmented_data_dir = augmented_data_dir
        self.labeling_ready_dir = labeling_ready_dir
        
        # 디렉토리 생성
        os.makedirs(self.labeling_ready_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # 처리된 파일 추적
        self.processed_files = set()
        self.load_processed_files()
        
        logger.info("🚀 자동 라벨링 파이프라인 초기화 완료")
        logger.info(f"   증강 데이터 디렉토리: {self.augmented_data_dir}")
        logger.info(f"   라벨링 준비 디렉토리: {self.labeling_ready_dir}")
        logger.info(f"   라벨링 서버: {self.labeling_server_url}")
    
    def load_processed_files(self):
        """처리된 파일 목록 로드"""
        try:
            processed_file = "data/processed_files.json"
            if os.path.exists(processed_file):
                with open(processed_file, 'r', encoding='utf-8') as f:
                    self.processed_files = set(json.load(f))
                logger.info(f"📚 처리된 파일 {len(self.processed_files)}개 로드 완료")
        except Exception as e:
            logger.warning(f"⚠️ 처리된 파일 로드 실패: {e}")
            self.processed_files = set()
    
    def save_processed_files(self):
        """처리된 파일 목록 저장"""
        try:
            processed_file = "data/processed_files.json"
            os.makedirs(os.path.dirname(processed_file), exist_ok=True)
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(list(self.processed_files), f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ 처리된 파일 저장 실패: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """파일 해시 계산"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"❌ 파일 해시 계산 실패: {e}")
            return ""
    
    def scan_augmented_files(self) -> List[Dict]:
        """증강된 파일 스캔"""
        try:
            augmented_files = []
            
            if not os.path.exists(self.augmented_data_dir):
                logger.warning(f"⚠️ 증강 데이터 디렉토리가 존재하지 않습니다: {self.augmented_data_dir}")
                return augmented_files
            
            for root, dirs, files in os.walk(self.augmented_data_dir):
                for file in files:
                    if file.endswith('.wav'):
                        file_path = os.path.join(root, file)
                        file_hash = self.get_file_hash(file_path)
                        
                        # 이미 처리된 파일인지 확인
                        if file_hash in self.processed_files:
                            continue
                        
                        # 파일 정보 수집
                        file_info = {
                            'file_path': file_path,
                            'file_name': file,
                            'file_hash': file_hash,
                            'file_size': os.path.getsize(file_path),
                            'created_time': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                            'relative_path': os.path.relpath(file_path, self.augmented_data_dir)
                        }
                        
                        # 라벨 추출 (파일명에서)
                        label = self.extract_label_from_filename(file)
                        file_info['suggested_label'] = label
                        
                        augmented_files.append(file_info)
            
            logger.info(f"🔍 증강된 파일 {len(augmented_files)}개 발견")
            return augmented_files
            
        except Exception as e:
            logger.error(f"❌ 증강 파일 스캔 실패: {e}")
            return []
    
    def extract_label_from_filename(self, filename: str) -> str:
        """파일명에서 라벨 추출"""
        try:
            # 파일명 패턴 분석
            if 'normal' in filename.lower():
                return 'normal'
            elif 'abnormal' in filename.lower():
                if 'bearing' in filename.lower():
                    return 'critical'
                elif 'overload' in filename.lower():
                    return 'critical'
                elif 'unbalance' in filename.lower():
                    return 'warning'
                elif 'friction' in filename.lower():
                    return 'warning'
                else:
                    return 'critical'
            else:
                return 'unknown'
        except Exception as e:
            logger.warning(f"⚠️ 라벨 추출 실패: {e}")
            return 'unknown'
    
    def prepare_for_labeling(self, file_info: Dict) -> bool:
        """라벨링을 위한 파일 준비"""
        try:
            # 라벨링 준비 디렉토리로 복사
            dest_path = os.path.join(self.labeling_ready_dir, file_info['file_name'])
            
            # 파일 복사
            import shutil
            shutil.copy2(file_info['file_path'], dest_path)
            
            # 메타데이터 파일 생성
            metadata = {
                'original_path': file_info['file_path'],
                'file_name': file_info['file_name'],
                'file_size': file_info['file_size'],
                'created_time': file_info['created_time'],
                'suggested_label': file_info['suggested_label'],
                'prepared_time': datetime.now().isoformat(),
                'status': 'ready_for_labeling'
            }
            
            metadata_path = dest_path.replace('.wav', '_metadata.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 라벨링 준비 완료: {file_info['file_name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 라벨링 준비 실패: {e}")
            return False
    
    def upload_to_labeling_server(self, file_info: Dict) -> bool:
        """라벨링 서버에 업로드"""
        try:
            # 라벨링 서버 상태 확인
            if not self.check_labeling_server():
                logger.error("❌ 라벨링 서버가 응답하지 않습니다")
                return False
            
            # 파일 업로드
            file_path = os.path.join(self.labeling_ready_dir, file_info['file_name'])
            
            if not os.path.exists(file_path):
                logger.error(f"❌ 파일이 존재하지 않습니다: {file_path}")
                return False
            
            # 업로드 요청
            with open(file_path, 'rb') as f:
                files = {'audio': (file_info['file_name'], f, 'audio/wav')}
                data = {
                    'fileName': file_info['file_name'],
                    'suggestedLabel': file_info['suggested_label'],
                    'fileSize': file_info['file_size'],
                    'createdTime': file_info['created_time'],
                    'status': 'ready_for_labeling'
                }
                
                response = requests.post(
                    f"{self.labeling_server_url}/api/labeling/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info(f"✅ 라벨링 서버 업로드 완료: {file_info['file_name']}")
                    return True
                else:
                    logger.error(f"❌ 업로드 실패: {result.get('message', 'Unknown error')}")
                    return False
            else:
                logger.error(f"❌ 업로드 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 라벨링 서버 업로드 오류: {e}")
            return False
    
    def check_labeling_server(self) -> bool:
        """라벨링 서버 상태 확인"""
        try:
            response = requests.get(f"{self.labeling_server_url}/api/labeling/stats", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"⚠️ 라벨링 서버 상태 확인 실패: {e}")
            return False
    
    def process_single_file(self, file_info: Dict) -> bool:
        """단일 파일 처리"""
        try:
            logger.info(f"🔄 파일 처리 시작: {file_info['file_name']}")
            
            # 1. 라벨링 준비
            if not self.prepare_for_labeling(file_info):
                return False
            
            # 2. 라벨링 서버 업로드
            if not self.upload_to_labeling_server(file_info):
                return False
            
            # 3. 처리 완료 표시
            self.processed_files.add(file_info['file_hash'])
            self.save_processed_files()
            
            logger.info(f"✅ 파일 처리 완료: {file_info['file_name']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 처리 실패: {e}")
            return False
    
    def run_pipeline(self, max_files: Optional[int] = None) -> Dict:
        """파이프라인 실행"""
        try:
            logger.info("🚀 자동 라벨링 파이프라인 시작")
            
            # 1. 증강된 파일 스캔
            augmented_files = self.scan_augmented_files()
            
            if not augmented_files:
                logger.info("📭 처리할 증강 파일이 없습니다")
                return {'success': True, 'processed': 0, 'failed': 0}
            
            # 2. 파일 수 제한
            if max_files:
                augmented_files = augmented_files[:max_files]
                logger.info(f"📊 최대 {max_files}개 파일로 제한")
            
            # 3. 파일 처리
            processed_count = 0
            failed_count = 0
            
            for file_info in augmented_files:
                if self.process_single_file(file_info):
                    processed_count += 1
                else:
                    failed_count += 1
                
                # 처리 간격 (서버 부하 방지)
                time.sleep(0.5)
            
            # 4. 결과 요약
            result = {
                'success': True,
                'total_found': len(augmented_files),
                'processed': processed_count,
                'failed': failed_count,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"🎉 파이프라인 완료: {processed_count}개 성공, {failed_count}개 실패")
            return result
            
        except Exception as e:
            logger.error(f"❌ 파이프라인 실행 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_continuous(self, interval: int = 60):
        """연속 실행 (파일 감시)"""
        logger.info(f"🔄 연속 실행 모드 시작 (간격: {interval}초)")
        
        try:
            while True:
                logger.info("🔍 새로운 증강 파일 검색 중...")
                result = self.run_pipeline()
                
                if result['success']:
                    logger.info(f"✅ 처리 완료: {result['processed']}개 파일")
                else:
                    logger.error(f"❌ 처리 실패: {result.get('error', 'Unknown error')}")
                
                logger.info(f"⏰ {interval}초 후 다시 검색...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 연속 실행 중단됨")
        except Exception as e:
            logger.error(f"❌ 연속 실행 오류: {e}")

def main():
    parser = argparse.ArgumentParser(description='자동 라벨링 파이프라인')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                       help='실행 모드: single (한 번 실행) 또는 continuous (연속 실행)')
    parser.add_argument('--max-files', type=int, help='최대 처리 파일 수')
    parser.add_argument('--interval', type=int, default=60, help='연속 실행 간격 (초)')
    parser.add_argument('--server-url', default='http://localhost:3000',
                       help='라벨링 서버 URL')
    parser.add_argument('--augmented-dir', default='data/augmented_audio',
                       help='증강 데이터 디렉토리')
    parser.add_argument('--labeling-dir', default='data/labeling_ready',
                       help='라벨링 준비 디렉토리')
    
    args = parser.parse_args()
    
    # 파이프라인 초기화
    pipeline = AutoLabelingPipeline(
        labeling_server_url=args.server_url,
        augmented_data_dir=args.augmented_dir,
        labeling_ready_dir=args.labeling_dir
    )
    
    # 실행
    if args.mode == 'single':
        result = pipeline.run_pipeline(max_files=args.max_files)
        if result['success']:
            print(f"✅ 파이프라인 완료: {result['processed']}개 파일 처리")
            sys.exit(0)
        else:
            print(f"❌ 파이프라인 실패: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    else:
        pipeline.run_continuous(interval=args.interval)

if __name__ == "__main__":
    main()
