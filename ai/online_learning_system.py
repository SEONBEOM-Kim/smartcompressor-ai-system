#!/usr/bin/env python3
"""
온라인 학습 시스템
24시간 모니터링 데이터를 실시간으로 학습하여 모델 성능 지속 개선
"""

import numpy as np
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from collections import deque
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import threading
import time

class OnlineLearningSystem:
    def __init__(self, 
                 model_save_path: str = "data/models/",
                 learning_rate: float = 0.01,
                 memory_size: int = 10000,
                 update_frequency: int = 100):
        """
        온라인 학습 시스템 초기화
        
        Args:
            model_save_path: 모델 저장 경로
            learning_rate: 학습률
            memory_size: 메모리에 유지할 샘플 수
            update_frequency: 모델 업데이트 주기 (샘플 수)
        """
        self.model_save_path = model_save_path
        os.makedirs(model_save_path, exist_ok=True)
        
        self.learning_rate = learning_rate
        self.memory_size = memory_size
        self.update_frequency = update_frequency
        
        # 학습 데이터 버퍼
        self.feature_buffer = deque(maxlen=memory_size)
        self.label_buffer = deque(maxlen=memory_size)
        self.timestamp_buffer = deque(maxlen=memory_size)
        
        # 모델들
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.pca = None
        
        # 통계 정보
        self.normal_stats = {}
        self.anomaly_stats = {}
        
        # 학습 상태
        self.is_learning = False
        self.total_samples = 0
        self.last_update = None
        
        # 스레드 안전을 위한 락
        self.lock = threading.Lock()
        
        print(f"🧠 온라인 학습 시스템 초기화")
        print(f"📚 학습률: {learning_rate}")
        print(f"💾 메모리 크기: {memory_size}")
        print(f"🔄 업데이트 주기: {update_frequency}샘플")
    
    def add_sample(self, features: Dict[str, float], 
                  is_anomaly: bool, 
                  confidence: float = 1.0,
                  timestamp: datetime = None):
        """
        새로운 샘플 추가 및 온라인 학습
        
        Args:
            features: 추출된 특징
            is_anomaly: 이상 여부
            confidence: 신뢰도 (0.0-1.0)
            timestamp: 시간
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
            # 특징 벡터로 변환
            feature_vector = np.array(list(features.values()))
            
            # 버퍼에 추가
            self.feature_buffer.append(feature_vector)
            self.label_buffer.append(is_anomaly)
            self.timestamp_buffer.append(timestamp)
            
            self.total_samples += 1
            
            # 통계 업데이트
            self._update_statistics(feature_vector, is_anomaly, confidence)
            
            # 주기적 모델 업데이트
            if self.total_samples % self.update_frequency == 0:
                self._trigger_model_update()
    
    def _update_statistics(self, features: np.ndarray, 
                          is_anomaly: bool, confidence: float):
        """통계 정보 업데이트"""
        feature_names = list(self._get_default_features().keys())
        
        for i, feature_name in enumerate(feature_names):
            if i < len(features):
                value = features[i]
                
                if is_anomaly:
                    if feature_name not in self.anomaly_stats:
                        self.anomaly_stats[feature_name] = {
                            'values': [],
                            'count': 0,
                            'mean': 0,
                            'std': 0
                        }
                    
                    stats = self.anomaly_stats[feature_name]
                    stats['values'].append(value)
                    stats['count'] += 1
                    
                    # 이동 평균으로 통계 업데이트
                    if stats['count'] == 1:
                        stats['mean'] = value
                        stats['std'] = 0
                    else:
                        old_mean = stats['mean']
                        stats['mean'] = old_mean + (value - old_mean) / stats['count']
                        stats['std'] = np.sqrt(
                            (stats['std']**2 * (stats['count']-1) + (value - stats['mean'])**2) / stats['count']
                        )
                    
                    # 최근 1000개만 유지
                    if len(stats['values']) > 1000:
                        stats['values'] = stats['values'][-1000:]
                else:
                    if feature_name not in self.normal_stats:
                        self.normal_stats[feature_name] = {
                            'values': [],
                            'count': 0,
                            'mean': 0,
                            'std': 0
                        }
                    
                    stats = self.normal_stats[feature_name]
                    stats['values'].append(value)
                    stats['count'] += 1
                    
                    # 이동 평균으로 통계 업데이트
                    if stats['count'] == 1:
                        stats['mean'] = value
                        stats['std'] = 0
                    else:
                        old_mean = stats['mean']
                        stats['mean'] = old_mean + (value - old_mean) / stats['count']
                        stats['std'] = np.sqrt(
                            (stats['std']**2 * (stats['count']-1) + (value - stats['mean'])**2) / stats['count']
                        )
                    
                    # 최근 5000개만 유지
                    if len(stats['values']) > 5000:
                        stats['values'] = stats['values'][-5000:]
    
    def _trigger_model_update(self):
        """모델 업데이트 트리거"""
        if len(self.feature_buffer) < 50:  # 최소 샘플 수
            return
        
        print(f"🔄 모델 업데이트 시작 (샘플 수: {len(self.feature_buffer)})")
        
        try:
            # 데이터 준비
            X = np.array(list(self.feature_buffer))
            y = np.array(list(self.label_buffer))
            
            # 정상 데이터만 사용 (이상 탐지 모델)
            normal_mask = ~y
            X_normal = X[normal_mask]
            
            if len(X_normal) < 10:
                print("❌ 정상 데이터가 부족하여 모델 업데이트 건너뜀")
                return
            
            # 정규화
            X_scaled = self.scaler.fit_transform(X_normal)
            
            # PCA 차원 축소
            n_components = min(10, X_scaled.shape[1])
            self.pca = PCA(n_components=n_components, random_state=42)
            X_pca = self.pca.fit_transform(X_scaled)
            
            # Isolation Forest 업데이트
            contamination = min(0.1, max(0.01, np.sum(y) / len(y)))
            self.isolation_forest = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            self.isolation_forest.fit(X_pca)
            
            self.last_update = datetime.now()
            print(f"✅ 모델 업데이트 완료 (오염률: {contamination:.3f})")
            
            # 모델 저장
            self._save_model()
            
        except Exception as e:
            print(f"❌ 모델 업데이트 오류: {e}")
    
    def predict(self, features: Dict[str, float]) -> Dict:
        """
        이상 탐지 예측
        
        Args:
            features: 확인할 특징
            
        Returns:
            예측 결과
        """
        if self.isolation_forest is None:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': '모델이 아직 훈련되지 않았습니다.',
                'anomaly_score': 0.0
            }
        
        try:
            # 특징 벡터 변환
            feature_vector = np.array(list(features.values())).reshape(1, -1)
            
            # 정규화 및 PCA 변환
            X_scaled = self.scaler.transform(feature_vector)
            X_pca = self.pca.transform(X_scaled)
            
            # 이상 탐지
            anomaly_score = self.isolation_forest.score_samples(X_pca)[0]
            is_anomaly = anomaly_score < 0  # 음수면 이상
            
            # 신뢰도 계산
            confidence = min(1.0, max(0.0, abs(anomaly_score)))
            
            # 통계 기반 추가 검증
            statistical_anomaly = self._check_statistical_anomaly(features)
            
            # 최종 판정
            final_anomaly = is_anomaly or statistical_anomaly
            
            message = self._get_anomaly_message(final_anomaly, confidence, statistical_anomaly)
            
            return {
                'is_anomaly': final_anomaly,
                'confidence': confidence,
                'message': message,
                'anomaly_score': float(anomaly_score),
                'statistical_anomaly': statistical_anomaly,
                'model_samples': len(self.feature_buffer),
                'last_update': self.last_update.isoformat() if self.last_update else None
            }
            
        except Exception as e:
            print(f"❌ 예측 오류: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': f'예측 중 오류 발생: {str(e)}',
                'anomaly_score': 0.0
            }
    
    def _check_statistical_anomaly(self, features: Dict[str, float]) -> bool:
        """통계 기반 이상 검사"""
        if not self.normal_stats:
            return False
        
        anomaly_count = 0
        total_features = 0
        
        for feature_name, value in features.items():
            if feature_name in self.normal_stats:
                stats = self.normal_stats[feature_name]
                if stats['count'] > 0 and stats['std'] > 0:
                    # Z-score 계산
                    z_score = abs((value - stats['mean']) / stats['std'])
                    if z_score > 3:  # 3시그마 규칙
                        anomaly_count += 1
                    total_features += 1
        
        # 30% 이상의 특징이 이상이면 전체를 이상으로 판정
        return total_features > 0 and (anomaly_count / total_features) > 0.3
    
    def _get_anomaly_message(self, is_anomaly: bool, confidence: float, 
                           statistical_anomaly: bool) -> str:
        """이상 메시지 생성"""
        if not is_anomaly:
            return "정상 작동 중"
        
        if statistical_anomaly:
            return f"통계적 이상 감지 (신뢰도: {confidence:.1%})"
        else:
            return f"모델 기반 이상 감지 (신뢰도: {confidence:.1%})"
    
    def _get_default_features(self) -> Dict[str, float]:
        """기본 특징값 반환"""
        return {
            'rms_energy': 0.0, 'energy_entropy': 0.0, 'temporal_std': 0.0,
            'spectral_centroid': 0.0, 'spectral_rolloff': 0.0, 'spectral_bandwidth': 0.0,
            'zero_crossing_rate': 0.0, 'low_freq_ratio': 0.0, 'mid_freq_ratio': 0.0,
            'high_freq_ratio': 0.0, 'mfcc_1_mean': 0.0, 'mfcc_2_mean': 0.0
        }
    
    def get_learning_statistics(self) -> Dict:
        """학습 통계 정보"""
        with self.lock:
            normal_count = sum(1 for label in self.label_buffer if not label)
            anomaly_count = sum(1 for label in self.label_buffer if label)
            
            return {
                'total_samples': self.total_samples,
                'buffer_size': len(self.feature_buffer),
                'normal_samples': normal_count,
                'anomaly_samples': anomaly_count,
                'anomaly_rate': anomaly_count / len(self.label_buffer) if self.label_buffer else 0,
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'learning_rate': self.learning_rate,
                'update_frequency': self.update_frequency
            }
    
    def get_feature_statistics(self) -> Dict:
        """특징별 통계 정보"""
        with self.lock:
            return {
                'normal_stats': self.normal_stats.copy(),
                'anomaly_stats': self.anomaly_stats.copy()
            }
    
    def _save_model(self):
        """모델 저장"""
        try:
            model_data = {
                'isolation_forest': self.isolation_forest,
                'scaler': self.scaler,
                'pca': self.pca,
                'normal_stats': self.normal_stats,
                'anomaly_stats': self.anomaly_stats,
                'total_samples': self.total_samples,
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'learning_rate': self.learning_rate
            }
            
            filepath = os.path.join(self.model_save_path, "online_learning_model.pkl")
            joblib.dump(model_data, filepath)
            
            print(f"💾 온라인 학습 모델 저장: {filepath}")
            
        except Exception as e:
            print(f"❌ 모델 저장 오류: {e}")
    
    def load_model(self, filepath: str = None):
        """모델 로드"""
        if filepath is None:
            filepath = os.path.join(self.model_save_path, "online_learning_model.pkl")
        
        if not os.path.exists(filepath):
            print(f"❌ 모델 파일을 찾을 수 없습니다: {filepath}")
            return
        
        try:
            with self.lock:
                model_data = joblib.load(filepath)
                
                self.isolation_forest = model_data['isolation_forest']
                self.scaler = model_data['scaler']
                self.pca = model_data['pca']
                self.normal_stats = model_data['normal_stats']
                self.anomaly_stats = model_data['anomaly_stats']
                self.total_samples = model_data['total_samples']
                self.learning_rate = model_data['learning_rate']
                
                if model_data['last_update']:
                    self.last_update = datetime.fromisoformat(model_data['last_update'])
                
                print(f"📂 온라인 학습 모델 로드: {filepath}")
                
        except Exception as e:
            print(f"❌ 모델 로드 오류: {e}")
    
    def reset_learning(self):
        """학습 상태 초기화"""
        with self.lock:
            self.feature_buffer.clear()
            self.label_buffer.clear()
            self.timestamp_buffer.clear()
            self.normal_stats.clear()
            self.anomaly_stats.clear()
            self.total_samples = 0
            self.last_update = None
            
            print("🔄 학습 상태 초기화 완료")
    
    def adjust_learning_rate(self, new_rate: float):
        """학습률 조정"""
        if 0.001 <= new_rate <= 1.0:
            self.learning_rate = new_rate
            print(f"📚 학습률 조정: {new_rate}")
        else:
            print("❌ 학습률은 0.001-1.0 사이여야 합니다.")

# 사용 예제
if __name__ == "__main__":
    # 온라인 학습 시스템 초기화
    online_learner = OnlineLearningSystem(
        learning_rate=0.01,
        memory_size=5000,
        update_frequency=50
    )
    
    print("🧠 온라인 학습 시스템 테스트")
    print("=" * 40)
    
    # 가상의 학습 데이터
    for i in range(200):
        features = {
            'rms_energy': np.random.normal(0.5, 0.1),
            'spectral_centroid': np.random.normal(1500, 200),
            'zero_crossing_rate': np.random.normal(0.1, 0.02)
        }
        
        # 90% 정상, 10% 이상
        is_anomaly = np.random.random() < 0.1
        online_learner.add_sample(features, is_anomaly)
    
    # 학습 통계 확인
    stats = online_learner.get_learning_statistics()
    print(f"📊 학습 통계: {stats}")
    
    # 예측 테스트
    test_features = {
        'rms_energy': 1.5,  # 이상적으로 높음
        'spectral_centroid': 800,  # 이상적으로 낮음
        'zero_crossing_rate': 0.3  # 이상적으로 높음
    }
    
    prediction = online_learner.predict(test_features)
    print(f"🔍 예측 결과: {prediction}")
