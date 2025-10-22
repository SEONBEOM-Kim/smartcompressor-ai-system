#!/usr/bin/env python3
"""
맥락 기반 고장 라벨링 시스템
시계열 패턴과 맥락을 고려한 AI 학습을 위한 라벨링 시스템
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from enum import Enum
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import librosa
from scipy import signal
from scipy.stats import zscore

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContextualPattern(Enum):
    """맥락적 패턴 유형"""
    NORMAL_OPERATION = "normal_operation"
    GRADUAL_DEGRADATION = "gradual_degradation"
    SUDDEN_FAILURE = "sudden_failure"
    INTERMITTENT_FAILURE = "intermittent_failure"
    CASCADE_FAILURE = "cascade_failure"
    SEASONAL_VARIATION = "seasonal_variation"
    MAINTENANCE_NEEDED = "maintenance_needed"

@dataclass
class ContextualFeatures:
    """맥락적 특징"""
    # 시계열 패턴 특징
    trend_slope: float = 0.0
    volatility: float = 0.0
    periodicity: float = 0.0
    autocorrelation: float = 0.0
    
    # 맥락적 특징
    temperature_context: float = 0.0
    time_context: float = 0.0
    seasonal_context: float = 0.0
    operational_context: float = 0.0
    
    # 고장 진행도 특징
    degradation_rate: float = 0.0
    failure_probability: float = 0.0
    maintenance_urgency: float = 0.0

class ContextualFailureLabeling:
    """맥락 기반 고장 라벨링 시스템"""
    
    def __init__(self, config_path: str = "data/contextual_labeling_config.json"):
        self.config_path = config_path
        self.labeling_history = []
        self.pattern_database = {}
        self.contextual_rules = {}
        self.ai_models = {}
        
        # 시계열 분석 윈도우 설정
        self.window_sizes = [60, 300, 900, 3600]  # 1분, 5분, 15분, 1시간
        self.lookback_periods = [24, 168, 720]  # 1일, 1주, 1월
        
        self._load_configuration()
        self._initialize_ai_models()
        logger.info("맥락 기반 고장 라벨링 시스템 초기화 완료")
    
    def _load_configuration(self):
        """설정 로드"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.contextual_rules = config.get('contextual_rules', {})
                    self.pattern_database = config.get('pattern_database', {})
        except Exception as e:
            logger.warning(f"설정 로드 실패, 기본값 사용: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """기본 설정 생성"""
        self.contextual_rules = {
            'gradual_degradation': {
                'min_duration': 1800,  # 30분
                'degradation_threshold': 0.1,
                'volatility_threshold': 0.05
            },
            'sudden_failure': {
                'max_duration': 300,  # 5분
                'intensity_threshold': 0.8,
                'change_rate_threshold': 0.5
            },
            'intermittent_failure': {
                'min_cycles': 3,
                'cycle_duration_range': (60, 1800),  # 1분~30분
                'reliability_threshold': 0.7
            }
        }
    
    def _initialize_ai_models(self):
        """AI 모델 초기화"""
        # 패턴 분류 모델
        self.ai_models['pattern_classifier'] = IsolationForest(
            contamination=0.1, random_state=42
        )
        
        # 맥락 분석 모델
        self.ai_models['context_analyzer'] = DBSCAN(
            eps=0.5, min_samples=5
        )
        
        # 고장 예측 모델
        self.ai_models['failure_predictor'] = IsolationForest(
            contamination=0.05, random_state=42
        )
    
    def extract_contextual_features(self, 
                                  time_series_data: List[Dict],
                                  context_data: Dict) -> ContextualFeatures:
        """맥락적 특징 추출"""
        
        if len(time_series_data) < 10:
            return ContextualFeatures()
        
        # 시계열 데이터 정리
        timestamps = [d['timestamp'] for d in time_series_data]
        decibel_values = [d['decibel_level'] for d in time_series_data]
        temperature_values = [d.get('temperature', 20) for d in time_series_data]
        
        # 시계열 패턴 특징
        trend_slope = self._calculate_trend_slope(decibel_values)
        volatility = self._calculate_volatility(decibel_values)
        periodicity = self._calculate_periodicity(decibel_values)
        autocorrelation = self._calculate_autocorrelation(decibel_values)
        
        # 맥락적 특징
        temperature_context = self._analyze_temperature_context(
            temperature_values, context_data.get('current_temperature', 20)
        )
        time_context = self._analyze_time_context(
            timestamps, context_data.get('time_of_day', 12)
        )
        seasonal_context = self._analyze_seasonal_context(
            timestamps, context_data.get('season', 'spring')
        )
        operational_context = self._analyze_operational_context(
            time_series_data, context_data
        )
        
        # 고장 진행도 특징
        degradation_rate = self._calculate_degradation_rate(decibel_values)
        failure_probability = self._calculate_failure_probability(
            decibel_values, temperature_values, context_data
        )
        maintenance_urgency = self._calculate_maintenance_urgency(
            degradation_rate, failure_probability, context_data
        )
        
        return ContextualFeatures(
            trend_slope=trend_slope,
            volatility=volatility,
            periodicity=periodicity,
            autocorrelation=autocorrelation,
            temperature_context=temperature_context,
            time_context=time_context,
            seasonal_context=seasonal_context,
            operational_context=operational_context,
            degradation_rate=degradation_rate,
            failure_probability=failure_probability,
            maintenance_urgency=maintenance_urgency
        )
    
    def _calculate_trend_slope(self, values: List[float]) -> float:
        """트렌드 기울기 계산"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        return float(slope)
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """변동성 계산"""
        if len(values) < 2:
            return 0.0
        
        return float(np.std(values))
    
    def _calculate_periodicity(self, values: List[float]) -> float:
        """주기성 계산"""
        if len(values) < 10:
            return 0.0
        
        try:
            # FFT를 사용한 주파수 분석
            fft = np.fft.fft(values)
            freqs = np.fft.fftfreq(len(values))
            
            # 주요 주파수 성분 찾기
            power_spectrum = np.abs(fft) ** 2
            dominant_freq_idx = np.argmax(power_spectrum[1:len(power_spectrum)//2]) + 1
            dominant_freq = freqs[dominant_freq_idx]
            
            return float(abs(dominant_freq))
        except:
            return 0.0
    
    def _calculate_autocorrelation(self, values: List[float]) -> float:
        """자기상관 계산"""
        if len(values) < 10:
            return 0.0
        
        try:
            # 1차 자기상관
            autocorr = np.corrcoef(values[:-1], values[1:])[0, 1]
            return float(autocorr) if not np.isnan(autocorr) else 0.0
        except:
            return 0.0
    
    def _analyze_temperature_context(self, 
                                   temperature_values: List[float],
                                   current_temperature: float) -> float:
        """온도 맥락 분석"""
        if not temperature_values:
            return 0.0
        
        avg_temp = np.mean(temperature_values)
        temp_variance = np.var(temperature_values)
        
        # 온도 변화율과 현재 온도와의 관계
        temp_change_rate = abs(current_temperature - avg_temp) / max(avg_temp, 1)
        temp_stability = 1.0 / (1.0 + temp_variance)
        
        return float(temp_change_rate * temp_stability)
    
    def _analyze_time_context(self, 
                            timestamps: List[str],
                            current_time: int) -> float:
        """시간 맥락 분석"""
        if not timestamps:
            return 0.0
        
        # 시간대별 패턴 분석
        hours = [datetime.fromisoformat(ts).hour for ts in timestamps]
        hour_distribution = np.bincount(hours, minlength=24)
        
        # 현재 시간대의 활동 수준
        current_activity = hour_distribution[current_time] / max(np.sum(hour_distribution), 1)
        
        return float(current_activity)
    
    def _analyze_seasonal_context(self, 
                                timestamps: List[str],
                                current_season: str) -> float:
        """계절 맥락 분석"""
        if not timestamps:
            return 0.0
        
        # 계절별 패턴 분석 (간단한 구현)
        seasonal_weights = {
            'spring': 1.0,
            'summer': 1.2,
            'autumn': 1.0,
            'winter': 0.8
        }
        
        return float(seasonal_weights.get(current_season, 1.0))
    
    def _analyze_operational_context(self, 
                                   time_series_data: List[Dict],
                                   context_data: Dict) -> float:
        """운영 맥락 분석"""
        if not time_series_data:
            return 0.0
        
        # 압축기 작동 패턴 분석
        compressor_states = [d.get('compressor_state', 0) for d in time_series_data]
        on_ratio = np.mean(compressor_states)
        
        # 전력 소비 패턴
        power_values = [d.get('power_consumption', 0) for d in time_series_data]
        avg_power = np.mean(power_values) if power_values else 0
        
        # 운영 강도 계산
        operational_intensity = on_ratio * (avg_power / 100.0)  # 정규화
        
        return float(operational_intensity)
    
    def _calculate_degradation_rate(self, values: List[float]) -> float:
        """성능 저하율 계산"""
        if len(values) < 10:
            return 0.0
        
        # 이동평균을 사용한 트렌드 분석
        window_size = min(10, len(values) // 2)
        moving_avg = pd.Series(values).rolling(window=window_size).mean()
        
        # 최근 값과 초기 값 비교
        if len(moving_avg.dropna()) < 2:
            return 0.0
        
        initial_avg = moving_avg.dropna().iloc[0]
        recent_avg = moving_avg.dropna().iloc[-1]
        
        degradation_rate = (recent_avg - initial_avg) / max(initial_avg, 1)
        return float(degradation_rate)
    
    def _calculate_failure_probability(self, 
                                     decibel_values: List[float],
                                     temperature_values: List[float],
                                     context_data: Dict) -> float:
        """고장 확률 계산"""
        if not decibel_values:
            return 0.0
        
        # 데시벨 기반 고장 확률
        max_decibel = max(decibel_values)
        decibel_prob = min(1.0, (max_decibel - 45) / 30)  # 45dB 기준
        
        # 온도 기반 고장 확률
        temp_variance = np.var(temperature_values) if temperature_values else 0
        temp_prob = min(1.0, temp_variance / 100)  # 온도 변동성
        
        # 맥락 기반 가중치
        context_weight = context_data.get('failure_risk_factor', 1.0)
        
        # 종합 고장 확률
        failure_prob = (decibel_prob * 0.6 + temp_prob * 0.4) * context_weight
        return float(min(1.0, failure_prob))
    
    def _calculate_maintenance_urgency(self, 
                                     degradation_rate: float,
                                     failure_probability: float,
                                     context_data: Dict) -> float:
        """유지보수 긴급도 계산"""
        # 성능 저하와 고장 확률을 종합
        urgency = (abs(degradation_rate) * 0.5 + failure_probability * 0.5)
        
        # 맥락적 요소 고려
        operational_hours = context_data.get('operational_hours', 0)
        last_maintenance = context_data.get('days_since_maintenance', 0)
        
        # 운영 시간이 길수록, 마지막 유지보수가 오래될수록 긴급도 증가
        time_factor = min(1.0, operational_hours / 10000)  # 10,000시간 기준
        maintenance_factor = min(1.0, last_maintenance / 365)  # 1년 기준
        
        urgency = urgency * (1 + time_factor * 0.3 + maintenance_factor * 0.2)
        
        return float(min(1.0, urgency))
    
    def generate_contextual_labels(self, 
                                 time_series_data: List[Dict],
                                 context_data: Dict) -> Dict:
        """맥락 기반 라벨 생성"""
        
        # 맥락적 특징 추출
        features = self.extract_contextual_features(time_series_data, context_data)
        
        # 패턴 분류
        pattern_type = self._classify_pattern(features, time_series_data)
        
        # 고장 유형 예측
        failure_type = self._predict_failure_type(features, pattern_type)
        
        # 신뢰도 계산
        confidence = self._calculate_label_confidence(features, pattern_type, failure_type)
        
        # 라벨 생성
        label = {
            'timestamp': datetime.now().isoformat(),
            'pattern_type': pattern_type.value,
            'failure_type': failure_type,
            'confidence': confidence,
            'features': features.__dict__,
            'context_data': context_data,
            'recommendations': self._generate_recommendations(features, pattern_type, failure_type)
        }
        
        # 라벨링 히스토리에 추가
        self.labeling_history.append(label)
        
        return label
    
    def _classify_pattern(self, 
                        features: ContextualFeatures,
                        time_series_data: List[Dict]) -> ContextualPattern:
        """패턴 분류"""
        
        # 점진적 성능 저하
        if (features.degradation_rate > 0.1 and 
            features.volatility < 0.05 and
            len(time_series_data) > 30):
            return ContextualPattern.GRADUAL_DEGRADATION
        
        # 급격한 고장
        if (features.volatility > 0.2 and
            features.failure_probability > 0.8):
            return ContextualPattern.SUDDEN_FAILURE
        
        # 간헐적 고장
        if (features.periodicity > 0.1 and
            features.autocorrelation < 0.3):
            return ContextualPattern.INTERMITTENT_FAILURE
        
        # 계단식 고장
        if (features.trend_slope > 0.5 and
            features.failure_probability > 0.6):
            return ContextualPattern.CASCADE_FAILURE
        
        # 계절적 변화
        if (features.seasonal_context > 0.8 and
            features.temperature_context > 0.5):
            return ContextualPattern.SEASONAL_VARIATION
        
        # 유지보수 필요
        if (features.maintenance_urgency > 0.7):
            return ContextualPattern.MAINTENANCE_NEEDED
        
        return ContextualPattern.NORMAL_OPERATION
    
    def _predict_failure_type(self, 
                            features: ContextualFeatures,
                            pattern_type: ContextualPattern) -> str:
        """고장 유형 예측"""
        
        if pattern_type == ContextualPattern.NORMAL_OPERATION:
            return "normal"
        
        # 특징 기반 고장 유형 예측
        if features.degradation_rate > 0.2 and features.volatility < 0.1:
            return "bearing_wear"
        elif features.volatility > 0.3 and features.failure_probability > 0.7:
            return "electrical_fault"
        elif features.periodicity > 0.2 and features.autocorrelation < 0.2:
            return "mechanical_looseness"
        elif features.trend_slope > 0.3 and features.maintenance_urgency > 0.6:
            return "compressor_fatigue"
        else:
            return "unknown_failure"
    
    def _calculate_label_confidence(self, 
                                  features: ContextualFeatures,
                                  pattern_type: ContextualPattern,
                                  failure_type: str) -> float:
        """라벨 신뢰도 계산"""
        
        # 특징 일관성 점수
        feature_consistency = self._calculate_feature_consistency(features)
        
        # 패턴 명확성 점수
        pattern_clarity = self._calculate_pattern_clarity(features, pattern_type)
        
        # 고장 유형 명확성 점수
        failure_clarity = self._calculate_failure_clarity(features, failure_type)
        
        # 종합 신뢰도
        confidence = (feature_consistency * 0.4 + 
                     pattern_clarity * 0.3 + 
                     failure_clarity * 0.3)
        
        return float(min(1.0, max(0.0, confidence)))
    
    def _calculate_feature_consistency(self, features: ContextualFeatures) -> float:
        """특징 일관성 계산"""
        # 특징들 간의 일관성 검사
        consistency_score = 1.0
        
        # 트렌드와 변동성의 일관성
        if features.trend_slope > 0 and features.volatility > 0.1:
            consistency_score *= 0.8
        
        # 온도 맥락과 계절 맥락의 일관성
        if abs(features.temperature_context - features.seasonal_context) > 0.5:
            consistency_score *= 0.9
        
        return consistency_score
    
    def _calculate_pattern_clarity(self, 
                                 features: ContextualFeatures,
                                 pattern_type: ContextualPattern) -> float:
        """패턴 명확성 계산"""
        if pattern_type == ContextualPattern.NORMAL_OPERATION:
            return 0.5  # 정상은 명확성이 낮음
        
        # 패턴별 명확성 기준
        clarity_scores = {
            ContextualPattern.GRADUAL_DEGRADATION: features.degradation_rate,
            ContextualPattern.SUDDEN_FAILURE: features.volatility,
            ContextualPattern.INTERMITTENT_FAILURE: features.periodicity,
            ContextualPattern.CASCADE_FAILURE: features.failure_probability,
            ContextualPattern.SEASONAL_VARIATION: features.seasonal_context,
            ContextualPattern.MAINTENANCE_NEEDED: features.maintenance_urgency
        }
        
        return clarity_scores.get(pattern_type, 0.5)
    
    def _calculate_failure_clarity(self, 
                                 features: ContextualFeatures,
                                 failure_type: str) -> float:
        """고장 유형 명확성 계산"""
        if failure_type == "normal":
            return 0.5
        
        # 고장 유형별 명확성 기준
        clarity_criteria = {
            "bearing_wear": features.degradation_rate > 0.1,
            "electrical_fault": features.volatility > 0.2,
            "mechanical_looseness": features.periodicity > 0.1,
            "compressor_fatigue": features.trend_slope > 0.2
        }
        
        return 1.0 if clarity_criteria.get(failure_type, False) else 0.3
    
    def _generate_recommendations(self, 
                                features: ContextualFeatures,
                                pattern_type: ContextualPattern,
                                failure_type: str) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        if pattern_type == ContextualPattern.GRADUAL_DEGRADATION:
            recommendations.append("성능 저하가 감지되었습니다. 정기 점검을 권장합니다.")
        
        if pattern_type == ContextualPattern.SUDDEN_FAILURE:
            recommendations.append("급격한 고장이 감지되었습니다. 즉시 점검이 필요합니다.")
        
        if pattern_type == ContextualPattern.INTERMITTENT_FAILURE:
            recommendations.append("간헐적 고장이 감지되었습니다. 연결 상태를 확인하세요.")
        
        if features.maintenance_urgency > 0.7:
            recommendations.append("유지보수가 시급합니다. 예방 정비를 권장합니다.")
        
        if features.failure_probability > 0.8:
            recommendations.append("고장 위험이 높습니다. 운영을 중단하고 점검하세요.")
        
        return recommendations
    
    def train_contextual_model(self, 
                             training_data: List[Dict],
                             labels: List[Dict]) -> Dict:
        """맥락적 모델 훈련"""
        
        if len(training_data) != len(labels):
            raise ValueError("훈련 데이터와 라벨의 개수가 일치하지 않습니다.")
        
        # 특징 추출
        features_list = []
        for data, label in zip(training_data, labels):
            context_data = label.get('context_data', {})
            features = self.extract_contextual_features(data, context_data)
            features_list.append(features)
        
        # 특징 벡터 생성
        feature_matrix = np.array([[f.trend_slope, f.volatility, f.periodicity, 
                                  f.autocorrelation, f.temperature_context, 
                                  f.time_context, f.seasonal_context, 
                                  f.operational_context, f.degradation_rate, 
                                  f.failure_probability, f.maintenance_urgency] 
                                 for f in features_list])
        
        # 라벨 벡터 생성
        pattern_labels = [label['pattern_type'] for label in labels]
        failure_labels = [label['failure_type'] for label in labels]
        
        # 모델 훈련
        training_results = {}
        
        # 패턴 분류기 훈련
        try:
            pattern_encoder = {pattern.value: i for i, pattern in enumerate(ContextualPattern)}
            pattern_y = [pattern_encoder[label] for label in pattern_labels]
            
            # 여기서는 간단한 예시로 IsolationForest 사용
            # 실제로는 더 적합한 분류기 사용
            self.ai_models['pattern_classifier'].fit(feature_matrix)
            training_results['pattern_classifier'] = "훈련 완료"
        except Exception as e:
            training_results['pattern_classifier'] = f"훈련 실패: {e}"
        
        # 맥락 분석기 훈련
        try:
            self.ai_models['context_analyzer'].fit(feature_matrix)
            training_results['context_analyzer'] = "훈련 완료"
        except Exception as e:
            training_results['context_analyzer'] = f"훈련 실패: {e}"
        
        # 고장 예측기 훈련
        try:
            failure_encoder = {ftype: i for i, ftype in enumerate(set(failure_labels))}
            failure_y = [failure_encoder[label] for label in failure_labels]
            
            self.ai_models['failure_predictor'].fit(feature_matrix)
            training_results['failure_predictor'] = "훈련 완료"
        except Exception as e:
            training_results['failure_predictor'] = f"훈련 실패: {e}"
        
        return training_results
    
    def export_labeling_data(self, output_path: str = "data/contextual_labeling_data.json"):
        """라벨링 데이터 내보내기"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            export_data = {
                'generated_at': datetime.now().isoformat(),
                'total_labels': len(self.labeling_history),
                'labeling_history': self.labeling_history[-1000:],  # 최근 1000개
                'contextual_rules': self.contextual_rules,
                'pattern_database': self.pattern_database
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"라벨링 데이터 내보내기 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"라벨링 데이터 내보내기 실패: {e}")
            return False

# 사용 예제
if __name__ == "__main__":
    # 맥락 기반 라벨링 시스템 초기화
    cfl = ContextualFailureLabeling()
    
    # 테스트 데이터
    test_time_series = [
        {'timestamp': '2024-01-01T10:00:00', 'decibel_level': 45.0, 'temperature': 20.0, 'compressor_state': 1},
        {'timestamp': '2024-01-01T10:01:00', 'decibel_level': 46.0, 'temperature': 20.1, 'compressor_state': 1},
        {'timestamp': '2024-01-01T10:02:00', 'decibel_level': 47.0, 'temperature': 20.2, 'compressor_state': 1},
        # ... 더 많은 데이터
    ]
    
    test_context = {
        'current_temperature': 20.0,
        'time_of_day': 10,
        'season': 'winter',
        'operational_hours': 5000,
        'days_since_maintenance': 30
    }
    
    # 맥락 기반 라벨 생성
    label = cfl.generate_contextual_labels(test_time_series, test_context)
    print(f"생성된 라벨: {label}")
