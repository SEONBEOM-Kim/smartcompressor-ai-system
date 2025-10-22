#!/usr/bin/env python3
"""
지능형 라벨링 시스템
AI가 라벨을 제안하고 전문가가 검증하는 시스템
"""

import numpy as np
import librosa
import json
import os
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class IntelligentLabelingSystem:
    """지능형 라벨링 시스템"""
    
    def __init__(self, model_path: str = "data/models/mimii_model.pkl"):
        self.model_path = model_path
        self.model = None
        self.scaler = None
        self.feature_names = [
            'rms', 'zcr', 'spectral_centroid', 'spectral_rolloff', 'spectral_bandwidth',
            'stability_factor', 'frequency_consistency', 'pattern_regularity', 
            'harmonic_ratio', 'noise_level'
        ]
        
        # 라벨링 히스토리
        self.labeling_history = []
        self.confidence_threshold = 0.7
        self.uncertainty_threshold = 0.3
        
        print("🧠 지능형 라벨링 시스템 초기화")
        self._load_ai_model()
        self._load_engineer_knowledge()
    
    def _load_ai_model(self):
        """AI 모델 로드"""
        try:
            print("📚 AI 모델 로드 중...")
            
            # 실제로는 훈련된 모델을 로드
            # 여기서는 가상의 모델로 구현
            self.model = MockAIModel()
            self.scaler = MockScaler()
            
            print("✅ AI 모델 로드 완료")
            
        except Exception as e:
            print(f"❌ AI 모델 로드 오류: {e}")
            self.model = None
            self.scaler = None
    
    def _load_engineer_knowledge(self):
        """엔지니어 지식 로드"""
        try:
            print("📚 엔지니어 지식 로드 중...")
            
            knowledge_path = "data/engineer_knowledge/engineer_knowledge.json"
            if os.path.exists(knowledge_path):
                with open(knowledge_path, 'r', encoding='utf-8') as f:
                    self.engineer_knowledge = json.load(f)
            else:
                # 기본 지식
                self.engineer_knowledge = {
                    'sound_classification': {
                        '정상_압축기': {'frequency_range': (20, 200), 'amplitude_range': (0.1, 0.3)},
                        '정상_팬': {'frequency_range': (200, 1000), 'amplitude_range': (0.2, 0.4)},
                        '정상_모터': {'frequency_range': (50, 500), 'amplitude_range': (0.15, 0.35)},
                        '베어링_마모': {'frequency_range': (2000, 8000), 'amplitude_range': (0.6, 1.0)},
                        '언밸런스': {'frequency_range': (50, 500), 'amplitude_range': (0.3, 0.8)},
                        '마찰': {'frequency_range': (500, 3000), 'amplitude_range': (0.25, 0.7)},
                        '과부하': {'frequency_range': (20, 8000), 'amplitude_range': (0.5, 1.0)}
                    }
                }
            
            print("✅ 엔지니어 지식 로드 완료")
            
        except Exception as e:
            print(f"❌ 엔지니어 지식 로드 오류: {e}")
            self.engineer_knowledge = {}
    
    def analyze_audio(self, audio_path: str) -> Dict:
        """오디오 분석 및 라벨 제안"""
        try:
            print(f"🎵 오디오 분석 중: {audio_path}")
            
            # 오디오 로드
            audio_data, sr = librosa.load(audio_path, sr=16000)
            
            # 특징 추출
            features = self._extract_audio_features(audio_data, sr)
            
            # AI 예측
            ai_prediction = self._predict_with_ai(features)
            
            # 엔지니어 지식 기반 검증
            knowledge_validation = self._validate_with_knowledge(features)
            
            # 불확실성 계산
            uncertainty = self._calculate_uncertainty(ai_prediction, knowledge_validation)
            
            # 최종 제안 생성
            suggestion = self._generate_label_suggestion(
                ai_prediction, knowledge_validation, uncertainty
            )
            
            print(f"✅ 오디오 분석 완료: {suggestion['suggested_label']}")
            return suggestion
            
        except Exception as e:
            print(f"❌ 오디오 분석 오류: {e}")
            return self._create_error_suggestion()
    
    def _extract_audio_features(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """오디오 특징 추출"""
        try:
            features = []
            
            # 기본 특징들
            features.append(np.sqrt(np.mean(audio_data ** 2)))  # RMS
            features.append(np.mean(librosa.feature.zero_crossing_rate(audio_data)))  # ZCR
            features.append(np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr)))  # Spectral Centroid
            features.append(np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr)))  # Spectral Rolloff
            features.append(np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)))  # Spectral Bandwidth
            
            # 안정성 계수
            stability = self._calculate_stability_factor(audio_data)
            features.append(stability)
            
            # 주파수 일관성
            frequency_consistency = self._calculate_frequency_consistency(audio_data, sr)
            features.append(frequency_consistency)
            
            # 패턴 규칙성
            pattern_regularity = self._calculate_pattern_regularity(audio_data)
            features.append(pattern_regularity)
            
            # 하모닉스 비율
            harmonic_ratio = self._calculate_harmonic_ratio(audio_data, sr)
            features.append(harmonic_ratio)
            
            # 노이즈 레벨
            noise_level = self._calculate_noise_level(audio_data)
            features.append(noise_level)
            
            return np.array(features)
            
        except Exception as e:
            print(f"⚠️ 특징 추출 오류: {e}")
            return np.zeros(10)
    
    def _predict_with_ai(self, features: np.ndarray) -> Dict:
        """AI 모델로 예측"""
        try:
            if self.model is None:
                return self._create_mock_prediction()
            
            # 특징 정규화
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # 예측 수행
            prediction = self.model.predict(features_scaled)
            probabilities = self.model.predict_proba(features_scaled)
            
            # 라벨 매핑
            label_mapping = {
                0: 'normal_compressor',
                1: 'normal_fan', 
                2: 'normal_motor',
                3: 'abnormal_bearing',
                4: 'abnormal_unbalance',
                5: 'abnormal_friction',
                6: 'abnormal_overload'
            }
            
            predicted_label = label_mapping.get(prediction[0], 'unknown')
            confidence = np.max(probabilities[0])
            
            return {
                'predicted_label': predicted_label,
                'confidence': float(confidence),
                'probabilities': probabilities[0].tolist(),
                'method': 'ai_model'
            }
            
        except Exception as e:
            print(f"⚠️ AI 예측 오류: {e}")
            return self._create_mock_prediction()
    
    def _validate_with_knowledge(self, features: np.ndarray) -> Dict:
        """엔지니어 지식으로 검증"""
        try:
            if not self.engineer_knowledge:
                return {'validated_label': 'unknown', 'confidence': 0.5, 'method': 'knowledge'}
            
            # 특징 해석
            rms = features[0]
            spectral_centroid = features[2]
            stability = features[5]
            frequency_consistency = features[6]
            
            # 엔지니어 지식 기반 분류
            if rms < 0.3 and spectral_centroid < 500 and stability > 0.8:
                return {'validated_label': 'normal_compressor', 'confidence': 0.9, 'method': 'knowledge'}
            elif rms < 0.4 and 200 < spectral_centroid < 1000 and stability > 0.8:
                return {'validated_label': 'normal_fan', 'confidence': 0.9, 'method': 'knowledge'}
            elif rms < 0.35 and 50 < spectral_centroid < 500 and stability > 0.8:
                return {'validated_label': 'normal_motor', 'confidence': 0.9, 'method': 'knowledge'}
            elif rms > 0.6 and spectral_centroid > 2000 and stability < 0.5:
                return {'validated_label': 'abnormal_bearing', 'confidence': 0.85, 'method': 'knowledge'}
            elif rms > 0.3 and 50 < spectral_centroid < 500 and stability < 0.6:
                return {'validated_label': 'abnormal_unbalance', 'confidence': 0.8, 'method': 'knowledge'}
            elif rms > 0.25 and 500 < spectral_centroid < 3000 and stability < 0.5:
                return {'validated_label': 'abnormal_friction', 'confidence': 0.75, 'method': 'knowledge'}
            elif rms > 0.5 and spectral_centroid > 1000 and stability < 0.3:
                return {'validated_label': 'abnormal_overload', 'confidence': 0.9, 'method': 'knowledge'}
            else:
                return {'validated_label': 'unknown', 'confidence': 0.5, 'method': 'knowledge'}
                
        except Exception as e:
            print(f"⚠️ 지식 검증 오류: {e}")
            return {'validated_label': 'unknown', 'confidence': 0.5, 'method': 'knowledge'}
    
    def _calculate_uncertainty(self, ai_prediction: Dict, knowledge_validation: Dict) -> float:
        """불확실성 계산"""
        try:
            # AI와 지식 검증 결과 비교
            ai_confidence = ai_prediction['confidence']
            knowledge_confidence = knowledge_validation['confidence']
            
            # 라벨 일치 여부
            label_match = ai_prediction['predicted_label'] == knowledge_validation['validated_label']
            
            # 불확실성 계산
            if label_match:
                # 라벨이 일치하면 평균 신뢰도
                uncertainty = 1.0 - (ai_confidence + knowledge_confidence) / 2
            else:
                # 라벨이 다르면 높은 불확실성
                uncertainty = 1.0 - min(ai_confidence, knowledge_confidence)
            
            return min(1.0, max(0.0, uncertainty))
            
        except Exception as e:
            print(f"⚠️ 불확실성 계산 오류: {e}")
            return 0.5
    
    def _generate_label_suggestion(self, ai_prediction: Dict, knowledge_validation: Dict, uncertainty: float) -> Dict:
        """라벨 제안 생성"""
        try:
            # 최종 라벨 결정
            if uncertainty < self.uncertainty_threshold:
                # 불확실성이 낮으면 AI 예측 사용
                final_label = ai_prediction['predicted_label']
                final_confidence = ai_prediction['confidence']
                suggestion_type = 'ai_confident'
            elif ai_prediction['predicted_label'] == knowledge_validation['validated_label']:
                # AI와 지식이 일치하면 평균 신뢰도
                final_label = ai_prediction['predicted_label']
                final_confidence = (ai_prediction['confidence'] + knowledge_validation['confidence']) / 2
                suggestion_type = 'consensus'
            else:
                # 불일치하면 지식 기반 결과 사용
                final_label = knowledge_validation['validated_label']
                final_confidence = knowledge_validation['confidence']
                suggestion_type = 'knowledge_override'
            
            # 라벨 카테고리 결정
            if 'normal' in final_label:
                category = 'normal'
            elif 'abnormal' in final_label:
                category = 'abnormal'
            else:
                category = 'unknown'
            
            # 제안 생성
            suggestion = {
                'suggested_label': final_label,
                'category': category,
                'confidence': final_confidence,
                'uncertainty': uncertainty,
                'suggestion_type': suggestion_type,
                'ai_prediction': ai_prediction,
                'knowledge_validation': knowledge_validation,
                'requires_human_review': uncertainty > self.uncertainty_threshold,
                'confidence_level': self._get_confidence_level(final_confidence),
                'reasoning': self._generate_reasoning(ai_prediction, knowledge_validation, uncertainty),
                'timestamp': datetime.now().isoformat()
            }
            
            return suggestion
            
        except Exception as e:
            print(f"⚠️ 라벨 제안 생성 오류: {e}")
            return self._create_error_suggestion()
    
    def _get_confidence_level(self, confidence: float) -> str:
        """신뢰도 레벨 결정"""
        if confidence > 0.8:
            return "매우 높음"
        elif confidence > 0.6:
            return "높음"
        elif confidence > 0.4:
            return "보통"
        else:
            return "낮음"
    
    def _generate_reasoning(self, ai_prediction: Dict, knowledge_validation: Dict, uncertainty: float) -> str:
        """추론 과정 설명"""
        try:
            reasoning_parts = []
            
            # AI 예측 설명
            ai_label = ai_prediction['predicted_label']
            ai_conf = ai_prediction['confidence']
            reasoning_parts.append(f"AI 모델이 '{ai_label}'로 예측 (신뢰도: {ai_conf:.2%})")
            
            # 지식 검증 설명
            knowledge_label = knowledge_validation['validated_label']
            knowledge_conf = knowledge_validation['confidence']
            reasoning_parts.append(f"엔지니어 지식으로 '{knowledge_label}' 검증 (신뢰도: {knowledge_conf:.2%})")
            
            # 불확실성 설명
            if uncertainty > self.uncertainty_threshold:
                reasoning_parts.append(f"불확실성이 높음 ({uncertainty:.2%}) - 전문가 검토 필요")
            else:
                reasoning_parts.append(f"불확실성이 낮음 ({uncertainty:.2%}) - 자동 라벨링 가능")
            
            return " | ".join(reasoning_parts)
            
        except Exception as e:
            return f"추론 생성 오류: {e}"
    
    def save_labeling_decision(self, audio_path: str, suggestion: Dict, human_label: str, 
                              human_confidence: float, human_notes: str = "") -> bool:
        """라벨링 결정 저장"""
        try:
            decision = {
                'audio_path': audio_path,
                'ai_suggestion': suggestion,
                'human_label': human_label,
                'human_confidence': human_confidence,
                'human_notes': human_notes,
                'agreement': suggestion['suggested_label'] == human_label,
                'confidence_difference': abs(suggestion['confidence'] - human_confidence),
                'timestamp': datetime.now().isoformat()
            }
            
            self.labeling_history.append(decision)
            
            # 파일로 저장
            self._save_labeling_history()
            
            print(f"✅ 라벨링 결정 저장 완료: {audio_path}")
            return True
            
        except Exception as e:
            print(f"❌ 라벨링 결정 저장 오류: {e}")
            return False
    
    def _save_labeling_history(self):
        """라벨링 히스토리 저장"""
        try:
            history_path = "data/labeling_history.json"
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.labeling_history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ 히스토리 저장 오류: {e}")
    
    def get_labeling_statistics(self) -> Dict:
        """라벨링 통계 조회"""
        try:
            if not self.labeling_history:
                return {'total_decisions': 0, 'agreement_rate': 0, 'average_confidence': 0}
            
            total_decisions = len(self.labeling_history)
            agreements = sum(1 for d in self.labeling_history if d['agreement'])
            agreement_rate = agreements / total_decisions
            
            avg_confidence = np.mean([d['human_confidence'] for d in self.labeling_history])
            avg_confidence_diff = np.mean([d['confidence_difference'] for d in self.labeling_history])
            
            return {
                'total_decisions': total_decisions,
                'agreement_rate': agreement_rate,
                'average_confidence': avg_confidence,
                'average_confidence_difference': avg_confidence_diff,
                'ai_accuracy': agreement_rate
            }
            
        except Exception as e:
            print(f"⚠️ 통계 계산 오류: {e}")
            return {'total_decisions': 0, 'agreement_rate': 0, 'average_confidence': 0}
    
    def _create_mock_prediction(self) -> Dict:
        """가상 예측 생성"""
        labels = ['normal_compressor', 'normal_fan', 'normal_motor', 
                 'abnormal_bearing', 'abnormal_unbalance', 'abnormal_friction', 'abnormal_overload']
        probabilities = np.random.dirichlet(np.ones(7))
        
        predicted_idx = np.argmax(probabilities)
        return {
            'predicted_label': labels[predicted_idx],
            'confidence': float(probabilities[predicted_idx]),
            'probabilities': probabilities.tolist(),
            'method': 'mock_model'
        }
    
    def _create_error_suggestion(self) -> Dict:
        """오류 제안 생성"""
        return {
            'suggested_label': 'unknown',
            'category': 'unknown',
            'confidence': 0.0,
            'uncertainty': 1.0,
            'suggestion_type': 'error',
            'requires_human_review': True,
            'confidence_level': '낮음',
            'reasoning': '오디오 분석 중 오류 발생',
            'timestamp': datetime.now().isoformat()
        }
    
    # 특징 계산 메서드들 (기존 코드와 동일)
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
    
    def _calculate_frequency_consistency(self, audio_data: np.ndarray, sr: int) -> float:
        """주파수 일관성 계산"""
        try:
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
            
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
    
    def _calculate_harmonic_ratio(self, audio_data: np.ndarray, sr: int) -> float:
        """하모닉스 비율 계산"""
        try:
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/sr)
            
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

class MockAIModel:
    """가상 AI 모델"""
    
    def predict(self, X):
        return np.random.randint(0, 7, len(X))
    
    def predict_proba(self, X):
        proba = np.random.uniform(0.1, 0.9, (len(X), 7))
        return proba / np.sum(proba, axis=1, keepdims=True)

class MockScaler:
    """가상 스케일러"""
    
    def transform(self, X):
        return X

# 사용 예제
if __name__ == "__main__":
    # 지능형 라벨링 시스템 테스트
    labeling_system = IntelligentLabelingSystem()
    
    print("🧠 지능형 라벨링 시스템 테스트")
    print("=" * 60)
    
    # 샘플 오디오 분석
    sample_audio = "data/real_audio_uploads/real_2025-09-29T12-07-31-270Z_냉장고 소리.wav"
    if os.path.exists(sample_audio):
        suggestion = labeling_system.analyze_audio(sample_audio)
        
        print(f"\n🎵 오디오 분석 결과:")
        print(f"   제안 라벨: {suggestion['suggested_label']}")
        print(f"   카테고리: {suggestion['category']}")
        print(f"   신뢰도: {suggestion['confidence']:.2%}")
        print(f"   불확실성: {suggestion['uncertainty']:.2%}")
        print(f"   제안 타입: {suggestion['suggestion_type']}")
        print(f"   전문가 검토 필요: {suggestion['requires_human_review']}")
        print(f"   추론: {suggestion['reasoning']}")
    
    print("\n🎉 지능형 라벨링 시스템 초기화 완료!")
