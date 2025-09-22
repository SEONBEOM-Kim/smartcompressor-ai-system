#!/usr/bin/env python3
"""
1차 정제 및 증류 모듈 (preprocessor.py)
노이즈 제거 및 스펙트로그램 생성을 담당합니다.
"""

import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display
from datetime import datetime
import logging
import argparse

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioPreprocessor:
    """오디오 전처리 및 스펙트로그램 생성 클래스"""
    
    def __init__(self, sample_rate=22050, n_fft=2048, hop_length=512, n_mels=128):
        """
        Args:
            sample_rate (int): 샘플링 레이트
            n_fft (int): FFT 윈도우 크기
            hop_length (int): 홉 길이
            n_mels (int): 멜 스펙트럼 빈 수
        """
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        
    def noise_cancel(self, target_audio_path, noise_audio_path, output_dir="data/processed"):
        """
        노이즈 제거를 수행합니다.
        noise_audio의 위상을 반전시켜 target_audio와 합성하여 배경 소음을 제거합니다.
        
        Args:
            target_audio_path (str): 타겟 오디오 파일 경로
            noise_audio_path (str): 노이즈 오디오 파일 경로
            output_dir (str): 출력 디렉토리
            
        Returns:
            str: 정제된 오디오 파일 경로
        """
        try:
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 오디오 로드
            logger.info(f"타겟 오디오 로딩: {target_audio_path}")
            target_audio, sr = librosa.load(target_audio_path, sr=self.sample_rate)
            
            logger.info(f"노이즈 오디오 로딩: {noise_audio_path}")
            noise_audio, _ = librosa.load(noise_audio_path, sr=sr)
            
            # 길이 맞추기
            min_length = min(len(target_audio), len(noise_audio))
            target_audio = target_audio[:min_length]
            noise_audio = noise_audio[:min_length]
            
            # 노이즈 제거: 위상 반전 기법
            logger.info("노이즈 제거 수행 중...")
            
            # 1. 노이즈의 위상을 반전
            noise_inverted = -noise_audio
            
            # 2. 타겟 오디오와 합성 (노이즈가 상쇄됨)
            clean_audio = target_audio + noise_inverted
            
            # 3. 추가 노이즈 제거: 스펙트럼 차감
            clean_audio = self._spectral_subtraction(target_audio, noise_audio)
            
            # 4. 정규화
            clean_audio = self._normalize_audio(clean_audio)
            
            # 파일 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            clean_audio_path = os.path.join(output_dir, f"clean_audio_{timestamp}.wav")
            
            import soundfile as sf
            sf.write(clean_audio_path, clean_audio, sr)
            
            logger.info(f"노이즈 제거 완료: {clean_audio_path}")
            
            return clean_audio_path
            
        except Exception as e:
            logger.error(f"노이즈 제거 중 오류 발생: {e}")
            raise
    
    def _spectral_subtraction(self, target_audio, noise_audio, alpha=2.0, beta=0.01):
        """
        스펙트럼 차감을 통한 고급 노이즈 제거
        
        Args:
            target_audio (np.array): 타겟 오디오
            noise_audio (np.array): 노이즈 오디오
            alpha (float): 오버 차감 팩터
            beta (float): 바닥 팩터
            
        Returns:
            np.array: 정제된 오디오
        """
        # STFT 변환
        target_stft = librosa.stft(target_audio, n_fft=self.n_fft, hop_length=self.hop_length)
        noise_stft = librosa.stft(noise_audio, n_fft=self.n_fft, hop_length=self.hop_length)
        
        # 크기와 위상 분리
        target_magnitude = np.abs(target_stft)
        target_phase = np.angle(target_stft)
        noise_magnitude = np.abs(noise_stft)
        
        # 노이즈 스펙트럼 추정 (평균)
        noise_spectrum = np.mean(noise_magnitude, axis=1, keepdims=True)
        
        # 스펙트럼 차감
        # |S(ω)| = |Y(ω)| - α|N(ω)|
        # |S(ω)| = max(|S(ω)|, β|Y(ω)|)
        clean_magnitude = target_magnitude - alpha * noise_spectrum
        clean_magnitude = np.maximum(clean_magnitude, beta * target_magnitude)
        
        # 정제된 스펙트럼 재구성
        clean_stft = clean_magnitude * np.exp(1j * target_phase)
        
        # 역 STFT 변환
        clean_audio = librosa.istft(clean_stft, hop_length=self.hop_length)
        
        return clean_audio
    
    def _normalize_audio(self, audio):
        """오디오 정규화"""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val * 0.95
        return audio
    
    def create_spectrogram(self, clean_audio_path, output_dir="data/spectrograms", 
                          image_size=(256, 256), colormap='magma'):
        """
        정제된 오디오에서 스펙트로그램 이미지를 생성합니다.
        
        Args:
            clean_audio_path (str): 정제된 오디오 파일 경로
            output_dir (str): 스펙트로그램 이미지 출력 디렉토리
            image_size (tuple): 이미지 크기 (width, height)
            colormap (str): 컬러맵 ('magma', 'viridis', 'plasma' 등)
            
        Returns:
            str: 생성된 스펙트로그램 이미지 파일 경로
        """
        try:
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 오디오 로드
            logger.info(f"정제된 오디오 로딩: {clean_audio_path}")
            clean_audio, sr = librosa.load(clean_audio_path, sr=self.sample_rate)
            
            # 스펙트로그램 생성
            logger.info("스펙트로그램 생성 중...")
            
            # 멜 스펙트로그램 계산
            mel_spec = librosa.feature.melspectrogram(
                y=clean_audio, 
                sr=sr, 
                n_fft=self.n_fft, 
                hop_length=self.hop_length, 
                n_mels=self.n_mels
            )
            
            # 로그 스케일로 변환
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
            
            # 이미지 생성
            plt.figure(figsize=(image_size[0]/100, image_size[1]/100), dpi=100)
            plt.axis('off')  # 축 제거
            
            # 스펙트로그램 표시
            librosa.display.specshow(
                mel_spec_db, 
                sr=sr, 
                hop_length=self.hop_length,
                x_axis='time', 
                y_axis='mel',
                cmap=colormap
            )
            
            # 이미지 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            spectrogram_path = os.path.join(output_dir, f"spectrogram_{timestamp}.png")
            
            plt.tight_layout(pad=0)
            plt.savefig(spectrogram_path, bbox_inches='tight', pad_inches=0, 
                       facecolor='black', edgecolor='none', dpi=100)
            plt.close()
            
            logger.info(f"스펙트로그램 생성 완료: {spectrogram_path}")
            
            return spectrogram_path
            
        except Exception as e:
            logger.error(f"스펙트로그램 생성 중 오류 발생: {e}")
            raise
    
    def create_multiple_spectrograms(self, clean_audio_path, output_dir="data/spectrograms",
                                   window_sizes=[5.0, 3.0, 1.0], image_size=(256, 256)):
        """
        다양한 윈도우 크기로 여러 스펙트로그램을 생성합니다.
        
        Args:
            clean_audio_path (str): 정제된 오디오 파일 경로
            output_dir (str): 출력 디렉토리
            window_sizes (list): 윈도우 크기들 (초)
            image_size (tuple): 이미지 크기
            
        Returns:
            list: 생성된 스펙트로그램 파일 경로들
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            clean_audio, sr = librosa.load(clean_audio_path, sr=self.sample_rate)
            spectrogram_paths = []
            
            for window_size in window_sizes:
                # 윈도우 크기에 따른 샘플 수 계산
                window_samples = int(window_size * sr)
                
                if len(clean_audio) < window_samples:
                    # 오디오가 윈도우보다 짧으면 패딩
                    padded_audio = np.pad(clean_audio, (0, window_samples - len(clean_audio)), mode='constant')
                else:
                    # 오디오가 윈도우보다 길면 중앙 부분만 사용
                    start = (len(clean_audio) - window_samples) // 2
                    padded_audio = clean_audio[start:start + window_samples]
                
                # 스펙트로그램 생성
                mel_spec = librosa.feature.melspectrogram(
                    y=padded_audio, 
                    sr=sr, 
                    n_fft=self.n_fft, 
                    hop_length=self.hop_length, 
                    n_mels=self.n_mels
                )
                
                mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
                
                # 이미지 생성
                plt.figure(figsize=(image_size[0]/100, image_size[1]/100), dpi=100)
                plt.axis('off')
                
                librosa.display.specshow(
                    mel_spec_db, 
                    sr=sr, 
                    hop_length=self.hop_length,
                    x_axis='time', 
                    y_axis='mel',
                    cmap='magma'
                )
                
                # 파일 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                spectrogram_path = os.path.join(output_dir, f"spectrogram_{window_size}s_{timestamp}.png")
                
                plt.tight_layout(pad=0)
                plt.savefig(spectrogram_path, bbox_inches='tight', pad_inches=0, 
                           facecolor='black', edgecolor='none', dpi=100)
                plt.close()
                
                spectrogram_paths.append(spectrogram_path)
                logger.info(f"스펙트로그램 생성 ({window_size}s): {spectrogram_path}")
            
            return spectrogram_paths
            
        except Exception as e:
            logger.error(f"다중 스펙트로그램 생성 중 오류 발생: {e}")
            raise

def main():
    """메인 함수 - CLI 인터페이스"""
    parser = argparse.ArgumentParser(description='오디오 전처리 및 스펙트로그램 생성 도구')
    parser.add_argument('--target', required=True, help='타겟 오디오 파일 경로')
    parser.add_argument('--noise', required=True, help='노이즈 오디오 파일 경로')
    parser.add_argument('--output-processed', default='data/processed', help='정제된 오디오 출력 디렉토리')
    parser.add_argument('--output-spectrograms', default='data/spectrograms', help='스펙트로그램 출력 디렉토리')
    parser.add_argument('--image-size', nargs=2, type=int, default=[256, 256], help='이미지 크기 (width height)')
    parser.add_argument('--colormap', default='magma', help='컬러맵 (magma, viridis, plasma 등)')
    parser.add_argument('--multiple-windows', action='store_true', help='다양한 윈도우 크기로 스펙트로그램 생성')
    parser.add_argument('--window-sizes', nargs='+', type=float, default=[5.0, 3.0, 1.0], 
                       help='윈도우 크기들 (초)')
    
    args = parser.parse_args()
    
    # 파일 존재 확인
    if not os.path.exists(args.target):
        logger.error(f"타겟 오디오 파일을 찾을 수 없습니다: {args.target}")
        return
    
    if not os.path.exists(args.noise):
        logger.error(f"노이즈 오디오 파일을 찾을 수 없습니다: {args.noise}")
        return
    
    # 전처리기 초기화
    preprocessor = AudioPreprocessor()
    
    try:
        # 1. 노이즈 제거
        logger.info("=== 1단계: 노이즈 제거 ===")
        clean_audio_path = preprocessor.noise_cancel(
            args.target, args.noise, args.output_processed
        )
        
        # 2. 스펙트로그램 생성
        logger.info("=== 2단계: 스펙트로그램 생성 ===")
        if args.multiple_windows:
            spectrogram_paths = preprocessor.create_multiple_spectrograms(
                clean_audio_path, args.output_spectrograms, 
                args.window_sizes, tuple(args.image_size)
            )
            print(f"\n✅ 다중 스펙트로그램 생성 완료!")
            for i, path in enumerate(spectrogram_paths):
                print(f"📁 스펙트로그램 {i+1}: {path}")
        else:
            spectrogram_path = preprocessor.create_spectrogram(
                clean_audio_path, args.output_spectrograms, 
                tuple(args.image_size), args.colormap
            )
            print(f"\n✅ 스펙트로그램 생성 완료!")
            print(f"📁 스펙트로그램: {spectrogram_path}")
        
        print(f"\n📁 정제된 오디오: {clean_audio_path}")
        
    except Exception as e:
        logger.error(f"전처리 실패: {e}")
        return

if __name__ == "__main__":
    main()
