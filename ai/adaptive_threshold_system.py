#!/usr/bin/env python3
"""
적응형 임계값 시스템
24시간 모니터링 데이터를 기반으로 임계값을 동적으로 조정
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import os
from collections import deque
import statistics

class AdaptiveThresholdSystem:
    def __init__(self, 
                 update_interval_hours: int = 6,
                 history_days: int = 7,
                 sensitivity: float = 0.1):
        """
        적응형 임계값 시스템 초기화
        
        Args:
            update_interval_hours: 임계값 업데이트 간격 (시간)
            history_days: 통계 계산용 히스토리 기간 (일)
            sensitivity: 민감도 (0.0-1.0, 낮을수록 민감)
        """
        self.update_interval_hours = update_interval_hours
        self.history_days = history_days
        self.sensitivity = sensitivity
        
        # 임계값 저장소
        self.thresholds = {}
        self.feature_stats = {}
        
        # 히스토리 데이터 (시간순 정렬)
        self.history_data = deque(maxlen=history_days * 24 * 12)  # 5분 간격
        
        # 업데이트 시간 추적
        self.last_update = None
        
        print(f"🔄 적응형 임계값 시스템 초기화")
        print(f"⏰ 업데이트 간격: {update_interval_hours}시간")
        print(f"📊 히스토리 기간: {history_days}일")
        print(f"🎯 민감도: {sensitivity}")
    
    def add_data_point(self, features: Dict[str, float], 
                      is_anomaly: bool, timestamp: datetime = None):
        """
        새로운 데이터 포인트 추가
        
        Args:
            features: 추출된 특징 딕셔너리
            is_anomaly: 이상 여부
            timestamp: 시간 (None이면 현재 시간)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # 정상 데이터만 통계에 사용
        if not is_anomaly:
            data_point = {
                'timestamp': timestamp,
                'features': features.copy(),
                'is_anomaly': is_anomaly
            }
            self.history_data.append(data_point)
            
            # 임계값 업데이트 필요 여부 확인
            if self._should_update_thresholds():
                self._update_thresholds()
    
    def _should_update_thresholds(self) -> bool:
        """임계값 업데이트 필요 여부 확인"""
        if self.last_update is None:
            return True
        
        time_since_update = datetime.now() - self.last_update
        return time_since_update >= timedelta(hours=self.update_interval_hours)
    
    def _update_thresholds(self):
        """임계값 업데이트"""
        if len(self.history_data) < 10:  # 최소 데이터 필요
            return
        
        print("🔄 임계값 업데이트 중...")
        
        # 최근 데이터만 사용 (노이즈 감소)
        recent_data = list(self.history_data)[-1000:]  # 최근 1000개 샘플
        
        # 각 특징별 통계 계산
        feature_names = list(recent_data[0]['features'].keys())
        
        for feature_name in feature_names:
            values = [d['features'][feature_name] for d in recent_data]
            
            if len(values) > 0:
                # 기본 통계
                mean_val = statistics.mean(values)
                std_val = statistics.stdev(values) if len(values) > 1 else 0
                
                # 백분위수
                percentiles = {
                    'p1': np.percentile(values, 1),
                    'p5': np.percentile(values, 5),
                    'p10': np.percentile(values, 10),
                    'p25': np.percentile(values, 25),
                    'p50': np.percentile(values, 50),
                    'p75': np.percentile(values, 75),
                    'p90': np.percentile(values, 90),
                    'p95': np.percentile(values, 95),
                    'p99': np.percentile(values, 99)
                }
                
                # 적응형 임계값 계산
                # 민감도에 따라 임계값 범위 조정
                sensitivity_factor = 1.0 - self.sensitivity
                
                # 하한선: 하위 5% * 민감도
                lower_threshold = percentiles['p5'] * sensitivity_factor
                
                # 상한선: 상위 95% * (1 + 민감도)
                upper_threshold = percentiles['p95'] * (1 + sensitivity_factor)
                
                # Z-score 기반 임계값 (3시그마 규칙)
                z_lower = mean_val - (3 * std_val * sensitivity_factor)
                z_upper = mean_val + (3 * std_val * (1 + sensitivity_factor))
                
                # 두 방법의 조합
                final_lower = min(lower_threshold, z_lower)
                final_upper = max(upper_threshold, z_upper)
                
                self.thresholds[feature_name] = {
                    'lower': float(final_lower),
                    'upper': float(final_upper),
                    'mean': float(mean_val),
                    'std': float(std_val),
                    'percentiles': percentiles,
                    'sample_count': len(values),
                    'last_updated': datetime.now().isoformat()
                }
        
        self.last_update = datetime.now()
        print(f"✅ 임계값 업데이트 완료 ({len(feature_names)}개 특징)")
    
    def get_thresholds(self) -> Dict[str, Dict]:
        """현재 임계값 반환"""
        return self.thresholds.copy()
    
    def check_anomaly(self, features: Dict[str, float]) -> Dict[str, bool]:
        """
        특징별 이상 여부 확인
        
        Args:
            features: 확인할 특징 딕셔너리
            
        Returns:
            특징별 이상 여부 딕셔너리
        """
        anomalies = {}
        
        for feature_name, value in features.items():
            if feature_name in self.thresholds:
                threshold = self.thresholds[feature_name]
                is_anomaly = (value < threshold['lower'] or 
                            value > threshold['upper'])
                anomalies[feature_name] = is_anomaly
            else:
                anomalies[feature_name] = False
        
        return anomalies
    
    def get_anomaly_score(self, features: Dict[str, float]) -> float:
        """
        전체 이상 점수 계산 (0.0-1.0)
        
        Args:
            features: 확인할 특징 딕셔너리
            
        Returns:
            이상 점수 (높을수록 이상)
        """
        if not self.thresholds:
            return 0.0
        
        anomaly_scores = []
        
        for feature_name, value in features.items():
            if feature_name in self.thresholds:
                threshold = self.thresholds[feature_name]
                mean_val = threshold['mean']
                std_val = threshold['std']
                
                if std_val > 0:
                    # Z-score 계산
                    z_score = abs((value - mean_val) / std_val)
                    # 정규화된 이상 점수
                    anomaly_score = min(1.0, z_score / 3.0)  # 3시그마를 1.0으로 정규화
                    anomaly_scores.append(anomaly_score)
        
        if anomaly_scores:
            # 가중 평균 (최대값에 더 가중치)
            max_score = max(anomaly_scores)
            mean_score = statistics.mean(anomaly_scores)
            return 0.7 * max_score + 0.3 * mean_score
        
        return 0.0
    
    def get_feature_importance(self) -> Dict[str, float]:
        """특징별 중요도 계산 (변동성 기반)"""
        if not self.thresholds:
            return {}
        
        importance = {}
        
        for feature_name, stats in self.thresholds.items():
            # 변동 계수 (CV = std/mean)로 중요도 계산
            if stats['mean'] != 0:
                cv = stats['std'] / abs(stats['mean'])
                importance[feature_name] = float(cv)
            else:
                importance[feature_name] = 0.0
        
        # 정규화
        if importance:
            max_importance = max(importance.values())
            if max_importance > 0:
                for feature_name in importance:
                    importance[feature_name] /= max_importance
        
        return importance
    
    def get_statistics_summary(self) -> Dict:
        """통계 요약 정보"""
        if not self.thresholds:
            return {'total_features': 0, 'last_update': None}
        
        total_features = len(self.thresholds)
        last_update = self.last_update.isoformat() if self.last_update else None
        
        # 데이터 품질 지표
        data_quality = {
            'total_samples': len(self.history_data),
            'features_with_data': total_features,
            'update_frequency_hours': self.update_interval_hours,
            'sensitivity_level': self.sensitivity
        }
        
        # 특징별 통계 요약
        feature_summaries = {}
        for feature_name, stats in self.thresholds.items():
            feature_summaries[feature_name] = {
                'mean': stats['mean'],
                'std': stats['std'],
                'range': stats['upper'] - stats['lower'],
                'sample_count': stats['sample_count']
            }
        
        return {
            'total_features': total_features,
            'last_update': last_update,
            'data_quality': data_quality,
            'feature_summaries': feature_summaries,
            'feature_importance': self.get_feature_importance()
        }
    
    def adjust_sensitivity(self, new_sensitivity: float):
        """민감도 조정"""
        if 0.0 <= new_sensitivity <= 1.0:
            self.sensitivity = new_sensitivity
            print(f"🎯 민감도 조정: {new_sensitivity}")
            
            # 임계값 재계산
            if self.history_data:
                self._update_thresholds()
        else:
            print("❌ 민감도는 0.0-1.0 사이여야 합니다.")
    
    def save_thresholds(self, filepath: str):
        """임계값 저장"""
        data = {
            'thresholds': self.thresholds,
            'update_interval_hours': self.update_interval_hours,
            'history_days': self.history_days,
            'sensitivity': self.sensitivity,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 임계값 저장 완료: {filepath}")
    
    def load_thresholds(self, filepath: str):
        """임계값 로드"""
        if not os.path.exists(filepath):
            print(f"❌ 파일을 찾을 수 없습니다: {filepath}")
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.thresholds = data['thresholds']
        self.update_interval_hours = data['update_interval_hours']
        self.history_days = data['history_days']
        self.sensitivity = data['sensitivity']
        
        if data['last_update']:
            self.last_update = datetime.fromisoformat(data['last_update'])
        
        print(f"📂 임계값 로드 완료: {filepath}")
        print(f"📊 로드된 특징 수: {len(self.thresholds)}")

# 사용 예제
if __name__ == "__main__":
    # 적응형 임계값 시스템 초기화
    threshold_system = AdaptiveThresholdSystem(
        update_interval_hours=6,
        history_days=7,
        sensitivity=0.1
    )
    
    print("🔄 적응형 임계값 시스템 테스트")
    print("=" * 40)
    
    # 가상의 정상 데이터 추가
    for i in range(100):
        features = {
            'rms_energy': np.random.normal(0.5, 0.1),
            'spectral_centroid': np.random.normal(1500, 200),
            'zero_crossing_rate': np.random.normal(0.1, 0.02)
        }
        threshold_system.add_data_point(features, is_anomaly=False)
    
    # 임계값 확인
    thresholds = threshold_system.get_thresholds()
    print(f"📊 설정된 임계값 수: {len(thresholds)}")
    
    # 이상 데이터 테스트
    test_features = {
        'rms_energy': 2.0,  # 이상적으로 높음
        'spectral_centroid': 500,  # 이상적으로 낮음
        'zero_crossing_rate': 0.5  # 이상적으로 높음
    }
    
    anomalies = threshold_system.check_anomaly(test_features)
    anomaly_score = threshold_system.get_anomaly_score(test_features)
    
    print(f"🔍 이상 탐지 결과: {anomalies}")
    print(f"📈 이상 점수: {anomaly_score:.3f}")
