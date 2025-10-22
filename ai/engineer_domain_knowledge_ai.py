#!/usr/bin/env python3
"""
기계 엔지니어 도메인 지식 기반 AI 학습
실제 하드웨어 설치 전에 엔지니어의 경험과 지식을 활용한 AI 학습
"""

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.stats import kurtosis, skew
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class EngineerDomainKnowledgeAI:
    """기계 엔지니어 도메인 지식 기반 AI"""
    
    def __init__(self):
        self.domain_rules = {}
        self.expert_heuristics = {}
        self.training_data = {}
        
        print("🔧 기계 엔지니어 도메인 지식 기반 AI 초기화")
        print("   실제 하드웨어 설치 전 사전 학습 시스템")
    
    # ===== 1. 엔지니어 지식 기반 규칙 생성 =====
    
    def create_engineer_knowledge_rules(self) -> Dict:
        """기계 엔지니어의 경험과 지식을 기반으로 한 규칙 생성"""
        try:
            print("🔧 엔지니어 지식 기반 규칙 생성 시작")
            
            rules = {
                'sound_classification': {
                    'normal_sounds': {
                        'compressor_normal': {
                            'description': '정상 압축기 소리',
                            'frequency_range': (20, 200),
                            'rms_range': (0.1, 0.3),
                            'zcr_range': (0.05, 0.15),
                            'spectral_centroid_range': (100, 500),
                            'stability_threshold': 0.8,
                            'pattern_regularity': 'high',
                            'expert_notes': '일정한 리듬, 저주파, 안정적'
                        },
                        'fan_normal': {
                            'description': '정상 팬 소리',
                            'frequency_range': (200, 1000),
                            'rms_range': (0.2, 0.4),
                            'zcr_range': (0.1, 0.25),
                            'spectral_centroid_range': (300, 800),
                            'stability_threshold': 0.9,
                            'pattern_regularity': 'high',
                            'expert_notes': '부드러운 소음, 중주파, 안정적'
                        },
                        'motor_normal': {
                            'description': '정상 모터 소리',
                            'frequency_range': (1000, 5000),
                            'rms_range': (0.15, 0.35),
                            'zcr_range': (0.08, 0.2),
                            'spectral_centroid_range': (1200, 3000),
                            'stability_threshold': 0.85,
                            'pattern_regularity': 'high',
                            'expert_notes': '규칙적 패턴, 고주파, 안정적'
                        }
                    },
                    'abnormal_sounds': {
                        'bearing_wear': {
                            'description': '베어링 마모 소리',
                            'frequency_range': (2000, 8000),
                            'rms_range': (0.4, 1.0),
                            'zcr_range': (0.3, 0.8),
                            'spectral_centroid_range': (3000, 6000),
                            'irregularity_threshold': 0.7,
                            'pattern_regularity': 'low',
                            'expert_notes': '불규칙한 진동, 고주파, 마찰음',
                            'severity_indicators': ['고주파 진동 증가', '불규칙한 패턴', '마찰음']
                        },
                        'unbalance': {
                            'description': '언밸런스 소리',
                            'frequency_range': (50, 500),
                            'rms_range': (0.3, 0.8),
                            'zcr_range': (0.2, 0.6),
                            'spectral_centroid_range': (80, 300),
                            'periodicity_threshold': 0.6,
                            'pattern_regularity': 'medium',
                            'expert_notes': '주기적 진동, 저주파, 리듬 변화',
                            'severity_indicators': ['주기적 진동', '저주파 증가', '리듬 불안정']
                        },
                        'friction': {
                            'description': '마찰 소리',
                            'frequency_range': (500, 3000),
                            'rms_range': (0.25, 0.7),
                            'zcr_range': (0.15, 0.5),
                            'spectral_centroid_range': (800, 2000),
                            'scraping_threshold': 0.8,
                            'pattern_regularity': 'low',
                            'expert_notes': '긁는 소리, 중주파, 불안정',
                            'severity_indicators': ['긁는 소리', '중주파 노이즈', '불안정한 진동']
                        },
                        'overload': {
                            'description': '과부하 소리',
                            'frequency_range': (20, 8000),
                            'rms_range': (0.5, 1.0),
                            'zcr_range': (0.4, 0.9),
                            'spectral_centroid_range': (100, 4000),
                            'chaos_threshold': 0.9,
                            'pattern_regularity': 'very_low',
                            'expert_notes': '불규칙한 노이즈, 전체 주파수, 과부하',
                            'severity_indicators': ['전체 주파수 노이즈', '불규칙한 진동', '과부하 신호']
                        }
                    }
                },
                'diagnostic_heuristics': {
                    'stability_check': {
                        'description': '안정성 검사',
                        'method': 'RMS와 ZCR의 변동계수 계산',
                        'threshold': 0.2,
                        'expert_rule': '변동계수가 0.2 미만이면 정상, 이상이면 이상'
                    },
                    'frequency_consistency': {
                        'description': '주파수 일관성 검사',
                        'method': '스펙트럼 센트로이드의 안정성 측정',
                        'threshold': 0.3,
                        'expert_rule': '주파수 분포가 일정하면 정상, 변화가 크면 이상'
                    },
                    'pattern_regularity': {
                        'description': '패턴 규칙성 검사',
                        'method': '자기상관 함수를 이용한 주기성 측정',
                        'threshold': 0.7,
                        'expert_rule': '주기성이 높으면 정상, 낮으면 이상'
                    },
                    'harmonic_analysis': {
                        'description': '하모닉스 분석',
                        'method': '기본 주파수의 하모닉스 존재 여부 확인',
                        'threshold': 0.5,
                        'expert_rule': '하모닉스가 정상적이면 정상, 비정상적이면 이상'
                    },
                    'noise_level': {
                        'description': '노이즈 레벨 검사',
                        'method': '백그라운드 노이즈 레벨 측정',
                        'threshold': 0.1,
                        'expert_rule': '노이즈 레벨이 낮으면 정상, 높으면 이상'
                    }
                },
                'severity_assessment': {
                    'mild': {
                        'description': '경미한 이상',
                        'indicators': ['약간의 불규칙성', '주파수 변화 미미', '안정성 유지'],
                        'action': '모니터링 강화'
                    },
                    'moderate': {
                        'description': '중간 정도 이상',
                        'indicators': ['명확한 불규칙성', '주파수 변화 감지', '안정성 저하'],
                        'action': '점검 계획 수립'
                    },
                    'severe': {
                        'description': '심각한 이상',
                        'indicators': ['심각한 불규칙성', '주파수 변화 심각', '안정성 상실'],
                        'action': '즉시 점검 필요'
                    }
                }
            }
            
            self.domain_rules = rules
            print("✅ 엔지니어 지식 기반 규칙 생성 완료")
            return rules
            
        except Exception as e:
            print(f"❌ 엔지니어 지식 규칙 생성 오류: {e}")
            return {'error': str(e)}
    
    # ===== 2. 도메인 지식 기반 특징 추출 =====
    
    def extract_domain_features(self, audio_data: np.ndarray, sr: int) -> Dict:
        """도메인 지식 기반 특징 추출"""
        try:
            features = {}
            
            # 1. 기본 특징들
            features['rms'] = np.sqrt(np.mean(audio_data ** 2))
            features['zcr'] = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))
            features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr))
            features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sr))
            
            # 2. 엔지니어 지식 기반 특징들
            features['stability_factor'] = self._calculate_stability_factor(audio_data)
            features['frequency_consistency'] = self._calculate_frequency_consistency(audio_data, sr)
            features['pattern_regularity'] = self._calculate_pattern_regularity(audio_data)
            features['harmonic_ratio'] = self._calculate_harmonic_ratio(audio_data, sr)
            features['noise_level'] = self._calculate_noise_level(audio_data)
            
            # 3. 고급 특징들
            features['kurtosis'] = kurtosis(audio_data)
            features['skewness'] = skew(audio_data)
            features['crest_factor'] = np.max(np.abs(audio_data)) / features['rms']
            features['impulse_factor'] = np.max(np.abs(audio_data)) / np.mean(np.abs(audio_data))
            
            # 4. 주파수 도메인 특징들
            features['spectral_flatness'] = np.mean(librosa.feature.spectral_flatness(y=audio_data))
            features['spectral_contrast'] = np.mean(librosa.feature.spectral_contrast(y=audio_data, sr=sr))
            features['mfcc_mean'] = np.mean(librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13), axis=1)
            features['mfcc_std'] = np.std(librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13), axis=1)
            
            return features
            
        except Exception as e:
            print(f"⚠️ 도메인 특징 추출 오류: {e}")
            return {}
    
    def _calculate_stability_factor(self, audio_data: np.ndarray) -> float:
        """안정성 계수 계산"""
        try:
            # RMS의 변동계수 계산
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
            print(f"⚠️ 안정성 계수 계산 오류: {e}")
            return 0.5
    
    def _calculate_frequency_consistency(self, audio_data: np.ndarray, sr: int) -> float:
        """주파수 일관성 계산"""
        try:
            # 스펙트럼 센트로이드의 안정성 측정
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
            
            if len(spectral_centroids) > 1:
                consistency = 1.0 / (1.0 + np.std(spectral_centroids) / np.mean(spectral_centroids))
            else:
                consistency = 1.0
            
            return min(1.0, max(0.0, consistency))
            
        except Exception as e:
            print(f"⚠️ 주파수 일관성 계산 오류: {e}")
            return 0.5
    
    def _calculate_pattern_regularity(self, audio_data: np.ndarray) -> float:
        """패턴 규칙성 계산"""
        try:
            # 자기상관 함수를 이용한 주기성 측정
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # 최대 자기상관값 (0 제외)
            if len(autocorr) > 1:
                max_autocorr = np.max(autocorr[1:])
                regularity = max_autocorr / autocorr[0]
            else:
                regularity = 0.0
            
            return min(1.0, max(0.0, regularity))
            
        except Exception as e:
            print(f"⚠️ 패턴 규칙성 계산 오류: {e}")
            return 0.5
    
    def _calculate_harmonic_ratio(self, audio_data: np.ndarray, sr: int) -> float:
        """하모닉스 비율 계산"""
        try:
            # FFT 계산
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/sr)
            
            # 양의 주파수만 사용
            positive_freqs = freqs[:len(freqs)//2]
            positive_fft = np.abs(fft[:len(fft)//2])
            
            # 기본 주파수 찾기
            fundamental_freq = positive_freqs[np.argmax(positive_fft)]
            
            if fundamental_freq > 0:
                # 하모닉스 확인 (2배, 3배 주파수)
                harmonic2_idx = np.argmin(np.abs(positive_freqs - 2 * fundamental_freq))
                harmonic3_idx = np.argmin(np.abs(positive_freqs - 3 * fundamental_freq))
                
                # 하모닉스 비율 계산
                fundamental_amp = positive_fft[np.argmax(positive_fft)]
                harmonic2_amp = positive_fft[harmonic2_idx]
                harmonic3_amp = positive_fft[harmonic3_idx]
                
                harmonic_ratio = (harmonic2_amp + harmonic3_amp) / (2 * fundamental_amp)
            else:
                harmonic_ratio = 0.0
            
            return min(1.0, max(0.0, harmonic_ratio))
            
        except Exception as e:
            print(f"⚠️ 하모닉스 비율 계산 오류: {e}")
            return 0.5
    
    def _calculate_noise_level(self, audio_data: np.ndarray) -> float:
        """노이즈 레벨 계산"""
        try:
            # 고주파 노이즈 측정
            high_freq_noise = np.std(audio_data)
            
            # 정규화
            noise_level = min(1.0, high_freq_noise / 0.5)
            
            return noise_level
            
        except Exception as e:
            print(f"⚠️ 노이즈 레벨 계산 오류: {e}")
            return 0.5
    
    # ===== 3. 엔지니어 지식 기반 진단 =====
    
    def engineer_based_diagnosis(self, audio_data: np.ndarray, sr: int) -> Dict:
        """엔지니어 지식 기반 진단"""
        try:
            print("🔧 엔지니어 지식 기반 진단 시작")
            
            # 특징 추출
            features = self.extract_domain_features(audio_data, sr)
            
            # 진단 수행
            diagnosis = {
                'prediction': 0,  # 0: 정상, 1: 이상
                'confidence': 0.0,
                'severity': 'normal',
                'anomaly_type': 'none',
                'expert_analysis': {},
                'recommendations': []
            }
            
            # 1. 기본 규칙 기반 진단
            basic_diagnosis = self._basic_rule_diagnosis(features)
            diagnosis.update(basic_diagnosis)
            
            # 2. 엔지니어 휴리스틱 진단
            heuristic_diagnosis = self._heuristic_diagnosis(features)
            diagnosis['expert_analysis'].update(heuristic_diagnosis)
            
            # 3. 심각도 평가
            severity_assessment = self._assess_severity(features, diagnosis)
            diagnosis['severity'] = severity_assessment['severity']
            diagnosis['recommendations'] = severity_assessment['recommendations']
            
            # 4. 최종 진단
            final_diagnosis = self._final_diagnosis(diagnosis)
            diagnosis.update(final_diagnosis)
            
            print(f"✅ 엔지니어 지식 기반 진단 완료: {diagnosis['prediction']} ({diagnosis['confidence']:.3f})")
            return diagnosis
            
        except Exception as e:
            print(f"❌ 엔지니어 지식 기반 진단 오류: {e}")
            return {'error': str(e)}
    
    def _basic_rule_diagnosis(self, features: Dict) -> Dict:
        """기본 규칙 기반 진단"""
        try:
            # 정상 소리 규칙 확인
            normal_score = 0
            abnormal_score = 0
            
            # RMS 규칙
            if 0.1 <= features['rms'] <= 0.3:
                normal_score += 1
            elif features['rms'] > 0.4:
                abnormal_score += 1
            
            # ZCR 규칙
            if 0.05 <= features['zcr'] <= 0.15:
                normal_score += 1
            elif features['zcr'] > 0.3:
                abnormal_score += 1
            
            # 스펙트럼 센트로이드 규칙
            if 100 <= features['spectral_centroid'] <= 500:
                normal_score += 1
            elif features['spectral_centroid'] > 3000:
                abnormal_score += 1
            
            # 안정성 규칙
            if features['stability_factor'] > 0.8:
                normal_score += 1
            elif features['stability_factor'] < 0.5:
                abnormal_score += 1
            
            # 패턴 규칙성 규칙
            if features['pattern_regularity'] > 0.7:
                normal_score += 1
            elif features['pattern_regularity'] < 0.3:
                abnormal_score += 1
            
            # 진단 결과
            if normal_score > abnormal_score:
                prediction = 0  # 정상
                confidence = normal_score / (normal_score + abnormal_score)
                anomaly_type = 'none'
            else:
                prediction = 1  # 이상
                confidence = abnormal_score / (normal_score + abnormal_score)
                anomaly_type = self._identify_anomaly_type(features)
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'anomaly_type': anomaly_type,
                'normal_score': normal_score,
                'abnormal_score': abnormal_score
            }
            
        except Exception as e:
            print(f"⚠️ 기본 규칙 진단 오류: {e}")
            return {'prediction': 0, 'confidence': 0.0, 'anomaly_type': 'none'}
    
    def _heuristic_diagnosis(self, features: Dict) -> Dict:
        """엔지니어 휴리스틱 진단"""
        try:
            heuristic_analysis = {}
            
            # 안정성 검사
            if features['stability_factor'] > 0.8:
                heuristic_analysis['stability'] = '정상 - 안정적인 신호'
            elif features['stability_factor'] > 0.5:
                heuristic_analysis['stability'] = '주의 - 약간의 불안정성'
            else:
                heuristic_analysis['stability'] = '이상 - 심각한 불안정성'
            
            # 주파수 일관성 검사
            if features['frequency_consistency'] > 0.7:
                heuristic_analysis['frequency'] = '정상 - 일관된 주파수 분포'
            elif features['frequency_consistency'] > 0.4:
                heuristic_analysis['frequency'] = '주의 - 주파수 변화 감지'
            else:
                heuristic_analysis['frequency'] = '이상 - 심각한 주파수 변화'
            
            # 패턴 규칙성 검사
            if features['pattern_regularity'] > 0.7:
                heuristic_analysis['pattern'] = '정상 - 규칙적인 패턴'
            elif features['pattern_regularity'] > 0.4:
                heuristic_analysis['pattern'] = '주의 - 패턴 변화 감지'
            else:
                heuristic_analysis['pattern'] = '이상 - 불규칙한 패턴'
            
            # 하모닉스 분석
            if features['harmonic_ratio'] > 0.5:
                heuristic_analysis['harmonics'] = '정상 - 정상적인 하모닉스'
            elif features['harmonic_ratio'] > 0.2:
                heuristic_analysis['harmonics'] = '주의 - 하모닉스 변화'
            else:
                heuristic_analysis['harmonics'] = '이상 - 비정상적인 하모닉스'
            
            # 노이즈 레벨 검사
            if features['noise_level'] < 0.2:
                heuristic_analysis['noise'] = '정상 - 낮은 노이즈 레벨'
            elif features['noise_level'] < 0.5:
                heuristic_analysis['noise'] = '주의 - 중간 노이즈 레벨'
            else:
                heuristic_analysis['noise'] = '이상 - 높은 노이즈 레벨'
            
            return heuristic_analysis
            
        except Exception as e:
            print(f"⚠️ 휴리스틱 진단 오류: {e}")
            return {}
    
    def _identify_anomaly_type(self, features: Dict) -> str:
        """이상 유형 식별"""
        try:
            # 베어링 마모 확인
            if (features['spectral_centroid'] > 3000 and 
                features['rms'] > 0.4 and 
                features['pattern_regularity'] < 0.5):
                return 'bearing_wear'
            
            # 언밸런스 확인
            elif (features['spectral_centroid'] < 300 and 
                  features['rms'] > 0.3 and 
                  features['pattern_regularity'] > 0.4):
                return 'unbalance'
            
            # 마찰 확인
            elif (500 <= features['spectral_centroid'] <= 2000 and 
                  features['rms'] > 0.25 and 
                  features['pattern_regularity'] < 0.6):
                return 'friction'
            
            # 과부하 확인
            elif (features['rms'] > 0.5 and 
                  features['noise_level'] > 0.5 and 
                  features['pattern_regularity'] < 0.3):
                return 'overload'
            
            else:
                return 'unknown'
                
        except Exception as e:
            print(f"⚠️ 이상 유형 식별 오류: {e}")
            return 'unknown'
    
    def _assess_severity(self, features: Dict, diagnosis: Dict) -> Dict:
        """심각도 평가"""
        try:
            severity_indicators = []
            
            # 안정성 지표
            if features['stability_factor'] < 0.3:
                severity_indicators.append('심각한 불안정성')
            elif features['stability_factor'] < 0.6:
                severity_indicators.append('불안정성 감지')
            
            # 주파수 일관성 지표
            if features['frequency_consistency'] < 0.3:
                severity_indicators.append('심각한 주파수 변화')
            elif features['frequency_consistency'] < 0.6:
                severity_indicators.append('주파수 변화 감지')
            
            # 패턴 규칙성 지표
            if features['pattern_regularity'] < 0.3:
                severity_indicators.append('심각한 패턴 불규칙성')
            elif features['pattern_regularity'] < 0.6:
                severity_indicators.append('패턴 변화 감지')
            
            # 노이즈 레벨 지표
            if features['noise_level'] > 0.7:
                severity_indicators.append('높은 노이즈 레벨')
            elif features['noise_level'] > 0.4:
                severity_indicators.append('노이즈 레벨 증가')
            
            # 심각도 결정
            if len(severity_indicators) >= 3:
                severity = 'severe'
                recommendations = ['즉시 점검 필요', '운전 중단 고려', '전문가 상담']
            elif len(severity_indicators) >= 2:
                severity = 'moderate'
                recommendations = ['점검 계획 수립', '모니터링 강화', '예방 정비 고려']
            elif len(severity_indicators) >= 1:
                severity = 'mild'
                recommendations = ['모니터링 강화', '정기 점검', '추가 관찰']
            else:
                severity = 'normal'
                recommendations = ['정상 운영', '정기 모니터링']
            
            return {
                'severity': severity,
                'indicators': severity_indicators,
                'recommendations': recommendations
            }
            
        except Exception as e:
            print(f"⚠️ 심각도 평가 오류: {e}")
            return {'severity': 'normal', 'indicators': [], 'recommendations': ['정상 운영']}
    
    def _final_diagnosis(self, diagnosis: Dict) -> Dict:
        """최종 진단"""
        try:
            # 신뢰도 조정
            if diagnosis['severity'] == 'severe':
                diagnosis['confidence'] = min(1.0, diagnosis['confidence'] + 0.2)
            elif diagnosis['severity'] == 'moderate':
                diagnosis['confidence'] = min(1.0, diagnosis['confidence'] + 0.1)
            
            # 최종 예측 조정
            if diagnosis['severity'] in ['severe', 'moderate']:
                diagnosis['prediction'] = 1  # 이상
            elif diagnosis['severity'] == 'mild':
                diagnosis['prediction'] = 1  # 이상 (경미하지만)
            else:
                diagnosis['prediction'] = 0  # 정상
            
            return diagnosis
            
        except Exception as e:
            print(f"⚠️ 최종 진단 오류: {e}")
            return diagnosis

# 사용 예제
if __name__ == "__main__":
    # 기계 엔지니어 도메인 지식 기반 AI 테스트
    engineer_ai = EngineerDomainKnowledgeAI()
    
    print("🔧 기계 엔지니어 도메인 지식 기반 AI 테스트")
    print("=" * 60)
    
    # 1. 엔지니어 지식 기반 규칙 생성
    print("\n1️⃣ 엔지니어 지식 기반 규칙 생성")
    domain_rules = engineer_ai.create_engineer_knowledge_rules()
    
    # 2. 가상의 오디오 데이터로 테스트
    print("\n2️⃣ 가상의 오디오 데이터로 테스트")
    
    # 정상 소리 시뮬레이션
    t = np.linspace(0, 5, 80000)
    normal_audio = 0.3 * np.sin(2 * np.pi * 60 * t) + 0.1 * np.sin(2 * np.pi * 120 * t)
    normal_audio += 0.05 * np.random.normal(0, 1, len(t))
    
    # 이상 소리 시뮬레이션
    abnormal_audio = 0.5 * np.sin(2 * np.pi * 60 * t) + 0.3 * np.sin(2 * np.pi * 3000 * t)
    abnormal_audio += 0.2 * np.random.normal(0, 1, len(t))
    
    # 정상 소리 진단
    print("\n3️⃣ 정상 소리 진단")
    normal_diagnosis = engineer_ai.engineer_based_diagnosis(normal_audio, 16000)
    print(f"   예측: {normal_diagnosis['prediction']} ({'정상' if normal_diagnosis['prediction'] == 0 else '이상'})")
    print(f"   신뢰도: {normal_diagnosis['confidence']:.3f}")
    print(f"   심각도: {normal_diagnosis['severity']}")
    print(f"   이상 유형: {normal_diagnosis['anomaly_type']}")
    
    # 이상 소리 진단
    print("\n4️⃣ 이상 소리 진단")
    abnormal_diagnosis = engineer_ai.engineer_based_diagnosis(abnormal_audio, 16000)
    print(f"   예측: {abnormal_diagnosis['prediction']} ({'정상' if abnormal_diagnosis['prediction'] == 0 else '이상'})")
    print(f"   신뢰도: {abnormal_diagnosis['confidence']:.3f}")
    print(f"   심각도: {abnormal_diagnosis['severity']}")
    print(f"   이상 유형: {abnormal_diagnosis['anomaly_type']}")
    
    print("\n🎉 기계 엔지니어 도메인 지식 기반 AI 테스트 완료!")
    print("   실제 하드웨어 설치 전 사전 학습 준비 완료")
