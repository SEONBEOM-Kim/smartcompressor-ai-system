#!/usr/bin/env python3
"""
GPU 없이도 안전하게 동작하는 시스템
GPU 도입 시점에 쉽게 전환할 수 있는 구조
"""

import numpy as np
import librosa
import time
import warnings
from typing import Dict, List, Tuple, Optional, Union
import joblib
import os
from datetime import datetime

warnings.filterwarnings('ignore')

class SafeGPUReadySystem:
    """GPU 없이도 안전하게 동작하는 시스템"""
    
    def __init__(self, model_save_path: str = "data/models/safe_gpu_ready/"):
        self.model_save_path = model_save_path
        os.makedirs(model_save_path, exist_ok=True)
        
        # GPU 사용 가능 여부 확인
        self.gpu_available = self._check_gpu_availability()
        self.device = 'cuda' if self.gpu_available else 'cpu'
        
        # 모델들
        self.models = {}
        self.performance_metrics = {}
        
        print(f"🛡️ 안전한 GPU 준비 시스템 초기화 완료")
        print(f"   GPU 사용 가능: {self.gpu_available}")
        print(f"   현재 디바이스: {self.device}")
    
    def _check_gpu_availability(self) -> bool:
        """GPU 사용 가능 여부 확인"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    # ===== 1. 안전한 모델 생성 =====
    
    def create_safe_models(self, input_size: int) -> Dict:
        """안전한 모델들 생성 (GPU/CPU 자동 선택)"""
        models = {}
        
        if self.gpu_available:
            print("✅ GPU 사용 가능 - 딥러닝 모델 생성")
            models.update(self._create_gpu_models(input_size))
        else:
            print("⚠️ GPU 사용 불가 - CPU 최적화 모델 생성")
            models.update(self._create_cpu_models(input_size))
        
        return models
    
    def _create_gpu_models(self, input_size: int) -> Dict:
        """GPU 모델들 생성"""
        try:
            import torch
            import torch.nn as nn
            
            # 간단한 CNN
            class AudioCNN(nn.Module):
                def __init__(self, input_size, hidden_size=64, output_size=2):
                    super().__init__()
                    self.fc1 = nn.Linear(input_size, hidden_size)
                    self.fc2 = nn.Linear(hidden_size, hidden_size)
                    self.fc3 = nn.Linear(hidden_size, output_size)
                    self.relu = nn.ReLU()
                    self.dropout = nn.Dropout(0.2)
                
                def forward(self, x):
                    x = self.relu(self.fc1(x))
                    x = self.dropout(x)
                    x = self.relu(self.fc2(x))
                    x = self.dropout(x)
                    x = self.fc3(x)
                    return x
            
            # RNN 모델
            class AudioRNN(nn.Module):
                def __init__(self, input_size, hidden_size=64, output_size=2):
                    super().__init__()
                    self.rnn = nn.LSTM(input_size, hidden_size, batch_first=True)
                    self.fc = nn.Linear(hidden_size, output_size)
                
                def forward(self, x):
                    rnn_out, _ = self.rnn(x)
                    output = self.fc(rnn_out[:, -1, :])
                    return output
            
            models = {
                'cnn': AudioCNN(input_size),
                'rnn': AudioRNN(input_size),
                'device': self.device
            }
            
            # GPU로 이동
            for name, model in models.items():
                if name != 'device':
                    models[name] = model.to(self.device)
            
            return models
            
        except Exception as e:
            print(f"⚠️ GPU 모델 생성 중 오류: {e}")
            return self._create_cpu_models(input_size)
    
    def _create_cpu_models(self, input_size: int) -> Dict:
        """CPU 모델들 생성"""
        try:
            from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
            from sklearn.linear_model import LogisticRegression
            from sklearn.naive_bayes import GaussianNB
            from sklearn.svm import SVC
            
            models = {
                'random_forest': RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                ),
                'gradient_boosting': GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    random_state=42
                ),
                'logistic_regression': LogisticRegression(
                    max_iter=1000,
                    random_state=42
                ),
                'naive_bayes': GaussianNB(),
                'svm': SVC(
                    kernel='rbf',
                    probability=True,
                    random_state=42
                ),
                'device': 'cpu'
            }
            
            return models
            
        except Exception as e:
            print(f"⚠️ CPU 모델 생성 중 오류: {e}")
            return {'device': 'cpu'}
    
    # ===== 2. 안전한 특징 추출 =====
    
    def extract_safe_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """안전한 특징 추출 (GPU/CPU 자동 선택)"""
        try:
            if self.gpu_available:
                return self._extract_gpu_features(audio_data, sr)
            else:
                return self._extract_cpu_features(audio_data, sr)
        except Exception as e:
            print(f"⚠️ 특징 추출 중 오류: {e}")
            return self._extract_basic_features(audio_data, sr)
    
    def _extract_gpu_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """GPU 특징 추출 (향후 구현)"""
        # GPU 특징 추출은 향후 구현
        # 현재는 CPU 특징 추출 사용
        return self._extract_cpu_features(audio_data, sr)
    
    def _extract_cpu_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """CPU 특징 추출"""
        try:
            features = {}
            
            # 기본 특징들
            features['rms'] = np.sqrt(np.mean(audio_data ** 2))
            features['zcr'] = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))
            features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr))
            features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sr))
            
            # MFCC
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
            
            # Chroma
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
            
            # Spectral Contrast
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
            features['contrast_mean'] = np.mean(contrast, axis=1).tolist()
            
            return features
            
        except Exception as e:
            print(f"⚠️ CPU 특징 추출 중 오류: {e}")
            return self._extract_basic_features(audio_data, sr)
    
    def _extract_basic_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """기본 특징 추출 (오류 시 사용)"""
        try:
            return {
                'rms': np.sqrt(np.mean(audio_data ** 2)),
                'zcr': np.mean(librosa.feature.zero_crossing_rate(audio_data)),
                'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))
            }
        except:
            return {'rms': 0.0, 'zcr': 0.0, 'spectral_centroid': 0.0}
    
    # ===== 3. 안전한 모델 훈련 =====
    
    def train_safe_models(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """안전한 모델 훈련"""
        try:
            if self.gpu_available:
                return self._train_gpu_models(X, y)
            else:
                return self._train_cpu_models(X, y)
        except Exception as e:
            print(f"⚠️ 모델 훈련 중 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def _train_gpu_models(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """GPU 모델 훈련 (향후 구현)"""
        # GPU 모델 훈련은 향후 구현
        # 현재는 CPU 모델 훈련 사용
        return self._train_cpu_models(X, y)
    
    def _train_cpu_models(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """CPU 모델 훈련"""
        try:
            models = self.create_safe_models(X.shape[1])
            training_results = {}
            
            for name, model in models.items():
                if name != 'device':
                    try:
                        start_time = time.time()
                        model.fit(X, y)
                        training_time = time.time() - start_time
                        
                        training_results[name] = {
                            'model': model,
                            'training_time': training_time,
                            'success': True
                        }
                        print(f"✅ {name} 모델 훈련 완료 ({training_time:.2f}초)")
                        
                    except Exception as e:
                        print(f"❌ {name} 모델 훈련 실패: {e}")
                        training_results[name] = {
                            'model': None,
                            'training_time': 0.0,
                            'success': False,
                            'error': str(e)
                        }
            
            return {
                'success': True,
                'models': training_results,
                'device': self.device
            }
            
        except Exception as e:
            print(f"⚠️ CPU 모델 훈련 중 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    # ===== 4. 안전한 예측 =====
    
    def predict_safe(self, X: np.ndarray, model_name: str = None) -> Dict:
        """안전한 예측"""
        try:
            if self.gpu_available:
                return self._predict_gpu(X, model_name)
            else:
                return self._predict_cpu(X, model_name)
        except Exception as e:
            print(f"⚠️ 예측 중 오류: {e}")
            return {
                'prediction': np.zeros(X.shape[0]),
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def _predict_gpu(self, X: np.ndarray, model_name: str = None) -> Dict:
        """GPU 예측 (향후 구현)"""
        # GPU 예측은 향후 구현
        # 현재는 CPU 예측 사용
        return self._predict_cpu(X, model_name)
    
    def _predict_cpu(self, X: np.ndarray, model_name: str = None) -> Dict:
        """CPU 예측"""
        try:
            if not hasattr(self, 'trained_models') or not self.trained_models:
                return {
                    'prediction': np.zeros(X.shape[0]),
                    'confidence': 0.0,
                    'success': False,
                    'error': '모델이 훈련되지 않았습니다.'
                }
            
            # 모델 선택
            if model_name and model_name in self.trained_models:
                model = self.trained_models[model_name]['model']
            else:
                # 가장 성능이 좋은 모델 선택
                model = self._get_best_model()
            
            if model is None:
                return {
                    'prediction': np.zeros(X.shape[0]),
                    'confidence': 0.0,
                    'success': False,
                    'error': '사용 가능한 모델이 없습니다.'
                }
            
            # 예측 수행
            start_time = time.time()
            prediction = model.predict(X)
            prediction_time = time.time() - start_time
            
            # 신뢰도 계산
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)
                confidence = np.max(proba, axis=1)
            else:
                confidence = np.ones(X.shape[0]) * 0.5
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'prediction_time': prediction_time,
                'success': True
            }
            
        except Exception as e:
            print(f"⚠️ CPU 예측 중 오류: {e}")
            return {
                'prediction': np.zeros(X.shape[0]),
                'confidence': 0.0,
                'success': False,
                'error': str(e)
            }
    
    def _get_best_model(self):
        """가장 성능이 좋은 모델 반환"""
        if not hasattr(self, 'trained_models') or not self.trained_models:
            return None
        
        # 성능이 좋은 모델 선택 (간단한 휴리스틱)
        for name, model_info in self.trained_models.items():
            if model_info['success'] and model_info['model'] is not None:
                return model_info['model']
        
        return None
    
    # ===== 5. 통합 안전 시스템 =====
    
    def safe_ai_pipeline(self, audio_files: List[str], labels: List[int]) -> Dict:
        """통합 안전 AI 파이프라인"""
        
        print("🛡️ 통합 안전 AI 파이프라인 시작")
        print(f"   GPU 사용 가능: {self.gpu_available}")
        print(f"   현재 디바이스: {self.device}")
        
        try:
            # 1. 오디오 데이터 로드
            print("1️⃣ 오디오 데이터 로드 중...")
            audio_data_list = []
            for audio_file in audio_files:
                try:
                    audio_data, sr = librosa.load(audio_file, sr=16000)
                    audio_data_list.append(audio_data)
                except Exception as e:
                    print(f"⚠️ 파일 로드 오류 {audio_file}: {e}")
                    continue
            
            # 2. 특징 추출
            print("2️⃣ 특징 추출 중...")
            features_list = []
            for audio_data in audio_data_list:
                features = self.extract_safe_features(audio_data, 16000)
                # 딕셔너리를 평탄화
                flat_features = []
                for key, value in features.items():
                    if isinstance(value, list):
                        flat_features.extend(value)
                    else:
                        flat_features.append(value)
                features_list.append(flat_features)
            
            X = np.array(features_list)
            y = np.array(labels[:len(features_list)])
            
            # 3. 모델 훈련
            print("3️⃣ 모델 훈련 중...")
            training_result = self.train_safe_models(X, y)
            
            if training_result['success']:
                self.trained_models = training_result['models']
                
                # 4. 모델 평가
                print("4️⃣ 모델 평가 중...")
                evaluation_results = {}
                
                for name, model_info in self.trained_models.items():
                    if model_info['success'] and model_info['model'] is not None:
                        try:
                            # 예측 수행
                            pred_result = self.predict_safe(X, name)
                            
                            if pred_result['success']:
                                # 정확도 계산
                                from sklearn.metrics import accuracy_score
                                accuracy = accuracy_score(y, pred_result['prediction'])
                                
                                evaluation_results[name] = {
                                    'accuracy': accuracy,
                                    'prediction_time': pred_result['prediction_time'],
                                    'confidence': np.mean(pred_result['confidence'])
                                }
                                
                                print(f"   {name}: 정확도 {accuracy:.3f}, 예측 시간 {pred_result['prediction_time']:.3f}초")
                        
                        except Exception as e:
                            print(f"⚠️ {name} 모델 평가 중 오류: {e}")
                
                # 5. 최고 성능 모델 선택
                best_model_name = None
                best_accuracy = 0
                
                for name, result in evaluation_results.items():
                    if result['accuracy'] > best_accuracy:
                        best_accuracy = result['accuracy']
                        best_model_name = name
                
                # 6. 결과 반환
                results = {
                    'success': True,
                    'gpu_available': self.gpu_available,
                    'device': self.device,
                    'best_model': best_model_name,
                    'best_accuracy': best_accuracy,
                    'evaluation_results': evaluation_results,
                    'feature_count': X.shape[1],
                    'total_samples': len(audio_data_list),
                    'training_results': training_result
                }
                
                print(f"✅ 안전 AI 파이프라인 완료!")
                print(f"   최고 정확도: {best_accuracy:.3f}")
                print(f"   최고 모델: {best_model_name}")
                print(f"   특징 수: {X.shape[1]}")
                
                return results
            
            else:
                return {
                    'success': False,
                    'error': training_result.get('error', '모델 훈련 실패'),
                    'gpu_available': self.gpu_available,
                    'device': self.device
                }
                
        except Exception as e:
            print(f"❌ 안전 AI 파이프라인 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'gpu_available': self.gpu_available,
                'device': self.device
            }
    
    # ===== 6. 모델 저장/로드 =====
    
    def save_safe_models(self, filepath: str = None):
        """안전한 모델 저장"""
        try:
            if filepath is None:
                filepath = os.path.join(self.model_save_path, "safe_gpu_ready_models.pkl")
            
            # CPU 모델만 저장 (GPU 모델은 별도 처리)
            cpu_models = {}
            for name, model_info in self.trained_models.items():
                if model_info['success'] and model_info['model'] is not None:
                    cpu_models[name] = model_info['model']
            
            model_data = {
                'cpu_models': cpu_models,
                'gpu_available': self.gpu_available,
                'device': self.device,
                'performance_metrics': self.performance_metrics,
                'saved_at': datetime.now().isoformat()
            }
            
            joblib.dump(model_data, filepath)
            print(f"✅ 안전 모델 저장 완료: {filepath}")
            
        except Exception as e:
            print(f"⚠️ 모델 저장 중 오류: {e}")
    
    def load_safe_models(self, filepath: str = None):
        """안전한 모델 로드"""
        try:
            if filepath is None:
                filepath = os.path.join(self.model_save_path, "safe_gpu_ready_models.pkl")
            
            if not os.path.exists(filepath):
                print(f"⚠️ 모델 파일을 찾을 수 없습니다: {filepath}")
                return False
            
            model_data = joblib.load(filepath)
            
            # CPU 모델 로드
            self.trained_models = {}
            for name, model in model_data['cpu_models'].items():
                self.trained_models[name] = {
                    'model': model,
                    'training_time': 0.0,
                    'success': True
                }
            
            self.gpu_available = model_data.get('gpu_available', False)
            self.device = model_data.get('device', 'cpu')
            self.performance_metrics = model_data.get('performance_metrics', {})
            
            print(f"✅ 안전 모델 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"⚠️ 모델 로드 중 오류: {e}")
            return False

# 사용 예제
if __name__ == "__main__":
    # 안전한 GPU 준비 시스템 테스트
    safe_system = SafeGPUReadySystem()
    
    print("🛡️ 안전한 GPU 준비 시스템 테스트")
    print("=" * 50)
    
    # 가상의 테스트 데이터
    test_audio_files = ["test1.wav", "test2.wav", "test3.wav"]
    test_labels = [0, 1, 0]  # 0: 정상, 1: 이상
    
    # 안전 AI 파이프라인 실행
    results = safe_system.safe_ai_pipeline(test_audio_files, test_labels)
    
    if results['success']:
        print("📊 결과:")
        print(f"   GPU 사용 가능: {results['gpu_available']}")
        print(f"   현재 디바이스: {results['device']}")
        print(f"   최고 정확도: {results['best_accuracy']:.3f}")
        print(f"   최고 모델: {results['best_model']}")
        print(f"   특징 수: {results['feature_count']}")
        print(f"   총 샘플 수: {results['total_samples']}")
    else:
        print(f"❌ 파이프라인 실패: {results['error']}")
