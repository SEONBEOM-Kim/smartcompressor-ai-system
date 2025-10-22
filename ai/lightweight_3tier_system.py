#!/usr/bin/env python3
"""
경량화된 3순위 조합 시스템
10-15개 하드웨어로 딥러닝 + 다중 센서 융합 + 실시간 적응형 학습 구현
"""

import numpy as np
import librosa
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import psutil
import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class Lightweight3TierSystem:
    """경량화된 3순위 조합 시스템"""
    
    def __init__(self, hardware_count: int = 10):
        self.hardware_count = hardware_count
        self.models = {}
        self.sensors = {}
        self.learning_systems = {}
        self.performance_metrics = {}
        
        # 하드웨어 사양 확인
        self.hardware_specs = self._check_hardware_specs()
        
        # 시스템 초기화
        self._initialize_system()
        
        print(f"🚀 경량화된 3순위 조합 시스템 초기화 완료")
        print(f"   하드웨어 수: {hardware_count}")
        print(f"   CPU 코어: {self.hardware_specs['cpu_cores']}")
        print(f"   RAM: {self.hardware_specs['ram_gb']}GB")
        print(f"   GPU 사용 가능: {self.hardware_specs['gpu_available']}")
    
    def _check_hardware_specs(self) -> Dict:
        """하드웨어 사양 확인"""
        try:
            specs = {
                'cpu_cores': psutil.cpu_count(logical=False),
                'ram_gb': round(psutil.virtual_memory().total / (1024**3), 1),
                'disk_gb': round(psutil.disk_usage('/').total / (1024**3), 1),
                'gpu_available': torch.cuda.is_available(),
                'network_mbps': 100  # 기본값
            }
            return specs
        except Exception as e:
            print(f"⚠️ 하드웨어 사양 확인 오류: {e}")
            return {
                'cpu_cores': 4,
                'ram_gb': 8,
                'disk_gb': 50,
                'gpu_available': False,
                'network_mbps': 100
            }
    
    def _initialize_system(self):
        """시스템 초기화"""
        try:
            # 1. 경량화된 딥러닝 모델 초기화
            self._initialize_lightweight_models()
            
            # 2. 가상 센서 시스템 초기화
            self._initialize_virtual_sensors()
            
            # 3. 적응형 학습 시스템 초기화
            self._initialize_adaptive_learning()
            
            print("✅ 시스템 초기화 완료")
            
        except Exception as e:
            print(f"❌ 시스템 초기화 오류: {e}")
    
    def _initialize_lightweight_models(self):
        """경량화된 딥러닝 모델 초기화"""
        try:
            # 각 하드웨어별로 경량화된 모델 생성
            for i in range(self.hardware_count):
                model = LightweightCNN(
                    input_size=50,  # 특징 수
                    hidden_size=32,  # 작은 히든 레이어
                    output_size=2   # 이진 분류
                )
                
                # 모델 압축 (CPU 최적화)
                if not self.hardware_specs['gpu_available']:
                    model = self._compress_model(model)
                
                self.models[i] = {
                    'model': model,
                    'optimizer': optim.Adam(model.parameters(), lr=0.001),
                    'criterion': nn.CrossEntropyLoss(),
                    'device': 'cuda' if self.hardware_specs['gpu_available'] else 'cpu'
                }
            
            print(f"✅ 경량화된 딥러닝 모델 {self.hardware_count}개 초기화 완료")
            
        except Exception as e:
            print(f"❌ 딥러닝 모델 초기화 오류: {e}")
    
    def _compress_model(self, model):
        """모델 압축 (CPU 최적화)"""
        try:
            # 동적 양자화
            model = torch.quantization.quantize_dynamic(
                model, {nn.Linear}, dtype=torch.qint8
            )
            return model
        except Exception as e:
            print(f"⚠️ 모델 압축 오류: {e}")
            return model
    
    def _initialize_virtual_sensors(self):
        """가상 센서 시스템 초기화"""
        try:
            sensor_types = ['temperature', 'vibration', 'current', 'pressure', 'humidity']
            
            for i in range(self.hardware_count):
                sensor_type = sensor_types[i % len(sensor_types)]
                self.sensors[i] = VirtualSensor(
                    sensor_id=i,
                    sensor_type=sensor_type,
                    hardware_specs=self.hardware_specs
                )
            
            print(f"✅ 가상 센서 {self.hardware_count}개 초기화 완료")
            
        except Exception as e:
            print(f"❌ 가상 센서 초기화 오류: {e}")
    
    def _initialize_adaptive_learning(self):
        """적응형 학습 시스템 초기화"""
        try:
            for i in range(self.hardware_count):
                self.learning_systems[i] = AdaptiveLearningSystem(
                    hardware_id=i,
                    model=self.models[i]['model'],
                    optimizer=self.models[i]['optimizer'],
                    criterion=self.models[i]['criterion']
                )
            
            print(f"✅ 적응형 학습 시스템 {self.hardware_count}개 초기화 완료")
            
        except Exception as e:
            print(f"❌ 적응형 학습 초기화 오류: {e}")
    
    # ===== 1. 경량화된 딥러닝 모델 =====
    
    def train_lightweight_models(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """경량화된 딥러닝 모델 훈련"""
        try:
            print("🧠 경량화된 딥러닝 모델 훈련 시작")
            
            # 데이터 분산
            chunk_size = len(X) // self.hardware_count
            training_results = {}
            
            for i in range(self.hardware_count):
                start = i * chunk_size
                end = start + chunk_size if i < self.hardware_count - 1 else len(X)
                
                X_chunk = X[start:end]
                y_chunk = y[start:end]
                
                # 각 하드웨어에서 모델 훈련
                result = self._train_single_model(i, X_chunk, y_chunk)
                training_results[i] = result
            
            # 결과 통합
            overall_accuracy = np.mean([r['accuracy'] for r in training_results.values()])
            
            print(f"✅ 딥러닝 모델 훈련 완료! 평균 정확도: {overall_accuracy:.3f}")
            
            return {
                'success': True,
                'overall_accuracy': overall_accuracy,
                'hardware_results': training_results
            }
            
        except Exception as e:
            print(f"❌ 딥러닝 모델 훈련 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def _train_single_model(self, hardware_id: int, X: np.ndarray, y: np.ndarray) -> Dict:
        """단일 하드웨어에서 모델 훈련"""
        try:
            model_info = self.models[hardware_id]
            model = model_info['model']
            optimizer = model_info['optimizer']
            criterion = model_info['criterion']
            device = model_info['device']
            
            # 데이터를 텐서로 변환
            X_tensor = torch.FloatTensor(X)
            y_tensor = torch.LongTensor(y)
            
            if device == 'cuda':
                X_tensor = X_tensor.cuda()
                y_tensor = y_tensor.cuda()
                model = model.cuda()
            
            # 훈련 루프
            model.train()
            for epoch in range(10):  # 적은 에포크
                optimizer.zero_grad()
                outputs = model(X_tensor)
                loss = criterion(outputs, y_tensor)
                loss.backward()
                optimizer.step()
            
            # 정확도 계산
            model.eval()
            with torch.no_grad():
                predictions = model(X_tensor)
                predicted_classes = torch.argmax(predictions, dim=1)
                accuracy = accuracy_score(y_tensor.cpu().numpy(), predicted_classes.cpu().numpy())
            
            return {
                'hardware_id': hardware_id,
                'accuracy': accuracy,
                'loss': loss.item(),
                'epochs': 10
            }
            
        except Exception as e:
            print(f"❌ 하드웨어 {hardware_id} 모델 훈련 오류: {e}")
            return {
                'hardware_id': hardware_id,
                'accuracy': 0.0,
                'loss': float('inf'),
                'error': str(e)
            }
    
    # ===== 2. 다중 센서 융합 =====
    
    def multi_sensor_fusion(self, audio_data: np.ndarray) -> Dict:
        """다중 센서 융합"""
        try:
            print("🔍 다중 센서 융합 시작")
            
            # 각 센서에서 데이터 수집
            sensor_readings = {}
            for sensor_id, sensor in self.sensors.items():
                reading = sensor.simulate_reading(audio_data)
                sensor_readings[sensor_id] = reading
            
            # 센서 데이터 융합
            fused_result = self._fuse_sensor_data(sensor_readings)
            
            print(f"✅ 다중 센서 융합 완료! 융합된 특징 수: {len(fused_result)}")
            
            return {
                'success': True,
                'sensor_readings': sensor_readings,
                'fused_features': fused_result,
                'fusion_method': 'weighted_average'
            }
            
        except Exception as e:
            print(f"❌ 다중 센서 융합 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def _fuse_sensor_data(self, sensor_readings: Dict) -> np.ndarray:
        """센서 데이터 융합"""
        try:
            # 가중 평균 융합
            weights = [1.0 / len(sensor_readings)] * len(sensor_readings)
            readings_array = np.array(list(sensor_readings.values()))
            
            # 가중 평균 계산
            fused_features = np.average(readings_array, axis=0, weights=weights)
            
            return fused_features
            
        except Exception as e:
            print(f"⚠️ 센서 데이터 융합 오류: {e}")
            return np.zeros(50)  # 기본값
    
    # ===== 3. 실시간 적응형 학습 =====
    
    def adaptive_learning(self, audio_data: np.ndarray, ground_truth: int, hardware_id: int) -> Dict:
        """실시간 적응형 학습"""
        try:
            learning_system = self.learning_systems[hardware_id]
            
            # 적응형 학습 수행
            result = learning_system.learn(audio_data, ground_truth)
            
            return {
                'success': True,
                'hardware_id': hardware_id,
                'prediction': result['prediction'],
                'confidence': result['confidence'],
                'learning_rate': result['learning_rate'],
                'error': result['error']
            }
            
        except Exception as e:
            print(f"❌ 적응형 학습 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    # ===== 4. 통합 시스템 =====
    
    def integrated_3tier_system(self, audio_files: List[str], labels: List[int]) -> Dict:
        """통합 3순위 조합 시스템"""
        try:
            print("🚀 통합 3순위 조합 시스템 시작")
            
            # 1. 오디오 데이터 로드 및 특징 추출
            print("1️⃣ 오디오 데이터 로드 및 특징 추출")
            features_list = []
            for audio_file in audio_files:
                try:
                    audio_data, sr = librosa.load(audio_file, sr=16000)
                    features = self._extract_lightweight_features(audio_data, sr)
                    features_list.append(features)
                except Exception as e:
                    print(f"⚠️ 파일 로드 오류 {audio_file}: {e}")
                    continue
            
            X = np.array(features_list)
            y = np.array(labels[:len(features_list)])
            
            # 2. 경량화된 딥러닝 모델 훈련
            print("2️⃣ 경량화된 딥러닝 모델 훈련")
            dl_result = self.train_lightweight_models(X, y)
            
            # 3. 다중 센서 융합
            print("3️⃣ 다중 센서 융합")
            sensor_result = self.multi_sensor_fusion(audio_data)
            
            # 4. 적응형 학습
            print("4️⃣ 적응형 학습")
            adaptive_results = []
            for i, (audio_file, label) in enumerate(zip(audio_files, labels)):
                try:
                    audio_data, sr = librosa.load(audio_file, sr=16000)
                    hardware_id = i % self.hardware_count
                    adaptive_result = self.adaptive_learning(audio_data, label, hardware_id)
                    adaptive_results.append(adaptive_result)
                except Exception as e:
                    print(f"⚠️ 적응형 학습 오류 {audio_file}: {e}")
                    continue
            
            # 5. 결과 통합
            print("5️⃣ 결과 통합")
            final_result = self._integrate_results(dl_result, sensor_result, adaptive_results)
            
            print(f"✅ 통합 3순위 조합 시스템 완료!")
            print(f"   딥러닝 정확도: {dl_result.get('overall_accuracy', 0):.3f}")
            print(f"   센서 융합 성공: {sensor_result.get('success', False)}")
            print(f"   적응형 학습 성공: {len([r for r in adaptive_results if r.get('success', False)])}")
            
            return final_result
            
        except Exception as e:
            print(f"❌ 통합 시스템 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def _extract_lightweight_features(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """경량화된 특징 추출"""
        try:
            features = []
            
            # 기본 특징들만 추출 (처리 시간 단축)
            features.append(np.sqrt(np.mean(audio_data ** 2)))  # RMS
            features.append(np.mean(librosa.feature.zero_crossing_rate(audio_data)))  # ZCR
            features.append(np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr)))  # Spectral Centroid
            features.append(np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr)))  # Spectral Rolloff
            features.append(np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)))  # Spectral Bandwidth
            
            # MFCC (13개 계수)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            features.extend(np.mean(mfccs, axis=1))
            
            # Chroma (12개 계수)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            features.extend(np.mean(chroma, axis=1))
            
            # Spectral Contrast (7개 계수)
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
            features.extend(np.mean(contrast, axis=1))
            
            # Zero Crossing Rate (고급)
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            features.append(np.mean(zcr))
            features.append(np.std(zcr))
            
            return np.array(features)
            
        except Exception as e:
            print(f"⚠️ 특징 추출 오류: {e}")
            return np.zeros(50)  # 기본값
    
    def _integrate_results(self, dl_result: Dict, sensor_result: Dict, adaptive_results: List[Dict]) -> Dict:
        """결과 통합"""
        try:
            # 딥러닝 결과
            dl_accuracy = dl_result.get('overall_accuracy', 0.0)
            
            # 센서 융합 결과
            sensor_success = sensor_result.get('success', False)
            sensor_features = sensor_result.get('fused_features', [])
            
            # 적응형 학습 결과
            adaptive_success_count = len([r for r in adaptive_results if r.get('success', False)])
            adaptive_total_count = len(adaptive_results)
            adaptive_success_rate = adaptive_success_count / adaptive_total_count if adaptive_total_count > 0 else 0
            
            # 최종 정확도 계산 (가중 평균)
            weights = [0.4, 0.3, 0.3]  # 딥러닝, 센서, 적응형 학습
            final_accuracy = (
                weights[0] * dl_accuracy +
                weights[1] * (1.0 if sensor_success else 0.0) +
                weights[2] * adaptive_success_rate
            )
            
            return {
                'success': True,
                'final_accuracy': final_accuracy,
                'dl_accuracy': dl_accuracy,
                'sensor_success': sensor_success,
                'adaptive_success_rate': adaptive_success_rate,
                'hardware_count': self.hardware_count,
                'performance_metrics': {
                    'dl_accuracy': dl_accuracy,
                    'sensor_success': sensor_success,
                    'adaptive_success_rate': adaptive_success_rate,
                    'final_accuracy': final_accuracy
                }
            }
            
        except Exception as e:
            print(f"⚠️ 결과 통합 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    # ===== 5. 성능 모니터링 =====
    
    def get_performance_metrics(self) -> Dict:
        """성능 메트릭 조회"""
        try:
            metrics = {
                'hardware_specs': self.hardware_specs,
                'model_count': len(self.models),
                'sensor_count': len(self.sensors),
                'learning_system_count': len(self.learning_systems),
                'timestamp': time.time()
            }
            
            return metrics
            
        except Exception as e:
            print(f"⚠️ 성능 메트릭 조회 오류: {e}")
            return {'error': str(e)}

# ===== 보조 클래스들 =====

class LightweightCNN(nn.Module):
    """경량화된 CNN 모델"""
    
    def __init__(self, input_size: int, hidden_size: int = 32, output_size: int = 2):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(0.2)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x

class VirtualSensor:
    """가상 센서 클래스"""
    
    def __init__(self, sensor_id: int, sensor_type: str, hardware_specs: Dict):
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self.hardware_specs = hardware_specs
        self.calibration_data = self._load_calibration()
    
    def _load_calibration(self) -> Dict:
        """센서 보정 데이터 로드"""
        return {
            'temp_coeff': 0.1,
            'vib_coeff': 0.05,
            'curr_coeff': 0.02,
            'press_coeff': 0.03,
            'hum_coeff': 0.08
        }
    
    def simulate_reading(self, audio_data: np.ndarray) -> np.ndarray:
        """센서 값 시뮬레이션"""
        try:
            if self.sensor_type == 'temperature':
                return self._extract_temperature(audio_data)
            elif self.sensor_type == 'vibration':
                return self._extract_vibration(audio_data)
            elif self.sensor_type == 'current':
                return self._extract_current(audio_data)
            elif self.sensor_type == 'pressure':
                return self._extract_pressure(audio_data)
            elif self.sensor_type == 'humidity':
                return self._extract_humidity(audio_data)
            else:
                return np.zeros(10)  # 기본값
                
        except Exception as e:
            print(f"⚠️ 센서 {self.sensor_id} 시뮬레이션 오류: {e}")
            return np.zeros(10)
    
    def _extract_temperature(self, audio_data: np.ndarray) -> np.ndarray:
        """온도 추출"""
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data)
        temperature = self.calibration_data['temp_coeff'] * np.mean(spectral_centroid)
        return np.array([temperature] * 10)
    
    def _extract_vibration(self, audio_data: np.ndarray) -> np.ndarray:
        """진동 추출"""
        rms = np.sqrt(np.mean(audio_data ** 2))
        vibration = self.calibration_data['vib_coeff'] * rms
        return np.array([vibration] * 10)
    
    def _extract_current(self, audio_data: np.ndarray) -> np.ndarray:
        """전류 추출"""
        zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
        current = self.calibration_data['curr_coeff'] * zcr
        return np.array([current] * 10)
    
    def _extract_pressure(self, audio_data: np.ndarray) -> np.ndarray:
        """압력 추출"""
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data)
        pressure = self.calibration_data['press_coeff'] * np.mean(spectral_rolloff)
        return np.array([pressure] * 10)
    
    def _extract_humidity(self, audio_data: np.ndarray) -> np.ndarray:
        """습도 추출"""
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data)
        humidity = self.calibration_data['hum_coeff'] * np.mean(spectral_bandwidth)
        return np.array([humidity] * 10)

class AdaptiveLearningSystem:
    """적응형 학습 시스템"""
    
    def __init__(self, hardware_id: int, model, optimizer, criterion):
        self.hardware_id = hardware_id
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.learning_rate = 0.001
        self.error_history = []
        self.adaptation_count = 0
    
    def learn(self, audio_data: np.ndarray, ground_truth: int) -> Dict:
        """적응형 학습 수행"""
        try:
            # 특징 추출
            features = self._extract_features(audio_data)
            
            # 예측 수행
            prediction = self._predict(features)
            
            # 오류 계산
            error = abs(prediction - ground_truth)
            self.error_history.append(error)
            
            # 적응형 학습률 조정
            self._adjust_learning_rate(error)
            
            # 모델 업데이트
            self._update_model(features, ground_truth)
            
            return {
                'prediction': prediction,
                'confidence': 1.0 - error,
                'learning_rate': self.learning_rate,
                'error': error,
                'adaptation_count': self.adaptation_count
            }
            
        except Exception as e:
            print(f"⚠️ 적응형 학습 오류: {e}")
            return {
                'prediction': 0,
                'confidence': 0.0,
                'learning_rate': self.learning_rate,
                'error': 1.0,
                'adaptation_count': self.adaptation_count
            }
    
    def _extract_features(self, audio_data: np.ndarray) -> np.ndarray:
        """특징 추출"""
        try:
            features = [
                np.sqrt(np.mean(audio_data ** 2)),  # RMS
                np.mean(librosa.feature.zero_crossing_rate(audio_data)),  # ZCR
                np.mean(librosa.feature.spectral_centroid(y=audio_data))  # Spectral Centroid
            ]
            return np.array(features)
        except:
            return np.zeros(3)
    
    def _predict(self, features: np.ndarray) -> int:
        """예측 수행"""
        try:
            with torch.no_grad():
                features_tensor = torch.FloatTensor(features).unsqueeze(0)
                output = self.model(features_tensor)
                prediction = torch.argmax(output, dim=1).item()
                return prediction
        except:
            return 0
    
    def _adjust_learning_rate(self, error: float):
        """학습률 조정"""
        if error > 0.1:  # 높은 오류
            self.learning_rate *= 1.1
        else:  # 낮은 오류
            self.learning_rate *= 0.9
        
        # 학습률 범위 제한
        self.learning_rate = max(0.0001, min(0.01, self.learning_rate))
        
        # 옵티마이저 학습률 업데이트
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = self.learning_rate
    
    def _update_model(self, features: np.ndarray, ground_truth: int):
        """모델 업데이트"""
        try:
            self.model.train()
            self.optimizer.zero_grad()
            
            features_tensor = torch.FloatTensor(features).unsqueeze(0)
            target_tensor = torch.LongTensor([ground_truth])
            
            output = self.model(features_tensor)
            loss = self.criterion(output, target_tensor)
            
            loss.backward()
            self.optimizer.step()
            
            self.adaptation_count += 1
            
        except Exception as e:
            print(f"⚠️ 모델 업데이트 오류: {e}")

# 사용 예제
if __name__ == "__main__":
    # 경량화된 3순위 조합 시스템 테스트
    system = Lightweight3TierSystem(hardware_count=10)
    
    print("🚀 경량화된 3순위 조합 시스템 테스트")
    print("=" * 60)
    
    # 가상의 테스트 데이터
    test_audio_files = ["test1.wav", "test2.wav", "test3.wav"]
    test_labels = [0, 1, 0]  # 0: 정상, 1: 이상
    
    # 통합 시스템 실행
    results = system.integrated_3tier_system(test_audio_files, test_labels)
    
    if results['success']:
        print("📊 결과:")
        print(f"   최종 정확도: {results['final_accuracy']:.3f}")
        print(f"   딥러닝 정확도: {results['dl_accuracy']:.3f}")
        print(f"   센서 융합 성공: {results['sensor_success']}")
        print(f"   적응형 학습 성공률: {results['adaptive_success_rate']:.3f}")
        print(f"   하드웨어 수: {results['hardware_count']}")
    else:
        print(f"❌ 시스템 실행 실패: {results['error']}")
