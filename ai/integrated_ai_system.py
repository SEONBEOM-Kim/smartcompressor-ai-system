#!/usr/bin/env python3
"""
통합 AI 시스템
24시간 모니터링 데이터에 최적화된 종합 AI 진단 시스템
"""

import numpy as np
import librosa
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
import os
from collections import deque
import threading

# 내부 모듈 import
from .anomaly_detection_ai import RefrigeratorAnomalyDetector
from .adaptive_threshold_system import AdaptiveThresholdSystem
from .online_learning_system import OnlineLearningSystem

class IntegratedAISystem:
    def __init__(self, 
                 model_save_path: str = "data/models/",
                 monitoring_window_seconds: int = 5,
                 confidence_threshold: float = 0.7):
        """
        통합 AI 시스템 초기화
        
        Args:
            model_save_path: 모델 저장 경로
            monitoring_window_seconds: 모니터링 윈도우 크기 (초)
            confidence_threshold: 최종 판정 신뢰도 임계값
        """
        self.model_save_path = model_save_path
        os.makedirs(model_save_path, exist_ok=True)
        
        self.monitoring_window_seconds = monitoring_window_seconds
        self.confidence_threshold = confidence_threshold
        
        # 하위 시스템들
        self.anomaly_detector = RefrigeratorAnomalyDetector(model_save_path)
        self.threshold_system = AdaptiveThresholdSystem(
            update_interval_hours=6,
            history_days=7,
            sensitivity=0.1
        )
        self.online_learner = OnlineLearningSystem(
            model_save_path=model_save_path,
            learning_rate=0.01,
            memory_size=10000,
            update_frequency=100
        )
        
        # 통합 진단 상태
        self.is_initialized = False
        self.diagnosis_history = deque(maxlen=1000)  # 최근 1000개 진단 결과
        
        # 실시간 모니터링 상태
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_lock = threading.Lock()
        
        # 성능 지표
        self.performance_metrics = {
            'total_diagnoses': 0,
            'anomaly_detections': 0,
            'false_positives': 0,
            'false_negatives': 0,
            'average_processing_time': 0.0,
            'last_accuracy_update': None
        }
        
        print("🧠 통합 AI 시스템 초기화 완료")
        print(f"📊 모니터링 윈도우: {monitoring_window_seconds}초")
        print(f"🎯 신뢰도 임계값: {confidence_threshold}")
    
    def initialize_with_normal_data(self, normal_audio_files: List[str]) -> Dict:
        """
        정상 데이터로 시스템 초기화
        
        Args:
            normal_audio_files: 정상 상태 오디오 파일 경로 리스트
            
        Returns:
            초기화 결과
        """
        print("🚀 정상 데이터로 시스템 초기화 시작")
        
        try:
            # 1. 이상 탐지 모델 훈련
            print("1️⃣ 이상 탐지 모델 훈련 중...")
            anomaly_result = self.anomaly_detector.train_on_normal_data(normal_audio_files)
            
            # 2. 정상 데이터로 임계값 시스템 초기화
            print("2️⃣ 적응형 임계값 시스템 초기화 중...")
            self._initialize_threshold_system(normal_audio_files)
            
            # 3. 온라인 학습 시스템 초기화
            print("3️⃣ 온라인 학습 시스템 초기화 중...")
            self._initialize_online_learning(normal_audio_files)
            
            self.is_initialized = True
            
            result = {
                'initialization_success': True,
                'anomaly_detector': anomaly_result,
                'threshold_system_ready': True,
                'online_learning_ready': True,
                'total_normal_samples': len(normal_audio_files),
                'initialization_time': datetime.now().isoformat()
            }
            
            print("✅ 시스템 초기화 완료!")
            return result
            
        except Exception as e:
            print(f"❌ 시스템 초기화 오류: {e}")
            return {
                'initialization_success': False,
                'error': str(e),
                'initialization_time': datetime.now().isoformat()
            }
    
    def _initialize_threshold_system(self, normal_audio_files: List[str]):
        """임계값 시스템 초기화"""
        for file_path in normal_audio_files[:100]:  # 최대 100개 파일만 사용
            try:
                audio_data, sr = librosa.load(file_path, sr=None)
                
                # 청크 단위로 처리
                chunk_samples = int(self.monitoring_window_seconds * sr)
                for start in range(0, len(audio_data), chunk_samples):
                    chunk = audio_data[start:start + chunk_samples]
                    if len(chunk) >= chunk_samples:
                        features = self.anomaly_detector.extract_comprehensive_features(chunk, sr)
                        self.threshold_system.add_data_point(features, is_anomaly=False)
                        
            except Exception as e:
                print(f"❌ 임계값 초기화 오류 {file_path}: {e}")
                continue
    
    def _initialize_online_learning(self, normal_audio_files: List[str]):
        """온라인 학습 시스템 초기화"""
        for file_path in normal_audio_files[:50]:  # 최대 50개 파일만 사용
            try:
                audio_data, sr = librosa.load(file_path, sr=None)
                
                # 청크 단위로 처리
                chunk_samples = int(self.monitoring_window_seconds * sr)
                for start in range(0, len(audio_data), chunk_samples):
                    chunk = audio_data[start:start + chunk_samples]
                    if len(chunk) >= chunk_samples:
                        features = self.anomaly_detector.extract_comprehensive_features(chunk, sr)
                        self.online_learner.add_sample(features, is_anomaly=False)
                        
            except Exception as e:
                print(f"❌ 온라인 학습 초기화 오류 {file_path}: {e}")
                continue
    
    def diagnose_audio(self, audio_data: np.ndarray, sr: int, 
                      ground_truth: Optional[bool] = None) -> Dict:
        """
        통합 오디오 진단
        
        Args:
            audio_data: 오디오 데이터
            sr: 샘플링 레이트
            ground_truth: 실제 이상 여부 (성능 평가용, 선택사항)
            
        Returns:
            통합 진단 결과
        """
        if not self.is_initialized:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': '시스템이 초기화되지 않았습니다.',
                'diagnosis_type': 'system_not_ready',
                'processing_time_ms': 0
            }
        
        start_time = time.time()
        
        try:
            # 1. 특징 추출
            features = self.anomaly_detector.extract_comprehensive_features(audio_data, sr)
            
            # 2. 이상 탐지 모델 예측
            anomaly_result = self.anomaly_detector.detect_anomaly(audio_data, sr)
            
            # 3. 적응형 임계값 검사
            threshold_anomalies = self.threshold_system.check_anomaly(features)
            threshold_score = self.threshold_system.get_anomaly_score(features)
            
            # 4. 온라인 학습 모델 예측
            online_result = self.online_learner.predict(features)
            
            # 5. 통합 판정
            final_result = self._integrate_predictions(
                anomaly_result, threshold_anomalies, threshold_score, online_result
            )
            
            # 6. 온라인 학습 업데이트
            if ground_truth is not None:
                self.online_learner.add_sample(features, ground_truth)
                self.threshold_system.add_data_point(features, ground_truth)
            
            # 7. 성능 지표 업데이트
            processing_time = (time.time() - start_time) * 1000
            self._update_performance_metrics(final_result, ground_truth, processing_time)
            
            # 8. 진단 히스토리 업데이트
            diagnosis_record = {
                'timestamp': datetime.now(),
                'result': final_result,
                'features': features,
                'ground_truth': ground_truth,
                'processing_time_ms': processing_time
            }
            self.diagnosis_history.append(diagnosis_record)
            
            return final_result
            
        except Exception as e:
            print(f"❌ 통합 진단 오류: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': f'진단 중 오류 발생: {str(e)}',
                'diagnosis_type': 'error',
                'processing_time_ms': (time.time() - start_time) * 1000
            }
    
    def _integrate_predictions(self, anomaly_result: Dict, 
                              threshold_anomalies: Dict, 
                              threshold_score: float,
                              online_result: Dict) -> Dict:
        """여러 모델의 예측 결과 통합"""
        
        # 각 모델의 이상 여부
        anomaly_detected = anomaly_result['is_anomaly']
        threshold_detected = len([a for a in threshold_anomalies.values() if a]) > 2
        online_detected = online_result['is_anomaly']
        
        # 가중 투표 (각 모델의 신뢰도 기반)
        weights = {
            'anomaly_detector': 0.4,  # 가장 신뢰할 만한 모델
            'threshold_system': 0.3,
            'online_learner': 0.3
        }
        
        # 가중 평균 신뢰도
        weighted_confidence = (
            weights['anomaly_detector'] * anomaly_result['confidence'] +
            weights['threshold_system'] * threshold_score +
            weights['online_learner'] * online_result['confidence']
        )
        
        # 최종 이상 여부 (다수결 + 신뢰도)
        votes = [anomaly_detected, threshold_detected, online_detected]
        majority_vote = sum(votes) >= 2
        
        # 신뢰도가 임계값 이상이면 최종 판정
        final_anomaly = majority_vote and weighted_confidence >= self.confidence_threshold
        
        # 이상 유형 분류
        anomaly_type = self._classify_anomaly_type(
            anomaly_result, threshold_anomalies, online_result
        )
        
        # 메시지 생성
        message = self._generate_diagnosis_message(
            final_anomaly, weighted_confidence, anomaly_type, votes
        )
        
        return {
            'is_anomaly': final_anomaly,
            'confidence': weighted_confidence,
            'message': message,
            'diagnosis_type': anomaly_type,
            'individual_predictions': {
                'anomaly_detector': {
                    'prediction': anomaly_detected,
                    'confidence': anomaly_result['confidence'],
                    'anomaly_type': anomaly_result.get('anomaly_type', 'unknown')
                },
                'threshold_system': {
                    'prediction': threshold_detected,
                    'confidence': threshold_score,
                    'anomaly_features': [k for k, v in threshold_anomalies.items() if v]
                },
                'online_learner': {
                    'prediction': online_detected,
                    'confidence': online_result['confidence'],
                    'anomaly_score': online_result.get('anomaly_score', 0.0)
                }
            },
            'voting_result': {
                'votes': votes,
                'majority_vote': majority_vote,
                'weights': weights
            }
        }
    
    def _classify_anomaly_type(self, anomaly_result: Dict, 
                              threshold_anomalies: Dict, 
                              online_result: Dict) -> str:
        """이상 유형 분류"""
        
        # 이상 탐지 모델의 유형이 가장 신뢰할 만함
        if anomaly_result.get('anomaly_type') != 'normal':
            return anomaly_result['anomaly_type']
        
        # 임계값 시스템 기반 분류
        anomaly_features = [k for k, v in threshold_anomalies.items() if v]
        if 'rms_energy' in anomaly_features and 'spectral_centroid' in anomaly_features:
            return 'compressor_abnormal'
        elif 'zero_crossing_rate' in anomaly_features:
            return 'bearing_wear'
        elif 'low_freq_ratio' in anomaly_features:
            return 'refrigerant_leak'
        
        # 온라인 학습 기반 분류
        if online_result.get('statistical_anomaly', False):
            return 'statistical_anomaly'
        
        return 'general_anomaly'
    
    def _generate_diagnosis_message(self, is_anomaly: bool, confidence: float, 
                                   anomaly_type: str, votes: List[bool]) -> str:
        """진단 메시지 생성"""
        if not is_anomaly:
            return "정상 작동 중"
        
        vote_count = sum(votes)
        confidence_level = "높음" if confidence > 0.8 else "보통" if confidence > 0.6 else "낮음"
        
        messages = {
            'bearing_wear': f"베어링 마모 의심 ({vote_count}/3 모델 일치, 신뢰도: {confidence_level})",
            'compressor_abnormal': f"압축기 이상 의심 ({vote_count}/3 모델 일치, 신뢰도: {confidence_level})",
            'refrigerant_leak': f"냉매 누출 의심 ({vote_count}/3 모델 일치, 신뢰도: {confidence_level})",
            'statistical_anomaly': f"통계적 이상 감지 ({vote_count}/3 모델 일치, 신뢰도: {confidence_level})",
            'general_anomaly': f"이상 소음 감지 ({vote_count}/3 모델 일치, 신뢰도: {confidence_level})"
        }
        
        return messages.get(anomaly_type, f"이상 감지 ({vote_count}/3 모델 일치, 신뢰도: {confidence_level})")
    
    def _update_performance_metrics(self, result: Dict, ground_truth: Optional[bool], 
                                   processing_time: float):
        """성능 지표 업데이트"""
        self.performance_metrics['total_diagnoses'] += 1
        
        if result['is_anomaly']:
            self.performance_metrics['anomaly_detections'] += 1
        
        # 정확도 계산 (ground_truth가 있는 경우)
        if ground_truth is not None:
            predicted = result['is_anomaly']
            if predicted and not ground_truth:
                self.performance_metrics['false_positives'] += 1
            elif not predicted and ground_truth:
                self.performance_metrics['false_negatives'] += 1
        
        # 평균 처리 시간 업데이트
        total = self.performance_metrics['total_diagnoses']
        current_avg = self.performance_metrics['average_processing_time']
        self.performance_metrics['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        # 정확도 업데이트 (100개마다)
        if total % 100 == 0:
            self.performance_metrics['last_accuracy_update'] = datetime.now().isoformat()
    
    def get_system_status(self) -> Dict:
        """시스템 상태 정보"""
        return {
            'initialized': self.is_initialized,
            'monitoring_active': self.monitoring_active,
            'performance_metrics': self.performance_metrics.copy(),
            'anomaly_detector_status': {
                'trained': self.anomaly_detector.is_trained,
                'monitoring_summary': self.anomaly_detector.get_monitoring_summary()
            },
            'threshold_system_status': self.threshold_system.get_statistics_summary(),
            'online_learner_status': self.online_learner.get_learning_statistics(),
            'diagnosis_history_size': len(self.diagnosis_history)
        }
    
    def start_monitoring(self, audio_callback):
        """실시간 모니터링 시작"""
        if not self.is_initialized:
            print("❌ 시스템이 초기화되지 않았습니다.")
            return False
        
        if self.monitoring_active:
            print("⚠️ 모니터링이 이미 실행 중입니다.")
            return False
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(audio_callback,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        print("🎯 실시간 모니터링 시작")
        return True
    
    def stop_monitoring(self):
        """실시간 모니터링 중지"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        print("⏹️ 실시간 모니터링 중지")
    
    def _monitoring_loop(self, audio_callback):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 오디오 데이터 콜백 호출
                audio_data, sr = audio_callback()
                
                if audio_data is not None:
                    # 진단 수행
                    result = self.diagnose_audio(audio_data, sr)
                    
                    # 이상 감지 시 알림
                    if result['is_anomaly']:
                        print(f"🚨 이상 감지: {result['message']}")
                
                # 5초 대기
                time.sleep(self.monitoring_window_seconds)
                
            except Exception as e:
                print(f"❌ 모니터링 루프 오류: {e}")
                time.sleep(1)
    
    def save_system(self, filepath: str = None):
        """시스템 저장"""
        if filepath is None:
            filepath = os.path.join(self.model_save_path, "integrated_ai_system.json")
        
        system_data = {
            'monitoring_window_seconds': self.monitoring_window_seconds,
            'confidence_threshold': self.confidence_threshold,
            'is_initialized': self.is_initialized,
            'performance_metrics': self.performance_metrics,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(system_data, f, indent=2, ensure_ascii=False)
        
        # 하위 시스템들 저장
        self.anomaly_detector.save_model()
        self.threshold_system.save_thresholds(
            os.path.join(self.model_save_path, "adaptive_thresholds.json")
        )
        self.online_learner._save_model()
        
        print(f"💾 통합 AI 시스템 저장 완료: {filepath}")

# 사용 예제
if __name__ == "__main__":
    # 통합 AI 시스템 초기화
    ai_system = IntegratedAISystem()
    
    print("🧠 통합 AI 시스템 테스트")
    print("=" * 40)
    
    # 정상 데이터로 초기화 (실제로는 파일 경로 리스트 사용)
    # normal_files = ["normal1.wav", "normal2.wav", ...]
    # init_result = ai_system.initialize_with_normal_data(normal_files)
    
    print("시스템 초기화 후 24시간 모니터링 준비 완료")
    print("실제 사용 시 정상 데이터로 초기화 후 모니터링 시작")
