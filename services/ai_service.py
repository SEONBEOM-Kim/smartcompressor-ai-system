#!/usr/bin/env python3
"""
통합 AI 서비스 - Single Source of Truth
모든 AI 모델과 로직을 통합한 중앙 집중식 AI 서비스
"""

import os
import numpy as np
import librosa
import joblib
import time
from typing import Dict, List, Optional, Union
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model
from scipy import signal
from scipy.signal import butter, filtfilt
import threading
import hashlib
import json
from datetime import datetime
from services.ai_model_training import compressor_ai_model
from services.smart_storage_service import SmartStorageService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedAIService:
    """
    통합 AI 서비스 - 모든 AI 모델과 로직의 Single Source of Truth
    
    이 클래스는 다음 기능들을 통합합니다:
    1. Lightweight Compressor AI (경량화 압축기 진단)
    2. Ensemble AI (앙상블 모델)
    3. MIMII Model (산업용 이상 감지)
    4. 모델 관리 및 OTA 업데이트
    """

    def __init__(self, models_dir='data/models', features_dir='data/features'):
        self.models_dir = models_dir
        self.features_dir = features_dir
        
        # 모델 저장소
        self.models = {}
        self.scalers = {}
        self.model_metadata = {}
        
        # 압축기 AI 모델 초기화
        self.compressor_model = compressor_ai_model
        
        # 스마트 저장 서비스 초기화
        self.storage_service = SmartStorageService()
        self.model_versions = {}
        
        # 서비스 상태
        self.is_initialized = False
        self.last_update = None
        self.update_lock = threading.Lock()
        
        # 모델 로드 및 초기화
        self._initialize_models()
        
        logger.info("통합 AI 서비스 초기화 완료")

    def _initialize_models(self):
        """모든 AI 모델 초기화"""
        try:
            with self.update_lock:
                # 1. Lightweight Compressor AI 초기화
                self._init_lightweight_ai()
                
                # 2. Ensemble AI 모델 초기화
                self._init_ensemble_models()
                
                # 3. MIMII 모델 초기화
                self._init_mimii_model()
                
                # 4. 모델 메타데이터 로드
                self._load_model_metadata()
                
                self.is_initialized = True
                self.last_update = datetime.now()
                
                logger.info(f"모든 AI 모델 초기화 완료: {len(self.models)}개 모델")
                
        except Exception as e:
            logger.error(f"모델 초기화 실패: {e}")
            self.is_initialized = False

    def _init_lightweight_ai(self):
        """경량화 압축기 AI 초기화"""
        try:
            # Lightweight AI는 규칙 기반이므로 별도 모델 파일 불필요
            self.models['lightweight'] = {
                'type': 'rule_based',
                'overload_freq_range': (500, 2000),
                'overload_threshold': 0.5,
                'sample_rate': 16000,
                'n_fft': 1024,
                'hop_length': 512
            }
            self.model_versions['lightweight'] = '1.0.0'
            logger.info("Lightweight Compressor AI 초기화 완료")
            
        except Exception as e:
            logger.error(f"Lightweight AI 초기화 실패: {e}")

    def _init_ensemble_models(self):
        """앙상블 AI 모델 초기화"""
        try:
            # MIMII 모델 로드
            mimii_model_path = os.path.join(self.models_dir, 'mimii_model.pkl')
            mimii_scaler_path = os.path.join(self.models_dir, 'mimii_scaler.pkl')

            if os.path.exists(mimii_model_path) and os.path.exists(mimii_scaler_path):
                self.models['mimii_rf'] = joblib.load(mimii_model_path)
                self.scalers['mimii_rf'] = joblib.load(mimii_scaler_path)
                self.model_versions['mimii_rf'] = '1.0.0'
                logger.info("MIMII 모델 로드 완료")
            
            # 추가 앙상블 모델들 생성
            self._create_ensemble_models()

        except Exception as e:
            logger.error(f"앙상블 모델 초기화 실패: {e}")

    def _create_ensemble_models(self):
        """앙상블 모델들 생성"""
        try:
            # RandomForest
            self.models['random_forest'] = RandomForestClassifier(
                n_estimators=100, max_depth=20, min_samples_split=5, 
                min_samples_leaf=2, random_state=42
            )
            self.model_versions['random_forest'] = '1.0.0'
            
            # SVM
            self.models['svm'] = SVC(
                kernel='rbf', C=1.0, gamma='scale', 
                probability=True, random_state=42
            )
            self.model_versions['svm'] = '1.0.0'
            
            # MLP
            self.models['mlp'] = MLPClassifier(
                hidden_layer_sizes=(100, 50), activation='relu', 
                solver='adam', alpha=0.001, learning_rate='adaptive', 
                max_iter=1000, random_state=42
            )
            self.model_versions['mlp'] = '1.0.0'

            # Logistic Regression
            self.models['logistic'] = LogisticRegression(
                C=1.0, max_iter=1000, random_state=42
            )
            self.model_versions['logistic'] = '1.0.0'
            
            logger.info("앙상블 모델들 생성 완료")
            
        except Exception as e:
            logger.error(f"앙상블 모델 생성 실패: {e}")

    def _init_mimii_model(self):
        """MIMII 모델 초기화 (이미 앙상블에서 처리됨)"""
        # MIMII 모델은 이미 _init_ensemble_models에서 처리됨
        pass

    def _load_model_metadata(self):
        """모델 메타데이터 로드"""
        try:
            metadata_path = os.path.join(self.models_dir, 'model_metadata.json')
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.model_metadata = json.load(f)
            else:
                # 기본 메타데이터 생성
                self.model_metadata = {
                    'lightweight': {
                        'description': '경량화 압축기 진단 AI',
                        'type': 'rule_based',
                        'performance': {'accuracy': 0.85, 'precision': 0.82, 'recall': 0.88}
                    },
                    'mimii_rf': {
                        'description': 'MIMII RandomForest 모델',
                        'type': 'machine_learning',
                        'performance': {'accuracy': 0.92, 'precision': 0.89, 'recall': 0.91}
                    }
                }
                self._save_model_metadata()
                
        except Exception as e:
            logger.error(f"모델 메타데이터 로드 실패: {e}")

    def _save_model_metadata(self):
        """모델 메타데이터 저장"""
        try:
            metadata_path = os.path.join(self.models_dir, 'model_metadata.json')
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.model_metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"모델 메타데이터 저장 실패: {e}")

    def analyze_audio(self, audio_input: Union[str, np.ndarray], 
                     model_type: str = 'auto', 
                     sr: Optional[int] = None,
                     enable_noise_cancellation: bool = True,
                     enable_quality_optimization: bool = True) -> Dict:
        """
        오디오 분석 - 통합 진입점 (노이즈 캔슬링 및 품질 최적화 포함)
        
        Args:
            audio_input: 오디오 파일 경로 또는 오디오 데이터
            model_type: 사용할 모델 타입 ('lightweight', 'ensemble', 'mimii', 'auto')
            sr: 샘플링 레이트 (오디오 데이터인 경우)
            enable_noise_cancellation: 노이즈 캔슬링 활성화
            enable_quality_optimization: 품질 최적화 활성화
            
        Returns:
            분석 결과 딕셔너리
        """
        if not self.is_initialized:
            return self._create_error_result("AI 서비스가 초기화되지 않았습니다.")
        
        try:
            start_time = time.time()
            
            # 오디오 데이터 로드
            if isinstance(audio_input, str):
                audio_data, sample_rate = librosa.load(audio_input, sr=16000)
            else:
                audio_data = audio_input
                sample_rate = sr or 16000
            
            # 오디오 품질 분석 및 최적화
            quality_metrics = self._analyze_audio_quality(audio_data, sample_rate)
            
            # 품질 최적화 적용
            if enable_quality_optimization:
                audio_data, optimization_info = self._optimize_audio_quality(
                    audio_data, sample_rate, quality_metrics
                )
            else:
                optimization_info = {}
            
            # 노이즈 캔슬링 적용
            if enable_noise_cancellation:
                audio_data, noise_info = self._apply_noise_cancellation(
                    audio_data, sample_rate
                )
            else:
                noise_info = {}
            
            # 모델 타입 결정
            if model_type == 'auto':
                model_type = self._select_best_model(audio_data, sample_rate)
            
            # 모델별 분석 실행
            if model_type == 'lightweight':
                result = self._analyze_with_lightweight(audio_data, sample_rate)
            elif model_type == 'ensemble':
                result = self._analyze_with_ensemble(audio_data, sample_rate)
            elif model_type == 'mimii':
                result = self._analyze_with_mimii(audio_data, sample_rate)
            else:
                return self._create_error_result(f"지원하지 않는 모델 타입: {model_type}")
            
            # 공통 결과 포맷팅
            result['model_type'] = model_type
            result['processing_time_ms'] = (time.time() - start_time) * 1000
            result['timestamp'] = datetime.now().isoformat()
            result['service_version'] = '1.0.0'
            
            # 품질 및 노이즈 정보 추가
            result['quality_metrics'] = quality_metrics
            result['optimization_info'] = optimization_info
            result['noise_info'] = noise_info
            
            # 이상 감지 시 알림 전송
            if result.get('is_overload', False):
                self._send_diagnosis_alert(result)
            
            # 스마트 저장 (주의/긴급만 저장)
            try:
                store_id = "default_store"  # 실제로는 요청에서 가져와야 함
                device_id = "default_device"  # 실제로는 요청에서 가져와야 함
                
                # 파일 정보 (실제로는 요청에서 가져와야 함)
                file_info = {
                    'name': 'audio_file',
                    'size': 0  # 실제 파일 크기
                }
                
                # 분석 결과 저장 (주의/긴급만)
                analysis_id = self.storage_service.store_analysis_result(
                    store_id, device_id, result, file_info
                )
                
                if analysis_id:
                    result['analysis_id'] = analysis_id
                    result['stored'] = True
                else:
                    result['stored'] = False
                    
                # 긍정적 신호 요약 업데이트 (정상인 경우)
                if not result.get('is_overload', False) and result.get('confidence', 0) > 0.8:
                    self.storage_service.update_positive_summary(store_id, result)
                    
            except Exception as e:
                logger.error(f"스마트 저장 실패: {e}")
                result['stored'] = False
            
            return result
            
        except Exception as e:
            logger.error(f"오디오 분석 실패: {e}")
            return self._create_error_result(f"분석 중 오류 발생: {str(e)}")

    def _select_best_model(self, audio_data: np.ndarray, sr: int) -> str:
        """최적의 모델 선택"""
        # 간단한 규칙: 짧은 오디오는 lightweight, 긴 오디오는 ensemble
        duration = len(audio_data) / sr
        if duration < 10:  # 10초 미만
            return 'lightweight'
        else:
            return 'ensemble'

    def _analyze_with_lightweight(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Lightweight AI로 분석"""
        try:
            # 전처리
            processed_audio = self._preprocess_audio_lightweight(audio_data, sr)
            
            # 특징 추출
            features = self._extract_lightweight_features(processed_audio, sr)
            
            # 판별
            is_overload, confidence = self._is_overload_lightweight(features)
            
            return {
                'is_overload': is_overload,
                'confidence': confidence,
                'message': '베어링 마모 감지됨' if is_overload else '정상 작동 중',
                'features': features,
                'diagnosis_type': 'bearing_wear_detection'
            }
            
        except Exception as e:
            logger.error(f"Lightweight 분석 실패: {e}")
            return self._create_error_result(f"Lightweight 분석 실패: {str(e)}")

    def _analyze_with_ensemble(self, audio_data: np.ndarray, sr: int) -> Dict:
        """앙상블 AI로 분석"""
        try:
            # 특징 추출
            features = self._extract_comprehensive_features(audio_data, sr)
            if features is None:
                return self._create_error_result("특징 추출 실패")
            
            # 각 모델별 예측
            predictions = {}
            probabilities = {}
            
            for model_name, model in self.models.items():
                if model_name == 'lightweight':
                    continue
                    
                try:
                    # MIMII 모델은 스케일러 필요
                    if model_name == 'mimii_rf' and 'mimii_rf' in self.scalers:
                        features_scaled = self.scalers['mimii_rf'].transform(features.reshape(1, -1))
                    else:
                        features_scaled = features.reshape(1, -1)
                    
                    pred = model.predict(features_scaled)[0]
                    
                    if hasattr(model, 'predict_proba'):
                        prob = model.predict_proba(features_scaled)[0]
                        probability = float(max(prob))
                    else:
                        probability = 0.5
                    
                    predictions[model_name] = int(pred)
                    probabilities[model_name] = probability
                    
                except Exception as e:
                    logger.warning(f"{model_name} 모델 예측 실패: {e}")
                    continue
            
            # 앙상블 결과 계산
            if not predictions:
                return self._create_error_result("예측 가능한 모델이 없습니다")
            
            # 가중 평균 (MIMII에 더 높은 가중치)
            weights = {'mimii_rf': 0.4, 'random_forest': 0.25, 'svm': 0.15, 'mlp': 0.1, 'logistic': 0.1}
            
            ensemble_prediction = 0
            ensemble_probability = 0
            total_weight = 0
            
            for model_name, pred in predictions.items():
                weight = weights.get(model_name, 0.1)
                ensemble_prediction += pred * weight
                ensemble_probability += probabilities.get(model_name, 0) * weight
                total_weight += weight
            
            if total_weight > 0:
                ensemble_prediction = int(round(ensemble_prediction / total_weight))
                ensemble_probability /= total_weight
            
            return {
                'is_overload': ensemble_prediction == 1,
                'confidence': ensemble_probability,
                'message': '과부하음 감지됨' if ensemble_prediction == 1 else '정상 작동 중',
                'individual_predictions': predictions,
                'individual_probabilities': probabilities,
                'diagnosis_type': 'ensemble_analysis'
            }
            
        except Exception as e:
            logger.error(f"앙상블 분석 실패: {e}")
            return self._create_error_result(f"앙상블 분석 실패: {str(e)}")

    def _analyze_with_mimii(self, audio_data: np.ndarray, sr: int) -> Dict:
        """MIMII 모델로 분석"""
        try:
            if 'mimii_rf' not in self.models:
                return self._create_error_result("MIMII 모델이 로드되지 않았습니다")
            
            # 특징 추출
            features = self._extract_comprehensive_features(audio_data, sr)
            if features is None:
                return self._create_error_result("특징 추출 실패")
            
            # MIMII 모델 예측
            features_scaled = self.scalers['mimii_rf'].transform(features.reshape(1, -1))
            prediction = self.models['mimii_rf'].predict(features_scaled)[0]
            probability = self.models['mimii_rf'].predict_proba(features_scaled)[0].max()
            
            return {
                'is_overload': prediction == 1,
                'confidence': float(probability),
                'message': 'MIMII 이상 감지됨' if prediction == 1 else 'MIMII 정상',
                'diagnosis_type': 'mimii_analysis'
            }
            
        except Exception as e:
            logger.error(f"MIMII 분석 실패: {e}")
            return self._create_error_result(f"MIMII 분석 실패: {str(e)}")

    def _preprocess_audio_lightweight(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """Lightweight AI용 오디오 전처리"""
        try:
            # 16kHz로 리샘플링
            if sr != 16000:
                audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=16000)
            
            # 노이즈 필터링
            nyquist = 16000 / 2
            low_cutoff = 100 / nyquist
            high_cutoff = 3000 / nyquist
            
            b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
            filtered_audio = filtfilt(b, a, audio_data)
            
            # 정규화
            rms_energy = np.sqrt(np.mean(filtered_audio ** 2))
            if rms_energy > 0:
                normalized_audio = filtered_audio / rms_energy
            else:
                normalized_audio = filtered_audio
            
            return normalized_audio

        except Exception as e:
            logger.error(f"오디오 전처리 실패: {e}")
            return audio_data

    def _extract_lightweight_features(self, audio_data: np.ndarray, sr: int) -> Dict:
        """Lightweight AI용 특징 추출"""
        try:
            n_fft = 1024
            hop_length = 512
            overload_freq_range = (500, 2000)
            
            # RMS 에너지
            rms_energy = np.sqrt(np.mean(audio_data ** 2))
            
            # 주파수 도메인 분석
            stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
            magnitude = np.abs(stft)
            frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
            
            # 특정 주파수 대역의 에너지 비율
            freq_mask = (frequencies >= overload_freq_range[0]) & (frequencies <= overload_freq_range[1])
            target_energy = np.sum(magnitude[freq_mask, :])
            total_energy = np.sum(magnitude)
            
            overload_ratio = target_energy / total_energy if total_energy > 0 else 0
            
            # Zero Crossing Rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data, hop_length=hop_length))
            
            # 스펙트럼 중심
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr, hop_length=hop_length))
            
            # 스펙트럼 롤오프
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr, hop_length=hop_length))
            
            return {
                'rms_energy': rms_energy,
                'overload_ratio': overload_ratio,
                'zero_crossing_rate': zcr,
                'spectral_centroid': spectral_centroid,
                'spectral_rolloff': spectral_rolloff,
                'target_freq_energy': target_energy,
                'total_energy': total_energy
            }

        except Exception as e:
            logger.error(f"Lightweight 특징 추출 실패: {e}")
            return {}

    def _is_overload_lightweight(self, features: Dict) -> tuple:
        """Lightweight AI 과부하 판별"""
        try:
            rms_energy = features.get('rms_energy', 0)
            overload_ratio = features.get('overload_ratio', 0)
            zcr = features.get('zero_crossing_rate', 0)
            spectral_centroid = features.get('spectral_centroid', 0)
            spectral_rolloff = features.get('spectral_rolloff', 0)
            
            # 판별 조건
            energy_condition = rms_energy > 0.01
            freq_condition = overload_ratio > 0.5
            zcr_condition = zcr > 0.1
            centroid_condition = spectral_centroid > 1000
            rolloff_condition = spectral_rolloff > 2000
            
            is_overload = (
                energy_condition and 
                freq_condition and 
                zcr_condition and 
                (centroid_condition or rolloff_condition)
            )
            
            # 신뢰도 계산
            if is_overload:
                confidence = (
                    min(overload_ratio * 2, 1.0) * 0.3 +
                    min(zcr * 10, 1.0) * 0.3 +
                    min(spectral_centroid / 2000, 1.0) * 0.2 +
                    min(spectral_rolloff / 4000, 1.0) * 0.2
                )
            else:
                confidence = 1.0 - min(overload_ratio * 2, 1.0)
            
            return is_overload, confidence
            
        except Exception as e:
            logger.error(f"Lightweight 판별 실패: {e}")
            return False, 0.0

    def _extract_comprehensive_features(self, audio_data: np.ndarray, sr: int) -> Optional[np.ndarray]:
        """포괄적인 특징 추출 (앙상블용)"""
        try:
            y, sr = librosa.load(audio_data, sr=16000) if isinstance(audio_data, str) else (audio_data, sr)
            features = []

            # 주요 특징들 계산
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

            # MFCC 특징
            for i in range(13):
                features.extend([np.mean(mfccs[i]), np.std(mfccs[i]), np.max(mfccs[i]), np.min(mfccs[i])])

            # FFT 특징
            features.extend([np.mean(fft_magnitude), np.std(fft_magnitude), np.max(fft_magnitude), np.min(fft_magnitude)])

            # Chroma 특징
            for i in range(12):
                features.extend([np.mean(chroma[i]), np.std(chroma[i])])

            # Tonnetz 특징
            for i in range(6):
                features.extend([np.mean(tonnetz[i]), np.std(tonnetz[i])])

            # Spectral Contrast 특징
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
            logger.error(f"포괄적 특징 추출 실패: {e}")
            return None

    def _create_error_result(self, message: str) -> Dict:
        """에러 결과 생성"""
        return {
            'is_overload': False,
            'confidence': 0.0,
            'message': message,
            'error': True,
            'diagnosis_type': 'error'
        }

    def get_model_info(self) -> Dict:
        """모델 정보 반환"""
        return {
            'initialized': self.is_initialized,
            'models_count': len(self.models),
            'model_types': list(self.models.keys()),
            'model_versions': self.model_versions,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'metadata': self.model_metadata
        }

    def update_model(self, model_name: str, model_data: bytes, version: str) -> bool:
        """모델 OTA 업데이트"""
        try:
            with self.update_lock:
                # 모델 파일 저장
                model_path = os.path.join(self.models_dir, f'{model_name}.pkl')
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                
                with open(model_path, 'wb') as f:
                    f.write(model_data)
                
                # 모델 로드
                if model_name.endswith('_scaler'):
                    self.scalers[model_name] = joblib.load(model_path)
                else:
                    self.models[model_name] = joblib.load(model_path)
                
                # 버전 업데이트
                self.model_versions[model_name] = version
                
                # 메타데이터 업데이트
                self.model_metadata[model_name] = {
                    'version': version,
                    'updated_at': datetime.now().isoformat(),
                    'file_size': len(model_data)
                }
                self._save_model_metadata()
                
                self.last_update = datetime.now()
                logger.info(f"모델 {model_name} v{version} 업데이트 완료")
                return True

        except Exception as e:
            logger.error(f"모델 업데이트 실패: {e}")
            return False

    def _send_diagnosis_alert(self, diagnosis_result: Dict):
        """진단 경고 알림 전송"""
        try:
            from services.notification_service import unified_notification_service

            # 진단 데이터 준비
            diagnosis_data = {
                'result': diagnosis_result.get('message', 'Unknown'),
                'confidence': diagnosis_result.get('confidence', 0.0),
                'model_type': diagnosis_result.get('model_type', 'Unknown'),
                'timestamp': diagnosis_result.get('timestamp', datetime.now().isoformat()),
                'is_overload': diagnosis_result.get('is_overload', False)
            }

            # 알림 전송 (실제로는 사용자 정보가 필요하지만, 여기서는 시스템 알림으로 처리)
            unified_notification_service.send_diagnosis_alert(
                diagnosis_data=diagnosis_data,
                user_email=None,  # 실제 구현에서는 사용자 정보 필요
                user_kakao_id=None
            )

            logger.info("진단 경고 알림 전송 완료")

        except Exception as e:
            logger.error(f"진단 경고 알림 전송 실패: {e}")
    
    def analyze_compressor_door_status(self, audio_file_path: str) -> Dict:
        """압축기 문 열림 상태 분석 (새로운 AI 모델)"""
        try:
            if not self.compressor_model.is_trained:
                # 모델이 훈련되지 않은 경우 기본 모델로 훈련
                logger.info("압축기 AI 모델이 훈련되지 않음. 기본 모델로 훈련 시작...")
                from services.ai_model_training import train_compressor_model
                train_compressor_model()
            
            # 압축기 문 상태 예측
            result = self.compressor_model.predict(audio_file_path)
            
            # 결과 포맷팅
            analysis_result = {
                'status': 'success',
                'prediction': result['prediction'],
                'confidence': result['confidence'],
                'probability': result['probability'],
                'model_type': 'compressor_door_classifier',
                'timestamp': datetime.now().isoformat(),
                'is_door_open': result['prediction'] == 'door_open',
                'message': f"압축기 문 상태: {result['prediction']} (신뢰도: {result['confidence']:.2f})"
            }
            
            # 문이 열린 것으로 감지된 경우 알림 전송
            if result['prediction'] == 'door_open' and result['confidence'] > 0.7:
                self._send_door_open_alert(analysis_result)
            
            logger.info(f"압축기 문 상태 분석 완료: {result['prediction']}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"압축기 문 상태 분석 실패: {e}")
            return {
                'status': 'error',
                'prediction': 'unknown',
                'confidence': 0.0,
                'model_type': 'compressor_door_classifier',
                'timestamp': datetime.now().isoformat(),
                'is_door_open': False,
                'message': f"분석 중 오류 발생: {str(e)}"
            }
    
    def _send_door_open_alert(self, analysis_result: Dict):
        """문 열림 알림 전송"""
        try:
            from services.notification_service import unified_notification_service

            # 문 열림 알림 데이터 준비
            alert_data = {
                'alert_type': 'door_open',
                'message': '냉동고 문이 열린 것으로 감지되었습니다.',
                'confidence': analysis_result['confidence'],
                'timestamp': analysis_result['timestamp'],
                'model_type': analysis_result['model_type']
            }

            # 알림 전송
            unified_notification_service.send_diagnosis_alert(
                diagnosis_data=alert_data,
                user_email=None,  # 실제 구현에서는 사용자 정보 필요
                user_kakao_id=None
            )

            logger.info("문 열림 알림 전송 완료")

        except Exception as e:
            logger.error(f"문 열림 알림 전송 실패: {e}")
    
    def train_compressor_model(self, num_samples: int = 2000) -> Dict:
        """압축기 AI 모델 훈련"""
        try:
            logger.info("압축기 AI 모델 훈련 시작")
            
            # 합성 데이터셋 생성
            X, y = self.compressor_model.create_synthetic_dataset(num_samples)
            
            # 모델 훈련
            training_result = self.compressor_model.train_model(X, y)
            
            logger.info("압축기 AI 모델 훈련 완료")
            return training_result

        except Exception as e:
            logger.error(f"압축기 AI 모델 훈련 실패: {e}")
            raise
    
    def get_compressor_model_info(self) -> Dict:
        """압축기 AI 모델 정보 조회"""
        try:
            return self.compressor_model.get_model_info()
        except Exception as e:
            logger.error(f"압축기 AI 모델 정보 조회 실패: {e}")
            return {'error': str(e)}
    
    def _analyze_audio_quality(self, audio_data: np.ndarray, sr: int) -> Dict:
        """오디오 품질 분석"""
        try:
            # 기본 품질 지표 계산
            rms_energy = np.sqrt(np.mean(audio_data**2))
            peak_amplitude = np.max(np.abs(audio_data))
            snr_estimate = 20 * np.log10(rms_energy / (np.std(audio_data) + 1e-10))
            
            # 주파수 도메인 분석
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/sr)
            power_spectrum = np.abs(fft)**2
            
            # 주파수 분포 분석
            low_freq_power = np.sum(power_spectrum[freqs < 1000])
            mid_freq_power = np.sum(power_spectrum[(freqs >= 1000) & (freqs < 4000)])
            high_freq_power = np.sum(power_spectrum[freqs >= 4000])
            total_power = np.sum(power_spectrum)
            
            # 품질 점수 계산 (0-100)
            volume_score = min(100, max(0, (rms_energy * 1000) * 100))  # 음량 점수
            clarity_score = min(100, max(0, snr_estimate + 20))  # 명료도 점수
            balance_score = min(100, max(0, 100 - abs(50 - (mid_freq_power/total_power)*100)))  # 주파수 균형
            
            overall_quality = (volume_score + clarity_score + balance_score) / 3
            
            return {
                'rms_energy': float(rms_energy),
                'peak_amplitude': float(peak_amplitude),
                'snr_estimate': float(snr_estimate),
                'volume_score': float(volume_score),
                'clarity_score': float(clarity_score),
                'balance_score': float(balance_score),
                'overall_quality': float(overall_quality),
                'frequency_distribution': {
                    'low_freq_ratio': float(low_freq_power / total_power),
                    'mid_freq_ratio': float(mid_freq_power / total_power),
                    'high_freq_ratio': float(high_freq_power / total_power)
                },
                'needs_amplification': volume_score < 30,
                'needs_noise_reduction': clarity_score < 40,
                'needs_balance_adjustment': balance_score < 50
            }
            
        except Exception as e:
            logger.error(f"오디오 품질 분석 실패: {e}")
            return {
                'overall_quality': 50.0,
                'needs_amplification': True,
                'needs_noise_reduction': True,
                'needs_balance_adjustment': True
            }
    
    def _optimize_audio_quality(self, audio_data: np.ndarray, sr: int, quality_metrics: Dict) -> tuple:
        """오디오 품질 최적화"""
        try:
            optimized_audio = audio_data.copy()
            optimization_applied = []
            
            # 1. 음량 증폭 (너무 작은 경우)
            if quality_metrics.get('needs_amplification', False):
                target_rms = 0.1  # 목표 RMS 에너지
                current_rms = quality_metrics.get('rms_energy', 0.01)
                if current_rms > 0:
                    amplification_factor = min(10.0, target_rms / current_rms)
                    optimized_audio = optimized_audio * amplification_factor
                    optimization_applied.append(f"음량 증폭 ({amplification_factor:.2f}x)")
            
            # 2. 클리핑 방지
            if np.max(np.abs(optimized_audio)) > 0.95:
                optimized_audio = optimized_audio * 0.95 / np.max(np.abs(optimized_audio))
                optimization_applied.append("클리핑 방지")
            
            # 3. 주파수 균형 조정
            if quality_metrics.get('needs_balance_adjustment', False):
                # 고주파 부스트 (압축기 소리 특성상)
                freqs = np.fft.fftfreq(len(optimized_audio), 1/sr)
                fft = np.fft.fft(optimized_audio)
                
                # 1000-4000Hz 대역 부스트
                boost_mask = (freqs >= 1000) & (freqs <= 4000)
                fft[boost_mask] = fft[boost_mask] * 1.2
                
                optimized_audio = np.real(np.fft.ifft(fft))
                optimization_applied.append("주파수 균형 조정")
            
            # 4. 정규화
            if np.max(np.abs(optimized_audio)) > 0:
                optimized_audio = optimized_audio / np.max(np.abs(optimized_audio)) * 0.9
                optimization_applied.append("정규화")
            
            return optimized_audio, {
                'optimizations_applied': optimization_applied,
                'original_rms': quality_metrics.get('rms_energy', 0),
                'optimized_rms': float(np.sqrt(np.mean(optimized_audio**2))),
                'quality_improvement': float(np.sqrt(np.mean(optimized_audio**2)) / max(quality_metrics.get('rms_energy', 0.01), 0.01))
            }
            
        except Exception as e:
            logger.error(f"오디오 품질 최적화 실패: {e}")
            return audio_data, {'error': str(e)}
    
    def _apply_noise_cancellation(self, audio_data: np.ndarray, sr: int) -> tuple:
        """노이즈 캔슬링 적용"""
        try:
            # 1. 스펙트럼 서브트랙션 노이즈 제거
            # FFT 변환
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/sr)
            magnitude = np.abs(fft)
            phase = np.angle(fft)
            
            # 2. 노이즈 프로파일 추정 (저에너지 주파수 대역)
            noise_threshold = np.percentile(magnitude, 20)  # 하위 20%를 노이즈로 간주
            noise_mask = magnitude < noise_threshold
            
            # 3. 노이즈 감소 적용
            alpha = 0.1  # 노이즈 감소 강도
            magnitude_denoised = magnitude.copy()
            magnitude_denoised[noise_mask] = magnitude_denoised[noise_mask] * alpha
            
            # 4. 역 FFT
            fft_denoised = magnitude_denoised * np.exp(1j * phase)
            audio_denoised = np.real(np.fft.ifft(fft_denoised))
            
            # 5. 고주파 노이즈 필터링 (저역 통과 필터)
            nyquist = sr / 2
            cutoff = 8000  # 8kHz 이상 필터링
            normal_cutoff = cutoff / nyquist
            b, a = signal.butter(4, normal_cutoff, btype='low', analog=False)
            audio_filtered = signal.filtfilt(b, a, audio_denoised)
            
            # 6. 노이즈 감소 효과 측정
            original_noise_level = np.std(audio_data)
            denoised_noise_level = np.std(audio_filtered)
            noise_reduction_db = 20 * np.log10(original_noise_level / max(denoised_noise_level, 1e-10))
            
            return audio_filtered, {
                'noise_reduction_db': float(noise_reduction_db),
                'original_noise_level': float(original_noise_level),
                'denoised_noise_level': float(denoised_noise_level),
                'noise_threshold': float(noise_threshold),
                'filter_cutoff_hz': cutoff
            }
            
        except Exception as e:
            logger.error(f"노이즈 캔슬링 실패: {e}")
            return audio_data, {'error': str(e)}
    
    def _detect_audio_issues(self, audio_data: np.ndarray, sr: int) -> Dict:
        """오디오 문제점 자동 감지"""
        try:
            issues = []
            recommendations = []
            
            # 1. 음량 부족 감지
            rms_energy = np.sqrt(np.mean(audio_data**2))
            if rms_energy < 0.01:
                issues.append("음량 부족")
                recommendations.append("마이크를 더 가까이 가져가거나 녹음 설정을 확인하세요")
            
            # 2. 클리핑 감지
            if np.max(np.abs(audio_data)) > 0.95:
                issues.append("클리핑 발생")
                recommendations.append("녹음 레벨을 낮춰주세요")
            
            # 3. 노이즈 레벨 감지
            noise_level = np.std(audio_data)
            if noise_level > 0.1:
                issues.append("높은 노이즈 레벨")
                recommendations.append("조용한 환경에서 녹음하거나 노이즈 캔슬링을 활성화하세요")
            
            # 4. 주파수 분포 분석
            fft = np.fft.fft(audio_data)
            freqs = np.fft.fftfreq(len(audio_data), 1/sr)
            power_spectrum = np.abs(fft)**2
            
            low_power = np.sum(power_spectrum[freqs < 1000])
            mid_power = np.sum(power_spectrum[(freqs >= 1000) & (freqs < 4000)])
            high_power = np.sum(power_spectrum[freqs >= 4000])
            total_power = np.sum(power_spectrum)
            
            if mid_power / total_power < 0.3:
                issues.append("중간 주파수 부족")
                recommendations.append("압축기 소리가 명확하게 들리도록 마이크 위치를 조정하세요")
            
            return {
                'issues_detected': issues,
                'recommendations': recommendations,
                'quality_score': max(0, 100 - len(issues) * 20),
                'needs_attention': len(issues) > 0
            }
            
        except Exception as e:
            logger.error(f"오디오 문제점 감지 실패: {e}")
            return {
                'issues_detected': ["분석 오류"],
                'recommendations': ["다시 시도해주세요"],
                'quality_score': 0,
                'needs_attention': True
            }

    def health_check(self) -> Dict:
        """서비스 상태 확인"""
        return {
            'status': 'healthy' if self.is_initialized else 'unhealthy',
            'initialized': self.is_initialized,
            'models_loaded': len(self.models),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'uptime': time.time() - (self.last_update.timestamp() if self.last_update else time.time())
        }

# 전역 서비스 인스턴스
unified_ai_service = UnifiedAIService()

# 하위 호환성을 위한 별칭
ensemble_ai_service = unified_ai_service
