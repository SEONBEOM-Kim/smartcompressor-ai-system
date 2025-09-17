# lightweight_compressor_ai.py
import numpy as np
import librosa
import time
from scipy import signal
from scipy.signal import butter, filtfilt

class LightweightCompressorAI:
    def __init__(self):
        """경량화 압축기 AI 진단 시스템 초기화"""
        # 베어링 마모로 인한 고주파 소음 감지를 위한 설정
        self.overload_freq_range = (500, 2000)  # 중고주파수 대역 (베어링 소리)
        self.overload_threshold = 0.5  # 더 민감한 반응을 위한 낮은 임계값
        self.sample_rate = 16000
        self.n_fft = 1024
        self.hop_length = 512
        
        print("�� 베어링 마모 감지 AI 모델 초기화 완료")
        print(f"📊 감지 주파수 대역: {self.overload_freq_range} Hz")
        print(f"�� 감지 임계값: {self.overload_threshold}")
    
    def preprocess_audio(self, audio_data, sr):
        """오디오 전처리"""
        try:
            # 16kHz로 리샘플링
            if sr != self.sample_rate:
                audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=self.sample_rate)
            
            # 노이즈 필터링 (고주파 노이즈 제거)
            nyquist = self.sample_rate / 2
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
            print(f"❌ 오디오 전처리 오류: {e}")
            return audio_data
    
    def extract_simple_features(self, audio_data, sr):
        """간단한 특징 추출"""
        try:
            # RMS 에너지
            rms_energy = np.sqrt(np.mean(audio_data ** 2))
            
            # 주파수 도메인 분석
            stft = librosa.stft(audio_data, n_fft=self.n_fft, hop_length=self.hop_length)
            magnitude = np.abs(stft)
            frequencies = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)
            
            # 특정 주파수 대역의 에너지 비율
            freq_mask = (frequencies >= self.overload_freq_range[0]) & (frequencies <= self.overload_freq_range[1])
            target_energy = np.sum(magnitude[freq_mask, :])
            total_energy = np.sum(magnitude)
            
            if total_energy > 0:
                overload_ratio = target_energy / total_energy
            else:
                overload_ratio = 0
            
            # Zero Crossing Rate (ZCR) - 날카로운 소음 감지
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data, hop_length=self.hop_length))
            
            # 스펙트럼 중심 (Spectral Centroid) - 고주파 성분 감지
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr, hop_length=self.hop_length))
            
            # 스펙트럼 롤오프 (Spectral Rolloff) - 고주파 에너지 분포
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr, hop_length=self.hop_length))
            
            features = {
                'rms_energy': rms_energy,
                'overload_ratio': overload_ratio,
                'zero_crossing_rate': zcr,
                'spectral_centroid': spectral_centroid,
                'spectral_rolloff': spectral_rolloff,
                'target_freq_energy': target_energy,
                'total_energy': total_energy
            }
            
            return features
            
        except Exception as e:
            print(f"❌ 특징 추출 오류: {e}")
            return {
                'rms_energy': 0,
                'overload_ratio': 0,
                'zero_crossing_rate': 0,
                'spectral_centroid': 0,
                'spectral_rolloff': 0,
                'target_freq_energy': 0,
                'total_energy': 0
            }
    
    def is_overload_sound(self, features):
        """베어링 마모로 인한 고주파 소음 판별"""
        try:
            rms_energy = features['rms_energy']
            overload_ratio = features['overload_ratio']
            zcr = features['zero_crossing_rate']
            spectral_centroid = features['spectral_centroid']
            spectral_rolloff = features['spectral_rolloff']
            
            # 기본 에너지 조건
            energy_condition = rms_energy > 0.01  # 최소 에너지 임계값
            
            # 주파수 대역 조건 (중고주파수 집중)
            freq_condition = overload_ratio > self.overload_threshold
            
            # Zero Crossing Rate 조건 (날카로운 소음)
            zcr_condition = zcr > 0.1  # 높은 ZCR은 날카로운 소음을 의미
            
            # 스펙트럼 중심 조건 (고주파 성분)
            centroid_condition = spectral_centroid > 1000  # 1000Hz 이상의 중심 주파수
            
            # 스펙트럼 롤오프 조건 (고주파 에너지 분포)
            rolloff_condition = spectral_rolloff > 2000  # 2000Hz 이상의 롤오프
            
            # 종합 판별 조건
            # 베어링 마모 소음은 중고주파수에 집중되고, ZCR이 높으며, 고주파 성분이 많아야 함
            is_overload = (
                energy_condition and 
                freq_condition and 
                zcr_condition and 
                (centroid_condition or rolloff_condition)
            )
            
            # 신뢰도 계산
            confidence = 0.0
            if is_overload:
                # 각 조건의 가중치를 적용한 신뢰도 계산
                confidence = (
                    min(overload_ratio * 2, 1.0) * 0.3 +  # 주파수 대역 비율
                    min(zcr * 10, 1.0) * 0.3 +            # Zero Crossing Rate
                    min(spectral_centroid / 2000, 1.0) * 0.2 +  # 스펙트럼 중심
                    min(spectral_rolloff / 4000, 1.0) * 0.2     # 스펙트럼 롤오프
                )
            else:
                # 정상 상태일 때의 신뢰도
                confidence = 1.0 - min(overload_ratio * 2, 1.0)
            
            return is_overload, confidence
            
        except Exception as e:
            print(f"❌ 소음 판별 오류: {e}")
            return False, 0.0
    
    def analyze_audio_chunk(self, audio_data, sr):
        """오디오 청크 분석"""
        try:
            start_time = time.time()
            
            # 전처리
            processed_audio = self.preprocess_audio(audio_data, sr)
            
            # 특징 추출
            features = self.extract_simple_features(processed_audio, sr)
            
            # 소음 판별
            is_overload, confidence = self.is_overload_sound(features)
            
            processing_time = (time.time() - start_time) * 1000  # ms
            
            result = {
                'is_overload': is_overload,
                'confidence': confidence,
                'processing_time_ms': processing_time,
                'message': '베어링 마모 감지됨' if is_overload else '정상 작동 중',
                'features': features,
                'diagnosis_type': 'bearing_wear_detection'
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 오디오 분석 오류: {e}")
            return {
                'is_overload': False,
                'confidence': 0.0,
                'processing_time_ms': 0,
                'message': f'분석 중 오류 발생: {str(e)}',
                'features': {},
                'diagnosis_type': 'error'
            }
    
    def analyze_audio_file(self, file_path):
        """오디오 파일 분석"""
        try:
            # 오디오 파일 로드
            audio_data, sr = librosa.load(file_path, sr=None)
            
            # 청크 단위로 분석 (5초씩)
            chunk_duration = 5.0  # 5초
            chunk_samples = int(chunk_duration * sr)
            
            results = []
            for i in range(0, len(audio_data), chunk_samples):
                chunk = audio_data[i:i + chunk_samples]
                if len(chunk) < chunk_samples:
                    break
                
                result = self.analyze_audio_chunk(chunk, sr)
                results.append(result)
            
            # 전체 결과 통합
            if results:
                # 가장 높은 신뢰도와 함께 과부하가 감지된 결과 선택
                overload_results = [r for r in results if r['is_overload']]
                if overload_results:
                    best_result = max(overload_results, key=lambda x: x['confidence'])
                else:
                    best_result = max(results, key=lambda x: x['confidence'])
                
                # 전체 처리 시간 계산
                total_processing_time = sum(r['processing_time_ms'] for r in results)
                
                return {
                    'overall_status': 'overload' if best_result['is_overload'] else 'normal',
                    'average_confidence': best_result['confidence'],
                    'total_processing_time_ms': total_processing_time,
                    'message': best_result['message'],
                    'chunk_results': results,
                    'diagnosis_type': 'bearing_wear_detection'
                }
            else:
                return {
                    'overall_status': 'normal',
                    'average_confidence': 0.0,
                    'total_processing_time_ms': 0,
                    'message': '분석할 오디오 데이터가 없습니다.',
                    'chunk_results': [],
                    'diagnosis_type': 'error'
                }
                
        except Exception as e:
            print(f"❌ 파일 분석 오류: {e}")
            return {
                'overall_status': 'normal',
                'average_confidence': 0.0,
                'total_processing_time_ms': 0,
                'message': f'파일 분석 중 오류 발생: {str(e)}',
                'chunk_results': [],
                'diagnosis_type': 'error'
            }

# 사용 예시
if __name__ == "__main__":
    # AI 모델 초기화
    ai = LightweightCompressorAI()
    
    # 테스트 오디오 파일 분석
    test_file = "test_audio.wav"
    if os.path.exists(test_file):
        result = ai.analyze_audio_file(test_file)
        print(f" 진단 결과: {result['overall_status']}")
        print(f" 신뢰도: {result['average_confidence']:.2f}")
        print(f" 메시지: {result['message']}")
    else:
        print("❌ 테스트 파일이 없습니다.")
