#!/usr/bin/env python3
"""
실제 오디오 데이터 증강 스크립트
하루 2-3개의 실제 데이터를 100-200개의 증강 데이터로 변환
"""

import os
import sys
import argparse
import numpy as np
import librosa
import soundfile as sf
from scipy import signal
import random
from datetime import datetime

class AudioAugmentation:
    def __init__(self):
        self.sample_rate = 16000
        self.duration = 5.0  # 5초로 고정
        
    def load_audio(self, file_path):
        """오디오 파일 로드"""
        try:
            audio, sr = librosa.load(file_path, sr=self.sample_rate)
            return audio, sr
        except Exception as e:
            print(f"오디오 로드 실패: {e}")
            return None, None
    
    def save_audio(self, audio, output_path, sr):
        """오디오 파일 저장"""
        try:
            sf.write(output_path, audio, sr)
            return True
        except Exception as e:
            print(f"오디오 저장 실패: {e}")
            return False
    
    def add_noise(self, audio, noise_factor=0.1):
        """노이즈 추가"""
        noise = np.random.normal(0, noise_factor, len(audio))
        return audio + noise
    
    def time_stretch(self, audio, stretch_factor):
        """시간 스트레칭"""
        return librosa.effects.time_stretch(audio, rate=stretch_factor)
    
    def pitch_shift(self, audio, n_steps):
        """피치 시프트"""
        return librosa.effects.pitch_shift(audio, sr=self.sample_rate, n_steps=n_steps)
    
    def volume_change(self, audio, volume_factor):
        """볼륨 변경"""
        return audio * volume_factor
    
    def add_reverb(self, audio, reverb_factor=0.3):
        """리버브 효과 추가"""
        # 간단한 리버브 시뮬레이션
        reverb = np.zeros_like(audio)
        for i in range(1, len(audio)):
            if i > 100:  # 100 샘플 지연
                reverb[i] = audio[i-100] * reverb_factor
        return audio + reverb
    
    def frequency_mask(self, audio, mask_factor=0.1):
        """주파수 마스킹"""
        # FFT 변환
        fft = np.fft.fft(audio)
        freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
        
        # 랜덤 주파수 대역 마스킹
        mask_start = random.randint(0, len(fft)//2)
        mask_end = mask_start + int(len(fft) * mask_factor)
        mask_end = min(mask_end, len(fft)//2)
        
        fft[mask_start:mask_end] *= 0.1
        fft[-(mask_end-mask_start):] *= 0.1  # 대칭성 유지
        
        return np.real(np.fft.ifft(fft))
    
    def add_environmental_noise(self, audio, noise_type='fan'):
        """환경 노이즈 추가"""
        if noise_type == 'fan':
            # 팬 소리 시뮬레이션
            t = np.linspace(0, len(audio)/self.sample_rate, len(audio))
            fan_noise = 0.05 * np.sin(2 * np.pi * 60 * t) * np.random.random(len(audio))
        elif noise_type == 'traffic':
            # 교통 소음 시뮬레이션
            traffic_noise = np.random.normal(0, 0.03, len(audio))
        else:
            # 일반 노이즈
            traffic_noise = np.random.normal(0, 0.02, len(audio))
        
        return audio + traffic_noise
    
    def augment_audio(self, audio, augmentation_type):
        """오디오 증강 실행"""
        augmented = audio.copy()
        
        if augmentation_type == 'noise':
            augmented = self.add_noise(augmented, noise_factor=random.uniform(0.05, 0.2))
        
        elif augmentation_type == 'time_stretch':
            stretch_factor = random.uniform(0.8, 1.2)
            augmented = self.time_stretch(augmented, stretch_factor)
        
        elif augmentation_type == 'pitch_shift':
            n_steps = random.uniform(-2, 2)
            augmented = self.pitch_shift(augmented, n_steps)
        
        elif augmentation_type == 'volume':
            volume_factor = random.uniform(0.5, 1.5)
            augmented = self.volume_change(augmented, volume_factor)
        
        elif augmentation_type == 'reverb':
            augmented = self.add_reverb(augmented, reverb_factor=random.uniform(0.1, 0.4))
        
        elif augmentation_type == 'frequency_mask':
            augmented = self.frequency_mask(augmented, mask_factor=random.uniform(0.05, 0.2))
        
        elif augmentation_type == 'environmental':
            noise_types = ['fan', 'traffic', 'general']
            noise_type = random.choice(noise_types)
            augmented = self.add_environmental_noise(augmented, noise_type)
        
        elif augmentation_type == 'combined':
            # 여러 증강 기법 조합
            techniques = ['noise', 'time_stretch', 'pitch_shift', 'volume', 'reverb']
            selected_techniques = random.sample(techniques, random.randint(2, 4))
            
            for technique in selected_techniques:
                if technique == 'noise':
                    augmented = self.add_noise(augmented, noise_factor=random.uniform(0.05, 0.15))
                elif technique == 'time_stretch':
                    stretch_factor = random.uniform(0.9, 1.1)
                    augmented = self.time_stretch(augmented, stretch_factor)
                elif technique == 'pitch_shift':
                    n_steps = random.uniform(-1, 1)
                    augmented = self.pitch_shift(augmented, n_steps)
                elif technique == 'volume':
                    volume_factor = random.uniform(0.7, 1.3)
                    augmented = self.volume_change(augmented, volume_factor)
                elif technique == 'reverb':
                    augmented = self.add_reverb(augmented, reverb_factor=random.uniform(0.1, 0.3))
        
        # 정규화
        if np.max(np.abs(augmented)) > 0:
            augmented = augmented / np.max(np.abs(augmented)) * 0.9
        
        return augmented
    
    def generate_augmented_data(self, input_file, output_dir, count=10, label='unknown'):
        """증강 데이터 생성"""
        print(f"📁 입력 파일: {input_file}")
        print(f"📁 출력 디렉토리: {output_dir}")
        print(f"🔢 증강 개수: {count}")
        print(f"🏷️ 라벨: {label}")
        
        # 오디오 로드
        audio, sr = self.load_audio(input_file)
        if audio is None:
            return False
        
        print(f"✅ 오디오 로드 완료: {len(audio)} 샘플, {sr} Hz")
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 증강 기법 목록
        augmentation_types = [
            'noise', 'time_stretch', 'pitch_shift', 'volume', 
            'reverb', 'frequency_mask', 'environmental', 'combined'
        ]
        
        # 원본 파일도 복사
        original_name = f"{label}_original_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        original_path = os.path.join(output_dir, original_name)
        self.save_audio(audio, original_path, sr)
        print(f"📄 원본 저장: {original_name}")
        
        # 증강 데이터 생성
        success_count = 0
        for i in range(count):
            try:
                # 랜덤 증강 기법 선택
                aug_type = random.choice(augmentation_types)
                
                # 증강 실행
                augmented_audio = self.augment_audio(audio, aug_type)
                
                # 파일명 생성
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                filename = f"{label}_{aug_type}_{timestamp}.wav"
                output_path = os.path.join(output_dir, filename)
                
                # 저장
                if self.save_audio(augmented_audio, output_path, sr):
                    success_count += 1
                    print(f"✅ 증강 완료 ({success_count}/{count}): {filename}")
                else:
                    print(f"❌ 증강 실패: {filename}")
                    
            except Exception as e:
                print(f"❌ 증강 오류: {e}")
                continue
        
        print(f"🎉 증강 완료: {success_count}/{count}개 파일 생성")
        return success_count > 0

def main():
    parser = argparse.ArgumentParser(description='오디오 데이터 증강')
    parser.add_argument('--input', required=True, help='입력 오디오 파일 경로')
    parser.add_argument('--output', required=True, help='출력 디렉토리 경로')
    parser.add_argument('--count', type=int, default=10, help='증강할 데이터 개수')
    parser.add_argument('--label', default='unknown', help='데이터 라벨')
    
    args = parser.parse_args()
    
    # 증강 실행
    augmenter = AudioAugmentation()
    success = augmenter.generate_augmented_data(
        args.input, 
        args.output, 
        args.count, 
        args.label
    )
    
    if success:
        print("🎵 데이터 증강이 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("❌ 데이터 증강에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
