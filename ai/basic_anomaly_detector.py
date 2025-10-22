#!/usr/bin/env python3
"""
기본 이상 탐지 시스템
CPU 최적화된 경량 이상 탐지 AI
"""

import numpy as np
import librosa
import time
from scipy import signal
from scipy.signal import butter, filtfilt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import json
from collections import deque
import threading

class BasicAnomalyDetector:
    def __init__(self, 
                 model_save_path: str = "data/models/",
                 window_size: float = 5.0,
                 sample_rate: int = 16000):
        """
        기본 이상 탐지 시스템 초기화
        
        Args:
            model_save_path: 모델 저장 경로
            window_size: 분석 윈도우 크기 (초)
            sample_rate: 샘플링 레이트
        """
        self.model_save_path = model_save_path
        os.makedirs(model_save_path, exist_ok=True)
        
        self.window_size = window_size
        self.sample_rate = sample_rate
        self.n_fft = 1024
        self.hop_length = 512
        
        # 모델들
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.pca = None
        self.is_trained = False
        
        # 통계 정보
        self.normal_stats = {}
        self.feature_names = [
            'rms_energy', 'spectral_centroid', 'spectral_rolloff', 
            'zero_crossing_rate', 'spectral_bandwidth', 'spectral_contrast',
            'low_freq_ratio', 'mid_freq_ratio', 'high_freq_ratio',
            'mfcc_1_mean', 'mfcc_2_mean', 'mfcc_3_mean'
        ]
        
        # 모니터링 히스토리
        self.detection_history = deque(maxlen=1000)
        self.performance_stats = {
            'total_detections': 0,
            'anomaly_count': 0,
            'average_processing_time': 0.0,
            'last_update': None
        }
        
        print("🧠 기본 이상 탐지 시스템 초기화")
        print(f"⏱️ 윈도우 크기: {window_size}초")
        print(f"🎵 샘플링 레이트: {sample_rate}Hz")
        print(f"💾 모델 저장 경로: {model_save_path}")
    
    def extract_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """오디오 특징 추출 (CPU 최적화)"""
        try:
            # 리샘플링
            if sr != self.sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=self.sample_rate)
            
            # 노이즈 필터링
            nyquist = self.sample_rate / 2
            low_cutoff = 50 / nyquist
            high_cutoff = 4000 / nyquist
            b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
            filtered_audio = filtfilt(b, a, audio_data)
            
            # 1. 에너지 특징
            rms_energy = np.sqrt(np.mean(filtered_audio ** 2))
            
            # 2. 주파수 도메인 특징
            stft = librosa.stft(filtered_audio, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
            
            # 스펙트럼 특징
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=filtered_audio, sr=self.sample_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=filtered_audio, sr=self.sample_rate))
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=filtered_audio, sr=self.sample_rate))
            spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=filtered_audio, sr=self.sample_rate))
            
            # Zero Crossing Rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(filtered_audio, hop_length=self.hop_length))
            
            # 주파수 대역별 에너지 비율
            low_freq_energy = np.sum(magnitude[(frequencies >= 50) & (frequencies <= 500), :])
            mid_freq_energy = np.sum(magnitude[(frequencies >= 500) & (frequencies <= 2000), :])
            high_freq_energy = np.sum(magnitude[(frequencies >= 2000) & (frequencies <= 4000), :])
            total_energy = np.sum(magnitude)
            
            if total_energy > 0:
                low_freq_ratio = low_freq_energy / total_energy
                mid_freq_ratio = mid_freq_energy / total_energy
                high_freq_ratio = high_freq_energy / total_energy
            else:
                low_freq_ratio = mid_freq_ratio = high_freq_ratio = 0
            
            # MFCC 특징 (첫 3개만 사용)
            mfccs = librosa.feature.mfcc(y=filtered_audio, sr=self.sample_rate, n_mfcc=13)
            mfcc_means = np.mean(mfccs, axis=1)
            
            features = {
                'rms_energy': float(rms_energy),
                'spectral_centroid': float(spectral_centroid),
                'spectral_rolloff': float(spectral_rolloff),
                'zero_crossing_rate': float(zcr),
                'spectral_bandwidth': float(spectral_bandwidth),
                'spectral_contrast': float(spectral_contrast),
                'low_freq_ratio': float(low_freq_ratio),
                'mid_freq_ratio': float(mid_freq_ratio),
                'high_freq_ratio': float(high_freq_ratio),
                'mfcc_1_mean': float(mfcc_means[0]),
                'mfcc_2_mean': float(mfcc_means[1]),
                'mfcc_3_mean': float(mfcc_means[2])
            }
            
            return features
            
        except Exception as e:
            print(f"❌ 특징 추출 오류: {e}")
            return {name: 0.0 for name in self.feature_names}
    
    def train_on_normal_data(self, normal_audio_files: List[str]) -> Dict:
        """
        정상 데이터로 훈련
        
        Args:
            normal_audio_files: 정상 오디오 파일 경로 리스트
            
        Returns:
            훈련 결과
        """
        print("🎯 정상 데이터로 이상 탐지 모델 훈련 시작")
        print(f"📁 정상 오디오 파일 수: {len(normal_audio_files)}")
        
        # 정상 데이터 특징 추출
        normal_features = []
        processed_files = 0
        
        for i, file_path in enumerate(normal_audio_files):
            try:
                if i % 10 == 0:
                    print(f"처리 중: {i+1}/{len(normal_audio_files)}")
                
                audio_data, sr = librosa.load(file_path, sr=None)
                
                # 청크 단위로 분석
                chunk_samples = int(self.window_size * sr)
                for start in range(0, len(audio_data), chunk_samples):
                    chunk = audio_data[start:start + chunk_samples]
                    if len(chunk) >= chunk_samples:
                        features = self.extract_features(chunk, sr)
                        normal_features.append(list(features.values()))
                        processed_files += 1
                        
            except Exception as e:
                print(f"❌ 파일 처리 오류 {file_path}: {e}")
                continue
        
        if len(normal_features) < 10:
            raise ValueError("충분한 정상 데이터가 없습니다. 최소 10개 샘플 필요")
        
        print(f"✅ 처리된 샘플 수: {len(normal_features)}")
        
        # 특징 정규화
        X_normal = np.array(normal_features)
        X_scaled = self.scaler.fit_transform(X_normal)
        
        # PCA로 차원 축소 (노이즈 감소)
        n_components = min(8, X_scaled.shape[1])
        self.pca = PCA(n_components=n_components, random_state=42)
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Isolation Forest 훈련
        contamination = 0.05  # 5%를 이상으로 간주
        self.isolation_forest = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            n_jobs=-1  # CPU 병렬 처리
        )
        
        # 정상 데이터로 훈련
        self.isolation_forest.fit(X_pca)
        
        # 정상 데이터 통계 저장
        self._calculate_normal_statistics(X_normal)
        
        self.is_trained = True
        
        # 훈련 결과
        result = {
            'total_samples': len(normal_features),
            'processed_files': processed_files,
            'feature_dimensions': X_normal.shape[1],
            'pca_components': n_components,
            'explained_variance_ratio': float(np.sum(self.pca.explained_variance_ratio_)),
            'contamination_rate': contamination,
            'training_completed': True,
            'training_time': datetime.now().isoformat()
        }
        
        print("✅ 이상 탐지 모델 훈련 완료!")
        print(f"📊 총 샘플 수: {result['total_samples']}")
        print(f"📈 PCA 설명 분산: {result['explained_variance_ratio']:.3f}")
        print(f"🎯 오염률: {contamination}")
        
        return result
    
    def _calculate_normal_statistics(self, X_normal: np.ndarray):
        """정상 데이터 통계 계산"""
        for i, feature_name in enumerate(self.feature_names):
            if i < X_normal.shape[1]:
                values = X_normal[:, i]
                self.normal_stats[feature_name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'percentiles': {
                        'p5': float(np.percentile(values, 5)),
                        'p25': float(np.percentile(values, 25)),
                        'p75': float(np.percentile(values, 75)),
                        'p95': float(np.percentile(values, 95))
                    }
                }
    
    def detect_anomaly(self, audio_data: np.ndarray, sr: int) -> Dict:
        """
        이상 탐지 수행
        
        Args:
            audio_data: 오디오 데이터
            sr: 샘플링 레이트
            
        Returns:
            이상 탐지 결과
        """
        if not self.is_trained:
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': '모델이 훈련되지 않았습니다.',
                'anomaly_type': 'model_not_trained',
                'processing_time_ms': 0
            }
        
        start_time = time.time()
        
        try:
            # 특징 추출
            features = self.extract_features(audio_data, sr)
            feature_vector = np.array(list(features.values())).reshape(1, -1)
            
            # 정규화 및 PCA 변환
            X_scaled = self.scaler.transform(feature_vector)
            X_pca = self.pca.transform(X_scaled)
            
            # Isolation Forest 점수 계산
            isolation_score = self.isolation_forest.score_samples(X_pca)[0]
            is_anomaly = isolation_score < 0  # 음수면 이상
            
            # 통계 기반 추가 검증
            statistical_anomaly = self._check_statistical_anomaly(features)
            
            # 이상 유형 분류
            anomaly_type = self._classify_anomaly_type(features, statistical_anomaly)
            
            # 신뢰도 계산
            confidence = self._calculate_confidence(isolation_score, statistical_anomaly)
            
            # 최종 판정
            final_anomaly = is_anomaly or statistical_anomaly
            
            processing_time = (time.time() - start_time) * 1000
            
            # 성능 통계 업데이트
            self._update_performance_stats(final_anomaly, processing_time)
            
            # 히스토리 업데이트
            self.detection_history.append({
                'timestamp': datetime.now(),
                'is_anomaly': final_anomaly,
                'confidence': confidence,
                'anomaly_type': anomaly_type,
                'isolation_score': float(isolation_score),
                'statistical_anomaly': statistical_anomaly,
                'processing_time_ms': processing_time
            })
            
            result = {
                'is_anomaly': final_anomaly,
                'confidence': confidence,
                'message': self._get_anomaly_message(anomaly_type, confidence),
                'anomaly_type': anomaly_type,
                'features': features,
                'isolation_score': float(isolation_score),
                'statistical_anomaly': statistical_anomaly,
                'processing_time_ms': processing_time
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 이상 탐지 오류: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': f'분석 중 오류 발생: {str(e)}',
                'anomaly_type': 'error',
                'processing_time_ms': (time.time() - start_time) * 1000
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
                if stats['std'] > 0:
                    # Z-score 계산
                    z_score = abs((value - stats['mean']) / stats['std'])
                    if z_score > 3:  # 3시그마 규칙
                        anomaly_count += 1
                    total_features += 1
        
        # 30% 이상의 특징이 이상이면 전체를 이상으로 판정
        return total_features > 0 and (anomaly_count / total_features) > 0.3
    
    def _classify_anomaly_type(self, features: Dict[str, float], 
                              statistical_anomaly: bool) -> str:
        """이상 유형 분류"""
        if not statistical_anomaly:
            return 'normal'
        
        # 베어링 마모 (고주파, ZCR 높음)
        if (features.get('spectral_centroid', 0) > 2000 and 
            features.get('zero_crossing_rate', 0) > 0.2):
            return 'bearing_wear'
        
        # 압축기 이상 (에너지 패턴 변화)
        if (features.get('rms_energy', 0) > 1.0 or 
            features.get('rms_energy', 0) < 0.01):
            return 'compressor_abnormal'
        
        # 냉매 누출 (저주파 에너지 증가)
        if features.get('low_freq_ratio', 0) > 0.8:
            return 'refrigerant_leak'
        
        # 일반적인 이상
        return 'general_anomaly'
    
    def _calculate_confidence(self, isolation_score: float, 
                            statistical_anomaly: bool) -> float:
        """신뢰도 계산"""
        # Isolation Forest 점수 기반 신뢰도
        score_confidence = min(1.0, max(0.0, abs(isolation_score) / 2.0))
        
        # 통계 기반 신뢰도
        stat_confidence = 0.8 if statistical_anomaly else 0.2
        
        # 가중 평균
        confidence = 0.6 * score_confidence + 0.4 * stat_confidence
        return float(confidence)
    
    def _get_anomaly_message(self, anomaly_type: str, confidence: float) -> str:
        """이상 메시지 생성"""
        messages = {
            'normal': '정상 작동 중',
            'bearing_wear': f'베어링 마모 의심 (신뢰도: {confidence:.1%})',
            'compressor_abnormal': f'압축기 이상 의심 (신뢰도: {confidence:.1%})',
            'refrigerant_leak': f'냉매 누출 의심 (신뢰도: {confidence:.1%})',
            'general_anomaly': f'이상 소음 감지 (신뢰도: {confidence:.1%})',
            'model_not_trained': '모델이 훈련되지 않았습니다',
            'error': '분석 중 오류 발생'
        }
        return messages.get(anomaly_type, '알 수 없는 이상')
    
    def _update_performance_stats(self, is_anomaly: bool, processing_time: float):
        """성능 통계 업데이트"""
        self.performance_stats['total_detections'] += 1
        
        if is_anomaly:
            self.performance_stats['anomaly_count'] += 1
        
        # 평균 처리 시간 업데이트
        total = self.performance_stats['total_detections']
        current_avg = self.performance_stats['average_processing_time']
        self.performance_stats['average_processing_time'] = (
            (current_avg * (total - 1) + processing_time) / total
        )
        
        self.performance_stats['last_update'] = datetime.now().isoformat()
    
    def get_performance_stats(self) -> Dict:
        """성능 통계 반환"""
        stats = self.performance_stats.copy()
        
        if stats['total_detections'] > 0:
            stats['anomaly_rate'] = stats['anomaly_count'] / stats['total_detections']
        else:
            stats['anomaly_rate'] = 0.0
        
        return stats
    
    def get_detection_history(self, limit: int = 100) -> List[Dict]:
        """최근 탐지 히스토리 반환"""
        return list(self.detection_history)[-limit:]
    
    def save_model(self, filepath: str = None):
        """모델 저장"""
        if not self.is_trained:
            raise ValueError("모델이 훈련되지 않았습니다.")
        
        if filepath is None:
            filepath = os.path.join(self.model_save_path, "basic_anomaly_detector.pkl")
        
        # 모델과 전처리기 저장
        model_data = {
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler,
            'pca': self.pca,
            'normal_stats': self.normal_stats,
            'feature_names': self.feature_names,
            'window_size': self.window_size,
            'sample_rate': self.sample_rate,
            'is_trained': self.is_trained,
            'performance_stats': self.performance_stats
        }
        
        joblib.dump(model_data, filepath)
        
        # 메타데이터 저장
        metadata = {
            'model_type': 'basic_anomaly_detector',
            'created_at': datetime.now().isoformat(),
            'feature_count': len(self.feature_names),
            'pca_components': self.pca.n_components_ if self.pca else 0,
            'contamination_rate': 0.05,
            'window_size': self.window_size,
            'sample_rate': self.sample_rate
        }
        
        metadata_file = filepath.replace('.pkl', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 기본 이상 탐지 모델 저장 완료: {filepath}")
        print(f"📊 메타데이터 저장 완료: {metadata_file}")
    
    def load_model(self, filepath: str = None):
        """모델 로드"""
        if filepath is None:
            filepath = os.path.join(self.model_save_path, "basic_anomaly_detector.pkl")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {filepath}")
        
        # 모델 로드
        model_data = joblib.load(filepath)
        
        self.isolation_forest = model_data['isolation_forest']
        self.scaler = model_data['scaler']
        self.pca = model_data['pca']
        self.normal_stats = model_data['normal_stats']
        self.feature_names = model_data['feature_names']
        self.window_size = model_data['window_size']
        self.sample_rate = model_data['sample_rate']
        self.is_trained = model_data['is_trained']
        self.performance_stats = model_data.get('performance_stats', {})
        
        print(f"✅ 기본 이상 탐지 모델 로드 완료: {filepath}")

# 사용 예제
if __name__ == "__main__":
    # 기본 이상 탐지 시스템 초기화
    detector = BasicAnomalyDetector()
    
    print("🧠 기본 이상 탐지 시스템 테스트")
    print("=" * 50)
    print("CPU 최적화된 경량 이상 탐지 AI")
    print("GPU 없이도 고성능 달성 가능")
    print("=" * 50)
    
    # 가상의 정상 데이터로 훈련 (실제로는 파일 경로 리스트 사용)
    # normal_files = ["normal1.wav", "normal2.wav", ...]
    # training_result = detector.train_on_normal_data(normal_files)
    
    print("시스템 준비 완료!")
    print("정상 데이터로 훈련 후 실시간 이상 탐지 가능")
