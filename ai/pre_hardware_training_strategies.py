#!/usr/bin/env python3
"""
실제 하드웨어 설치 전 AI 학습 전략
기계 엔지니어의 도메인 지식을 활용한 사전 학습 방법들
"""

import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
import os
import json
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class PreHardwareTrainingStrategies:
    """실제 하드웨어 설치 전 AI 학습 전략"""
    
    def __init__(self):
        self.synthetic_data = {}
        self.domain_knowledge = {}
        self.training_data = {}
        
        print("🔧 실제 하드웨어 설치 전 AI 학습 전략 초기화")
        print("   기계 엔지니어의 도메인 지식을 활용한 사전 학습")
    
    # ===== 1. 합성 데이터 생성 =====
    
    def generate_synthetic_audio_data(self, duration: float = 10.0, sample_rate: int = 16000) -> Dict:
        """합성 오디오 데이터 생성"""
        try:
            print("🎵 합성 오디오 데이터 생성 시작")
            
            synthetic_data = {
                'normal_sounds': [],
                'abnormal_sounds': [],
                'metadata': {}
            }
            
            # 1. 정상 소리 생성
            normal_sounds = self._generate_normal_sounds(duration, sample_rate)
            synthetic_data['normal_sounds'] = normal_sounds
            
            # 2. 이상 소리 생성 (기계 엔지니어 지식 기반)
            abnormal_sounds = self._generate_abnormal_sounds(duration, sample_rate)
            synthetic_data['abnormal_sounds'] = abnormal_sounds
            
            # 3. 메타데이터 생성
            synthetic_data['metadata'] = {
                'total_duration': duration,
                'sample_rate': sample_rate,
                'normal_count': len(normal_sounds),
                'abnormal_count': len(abnormal_sounds),
                'generation_method': 'synthetic_based_on_domain_knowledge'
            }
            
            print(f"✅ 합성 데이터 생성 완료: 정상 {len(normal_sounds)}개, 이상 {len(abnormal_sounds)}개")
            return synthetic_data
            
        except Exception as e:
            print(f"❌ 합성 데이터 생성 오류: {e}")
            return {'error': str(e)}
    
    def _generate_normal_sounds(self, duration: float, sample_rate: int) -> List[Dict]:
        """정상 소리 생성 (기계 엔지니어 지식 기반)"""
        normal_sounds = []
        
        # 1. 정상 압축기 소리 (저주파 + 일정한 리듬)
        normal_compressor = self._create_normal_compressor_sound(duration, sample_rate)
        normal_sounds.append({
            'name': 'normal_compressor',
            'description': '정상 압축기 소리 - 저주파 + 일정한 리듬',
            'audio_data': normal_compressor,
            'label': 0,
            'frequency_range': '20-200Hz',
            'characteristics': ['일정한 리듬', '저주파', '안정적']
        })
        
        # 2. 정상 팬 소리 (중주파 + 부드러운 소음)
        normal_fan = self._create_normal_fan_sound(duration, sample_rate)
        normal_sounds.append({
            'name': 'normal_fan',
            'description': '정상 팬 소리 - 중주파 + 부드러운 소음',
            'audio_data': normal_fan,
            'label': 0,
            'frequency_range': '200-1000Hz',
            'characteristics': ['부드러운 소음', '중주파', '안정적']
        })
        
        # 3. 정상 모터 소리 (고주파 + 규칙적 패턴)
        normal_motor = self._create_normal_motor_sound(duration, sample_rate)
        normal_sounds.append({
            'name': 'normal_motor',
            'description': '정상 모터 소리 - 고주파 + 규칙적 패턴',
            'audio_data': normal_motor,
            'label': 0,
            'frequency_range': '1000-5000Hz',
            'characteristics': ['규칙적 패턴', '고주파', '안정적']
        })
        
        return normal_sounds
    
    def _generate_abnormal_sounds(self, duration: float, sample_rate: int) -> List[Dict]:
        """이상 소리 생성 (기계 엔지니어 지식 기반)"""
        abnormal_sounds = []
        
        # 1. 베어링 마모 소리 (고주파 + 불규칙한 진동)
        bearing_wear = self._create_bearing_wear_sound(duration, sample_rate)
        abnormal_sounds.append({
            'name': 'bearing_wear',
            'description': '베어링 마모 소리 - 고주파 + 불규칙한 진동',
            'audio_data': bearing_wear,
            'label': 1,
            'frequency_range': '2000-8000Hz',
            'characteristics': ['불규칙한 진동', '고주파', '마찰음']
        })
        
        # 2. 언밸런스 소리 (저주파 + 주기적 진동)
        unbalance = self._create_unbalance_sound(duration, sample_rate)
        abnormal_sounds.append({
            'name': 'unbalance',
            'description': '언밸런스 소리 - 저주파 + 주기적 진동',
            'audio_data': unbalance,
            'label': 1,
            'frequency_range': '50-500Hz',
            'characteristics': ['주기적 진동', '저주파', '리듬 변화']
        })
        
        # 3. 마찰 소리 (중주파 + 긁는 소리)
        friction = self._create_friction_sound(duration, sample_rate)
        abnormal_sounds.append({
            'name': 'friction',
            'description': '마찰 소리 - 중주파 + 긁는 소리',
            'audio_data': friction,
            'label': 1,
            'frequency_range': '500-3000Hz',
            'characteristics': ['긁는 소리', '중주파', '불안정']
        })
        
        # 4. 과부하 소리 (전체 주파수 + 불규칙한 노이즈)
        overload = self._create_overload_sound(duration, sample_rate)
        abnormal_sounds.append({
            'name': 'overload',
            'description': '과부하 소리 - 전체 주파수 + 불규칙한 노이즈',
            'audio_data': overload,
            'label': 1,
            'frequency_range': '20-8000Hz',
            'characteristics': ['불규칙한 노이즈', '전체 주파수', '과부하']
        })
        
        return abnormal_sounds
    
    def _create_normal_compressor_sound(self, duration: float, sample_rate: int) -> np.ndarray:
        """정상 압축기 소리 생성"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 기본 저주파 (60Hz)
        base_freq = 60
        base_signal = np.sin(2 * np.pi * base_freq * t)
        
        # 하모닉스 (120Hz, 180Hz)
        harmonic1 = 0.3 * np.sin(2 * np.pi * 120 * t)
        harmonic2 = 0.1 * np.sin(2 * np.pi * 180 * t)
        
        # 일정한 리듬 (0.5Hz)
        rhythm = 0.2 * np.sin(2 * np.pi * 0.5 * t)
        
        # 백그라운드 노이즈
        noise = 0.05 * np.random.normal(0, 1, len(t))
        
        # 합성
        signal = base_signal + harmonic1 + harmonic2 + rhythm + noise
        
        # 정규화
        signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal
    
    def _create_normal_fan_sound(self, duration: float, sample_rate: int) -> np.ndarray:
        """정상 팬 소리 생성"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 기본 중주파 (300Hz)
        base_freq = 300
        base_signal = np.sin(2 * np.pi * base_freq * t)
        
        # 하모닉스 (600Hz, 900Hz)
        harmonic1 = 0.4 * np.sin(2 * np.pi * 600 * t)
        harmonic2 = 0.2 * np.sin(2 * np.pi * 900 * t)
        
        # 부드러운 소음 (화이트 노이즈 필터링)
        noise = np.random.normal(0, 1, len(t))
        noise = signal.butter(4, 0.1, btype='low')(noise)[0] * 0.1
        
        # 합성
        signal = base_signal + harmonic1 + harmonic2 + noise
        
        # 정규화
        signal = signal / np.max(np.abs(signal)) * 0.7
        
        return signal
    
    def _create_normal_motor_sound(self, duration: float, sample_rate: int) -> np.ndarray:
        """정상 모터 소리 생성"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 기본 고주파 (1200Hz)
        base_freq = 1200
        base_signal = np.sin(2 * np.pi * base_freq * t)
        
        # 하모닉스 (2400Hz, 3600Hz)
        harmonic1 = 0.3 * np.sin(2 * np.pi * 2400 * t)
        harmonic2 = 0.1 * np.sin(2 * np.pi * 3600 * t)
        
        # 규칙적 패턴 (2Hz)
        pattern = 0.3 * np.sin(2 * np.pi * 2 * t)
        
        # 합성
        signal = base_signal + harmonic1 + harmonic2 + pattern
        
        # 정규화
        signal = signal / np.max(np.abs(signal)) * 0.6
        
        return signal
    
    def _create_bearing_wear_sound(self, duration: float, sample_rate: int) -> np.ndarray:
        """베어링 마모 소리 생성"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 기본 고주파 (3000Hz)
        base_freq = 3000
        base_signal = np.sin(2 * np.pi * base_freq * t)
        
        # 불규칙한 진동 (마모로 인한)
        irregular_vib = 0.5 * np.sin(2 * np.pi * 3000 * t + 0.1 * np.sin(2 * np.pi * 10 * t))
        
        # 마찰음 (고주파 노이즈)
        friction_noise = 0.3 * np.random.normal(0, 1, len(t))
        friction_noise = signal.butter(4, [0.3, 0.8], btype='band')(friction_noise)[0]
        
        # 합성
        signal = base_signal + irregular_vib + friction_noise
        
        # 정규화
        signal = signal / np.max(np.abs(signal)) * 0.9
        
        return signal
    
    def _create_unbalance_sound(self, duration: float, sample_rate: int) -> np.ndarray:
        """언밸런스 소리 생성"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 기본 저주파 (80Hz)
        base_freq = 80
        base_signal = np.sin(2 * np.pi * base_freq * t)
        
        # 주기적 진동 (언밸런스로 인한)
        periodic_vib = 0.6 * np.sin(2 * np.pi * 80 * t + 0.2 * np.sin(2 * np.pi * 5 * t))
        
        # 리듬 변화 (불안정)
        rhythm_change = 0.3 * np.sin(2 * np.pi * 0.3 * t)
        
        # 합성
        signal = base_signal + periodic_vib + rhythm_change
        
        # 정규화
        signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal
    
    def _create_friction_sound(self, duration: float, sample_rate: int) -> np.ndarray:
        """마찰 소리 생성"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 기본 중주파 (800Hz)
        base_freq = 800
        base_signal = np.sin(2 * np.pi * base_freq * t)
        
        # 긁는 소리 (중주파 노이즈)
        scraping_noise = 0.4 * np.random.normal(0, 1, len(t))
        scraping_noise = signal.butter(4, [0.2, 0.6], btype='band')(scraping_noise)[0]
        
        # 불안정한 진동
        unstable_vib = 0.3 * np.sin(2 * np.pi * 800 * t + 0.5 * np.sin(2 * np.pi * 15 * t))
        
        # 합성
        signal = base_signal + scraping_noise + unstable_vib
        
        # 정규화
        signal = signal / np.max(np.abs(signal)) * 0.7
        
        return signal
    
    def _create_overload_sound(self, duration: float, sample_rate: int) -> np.ndarray:
        """과부하 소리 생성"""
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # 전체 주파수 범위의 불규칙한 노이즈
        overload_noise = np.random.normal(0, 1, len(t))
        
        # 저주파 과부하 (50Hz)
        low_freq_overload = 0.6 * np.sin(2 * np.pi * 50 * t)
        
        # 중주파 과부하 (400Hz)
        mid_freq_overload = 0.4 * np.sin(2 * np.pi * 400 * t)
        
        # 고주파 과부하 (2000Hz)
        high_freq_overload = 0.3 * np.sin(2 * np.pi * 2000 * t)
        
        # 불규칙한 진동
        irregular_vib = 0.5 * np.sin(2 * np.pi * 100 * t + 0.3 * np.sin(2 * np.pi * 20 * t))
        
        # 합성
        signal = overload_noise + low_freq_overload + mid_freq_overload + high_freq_overload + irregular_vib
        
        # 정규화
        signal = signal / np.max(np.abs(signal)) * 0.9
        
        return signal
    
    # ===== 2. 도메인 지식 기반 규칙 생성 =====
    
    def create_domain_knowledge_rules(self) -> Dict:
        """기계 엔지니어의 도메인 지식을 기반으로 한 규칙 생성"""
        try:
            print("🔧 도메인 지식 기반 규칙 생성 시작")
            
            rules = {
                'normal_patterns': {
                    'compressor': {
                        'frequency_range': (20, 200),
                        'rms_threshold': (0.1, 0.3),
                        'zcr_threshold': (0.05, 0.15),
                        'spectral_centroid_range': (100, 500),
                        'stability_factor': 0.8
                    },
                    'fan': {
                        'frequency_range': (200, 1000),
                        'rms_threshold': (0.2, 0.4),
                        'zcr_threshold': (0.1, 0.25),
                        'spectral_centroid_range': (300, 800),
                        'stability_factor': 0.9
                    },
                    'motor': {
                        'frequency_range': (1000, 5000),
                        'rms_threshold': (0.15, 0.35),
                        'zcr_threshold': (0.08, 0.2),
                        'spectral_centroid_range': (1200, 3000),
                        'stability_factor': 0.85
                    }
                },
                'abnormal_patterns': {
                    'bearing_wear': {
                        'frequency_range': (2000, 8000),
                        'rms_threshold': (0.4, 1.0),
                        'zcr_threshold': (0.3, 0.8),
                        'spectral_centroid_range': (3000, 6000),
                        'irregularity_factor': 0.7
                    },
                    'unbalance': {
                        'frequency_range': (50, 500),
                        'rms_threshold': (0.3, 0.8),
                        'zcr_threshold': (0.2, 0.6),
                        'spectral_centroid_range': (80, 300),
                        'periodicity_factor': 0.6
                    },
                    'friction': {
                        'frequency_range': (500, 3000),
                        'rms_threshold': (0.25, 0.7),
                        'zcr_threshold': (0.15, 0.5),
                        'spectral_centroid_range': (800, 2000),
                        'scraping_factor': 0.8
                    },
                    'overload': {
                        'frequency_range': (20, 8000),
                        'rms_threshold': (0.5, 1.0),
                        'zcr_threshold': (0.4, 0.9),
                        'spectral_centroid_range': (100, 4000),
                        'chaos_factor': 0.9
                    }
                },
                'expert_heuristics': {
                    'stability_check': 'RMS와 ZCR이 일정한 범위 내에서 유지되는가?',
                    'frequency_consistency': '주파수 분포가 예상 범위 내에 있는가?',
                    'pattern_regularity': '패턴이 규칙적인가? (정상) 또는 불규칙한가? (이상)',
                    'harmonic_analysis': '하모닉스가 정상적인가?',
                    'noise_level': '노이즈 레벨이 허용 범위 내에 있는가?'
                }
            }
            
            self.domain_knowledge = rules
            print("✅ 도메인 지식 기반 규칙 생성 완료")
            return rules
            
        except Exception as e:
            print(f"❌ 도메인 지식 규칙 생성 오류: {e}")
            return {'error': str(e)}
    
    # ===== 3. 시뮬레이션 기반 학습 =====
    
    def create_simulation_training_data(self) -> Dict:
        """시뮬레이션 기반 훈련 데이터 생성"""
        try:
            print("🎮 시뮬레이션 기반 훈련 데이터 생성 시작")
            
            simulation_data = {
                'scenarios': [],
                'training_samples': [],
                'validation_samples': []
            }
            
            # 1. 다양한 시나리오 생성
            scenarios = self._create_simulation_scenarios()
            simulation_data['scenarios'] = scenarios
            
            # 2. 각 시나리오별 오디오 데이터 생성
            for scenario in scenarios:
                audio_data = self._generate_scenario_audio(scenario)
                simulation_data['training_samples'].extend(audio_data['training'])
                simulation_data['validation_samples'].extend(audio_data['validation'])
            
            print(f"✅ 시뮬레이션 데이터 생성 완료: {len(simulation_data['training_samples'])}개 훈련 샘플")
            return simulation_data
            
        except Exception as e:
            print(f"❌ 시뮬레이션 데이터 생성 오류: {e}")
            return {'error': str(e)}
    
    def _create_simulation_scenarios(self) -> List[Dict]:
        """시뮬레이션 시나리오 생성"""
        scenarios = [
            {
                'name': 'normal_operation',
                'description': '정상 작동 상태',
                'conditions': {
                    'temperature': (20, 25),
                    'humidity': (40, 60),
                    'load': (80, 100),
                    'vibration': (0.1, 0.3)
                },
                'expected_sound': 'normal',
                'duration': 30.0
            },
            {
                'name': 'bearing_wear_early',
                'description': '베어링 마모 초기 단계',
                'conditions': {
                    'temperature': (25, 30),
                    'humidity': (50, 70),
                    'load': (70, 90),
                    'vibration': (0.3, 0.5)
                },
                'expected_sound': 'abnormal',
                'duration': 30.0
            },
            {
                'name': 'bearing_wear_severe',
                'description': '베어링 마모 심각 단계',
                'conditions': {
                    'temperature': (30, 35),
                    'humidity': (60, 80),
                    'load': (60, 80),
                    'vibration': (0.5, 0.8)
                },
                'expected_sound': 'abnormal',
                'duration': 30.0
            },
            {
                'name': 'unbalance_condition',
                'description': '언밸런스 상태',
                'conditions': {
                    'temperature': (22, 28),
                    'humidity': (45, 65),
                    'load': (85, 95),
                    'vibration': (0.4, 0.7)
                },
                'expected_sound': 'abnormal',
                'duration': 30.0
            },
            {
                'name': 'overload_condition',
                'description': '과부하 상태',
                'conditions': {
                    'temperature': (35, 40),
                    'humidity': (70, 90),
                    'load': (95, 100),
                    'vibration': (0.6, 1.0)
                },
                'expected_sound': 'abnormal',
                'duration': 30.0
            }
        ]
        
        return scenarios
    
    def _generate_scenario_audio(self, scenario: Dict) -> Dict:
        """시나리오별 오디오 데이터 생성"""
        try:
            duration = scenario['duration']
            sample_rate = 16000
            
            if scenario['expected_sound'] == 'normal':
                # 정상 소리 생성
                audio_data = self._create_normal_compressor_sound(duration, sample_rate)
                label = 0
            else:
                # 이상 소리 생성 (시나리오에 따라)
                if 'bearing_wear' in scenario['name']:
                    audio_data = self._create_bearing_wear_sound(duration, sample_rate)
                elif 'unbalance' in scenario['name']:
                    audio_data = self._create_unbalance_sound(duration, sample_rate)
                elif 'overload' in scenario['name']:
                    audio_data = self._create_overload_sound(duration, sample_rate)
                else:
                    audio_data = self._create_bearing_wear_sound(duration, sample_rate)
                label = 1
            
            # 환경 조건에 따른 노이즈 추가
            audio_data = self._add_environmental_noise(audio_data, scenario['conditions'])
            
            return {
                'training': [{
                    'audio_data': audio_data,
                    'label': label,
                    'scenario': scenario['name'],
                    'conditions': scenario['conditions']
                }],
                'validation': [{
                    'audio_data': audio_data,
                    'label': label,
                    'scenario': scenario['name'],
                    'conditions': scenario['conditions']
                }]
            }
            
        except Exception as e:
            print(f"⚠️ 시나리오 오디오 생성 오류: {e}")
            return {'training': [], 'validation': []}
    
    def _add_environmental_noise(self, audio_data: np.ndarray, conditions: Dict) -> np.ndarray:
        """환경 조건에 따른 노이즈 추가"""
        try:
            # 온도에 따른 노이즈 레벨 조정
            temp_factor = (conditions['temperature'][0] + conditions['temperature'][1]) / 2 / 25.0
            
            # 습도에 따른 노이즈 레벨 조정
            humidity_factor = (conditions['humidity'][0] + conditions['humidity'][1]) / 2 / 50.0
            
            # 진동에 따른 노이즈 레벨 조정
            vibration_factor = (conditions['vibration'][0] + conditions['vibration'][1]) / 2 / 0.5
            
            # 노이즈 생성
            noise_level = 0.1 * temp_factor * humidity_factor * vibration_factor
            noise = np.random.normal(0, noise_level, len(audio_data))
            
            # 오디오에 노이즈 추가
            noisy_audio = audio_data + noise
            
            # 정규화
            noisy_audio = noisy_audio / np.max(np.abs(noisy_audio)) * 0.9
            
            return noisy_audio
            
        except Exception as e:
            print(f"⚠️ 환경 노이즈 추가 오류: {e}")
            return audio_data
    
    # ===== 4. 데이터 저장 및 관리 =====
    
    def save_training_data(self, data: Dict, filepath: str = "data/pre_hardware_training.json"):
        """훈련 데이터 저장"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 오디오 데이터는 별도 파일로 저장
            audio_files = []
            for i, sample in enumerate(data.get('training_samples', [])):
                audio_file = f"data/audio/training_{i}.wav"
                os.makedirs(os.path.dirname(audio_file), exist_ok=True)
                sf.write(audio_file, sample['audio_data'], 16000)
                audio_files.append(audio_file)
            
            # 메타데이터만 JSON으로 저장
            metadata = {
                'training_samples_count': len(data.get('training_samples', [])),
                'validation_samples_count': len(data.get('validation_samples', [])),
                'audio_files': audio_files,
                'scenarios': data.get('scenarios', []),
                'generation_timestamp': str(np.datetime64('now'))
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 훈련 데이터 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 훈련 데이터 저장 오류: {e}")
            return False
    
    def load_training_data(self, filepath: str = "data/pre_hardware_training.json") -> Dict:
        """훈련 데이터 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # 오디오 데이터 로드
            training_samples = []
            for audio_file in metadata.get('audio_files', []):
                if os.path.exists(audio_file):
                    audio_data, sr = sf.read(audio_file)
                    training_samples.append({
                        'audio_data': audio_data,
                        'sample_rate': sr,
                        'file_path': audio_file
                    })
            
            print(f"✅ 훈련 데이터 로드 완료: {len(training_samples)}개 샘플")
            return {
                'training_samples': training_samples,
                'metadata': metadata
            }
            
        except Exception as e:
            print(f"❌ 훈련 데이터 로드 오류: {e}")
            return {'error': str(e)}

# 사용 예제
if __name__ == "__main__":
    # 실제 하드웨어 설치 전 AI 학습 전략 테스트
    trainer = PreHardwareTrainingStrategies()
    
    print("🔧 실제 하드웨어 설치 전 AI 학습 전략 테스트")
    print("=" * 60)
    
    # 1. 합성 데이터 생성
    print("\n1️⃣ 합성 데이터 생성")
    synthetic_data = trainer.generate_synthetic_audio_data(duration=5.0)
    
    # 2. 도메인 지식 기반 규칙 생성
    print("\n2️⃣ 도메인 지식 기반 규칙 생성")
    domain_rules = trainer.create_domain_knowledge_rules()
    
    # 3. 시뮬레이션 기반 훈련 데이터 생성
    print("\n3️⃣ 시뮬레이션 기반 훈련 데이터 생성")
    simulation_data = trainer.create_simulation_training_data()
    
    # 4. 데이터 저장
    print("\n4️⃣ 데이터 저장")
    trainer.save_training_data(simulation_data)
    
    print("\n🎉 실제 하드웨어 설치 전 AI 학습 전략 완료!")
    print("   기계 엔지니어의 도메인 지식을 활용한 사전 학습 준비 완료")
