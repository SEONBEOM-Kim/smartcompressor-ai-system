#!/usr/bin/env python3
"""
노리스크 정확도 향상 방법들
GPU 없이도 안전하게 동작하는 개선 방법들
"""

import numpy as np
import librosa
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
import joblib
from typing import Dict, List, Tuple, Optional
import warnings
import time
import threading
from concurrent.futures import ThreadPoolExecutor
warnings.filterwarnings('ignore')

class NoRiskAccuracyImprovements:
    """노리스크 정확도 향상 방법들"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.models = {}
        self.feature_importance = {}
        self.performance_cache = {}
        
        print("🚀 노리스크 정확도 향상 방법들 초기화 완료")
    
    # ===== 1. 데이터 증강 (Data Augmentation) =====
    
    def augment_audio_data(self, audio_data: np.ndarray, sr: int, 
                          augmentation_factor: int = 2) -> List[np.ndarray]:
        """안전한 오디오 데이터 증강"""
        augmented_data = [audio_data]  # 원본 포함
        
        try:
            for i in range(augmentation_factor):
                # 1. 노이즈 추가 (안전한 범위)
                noise_factor = np.random.uniform(0.001, 0.005)  # 매우 작은 노이즈
                noise = np.random.normal(0, noise_factor, len(audio_data))
                noisy_audio = audio_data + noise
                augmented_data.append(noisy_audio)
                
                # 2. 시간 변형 (안전한 범위)
                speed_factor = np.random.uniform(0.95, 1.05)  # 5% 범위 내
                if speed_factor != 1.0:
                    try:
                        time_stretched = librosa.effects.time_stretch(audio_data, rate=speed_factor)
                        # 길이 맞추기
                        if len(time_stretched) > len(audio_data):
                            time_stretched = time_stretched[:len(audio_data)]
                        else:
                            time_stretched = np.pad(time_stretched, (0, len(audio_data) - len(time_stretched)))
                        augmented_data.append(time_stretched)
                    except:
                        pass
                
                # 3. 볼륨 조절 (안전한 범위)
                volume_factor = np.random.uniform(0.9, 1.1)  # 10% 범위 내
                volume_adjusted = audio_data * volume_factor
                augmented_data.append(volume_adjusted)
                
                # 4. 시간 이동 (안전한 범위)
                shift_samples = np.random.randint(0, len(audio_data) // 10)  # 10% 범위 내
                shifted_audio = np.roll(audio_data, shift_samples)
                augmented_data.append(shifted_audio)
                
        except Exception as e:
            print(f"⚠️ 데이터 증강 중 오류 (무시하고 계속): {e}")
        
        return augmented_data
    
    # ===== 2. 고급 특징 추출 (Advanced Feature Extraction) =====
    
    def extract_advanced_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """고급 오디오 특징 추출 (안전한 버전)"""
        features = {}
        
        try:
            # 1. MFCC (안전한 범위)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
            
            # 2. Chroma (음계 특징)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
            features['chroma_std'] = np.std(chroma, axis=1).tolist()
            
            # 3. Spectral Contrast
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
            features['contrast_mean'] = np.mean(contrast, axis=1).tolist()
            features['contrast_std'] = np.std(contrast, axis=1).tolist()
            
            # 4. Zero Crossing Rate
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            
            # 5. Spectral Rolloff
            rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
            features['rolloff_mean'] = np.mean(rolloff)
            features['rolloff_std'] = np.std(rolloff)
            
            # 6. Spectral Bandwidth
            bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)
            features['bandwidth_mean'] = np.mean(bandwidth)
            features['bandwidth_std'] = np.std(bandwidth)
            
            # 7. Spectral Centroid
            centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
            features['centroid_mean'] = np.mean(centroid)
            features['centroid_std'] = np.std(centroid)
            
            # 8. RMS Energy
            rms = librosa.feature.rms(y=audio_data)
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            
            # 9. Spectral Flatness
            flatness = librosa.feature.spectral_flatness(y=audio_data)
            features['flatness_mean'] = np.mean(flatness)
            features['flatness_std'] = np.std(flatness)
            
            # 10. Tempo (안전한 범위)
            try:
                tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)
                features['tempo'] = tempo if tempo is not None and 0 < tempo < 300 else 0.0
            except:
                features['tempo'] = 0.0
            
        except Exception as e:
            print(f"⚠️ 고급 특징 추출 중 오류 (기본값 사용): {e}")
            # 기본값으로 채우기
            features = {f'feature_{i}': 0.0 for i in range(50)}
        
        return features
    
    # ===== 3. 특징 선택 (Feature Selection) =====
    
    def select_best_features(self, X: np.ndarray, y: np.ndarray, 
                           method: str = 'mutual_info', k: int = 20) -> np.ndarray:
        """안전한 특징 선택"""
        try:
            if method == 'mutual_info':
                selector = SelectKBest(score_func=mutual_info_classif, k=min(k, X.shape[1]))
            elif method == 'f_score':
                selector = SelectKBest(score_func=f_classif, k=min(k, X.shape[1]))
            else:
                from sklearn.feature_selection import VarianceThreshold
                selector = VarianceThreshold(threshold=0.01)
            
            X_selected = selector.fit_transform(X, y)
            self.feature_selector = selector
            
            # 특징 중요도 저장
            if hasattr(selector, 'scores_'):
                self.feature_importance = {
                    'scores': selector.scores_,
                    'selected_features': selector.get_support(indices=True)
                }
            
            return X_selected
            
        except Exception as e:
            print(f"⚠️ 특징 선택 중 오류 (원본 사용): {e}")
            return X
    
    # ===== 4. 액티브 학습 (Active Learning) =====
    
    def active_learning_query(self, X: np.ndarray, model, 
                            query_strategy: str = 'uncertainty', n_queries: int = 10) -> np.ndarray:
        """액티브 학습을 위한 쿼리 샘플 선택"""
        try:
            if query_strategy == 'uncertainty':
                # 불확실성 기반 선택
                pred_proba = model.predict_proba(X)
                uncertainty = 1 - np.max(pred_proba, axis=1)
                query_indices = np.argsort(uncertainty)[-n_queries:]
                
            elif query_strategy == 'diversity':
                # 다양성 기반 선택 (클러스터링)
                n_clusters = min(10, len(X) // 2)
                if n_clusters > 1:
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                    cluster_labels = kmeans.fit_predict(X)
                    
                    # 각 클러스터에서 하나씩 선택
                    query_indices = []
                    for cluster_id in range(n_clusters):
                        cluster_mask = cluster_labels == cluster_id
                        if np.any(cluster_mask):
                            cluster_indices = np.where(cluster_mask)[0]
                            query_indices.append(np.random.choice(cluster_indices))
                else:
                    query_indices = np.random.choice(len(X), size=min(n_queries, len(X)), replace=False)
                    
            else:  # random
                # 랜덤 선택
                query_indices = np.random.choice(len(X), size=min(n_queries, len(X)), replace=False)
            
            return query_indices
            
        except Exception as e:
            print(f"⚠️ 액티브 학습 쿼리 중 오류 (랜덤 선택): {e}")
            return np.random.choice(len(X), size=min(n_queries, len(X)), replace=False)
    
    def active_learning_pipeline(self, X: np.ndarray, y: np.ndarray, 
                               initial_size: int = 100, query_size: int = 10, 
                               max_iterations: int = 10) -> Dict:
        """액티브 학습 파이프라인"""
        try:
            # 초기 데이터로 모델 훈련
            initial_indices = np.random.choice(len(X), size=min(initial_size, len(X)), replace=False)
            X_initial = X[initial_indices]
            y_initial = y[initial_indices]
            
            # 초기 모델 훈련
            model = GradientBoostingClassifier(n_estimators=50, random_state=42)
            model.fit(X_initial, y_initial)
            
            # 액티브 학습 반복
            labeled_indices = set(initial_indices)
            performance_history = []
            
            for iteration in range(max_iterations):
                # 쿼리 샘플 선택
                unlabeled_mask = ~np.isin(np.arange(len(X)), list(labeled_indices))
                X_unlabeled = X[unlabeled_mask]
                
                if len(X_unlabeled) == 0:
                    break
                
                # 쿼리 샘플 선택
                query_indices = self.active_learning_query(X_unlabeled, model, n_queries=query_size)
                actual_query_indices = np.where(unlabeled_mask)[0][query_indices]
                
                # 새로운 샘플 추가
                labeled_indices.update(actual_query_indices)
                X_labeled = X[list(labeled_indices)]
                y_labeled = y[list(labeled_indices)]
                
                # 모델 재훈련
                model.fit(X_labeled, y_labeled)
                
                # 성능 평가
                if len(labeled_indices) < len(X):
                    test_indices = np.random.choice(
                        [i for i in range(len(X)) if i not in labeled_indices],
                        size=min(50, len(X) - len(labeled_indices)),
                        replace=False
                    )
                    X_test = X[test_indices]
                    y_test = y[test_indices]
                    
                    y_pred = model.predict(X_test)
                    accuracy = accuracy_score(y_test, y_pred)
                    performance_history.append(accuracy)
                    
                    print(f"액티브 학습 반복 {iteration + 1}: 정확도 {accuracy:.3f}")
            
            return {
                'model': model,
                'performance_history': performance_history,
                'final_accuracy': performance_history[-1] if performance_history else 0.0,
                'total_labeled_samples': len(labeled_indices)
            }
            
        except Exception as e:
            print(f"⚠️ 액티브 학습 파이프라인 중 오류: {e}")
            return {'model': None, 'performance_history': [], 'final_accuracy': 0.0, 'total_labeled_samples': 0}
    
    # ===== 5. 처리 시간 최적화 =====
    
    def optimize_processing_time(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """처리 시간 최적화"""
        try:
            # 1. 특징 수 줄이기
            X_reduced = self.select_best_features(X, y, k=20)
            
            # 2. PCA로 차원 축소
            pca = PCA(n_components=min(10, X_reduced.shape[1]))
            X_pca = pca.fit_transform(X_reduced)
            
            # 3. 빠른 모델 사용
            fast_model = RandomForestClassifier(
                n_estimators=50,  # 트리 수 줄이기
                max_depth=10,     # 깊이 제한
                random_state=42
            )
            
            # 4. 성능 측정
            start_time = time.time()
            fast_model.fit(X_pca, y)
            training_time = time.time() - start_time
            
            start_time = time.time()
            y_pred = fast_model.predict(X_pca)
            prediction_time = time.time() - start_time
            
            accuracy = accuracy_score(y, y_pred)
            
            return {
                'model': fast_model,
                'pca': pca,
                'accuracy': accuracy,
                'training_time': training_time,
                'prediction_time': prediction_time,
                'feature_count': X_pca.shape[1]
            }
            
        except Exception as e:
            print(f"⚠️ 처리 시간 최적화 중 오류: {e}")
            return {'model': None, 'accuracy': 0.0, 'training_time': 0.0, 'prediction_time': 0.0}
    
    # ===== 6. GPU 없이 안전한 딥러닝 준비 =====
    
    def prepare_gpu_ready_code(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """GPU 없이도 동작하는 딥러닝 준비 코드"""
        try:
            # GPU 사용 가능 여부 확인
            gpu_available = self._check_gpu_availability()
            
            if gpu_available:
                print("✅ GPU 사용 가능 - 딥러닝 모델 사용")
                return self._create_deep_learning_model(X, y)
            else:
                print("⚠️ GPU 사용 불가 - 전통적 ML 모델 사용")
                return self._create_traditional_model(X, y)
                
        except Exception as e:
            print(f"⚠️ GPU 준비 코드 중 오류: {e}")
            return self._create_traditional_model(X, y)
    
    def _check_gpu_availability(self) -> bool:
        """GPU 사용 가능 여부 확인"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False
    
    def _create_deep_learning_model(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """딥러닝 모델 생성 (GPU 사용)"""
        try:
            import torch
            import torch.nn as nn
            
            # 간단한 신경망
            class SimpleNN(nn.Module):
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
            
            model = SimpleNN(X.shape[1])
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            model = model.to(device)
            
            return {
                'model': model,
                'device': device,
                'model_type': 'deep_learning',
                'gpu_available': True
            }
            
        except Exception as e:
            print(f"⚠️ 딥러닝 모델 생성 중 오류: {e}")
            return self._create_traditional_model(X, y)
    
    def _create_traditional_model(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """전통적 ML 모델 생성 (CPU 사용)"""
        try:
            model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                random_state=42
            )
            
            model.fit(X, y)
            
            return {
                'model': model,
                'device': 'cpu',
                'model_type': 'traditional',
                'gpu_available': False
            }
            
        except Exception as e:
            print(f"⚠️ 전통적 모델 생성 중 오류: {e}")
            return {'model': None, 'device': 'cpu', 'model_type': 'error', 'gpu_available': False}
    
    # ===== 7. 통합 노리스크 파이프라인 =====
    
    def no_risk_improvement_pipeline(self, audio_files: List[str], 
                                   labels: List[int]) -> Dict:
        """통합 노리스크 개선 파이프라인"""
        
        print("🚀 노리스크 정확도 향상 파이프라인 시작")
        
        try:
            # 1. 데이터 증강 (안전한 범위)
            print("1️⃣ 안전한 데이터 증강 중...")
            augmented_audio, augmented_labels = self.batch_augment_data(
                audio_files, labels, augmentation_factor=2
            )
            
            # 2. 고급 특징 추출
            print("2️⃣ 고급 특징 추출 중...")
            features_list = []
            for audio_data in augmented_audio:
                features = self.extract_advanced_features(audio_data, 16000)
                # 딕셔너리를 평탄화
                flat_features = []
                for key, value in features.items():
                    if isinstance(value, list):
                        flat_features.extend(value)
                    else:
                        flat_features.append(value)
                features_list.append(flat_features)
            
            X = np.array(features_list)
            y = np.array(augmented_labels)
            
            # 3. 특징 선택
            print("3️⃣ 특징 선택 중...")
            X_selected = self.select_best_features(X, y, method='mutual_info', k=30)
            
            # 4. 액티브 학습
            print("4️⃣ 액티브 학습 중...")
            active_learning_result = self.active_learning_pipeline(
                X_selected, y, initial_size=50, query_size=5, max_iterations=5
            )
            
            # 5. 처리 시간 최적화
            print("5️⃣ 처리 시간 최적화 중...")
            optimization_result = self.optimize_processing_time(X_selected, y)
            
            # 6. GPU 준비 코드
            print("6️⃣ GPU 준비 코드 생성 중...")
            gpu_ready_result = self.prepare_gpu_ready_code(X_selected, y)
            
            # 7. 성능 평가
            print("7️⃣ 성능 평가 중...")
            X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42)
            
            if active_learning_result['model'] is not None:
                final_model = active_learning_result['model']
            else:
                final_model = optimization_result['model']
            
            if final_model is not None:
                final_model.fit(X_train, y_train)
                y_pred = final_model.predict(X_test)
                accuracy = accuracy_score(y_test, y_pred)
            else:
                accuracy = 0.0
            
            results = {
                'accuracy': accuracy,
                'active_learning': active_learning_result,
                'optimization': optimization_result,
                'gpu_ready': gpu_ready_result,
                'feature_count': X_selected.shape[1],
                'total_samples': len(augmented_audio),
                'original_samples': len(audio_files),
                'improvement_methods': [
                    'data_augmentation',
                    'advanced_feature_extraction',
                    'feature_selection',
                    'active_learning',
                    'processing_time_optimization',
                    'gpu_ready_preparation'
                ]
            }
            
            print(f"✅ 노리스크 파이프라인 완료! 정확도: {accuracy:.3f}")
            return results
            
        except Exception as e:
            print(f"❌ 노리스크 파이프라인 중 오류: {e}")
            return {
                'accuracy': 0.0,
                'error': str(e),
                'improvement_methods': []
            }
    
    def batch_augment_data(self, audio_files: List[str], labels: List[int], 
                          augmentation_factor: int = 2) -> Tuple[List[np.ndarray], List[int]]:
        """배치 데이터 증강 (안전한 버전)"""
        augmented_audio = []
        augmented_labels = []
        
        for audio_file, label in zip(audio_files, labels):
            try:
                audio_data, sr = librosa.load(audio_file, sr=16000)
                augmented_samples = self.augment_audio_data(audio_data, sr, augmentation_factor)
                
                augmented_audio.extend(augmented_samples)
                augmented_labels.extend([label] * len(augmented_samples))
                
            except Exception as e:
                print(f"⚠️ 파일 증강 오류 {audio_file} (무시하고 계속): {e}")
                continue
        
        return augmented_audio, augmented_labels

# 사용 예제
if __name__ == "__main__":
    # 노리스크 정확도 향상 테스트
    improver = NoRiskAccuracyImprovements()
    
    print("🎯 노리스크 정확도 향상 방법들 테스트")
    print("=" * 50)
    
    # 가상의 테스트 데이터
    test_audio_files = ["test1.wav", "test2.wav", "test3.wav"]
    test_labels = [0, 1, 0]  # 0: 정상, 1: 이상
    
    # 노리스크 파이프라인 실행
    results = improver.no_risk_improvement_pipeline(test_audio_files, test_labels)
    
    print("📊 결과:")
    print(f"   정확도: {results['accuracy']:.3f}")
    print(f"   선택된 특징 수: {results['feature_count']}")
    print(f"   총 샘플 수: {results['total_samples']}")
    print(f"   원본 샘플 수: {results['original_samples']}")
    print(f"   개선 방법들: {results['improvement_methods']}")
