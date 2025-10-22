#!/usr/bin/env python3
"""
냉동고 24시간 모니터링 데이터 기반 이상 탐지 AI
정상 데이터가 대부분인 상황에 최적화된 시스템
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
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

class RefrigeratorAnomalyDetector:
    def __init__(self, model_save_path: str = "data/models/"):
        """
        냉동고 이상 탐지 AI 초기화
        
        Args:
            model_save_path: 모델 저장 경로
        """
        self.model_save_path = model_save_path
        os.makedirs(model_save_path, exist_ok=True)
        
        # 오디오 처리 설정
        self.sample_rate = 16000
        self.n_fft = 1024
        self.hop_length = 512
        self.window_size = 5.0  # 5초 윈도우
        
        # 이상 탐지 모델들
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.pca = None
        self.is_trained = False
        
        # 정상 데이터 통계 (적응형 임계값용)
        self.normal_stats = {
            'rms_energy': {'mean': 0, 'std': 0, 'percentiles': {}},
            'spectral_centroid': {'mean': 0, 'std': 0, 'percentiles': {}},
            'zero_crossing_rate': {'mean': 0, 'std': 0, 'percentiles': {}},
            'spectral_rolloff': {'mean': 0, 'std': 0, 'percentiles': {}},
            'mfcc_means': {'mean': 0, 'std': 0},
            'mfcc_stds': {'mean': 0, 'std': 0}
        }
        
        # 적응형 임계값 설정
        self.adaptive_thresholds = {
            'rms_energy': {'lower': 0, 'upper': 0},
            'spectral_centroid': {'lower': 0, 'upper': 0},
            'zero_crossing_rate': {'lower': 0, 'upper': 0},
            'spectral_rolloff': {'lower': 0, 'upper': 0},
            'isolation_score': {'threshold': 0}
        }
        
        # 모니터링 히스토리 (최근 24시간)
        self.monitoring_history = []
        self.max_history_hours = 24
        
        print("🧠 냉동고 이상 탐지 AI 초기화 완료")
        print(f"📊 모니터링 윈도우: {self.window_size}초")
        print(f"📈 적응형 임계값 시스템 활성화")
    
    def extract_comprehensive_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, float]:
        """종합적인 특징 추출 (정상 데이터 패턴 학습용)"""
        try:
            # 기본 오디오 전처리
            if sr != self.sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=self.sample_rate)
            
            # 노이즈 필터링
            nyquist = self.sample_rate / 2
            low_cutoff = 50 / nyquist
            high_cutoff = 4000 / nyquist
            b, a = butter(4, [low_cutoff, high_cutoff], btype='band')
            filtered_audio = filtfilt(b, a, audio_data)
            
            # 1. 에너지 기반 특징
            rms_energy = np.sqrt(np.mean(filtered_audio ** 2))
            energy_entropy = self._calculate_energy_entropy(filtered_audio)
            
            # 2. 주파수 도메인 특징
            stft = librosa.stft(filtered_audio, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
            
            # 스펙트럼 중심, 롤오프, 대역폭
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=filtered_audio, sr=self.sample_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=filtered_audio, sr=self.sample_rate))
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=filtered_audio, sr=self.sample_rate))
            
            # 3. Zero Crossing Rate (날카로운 소음 감지)
            zcr = np.mean(librosa.feature.zero_crossing_rate(filtered_audio, hop_length=self.hop_length))
            
            # 4. MFCC 특징 (음성 인식에서 효과적)
            mfccs = librosa.feature.mfcc(y=filtered_audio, sr=self.sample_rate, n_mfcc=13)
            mfcc_means = np.mean(mfccs, axis=1)
            mfcc_stds = np.std(mfccs, axis=1)
            
            # 5. 스펙트럼 특징
            spectral_contrast = np.mean(librosa.feature.spectral_contrast(y=filtered_audio, sr=self.sample_rate))
            spectral_flatness = np.mean(librosa.feature.spectral_flatness(y=filtered_audio))
            
            # 6. 주파수 대역별 에너지 비율
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
            
            # 7. 시간적 특징 (변동성)
            rms_temporal = librosa.feature.rms(y=filtered_audio, hop_length=self.hop_length)[0]
            temporal_std = np.std(rms_temporal)
            temporal_mean = np.mean(rms_temporal)
            
            features = {
                # 에너지 특징
                'rms_energy': float(rms_energy),
                'energy_entropy': float(energy_entropy),
                'temporal_std': float(temporal_std),
                'temporal_mean': float(temporal_mean),
                
                # 주파수 특징
                'spectral_centroid': float(spectral_centroid),
                'spectral_rolloff': float(spectral_rolloff),
                'spectral_bandwidth': float(spectral_bandwidth),
                'spectral_contrast': float(spectral_contrast),
                'spectral_flatness': float(spectral_flatness),
                
                # Zero Crossing Rate
                'zero_crossing_rate': float(zcr),
                
                # 주파수 대역 비율
                'low_freq_ratio': float(low_freq_ratio),
                'mid_freq_ratio': float(mid_freq_ratio),
                'high_freq_ratio': float(high_freq_ratio),
                
                # MFCC 통계
                'mfcc_1_mean': float(mfcc_means[0]),
                'mfcc_2_mean': float(mfcc_means[1]),
                'mfcc_3_mean': float(mfcc_means[2]),
                'mfcc_1_std': float(mfcc_stds[0]),
                'mfcc_2_std': float(mfcc_stds[1]),
                'mfcc_3_std': float(mfcc_stds[2])
            }
            
            return features
            
        except Exception as e:
            print(f"❌ 특징 추출 오류: {e}")
            return self._get_default_features()
    
    def _calculate_energy_entropy(self, audio_data: np.ndarray) -> float:
        """에너지 엔트로피 계산"""
        try:
            # 프레임 단위로 에너지 계산
            frame_length = 1024
            hop_length = 512
            frames = librosa.util.frame(audio_data, frame_length=frame_length, hop_length=hop_length)
            frame_energies = np.sum(frames ** 2, axis=0)
            
            # 정규화
            if np.sum(frame_energies) > 0:
                frame_energies = frame_energies / np.sum(frame_energies)
                # 엔트로피 계산 (0으로 나누기 방지)
                frame_energies = frame_energies + 1e-10
                entropy = -np.sum(frame_energies * np.log2(frame_energies))
            else:
                entropy = 0
            
            return float(entropy)
        except:
            return 0.0
    
    def _get_default_features(self) -> Dict[str, float]:
        """기본 특징값 반환 (오류 시)"""
        return {
            'rms_energy': 0.0, 'energy_entropy': 0.0, 'temporal_std': 0.0, 'temporal_mean': 0.0,
            'spectral_centroid': 0.0, 'spectral_rolloff': 0.0, 'spectral_bandwidth': 0.0,
            'spectral_contrast': 0.0, 'spectral_flatness': 0.0, 'zero_crossing_rate': 0.0,
            'low_freq_ratio': 0.0, 'mid_freq_ratio': 0.0, 'high_freq_ratio': 0.0,
            'mfcc_1_mean': 0.0, 'mfcc_2_mean': 0.0, 'mfcc_3_mean': 0.0,
            'mfcc_1_std': 0.0, 'mfcc_2_std': 0.0, 'mfcc_3_std': 0.0
        }
    
    def train_on_normal_data(self, normal_audio_files: List[str], 
                           validation_split: float = 0.2) -> Dict:
        """
        정상 데이터로만 훈련 (이상 탐지 모델)
        
        Args:
            normal_audio_files: 정상 상태 오디오 파일 경로 리스트
            validation_split: 검증 데이터 비율
        """
        print("🎯 정상 데이터 기반 이상 탐지 모델 훈련 시작")
        print(f"📁 정상 오디오 파일 수: {len(normal_audio_files)}")
        
        # 정상 데이터 특징 추출
        normal_features = []
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
                        features = self.extract_comprehensive_features(chunk, sr)
                        normal_features.append(list(features.values()))
                        
            except Exception as e:
                print(f"❌ 파일 처리 오류 {file_path}: {e}")
                continue
        
        if len(normal_features) < 10:
            raise ValueError("충분한 정상 데이터가 없습니다. 최소 10개 샘플 필요")
        
        # 특징 정규화
        X_normal = np.array(normal_features)
        X_scaled = self.scaler.fit_transform(X_normal)
        
        # PCA로 차원 축소 (노이즈 감소)
        self.pca = PCA(n_components=min(10, X_scaled.shape[1]), random_state=42)
        X_pca = self.pca.fit_transform(X_scaled)
        
        # Isolation Forest 훈련 (정상 데이터만으로)
        self.isolation_forest = IsolationForest(
            contamination=0.05,  # 5%를 이상으로 간주
            random_state=42,
            n_estimators=100
        )
        
        # 정상 데이터로 훈련
        self.isolation_forest.fit(X_pca)
        
        # 정상 데이터 통계 계산 (적응형 임계값용)
        self._calculate_normal_statistics(X_normal)
        
        # 적응형 임계값 설정
        self._set_adaptive_thresholds(X_pca)
        
        self.is_trained = True
        
        # 훈련 결과 저장
        training_result = {
            'total_samples': len(normal_features),
            'feature_dimensions': X_normal.shape[1],
            'pca_components': self.pca.n_components_,
            'explained_variance_ratio': float(np.sum(self.pca.explained_variance_ratio_)),
            'isolation_forest_score': float(np.mean(self.isolation_forest.score_samples(X_pca))),
            'training_completed': True
        }
        
        print("✅ 정상 데이터 기반 훈련 완료!")
        print(f"📊 총 샘플 수: {training_result['total_samples']}")
        print(f"📈 PCA 설명 분산: {training_result['explained_variance_ratio']:.3f}")
        
        return training_result
    
    def _calculate_normal_statistics(self, X_normal: np.ndarray):
        """정상 데이터 통계 계산"""
        feature_names = list(self._get_default_features().keys())
        
        for i, feature_name in enumerate(feature_names):
            if i < X_normal.shape[1]:
                values = X_normal[:, i]
                self.normal_stats[feature_name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'percentiles': {
                        'p5': float(np.percentile(values, 5)),
                        'p25': float(np.percentile(values, 25)),
                        'p75': float(np.percentile(values, 75)),
                        'p95': float(np.percentile(values, 95))
                    }
                }
    
    def _set_adaptive_thresholds(self, X_pca: np.ndarray):
        """적응형 임계값 설정"""
        # Isolation Forest 점수 기반 임계값
        scores = self.isolation_forest.score_samples(X_pca)
        self.adaptive_thresholds['isolation_score']['threshold'] = float(np.percentile(scores, 5))
        
        # 개별 특징 기반 임계값 (3시그마 규칙)
        for feature_name, stats in self.normal_stats.items():
            if 'percentiles' in stats:
                lower = stats['percentiles']['p5']  # 하위 5%
                upper = stats['percentiles']['p95']  # 상위 5%
                self.adaptive_thresholds[feature_name] = {
                    'lower': lower,
                    'upper': upper
                }
    
    def detect_anomaly(self, audio_data: np.ndarray, sr: int) -> Dict:
        """
        실시간 이상 탐지
        
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
                'anomaly_type': 'unknown',
                'features': {},
                'processing_time_ms': 0
            }
        
        try:
            start_time = time.time()
            
            # 특징 추출
            features = self.extract_comprehensive_features(audio_data, sr)
            feature_vector = np.array(list(features.values())).reshape(1, -1)
            
            # 정규화 및 PCA 변환
            X_scaled = self.scaler.transform(feature_vector)
            X_pca = self.pca.transform(X_scaled)
            
            # Isolation Forest 점수 계산
            isolation_score = self.isolation_forest.score_samples(X_pca)[0]
            is_anomaly = isolation_score < self.adaptive_thresholds['isolation_score']['threshold']
            
            # 개별 특징 기반 이상 탐지
            feature_anomalies = self._check_individual_features(features)
            
            # 이상 유형 분류
            anomaly_type = self._classify_anomaly_type(features, feature_anomalies)
            
            # 신뢰도 계산
            confidence = self._calculate_confidence(isolation_score, feature_anomalies)
            
            # 최종 판정
            final_anomaly = is_anomaly or len(feature_anomalies) > 2
            
            processing_time = (time.time() - start_time) * 1000
            
            # 모니터링 히스토리 업데이트
            self._update_monitoring_history({
                'timestamp': datetime.now(),
                'is_anomaly': final_anomaly,
                'confidence': confidence,
                'anomaly_type': anomaly_type,
                'isolation_score': float(isolation_score),
                'feature_anomalies': feature_anomalies
            })
            
            result = {
                'is_anomaly': final_anomaly,
                'confidence': confidence,
                'message': self._get_anomaly_message(anomaly_type, confidence),
                'anomaly_type': anomaly_type,
                'features': features,
                'isolation_score': float(isolation_score),
                'feature_anomalies': feature_anomalies,
                'processing_time_ms': processing_time,
                'adaptive_thresholds': self.adaptive_thresholds
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 이상 탐지 오류: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'message': f'분석 중 오류 발생: {str(e)}',
                'anomaly_type': 'error',
                'features': {},
                'processing_time_ms': 0
            }
    
    def _check_individual_features(self, features: Dict[str, float]) -> List[str]:
        """개별 특징 기반 이상 탐지"""
        anomalies = []
        
        for feature_name, value in features.items():
            if feature_name in self.adaptive_thresholds:
                threshold = self.adaptive_thresholds[feature_name]
                if value < threshold['lower'] or value > threshold['upper']:
                    anomalies.append(feature_name)
        
        return anomalies
    
    def _classify_anomaly_type(self, features: Dict[str, float], 
                              feature_anomalies: List[str]) -> str:
        """이상 유형 분류"""
        if not feature_anomalies:
            return 'normal'
        
        # 베어링 마모 (고주파, ZCR 높음)
        if 'spectral_centroid' in feature_anomalies and 'zero_crossing_rate' in feature_anomalies:
            return 'bearing_wear'
        
        # 압축기 이상 (에너지 패턴 변화)
        if 'rms_energy' in feature_anomalies and 'temporal_std' in feature_anomalies:
            return 'compressor_abnormal'
        
        # 냉매 누출 (저주파 에너지 증가)
        if 'low_freq_ratio' in feature_anomalies:
            return 'refrigerant_leak'
        
        # 일반적인 이상
        return 'general_anomaly'
    
    def _calculate_confidence(self, isolation_score: float, 
                            feature_anomalies: List[str]) -> float:
        """신뢰도 계산"""
        # Isolation Forest 점수 기반 신뢰도
        score_confidence = min(1.0, max(0.0, abs(isolation_score) / 2.0))
        
        # 특징 기반 신뢰도
        feature_confidence = min(1.0, len(feature_anomalies) / 5.0)
        
        # 가중 평균
        confidence = 0.7 * score_confidence + 0.3 * feature_confidence
        return float(confidence)
    
    def _get_anomaly_message(self, anomaly_type: str, confidence: float) -> str:
        """이상 메시지 생성"""
        messages = {
            'normal': '정상 작동 중',
            'bearing_wear': f'베어링 마모 의심 (신뢰도: {confidence:.1%})',
            'compressor_abnormal': f'압축기 이상 의심 (신뢰도: {confidence:.1%})',
            'refrigerant_leak': f'냉매 누출 의심 (신뢰도: {confidence:.1%})',
            'general_anomaly': f'이상 소음 감지 (신뢰도: {confidence:.1%})',
            'error': '분석 중 오류 발생'
        }
        return messages.get(anomaly_type, '알 수 없는 이상')
    
    def _update_monitoring_history(self, result: Dict):
        """모니터링 히스토리 업데이트"""
        self.monitoring_history.append(result)
        
        # 24시간 이전 데이터 제거
        cutoff_time = datetime.now() - timedelta(hours=self.max_history_hours)
        self.monitoring_history = [
            r for r in self.monitoring_history 
            if r['timestamp'] > cutoff_time
        ]
    
    def get_monitoring_summary(self) -> Dict:
        """모니터링 요약 정보"""
        if not self.monitoring_history:
            return {'total_samples': 0, 'anomaly_rate': 0.0}
        
        total_samples = len(self.monitoring_history)
        anomaly_count = sum(1 for r in self.monitoring_history if r['is_anomaly'])
        anomaly_rate = anomaly_count / total_samples if total_samples > 0 else 0.0
        
        # 최근 이상 유형별 통계
        recent_anomalies = [r for r in self.monitoring_history if r['is_anomaly']]
        anomaly_types = {}
        for anomaly in recent_anomalies:
            anomaly_type = anomaly['anomaly_type']
            anomaly_types[anomaly_type] = anomaly_types.get(anomaly_type, 0) + 1
        
        return {
            'total_samples': total_samples,
            'anomaly_count': anomaly_count,
            'anomaly_rate': float(anomaly_rate),
            'anomaly_types': anomaly_types,
            'monitoring_duration_hours': self.max_history_hours,
            'last_update': self.monitoring_history[-1]['timestamp'].isoformat() if self.monitoring_history else None
        }
    
    def save_model(self, filepath: str = None):
        """모델 저장"""
        if not self.is_trained:
            raise ValueError("모델이 훈련되지 않았습니다.")
        
        if filepath is None:
            filepath = os.path.join(self.model_save_path, "anomaly_detector.pkl")
        
        # 모델과 전처리기 저장
        model_data = {
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler,
            'pca': self.pca,
            'normal_stats': self.normal_stats,
            'adaptive_thresholds': self.adaptive_thresholds,
            'is_trained': self.is_trained,
            'sample_rate': self.sample_rate,
            'window_size': self.window_size
        }
        
        joblib.dump(model_data, filepath)
        
        # 메타데이터 저장
        metadata = {
            'model_type': 'refrigerator_anomaly_detector',
            'created_at': datetime.now().isoformat(),
            'feature_count': len(self._get_default_features()),
            'pca_components': self.pca.n_components_ if self.pca else 0,
            'contamination_rate': 0.05
        }
        
        metadata_file = filepath.replace('.pkl', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 이상 탐지 모델 저장 완료: {filepath}")
        print(f"📊 메타데이터 저장 완료: {metadata_file}")
    
    def load_model(self, filepath: str = None):
        """모델 로드"""
        if filepath is None:
            filepath = os.path.join(self.model_save_path, "anomaly_detector.pkl")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {filepath}")
        
        # 모델 로드
        model_data = joblib.load(filepath)
        
        self.isolation_forest = model_data['isolation_forest']
        self.scaler = model_data['scaler']
        self.pca = model_data['pca']
        self.normal_stats = model_data['normal_stats']
        self.adaptive_thresholds = model_data['adaptive_thresholds']
        self.is_trained = model_data['is_trained']
        self.sample_rate = model_data['sample_rate']
        self.window_size = model_data['window_size']
        
        print(f"✅ 이상 탐지 모델 로드 완료: {filepath}")

# 사용 예제
if __name__ == "__main__":
    # 이상 탐지 AI 초기화
    detector = RefrigeratorAnomalyDetector()
    
    print("🧠 냉동고 이상 탐지 AI 시스템")
    print("=" * 50)
    print("정상 데이터로 훈련 후 이상 탐지 수행")
    print("24시간 모니터링에 최적화된 시스템")
    print("=" * 50)
