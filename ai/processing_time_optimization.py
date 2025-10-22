#!/usr/bin/env python3
"""
처리 시간 최적화 방법들
GPU 없이도 빠른 처리를 위한 다양한 최적화 기법들
"""

import numpy as np
import librosa
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from functools import lru_cache
import joblib
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class ProcessingTimeOptimizer:
    """처리 시간 최적화 클래스"""
    
    def __init__(self):
        self.feature_cache = {}
        self.model_cache = {}
        self.performance_metrics = {}
        
        print("⚡ 처리 시간 최적화 시스템 초기화 완료")
    
    # ===== 1. 캐싱 시스템 =====
    
    @lru_cache(maxsize=1000)
    def cached_feature_extraction(self, audio_hash: str, sr: int) -> Dict:
        """캐시된 특징 추출"""
        # 실제로는 audio_hash를 사용하여 캐시에서 가져옴
        # 여기서는 간단한 예시
        return {'feature_1': 0.5, 'feature_2': 0.3}
    
    def get_audio_hash(self, audio_data: np.ndarray) -> str:
        """오디오 데이터의 해시 생성"""
        return str(hash(audio_data.tobytes()))
    
    # ===== 2. 병렬 처리 =====
    
    def parallel_feature_extraction(self, audio_data_list: List[np.ndarray], 
                                  sr: int, max_workers: int = 4) -> List[Dict]:
        """병렬 특징 추출"""
        def extract_features_single(audio_data):
            try:
                # 간단한 특징 추출
                features = {
                    'rms': np.sqrt(np.mean(audio_data ** 2)),
                    'zcr': np.mean(librosa.feature.zero_crossing_rate(audio_data)),
                    'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))
                }
                return features
            except:
                return {'rms': 0.0, 'zcr': 0.0, 'spectral_centroid': 0.0}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(extract_features_single, audio_data_list))
        
        return results
    
    def parallel_model_prediction(self, X: np.ndarray, models: List) -> List[np.ndarray]:
        """병렬 모델 예측"""
        def predict_single(model):
            try:
                return model.predict(X)
            except:
                return np.zeros(X.shape[0])
        
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            results = list(executor.map(predict_single, models))
        
        return results
    
    # ===== 3. 배치 처리 =====
    
    def batch_process_audio(self, audio_data_list: List[np.ndarray], 
                           batch_size: int = 32) -> List[Dict]:
        """배치 오디오 처리"""
        results = []
        
        for i in range(0, len(audio_data_list), batch_size):
            batch = audio_data_list[i:i + batch_size]
            batch_results = self.parallel_feature_extraction(batch, 16000)
            results.extend(batch_results)
        
        return results
    
    # ===== 4. 메모리 최적화 =====
    
    def memory_efficient_processing(self, audio_data: np.ndarray, sr: int) -> Dict:
        """메모리 효율적 처리"""
        try:
            # 청크 단위로 처리
            chunk_size = int(5.0 * sr)  # 5초 청크
            features_list = []
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                if len(chunk) >= chunk_size:
                    # 간단한 특징만 추출
                    features = {
                        'rms': np.sqrt(np.mean(chunk ** 2)),
                        'zcr': np.mean(librosa.feature.zero_crossing_rate(chunk))
                    }
                    features_list.append(features)
            
            # 청크별 특징을 평균
            if features_list:
                final_features = {}
                for key in features_list[0].keys():
                    final_features[key] = np.mean([f[key] for f in features_list])
            else:
                final_features = {'rms': 0.0, 'zcr': 0.0}
            
            return final_features
            
        except Exception as e:
            print(f"⚠️ 메모리 효율적 처리 중 오류: {e}")
            return {'rms': 0.0, 'zcr': 0.0}
    
    # ===== 5. 빠른 모델 사용 =====
    
    def create_fast_models(self) -> Dict:
        """빠른 모델들 생성"""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.naive_bayes import GaussianNB
        
        models = {
            'fast_rf': RandomForestClassifier(
                n_estimators=50,  # 트리 수 줄이기
                max_depth=10,     # 깊이 제한
                random_state=42
            ),
            'logistic': LogisticRegression(
                max_iter=100,     # 반복 수 줄이기
                random_state=42
            ),
            'naive_bayes': GaussianNB()
        }
        
        return models
    
    def fast_prediction(self, X: np.ndarray, model) -> np.ndarray:
        """빠른 예측"""
        try:
            # 예측 시간 측정
            start_time = time.time()
            y_pred = model.predict(X)
            prediction_time = time.time() - start_time
            
            # 성능 메트릭 저장
            if 'prediction_times' not in self.performance_metrics:
                self.performance_metrics['prediction_times'] = []
            self.performance_metrics['prediction_times'].append(prediction_time)
            
            return y_pred
            
        except Exception as e:
            print(f"⚠️ 빠른 예측 중 오류: {e}")
            return np.zeros(X.shape[0])
    
    # ===== 6. 특징 압축 =====
    
    def compress_features(self, X: np.ndarray, compression_ratio: float = 0.5) -> np.ndarray:
        """특징 압축"""
        try:
            from sklearn.decomposition import PCA
            
            n_components = int(X.shape[1] * compression_ratio)
            n_components = max(1, min(n_components, X.shape[1]))
            
            pca = PCA(n_components=n_components)
            X_compressed = pca.fit_transform(X)
            
            return X_compressed
            
        except Exception as e:
            print(f"⚠️ 특징 압축 중 오류: {e}")
            return X
    
    # ===== 7. 실시간 처리 최적화 =====
    
    def real_time_optimization(self, audio_data: np.ndarray, sr: int) -> Dict:
        """실시간 처리 최적화"""
        try:
            # 1. 빠른 전처리
            start_time = time.time()
            
            # 간단한 필터링
            audio_filtered = audio_data
            
            # 2. 최소한의 특징만 추출
            features = {
                'rms': np.sqrt(np.mean(audio_filtered ** 2)),
                'zcr': np.mean(librosa.feature.zero_crossing_rate(audio_filtered)),
                'spectral_centroid': np.mean(librosa.feature.spectral_centroid(y=audio_filtered, sr=sr))
            }
            
            # 3. 빠른 예측
            X = np.array([list(features.values())]).reshape(1, -1)
            
            # 간단한 규칙 기반 예측 (가장 빠름)
            if features['rms'] > 0.1 and features['zcr'] > 0.1:
                prediction = 1  # 이상
                confidence = 0.8
            else:
                prediction = 0  # 정상
                confidence = 0.6
            
            processing_time = time.time() - start_time
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'processing_time': processing_time,
                'features': features
            }
            
        except Exception as e:
            print(f"⚠️ 실시간 최적화 중 오류: {e}")
            return {
                'prediction': 0,
                'confidence': 0.0,
                'processing_time': 0.0,
                'features': {}
            }
    
    # ===== 8. GPU 준비 코드 (GPU 없이도 동작) =====
    
    def gpu_ready_processing(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """GPU 준비 코드 (GPU 없이도 동작)"""
        try:
            # GPU 사용 가능 여부 확인
            gpu_available = self._check_gpu_availability()
            
            if gpu_available:
                print("✅ GPU 사용 가능 - 딥러닝 모델 사용")
                return self._gpu_processing(X, y)
            else:
                print("⚠️ GPU 사용 불가 - CPU 최적화 모델 사용")
                return self._cpu_optimized_processing(X, y)
                
        except Exception as e:
            print(f"⚠️ GPU 준비 처리 중 오류: {e}")
            return self._cpu_optimized_processing(X, y)
    
    def _check_gpu_availability(self) -> bool:
        """GPU 사용 가능 여부 확인"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def _gpu_processing(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """GPU 처리 (GPU 사용 가능 시)"""
        try:
            import torch
            import torch.nn as nn
            
            # 간단한 신경망
            class FastNN(nn.Module):
                def __init__(self, input_size, hidden_size=32, output_size=2):
                    super().__init__()
                    self.fc1 = nn.Linear(input_size, hidden_size)
                    self.fc2 = nn.Linear(hidden_size, output_size)
                    self.relu = nn.ReLU()
                
                def forward(self, x):
                    x = self.relu(self.fc1(x))
                    x = self.fc2(x)
                    return x
            
            model = FastNN(X.shape[1])
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model = model.to(device)
            
            return {
                'model': model,
                'device': device,
                'processing_type': 'gpu',
                'gpu_available': True
            }
            
        except Exception as e:
            print(f"⚠️ GPU 처리 중 오류: {e}")
            return self._cpu_optimized_processing(X, y)
    
    def _cpu_optimized_processing(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """CPU 최적화 처리"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.linear_model import LogisticRegression
            
            # 빠른 모델들
            models = {
                'fast_rf': RandomForestClassifier(
                    n_estimators=50,
                    max_depth=10,
                    random_state=42
                ),
                'logistic': LogisticRegression(
                    max_iter=100,
                    random_state=42
                )
            }
            
            # 가장 빠른 모델 선택
            fast_model = models['logistic']
            fast_model.fit(X, y)
            
            return {
                'model': fast_model,
                'device': 'cpu',
                'processing_type': 'cpu_optimized',
                'gpu_available': False
            }
            
        except Exception as e:
            print(f"⚠️ CPU 최적화 처리 중 오류: {e}")
            return {'model': None, 'device': 'cpu', 'processing_type': 'error', 'gpu_available': False}
    
    # ===== 9. 통합 최적화 파이프라인 =====
    
    def comprehensive_optimization_pipeline(self, audio_files: List[str], 
                                          labels: List[int]) -> Dict:
        """종합 최적화 파이프라인"""
        
        print("⚡ 종합 처리 시간 최적화 파이프라인 시작")
        
        try:
            # 1. 오디오 데이터 로드
            print("1️⃣ 오디오 데이터 로드 중...")
            audio_data_list = []
            for audio_file in audio_files:
                try:
                    audio_data, sr = librosa.load(audio_file, sr=16000)
                    audio_data_list.append(audio_data)
                except:
                    continue
            
            # 2. 병렬 특징 추출
            print("2️⃣ 병렬 특징 추출 중...")
            start_time = time.time()
            features_list = self.parallel_feature_extraction(audio_data_list, 16000)
            feature_extraction_time = time.time() - start_time
            
            # 3. 특징 압축
            print("3️⃣ 특징 압축 중...")
            X = np.array([list(f.values()) for f in features_list])
            X_compressed = self.compress_features(X, compression_ratio=0.5)
            
            # 4. 빠른 모델 훈련
            print("4️⃣ 빠른 모델 훈련 중...")
            start_time = time.time()
            fast_models = self.create_fast_models()
            training_times = {}
            
            for name, model in fast_models.items():
                model_start = time.time()
                model.fit(X_compressed, labels[:len(X_compressed)])
                training_times[name] = time.time() - model_start
            
            # 5. 빠른 예측 테스트
            print("5️⃣ 빠른 예측 테스트 중...")
            prediction_times = {}
            for name, model in fast_models.items():
                start_time = time.time()
                y_pred = self.fast_prediction(X_compressed, model)
                prediction_times[name] = time.time() - start_time
            
            # 6. GPU 준비 코드
            print("6️⃣ GPU 준비 코드 생성 중...")
            gpu_ready_result = self.gpu_ready_processing(X_compressed, labels[:len(X_compressed)])
            
            # 7. 성능 평가
            print("7️⃣ 성능 평가 중...")
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import accuracy_score
            
            X_train, X_test, y_train, y_test = train_test_split(
                X_compressed, labels[:len(X_compressed)], test_size=0.2, random_state=42
            )
            
            best_model = None
            best_accuracy = 0
            best_prediction_time = float('inf')
            
            for name, model in fast_models.items():
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
                
                if accuracy > best_accuracy or (accuracy == best_accuracy and prediction_times[name] < best_prediction_time):
                    best_accuracy = accuracy
                    best_prediction_time = prediction_times[name]
                    best_model = model
            
            results = {
                'best_model': best_model,
                'best_accuracy': best_accuracy,
                'best_prediction_time': best_prediction_time,
                'feature_extraction_time': feature_extraction_time,
                'training_times': training_times,
                'prediction_times': prediction_times,
                'gpu_ready': gpu_ready_result,
                'compression_ratio': 0.5,
                'feature_count': X_compressed.shape[1],
                'total_samples': len(audio_data_list),
                'optimization_methods': [
                    'parallel_processing',
                    'feature_compression',
                    'fast_models',
                    'batch_processing',
                    'memory_optimization',
                    'gpu_ready_preparation'
                ]
            }
            
            print(f"✅ 최적화 파이프라인 완료!")
            print(f"   최고 정확도: {best_accuracy:.3f}")
            print(f"   최고 예측 시간: {best_prediction_time:.3f}초")
            print(f"   특징 추출 시간: {feature_extraction_time:.3f}초")
            
            return results
            
        except Exception as e:
            print(f"❌ 최적화 파이프라인 중 오류: {e}")
            return {
                'best_accuracy': 0.0,
                'best_prediction_time': 0.0,
                'error': str(e),
                'optimization_methods': []
            }

# 사용 예제
if __name__ == "__main__":
    # 처리 시간 최적화 테스트
    optimizer = ProcessingTimeOptimizer()
    
    print("⚡ 처리 시간 최적화 방법들 테스트")
    print("=" * 50)
    
    # 가상의 테스트 데이터
    test_audio_files = ["test1.wav", "test2.wav", "test3.wav"]
    test_labels = [0, 1, 0]  # 0: 정상, 1: 이상
    
    # 최적화 파이프라인 실행
    results = optimizer.comprehensive_optimization_pipeline(test_audio_files, test_labels)
    
    print("📊 결과:")
    print(f"   최고 정확도: {results['best_accuracy']:.3f}")
    print(f"   최고 예측 시간: {results['best_prediction_time']:.3f}초")
    print(f"   특징 추출 시간: {results['feature_extraction_time']:.3f}초")
    print(f"   특징 수: {results['feature_count']}")
    print(f"   최적화 방법들: {results['optimization_methods']}")
