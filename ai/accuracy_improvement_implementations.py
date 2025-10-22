#!/usr/bin/env python3
"""
정확도 향상을 위한 다양한 구현 방법들
사용자가 선택한 방법에 따라 구현할 수 있는 코드 예시들
"""

import numpy as np
import librosa
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import joblib
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class AccuracyImprovementMethods:
    """정확도 향상을 위한 다양한 방법들을 구현하는 클래스"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.models = {}
        self.feature_importance = {}
        
        print("🚀 정확도 향상 방법들 초기화 완료")
    
    # ===== 1. 데이터 증강 (Data Augmentation) =====
    
    def augment_audio_data(self, audio_data: np.ndarray, sr: int, 
                          augmentation_factor: int = 3) -> List[np.ndarray]:
        """
        오디오 데이터 증강
        
        Args:
            audio_data: 원본 오디오 데이터
            sr: 샘플링 레이트
            augmentation_factor: 증강 배수
            
        Returns:
            증강된 오디오 데이터 리스트
        """
        augmented_data = [audio_data]  # 원본 포함
        
        for i in range(augmentation_factor):
            # 1. 노이즈 추가
            noise_factor = np.random.uniform(0.001, 0.01)
            noise = np.random.normal(0, noise_factor, len(audio_data))
            noisy_audio = audio_data + noise
            augmented_data.append(noisy_audio)
            
            # 2. 시간 변형 (속도 조절)
            speed_factor = np.random.uniform(0.8, 1.2)
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
            
            # 3. 주파수 변형 (피치 조절)
            pitch_shift = np.random.randint(-2, 3)
            if pitch_shift != 0:
                try:
                    pitch_shifted = librosa.effects.pitch_shift(audio_data, sr=sr, n_steps=pitch_shift)
                    augmented_data.append(pitch_shifted)
                except:
                    pass
            
            # 4. 볼륨 조절
            volume_factor = np.random.uniform(0.7, 1.3)
            volume_adjusted = audio_data * volume_factor
            augmented_data.append(volume_adjusted)
            
            # 5. 시간 이동 (Time Shifting)
            shift_samples = np.random.randint(0, len(audio_data) // 4)
            shifted_audio = np.roll(audio_data, shift_samples)
            augmented_data.append(shifted_audio)
        
        return augmented_data
    
    def batch_augment_data(self, audio_files: List[str], labels: List[int], 
                          augmentation_factor: int = 3) -> Tuple[List[np.ndarray], List[int]]:
        """배치 데이터 증강"""
        augmented_audio = []
        augmented_labels = []
        
        for audio_file, label in zip(audio_files, labels):
            try:
                audio_data, sr = librosa.load(audio_file, sr=16000)
                augmented_samples = self.augment_audio_data(audio_data, sr, augmentation_factor)
                
                augmented_audio.extend(augmented_samples)
                augmented_labels.extend([label] * len(augmented_samples))
                
            except Exception as e:
                print(f"❌ 파일 증강 오류 {audio_file}: {e}")
                continue
        
        return augmented_audio, augmented_labels
    
    # ===== 2. 고급 특징 추출 (Advanced Feature Extraction) =====
    
    def extract_advanced_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """고급 오디오 특징 추출"""
        features = {}
        
        try:
            # 1. MFCC (Mel-frequency cepstral coefficients)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1).tolist()
            features['mfcc_std'] = np.std(mfccs, axis=1).tolist()
            features['mfcc_delta'] = np.mean(librosa.feature.delta(mfccs), axis=1).tolist()
            
            # 2. Chroma (음계 특징)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            features['chroma_mean'] = np.mean(chroma, axis=1).tolist()
            features['chroma_std'] = np.std(chroma, axis=1).tolist()
            
            # 3. Spectral Contrast
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
            features['contrast_mean'] = np.mean(contrast, axis=1).tolist()
            features['contrast_std'] = np.std(contrast, axis=1).tolist()
            
            # 4. Tonnetz (조성 특징)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sr)
            features['tonnetz_mean'] = np.mean(tonnetz, axis=1).tolist()
            
            # 5. Zero Crossing Rate (고급)
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            features['zcr_mean'] = np.mean(zcr)
            features['zcr_std'] = np.std(zcr)
            
            # 6. Spectral Rolloff (고급)
            rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
            features['rolloff_mean'] = np.mean(rolloff)
            features['rolloff_std'] = np.std(rolloff)
            
            # 7. Spectral Bandwidth (고급)
            bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)
            features['bandwidth_mean'] = np.mean(bandwidth)
            features['bandwidth_std'] = np.std(bandwidth)
            
            # 8. Spectral Centroid (고급)
            centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
            features['centroid_mean'] = np.mean(centroid)
            features['centroid_std'] = np.std(centroid)
            
            # 9. RMS Energy (고급)
            rms = librosa.feature.rms(y=audio_data)
            features['rms_mean'] = np.mean(rms)
            features['rms_std'] = np.std(rms)
            
            # 10. Spectral Flatness
            flatness = librosa.feature.spectral_flatness(y=audio_data)
            features['flatness_mean'] = np.mean(flatness)
            features['flatness_std'] = np.std(flatness)
            
            # 11. Tempo (템포)
            tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)
            features['tempo'] = tempo if tempo is not None else 0.0
            
            # 12. Spectral Contrast (고급)
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
            features['contrast_mean'] = np.mean(contrast)
            features['contrast_std'] = np.std(contrast)
            
            # 13. Poly Features (다항식 특징)
            poly_features = librosa.feature.poly_features(y=audio_data, sr=sr)
            features['poly_mean'] = np.mean(poly_features)
            features['poly_std'] = np.std(poly_features)
            
            # 14. Tonnetz (고급)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sr)
            features['tonnetz_mean'] = np.mean(tonnetz)
            features['tonnetz_std'] = np.std(tonnetz)
            
            # 15. Chroma CQT
            chroma_cqt = librosa.feature.chroma_cqt(y=audio_data, sr=sr)
            features['chroma_cqt_mean'] = np.mean(chroma_cqt, axis=1).tolist()
            
        except Exception as e:
            print(f"❌ 고급 특징 추출 오류: {e}")
            # 기본값으로 채우기
            features = {f'feature_{i}': 0.0 for i in range(50)}
        
        return features
    
    # ===== 3. 특징 선택 (Feature Selection) =====
    
    def select_best_features(self, X: np.ndarray, y: np.ndarray, 
                           method: str = 'mutual_info', k: int = 20) -> np.ndarray:
        """
        최적 특징 선택
        
        Args:
            X: 특징 행렬
            y: 레이블
            method: 선택 방법 ('mutual_info', 'f_score', 'variance')
            k: 선택할 특징 수
            
        Returns:
            선택된 특징 인덱스
        """
        if method == 'mutual_info':
            selector = SelectKBest(score_func=mutual_info_classif, k=k)
        elif method == 'f_score':
            selector = SelectKBest(score_func=f_classif, k=k)
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
    
    # ===== 4. 고급 앙상블 방법 =====
    
    def create_advanced_ensemble(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """고급 앙상블 모델 생성"""
        
        # 다양한 모델들
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
            'extra_trees': RandomForestClassifier(
                n_estimators=100, 
                max_depth=10, 
                random_state=42,
                criterion='entropy'
            )
        }
        
        # 각 모델 훈련
        trained_models = {}
        for name, model in models.items():
            model.fit(X, y)
            trained_models[name] = model
            print(f"✅ {name} 모델 훈련 완료")
        
        self.models = trained_models
        return trained_models
    
    def stacking_ensemble_predict(self, X: np.ndarray) -> np.ndarray:
        """스태킹 앙상블 예측"""
        if not self.models:
            raise ValueError("모델이 훈련되지 않았습니다.")
        
        # 1단계: 기본 모델들의 예측
        base_predictions = []
        for name, model in self.models.items():
            pred_proba = model.predict_proba(X)
            base_predictions.append(pred_proba)
        
        # 2단계: 메타 학습기 (간단한 평균)
        meta_features = np.hstack(base_predictions)
        final_prediction = np.mean(meta_features, axis=1)
        
        return final_prediction
    
    # ===== 5. 액티브 학습 (Active Learning) =====
    
    def active_learning_query(self, X: np.ndarray, model, 
                            query_strategy: str = 'uncertainty') -> np.ndarray:
        """
        액티브 학습을 위한 쿼리 샘플 선택
        
        Args:
            X: 특징 행렬
            model: 훈련된 모델
            query_strategy: 쿼리 전략 ('uncertainty', 'diversity', 'random')
            
        Returns:
            선택된 샘플 인덱스
        """
        if query_strategy == 'uncertainty':
            # 불확실성 기반 선택
            pred_proba = model.predict_proba(X)
            uncertainty = 1 - np.max(pred_proba, axis=1)
            query_indices = np.argsort(uncertainty)[-10:]  # 상위 10개
            
        elif query_strategy == 'diversity':
            # 다양성 기반 선택 (클러스터링)
            kmeans = KMeans(n_clusters=10, random_state=42)
            cluster_labels = kmeans.fit_predict(X)
            
            # 각 클러스터에서 하나씩 선택
            query_indices = []
            for cluster_id in range(10):
                cluster_mask = cluster_labels == cluster_id
                if np.any(cluster_mask):
                    cluster_indices = np.where(cluster_mask)[0]
                    query_indices.append(np.random.choice(cluster_indices))
            
        else:  # random
            # 랜덤 선택
            query_indices = np.random.choice(len(X), size=10, replace=False)
        
        return query_indices
    
    # ===== 6. 다중 시간 스케일 분석 =====
    
    def multi_timescale_analysis(self, audio_data: np.ndarray, sr: int) -> Dict[str, Dict]:
        """다중 시간 스케일 분석"""
        
        results = {}
        
        # 단기 분석 (1초)
        short_window = int(1.0 * sr)
        if len(audio_data) >= short_window:
            short_audio = audio_data[:short_window]
            results['short_term'] = self.extract_advanced_features(short_audio, sr)
        
        # 중기 분석 (5초)
        medium_window = int(5.0 * sr)
        if len(audio_data) >= medium_window:
            medium_audio = audio_data[:medium_window]
            results['medium_term'] = self.extract_advanced_features(medium_audio, sr)
        
        # 장기 분석 (전체)
        results['long_term'] = self.extract_advanced_features(audio_data, sr)
        
        # 시간적 변화 분석
        if len(audio_data) >= medium_window:
            # 윈도우별 분석
            window_size = int(1.0 * sr)  # 1초 윈도우
            windows = [audio_data[i:i+window_size] for i in range(0, len(audio_data)-window_size, window_size)]
            
            window_features = []
            for window in windows:
                if len(window) == window_size:
                    features = self.extract_advanced_features(window, sr)
                    window_features.append(features)
            
            if window_features:
                # 시간적 변화 통계
                temporal_stats = {}
                for key in window_features[0].keys():
                    if isinstance(window_features[0][key], (int, float)):
                        values = [f[key] for f in window_features]
                        temporal_stats[f'{key}_temporal_mean'] = np.mean(values)
                        temporal_stats[f'{key}_temporal_std'] = np.std(values)
                        temporal_stats[f'{key}_temporal_trend'] = np.polyfit(range(len(values)), values, 1)[0]
                
                results['temporal_analysis'] = temporal_stats
        
        return results
    
    # ===== 7. 베이지안 최적화 =====
    
    def bayesian_optimization(self, X: np.ndarray, y: np.ndarray, 
                            param_space: Dict) -> Dict:
        """베이지안 최적화 (간단한 그리드 서치)"""
        
        best_score = 0
        best_params = {}
        
        # 간단한 그리드 서치 (실제로는 Gaussian Process 사용)
        for n_estimators in param_space.get('n_estimators', [50, 100, 200]):
            for max_depth in param_space.get('max_depth', [5, 10, 15]):
                for learning_rate in param_space.get('learning_rate', [0.01, 0.1, 0.2]):
                    
                    # 모델 훈련
                    model = GradientBoostingClassifier(
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                        learning_rate=learning_rate,
                        random_state=42
                    )
                    
                    # 교차 검증
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                    model.fit(X_train, y_train)
                    score = model.score(X_test, y_test)
                    
                    if score > best_score:
                        best_score = score
                        best_params = {
                            'n_estimators': n_estimators,
                            'max_depth': max_depth,
                            'learning_rate': learning_rate,
                            'score': score
                        }
        
        return best_params
    
    # ===== 8. 통합 정확도 향상 파이프라인 =====
    
    def comprehensive_improvement_pipeline(self, audio_files: List[str], 
                                         labels: List[int]) -> Dict:
        """종합적인 정확도 향상 파이프라인"""
        
        print("🚀 종합 정확도 향상 파이프라인 시작")
        
        # 1. 데이터 증강
        print("1️⃣ 데이터 증강 중...")
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
        
        # 4. 고급 앙상블
        print("4️⃣ 고급 앙상블 모델 훈련 중...")
        models = self.create_advanced_ensemble(X_selected, y)
        
        # 5. 베이지안 최적화
        print("5️⃣ 하이퍼파라미터 최적화 중...")
        param_space = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15],
            'learning_rate': [0.01, 0.1, 0.2]
        }
        best_params = self.bayesian_optimization(X_selected, y, param_space)
        
        # 6. 최종 모델 훈련
        print("6️⃣ 최종 모델 훈련 중...")
        final_model = GradientBoostingClassifier(**best_params, random_state=42)
        final_model.fit(X_selected, y)
        
        # 7. 성능 평가
        print("7️⃣ 성능 평가 중...")
        X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42)
        final_model.fit(X_train, y_train)
        y_pred = final_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        results = {
            'accuracy': accuracy,
            'best_params': best_params,
            'feature_importance': self.feature_importance,
            'selected_features_count': X_selected.shape[1],
            'total_samples': len(augmented_audio),
            'original_samples': len(audio_files)
        }
        
        print(f"✅ 파이프라인 완료! 정확도: {accuracy:.3f}")
        return results

# 사용 예제
if __name__ == "__main__":
    # 정확도 향상 방법들 테스트
    improver = AccuracyImprovementMethods()
    
    print("🎯 정확도 향상 방법들 테스트")
    print("=" * 50)
    
    # 가상의 테스트 데이터
    test_audio_files = ["test1.wav", "test2.wav", "test3.wav"]
    test_labels = [0, 1, 0]  # 0: 정상, 1: 이상
    
    # 종합 파이프라인 실행
    results = improver.comprehensive_improvement_pipeline(test_audio_files, test_labels)
    
    print("📊 결과:")
    print(f"   정확도: {results['accuracy']:.3f}")
    print(f"   선택된 특징 수: {results['selected_features_count']}")
    print(f"   총 샘플 수: {results['total_samples']}")
    print(f"   원본 샘플 수: {results['original_samples']}")
