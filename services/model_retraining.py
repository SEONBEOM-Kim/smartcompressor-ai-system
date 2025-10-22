#!/usr/bin/env python3
"""
모델 재훈련 서비스
현장 데이터를 활용한 AI 모델 정확도 개선
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import librosa
from services.field_data_collection import field_data_collector

logger = logging.getLogger(__name__)

class ModelRetrainingService:
    """모델 재훈련 서비스"""
    
    def __init__(self, models_dir: str = 'data/models'):
        self.models_dir = models_dir
        self.field_collector = field_data_collector
        self.retraining_history = []
        
        # 모델 저장소
        self.models = {}
        self.scalers = {}
        
        # 재훈련 설정
        self.min_samples_for_retraining = 50
        self.retraining_threshold_accuracy = 0.8
        self.retraining_interval_days = 7
        
    def should_retrain(self) -> Dict:
        """재훈련 필요성 판단"""
        try:
            # 최근 7일간의 검증된 데이터 조회
            recent_data = self.field_collector.get_verified_data(days=7)
            
            if len(recent_data) < self.min_samples_for_retraining:
                return {
                    'should_retrain': False,
                    'reason': f'샘플 수 부족: {len(recent_data)}/{self.min_samples_for_retraining}',
                    'samples_needed': self.min_samples_for_retraining - len(recent_data)
                }
            
            # 현재 정확도 확인
            accuracy_stats = self.field_collector.get_ai_accuracy_stats(days=7)
            current_accuracy = accuracy_stats['accuracy']
            
            if current_accuracy < self.retraining_threshold_accuracy:
                return {
                    'should_retrain': True,
                    'reason': f'정확도 낮음: {current_accuracy:.3f} < {self.retraining_threshold_accuracy}',
                    'current_accuracy': current_accuracy,
                    'target_accuracy': self.retraining_threshold_accuracy
                }
            
            # 마지막 재훈련 시간 확인
            last_retraining = self._get_last_retraining_time()
            if last_retraining:
                days_since_retraining = (datetime.now() - last_retraining).days
                if days_since_retraining >= self.retraining_interval_days:
                    return {
                        'should_retrain': True,
                        'reason': f'정기 재훈련 필요: {days_since_retraining}일 경과',
                        'days_since_retraining': days_since_retraining
                    }
            
            return {
                'should_retrain': False,
                'reason': '재훈련 불필요',
                'current_accuracy': current_accuracy
            }
            
        except Exception as e:
            logger.error(f"재훈련 필요성 판단 실패: {e}")
            return {
                'should_retrain': False,
                'reason': f'오류: {str(e)}'
            }
    
    def prepare_training_data(self, days: int = 30) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """훈련 데이터 준비"""
        try:
            # 검증된 데이터 조회
            verified_data = self.field_collector.get_verified_data(days=days)
            
            if len(verified_data) < 10:
                raise ValueError(f"훈련 데이터 부족: {len(verified_data)}개")
            
            X = []
            y = []
            feature_names = []
            
            for data in verified_data:
                try:
                    # 오디오 파일에서 특징 추출
                    audio_path = data['audio_file_path']
                    if not os.path.exists(audio_path):
                        logger.warning(f"오디오 파일 없음: {audio_path}")
                        continue
                    
                    features = self._extract_audio_features(audio_path)
                    if features is not None:
                        X.append(features)
                        y.append(data['ground_truth_label'])
                        
                        # 첫 번째 샘플에서 특징 이름 추출
                        if not feature_names:
                            feature_names = list(features.keys())
                            
                except Exception as e:
                    logger.warning(f"특징 추출 실패: {e}")
                    continue
            
            if len(X) < 10:
                raise ValueError(f"유효한 훈련 데이터 부족: {len(X)}개")
            
            # 특징을 배열로 변환
            X_array = np.array([[features[f] for f in feature_names] for features in X])
            y_array = np.array(y)
            
            logger.info(f"훈련 데이터 준비 완료: {len(X_array)}개 샘플, {len(feature_names)}개 특징")
            
            return X_array, y_array, feature_names
            
        except Exception as e:
            logger.error(f"훈련 데이터 준비 실패: {e}")
            raise
    
    def _extract_audio_features(self, audio_path: str) -> Optional[Dict]:
        """오디오 특징 추출"""
        try:
            # 오디오 로드
            y, sr = librosa.load(audio_path, sr=16000)
            
            features = {}
            
            # 시간 도메인 특징
            features['rms_energy'] = np.sqrt(np.mean(y**2))
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(y))
            features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
            features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr))
            
            # MFCC 특징
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}'] = np.mean(mfccs[i])
                features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            
            # 스펙트럼 특징
            stft = librosa.stft(y)
            magnitude = np.abs(stft)
            freqs = librosa.fft_frequencies(sr=sr)
            
            # 주파수 대역별 에너지
            low_freq_energy = np.sum(magnitude[freqs < 1000])
            mid_freq_energy = np.sum(magnitude[(freqs >= 1000) & (freqs < 4000)])
            high_freq_energy = np.sum(magnitude[freqs >= 4000])
            total_energy = np.sum(magnitude)
            
            features['low_freq_ratio'] = low_freq_energy / total_energy if total_energy > 0 else 0
            features['mid_freq_ratio'] = mid_freq_energy / total_energy if total_energy > 0 else 0
            features['high_freq_ratio'] = high_freq_energy / total_energy if total_energy > 0 else 0
            
            # 압축기 특화 특징
            features['compressor_freq_energy'] = np.sum(magnitude[(freqs >= 500) & (freqs < 2000)]) / total_energy if total_energy > 0 else 0
            features['leak_freq_energy'] = np.sum(magnitude[(freqs >= 2000) & (freqs < 8000)]) / total_energy if total_energy > 0 else 0
            
            return features
            
        except Exception as e:
            logger.error(f"오디오 특징 추출 실패: {e}")
            return None
    
    def retrain_models(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict:
        """모델 재훈련"""
        try:
            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # 스케일러 훈련
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # 모델들 훈련
            models = {
                'random_forest': RandomForestClassifier(
                    n_estimators=100, max_depth=20, min_samples_split=5,
                    min_samples_leaf=2, random_state=42
                ),
                'svm': SVC(
                    kernel='rbf', C=1.0, gamma='scale',
                    probability=True, random_state=42
                ),
                'mlp': MLPClassifier(
                    hidden_layer_sizes=(100, 50), activation='relu',
                    solver='adam', alpha=0.001, learning_rate='adaptive',
                    max_iter=1000, random_state=42
                )
            }
            
            results = {}
            
            for model_name, model in models.items():
                # 모델 훈련
                model.fit(X_train_scaled, y_train)
                
                # 예측 및 평가
                y_pred = model.predict(X_test_scaled)
                accuracy = accuracy_score(y_test, y_pred)
                
                # 분류 리포트
                report = classification_report(y_test, y_pred, output_dict=True)
                
                results[model_name] = {
                    'accuracy': accuracy,
                    'classification_report': report,
                    'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
                }
                
                logger.info(f"{model_name} 정확도: {accuracy:.3f}")
            
            # 최고 성능 모델 선택
            best_model_name = max(results.keys(), key=lambda k: results[k]['accuracy'])
            best_model = models[best_model_name]
            best_accuracy = results[best_model_name]['accuracy']
            
            # 모델 저장
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 모델 저장
            model_path = os.path.join(self.models_dir, f'{best_model_name}_{timestamp}.pkl')
            os.makedirs(self.models_dir, exist_ok=True)
            joblib.dump(best_model, model_path)
            
            # 스케일러 저장
            scaler_path = os.path.join(self.models_dir, f'{best_model_name}_scaler_{timestamp}.pkl')
            joblib.dump(scaler, scaler_path)
            
            # 메타데이터 저장
            metadata = {
                'model_name': best_model_name,
                'timestamp': timestamp,
                'accuracy': best_accuracy,
                'feature_names': feature_names,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'retraining_reason': 'field_data_improvement'
            }
            
            metadata_path = os.path.join(self.models_dir, f'{best_model_name}_metadata_{timestamp}.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # 재훈련 이력 저장
            self.retraining_history.append({
                'timestamp': datetime.now().isoformat(),
                'model_name': best_model_name,
                'accuracy': best_accuracy,
                'training_samples': len(X_train),
                'feature_names': feature_names
            })
            
            logger.info(f"모델 재훈련 완료: {best_model_name} (정확도: {best_accuracy:.3f})")
            
            return {
                'success': True,
                'best_model': best_model_name,
                'accuracy': best_accuracy,
                'results': results,
                'model_path': model_path,
                'scaler_path': scaler_path,
                'metadata_path': metadata_path
            }
            
        except Exception as e:
            logger.error(f"모델 재훈련 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_last_retraining_time(self) -> Optional[datetime]:
        """마지막 재훈련 시간 조회"""
        try:
            if not self.retraining_history:
                return None
            
            last_retraining = max(self.retraining_history, key=lambda x: x['timestamp'])
            return datetime.fromisoformat(last_retraining['timestamp'])
            
        except Exception as e:
            logger.error(f"마지막 재훈련 시간 조회 실패: {e}")
            return None
    
    def get_retraining_status(self) -> Dict:
        """재훈련 상태 조회"""
        try:
            should_retrain_info = self.should_retrain()
            last_retraining = self._get_last_retraining_time()
            
            return {
                'should_retrain': should_retrain_info['should_retrain'],
                'reason': should_retrain_info.get('reason', ''),
                'last_retraining': last_retraining.isoformat() if last_retraining else None,
                'retraining_history': self.retraining_history[-5:],  # 최근 5개
                'min_samples_required': self.min_samples_for_retraining,
                'accuracy_threshold': self.retraining_threshold_accuracy
            }
            
        except Exception as e:
            logger.error(f"재훈련 상태 조회 실패: {e}")
            return {
                'should_retrain': False,
                'reason': f'오류: {str(e)}',
                'last_retraining': None,
                'retraining_history': [],
                'min_samples_required': self.min_samples_for_retraining,
                'accuracy_threshold': self.retraining_threshold_accuracy
            }
    
    def auto_retrain_if_needed(self) -> Dict:
        """필요시 자동 재훈련"""
        try:
            should_retrain_info = self.should_retrain()
            
            if not should_retrain_info['should_retrain']:
                return {
                    'success': True,
                    'message': '재훈련 불필요',
                    'reason': should_retrain_info['reason']
                }
            
            # 훈련 데이터 준비
            X, y, feature_names = self.prepare_training_data()
            
            # 모델 재훈련
            result = self.retrain_models(X, y, feature_names)
            
            if result['success']:
                return {
                    'success': True,
                    'message': '자동 재훈련 완료',
                    'model': result['best_model'],
                    'accuracy': result['accuracy']
                }
            else:
                return {
                    'success': False,
                    'message': '자동 재훈련 실패',
                    'error': result['error']
                }
                
        except Exception as e:
            logger.error(f"자동 재훈련 실패: {e}")
            return {
                'success': False,
                'message': f'자동 재훈련 오류: {str(e)}'
            }

# 전역 인스턴스
model_retraining_service = ModelRetrainingService()
