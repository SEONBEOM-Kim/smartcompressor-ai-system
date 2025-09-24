#!/usr/bin/env python3
"""
데이터 수집 시뮬레이터 (data_collector.py)
듀얼 마이크 환경을 시뮬레이션하여 오디오 데이터를 수집하고 전처리합니다.
"""

import os
import librosa
import numpy as np
import soundfile as sf
from datetime import datetime
import argparse
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCollector:
    """듀얼 마이크 환경 시뮬레이터"""
    
    def __init__(self, sample_rate=22050, duration=5.0):
        """
        Args:
            sample_rate (int): 샘플링 레이트 (기본값: 22050Hz)
            duration (float): 수집할 오디오 길이 (초, 기본값: 5.0초)
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.samples = int(sample_rate * duration)
        
    def collect_audio_data(self, target_audio_path, noise_audio_path, output_dir="data/raw"):
        """
        듀얼 마이크 환경을 시뮬레이션하여 오디오 데이터를 수집합니다.
        
        Args:
            target_audio_path (str): 타겟 오디오 파일 경로
            noise_audio_path (str): 노이즈 오디오 파일 경로
            output_dir (str): 출력 디렉토리
            
        Returns:
            tuple: (target_with_noise_path, noise_only_path)
        """
        try:
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 타겟 오디오 로드 및 전처리
            logger.info(f"타겟 오디오 로딩: {target_audio_path}")
            target_audio, _ = librosa.load(target_audio_path, sr=self.sample_rate, duration=self.duration)
            
            # 노이즈 오디오 로드 및 전처리
            logger.info(f"노이즈 오디오 로딩: {noise_audio_path}")
            noise_audio, _ = librosa.load(noise_audio_path, sr=self.sample_rate, duration=self.duration)
            
            # 길이 맞추기 (더 짧은 길이에 맞춤)
            min_length = min(len(target_audio), len(noise_audio))
            target_audio = target_audio[:min_length]
            noise_audio = noise_audio[:min_length]
            
            # 타겟 + 노이즈 합성 (실제 듀얼 마이크 환경 시뮬레이션)
            target_with_noise = target_audio + noise_audio
            
            # 정규화 (클리핑 방지)
            target_with_noise = self._normalize_audio(target_with_noise)
            noise_only = self._normalize_audio(noise_audio)
            
            # 타임스탬프 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 파일 저장
            target_with_noise_path = os.path.join(output_dir, f"target_with_noise_{timestamp}.wav")
            noise_only_path = os.path.join(output_dir, f"noise_only_{timestamp}.wav")
            
            sf.write(target_with_noise_path, target_with_noise, self.sample_rate)
            sf.write(noise_only_path, noise_only, self.sample_rate)
            
            logger.info(f"수집 완료:")
            logger.info(f"  - 타겟+노이즈: {target_with_noise_path}")
            logger.info(f"  - 노이즈만: {noise_only_path}")
            
            return target_with_noise_path, noise_only_path
            
        except Exception as e:
            logger.error(f"오디오 데이터 수집 중 오류 발생: {e}")
            raise
    
    def _normalize_audio(self, audio):
        """오디오 정규화 (클리핑 방지)"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val * 0.95  # 95%로 제한하여 여유 공간 확보
        return audio
    
    def simulate_dual_mic_environment(self, target_audio_path, noise_audio_path, 
                                    mic_distance=0.1, output_dir="data/raw"):
        """
        실제 듀얼 마이크 환경을 더 정확하게 시뮬레이션합니다.
        
        Args:
            target_audio_path (str): 타겟 오디오 파일 경로
            noise_audio_path (str): 노이즈 오디오 파일 경로
            mic_distance (float): 마이크 간 거리 (미터)
            output_dir (str): 출력 디렉토리
        """
        try:
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 오디오 로드
            target_audio, _ = librosa.load(target_audio_path, sr=self.sample_rate, duration=self.duration)
            noise_audio, _ = librosa.load(noise_audio_path, sr=self.sample_rate, duration=self.duration)
            
            # 길이 맞추기
            min_length = min(len(target_audio), len(noise_audio))
            target_audio = target_audio[:min_length]
            noise_audio = noise_audio[:min_length]
            
            # 마이크 간 거리에 따른 지연 시뮬레이션 (소리 속도: 343m/s)
            sound_speed = 343.0  # m/s
            delay_samples = int(mic_distance / sound_speed * self.sample_rate)
            
            # 노이즈에 지연 적용
            if delay_samples > 0:
                noise_delayed = np.pad(noise_audio, (delay_samples, 0), mode='constant')
                noise_delayed = noise_delayed[:len(target_audio)]
            else:
                noise_delayed = noise_audio
            
            # 듀얼 마이크 시뮬레이션
            # 마이크 1: 타겟 + 노이즈 (주 마이크)
            mic1_signal = target_audio + noise_delayed * 0.7
            
            # 마이크 2: 노이즈만 (참조 마이크)
            mic2_signal = noise_delayed * 0.8
            
            # 정규화
            mic1_signal = self._normalize_audio(mic1_signal)
            mic2_signal = self._normalize_audio(mic2_signal)
            
            # 타임스탬프 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 파일 저장
            mic1_path = os.path.join(output_dir, f"mic1_target_with_noise_{timestamp}.wav")
            mic2_path = os.path.join(output_dir, f"mic2_noise_only_{timestamp}.wav")
            
            sf.write(mic1_path, mic1_signal, self.sample_rate)
            sf.write(mic2_path, mic2_signal, self.sample_rate)
            
            logger.info(f"듀얼 마이크 시뮬레이션 완료:")
            logger.info(f"  - 마이크 1 (타겟+노이즈): {mic1_path}")
            logger.info(f"  - 마이크 2 (노이즈만): {mic2_path}")
            
            return mic1_path, mic2_path
            
        except Exception as e:
            logger.error(f"듀얼 마이크 시뮬레이션 중 오류 발생: {e}")
            raise

def main():
    """메인 함수 - CLI 인터페이스"""
    parser = argparse.ArgumentParser(description='듀얼 마이크 환경 오디오 데이터 수집 시뮬레이터')
    parser.add_argument('--target', required=True, help='타겟 오디오 파일 경로')
    parser.add_argument('--noise', required=True, help='노이즈 오디오 파일 경로')
    parser.add_argument('--output', default='data/raw', help='출력 디렉토리 (기본값: data/raw)')
    parser.add_argument('--duration', type=float, default=5.0, help='수집할 오디오 길이 (초, 기본값: 5.0)')
    parser.add_argument('--sample-rate', type=int, default=22050, help='샘플링 레이트 (기본값: 22050)')
    parser.add_argument('--dual-mic', action='store_true', help='듀얼 마이크 환경 시뮬레이션 사용')
    parser.add_argument('--mic-distance', type=float, default=0.1, help='마이크 간 거리 (미터, 기본값: 0.1)')
    
    args = parser.parse_args()
    
    # 파일 존재 확인
    if not os.path.exists(args.target):
        logger.error(f"타겟 오디오 파일을 찾을 수 없습니다: {args.target}")
        return
    
    if not os.path.exists(args.noise):
        logger.error(f"노이즈 오디오 파일을 찾을 수 없습니다: {args.noise}")
        return
    
    # 데이터 수집기 초기화
    collector = DataCollector(sample_rate=args.sample_rate, duration=args.duration)
    
    try:
        if args.dual_mic:
            # 듀얼 마이크 시뮬레이션
            mic1_path, mic2_path = collector.simulate_dual_mic_environment(
                args.target, args.noise, args.mic_distance, args.output
            )
            print(f"\n✅ 듀얼 마이크 시뮬레이션 완료!")
            print(f"📁 마이크 1 (타겟+노이즈): {mic1_path}")
            print(f"📁 마이크 2 (노이즈만): {mic2_path}")
        else:
            # 기본 수집
            target_with_noise_path, noise_only_path = collector.collect_audio_data(
                args.target, args.noise, args.output
            )
            print(f"\n✅ 오디오 데이터 수집 완료!")
            print(f"📁 타겟+노이즈: {target_with_noise_path}")
            print(f"📁 노이즈만: {noise_only_path}")
            
    except Exception as e:
        logger.error(f"데이터 수집 실패: {e}")
        return

if __name__ == "__main__":
    main()
