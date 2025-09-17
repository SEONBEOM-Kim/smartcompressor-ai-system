import numpy as np
import librosa
import scipy.signal
import scipy.stats
from scipy.signal import butter, filtfilt, medfilt, wiener
import matplotlib.pyplot as plt
import os
from typing import Tuple, Dict, List, Optional, Union
import warnings
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from functools import partial
import threading
import queue
import time
warnings.filterwarnings('ignore')

class OptimizedSignalPreprocessor:
    def __init__(self, sample_rate: int = 22050, n_mfcc: int = 13, 
                 n_workers: int = None, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.feature_length = 100
        self.n_workers = n_workers or min(mp.cpu_count(), 4)
        self.chunk_size = chunk_size
        
        # 압축기 주파수 대역
        self.compressor_freq_range = (50, 2000)
        self.refrigerant_freq_range = (2000, 8000)
        
        # 캐시된 필터 계수 (성능 최적화)
        self._filter_cache = {}
        self._initialize_filter_cache()
        
        # 스트리밍을 위한 버퍼
        self._streaming_buffer = queue.Queue(maxsize=100)
        self._streaming_thread = None
        self._streaming_active = False
    
    def _initialize_filter_cache(self):
        """필터 계수 캐시 초기화"""
        nyquist = self.sample_rate / 2
        
        # 압축기 필터
        low = self.compressor_freq_range[0] / nyquist
        high = self.compressor_freq_range[1] / nyquist
        self._filter_cache['compressor'] = butter(4, [low, high], btype='band')
        
        # 냉매 필터
        low = self.refrigerant_freq_range[0] / nyquist
        high = self.refrigerant_freq_range[1] / nyquist
        self._filter_cache['refrigerant'] = butter(4, [low, high], btype='band')
    
    def load_audio_optimized(self, file_path: str, duration: Optional[float] = None) -> Tuple[np.ndarray, int]:
        """최적화된 오디오 로드"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
            
            # 메모리 효율적인 로드
            y, sr = librosa.load(file_path, sr=self.sample_rate, duration=duration, mono=True)
            
            if len(y) == 0:
                raise ValueError("빈 오디오 파일입니다.")
            
            return y, sr
            
        except Exception as e:
            print(f"오디오 로드 오류: {e}")
            return None, None
    
    def load_audio_streaming(self, file_path: str, chunk_duration: float = 1.0) -> Generator:
        """스트리밍 오디오 로드 (청크 단위)"""
        try:
            # 오디오 파일 정보 가져오기
            info = librosa.get_duration(filename=file_path)
            total_duration = info
            
            chunk_samples = int(self.sample_rate * chunk_duration)
            current_time = 0.0
            
            while current_time < total_duration:
                # 청크 로드
                y, sr = librosa.load(file_path, sr=self.sample_rate, 
                                   offset=current_time, duration=chunk_duration)
                
                if len(y) == 0:
                    break
                
                yield y, sr, current_time
                current_time += chunk_duration
                
        except Exception as e:
            print(f"스트리밍 로드 오류: {e}")
            return
    
    def apply_bandpass_filter_cached(self, audio: np.ndarray, filter_type: str) -> np.ndarray:
        """캐시된 필터 적용"""
        try:
            if filter_type not in self._filter_cache:
                raise ValueError(f"지원하지 않는 필터 타입: {filter_type}")
            
            b, a = self._filter_cache[filter_type]
            return filtfilt(b, a, audio)
            
        except Exception as e:
            print(f"필터 적용 오류: {e}")
            return audio
    
    def remove_background_noise_optimized(self, audio: np.ndarray, 
                                        noise_reduction_factor: float = 0.1) -> np.ndarray:
        """최적화된 배경 소음 제거"""
        try:
            # 1. 중간값 필터 (벡터화된 연산)
            filtered_audio = medfilt(audio, kernel_size=5)
            
            # 2. Wiener 필터
            filtered_audio = wiener(filtered_audio, noise=noise_reduction_factor)
            
            # 3. 스펙트럼 서브트랙션 (FFT 최적화)
            fft = np.fft.fft(filtered_audio)
            magnitude = np.abs(fft)
            phase = np.angle(fft)
            
            # 벡터화된 노이즈 제거
            noise_threshold = np.percentile(magnitude, 20)
            noise_mask = magnitude < noise_threshold
            magnitude[noise_mask] *= 0.1
            
            # 역 FFT
            cleaned_fft = magnitude * np.exp(1j * phase)
            cleaned_audio = np.real(np.fft.ifft(cleaned_fft))
            
            return cleaned_audio
            
        except Exception as e:
            print(f"배경 소음 제거 오류: {e}")
            return audio
    
    def separate_audio_optimized(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        """최적화된 소리 분리 (한 번만 처리)"""
        try:
            # 캐시된 필터 사용
            compressor_audio = self.apply_bandpass_filter_cached(audio, 'compressor')
            refrigerant_audio = self.apply_bandpass_filter_cached(audio, 'refrigerant')
            
            return {
                'original': audio,
                'compressor': compressor_audio,
                'refrigerant': refrigerant_audio
            }
            
        except Exception as e:
            print(f"소리 분리 오류: {e}")
            return {'original': audio, 'compressor': audio, 'refrigerant': audio}
    
    def extract_features_batch(self, separated_audio: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """배치 특성 추출 (한 번에 모든 특성 추출)"""
        try:
            features = {}
            
            # 각 오디오에 대해 특성 추출
            for audio_type, audio in separated_audio.items():
                # MFCC 추출
                mfccs = self._extract_mfccs_fast(audio)
                features[f'mfccs_{audio_type}'] = mfccs
                
                # 스펙트럼 특성 추출
                spectral_features = self._extract_spectral_features_fast(audio)
                features[f'spectral_{audio_type}'] = spectral_features
            
            # 압축기 주기 분석 (compressor 오디오만)
            if 'compressor' in separated_audio:
                compressor_cycle = self._analyze_compressor_cycle_fast(separated_audio['compressor'])
                features['compressor_cycle'] = compressor_cycle
            
            # 시간적 특성 (original 오디오만)
            if 'original' in separated_audio:
                temporal_features = self._extract_temporal_features_fast(separated_audio['original'])
                features['temporal'] = temporal_features
            
            return features
            
        except Exception as e:
            print(f"배치 특성 추출 오류: {e}")
            return {}
    
    def _extract_mfccs_fast(self, audio: np.ndarray) -> np.ndarray:
        """빠른 MFCC 추출"""
        try:
            mfccs = librosa.feature.mfcc(
                y=audio, sr=self.sample_rate, n_mfcc=self.n_mfcc,
                n_fft=2048, hop_length=512, n_mels=128
            )
            
            # 고정 길이 조정
            if mfccs.shape[1] > self.feature_length:
                mfccs = mfccs[:, :self.feature_length]
            else:
                pad_width = self.feature_length - mfccs.shape[1]
                mfccs = np.pad(mfccs, ((0, 0), (0, pad_width)), mode='constant')
            
            return mfccs
            
        except Exception as e:
            print(f"MFCC 추출 오류: {e}")
            return None
    
    def _extract_spectral_features_fast(self, audio: np.ndarray) -> Dict[str, float]:
        """빠른 스펙트럼 특성 추출"""
        try:
            # 한 번의 FFT로 모든 스펙트럼 특성 계산
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            
            # 스펙트럼 중심
            spectral_centroids = librosa.feature.spectral_centroid(S=magnitude, sr=self.sample_rate)
            
            # 스펙트럼 롤오프
            spectral_rolloff = librosa.feature.spectral_rolloff(S=magnitude, sr=self.sample_rate)
            
            # 제로 크로싱 레이트
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)
            
            # 스펙트럼 대역폭
            spectral_bandwidth = librosa.feature.spectral_bandwidth(S=magnitude, sr=self.sample_rate)
            
            # 스펙트럼 평탄도
            spectral_flatness = librosa.feature.spectral_flatness(S=magnitude)
            
            # 스펙트럼 대비
            spectral_contrast = librosa.feature.spectral_contrast(S=magnitude, sr=self.sample_rate)
            
            return {
                'spectral_centroid_mean': np.mean(spectral_centroids),
                'spectral_centroid_std': np.std(spectral_centroids),
                'spectral_rolloff_mean': np.mean(spectral_rolloff),
                'zero_crossing_rate_mean': np.mean(zero_crossing_rate),
                'zero_crossing_rate_std': np.std(zero_crossing_rate),
                'spectral_bandwidth_mean': np.mean(spectral_bandwidth),
                'spectral_flatness_mean': np.mean(spectral_flatness),
                'spectral_contrast_mean': np.mean(spectral_contrast)
            }
            
        except Exception as e:
            print(f"스펙트럼 특성 추출 오류: {e}")
            return {}
    
    def _analyze_compressor_cycle_fast(self, compressor_audio: np.ndarray) -> Dict[str, float]:
        """빠른 압축기 주기 분석"""
        try:
            # RMS 에너지 계산
            rms = librosa.feature.rms(y=compressor_audio, hop_length=512)[0]
            
            # 피크 감지
            peaks, _ = scipy.signal.find_peaks(rms, height=np.mean(rms), distance=10)
            
            if len(peaks) > 1:
                peak_intervals = np.diff(peaks)
                cycle_period = np.mean(peak_intervals) * 512 / self.sample_rate
                cycle_frequency = 1.0 / cycle_period if cycle_period > 0 else 0
                cycle_stability = 1.0 / (1.0 + np.std(peak_intervals) / np.mean(peak_intervals))
            else:
                cycle_period = cycle_frequency = cycle_stability = 0
            
            # 작동 강도 분석
            operation_intensity = np.mean(rms)
            intensity_variance = np.var(rms)
            
            # 작동 비율
            threshold = np.percentile(rms, 30)
            on_ratio = np.mean(rms > threshold)
            
            return {
                'cycle_period': cycle_period,
                'cycle_frequency': cycle_frequency,
                'cycle_stability': cycle_stability,
                'operation_intensity': operation_intensity,
                'intensity_variance': intensity_variance,
                'on_ratio': on_ratio,
                'peak_count': len(peaks)
            }
            
        except Exception as e:
            print(f"압축기 주기 분석 오류: {e}")
            return {}
    
    def _extract_temporal_features_fast(self, audio: np.ndarray) -> Dict[str, float]:
        """빠른 시간적 특성 추출"""
        try:
            # RMS 에너지
            rms = librosa.feature.rms(y=audio)[0]
            rms_mean = np.mean(rms)
            rms_std = np.std(rms)
            
            # 에너지 변화율
            rms_diff = np.diff(rms)
            energy_change_rate = np.mean(np.abs(rms_diff))
            
            # 오디오 길이
            duration = len(audio) / self.sample_rate
            
            # 신호 대 잡음비
            signal_power = np.mean(audio ** 2)
            noise_power = np.var(audio - np.mean(audio))
            snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
            
            # 신호 복잡도 (샘플 엔트로피)
            def sample_entropy(data, m=2, r=0.2):
                N = len(data)
                B = A = 0.0
                
                for i in range(N - m):
                    template_i = data[i:i + m]
                    for j in range(i + 1, N - m):
                        template_j = data[j:j + m]
                        if np.max(np.abs(template_i - template_j)) <= r * np.std(data):
                            B += 1
                            if np.abs(data[i + m] - data[j + m]) <= r * np.std(data):
                                A += 1
                
                return -np.log(A / B) if B > 0 else 0
            
            complexity = sample_entropy(audio[:min(1000, len(audio))])
            
            return {
                'rms_mean': rms_mean,
                'rms_std': rms_std,
                'energy_change_rate': energy_change_rate,
                'duration': duration,
                'snr': snr,
                'complexity': complexity
            }
            
        except Exception as e:
            print(f"시간적 특성 추출 오류: {e}")
            return {}
    
    def preprocess_audio_optimized(self, file_path: str, save_features: bool = False, 
                                 output_dir: str = "extracted_features") -> Dict:
        """최적화된 오디오 전처리"""
        try:
            print(f"최적화된 오디오 전처리 시작: {file_path}")
            
            # 1. 오디오 로드
            audio, sr = self.load_audio_optimized(file_path)
            if audio is None:
                return {'success': False, 'error': '오디오 로드 실패'}
            
            # 2. 배경 소음 제거
            cleaned_audio = self.remove_background_noise_optimized(audio)
            
            # 3. 소리 분리 (한 번만 처리)
            separated_audio = self.separate_audio_optimized(cleaned_audio)
            
            # 4. 배치 특성 추출 (한 번에 모든 특성 추출)
            features = self.extract_features_batch(separated_audio)
            
            # 5. 결과 정리
            result = {
                'success': True,
                'file_path': file_path,
                'sample_rate': sr,
                'duration': len(audio) / sr,
                'features': features,
                'audio_length': len(audio)
            }
            
            # 6. 특성 저장
            if save_features:
                os.makedirs(output_dir, exist_ok=True)
                feature_file = os.path.join(output_dir, f"{os.path.basename(file_path)}_features.npz")
                np.savez_compressed(feature_file, **features)
                result['feature_file'] = feature_file
                print(f"특성 저장 완료: {feature_file}")
            
            print("최적화된 오디오 전처리 완료!")
            return result
            
        except Exception as e:
            print(f"오디오 전처리 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_audio_streaming(self, file_path: str, chunk_duration: float = 2.0, 
                              callback_func=None) -> Generator:
        """스트리밍 오디오 처리"""
        try:
            print(f"스트리밍 오디오 처리 시작: {file_path}")
            
            for chunk_audio, sr, current_time in self.load_audio_streaming(file_path, chunk_duration):
                # 청크 전처리
                cleaned_audio = self.remove_background_noise_optimized(chunk_audio)
                separated_audio = self.separate_audio_optimized(cleaned_audio)
                features = self.extract_features_batch(separated_audio)
                
                result = {
                    'success': True,
                    'chunk_time': current_time,
                    'chunk_duration': chunk_duration,
                    'features': features,
                    'audio_length': len(chunk_audio)
                }
                
                # 콜백 호출
                if callback_func:
                    callback_func(result)
                
                yield result
                
        except Exception as e:
            print(f"스트리밍 처리 오류: {e}")
            yield {'success': False, 'error': str(e)}

# 사용 예제
if __name__ == "__main__":
    # 최적화된 전처리기 생성
    preprocessor = OptimizedSignalPreprocessor()
    
    # 샘플 오디오 파일 경로
    audio_file = "sample_refrigerant_audio.wav"
    
    if os.path.exists(audio_file):
        # 최적화된 전처리
        result = preprocessor.preprocess_audio_optimized(
            audio_file, 
            save_features=True,
            output_dir="extracted_features"
        )
        
        if result['success']:
            print("최적화된 전처리 성공!")
            print(f"오디오 길이: {result['duration']:.2f}초")
            
            # 스트리밍 처리 예제
            print("\n스트리밍 처리 예제:")
            for chunk_result in preprocessor.process_audio_streaming(audio_file, chunk_duration=1.0):
                if chunk_result['success']:
                    print(f"청크 시간: {chunk_result['chunk_time']:.1f}초")
                else:
                    print(f"청크 처리 실패: {chunk_result['error']}")
    else:
        print("샘플 오디오 파일이 없습니다.")
