#!/usr/bin/env python3
"""
향상된 특징 추출기 - 비용 없이 성능 향상
기존 단순한 특징들을 고도화하여 더 정확한 진단 가능
"""

import numpy as np
import librosa
from scipy import signal
from scipy.stats import skew, kurtosis
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class EnhancedFeatureExtractor:
    """향상된 오디오 특징 추출기"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.n_fft = 1024
        self.hop_length = 512
        self.n_mfcc = 13
        
        # 베어링 마모 감지를 위한 주파수 대역
        self.bearing_freq_bands = [
            (500, 800),    # 저주파 베어링 소음
            (800, 1200),   # 중주파 베어링 소음
            (1200, 2000),  # 고주파 베어링 소음
            (2000, 3000)   # 매우 고주파 베어링 소음
        ]
        
        # 압축기 특성 주파수 대역
        self.compressor_freq_bands = [
            (50, 200),     # 압축기 기본 주파수
            (200, 500),    # 압축기 하모닉
            (1000, 1500),  # 압축기 고조파
            (1500, 2500)   # 압축기 노이즈
        ]
    
    def extract_comprehensive_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """종합적인 특징 추출"""
        try:
            features = {}
            
            # 1. 기본 통계 특징
            features.update(self._extract_statistical_features(audio_data))
            
            # 2. 주파수 도메인 특징
            features.update(self._extract_frequency_features(audio_data))
            
            # 3. 시간 도메인 특징
            features.update(self._extract_temporal_features(audio_data))
            
            # 4. 베어링 마모 특화 특징
            features.update(self._extract_bearing_features(audio_data))
            
            # 5. 압축기 특화 특징
            features.update(self._extract_compressor_features(audio_data))
            
            # 6. 고급 신호 처리 특징
            features.update(self._extract_advanced_features(audio_data))
            
            return features
            
        except Exception as e:
            print(f"특징 추출 오류: {e}")
            return self._get_default_features()
    
    def _extract_statistical_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """통계적 특징 추출"""
        features = {}
        
        # 기본 통계
        features['rms_energy'] = np.sqrt(np.mean(audio_data ** 2))
        features['mean_amplitude'] = np.mean(np.abs(audio_data))
        features['std_amplitude'] = np.std(audio_data)
        features['max_amplitude'] = np.max(np.abs(audio_data))
        features['min_amplitude'] = np.min(np.abs(audio_data))
        
        # 고급 통계
        features['skewness'] = skew(audio_data)
        features['kurtosis'] = kurtosis(audio_data)
        features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        
        # 에너지 분포
        features['energy_ratio'] = features['rms_energy'] / (features['max_amplitude'] + 1e-8)
        features['dynamic_range'] = features['max_amplitude'] - features['min_amplitude']
        
        return features
    
    def _extract_frequency_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """주파수 도메인 특징 추출"""
        features = {}
        
        # STFT 계산
        stft = librosa.stft(audio_data, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        
        # 스펙트럼 중심
        features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        ))
        
        # 스펙트럼 롤오프
        features['spectral_rolloff'] = np.mean(librosa.feature.spectral_rolloff(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        ))
        
        # 스펙트럼 대역폭
        features['spectral_bandwidth'] = np.mean(librosa.feature.spectral_bandwidth(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        ))
        
        # 스펙트럼 평탄도
        features['spectral_flatness'] = np.mean(librosa.feature.spectral_flatness(
            y=audio_data, hop_length=self.hop_length
        ))
        
        # 주파수 대역별 에너지 비율
        total_energy = np.sum(magnitude)
        for i, (low, high) in enumerate(self.bearing_freq_bands):
            freq_mask = (frequencies >= low) & (frequencies <= high)
            band_energy = np.sum(magnitude[freq_mask, :])
            features[f'bearing_band_{i+1}_energy_ratio'] = band_energy / (total_energy + 1e-8)
        
        return features
    
    def _extract_temporal_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """시간 도메인 특징 추출"""
        features = {}
        
        # 에너지 변화율
        frame_length = 1024
        hop_length = 512
        energy_frames = librosa.feature.rms(
            y=audio_data, frame_length=frame_length, hop_length=hop_length
        )[0]
        
        if len(energy_frames) > 1:
            features['energy_variance'] = np.var(energy_frames)
            features['energy_change_rate'] = np.mean(np.abs(np.diff(energy_frames)))
        else:
            features['energy_variance'] = 0.0
            features['energy_change_rate'] = 0.0
        
        # 오토코릴레이션 특징
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        if len(autocorr) > 1:
            features['autocorr_peak'] = np.max(autocorr[1:]) / (autocorr[0] + 1e-8)
            features['autocorr_ratio'] = features['autocorr_peak']
        else:
            features['autocorr_peak'] = 0.0
            features['autocorr_ratio'] = 0.0
        
        return features
    
    def _extract_bearing_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """베어링 마모 특화 특징"""
        features = {}
        
        # 베어링 마모는 특정 주파수 대역에서의 에너지 집중을 보임
        stft = librosa.stft(audio_data, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        
        # 베어링 마모 주파수 대역별 분석
        bearing_energies = []
        for low, high in self.bearing_freq_bands:
            freq_mask = (frequencies >= low) & (frequencies <= high)
            band_energy = np.sum(magnitude[freq_mask, :])
            bearing_energies.append(band_energy)
        
        total_energy = np.sum(magnitude)
        if total_energy > 0:
            features['bearing_energy_ratio'] = sum(bearing_energies) / total_energy
            features['bearing_energy_concentration'] = np.max(bearing_energies) / (sum(bearing_energies) + 1e-8)
        else:
            features['bearing_energy_ratio'] = 0.0
            features['bearing_energy_concentration'] = 0.0
        
        # 베어링 마모 패턴 감지 (주파수 도메인에서의 피크)
        features['bearing_peak_prominence'] = self._calculate_peak_prominence(magnitude, frequencies)
        
        return features
    
    def _extract_compressor_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """압축기 특화 특징"""
        features = {}
        
        # 압축기 주파수 대역 분석
        stft = librosa.stft(audio_data, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(stft)
        frequencies = librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft)
        
        compressor_energies = []
        for low, high in self.compressor_freq_bands:
            freq_mask = (frequencies >= low) & (frequencies <= high)
            band_energy = np.sum(magnitude[freq_mask, :])
            compressor_energies.append(band_energy)
        
        total_energy = np.sum(magnitude)
        if total_energy > 0:
            features['compressor_energy_ratio'] = sum(compressor_energies) / total_energy
            features['compressor_harmonic_ratio'] = compressor_energies[1] / (compressor_energies[0] + 1e-8)
        else:
            features['compressor_energy_ratio'] = 0.0
            features['compressor_harmonic_ratio'] = 0.0
        
        # 압축기 작동 패턴 (주기성)
        features['compressor_periodicity'] = self._calculate_periodicity(audio_data)
        
        return features
    
    def _extract_advanced_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """고급 신호 처리 특징"""
        features = {}
        
        # MFCC 특징 (더 많은 계수)
        mfccs = librosa.feature.mfcc(
            y=audio_data, sr=self.sample_rate, n_mfcc=20, 
            n_fft=self.n_fft, hop_length=self.hop_length
        )
        
        # MFCC 통계
        features['mfcc_mean'] = np.mean(mfccs)
        features['mfcc_std'] = np.std(mfccs)
        features['mfcc_delta_mean'] = np.mean(np.diff(mfccs, axis=1))
        features['mfcc_delta_std'] = np.std(np.diff(mfccs, axis=1))
        
        # 멜 스펙트로그램 특징
        mel_spec = librosa.feature.melspectrogram(
            y=audio_data, sr=self.sample_rate, n_fft=self.n_fft, 
            hop_length=self.hop_length, n_mels=128
        )
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        features['mel_spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(
            S=mel_spec, sr=self.sample_rate, hop_length=self.hop_length
        ))
        features['mel_spectral_contrast'] = np.mean(librosa.feature.spectral_contrast(
            S=mel_spec, sr=self.sample_rate, hop_length=self.hop_length
        ))
        
        # 크로마 특징 (음악적 특성)
        chroma = librosa.feature.chroma_stft(
            y=audio_data, sr=self.sample_rate, hop_length=self.hop_length
        )
        features['chroma_mean'] = np.mean(chroma)
        features['chroma_std'] = np.std(chroma)
        
        return features
    
    def _calculate_peak_prominence(self, magnitude: np.ndarray, frequencies: np.ndarray) -> float:
        """피크 돌출도 계산"""
        try:
            # 주파수별 평균 에너지
            freq_energy = np.mean(magnitude, axis=1)
            
            # 피크 찾기
            from scipy.signal import find_peaks
            peaks, properties = find_peaks(freq_energy, prominence=0.1)
            
            if len(peaks) > 0:
                # 가장 큰 피크의 돌출도
                prominences = properties['prominences']
                return np.max(prominences) if len(prominences) > 0 else 0.0
            else:
                return 0.0
        except:
            return 0.0
    
    def _calculate_periodicity(self, audio_data: np.ndarray) -> float:
        """주기성 계산"""
        try:
            # 오토코릴레이션을 통한 주기성 측정
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # 첫 번째 피크 이후의 피크들 찾기
            if len(autocorr) > 10:
                # 첫 번째 피크 제외하고 나머지 피크들 찾기
                peaks, _ = signal.find_peaks(autocorr[10:], height=0.1)
                if len(peaks) > 0:
                    # 피크 간격의 일관성 측정
                    peak_intervals = np.diff(peaks)
                    if len(peak_intervals) > 0:
                        return 1.0 / (np.std(peak_intervals) + 1e-8)
            
            return 0.0
        except:
            return 0.0
    
    def _get_default_features(self) -> Dict[str, float]:
        """기본 특징값 반환 (오류 시)"""
        return {
            'rms_energy': 0.0,
            'mean_amplitude': 0.0,
            'std_amplitude': 0.0,
            'max_amplitude': 0.0,
            'min_amplitude': 0.0,
            'skewness': 0.0,
            'kurtosis': 0.0,
            'zero_crossing_rate': 0.0,
            'energy_ratio': 0.0,
            'dynamic_range': 0.0,
            'spectral_centroid': 0.0,
            'spectral_rolloff': 0.0,
            'spectral_bandwidth': 0.0,
            'spectral_flatness': 0.0,
            'bearing_energy_ratio': 0.0,
            'bearing_energy_concentration': 0.0,
            'bearing_peak_prominence': 0.0,
            'compressor_energy_ratio': 0.0,
            'compressor_harmonic_ratio': 0.0,
            'compressor_periodicity': 0.0,
            'mfcc_mean': 0.0,
            'mfcc_std': 0.0,
            'mfcc_delta_mean': 0.0,
            'mfcc_delta_std': 0.0,
            'mel_spectral_centroid': 0.0,
            'mel_spectral_contrast': 0.0,
            'chroma_mean': 0.0,
            'chroma_std': 0.0
        }

# 사용 예제
if __name__ == "__main__":
    # 테스트 오디오 생성
    sample_rate = 16000
    duration = 5.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 베어링 마모 시뮬레이션 (고주파 노이즈)
    normal_sound = np.sin(2 * np.pi * 100 * t) + 0.1 * np.random.randn(len(t))
    bearing_wear = normal_sound + 0.3 * np.sin(2 * np.pi * 1200 * t) + 0.2 * np.random.randn(len(t))
    
    # 특징 추출기 초기화
    extractor = EnhancedFeatureExtractor(sample_rate)
    
    # 특징 추출
    normal_features = extractor.extract_comprehensive_features(normal_sound)
    bearing_features = extractor.extract_comprehensive_features(bearing_wear)
    
    print("정상 소음 특징:")
    for key, value in normal_features.items():
        print(f"  {key}: {value:.4f}")
    
    print("\n베어링 마모 소음 특징:")
    for key, value in bearing_features.items():
        print(f"  {key}: {value:.4f}")
    
    print(f"\n총 특징 수: {len(normal_features)}")
