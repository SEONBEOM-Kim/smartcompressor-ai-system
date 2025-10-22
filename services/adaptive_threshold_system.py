#!/usr/bin/env python3
"""
적응형 임계값 시스템
24시간 고장 신호 자동 감지를 위한 동적 임계값 조정 시스템
"""

import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FailureType(Enum):
    """고장 유형"""
    NORMAL = "normal"
    COMPRESSOR_FAILURE = "compressor_failure"
    MOTOR_FAILURE = "motor_failure"
    BEARING_FAILURE = "bearing_failure"
    ELECTRICAL_FAILURE = "electrical_failure"
    VIBRATION_FAILURE = "vibration_failure"
    TEMPERATURE_FAILURE = "temperature_failure"

@dataclass
class ThresholdConfig:
    """임계값 설정"""
    base_threshold: float = 45.0  # 기본 45dB
    temperature_factor: float = 0.1  # 온도 영향 계수
    time_factor: float = 0.05  # 시간대 영향 계수
    seasonal_factor: float = 0.15  # 계절 영향 계수
    vibration_factor: float = 0.2  # 진동 영향 계수
    power_factor: float = 0.1  # 전력 영향 계수
    failure_threshold: float = 0.8  # 고장 판정 임계값

class AdaptiveThresholdSystem:
    """적응형 임계값 시스템"""
    
    def __init__(self, config_path: str = "data/adaptive_threshold_config.json"):
        self.config_path = config_path
        self.config = ThresholdConfig()
        self.failure_history = []
        self.threshold_history = []
        self.learning_data = []
        
        # 고장 패턴 데이터베이스
        self.failure_patterns = {
            FailureType.COMPRESSOR_FAILURE: {
                'decibel_range': (60, 80),
                'frequency_range': (100, 500),
                'duration_min': 300,  # 5분 이상
                'pattern': 'continuous_high'
            },
            FailureType.MOTOR_FAILURE: {
                'decibel_range': (55, 75),
                'frequency_range': (50, 200),
                'duration_min': 180,  # 3분 이상
                'pattern': 'intermittent_high'
            },
            FailureType.BEARING_FAILURE: {
                'decibel_range': (50, 70),
                'frequency_range': (20, 100),
                'duration_min': 600,  # 10분 이상
                'pattern': 'gradual_increase'
            },
            FailureType.ELECTRICAL_FAILURE: {
                'decibel_range': (40, 60),
                'frequency_range': (1000, 5000),
                'duration_min': 60,  # 1분 이상
                'pattern': 'spike_pattern'
            }
        }
        
        self._load_config()
        logger.info("적응형 임계값 시스템 초기화 완료")
    
    def _load_config(self):
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.config = ThresholdConfig(**config_data)
                logger.info("설정 파일 로드 완료")
        except Exception as e:
            logger.warning(f"설정 파일 로드 실패, 기본값 사용: {e}")
    
    def _save_config(self):
        """설정 파일 저장"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config.__dict__, f, indent=2, ensure_ascii=False)
            logger.info("설정 파일 저장 완료")
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
    
    def calculate_adaptive_threshold(self, 
                                   temperature: float,
                                   time_of_day: int,
                                   season: str,
                                   vibration_level: float = 0.0,
                                   power_consumption: float = 0.0,
                                   historical_data: List[Dict] = None) -> float:
        """적응형 임계값 계산"""
        
        # 기본 임계값
        threshold = self.config.base_threshold
        
        # 1. 온도 보정
        temp_adjustment = self._calculate_temperature_adjustment(temperature)
        
        # 2. 시간대 보정
        time_adjustment = self._calculate_time_adjustment(time_of_day)
        
        # 3. 계절 보정
        seasonal_adjustment = self._calculate_seasonal_adjustment(season)
        
        # 4. 진동 보정
        vibration_adjustment = self._calculate_vibration_adjustment(vibration_level)
        
        # 5. 전력 보정
        power_adjustment = self._calculate_power_adjustment(power_consumption)
        
        # 6. 학습된 패턴 보정
        learning_adjustment = self._calculate_learning_adjustment(historical_data)
        
        # 최종 임계값 계산
        final_threshold = (threshold + 
                          temp_adjustment + 
                          time_adjustment + 
                          seasonal_adjustment + 
                          vibration_adjustment + 
                          power_adjustment + 
                          learning_adjustment)
        
        # 임계값 범위 제한 (30dB ~ 70dB)
        final_threshold = max(30.0, min(70.0, final_threshold))
        
        # 임계값 히스토리 저장
        self.threshold_history.append({
            'timestamp': datetime.now().isoformat(),
            'threshold': final_threshold,
            'temperature': temperature,
            'time_of_day': time_of_day,
            'season': season,
            'adjustments': {
                'temperature': temp_adjustment,
                'time': time_adjustment,
                'seasonal': seasonal_adjustment,
                'vibration': vibration_adjustment,
                'power': power_adjustment,
                'learning': learning_adjustment
            }
        })
        
        return final_threshold
    
    def _calculate_temperature_adjustment(self, temperature: float) -> float:
        """온도 기반 임계값 조정"""
        if temperature < 0:
            return -5.0  # 매우 추운 날: 임계값 낮춤
        elif temperature < 10:
            return -3.0  # 추운 날: 임계값 낮춤
        elif temperature < 20:
            return 0.0   # 적당한 날: 조정 없음
        elif temperature < 30:
            return 2.0   # 따뜻한 날: 임계값 높임
        else:
            return 5.0   # 더운 날: 임계값 높임
    
    def _calculate_time_adjustment(self, time_of_day: int) -> float:
        """시간대 기반 임계값 조정"""
        if 22 <= time_of_day or time_of_day <= 6:
            return -2.0  # 밤시간: 임계값 낮춤
        elif 7 <= time_of_day <= 9:
            return 1.0   # 아침 출근시간: 임계값 높임
        elif 18 <= time_of_day <= 21:
            return 0.5   # 저녁 시간: 약간 높임
        else:
            return 0.0   # 일반 시간: 조정 없음
    
    def _calculate_seasonal_adjustment(self, season: str) -> float:
        """계절 기반 임계값 조정"""
        seasonal_adjustments = {
            'spring': 0.0,
            'summer': 2.0,   # 여름: 임계값 높임
            'autumn': 0.0,
            'winter': -3.0   # 겨울: 임계값 낮춤
        }
        return seasonal_adjustments.get(season, 0.0)
    
    def _calculate_vibration_adjustment(self, vibration_level: float) -> float:
        """진동 기반 임계값 조정"""
        if vibration_level > 0.8:
            return 3.0   # 높은 진동: 임계값 높임
        elif vibration_level > 0.5:
            return 1.0   # 중간 진동: 약간 높임
        else:
            return 0.0   # 낮은 진동: 조정 없음
    
    def _calculate_power_adjustment(self, power_consumption: float) -> float:
        """전력 소비 기반 임계값 조정"""
        if power_consumption > 150:
            return 2.0   # 높은 전력: 임계값 높임
        elif power_consumption < 50:
            return -1.0  # 낮은 전력: 임계값 낮춤
        else:
            return 0.0   # 일반 전력: 조정 없음
    
    def _calculate_learning_adjustment(self, historical_data: List[Dict]) -> float:
        """학습된 패턴 기반 임계값 조정"""
        if not historical_data or len(historical_data) < 10:
            return 0.0
        
        # 최근 24시간 데이터 분석
        recent_data = historical_data[-24:]
        
        # 평균 데시벨 레벨 계산
        avg_decibel = np.mean([d.get('decibel_level', 0) for d in recent_data])
        
        # 패턴 분석
        if avg_decibel > 50:
            return 2.0   # 높은 소음 패턴: 임계값 높임
        elif avg_decibel < 35:
            return -2.0  # 낮은 소음 패턴: 임계값 낮춤
        else:
            return 0.0   # 일반 패턴: 조정 없음
    
    def detect_failure(self, 
                      decibel_level: float,
                      frequency_data: Dict,
                      duration: float,
                      temperature: float,
                      vibration_level: float = 0.0,
                      power_consumption: float = 0.0) -> Tuple[bool, FailureType, float]:
        """고장 감지"""
        
        # 현재 시간 정보
        now = datetime.now()
        time_of_day = now.hour
        season = self._get_current_season(now)
        
        # 적응형 임계값 계산
        adaptive_threshold = self.calculate_adaptive_threshold(
            temperature=temperature,
            time_of_day=time_of_day,
            season=season,
            vibration_level=vibration_level,
            power_consumption=power_consumption
        )
        
        # 고장 패턴 분석
        failure_detected = False
        failure_type = FailureType.NORMAL
        confidence = 0.0
        
        for ftype, pattern in self.failure_patterns.items():
            if self._analyze_failure_pattern(
                decibel_level, frequency_data, duration, pattern
            ):
                failure_detected = True
                failure_type = ftype
                confidence = self._calculate_confidence(
                    decibel_level, frequency_data, duration, pattern, adaptive_threshold
                )
                break
        
        # 고장 감지 결과 저장
        if failure_detected:
            self.failure_history.append({
                'timestamp': now.isoformat(),
                'failure_type': failure_type.value,
                'confidence': confidence,
                'decibel_level': decibel_level,
                'adaptive_threshold': adaptive_threshold,
                'temperature': temperature,
                'vibration_level': vibration_level,
                'power_consumption': power_consumption
            })
            
            logger.warning(f"고장 감지: {failure_type.value}, 신뢰도: {confidence:.2f}")
        
        return failure_detected, failure_type, confidence
    
    def _analyze_failure_pattern(self, 
                               decibel_level: float,
                               frequency_data: Dict,
                               duration: float,
                               pattern: Dict) -> bool:
        """고장 패턴 분석"""
        
        # 데시벨 범위 확인
        decibel_min, decibel_max = pattern['decibel_range']
        if not (decibel_min <= decibel_level <= decibel_max):
            return False
        
        # 주파수 범위 확인
        if 'frequency_range' in frequency_data:
            freq_min, freq_max = pattern['frequency_range']
            freq_centroid = frequency_data.get('spectral_centroid', 0)
            if not (freq_min <= freq_centroid <= freq_max):
                return False
        
        # 지속 시간 확인
        if duration < pattern['duration_min']:
            return False
        
        return True
    
    def _calculate_confidence(self, 
                            decibel_level: float,
                            frequency_data: Dict,
                            duration: float,
                            pattern: Dict,
                            adaptive_threshold: float) -> float:
        """고장 신뢰도 계산"""
        
        # 데시벨 신뢰도 (임계값 대비)
        decibel_confidence = min(1.0, (decibel_level - adaptive_threshold) / 20.0)
        
        # 지속 시간 신뢰도
        duration_confidence = min(1.0, duration / (pattern['duration_min'] * 2))
        
        # 주파수 신뢰도
        freq_confidence = 1.0
        if 'frequency_range' in frequency_data:
            freq_min, freq_max = pattern['frequency_range']
            freq_centroid = frequency_data.get('spectral_centroid', 0)
            if freq_min <= freq_centroid <= freq_max:
                freq_confidence = 1.0
            else:
                freq_confidence = 0.5
        
        # 종합 신뢰도
        total_confidence = (decibel_confidence * 0.4 + 
                          duration_confidence * 0.3 + 
                          freq_confidence * 0.3)
        
        return min(1.0, max(0.0, total_confidence))
    
    def _get_current_season(self, date: datetime) -> str:
        """현재 계절 계산"""
        month = date.month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def get_failure_statistics(self, hours: int = 24) -> Dict:
        """고장 통계 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_failures = [
            f for f in self.failure_history 
            if datetime.fromisoformat(f['timestamp']) >= cutoff_time
        ]
        
        if not recent_failures:
            return {
                'total_failures': 0,
                'failure_types': {},
                'avg_confidence': 0.0,
                'most_common_failure': None
            }
        
        # 고장 유형별 통계
        failure_types = {}
        for failure in recent_failures:
            ftype = failure['failure_type']
            failure_types[ftype] = failure_types.get(ftype, 0) + 1
        
        # 평균 신뢰도
        avg_confidence = np.mean([f['confidence'] for f in recent_failures])
        
        # 가장 흔한 고장 유형
        most_common = max(failure_types.items(), key=lambda x: x[1])[0] if failure_types else None
        
        return {
            'total_failures': len(recent_failures),
            'failure_types': failure_types,
            'avg_confidence': avg_confidence,
            'most_common_failure': most_common,
            'recent_failures': recent_failures[-10:]  # 최근 10개
        }
    
    def update_learning_data(self, sensor_data: Dict):
        """학습 데이터 업데이트"""
        self.learning_data.append({
            'timestamp': datetime.now().isoformat(),
            'data': sensor_data
        })
        
        # 최근 1000개 데이터만 유지
        if len(self.learning_data) > 1000:
            self.learning_data = self.learning_data[-1000:]
    
    def export_failure_report(self, output_path: str = "data/failure_report.json"):
        """고장 보고서 내보내기"""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'threshold_config': self.config.__dict__,
                'failure_statistics': self.get_failure_statistics(24),
                'threshold_history': self.threshold_history[-100:],  # 최근 100개
                'failure_history': self.failure_history[-50:]  # 최근 50개
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"고장 보고서 내보내기 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"고장 보고서 내보내기 실패: {e}")
            return False

# 사용 예제
if __name__ == "__main__":
    # 적응형 임계값 시스템 초기화
    ats = AdaptiveThresholdSystem()
    
    # 테스트 데이터
    test_data = {
        'decibel_level': 65.0,
        'frequency_data': {
            'spectral_centroid': 300.0,
            'spectral_rolloff': 2000.0
        },
        'duration': 400.0,  # 6분 40초
        'temperature': 15.0,
        'vibration_level': 0.3,
        'power_consumption': 120.0
    }
    
    # 고장 감지 테스트
    failure_detected, failure_type, confidence = ats.detect_failure(**test_data)
    
    print(f"고장 감지: {failure_detected}")
    print(f"고장 유형: {failure_type.value}")
    print(f"신뢰도: {confidence:.2f}")
    
    # 통계 조회
    stats = ats.get_failure_statistics(24)
    print(f"24시간 고장 통계: {stats}")
