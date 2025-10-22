#!/usr/bin/env python3
"""
합성 데이터 생성기
2단계에서 생성한 도메인 규칙을 바탕으로 실제 AI 학습에 사용할 수 있는 합성 데이터 생성
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from typing import Dict, List, Tuple, Optional
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class SyntheticDataGenerator:
    """합성 데이터 생성기"""
    
    def __init__(self):
        self.generated_data = {}
        self.audio_samples = {}
        self.feature_data = {}
        self.labels = {}
        
        print("🎵 합성 데이터 생성기 초기화")
        self._load_domain_rules()
        self._generate_synthetic_data()
    
    def _load_domain_rules(self):
        """2단계에서 생성한 도메인 규칙 로드"""
        try:
            print("📚 도메인 규칙 로드 중...")
            
            # 2단계에서 생성한 규칙 (실제로는 파일에서 로드)
            self.domain_rules = {
                'normal_sounds': {
                    'compressor_normal': {
                        'frequency_range': (20, 200),
                        'rms_range': (0.1, 0.3),
                        'stability_factor': 0.8,
                        'pattern_regularity': 0.8
                    },
                    'fan_normal': {
                        'frequency_range': (200, 1000),
                        'rms_range': (0.2, 0.4),
                        'stability_factor': 0.9,
                        'pattern_regularity': 0.9
                    },
                    'motor_normal': {
                        'frequency_range': (1000, 5000),
                        'rms_range': (0.15, 0.35),
                        'stability_factor': 0.85,
                        'pattern_regularity': 0.85
                    }
                },
                'abnormal_sounds': {
                    'bearing_wear': {
                        'frequency_range': (2000, 8000),
                        'rms_range': (0.4, 1.0),
                        'stability_factor': 0.3,
                        'pattern_regularity': 0.3
                    },
                    'unbalance': {
                        'frequency_range': (50, 500),
                        'rms_range': (0.3, 0.8),
                        'stability_factor': 0.4,
                        'pattern_regularity': 0.6
                    },
                    'friction': {
                        'frequency_range': (500, 3000),
                        'rms_range': (0.25, 0.7),
                        'stability_factor': 0.5,
                        'pattern_regularity': 0.5
                    },
                    'overload': {
                        'frequency_range': (20, 8000),
                        'rms_range': (0.5, 1.0),
                        'stability_factor': 0.2,
                        'pattern_regularity': 0.2
                    }
                }
            }
            
            print("✅ 도메인 규칙 로드 완료")
            
        except Exception as e:
            print(f"❌ 도메인 규칙 로드 오류: {e}")
            self.domain_rules = {}
    
    def _generate_synthetic_data(self):
        """합성 데이터 생성"""
        try:
            print("🎵 합성 데이터 생성 시작")
            
            # 1. 정상 소리 데이터 생성
            self._generate_normal_sounds()
            
            # 2. 이상 소리 데이터 생성
            self._generate_abnormal_sounds()
            
            # 3. 환경 조건별 데이터 생성
            self._generate_environmental_variations()
            
            # 4. 노이즈 및 간섭 추가
            self._add_noise_and_interference()
            
            # 5. 데이터 검증 및 정리
            self._validate_and_organize_data()
            
            print("✅ 합성 데이터 생성 완료")
            
        except Exception as e:
            print(f"❌ 합성 데이터 생성 오류: {e}")
    
    def _generate_normal_sounds(self):
        """정상 소리 데이터 생성"""
        try:
            print("1️⃣ 정상 소리 데이터 생성")
            
            self.audio_samples['normal'] = {}
            self.feature_data['normal'] = {}
            self.labels['normal'] = {}
            
            for sound_type, rules in self.domain_rules['normal_sounds'].items():
                print(f"   - {sound_type} 생성 중...")
                
                # 각 소리 유형별로 10개씩 생성
                samples = []
                features = []
                labels = []
                
                for i in range(10):
                    # 오디오 데이터 생성
                    audio_data = self._create_normal_audio_sample(sound_type, rules, i)
                    samples.append(audio_data)
                    
                    # 특징 추출
                    feature_vector = self._extract_features(audio_data)
                    features.append(feature_vector)
                    
                    # 레이블 생성
                    label = self._create_label(sound_type, 'normal')
                    labels.append(label)
                
                self.audio_samples['normal'][sound_type] = samples
                self.feature_data['normal'][sound_type] = features
                self.labels['normal'][sound_type] = labels
                
                print(f"   ✅ {sound_type}: {len(samples)}개 샘플 생성 완료")
            
            print("✅ 정상 소리 데이터 생성 완료")
            
        except Exception as e:
            print(f"⚠️ 정상 소리 데이터 생성 오류: {e}")
    
    def _generate_abnormal_sounds(self):
        """이상 소리 데이터 생성"""
        try:
            print("2️⃣ 이상 소리 데이터 생성")
            
            self.audio_samples['abnormal'] = {}
            self.feature_data['abnormal'] = {}
            self.labels['abnormal'] = {}
            
            for sound_type, rules in self.domain_rules['abnormal_sounds'].items():
                print(f"   - {sound_type} 생성 중...")
                
                # 각 소리 유형별로 10개씩 생성
                samples = []
                features = []
                labels = []
                
                for i in range(10):
                    # 오디오 데이터 생성
                    audio_data = self._create_abnormal_audio_sample(sound_type, rules, i)
                    samples.append(audio_data)
                    
                    # 특징 추출
                    feature_vector = self._extract_features(audio_data)
                    features.append(feature_vector)
                    
                    # 레이블 생성
                    label = self._create_label(sound_type, 'abnormal')
                    labels.append(label)
                
                self.audio_samples['abnormal'][sound_type] = samples
                self.feature_data['abnormal'][sound_type] = features
                self.labels['abnormal'][sound_type] = labels
                
                print(f"   ✅ {sound_type}: {len(samples)}개 샘플 생성 완료")
            
            print("✅ 이상 소리 데이터 생성 완료")
            
        except Exception as e:
            print(f"⚠️ 이상 소리 데이터 생성 오류: {e}")
    
    def _create_normal_audio_sample(self, sound_type: str, rules: Dict, sample_id: int) -> np.ndarray:
        """정상 오디오 샘플 생성"""
        try:
            duration = 5.0  # 5초
            sample_rate = 16000
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            if sound_type == 'compressor_normal':
                # 정상 압축기 소리
                base_freq = np.random.uniform(60, 80)  # 60-80Hz
                base_signal = np.sin(2 * np.pi * base_freq * t)
                
                # 하모닉스
                harmonic1 = 0.3 * np.sin(2 * np.pi * 2 * base_freq * t)
                harmonic2 = 0.1 * np.sin(2 * np.pi * 3 * base_freq * t)
                
                # 일정한 리듬
                rhythm = 0.2 * np.sin(2 * np.pi * 0.5 * t)
                
                # 백그라운드 노이즈
                noise = 0.05 * np.random.normal(0, 1, len(t))
                
                signal = base_signal + harmonic1 + harmonic2 + rhythm + noise
                
            elif sound_type == 'fan_normal':
                # 정상 팬 소리
                base_freq = np.random.uniform(300, 500)  # 300-500Hz
                base_signal = np.sin(2 * np.pi * base_freq * t)
                
                # 하모닉스
                harmonic1 = 0.4 * np.sin(2 * np.pi * 2 * base_freq * t)
                harmonic2 = 0.2 * np.sin(2 * np.pi * 3 * base_freq * t)
                
                # 부드러운 소음
                smooth_noise = 0.1 * np.random.normal(0, 1, len(t))
                smooth_noise = signal.butter(4, 0.1, btype='low')(smooth_noise)[0]
                
                signal = base_signal + harmonic1 + harmonic2 + smooth_noise
                
            elif sound_type == 'motor_normal':
                # 정상 모터 소리
                base_freq = np.random.uniform(1200, 1800)  # 1200-1800Hz
                base_signal = np.sin(2 * np.pi * base_freq * t)
                
                # 하모닉스
                harmonic1 = 0.3 * np.sin(2 * np.pi * 2 * base_freq * t)
                harmonic2 = 0.15 * np.sin(2 * np.pi * 3 * base_freq * t)
                
                # 규칙적 패턴
                pattern = 0.3 * np.sin(2 * np.pi * 2 * t)
                
                signal = base_signal + harmonic1 + harmonic2 + pattern
            
            # 정규화
            signal = signal / np.max(np.abs(signal)) * 0.8
            
            return signal
            
        except Exception as e:
            print(f"⚠️ 정상 오디오 샘플 생성 오류: {e}")
            return np.zeros(int(16000 * 5.0))
    
    def _create_abnormal_audio_sample(self, sound_type: str, rules: Dict, sample_id: int) -> np.ndarray:
        """이상 오디오 샘플 생성"""
        try:
            duration = 5.0  # 5초
            sample_rate = 16000
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            if sound_type == 'bearing_wear':
                # 베어링 마모 소리
                base_freq = np.random.uniform(3000, 5000)  # 3000-5000Hz
                base_signal = np.sin(2 * np.pi * base_freq * t)
                
                # 불규칙한 진동 (마모로 인한)
                irregular_vib = 0.5 * np.sin(2 * np.pi * base_freq * t + 0.1 * np.sin(2 * np.pi * 10 * t))
                
                # 마찰음 (고주파 노이즈)
                friction_noise = 0.3 * np.random.normal(0, 1, len(t))
                friction_noise = signal.butter(4, [0.3, 0.8], btype='band')(friction_noise)[0]
                
                signal = base_signal + irregular_vib + friction_noise
                
            elif sound_type == 'unbalance':
                # 언밸런스 소리
                base_freq = np.random.uniform(80, 120)  # 80-120Hz
                base_signal = np.sin(2 * np.pi * base_freq * t)
                
                # 주기적 진동 (언밸런스로 인한)
                periodic_vib = 0.6 * np.sin(2 * np.pi * base_freq * t + 0.2 * np.sin(2 * np.pi * 5 * t))
                
                # 리듬 변화 (불안정)
                rhythm_change = 0.3 * np.sin(2 * np.pi * 0.3 * t)
                
                signal = base_signal + periodic_vib + rhythm_change
                
            elif sound_type == 'friction':
                # 마찰 소리
                base_freq = np.random.uniform(800, 1200)  # 800-1200Hz
                base_signal = np.sin(2 * np.pi * base_freq * t)
                
                # 긁는 소리 (중주파 노이즈)
                scraping_noise = 0.4 * np.random.normal(0, 1, len(t))
                scraping_noise = signal.butter(4, [0.2, 0.6], btype='band')(scraping_noise)[0]
                
                # 불안정한 진동
                unstable_vib = 0.3 * np.sin(2 * np.pi * base_freq * t + 0.5 * np.sin(2 * np.pi * 15 * t))
                
                signal = base_signal + scraping_noise + unstable_vib
                
            elif sound_type == 'overload':
                # 과부하 소리
                # 전체 주파수 범위의 불규칙한 노이즈
                overload_noise = np.random.normal(0, 1, len(t))
                
                # 저주파 과부하
                low_freq_overload = 0.6 * np.sin(2 * np.pi * 50 * t)
                
                # 중주파 과부하
                mid_freq_overload = 0.4 * np.sin(2 * np.pi * 400 * t)
                
                # 고주파 과부하
                high_freq_overload = 0.3 * np.sin(2 * np.pi * 2000 * t)
                
                # 불규칙한 진동
                irregular_vib = 0.5 * np.sin(2 * np.pi * 100 * t + 0.3 * np.sin(2 * np.pi * 20 * t))
                
                signal = overload_noise + low_freq_overload + mid_freq_overload + high_freq_overload + irregular_vib
            
            # 정규화
            signal = signal / np.max(np.abs(signal)) * 0.9
            
            return signal
            
        except Exception as e:
            print(f"⚠️ 이상 오디오 샘플 생성 오류: {e}")
            return np.zeros(int(16000 * 5.0))
    
    def _extract_features(self, audio_data: np.ndarray) -> np.ndarray:
        """특징 추출"""
        try:
            features = []
            
            # 기본 특징들
            features.append(np.sqrt(np.mean(audio_data ** 2)))  # RMS
            features.append(np.mean(librosa.feature.zero_crossing_rate(audio_data)))  # ZCR
            features.append(np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=16000)))  # Spectral Centroid
            features.append(np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=16000)))  # Spectral Rolloff
            features.append(np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=16000)))  # Spectral Bandwidth
            
            # 안정성 계수
            stability = self._calculate_stability_factor(audio_data)
            features.append(stability)
            
            # 주파수 일관성
            frequency_consistency = self._calculate_frequency_consistency(audio_data)
            features.append(frequency_consistency)
            
            # 패턴 규칙성
            pattern_regularity = self._calculate_pattern_regularity(audio_data)
            features.append(pattern_regularity)
            
            # 하모닉스 비율
            harmonic_ratio = self._calculate_harmonic_ratio(audio_data)
            features.append(harmonic_ratio)
            
            # 노이즈 레벨
            noise_level = self._calculate_noise_level(audio_data)
            features.append(noise_level)
            
            return np.array(features)
            
        except Exception as e:
            print(f"⚠️ 특징 추출 오류: {e}")
            return np.zeros(10)
    
    def _calculate_stability_factor(self, audio_data: np.ndarray) -> float:
        """안정성 계수 계산"""
        try:
            window_size = len(audio_data) // 10
            rms_windows = []
            
            for i in range(0, len(audio_data) - window_size, window_size):
                window = audio_data[i:i + window_size]
                rms_windows.append(np.sqrt(np.mean(window ** 2)))
            
            if len(rms_windows) > 1:
                stability = 1.0 / (1.0 + np.std(rms_windows) / np.mean(rms_windows))
            else:
                stability = 1.0
            
            return min(1.0, max(0.0, stability))
            
        except Exception as e:
            return 0.5
    
    def _calculate_frequency_consistency(self, audio_data: np.ndarray) -> float:
        """주파수 일관성 계산"""
        try:
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=16000)[0]
            
            if len(spectral_centroids) > 1:
                consistency = 1.0 / (1.0 + np.std(spectral_centroids) / np.mean(spectral_centroids))
            else:
                consistency = 1.0
            
            return min(1.0, max(0.0, consistency))
            
        except Exception as e:
            return 0.5
    
    def _calculate_pattern_regularity(self, audio_data: np.ndarray) -> float:
        """패턴 규칙성 계산"""
        try:
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            if len(autocorr) > 1:
                max_autocorr = np.max(autocorr[1:])
                regularity = max_autocorr / autocorr[0]
            else:
                regularity = 0.0
            
            return min(1.0, max(0.0, regularity))
            
        except Exception as e:
            return 0.5
    
    def _calculate_harmonic_ratio(self, audio_data: np.ndarray) -> float:
        """하모닉스 비율 계산"""
        try:
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/16000)
            
            positive_freqs = freqs[:len(freqs)//2]
            positive_fft = np.abs(fft[:len(fft)//2])
            
            fundamental_freq = positive_freqs[np.argmax(positive_fft)]
            
            if fundamental_freq > 0:
                harmonic2_idx = np.argmin(np.abs(positive_freqs - 2 * fundamental_freq))
                harmonic3_idx = np.argmin(np.abs(positive_freqs - 3 * fundamental_freq))
                
                fundamental_amp = positive_fft[np.argmax(positive_fft)]
                harmonic2_amp = positive_fft[harmonic2_idx]
                harmonic3_amp = positive_fft[harmonic3_idx]
                
                harmonic_ratio = (harmonic2_amp + harmonic3_amp) / (2 * fundamental_amp)
            else:
                harmonic_ratio = 0.0
            
            return min(1.0, max(0.0, harmonic_ratio))
            
        except Exception as e:
            return 0.5
    
    def _calculate_noise_level(self, audio_data: np.ndarray) -> float:
        """노이즈 레벨 계산"""
        try:
            high_freq_noise = np.std(audio_data)
            noise_level = min(1.0, high_freq_noise / 0.5)
            return noise_level
        except Exception as e:
            return 0.5
    
    def _create_label(self, sound_type: str, category: str) -> Dict:
        """레이블 생성"""
        return {
            'sound_type': sound_type,
            'category': category,
            'is_normal': category == 'normal',
            'is_abnormal': category == 'abnormal',
            'anomaly_type': sound_type if category == 'abnormal' else 'none'
        }
    
    def _generate_environmental_variations(self):
        """환경 조건별 데이터 생성"""
        try:
            print("3️⃣ 환경 조건별 데이터 생성")
            
            # 온도, 습도, 부하 조건별 변형 생성
            environmental_conditions = [
                {'temperature': 'low', 'humidity': 'low', 'load': 'low'},
                {'temperature': 'normal', 'humidity': 'normal', 'load': 'normal'},
                {'temperature': 'high', 'humidity': 'high', 'load': 'high'}
            ]
            
            for condition in environmental_conditions:
                condition_name = f"{condition['temperature']}_{condition['humidity']}_{condition['load']}"
                print(f"   - {condition_name} 조건 생성 중...")
                
                # 각 조건별로 기존 데이터에 변형 적용
                self._apply_environmental_variation(condition_name, condition)
            
            print("✅ 환경 조건별 데이터 생성 완료")
            
        except Exception as e:
            print(f"⚠️ 환경 조건별 데이터 생성 오류: {e}")
    
    def _apply_environmental_variation(self, condition_name: str, condition: Dict):
        """환경 조건 변형 적용"""
        try:
            # 온도, 습도, 부하에 따른 노이즈 레벨 조정
            temp_factor = {'low': 0.8, 'normal': 1.0, 'high': 1.2}[condition['temperature']]
            humidity_factor = {'low': 0.9, 'normal': 1.0, 'high': 1.1}[condition['humidity']]
            load_factor = {'low': 0.9, 'normal': 1.0, 'high': 1.1}[condition['load']]
            
            # 기존 데이터에 변형 적용
            for category in ['normal', 'abnormal']:
                if category not in self.audio_samples:
                    continue
                
                for sound_type in self.audio_samples[category]:
                    for i, audio_data in enumerate(self.audio_samples[category][sound_type]):
                        # 환경 조건에 따른 변형 적용
                        variation_factor = temp_factor * humidity_factor * load_factor
                        varied_audio = audio_data * variation_factor
                        
                        # 노이즈 추가
                        noise_level = 0.1 * (variation_factor - 1.0)
                        noise = np.random.normal(0, noise_level, len(varied_audio))
                        varied_audio = varied_audio + noise
                        
                        # 정규화
                        varied_audio = varied_audio / np.max(np.abs(varied_audio)) * 0.8
                        
                        # 변형된 데이터 저장
                        if condition_name not in self.audio_samples[category]:
                            self.audio_samples[category][condition_name] = []
                        self.audio_samples[category][condition_name].append(varied_audio)
            
        except Exception as e:
            print(f"⚠️ 환경 조건 변형 적용 오류: {e}")
    
    def _add_noise_and_interference(self):
        """노이즈 및 간섭 추가"""
        try:
            print("4️⃣ 노이즈 및 간섭 추가")
            
            # 다양한 노이즈 레벨 추가
            noise_levels = [0.05, 0.1, 0.15, 0.2]
            
            for noise_level in noise_levels:
                noise_name = f"noise_{int(noise_level * 100)}"
                print(f"   - {noise_name} 레벨 추가 중...")
                
                # 각 카테고리별로 노이즈 추가
                for category in ['normal', 'abnormal']:
                    if category not in self.audio_samples:
                        continue
                    
                    for sound_type in self.audio_samples[category]:
                        for i, audio_data in enumerate(self.audio_samples[category][sound_type]):
                            # 노이즈 추가
                            noise = np.random.normal(0, noise_level, len(audio_data))
                            noisy_audio = audio_data + noise
                            
                            # 정규화
                            noisy_audio = noisy_audio / np.max(np.abs(noisy_audio)) * 0.8
                            
                            # 노이즈가 추가된 데이터 저장
                            if noise_name not in self.audio_samples[category]:
                                self.audio_samples[category][noise_name] = []
                            self.audio_samples[category][noise_name].append(noisy_audio)
            
            print("✅ 노이즈 및 간섭 추가 완료")
            
        except Exception as e:
            print(f"⚠️ 노이즈 및 간섭 추가 오류: {e}")
    
    def _validate_and_organize_data(self):
        """데이터 검증 및 정리"""
        try:
            print("5️⃣ 데이터 검증 및 정리")
            
            # 데이터 통계 계산
            total_samples = 0
            for category in self.audio_samples:
                for sound_type in self.audio_samples[category]:
                    total_samples += len(self.audio_samples[category][sound_type])
            
            print(f"   총 샘플 수: {total_samples}개")
            
            # 데이터 품질 검증
            valid_samples = 0
            for category in self.audio_samples:
                for sound_type in self.audio_samples[category]:
                    for audio_data in self.audio_samples[category][sound_type]:
                        if self._validate_audio_sample(audio_data):
                            valid_samples += 1
            
            print(f"   유효한 샘플 수: {valid_samples}개")
            print(f"   데이터 품질: {valid_samples/total_samples*100:.1f}%")
            
            print("✅ 데이터 검증 및 정리 완료")
            
        except Exception as e:
            print(f"⚠️ 데이터 검증 및 정리 오류: {e}")
    
    def _validate_audio_sample(self, audio_data: np.ndarray) -> bool:
        """오디오 샘플 검증"""
        try:
            # 기본 품질 검사
            if len(audio_data) == 0:
                return False
            
            if np.max(np.abs(audio_data)) > 1.0:
                return False
            
            if np.isnan(audio_data).any() or np.isinf(audio_data).any():
                return False
            
            return True
            
        except Exception as e:
            return False
    
    def save_generated_data(self, filepath: str = "data/synthetic_training_data.json"):
        """생성된 데이터 저장"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 오디오 데이터는 별도 파일로 저장
            audio_files = []
            for category in self.audio_samples:
                for sound_type in self.audio_samples[category]:
                    for i, audio_data in enumerate(self.audio_samples[category][sound_type]):
                        audio_file = f"data/audio/{category}_{sound_type}_{i}.wav"
                        os.makedirs(os.path.dirname(audio_file), exist_ok=True)
                        sf.write(audio_file, audio_data, 16000)
                        audio_files.append(audio_file)
            
            # 메타데이터 저장
            metadata = {
                'total_samples': sum(len(samples) for category in self.audio_samples.values() for samples in category.values()),
                'categories': list(self.audio_samples.keys()),
                'sound_types': {category: list(samples.keys()) for category, samples in self.audio_samples.items()},
                'audio_files': audio_files,
                'feature_data': self.feature_data,
                'labels': self.labels,
                'generation_timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 생성된 데이터 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 데이터 저장 오류: {e}")
            return False
    
    def print_data_summary(self):
        """생성된 데이터 요약 출력"""
        print("\n" + "=" * 60)
        print("🎵 합성 데이터 생성 결과")
        print("=" * 60)
        
        total_samples = 0
        for category in self.audio_samples:
            print(f"\n📁 {category} 카테고리:")
            for sound_type in self.audio_samples[category]:
                sample_count = len(self.audio_samples[category][sound_type])
                print(f"   - {sound_type}: {sample_count}개 샘플")
                total_samples += sample_count
        
        print(f"\n📊 총 샘플 수: {total_samples}개")
        print(f"📊 카테고리 수: {len(self.audio_samples)}개")
        print(f"📊 소리 유형 수: {sum(len(samples) for samples in self.audio_samples.values())}개")

# 사용 예제
if __name__ == "__main__":
    # 합성 데이터 생성기 테스트
    data_generator = SyntheticDataGenerator()
    
    print("🎵 합성 데이터 생성기 테스트")
    print("=" * 60)
    
    # 생성된 데이터 요약 출력
    data_generator.print_data_summary()
    
    # 데이터 저장
    data_generator.save_generated_data()
    
    print("\n🎉 3단계: 합성 데이터 생성 완료!")
    print("   시뮬레이션 기반 데이터가 AI 학습에 사용할 수 있도록 생성되었습니다.")
