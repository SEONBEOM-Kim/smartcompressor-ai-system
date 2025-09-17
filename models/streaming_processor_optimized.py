import numpy as np
import librosa
import scipy.signal
from collections import deque
from typing import Dict, List, Optional, Callable, Generator
import threading
import queue
import time
import sounddevice as sd
import soundfile as sf
from models.optimized_signal_preprocessing import OptimizedSignalPreprocessor

class OptimizedStreamingProcessor:
    def __init__(self, sample_rate: int = 22050, chunk_size: int = 1024, 
                 buffer_duration: float = 5.0):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.buffer_duration = buffer_duration
        self.buffer_size = int(sample_rate * buffer_duration)
        
        # 최적화된 전처리기
        self.preprocessor = OptimizedSignalPreprocessor(sample_rate)
        
        # 실시간 버퍼
        self.audio_buffer = deque(maxlen=self.buffer_size)
        self.feature_buffer = deque(maxlen=100)
        
        # 스트리밍 상태
        self.is_streaming = False
        self.stream_thread = None
        self.analysis_thread = None
        self.callbacks = []
        
        # 실시간 분석 설정
        self.analysis_interval = 1.0  # 1초마다 분석
        self.last_analysis_time = 0
        
        # 성능 최적화를 위한 캐시
        self._feature_cache = {}
        self._cache_size = 50
    
    def start_microphone_stream(self, device_id: Optional[int] = None):
        """마이크로부터 실시간 스트림 시작"""
        try:
            if self.is_streaming:
                print("이미 스트리밍 중입니다.")
                return
            
            self.is_streaming = True
            
            # 오디오 스트림 설정
            self.audio_stream = sd.InputStream(
                device=device_id,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            
            # 스트림 시작
            self.audio_stream.start()
            
            # 분석 스레드 시작
            self.analysis_thread = threading.Thread(target=self._analysis_loop)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            print(f"마이크 스트림 시작: {self.sample_rate}Hz, 청크 크기: {self.chunk_size}")
            
        except Exception as e:
            print(f"마이크 스트림 시작 오류: {e}")
            self.is_streaming = False
    
    def start_file_stream(self, file_path: str, chunk_duration: float = 1.0):
        """파일로부터 실시간 스트림 시작"""
        try:
            if self.is_streaming:
                print("이미 스트리밍 중입니다.")
                return
            
            self.is_streaming = True
            
            # 파일 스트림 스레드 시작
            self.stream_thread = threading.Thread(
                target=self._file_stream_loop, 
                args=(file_path, chunk_duration)
            )
            self.stream_thread.daemon = True
            self.stream_thread.start()
            
            # 분석 스레드 시작
            self.analysis_thread = threading.Thread(target=self._analysis_loop)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            
            print(f"파일 스트림 시작: {file_path}")
            
        except Exception as e:
            print(f"파일 스트림 시작 오류: {e}")
            self.is_streaming = False
    
    def stop_streaming(self):
        """스트리밍 중지"""
        try:
            self.is_streaming = False
            
            # 오디오 스트림 중지
            if hasattr(self, 'audio_stream'):
                self.audio_stream.stop()
                self.audio_stream.close()
            
            # 스레드 대기
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=1.0)
            
            if self.analysis_thread and self.analysis_thread.is_alive():
                self.analysis_thread.join(timeout=1.0)
            
            print("스트리밍 중지 완료")
            
        except Exception as e:
            print(f"스트리밍 중지 오류: {e}")
    
    def _audio_callback(self, indata, frames, time, status):
        """오디오 콜백 (마이크 스트림용)"""
        if status:
            print(f"오디오 스트림 상태: {status}")
        
        # 오디오 데이터를 버퍼에 추가
        audio_chunk = indata[:, 0]  # 모노 채널
        self.audio_buffer.extend(audio_chunk)
    
    def _file_stream_loop(self, file_path: str, chunk_duration: float):
        """파일 스트림 루프"""
        try:
            for chunk_audio, sr, current_time in self.preprocessor.load_audio_streaming(
                file_path, chunk_duration
            ):
                if not self.is_streaming:
                    break
                
                # 오디오 데이터를 버퍼에 추가
                self.audio_buffer.extend(chunk_audio)
                
                # 스트리밍 속도 조절
                time.sleep(chunk_duration * 0.1)  # 실제 시간보다 빠르게 재생
                
        except Exception as e:
            print(f"파일 스트림 루프 오류: {e}")
    
    def _analysis_loop(self):
        """실시간 분석 루프"""
        while self.is_streaming:
            try:
                current_time = time.time()
                
                # 분석 간격 체크
                if current_time - self.last_analysis_time < self.analysis_interval:
                    time.sleep(0.1)
                    continue
                
                # 충분한 데이터가 있는지 확인
                if len(self.audio_buffer) < self.sample_rate * 2:  # 최소 2초
                    time.sleep(0.1)
                    continue
                
                # 최근 데이터 추출
                recent_audio = np.array(list(self.audio_buffer))[-self.sample_rate * 5:]
                
                # 실시간 분석
                analysis_result = self._analyze_realtime_audio(recent_audio)
                
                # 결과를 버퍼에 추가
                self.feature_buffer.append(analysis_result)
                
                # 콜백 호출
                for callback in self.callbacks:
                    try:
                        callback(analysis_result)
                    except Exception as e:
                        print(f"콜백 오류: {e}")
                
                self.last_analysis_time = current_time
                
            except Exception as e:
                print(f"분석 루프 오류: {e}")
                time.sleep(0.1)
    
    def _analyze_realtime_audio(self, audio: np.ndarray) -> Dict:
        """실시간 오디오 분석 (최적화된 버전)"""
        try:
            # 캐시 키 생성
            cache_key = hash(audio.tobytes())
            
            # 캐시 확인
            if cache_key in self._feature_cache:
                cached_result = self._feature_cache[cache_key]
                cached_result['timestamp'] = time.time()
                return cached_result
            
            # 1. 빠른 전처리
            cleaned_audio = self.preprocessor.remove_background_noise_optimized(audio)
            separated_audio = self.preprocessor.separate_audio_optimized(cleaned_audio)
            
            # 2. 핵심 특성만 추출 (실시간 최적화)
            features = self._extract_realtime_features(separated_audio)
            
            # 3. 실시간 이상 감지
            anomaly_score = self._detect_realtime_anomaly_fast(features)
            
            # 4. 압축기 상태 분석
            compressor_status = self._analyze_compressor_status_fast(features)
            
            # 5. 냉매 누출 가능성 평가
            leak_probability = self._assess_leak_probability_fast(features)
            
            result = {
                'timestamp': time.time(),
                'anomaly_score': anomaly_score,
                'compressor_status': compressor_status,
                'leak_probability': leak_probability,
                'features': features,
                'alert_level': self._determine_alert_level(anomaly_score, leak_probability)
            }
            
            # 캐시에 저장 (크기 제한)
            if len(self._feature_cache) >= self._cache_size:
                # 가장 오래된 항목 제거
                oldest_key = next(iter(self._feature_cache))
                del self._feature_cache[oldest_key]
            
            self._feature_cache[cache_key] = result.copy()
            
            return result
            
        except Exception as e:
            print(f"실시간 분석 오류: {e}")
            return {
                'timestamp': time.time(),
                'anomaly_score': 0,
                'compressor_status': 'unknown',
                'leak_probability': 0,
                'alert_level': 'normal'
            }
    
    def _extract_realtime_features(self, separated_audio: Dict[str, np.ndarray]) -> Dict:
        """실시간 특성 추출 (최적화된 버전)"""
        try:
            features = {}
            
            # 각 오디오에 대해 핵심 특성만 추출
            for audio_type, audio in separated_audio.items():
                # RMS 에너지 (가장 빠른 특성)
                rms = librosa.feature.rms(y=audio)[0]
                features[f'rms_{audio_type}'] = np.mean(rms)
                
                # 스펙트럼 중심 (빠른 특성)
                spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)
                features[f'spectral_centroid_{audio_type}'] = np.mean(spectral_centroid)
                
                # 제로 크로싱 레이트 (빠른 특성)
                zcr = librosa.feature.zero_crossing_rate(audio)
                features[f'zcr_{audio_type}'] = np.mean(zcr)
            
            # 압축기 주기 분석 (compressor 오디오만)
            if 'compressor' in separated_audio:
                compressor_cycle = self.preprocessor._analyze_compressor_cycle_fast(
                    separated_audio['compressor']
                )
                features['compressor_cycle'] = compressor_cycle
            
            return features
            
        e
