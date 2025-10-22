#!/usr/bin/env python3
"""
Phase 2: 적응형 시스템 구축
환경 변화에 자동으로 적응하는 AI 시스템
"""

import numpy as np
import librosa
import time
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import deque
import threading
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import joblib
import statistics

class Phase2AdaptiveSystem:
    def __init__(self, 
                 model_save_path: str = "data/models/phase2/",
                 window_size: float = 5.0,
                 sample_rate: int = 16000,
                 adaptation_interval: int = 100):  # 100샘플마다 적응
        """
        Phase 2 적응형 시스템 초기화
        
        Args:
            model_save_path: 모델 저장 경로
            window_size: 분석 윈도우 크기 (초)
            sample_rate: 샘플링 레이트
            adaptation_interval: 적응 업데이트 간격 (샘플 수)
        """
        self.model_save_path = model_save_path
        os.makedirs(model_save_path, exist_ok=True)
        
        self.window_size = window_size
        self.sample_rate = sample_rate
        self.adaptation_interval = adaptation_interval
        
        # Phase 1 시스템 (기본 이상 탐지)
        self.phase1_detector = None
        
        # 적응형 시스템들
        self.adaptive_thresholds = {}
        self.online_learner = None
        self.cluster_analyzer = None
        
        # 적응형 통계
        self.adaptation_stats = {
            'total_adaptations': 0,
            'last_adaptation': None,
            'adaptation_effectiveness': 0.0,
            'threshold_updates': 0,
            'model_updates': 0
        }
        
        # 실시간 데이터 버퍼
        self.data_buffer = deque(maxlen=1000)  # 최근 1000개 샘플
        self.performance_buffer = deque(maxlen=100)  # 최근 100개 성능 지표
        
        # 적응형 파라미터
        self.adaptation_params = {
            'sensitivity': 0.1,  # 민감도 (0.0-1.0)
            'learning_rate': 0.01,  # 학습률
            'confidence_threshold': 0.7,  # 신뢰도 임계값
            'anomaly_threshold': 0.05,  # 이상 탐지 임계값
            'adaptation_threshold': 0.1  # 적응 트리거 임계값
        }
        
        # 성능 지표
        self.performance_metrics = {
            'total_detections': 0,
            'anomaly_count': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'average_processing_time': 0.0,
            'accuracy': 0.0,
            'adaptation_accuracy': 0.0,
            'last_update': None
        }
        
        print("🔄 Phase 2: 적응형 시스템 초기화")
        print(f"⏱️ 윈도우 크기: {window_size}초")
        print(f"🎵 샘플링 레이트: {sample_rate}Hz")
        print(f"🔄 적응 간격: {adaptation_interval}샘플")
        print(f"💾 모델 저장 경로: {model_save_path}")
    
    def initialize_with_phase1(self, phase1_detector):
        """Phase 1 시스템으로 초기화"""
        self.phase1_detector = phase1_detector
        
        # Phase 1의 특징 이름 가져오기
        self.feature_names = phase1_detector.feature_names
        
        # 적응형 임계값 초기화
        self._initialize_adaptive_thresholds()
        
        # 온라인 학습 시스템 초기화
        self._initialize_online_learner()
        
        # 클러스터 분석기 초기화
        self._initialize_cluster_analyzer()
        
        print("✅ Phase 1 시스템으로 Phase 2 초기화 완료")
    
    def _initialize_adaptive_thresholds(self):
        """적응형 임계값 시스템 초기화"""
        self.adaptive_thresholds = {}
        
        for feature_name in self.feature_names:
            self.adaptive_thresholds[feature_name] = {
                'lower': 0.0,
                'upper': 1.0,
                'mean': 0.0,
                'std': 1.0,
                'percentiles': {
                    'p5': 0.0,
                    'p25': 0.25,
                    'p75': 0.75,
                    'p95': 1.0
                },
                'update_count': 0,
                'last_update': None
            }
        
        print("🔄 적응형 임계값 시스템 초기화 완료")
    
    def _initialize_online_learner(self):
        """온라인 학습 시스템 초기화"""
        self.online_learner = {
            'isolation_forest': None,
            'scaler': StandardScaler(),
            'pca': None,
            'normal_stats': {},
            'anomaly_stats': {},
            'learning_rate': self.adaptation_params['learning_rate'],
            'sample_count': 0,
            'last_update': None
        }
        
        print("🧠 온라인 학습 시스템 초기화 완료")
    
    def _initialize_cluster_analyzer(self):
        """클러스터 분석기 초기화"""
        self.cluster_analyzer = {
            'kmeans': None,
            'cluster_centers': None,
            'cluster_labels': None,
            'anomaly_clusters': set(),
            'normal_clusters': set(),
            'cluster_stats': {},
            'last_analysis': None
        }
        
        print("🔍 클러스터 분석기 초기화 완료")
    
    def detect_anomaly_adaptive(self, audio_data: np.ndarray, sr: int, 
                               ground_truth: Optional[bool] = None) -> Dict:
        """
        적응형 이상 탐지 수행
        
        Args:
            audio_data: 오디오 데이터
            sr: 샘플링 레이트
            ground_truth: 실제 이상 여부 (성능 평가용)
            
        Returns:
            적응형 이상 탐지 결과
        """
        if not self.phase1_detector or not self.phase1_detector.is_trained:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': 'Phase 1 시스템이 초기화되지 않았습니다.',
                'anomaly_type': 'system_not_initialized',
                'processing_time_ms': 0,
                'phase': 'Phase 2'
            }
        
        start_time = time.time()
        
        try:
            # 1. Phase 1 기본 탐지
            phase1_result = self.phase1_detector.detect_anomaly(audio_data, sr, ground_truth)
            
            # 2. 특징 추출
            features = self.phase1_detector.extract_enhanced_features(audio_data, sr)
            
            # 3. 적응형 임계값 검사
            adaptive_anomaly = self._check_adaptive_thresholds(features)
            
            # 4. 온라인 학습 기반 탐지
            online_anomaly = self._check_online_learning(features)
            
            # 5. 클러스터 분석 기반 탐지
            cluster_anomaly = self._check_cluster_analysis(features)
            
            # 6. 다중 검증 통합
            final_result = self._integrate_adaptive_predictions(
                phase1_result, adaptive_anomaly, online_anomaly, cluster_anomaly, features
            )
            
            # 7. 데이터 버퍼 업데이트
            self._update_data_buffer(features, final_result['is_anomaly'], ground_truth)
            
            # 8. 적응형 업데이트 (주기적)
            if len(self.data_buffer) % self.adaptation_interval == 0:
                self._perform_adaptive_update()
            
            # 9. 성능 통계 업데이트
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(final_result, ground_truth, processing_time)
            
            final_result['processing_time_ms'] = processing_time
            final_result['phase'] = 'Phase 2'
            final_result['adaptation_stats'] = self.adaptation_stats.copy()
            
            return final_result
            
        except Exception as e:
            print(f"❌ 적응형 이상 탐지 오류: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': f'적응형 분석 중 오류 발생: {str(e)}',
                'anomaly_type': 'error',
                'processing_time_ms': (time.time() - start_time) * 1000,
                'phase': 'Phase 2'
            }
    
    def _check_adaptive_thresholds(self, features: Dict[str, float]) -> Dict:
        """적응형 임계값 검사"""
        anomaly_scores = []
        anomaly_features = []
        
        for feature_name, value in features.items():
            if feature_name in self.adaptive_thresholds:
                threshold = self.adaptive_thresholds[feature_name]
                
                # Z-score 계산
                if threshold['std'] > 0:
                    z_score = abs((value - threshold['mean']) / threshold['std'])
                    anomaly_scores.append(z_score)
                    
                    # 3시그마 규칙
                    if z_score > 3:
                        anomaly_features.append(feature_name)
        
        # 전체 이상 점수
        overall_anomaly_score = np.mean(anomaly_scores) if anomaly_scores else 0.0
        
        return {
            'is_anomaly': len(anomaly_features) > 2 or overall_anomaly_score > 2.5,
            'anomaly_score': overall_anomaly_score,
            'anomaly_features': anomaly_features,
            'confidence': min(1.0, overall_anomaly_score / 3.0)
        }
    
    def _check_online_learning(self, features: Dict[str, float]) -> Dict:
        """온라인 학습 기반 탐지"""
        if not self.online_learner['isolation_forest']:
            return {'is_anomaly': False, 'confidence': 0.0}
        
        try:
            # 특징 벡터 변환
            feature_vector = np.array(list(features.values())).reshape(1, -1)
            
            # 정규화 및 PCA 변환
            X_scaled = self.online_learner['scaler'].transform(feature_vector)
            X_pca = self.online_learner['pca'].transform(X_scaled)
            
            # Isolation Forest 점수 계산
            isolation_score = self.online_learner['isolation_forest'].score_samples(X_pca)[0]
            is_anomaly = isolation_score < 0
            
            return {
                'is_anomaly': is_anomaly,
                'confidence': min(1.0, abs(isolation_score) / 2.0),
                'isolation_score': isolation_score
            }
            
        except Exception as e:
            print(f"❌ 온라인 학습 탐지 오류: {e}")
            return {'is_anomaly': False, 'confidence': 0.0}
    
    def _check_cluster_analysis(self, features: Dict[str, float]) -> Dict:
        """클러스터 분석 기반 탐지"""
        if not self.cluster_analyzer['kmeans']:
            return {'is_anomaly': False, 'confidence': 0.0}
        
        try:
            # 특징 벡터 변환
            feature_vector = np.array(list(features.values())).reshape(1, -1)
            
            # 클러스터 예측
            cluster_label = self.cluster_analyzer['kmeans'].predict(feature_vector)[0]
            
            # 클러스터 중심까지의 거리
            cluster_center = self.cluster_analyzer['cluster_centers'][cluster_label]
            distance = np.linalg.norm(feature_vector - cluster_center)
            
            # 이상 클러스터 여부 확인
            is_anomaly_cluster = cluster_label in self.cluster_analyzer['anomaly_clusters']
            
            # 거리 기반 이상 판정
            threshold_distance = np.mean([
                np.linalg.norm(center) for center in self.cluster_analyzer['cluster_centers']
            ])
            
            distance_anomaly = distance > threshold_distance * 1.5
            
            return {
                'is_anomaly': is_anomaly_cluster or distance_anomaly,
                'confidence': min(1.0, distance / threshold_distance),
                'cluster_label': cluster_label,
                'distance': distance
            }
            
        except Exception as e:
            print(f"❌ 클러스터 분석 오류: {e}")
            return {'is_anomaly': False, 'confidence': 0.0}
    
    def _integrate_adaptive_predictions(self, phase1_result: Dict, 
                                      adaptive_anomaly: Dict, 
                                      online_anomaly: Dict, 
                                      cluster_anomaly: Dict,
                                      features: Dict[str, float]) -> Dict:
        """적응형 예측 결과 통합"""
        
        # 각 시스템의 이상 여부
        phase1_detected = phase1_result['is_anomaly']
        adaptive_detected = adaptive_anomaly['is_anomaly']
        online_detected = online_anomaly['is_anomaly']
        cluster_detected = cluster_anomaly['is_anomaly']
        
        # 가중 투표 (적응형 시스템에 더 높은 가중치)
        weights = {
            'phase1': 0.3,  # 기본 시스템
            'adaptive': 0.4,  # 적응형 임계값
            'online': 0.2,   # 온라인 학습
            'cluster': 0.1   # 클러스터 분석
        }
        
        # 가중 평균 신뢰도
        weighted_confidence = (
            weights['phase1'] * phase1_result['confidence'] +
            weights['adaptive'] * adaptive_anomaly['confidence'] +
            weights['online'] * online_anomaly['confidence'] +
            weights['cluster'] * cluster_anomaly['confidence']
        )
        
        # 다수결 + 신뢰도 기반 최종 판정
        votes = [phase1_detected, adaptive_detected, online_detected, cluster_detected]
        majority_vote = sum(votes) >= 2
        
        # 신뢰도가 임계값 이상이면 최종 판정
        final_anomaly = majority_vote and weighted_confidence >= self.adaptation_params['confidence_threshold']
        
        # 이상 유형 분류 (적응형)
        anomaly_type = self._classify_adaptive_anomaly_type(
            features, phase1_result, adaptive_anomaly, online_anomaly, cluster_anomaly
        )
        
        # 메시지 생성
        message = self._generate_adaptive_message(
            final_anomaly, weighted_confidence, anomaly_type, votes
        )
        
        return {
            'is_anomaly': final_anomaly,
            'confidence': weighted_confidence,
            'message': message,
            'anomaly_type': anomaly_type,
            'individual_predictions': {
                'phase1': {
                    'prediction': phase1_detected,
                    'confidence': phase1_result['confidence'],
                    'anomaly_type': phase1_result.get('anomaly_type', 'unknown')
                },
                'adaptive': {
                    'prediction': adaptive_detected,
                    'confidence': adaptive_anomaly['confidence'],
                    'anomaly_features': adaptive_anomaly.get('anomaly_features', [])
                },
                'online': {
                    'prediction': online_detected,
                    'confidence': online_anomaly['confidence'],
                    'isolation_score': online_anomaly.get('isolation_score', 0.0)
                },
                'cluster': {
                    'prediction': cluster_detected,
                    'confidence': cluster_anomaly['confidence'],
                    'cluster_label': cluster_anomaly.get('cluster_label', -1)
                }
            },
            'voting_result': {
                'votes': votes,
                'majority_vote': majority_vote,
                'weights': weights
            }
        }
    
    def _classify_adaptive_anomaly_type(self, features: Dict[str, float], 
                                       phase1_result: Dict, 
                                       adaptive_anomaly: Dict, 
                                       online_anomaly: Dict, 
                                       cluster_anomaly: Dict) -> str:
        """적응형 이상 유형 분류"""
        
        # Phase 1 결과가 가장 신뢰할 만함
        if phase1_result.get('anomaly_type') != 'normal':
            return phase1_result['anomaly_type']
        
        # 적응형 임계값 기반 분류
        anomaly_features = adaptive_anomaly.get('anomaly_features', [])
        if 'spectral_centroid' in anomaly_features and 'zero_crossing_rate' in anomaly_features:
            return 'bearing_wear'
        elif 'rms_energy' in anomaly_features:
            return 'compressor_abnormal'
        elif 'low_freq_ratio' in anomaly_features:
            return 'refrigerant_leak'
        
        # 온라인 학습 기반 분류
        if online_anomaly.get('isolation_score', 0) < -1.0:
            return 'statistical_anomaly'
        
        # 클러스터 분석 기반 분류
        if cluster_anomaly.get('cluster_label', -1) in self.cluster_analyzer['anomaly_clusters']:
            return 'cluster_anomaly'
        
        return 'general_anomaly'
    
    def _generate_adaptive_message(self, is_anomaly: bool, confidence: float, 
                                 anomaly_type: str, votes: List[bool]) -> str:
        """적응형 메시지 생성"""
        if not is_anomaly:
            return "정상 작동 중 (적응형 시스템)"
        
        vote_count = sum(votes)
        confidence_level = "높음" if confidence > 0.8 else "보통" if confidence > 0.6 else "낮음"
        
        messages = {
            'bearing_wear': f'베어링 마모 의심 ({vote_count}/4 시스템 일치, 신뢰도: {confidence_level})',
            'compressor_abnormal': f'압축기 이상 의심 ({vote_count}/4 시스템 일치, 신뢰도: {confidence_level})',
            'refrigerant_leak': f'냉매 누출 의심 ({vote_count}/4 시스템 일치, 신뢰도: {confidence_level})',
            'statistical_anomaly': f'통계적 이상 감지 ({vote_count}/4 시스템 일치, 신뢰도: {confidence_level})',
            'cluster_anomaly': f'클러스터 기반 이상 감지 ({vote_count}/4 시스템 일치, 신뢰도: {confidence_level})',
            'general_anomaly': f'이상 소음 감지 ({vote_count}/4 시스템 일치, 신뢰도: {confidence_level})'
        }
        
        return messages.get(anomaly_type, f'이상 감지 ({vote_count}/4 시스템 일치, 신뢰도: {confidence_level})')
    
    def _update_data_buffer(self, features: Dict[str, float], is_anomaly: bool, ground_truth: Optional[bool]):
        """데이터 버퍼 업데이트"""
        data_point = {
            'timestamp': datetime.now(),
            'features': features,
            'is_anomaly': is_anomaly,
            'ground_truth': ground_truth
        }
        
        self.data_buffer.append(data_point)
    
    def _perform_adaptive_update(self):
        """적응형 업데이트 수행"""
        if len(self.data_buffer) < 50:  # 최소 데이터 필요
            return
        
        print("🔄 적응형 업데이트 수행 중...")
        
        try:
            # 1. 적응형 임계값 업데이트
            self._update_adaptive_thresholds()
            
            # 2. 온라인 학습 업데이트
            self._update_online_learning()
            
            # 3. 클러스터 분석 업데이트
            self._update_cluster_analysis()
            
            # 4. 적응 통계 업데이트
            self.adaptation_stats['total_adaptations'] += 1
            self.adaptation_stats['last_adaptation'] = datetime.now().isoformat()
            
            print("✅ 적응형 업데이트 완료")
            
        except Exception as e:
            print(f"❌ 적응형 업데이트 오류: {e}")
    
    def _update_adaptive_thresholds(self):
        """적응형 임계값 업데이트"""
        # 최근 데이터만 사용
        recent_data = list(self.data_buffer)[-500:]  # 최근 500개 샘플
        
        for feature_name in self.feature_names:
            values = [d['features'][feature_name] for d in recent_data if feature_name in d['features']]
            
            if len(values) > 10:  # 충분한 데이터가 있을 때만 업데이트
                # 통계 계산
                mean_val = statistics.mean(values)
                std_val = statistics.stdev(values) if len(values) > 1 else 0
                
                # 백분위수
                percentiles = {
                    'p5': np.percentile(values, 5),
                    'p25': np.percentile(values, 25),
                    'p75': np.percentile(values, 75),
                    'p95': np.percentile(values, 95)
                }
                
                # 적응형 임계값 계산
                sensitivity = self.adaptation_params['sensitivity']
                lower_threshold = percentiles['p5'] * (1 - sensitivity)
                upper_threshold = percentiles['p95'] * (1 + sensitivity)
                
                # 업데이트
                self.adaptive_thresholds[feature_name].update({
                    'lower': lower_threshold,
                    'upper': upper_threshold,
                    'mean': mean_val,
                    'std': std_val,
                    'percentiles': percentiles,
                    'update_count': self.adaptive_thresholds[feature_name]['update_count'] + 1,
                    'last_update': datetime.now().isoformat()
                })
        
        self.adaptation_stats['threshold_updates'] += 1
    
    def _update_online_learning(self):
        """온라인 학습 업데이트"""
        # 정상 데이터만 사용
        normal_data = [d for d in self.data_buffer if not d['is_anomaly']]
        
        if len(normal_data) < 20:  # 최소 정상 데이터 필요
            return
        
        try:
            # 특징 벡터 추출
            feature_vectors = []
            for data_point in normal_data[-100:]:  # 최근 100개만 사용
                feature_vector = np.array(list(data_point['features'].values()))
                feature_vectors.append(feature_vector)
            
            X = np.array(feature_vectors)
            
            # 정규화
            X_scaled = self.online_learner['scaler'].fit_transform(X)
            
            # PCA
            n_components = min(8, X_scaled.shape[1])
            self.online_learner['pca'] = PCA(n_components=n_components, random_state=42)
            X_pca = self.online_learner['pca'].fit_transform(X_scaled)
            
            # Isolation Forest 업데이트
            contamination = min(0.1, max(0.01, len([d for d in self.data_buffer if d['is_anomaly']]) / len(self.data_buffer)))
            self.online_learner['isolation_forest'] = IsolationForest(
                contamination=contamination,
                random_state=42,
                n_estimators=100
            )
            self.online_learner['isolation_forest'].fit(X_pca)
            
            self.online_learner['sample_count'] = len(feature_vectors)
            self.online_learner['last_update'] = datetime.now().isoformat()
            
            self.adaptation_stats['model_updates'] += 1
            
        except Exception as e:
            print(f"❌ 온라인 학습 업데이트 오류: {e}")
    
    def _update_cluster_analysis(self):
        """클러스터 분석 업데이트"""
        if len(self.data_buffer) < 50:  # 최소 데이터 필요
            return
        
        try:
            # 특징 벡터 추출
            feature_vectors = []
            for data_point in self.data_buffer:
                feature_vector = np.array(list(data_point['features'].values()))
                feature_vectors.append(feature_vector)
            
            X = np.array(feature_vectors)
            
            # K-means 클러스터링
            n_clusters = min(5, len(X) // 10)  # 데이터 크기에 따라 클러스터 수 조정
            if n_clusters < 2:
                return
            
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(X)
            
            # 클러스터별 이상 비율 계산
            cluster_anomaly_ratios = {}
            for cluster_id in range(n_clusters):
                cluster_data = [self.data_buffer[i] for i in range(len(cluster_labels)) if cluster_labels[i] == cluster_id]
                if cluster_data:
                    anomaly_count = sum(1 for d in cluster_data if d['is_anomaly'])
                    cluster_anomaly_ratios[cluster_id] = anomaly_count / len(cluster_data)
            
            # 이상 클러스터 식별 (이상 비율이 0.3 이상)
            anomaly_clusters = {
                cluster_id for cluster_id, ratio in cluster_anomaly_ratios.items() 
                if ratio >= 0.3
            }
            normal_clusters = {
                cluster_id for cluster_id, ratio in cluster_anomaly_ratios.items() 
                if ratio < 0.3
            }
            
            # 업데이트
            self.cluster_analyzer.update({
                'kmeans': kmeans,
                'cluster_centers': kmeans.cluster_centers_,
                'cluster_labels': cluster_labels,
                'anomaly_clusters': anomaly_clusters,
                'normal_clusters': normal_clusters,
                'cluster_stats': cluster_anomaly_ratios,
                'last_analysis': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ 클러스터 분석 업데이트 오류: {e}")
    
    def _update_performance_metrics(self, result: Dict, ground_truth: Optional[bool], processing_time: float):
        """성능 통계 업데이트"""
        self.performance_metrics['total_detections'] += 1
        
        if result['is_anomaly']:
            self.performance_metrics['anomaly_count'] += 1
        
        # 정확도 계산
        if ground_truth is not None:
            predicted = result['is_anomaly']
            if predicted and not ground_truth:
                self.performance_metrics['false_positives'] += 1
            elif not predicted and ground_truth:
                self.performance_metrics['false_negatives'] += 1
            
            # 정확도 업데이트
            total = self.performance_metrics['total_detections']
            correct = total - (self.performance_metrics['false_positives'] + 
                             self.performance_metrics['false_negatives'])
            self.performance_metrics['accuracy'] = correct / total if total > 0 else 0.0
        
        # 평균 처리 시간 업데이트
        total = self.performance_metrics['total_detections']
        current_avg = self.performance_metrics['average_processing_time']
        self.performance_metrics['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        self.performance_metrics['last_update'] = datetime.now().isoformat()
    
    def get_adaptive_stats(self) -> Dict:
        """적응형 통계 반환"""
        stats = self.performance_metrics.copy()
        
        if stats['total_detections'] > 0:
            stats['anomaly_rate'] = stats['anomaly_count'] / stats['total_detections']
        else:
            stats['anomaly_rate'] = 0.0
        
        # 적응형 통계 추가
        stats.update({
            'phase': 'Phase 2',
            'adaptation_stats': self.adaptation_stats,
            'data_buffer_size': len(self.data_buffer),
            'adaptation_params': self.adaptation_params,
            'adaptive_thresholds_count': len(self.adaptive_thresholds),
            'online_learner_ready': self.online_learner['isolation_forest'] is not None,
            'cluster_analyzer_ready': self.cluster_analyzer['kmeans'] is not None
        })
        
        return stats
    
    def save_adaptive_system(self, filepath: str = None):
        """적응형 시스템 저장"""
        if filepath is None:
            filepath = os.path.join(self.model_save_path, "phase2_adaptive_system.pkl")
        
        # Phase 1 시스템 저장
        phase1_path = filepath.replace('phase2_adaptive_system.pkl', 'phase1_detector.pkl')
        if self.phase1_detector:
            self.phase1_detector.save_model(phase1_path)
        
        # 적응형 시스템 데이터 저장
        adaptive_data = {
            'adaptive_thresholds': self.adaptive_thresholds,
            'online_learner': {
                'scaler': self.online_learner['scaler'],
                'pca': self.online_learner['pca'],
                'isolation_forest': self.online_learner['isolation_forest'],
                'normal_stats': self.online_learner['normal_stats'],
                'anomaly_stats': self.online_learner['anomaly_stats'],
                'sample_count': self.online_learner['sample_count'],
                'last_update': self.online_learner['last_update']
            },
            'cluster_analyzer': self.cluster_analyzer,
            'adaptation_stats': self.adaptation_stats,
            'adaptation_params': self.adaptation_params,
            'performance_metrics': self.performance_metrics,
            'window_size': self.window_size,
            'sample_rate': self.sample_rate,
            'adaptation_interval': self.adaptation_interval,
            'phase': 'Phase 2'
        }
        
        joblib.dump(adaptive_data, filepath)
        
        # 메타데이터 저장
        metadata = {
            'model_type': 'phase2_adaptive_system',
            'phase': 'Phase 2',
            'created_at': datetime.now().isoformat(),
            'adaptation_stats': self.adaptation_stats,
            'performance_metrics': self.performance_metrics,
            'window_size': self.window_size,
            'sample_rate': self.sample_rate,
            'adaptation_interval': self.adaptation_interval
        }
        
        metadata_file = filepath.replace('.pkl', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Phase 2 적응형 시스템 저장 완료: {filepath}")
        print(f"📊 메타데이터 저장 완료: {metadata_file}")

# 사용 예제
if __name__ == "__main__":
    # Phase 2 적응형 시스템 초기화
    adaptive_system = Phase2AdaptiveSystem()
    
    print("🔄 Phase 2: 적응형 시스템 테스트")
    print("=" * 60)
    print("환경 변화에 자동으로 적응하는 AI 시스템")
    print("다중 검증 및 실시간 학습")
    print("=" * 60)
    
    print("Phase 2 시스템 준비 완료!")
    print("Phase 1 시스템과 연동 후 적응형 이상 탐지 가능")
    print("예상 정확도: 85-90%")
    print("예상 처리 속도: 50-100ms")
