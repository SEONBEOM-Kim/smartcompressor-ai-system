#!/usr/bin/env python3
"""
MIMII 샘플 데이터 다운로더 - 필요한 만큼만 선별적 다운로드
"""

import os
import requests
import zipfile
import numpy as np
import soundfile as sf
from pathlib import Path
import logging
import random
from typing import List, Dict, Tuple

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MIMIISampleDownloader:
    def __init__(self, data_dir="data/mimii_samples"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # MIMII 샘플 데이터 URL (작은 샘플만)
        self.sample_urls = {
            "fan_normal": "https://zenodo.org/record/3384388/files/fan_train_normal_00000000.wav",
            "fan_anomaly": "https://zenodo.org/record/3384388/files/fan_train_anomaly_00000000.wav",
            "pump_normal": "https://zenodo.org/record/3384388/files/pump_train_normal_00000000.wav", 
            "pump_anomaly": "https://zenodo.org/record/3384388/files/pump_train_anomaly_00000000.wav"
        }
        
        # 압축기와 유사한 기계 타입
        self.compressor_like_machines = ["fan", "pump"]
        
    def download_sample(self, url: str, filename: str) -> bool:
        """단일 샘플 파일 다운로드"""
        filepath = self.data_dir / filename
        
        if filepath.exists():
            logger.info(f"파일이 이미 존재합니다: {filename}")
            return True
            
        try:
            logger.info(f"다운로드 중: {filename}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
                
            logger.info(f"다운로드 완료: {filename}")
            return True
        except Exception as e:
            logger.error(f"다운로드 실패: {filename} - {e}")
            return False
    
    def generate_synthetic_samples(self, num_samples: int = 20) -> List[Path]:
        """기존 샘플을 기반으로 합성 샘플 생성"""
        synthetic_dir = self.data_dir / "synthetic"
        synthetic_dir.mkdir(exist_ok=True)
        
        generated_files = []
        
        # 기존 샘플 파일들 찾기
        sample_files = list(self.data_dir.glob("*.wav"))
        
        if not sample_files:
            logger.warning("기존 샘플 파일이 없습니다. 먼저 샘플을 다운로드하세요.")
            return generated_files
        
        logger.info(f"{num_samples}개의 합성 샘플 생성 중...")
        
        for i in range(num_samples):
            try:
                # 랜덤하게 샘플 선택
                source_file = random.choice(sample_files)
                
                # 오디오 로드
                audio, sr = sf.read(source_file)
                
                # 다양한 변형 적용
                augmented_audio = self._apply_variations(audio, sr, i)
                
                # 저장
                output_filename = f"synthetic_{i:03d}_{source_file.stem}.wav"
                output_path = synthetic_dir / output_filename
                
                sf.write(output_path, augmented_audio, sr)
                generated_files.append(output_path)
                
                logger.info(f"합성 샘플 생성 완료: {output_filename}")
                
            except Exception as e:
                logger.error(f"합성 샘플 생성 실패: {e}")
        
        return generated_files
    
    def _apply_variations(self, audio: np.ndarray, sr: int, seed: int) -> np.ndarray:
        """오디오에 다양한 변형 적용"""
        np.random.seed(seed)
        
        # 1. 피치 시프트 (0.8 ~ 1.2)
        pitch_factor = np.random.uniform(0.8, 1.2)
        if pitch_factor != 1.0:
            from scipy import signal
            new_length = int(len(audio) / pitch_factor)
            audio = signal.resample(audio, new_length)
        
        # 2. 볼륨 조절 (0.3 ~ 1.5)
        volume_factor = np.random.uniform(0.3, 1.5)
        audio = audio * volume_factor
        
        # 3. 노이즈 추가 (가우시안 노이즈)
        noise_level = np.random.uniform(0.001, 0.01)
        noise = np.random.normal(0, noise_level, len(audio))
        audio = audio + noise
        
        # 4. 시간 스트레치 (0.9 ~ 1.1)
        stretch_factor = np.random.uniform(0.9, 1.1)
        if stretch_factor != 1.0:
            new_length = int(len(audio) * stretch_factor)
            audio = signal.resample(audio, new_length)
        
        # 5. 정규화
        audio = audio / np.max(np.abs(audio)) * 0.8
        
        return audio
    
    def extract_features(self, audio_file: Path) -> Dict:
        """오디오 파일에서 특징 추출"""
        try:
            audio, sr = sf.read(audio_file)
            
            # 기본 통계 특징
            features = {
                'file': str(audio_file),
                'duration': len(audio) / sr,
                'sample_rate': sr,
                'rms': np.sqrt(np.mean(audio**2)),
                'zero_crossing_rate': np.mean(np.abs(np.diff(np.sign(audio)))),
                'spectral_centroid': self._spectral_centroid(audio, sr),
                'spectral_rolloff': self._spectral_rolloff(audio, sr),
                'mfcc': self._extract_mfcc(audio, sr)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"특징 추출 실패: {audio_file} - {e}")
            return {}
    
    def _spectral_centroid(self, audio: np.ndarray, sr: int) -> float:
        """스펙트럼 중심 추출"""
        fft = np.fft.fft(audio)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio), 1/sr)
        
        # 양수 주파수만 사용
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        if np.sum(positive_magnitude) == 0:
            return 0.0
            
        return np.sum(positive_freqs * positive_magnitude) / np.sum(positive_magnitude)
    
    def _spectral_rolloff(self, audio: np.ndarray, sr: int, rolloff_threshold: float = 0.85) -> float:
        """스펙트럼 롤오프 추출"""
        fft = np.fft.fft(audio)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio), 1/sr)
        
        # 양수 주파수만 사용
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        total_energy = np.sum(positive_magnitude)
        cumulative_energy = np.cumsum(positive_magnitude)
        
        rolloff_idx = np.where(cumulative_energy >= rolloff_threshold * total_energy)[0]
        
        if len(rolloff_idx) > 0:
            return positive_freqs[rolloff_idx[0]]
        else:
            return positive_freqs[-1]
    
    def _extract_mfcc(self, audio: np.ndarray, sr: int, n_mfcc: int = 13) -> List[float]:
        """MFCC 특징 추출 (간단한 구현)"""
        try:
            # FFT
            fft = np.fft.fft(audio)
            magnitude = np.abs(fft)
            
            # 멜 스케일 필터뱅크 (간단한 구현)
            n_fft = len(magnitude)
            mel_filters = self._create_mel_filterbank(sr, n_fft, n_mfcc)
            
            # 필터 적용
            mel_spectrum = np.dot(mel_filters, magnitude[:n_fft//2])
            
            # 로그 변환
            log_mel = np.log(mel_spectrum + 1e-10)
            
            # DCT (MFCC)
            mfcc = np.fft.fft(log_mel).real[:n_mfcc]
            
            return mfcc.tolist()
            
        except Exception as e:
            logger.error(f"MFCC 추출 실패: {e}")
            return [0.0] * n_mfcc
    
    def _create_mel_filterbank(self, sr: int, n_fft: int, n_mels: int) -> np.ndarray:
        """멜 스케일 필터뱅크 생성"""
        # 간단한 멜 필터뱅크 구현
        mel_filters = np.zeros((n_mels, n_fft // 2))
        
        # 주파수 범위
        low_freq = 0
        high_freq = sr // 2
        
        # 멜 스케일 변환
        low_mel = 2595 * np.log10(1 + low_freq / 700)
        high_mel = 2595 * np.log10(1 + high_freq / 700)
        
        mel_points = np.linspace(low_mel, high_mel, n_mels + 2)
        freq_points = 700 * (10**(mel_points / 2595) - 1)
        bin_points = np.floor((n_fft + 1) * freq_points / sr).astype(int)
        
        for i in range(1, n_mels + 1):
            left = bin_points[i - 1]
            center = bin_points[i]
            right = bin_points[i + 1]
            
            for j in range(left, center):
                if j < len(mel_filters[i-1]):
                    mel_filters[i-1, j] = (j - left) / (center - left)
            
            for j in range(center, right):
                if j < len(mel_filters[i-1]):
                    mel_filters[i-1, j] = (right - j) / (right - center)
        
        return mel_filters
    
    def download_essential_samples(self) -> bool:
        """필수 샘플만 다운로드"""
        logger.info("MIMII 필수 샘플 다운로드 시작...")
        
        success_count = 0
        for name, url in self.sample_urls.items():
            filename = f"{name}.wav"
            if self.download_sample(url, filename):
                success_count += 1
        
        logger.info(f"다운로드 완료: {success_count}/{len(self.sample_urls)} 파일")
        return success_count > 0
    
    def create_compressor_like_dataset(self, num_samples: int = 50) -> List[Dict]:
        """압축기와 유사한 데이터셋 생성"""
        logger.info(f"압축기 유사 데이터셋 생성 중... ({num_samples}개)")
        
        # 기존 샘플 다운로드
        if not self.download_essential_samples():
            logger.error("필수 샘플 다운로드 실패")
            return []
        
        # 합성 샘플 생성
        synthetic_files = self.generate_synthetic_samples(num_samples)
        
        # 특징 추출
        all_features = []
        
        # 기존 샘플 특징 추출
        for sample_file in self.data_dir.glob("*.wav"):
            if sample_file.name.startswith("synthetic"):
                continue
            features = self.extract_features(sample_file)
            if features:
                features['type'] = 'original'
                all_features.append(features)
        
        # 합성 샘플 특징 추출
        for synthetic_file in synthetic_files:
            features = self.extract_features(synthetic_file)
            if features:
                features['type'] = 'synthetic'
                all_features.append(features)
        
        logger.info(f"데이터셋 생성 완료: {len(all_features)}개 샘플")
        return all_features

if __name__ == "__main__":
    downloader = MIMIISampleDownloader()
    
    # 필수 샘플 다운로드
    if downloader.download_essential_samples():
        # 압축기 유사 데이터셋 생성
        dataset = downloader.create_compressor_like_dataset(30)
        
        # 결과 저장
        import json
        with open("data/mimii_samples/dataset_features.json", "w") as f:
            json.dump(dataset, f, indent=2)
        
        print(f"데이터셋 생성 완료: {len(dataset)}개 샘플")
    else:
        print("샘플 다운로드 실패")
