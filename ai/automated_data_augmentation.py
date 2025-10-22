#!/usr/bin/env python3
"""
자동화된 데이터 증강 스크립트
실제 오디오 파일을 증강하고 자동으로 라벨링 서버에 업로드
"""

import os
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
import logging

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.data_augmentation import AudioAugmentation
from ai.auto_labeling_pipeline import AutoLabelingPipeline

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automated_augmentation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomatedDataAugmentation:
    """자동화된 데이터 증강 시스템"""
    
    def __init__(self, 
                 input_dir: str = "data/real_audio_uploads",
                 output_dir: str = "data/augmented_audio",
                 labeling_server_url: str = "http://localhost:3000"):
        
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.labeling_server_url = labeling_server_url
        
        # 디렉토리 생성
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # 컴포넌트 초기화
        self.augmenter = AudioAugmentation()
        self.pipeline = AutoLabelingPipeline(
            labeling_server_url=labeling_server_url,
            augmented_data_dir=output_dir
        )
        
        logger.info("🚀 자동화된 데이터 증강 시스템 초기화 완료")
        logger.info(f"   입력 디렉토리: {self.input_dir}")
        logger.info(f"   출력 디렉토리: {self.output_dir}")
        logger.info(f"   라벨링 서버: {labeling_server_url}")
    
    def scan_input_files(self) -> list:
        """입력 디렉토리에서 오디오 파일 스캔"""
        try:
            audio_files = []
            
            if not os.path.exists(self.input_dir):
                logger.warning(f"⚠️ 입력 디렉토리가 존재하지 않습니다: {self.input_dir}")
                return audio_files
            
            for root, dirs, files in os.walk(self.input_dir):
                for file in files:
                    if file.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
                        file_path = os.path.join(root, file)
                        audio_files.append(file_path)
            
            logger.info(f"🔍 입력 파일 {len(audio_files)}개 발견")
            return audio_files
            
        except Exception as e:
            logger.error(f"❌ 입력 파일 스캔 실패: {e}")
            return []
    
    def extract_label_from_filename(self, filename: str) -> str:
        """파일명에서 라벨 추출"""
        try:
            filename_lower = filename.lower()
            
            if 'normal' in filename_lower:
                if 'compressor' in filename_lower:
                    return 'normal_compressor'
                elif 'fan' in filename_lower:
                    return 'normal_fan'
                elif 'motor' in filename_lower:
                    return 'normal_motor'
                else:
                    return 'normal'
            elif 'abnormal' in filename_lower:
                if 'bearing' in filename_lower:
                    return 'abnormal_bearing'
                elif 'overload' in filename_lower:
                    return 'abnormal_overload'
                elif 'unbalance' in filename_lower:
                    return 'abnormal_unbalance'
                elif 'friction' in filename_lower:
                    return 'abnormal_friction'
                else:
                    return 'abnormal'
            else:
                return 'unknown'
                
        except Exception as e:
            logger.warning(f"⚠️ 라벨 추출 실패: {e}")
            return 'unknown'
    
    def augment_single_file(self, input_file: str, augmentation_count: int = 10) -> bool:
        """단일 파일 증강"""
        try:
            logger.info(f"🔄 파일 증강 시작: {os.path.basename(input_file)}")
            
            # 라벨 추출
            label = self.extract_label_from_filename(input_file)
            logger.info(f"🏷️ 추출된 라벨: {label}")
            
            # 출력 디렉토리 생성 (라벨별)
            label_output_dir = os.path.join(self.output_dir, label)
            os.makedirs(label_output_dir, exist_ok=True)
            
            # 증강 실행
            success = self.augmenter.generate_augmented_data(
                input_file=input_file,
                output_dir=label_output_dir,
                count=augmentation_count,
                label=label
            )
            
            if success:
                logger.info(f"✅ 파일 증강 완료: {os.path.basename(input_file)}")
                return True
            else:
                logger.error(f"❌ 파일 증강 실패: {os.path.basename(input_file)}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 파일 증강 오류: {e}")
            return False
    
    def run_augmentation_pipeline(self, 
                                 max_files: int = None, 
                                 augmentation_count: int = 10) -> dict:
        """증강 파이프라인 실행"""
        try:
            logger.info("🚀 자동화된 데이터 증강 파이프라인 시작")
            
            # 1. 입력 파일 스캔
            input_files = self.scan_input_files()
            
            if not input_files:
                logger.info("📭 증강할 입력 파일이 없습니다")
                return {'success': True, 'processed': 0, 'failed': 0}
            
            # 2. 파일 수 제한
            if max_files:
                input_files = input_files[:max_files]
                logger.info(f"📊 최대 {max_files}개 파일로 제한")
            
            # 3. 파일 증강
            processed_count = 0
            failed_count = 0
            
            for input_file in input_files:
                if self.augment_single_file(input_file, augmentation_count):
                    processed_count += 1
                else:
                    failed_count += 1
                
                # 처리 간격
                time.sleep(1)
            
            # 4. 증강된 파일을 라벨링 서버에 업로드
            logger.info("📤 증강된 파일을 라벨링 서버에 업로드 중...")
            upload_result = self.pipeline.run_pipeline()
            
            # 5. 결과 요약
            result = {
                'success': True,
                'input_files': len(input_files),
                'processed': processed_count,
                'failed': failed_count,
                'upload_result': upload_result,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"🎉 증강 파이프라인 완료: {processed_count}개 성공, {failed_count}개 실패")
            return result
            
        except Exception as e:
            logger.error(f"❌ 증강 파이프라인 실행 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_continuous(self, 
                      interval: int = 300,  # 5분 간격
                      augmentation_count: int = 10):
        """연속 실행 (파일 감시)"""
        logger.info(f"🔄 연속 실행 모드 시작 (간격: {interval}초)")
        
        try:
            while True:
                logger.info("🔍 새로운 입력 파일 검색 중...")
                result = self.run_augmentation_pipeline(augmentation_count=augmentation_count)
                
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
    parser = argparse.ArgumentParser(description='자동화된 데이터 증강 시스템')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                       help='실행 모드: single (한 번 실행) 또는 continuous (연속 실행)')
    parser.add_argument('--input-dir', default='data/real_audio_uploads',
                       help='입력 오디오 파일 디렉토리')
    parser.add_argument('--output-dir', default='data/augmented_audio',
                       help='증강된 파일 출력 디렉토리')
    parser.add_argument('--max-files', type=int, help='최대 처리 파일 수')
    parser.add_argument('--augmentation-count', type=int, default=10,
                       help='파일당 증강 개수')
    parser.add_argument('--interval', type=int, default=300,
                       help='연속 실행 간격 (초)')
    parser.add_argument('--server-url', default='http://localhost:3000',
                       help='라벨링 서버 URL')
    
    args = parser.parse_args()
    
    # 시스템 초기화
    system = AutomatedDataAugmentation(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        labeling_server_url=args.server_url
    )
    
    # 실행
    if args.mode == 'single':
        result = system.run_augmentation_pipeline(
            max_files=args.max_files,
            augmentation_count=args.augmentation_count
        )
        
        if result['success']:
            print(f"✅ 증강 파이프라인 완료: {result['processed']}개 파일 처리")
            sys.exit(0)
        else:
            print(f"❌ 증강 파이프라인 실패: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    else:
        system.run_continuous(
            interval=args.interval,
            augmentation_count=args.augmentation_count
        )

if __name__ == "__main__":
    main()
