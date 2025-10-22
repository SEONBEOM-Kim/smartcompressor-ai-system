#!/usr/bin/env python3
"""
고품질 오디오 합성 엔진 - MIMII 기반 현실적인 합성음 생성
"""

import numpy as np
import soundfile as sf
from pathlib import Path
import logging
from typing import List, Dict, Tuple, Optional
import random
from scipy import signal
from scipy.signal import butter, filtfilt
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedAudioSynthesis:
    def __init__(self, mimii_data_dir="data/mimii_samples"):
        self.mimii_data_dir = Path(mimii_data_dir)
        self.features_cache = {}
        self.load_mimii_features()
        
    def load_mimii_features(self):
        """MIMII 특징 데이터 로드"""
        features_file = self.mimii_data_dir / "dataset_features.json"
        if features_file.exists():
            with open(features_file, 'r') as f:
                self.features_cache = json.load(f)
            logger.info(f"MIMII 특징 데이터 로드 완료: {len(self.features_cache)}개")
        else:
            logger.warning("MIMII 특징 데이터가 없습니다. 기본값을 사용합니다.")
            self.features_cache = []
    
    def synthesize_compressor_audio(self, 
                                  base_audio: np.ndarray, 
                                  sr: int,
                                  target_duration: float = 3.0,
                                  quality_level: str = "high") -> np.ndarray:
        """압축기 오디오 합성"""
        
        # 기본 길이 조정
        target_samples = int(target_duration * sr)
        if len(base_audio) > target_samples:
            # 랜덤 세그먼트 선택
            start_idx = random.randint(0, len(base_audio) - target_samples)
            base_audio = base_audio[start_idx:start_idx + target_samples]
        else:
            # 패딩 또는 반복
            repeat_times = int(np.ceil(target_samples / len(base_audio)))
            base_audio = np.tile(base_audio, repeat_times)[:target_samples]
        
        # 품질별 처리
        if quality_level == "high":
            return self._high_quality_synthesis(base_audio, sr)
        elif quality_level == "medium":
            return self._medium_quality_synthesis(base_audio, sr)
        else:
            return self._basic_synthesis(base_audio, sr)
    
    def _high_quality_synthesis(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """고품질 합성"""
        # 1. 스펙트럼 분석
        fft = np.fft.fft(audio)
        magnitude = np.abs(fft)
        phase = np.angle(fft)
        
        # 2. 하모닉 구조 강화
        enhanced_magnitude = self._enhance_harmonics(magnitude, sr)
        
        # 3. 노이즈 레이어 추가 (현실적인 배경음)
        noise_layer = self._generate_realistic_noise(len(audio), sr)
        
        # 4. 스펙트럼 복원
        enhanced_fft = enhanced_magnitude * np.exp(1j * phase)
        enhanced_audio = np.real(np.fft.ifft(enhanced_fft))
        
        # 5. 노이즈 믹싱
        mixed_audio = self._mix_audio_layers(enhanced_audio, noise_layer, 0.7)
        
        # 6. 동적 범위 압축
        compressed_audio = self._apply_compression(mixed_audio)
        
        # 7. 최종 정규화
        return self._normalize_audio(compressed_audio)
    
    def _medium_quality_synthesis(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """중간 품질 합성"""
        # 1. 기본 변형
        audio = self._apply_pitch_shift(audio, sr, random.uniform(0.9, 1.1))
        audio = self._apply_time_stretch(audio, sr, random.uniform(0.95, 1.05))
        
        # 2. 노이즈 추가
        noise = np.random.normal(0, 0.01, len(audio))
        audio = audio + noise
        
        # 3. 필터링
        audio = self._apply_bandpass_filter(audio, sr, 80, 8000)
        
        return self._normalize_audio(audio)
    
    def _basic_synthesis(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """기본 합성 (기존 방식)"""
        # 단순 변형
        volume_factor = random.uniform(0.5, 1.2)
        audio = audio * volume_factor
        
        # 노이즈 추가
        noise = np.random.normal(0, 0.005, len(audio))
        audio = audio + noise
        
        return self._normalize_audio(audio)
    
    def _enhance_harmonics(self, magnitude: np.ndarray, sr: int) -> np.ndarray:
        """하모닉 구조 강화"""
        enhanced = magnitude.copy()
        
        # 기본 주파수 찾기 (가장 강한 주파수)
        freqs = np.fft.fftfreq(len(magnitude), 1/sr)
        positive_freqs = freqs[:len(freqs)//2]
        positive_magnitude = magnitude[:len(magnitude)//2]
        
        # 기본 주파수 찾기
        fundamental_idx = np.argmax(positive_magnitude[10:]) + 10  # 10Hz 이상
        fundamental_freq = positive_freqs[fundamental_idx]
        
        # 하모닉 강화
        for harmonic in range(2, 6):  # 2차~5차 하모닉
            harmonic_freq = fundamental_freq * harmonic
            harmonic_idx = int(harmonic_freq * len(magnitude) / sr)
            
            if harmonic_idx < len(enhanced) // 2:
                # 하모닉 강화
                enhancement_factor = 1.0 + (0.3 / harmonic)  # 고차 하모닉일수록 약하게
                enhanced[harmonic_idx] *= enhancement_factor
                enhanced[-harmonic_idx] *= enhancement_factor  # 대칭성 유지
        
        return enhanced
    
    def _generate_realistic_noise(self, length: int, sr: int) -> np.ndarray:
        """현실적인 배경 노이즈 생성"""
        # 1. 화이트 노이즈
        white_noise = np.random.normal(0, 0.01, length)
        
        # 2. 브라운 노이즈 (저주파 강조)
        brown_noise = np.cumsum(np.random.normal(0, 0.005, length))
        brown_noise = brown_noise / np.max(np.abs(brown_noise)) * 0.02
        
        # 3. 주파수별 필터링
        # 저주파 (0-200Hz): 압축기 기본음
        low_freq = self._apply_bandpass_filter(white_noise, sr, 0, 200) * 0.3
        
        # 중주파 (200-2000Hz): 기계음
        mid_freq = self._apply_bandpass_filter(white_noise, sr, 200, 2000) * 0.2
        
        # 고주파 (2000-8000Hz): 마찰음
        high_freq = self._apply_bandpass_filter(white_noise, sr, 2000, 8000) * 0.1
        
        # 4. 결합
        combined_noise = low_freq + mid_freq + high_freq + brown_noise
        
        return self._normalize_audio(combined_noise) * 0.1  # 전체 볼륨 조절
    
    def _mix_audio_layers(self, main_audio: np.ndarray, noise_audio: np.ndarray, main_ratio: float = 0.7) -> np.ndarray:
        """오디오 레이어 믹싱"""
        # 길이 맞추기
        min_length = min(len(main_audio), len(noise_audio))
        main_audio = main_audio[:min_length]
        noise_audio = noise_audio[:min_length]
        
        # 믹싱
        mixed = main_audio * main_ratio + noise_audio * (1 - main_ratio)
        
        return mixed
    
    def _apply_compression(self, audio: np.ndarray, threshold: float = 0.3, ratio: float = 4.0) -> np.ndarray:
        """동적 범위 압축"""
        compressed = audio.copy()
        
        # 임계값 이상의 신호 압축
        above_threshold = np.abs(audio) > threshold
        compressed[above_threshold] = np.sign(audio[above_threshold]) * (
            threshold + (np.abs(audio[above_threshold]) - threshold) / ratio
        )
        
        return compressed
    
    def _apply_pitch_shift(self, audio: np.ndarray, sr: int, pitch_factor: float) -> np.ndarray:
        """피치 시프트"""
        if pitch_factor == 1.0:
            return audio
        
        # 간단한 피치 시프트 (시간 도메인)
        new_length = int(len(audio) / pitch_factor)
        shifted = signal.resample(audio, new_length)
        
        # 원래 길이로 조정
        if len(shifted) > len(audio):
            return shifted[:len(audio)]
        else:
            # 패딩
            padded = np.zeros(len(audio))
            padded[:len(shifted)] = shifted
            return padded
    
    def _apply_time_stretch(self, audio: np.ndarray, sr: int, stretch_factor: float) -> np.ndarray:
        """시간 스트레치"""
        if stretch_factor == 1.0:
            return audio
        
        new_length = int(len(audio) * stretch_factor)
        stretched = signal.resample(audio, new_length)
        
        # 원래 길이로 조정
        if len(stretched) > len(audio):
            return stretched[:len(audio)]
        else:
            # 패딩
            padded = np.zeros(len(audio))
            padded[:len(stretched)] = stretched
            return padded
    
    def _apply_bandpass_filter(self, audio: np.ndarray, sr: int, low_freq: float, high_freq: float) -> np.ndarray:
        """대역통과 필터"""
        nyquist = sr / 2
        low = low_freq / nyquist
        high = high_freq / nyquist
        
        # Butterworth 필터
        b, a = butter(4, [low, high], btype='band')
        filtered = filtfilt(b, a, audio)
        
        return filtered
    
    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """오디오 정규화"""
        if np.max(np.abs(audio)) == 0:
            return audio
        
        # 정규화 (클리핑 방지)
        normalized = audio / np.max(np.abs(audio)) * 0.95
        return normalized
    
    def generate_augmented_dataset(self, 
                                 source_audio: np.ndarray, 
                                 sr: int,
                                 num_augmentations: int = 20,
                                 quality_level: str = "high") -> List[np.ndarray]:
        """증강 데이터셋 생성"""
        logger.info(f"증강 데이터셋 생성 시작: {num_augmentations}개, 품질: {quality_level}")
        
        augmented_samples = []
        
        for i in range(num_augmentations):
            try:
                # 랜덤 시드 설정
                random.seed(i)
                np.random.seed(i)
                
                # 합성 오디오 생성
                synthetic_audio = self.synthesize_compressor_audio(
                    source_audio, sr, 
                    target_duration=3.0,
                    quality_level=quality_level
                )
                
                augmented_samples.append(synthetic_audio)
                
                if (i + 1) % 5 == 0:
                    logger.info(f"진행률: {i + 1}/{num_augmentations}")
                    
            except Exception as e:
                logger.error(f"증강 실패 ({i + 1}): {e}")
                continue
        
        logger.info(f"증강 완료: {len(augmented_samples)}개 샘플 생성")
        return augmented_samples

if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path
    
    # CLI 인자 파싱
    parser = argparse.ArgumentParser(description='고품질 오디오 합성 엔진')
    parser.add_argument('--input', required=True, help='입력 오디오 파일 경로')
    parser.add_argument('--output-dir', required=True, help='출력 디렉토리')
    parser.add_argument('--count', type=int, default=20, help='생성할 샘플 수')
    parser.add_argument('--duration', type=float, default=3.0, help='세그먼트 길이 (초)')
    parser.add_argument('--quality', choices=['high', 'medium', 'basic'], default='high', help='합성 품질')
    parser.add_argument('--label', default='unknown', help='데이터 라벨')
    
    args = parser.parse_args()
    
    try:
        # 입력 파일 확인
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"오류: 입력 파일을 찾을 수 없습니다: {args.input}")
            sys.exit(1)
        
        # 출력 디렉토리 생성
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 오디오 로드
        audio, sr = sf.read(input_path)
        print(f"입력 오디오 로드: {len(audio)} 샘플, {sr}Hz")
        
        # 합성 엔진 초기화
        synthesis = AdvancedAudioSynthesis()
        
        # 증강 데이터셋 생성
        augmented_samples = synthesis.generate_augmented_dataset(
            audio, sr, 
            num_augmentations=args.count,
            quality_level=args.quality
        )
        
        # 파일 저장
        timestamp = input_path.stem
        saved_files = []
        
        for i, sample in enumerate(augmented_samples):
            output_filename = f"{args.label}_synthetic_{timestamp}_{i+1:03d}.wav"
            output_path = output_dir / output_filename
            
            sf.write(output_path, sample, sr)
            saved_files.append(str(output_path))
            
            print(f"저장 완료 ({i+1}/{len(augmented_samples)}): {output_filename}")
        
        print(f"합성 완료: {len(saved_files)}개 파일 생성")
        print(f"출력 디렉토리: {output_dir}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)
