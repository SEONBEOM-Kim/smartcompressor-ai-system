#!/usr/bin/env python3
"""
ESP32 데이터 처리 최적화 서비스
실시간 오디오 데이터를 효율적으로 처리하고 성능을 최적화합니다.
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ESP32Device:
    """ESP32 디바이스 정보"""
    device_id: str
    ip_address: str
    last_seen: float
    status: str
    sample_rate: int = 16000
    buffer_size: int = 1024

@dataclass
class AudioChunk:
    """오디오 청크 데이터"""
    device_id: str
    timestamp: float
    data: np.ndarray
    sample_rate: int
    priority: int = 1  # 1: 정상, 2: 주의, 3: 긴급

class ESP32Optimizer:
    """ESP32 데이터 처리 최적화 클래스"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.audio_queue = queue.PriorityQueue()
        self.devices: Dict[str, ESP32Device] = {}
        self.is_processing = False
        self.processing_thread = None
        
        # 성능 메트릭
        self.metrics = {
            'processed_chunks': 0,
            'failed_chunks': 0,
            'avg_processing_time': 0.0,
            'queue_size': 0,
            'active_devices': 0
        }
        
        # 처리 시작
        self.start_processing()
    
    def register_device(self, device_id: str, ip_address: str, sample_rate: int = 16000) -> bool:
        """ESP32 디바이스 등록"""
        try:
            device = ESP32Device(
                device_id=device_id,
                ip_address=ip_address,
                last_seen=time.time(),
                status='connected',
                sample_rate=sample_rate
            )
            self.devices[device_id] = device
            self.metrics['active_devices'] = len(self.devices)
            logger.info(f"ESP32 디바이스 등록: {device_id} ({ip_address})")
            return True
        except Exception as e:
            logger.error(f"디바이스 등록 실패: {e}")
            return False
    
    def add_audio_chunk(self, device_id: str, audio_data: bytes, sample_rate: int, priority: int = 1):
        """오디오 청크 추가 (비동기)"""
        try:
            # 바이트 데이터를 numpy 배열로 변환
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            chunk = AudioChunk(
                device_id=device_id,
                timestamp=time.time(),
                data=audio_array,
                sample_rate=sample_rate,
                priority=priority
            )
            
            # 우선순위 큐에 추가 (우선순위가 높을수록 먼저 처리)
            self.audio_queue.put((priority, chunk))
            self.metrics['queue_size'] = self.audio_queue.qsize()
            
            # 디바이스 상태 업데이트
            if device_id in self.devices:
                self.devices[device_id].last_seen = time.time()
                self.devices[device_id].status = 'active'
            
        except Exception as e:
            logger.error(f"오디오 청크 추가 실패: {e}")
            self.metrics['failed_chunks'] += 1
    
    def start_processing(self):
        """오디오 처리 시작"""
        if not self.is_processing:
            self.is_processing = True
            self.processing_thread = threading.Thread(target=self._process_audio_loop)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            logger.info("ESP32 오디오 처리 시작")
    
    def stop_processing(self):
        """오디오 처리 중지"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join()
        logger.info("ESP32 오디오 처리 중지")
    
    def _process_audio_loop(self):
        """오디오 처리 루프 (별도 스레드에서 실행)"""
        while self.is_processing:
            try:
                # 큐에서 오디오 청크 가져오기 (타임아웃 1초)
                priority, chunk = self.audio_queue.get(timeout=1.0)
                
                # 비동기로 처리
                future = self.executor.submit(self._process_single_chunk, chunk)
                
                # 메트릭 업데이트
                self.metrics['queue_size'] = self.audio_queue.qsize()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"오디오 처리 루프 오류: {e}")
                time.sleep(0.1)
    
    def _process_single_chunk(self, chunk: AudioChunk) -> Dict:
        """단일 오디오 청크 처리"""
        start_time = time.time()
        
        try:
            # 기본 품질 검사
            if not self._validate_audio_chunk(chunk):
                logger.warning(f"오디오 청크 품질 검사 실패: {chunk.device_id}")
                return {'status': 'error', 'message': 'Invalid audio data'}
            
            # 오디오 전처리
            processed_audio = self._preprocess_audio(chunk.data, chunk.sample_rate)
            
            # AI 분석 (간소화된 버전)
            analysis_result = self._quick_analysis(processed_audio)
            
            # 결과 반환
            result = {
                'status': 'success',
                'device_id': chunk.device_id,
                'timestamp': chunk.timestamp,
                'analysis': analysis_result,
                'processing_time': time.time() - start_time
            }
            
            # 메트릭 업데이트
            self.metrics['processed_chunks'] += 1
            processing_time = time.time() - start_time
            self.metrics['avg_processing_time'] = (
                (self.metrics['avg_processing_time'] * (self.metrics['processed_chunks'] - 1) + processing_time) 
                / self.metrics['processed_chunks']
            )
            
            return result
            
        except Exception as e:
            logger.error(f"오디오 청크 처리 실패: {e}")
            self.metrics['failed_chunks'] += 1
            return {'status': 'error', 'message': str(e)}
    
    def _validate_audio_chunk(self, chunk: AudioChunk) -> bool:
        """오디오 청크 품질 검사"""
        try:
            # 데이터 길이 확인
            if len(chunk.data) < 100:  # 최소 100 샘플
                return False
            
            # 샘플링 레이트 확인
            if chunk.sample_rate not in [8000, 16000, 44100, 48000]:
                return False
            
            # 데이터 범위 확인 (16비트 오디오)
            if np.max(np.abs(chunk.data)) > 32767:
                return False
            
            return True
        except:
            return False
    
    def _preprocess_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """오디오 전처리"""
        try:
            # 정규화
            audio_normalized = audio_data.astype(np.float32) / 32768.0
            
            # 리샘플링 (16kHz로 통일)
            if sample_rate != 16000:
                from scipy import signal
                audio_normalized = signal.resample(audio_normalized, int(len(audio_normalized) * 16000 / sample_rate))
            
            # 노이즈 제거 (간단한 고역 통과 필터)
            from scipy import signal
            b, a = signal.butter(4, 0.01, 'high')
            audio_filtered = signal.filtfilt(b, a, audio_normalized)
            
            return audio_filtered
            
        except Exception as e:
            logger.error(f"오디오 전처리 실패: {e}")
            return audio_data.astype(np.float32) / 32768.0
    
    def _quick_analysis(self, audio_data: np.ndarray) -> Dict:
        """빠른 AI 분석 (간소화된 버전)"""
        try:
            # 기본 통계 계산
            rms = np.sqrt(np.mean(audio_data**2))
            zcr = np.mean(np.diff(np.sign(audio_data)) != 0)
            spectral_centroid = np.mean(np.abs(np.fft.fft(audio_data)))
            
            # 간단한 이상 감지
            is_anomaly = False
            confidence = 0.5
            
            if rms > 0.1:  # 높은 볼륨
                is_anomaly = True
                confidence = 0.8
            elif zcr > 0.3:  # 높은 제로 크로싱
                is_anomaly = True
                confidence = 0.7
            
            return {
                'is_anomaly': is_anomaly,
                'confidence': confidence,
                'rms': float(rms),
                'zcr': float(zcr),
                'spectral_centroid': float(spectral_centroid),
                'analysis_type': 'quick'
            }
            
        except Exception as e:
            logger.error(f"빠른 분석 실패: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def get_metrics(self) -> Dict:
        """성능 메트릭 반환"""
        return {
            **self.metrics,
            'queue_size': self.audio_queue.qsize(),
            'active_devices': len([d for d in self.devices.values() if d.status == 'active'])
        }
    
    def get_device_status(self, device_id: str) -> Optional[Dict]:
        """특정 디바이스 상태 반환"""
        if device_id not in self.devices:
            return None
        
        device = self.devices[device_id]
        return {
            'device_id': device.device_id,
            'ip_address': device.ip_address,
            'status': device.status,
            'last_seen': device.last_seen,
            'sample_rate': device.sample_rate,
            'is_online': time.time() - device.last_seen < 60  # 1분 이내
        }
    
    def cleanup_old_devices(self, timeout: int = 300):
        """오래된 디바이스 정리 (5분 이상 비활성)"""
        current_time = time.time()
        devices_to_remove = []
        
        for device_id, device in self.devices.items():
            if current_time - device.last_seen > timeout:
                devices_to_remove.append(device_id)
        
        for device_id in devices_to_remove:
            del self.devices[device_id]
            logger.info(f"비활성 디바이스 제거: {device_id}")
        
        self.metrics['active_devices'] = len(self.devices)

# 전역 인스턴스
esp32_optimizer = ESP32Optimizer()
