#!/usr/bin/env python3
"""
앙상블 AI 서비스
MIMII 모델 + 기존 모델들을 조합한 고성능 앙상블 AI
"""

import os
import numpy as np
import librosa
import joblib
from typing import Dict, List, Optional
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnsembleAIService:
    """앙상블 AI 진단 서비스"""

    def __init__(self, models_dir='data/models', features_dir='data/features'):
        self.models_dir = models_dir
        self.features_dir = features_dir
        self.ensemble_models = {}
        self.ensemble_weights = {}
        self.scalers = {}
        self.feature_importance = None
        self.is_ensemble_loaded = False

        # 앙상블 모델들 로드
        self._load_ensemble_models()

    def _load_ensemble_models(self):
        """앙상블 모델들 로드"""
        try:
            # 1. MIMII 모델 로드 (joblib)
            mimii_model_path = os.path.join(self.models_dir, 'mimii_model.pkl')
            mimii_scaler_path = os.path.join(self.models_dir, 'mimii_scaler.pkl')

            # MIMII 모델은 기존의 RandomForest 모델로 가정
            if os.path.exists(mimii_model_path) and os.path.exists(mimii_scaler_path):
                self.ensemble_models['mimii_rf'] = joblib.load(mimii_model_path)
                self.scalers['mimii_rf'] = joblib.load(mimii_scaler_path)
                self.ensemble_weights['mimii_rf'] = 0.4
                logger.info("MIMII (RandomForest) 모델 로드 성공!")
            else:
                logger.warning("MIMII 모델 파일을 찾을 수 없습니다. (mimii_model.pkl, mimii_scaler.pkl)")

            # 2. 추가 모델들 생성 및 로드
            self._create_optimized_models()

            # 3. 특성 중요도 로드
            feature_importance_path = os.path.join(self.features_dir, 'mimii_feature_importance.csv')
            if os.path.exists(feature_importance_path):
                self.feature_importance = pd.read_csv(feature_importance_path)
                logger.info("특성 중요도 로드 성공!")

            self.is_ensemble_loaded = len(self.ensemble_models) > 0
            logger.info(f"앙상블 모델 로드 완료: {len(self.ensemble_models)}개 모델")

        except Exception as e:
            logger.error(f"앙상블 모델 로드 실패: {e}")
            self.is_ensemble_loaded = False

    def _create_optimized_models(self):
        """가공된 특성에 최적화된 추가 모델들 생성"""
        try:
            # RandomForest
            self.ensemble_models['random_forest'] = RandomForestClassifier(
                n_estimators=100, max_depth=20, min_samples_split=5, min_samples_leaf=2, random_state=42
            )
            self.ensemble_weights['random_forest'] = 0.25

            # SVM
            self.ensemble_models['svm'] = SVC(
                kernel='rbf', C=1.0, gamma='scale', probability=True, random_state=42
            )
            self.ensemble_weights['svm'] = 0.15

            # MLP
            self.ensemble_models['mlp'] = MLPClassifier(
                hidden_layer_sizes=(100, 50), activation='relu', solver='adam', alpha=0.001,
                learning_rate='adaptive', max_iter=1000, random_state=42
            )
            self.ensemble_weights['mlp'] = 0.1

            # Logistic Regression
            self.ensemble_models['logistic'] = LogisticRegression(
                C=1.0, max_iter=1000, random_state=42
            )
            self.ensemble_weights['logistic'] = 0.1

            # 가중치 정규화
            total_weight = sum(self.ensemble_weights.values())
            if total_weight > 0:
                for model_name in self.ensemble_weights:
                    self.ensemble_weights[model_name] /= total_weight

            logger.info("최적화된 추가 모델들 생성 완료!")

        except Exception as e:
            logger.error(f"추가 모델 생성 실패: {e}")

    def extract_comprehensive_features(self, audio_file_path: str) -> Optional[np.ndarray]:
        """포괄적인 오디오 특성 추출 (앙상블용)"""
        try:
            y, sr = librosa.load(audio_file_path, sr=16000) # sr을 16000으로 통일
            features = []

            # 주요 특징들을 미리 계산
            rms = librosa.feature.rms(y=y)[0]
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            fft_magnitude = np.abs(np.fft.fft(y))
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            tonnetz = librosa.feature.tonnetz(y=y, sr=sr)
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            stft = librosa.stft(y)
            freqs = librosa.fft_frequencies(sr=sr)

            # 통계적 특징 추출
            features.extend([np.mean(rms), np.std(rms), np.max(rms), np.min(rms)])
            features.extend([np.mean(zcr), np.std(zcr), np.max(zcr), np.min(zcr)])
            features.extend([np.mean(spectral_centroid), np.std(spectral_centroid), np.max(spectral_centroid), np.min(spectral_centroid)])
            features.extend([np.mean(spectral_rolloff), np.std(spectral_rolloff), np.max(spectral_rolloff), np.min(spectral_rolloff)])
            features.extend([np.mean(spectral_bandwidth), np.std(spectral_bandwidth), np.max(spectral_bandwidth), np.min(spectral_bandwidth)])
            features.append(tempo)

            for i in range(13):
                features.extend([np.mean(mfccs[i]), np.std(mfccs[i]), np.max(mfccs[i]), np.min(mfccs[i])])

            features.extend([np.mean(fft_magnitude), np.std(fft_magnitude), np.max(fft_magnitude), np.min(fft_magnitude)])

            for i in range(12):
                features.extend([np.mean(chroma[i]), np.std(chroma[i])])

            for i in range(6):
                features.extend([np.mean(tonnetz[i]), np.std(tonnetz[i])])

            for i in range(7):
                features.extend([np.mean(spectral_contrast[i]), np.std(spectral_contrast[i])])

            # 냉매 누수 및 과부하 특성
            leak_freq_range = (2000, 8000)
            leak_indices = np.where((freqs >= leak_freq_range[0]) & (freqs <= leak_freq_range[1]))[0]
            if len(leak_indices) > 0:
                leak_energy = np.sum(np.abs(stft[leak_indices, :]))
                features.extend([np.mean(leak_energy), np.std(leak_energy), np.max(leak_energy), np.min(leak_energy)])
            else:
                features.extend([0, 0, 0, 0])

            overload_freq_range = (50, 500)
            overload_indices = np.where((freqs >= overload_freq_range[0]) & (freqs <= overload_freq_range[1]))[0]
            if len(overload_indices) > 0:
                overload_energy = np.sum(np.abs(stft[overload_indices, :]))
                features.extend([np.mean(overload_energy), np.std(overload_energy), np.max(overload_energy), np.min(overload_energy)])
            else:
                features.extend([0, 0, 0, 0])

            return np.array(features)

        except Exception as e:
            logger.error(f"특성 추출 오류: {e}")
            return None

    def predict_ensemble(self, audio_file_path: str) -> Optional[Dict]:
        """앙상블 모델로 예측"""
        if not self.is_ensemble_loaded:
            logger.warning("앙상블 모델이 로드되지 않았습니다. 예측을 수행할 수 없습니다.")
            return None

        try:
            # 특성 추출
            features = self.extract_comprehensive_features(audio_file_path)
            if features is None:
                return None

            # 각 모델별 예측
            predictions = {}
            probabilities = {}

            # 모든 모델에 대해 동일한 특성 배열 사용
            for model_name, model in self.ensemble_models.items():
                try:
                    # MIMII 모델은 스케일러가 필요
                    if model_name == 'mimii_rf' and 'mimii_rf' in self.scalers:
                        features_scaled = self.scalers['mimii_rf'].transform(features.reshape(1, -1))
                    else:
                        features_scaled = features.reshape(1, -1)

                    pred = model.predict(features_scaled)[0]
                    
                    # predict_proba가 없는 경우 예외 처리
                    if hasattr(model, 'predict_proba'):
                        prob = model.predict_proba(features_scaled)[0]
                        probability = float(max(prob))
                    else:
                        probability = 0.5 # 임시 값

                    predictions[model_name] = int(pred)
                    probabilities[model_name] = probability

                except Exception as e:
                    logger.warning(f"{model_name} 모델 예측 실패: {e}")
                    continue

            # 앙상블 예측 (가중 평균)
            if not predictions:
                logger.error("예측 가능한 모델이 없습니다.")
                return None

            ensemble_prediction = 0
            ensemble_probability = 0
            total_weight = sum(self.ensemble_weights.values())

            for model_name, pred in predictions.items():
                weight = self.ensemble_weights.get(model_name, 0)
                ensemble_prediction += pred * weight
                ensemble_probability += probabilities.get(model_name, 0) * weight

            if total_weight > 0:
                ensemble_prediction = int(round(ensemble_prediction / total_weight))
                ensemble_probability /= total_weight
            else:
                logger.warning("가중치 총합이 0입니다. 기본값 반환.")
                return None

            result = {
                'prediction': ensemble_prediction,
                'probability': ensemble_probability,
                'confidence': 'high' if ensemble_probability > 0.8 else 'medium' if ensemble_probability > 0.6 else 'low',
                'model_type': 'Ensemble',
                'models_used': list(predictions.keys()),
                'individual_predictions': predictions,
                'individual_probabilities': probabilities,
                'ensemble_weights': self.ensemble_weights,
                'features_used': len(features),
                'is_anomaly': ensemble_prediction == 1
            }

            return result

        except Exception as e:
            logger.error(f"앙상블 예측 오류: {e}")
            return None

    def get_ensemble_info(self) -> Dict:
        """앙상블 모델 정보 반환"""
        info = {
            'ensemble_loaded': self.is_ensemble_loaded,
            'models_count': len(self.ensemble_models),
            'models_dir': self.models_dir,
            'features_dir': self.features_dir,
            'models': list(self.ensemble_models.keys()),
            'weights': self.ensemble_weights
        }

        if self.feature_importance is not None:
            info['feature_importance_available'] = True
            info['top_features'] = self.feature_importance.head(10).to_dict('records')

        return info

# 전역 앙상블 AI 서비스 인스턴스
ensemble_ai_service = EnsembleAIService()
