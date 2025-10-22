#!/usr/bin/env python3
"""
MIMII 데이터셋 다운로드 및 전처리 스크립트
"""

import os
import requests
import zipfile
import tarfile
import numpy as np
import soundfile as sf
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MIMIIDownloader:
    def __init__(self, data_dir="data/mimii"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # MIMII 데이터셋 URL (공개 데이터셋)
        self.datasets = {
            "fan": "https://zenodo.org/record/3384388/files/DCASE2019task2_fan.zip",
            "pump": "https://zenodo.org/record/3384388/files/DCASE2019task2_pump.zip", 
            "slider": "https://zenodo.org/record/3384388/files/DCASE2019task2_slider.zip",
            "valve": "https://zenodo.org/record/3384388/files/DCASE2019task2_valve.zip"
        }
    
    def download_file(self, url, filename):
        """파일 다운로드"""
        filepath = self.data_dir / filename
        
        if filepath.exists():
            logger.info(f"파일이 이미 존재합니다: {filename}")
            return filepath
            
        logger.info(f"다운로드 중: {filename}")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"다운로드 완료: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"다운로드 실패: {e}")
            return None
    
    def extract_archive(self, filepath):
        """압축 파일 추출"""
        extract_dir = self.data_dir / filepath.stem
        
        if extract_dir.exists():
            logger.info(f"이미 추출됨: {extract_dir}")
            return extract_dir
            
        logger.info(f"추출 중: {filepath.name}")
        try:
            if filepath.suffix == '.zip':
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(self.data_dir)
            elif filepath.suffix in ['.tar', '.gz']:
                with tarfile.open(filepath, 'r') as tar_ref:
                    tar_ref.extractall(self.data_dir)
            
            logger.info(f"추출 완료: {extract_dir}")
            return extract_dir
        except Exception as e:
            logger.error(f"추출 실패: {e}")
            return None
    
    def preprocess_audio(self, audio_dir):
        """오디오 전처리"""
        processed_dir = self.data_dir / "processed"
        processed_dir.mkdir(exist_ok=True)
        
        logger.info("오디오 전처리 시작...")
        
        for audio_file in audio_dir.rglob("*.wav"):
            try:
                # 오디오 로드
                audio, sr = sf.read(audio_file)
                
                # 16kHz로 리샘플링 (필요한 경우)
                if sr != 16000:
                    from scipy import signal
                    audio = signal.resample(audio, int(len(audio) * 16000 / sr))
                    sr = 16000
                
                # 정규화
                audio = audio / np.max(np.abs(audio))
                
                # 저장
                rel_path = audio_file.relative_to(audio_dir)
                output_path = processed_dir / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                sf.write(output_path, audio, sr)
                
            except Exception as e:
                logger.warning(f"오디오 처리 실패: {audio_file} - {e}")
        
        logger.info("오디오 전처리 완료")
        return processed_dir
    
    def download_all(self):
        """모든 데이터셋 다운로드 및 전처리"""
        logger.info("MIMII 데이터셋 다운로드 시작...")
        
        for machine_type, url in self.datasets.items():
            logger.info(f"처리 중: {machine_type}")
            
            # 다운로드
            filename = f"{machine_type}.zip"
            filepath = self.download_file(url, filename)
            
            if filepath:
                # 추출
                extract_dir = self.extract_archive(filepath)
                
                if extract_dir:
                    # 전처리
                    self.preprocess_audio(extract_dir)
        
        logger.info("MIMII 데이터셋 준비 완료!")

if __name__ == "__main__":
    downloader = MIMIIDownloader()
    downloader.download_all()
