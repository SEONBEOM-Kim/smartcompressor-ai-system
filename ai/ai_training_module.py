#!/usr/bin/env python3
"""
AI 모델 훈련 모듈
기존 app.py에서 import하여 사용
"""

import os
import numpy as np
import json
import librosa
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import threading
import time

# AI 모델 import
from models.ensemble_learning import EnsembleDiagnosis
from models.refrigerator_diagnosis_cnn import RefrigeratorDiagnosisCNN

class AITrainingManager:
    """AI 모델 훈련 관리 클래스"""
    
    def __init__(self, upload_folder='uploads', models_folder='trained_models'):
        self.upload_folder = upload_folder
        self.models_folder = models_folder
        self.training_status = {
            'is_training': False,
            'progress': 0,
            'current_epoch': 0,
            'total_epochs': 0,
            'status_message': '대기 중...',
            'error': None,
            'model_name': None
        }
        
        # 폴더 생성
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.models_folder, exist_ok=True)
    
    def extract_audio_features(self, audio_file_path: str) -> Optional[np.ndarray]:
        """오디오 파일에서 MFCC 특성 추출"""
        try:
            # 오디오 로드
            y, sr = librosa.load(audio_file_path, sr=22050)
            
            # MFCC 특성 추출
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=2048, hop_length=512)
            
            # 100 프레임으로 패딩 또는 자르기
            if mfccs.shape[1] > 100:
                mfccs = mfccs[:, :100]
            else:
                mfccs = np.pad(mfccs, ((0, 0), (0, 100 - mfccs.shape[1])), mode='constant')
            
            return mfccs
            
        except Exception as e:
            print(f"오디오 특성 추출 오류: {e}")
            return None
    
    def create_dataset_from_uploads(self) -> Tuple[Optional[np.ndarray], Optional[Dict]]:
        """업로드된 파일들로부터 데이터셋 생성"""
        try:
            X_list = []
            y_leak = []
            y_frequency = []
            y_sound = []
            
            # 업로드 폴더의 모든 오디오 파일 처리
            for filename in os.listdir(self.upload_folder):
                if filename.endswith(('.wav', '.mp3', '.flac', '.m4a')):
                    audio_path = os.path.join(self.upload_folder, filename)
                    label_path = os.path.join(self.upload_folder, f"{filename}_labels.json")
                    
                    # 오디오 특성 추출
                    features = self.extract_audio_features(audio_path)
                    if features is not None:
                        X_list.append(features)
                        
                        # 라벨 로드
                        if os.path.exists(label_path):
                            with open(label_path, 'r', encoding='utf-8') as f:
                                labels = json.load(f)
                            
                            y_leak.append(labels.get('leak_detection', 0))
                            y_frequency.append(labels.get('compressor_frequency', 0))
                            y_sound.append(labels.get('compressor_sound', 0))
                        else:
                            # 라벨이 없으면 랜덤 생성 (실제로는 사용자가 라벨링해야 함)
                            y_leak.append(np.random.randint(0, 2))
                            y_frequency.append(np.random.randint(0, 2))
                            y_sound.append(np.random.randint(0, 2))
            
            if len(X_list) == 0:
                return None, None
            
            # 데이터셋 구성
            X = np.array(X_list)
            y = {
                'leak_detection': np.array(y_leak),
                'compressor_frequency': np.array(y_frequency),
                'compressor_sound': np.array(y_sound)
            }
            
            print(f"데이터셋 생성 완료: {len(X_list)}개 샘플")
            return X, y
            
        except Exception as e:
            print(f"데이터셋 생성 오류: {e}")
            return None, None
    
    def train_model_async(self, model_type: str, epochs: int, batch_size: int, 
                         model_name: str = None) -> bool:
        """비동기 모델 훈련 시작"""
        if self.training_status['is_training']:
            return False
        
        # 백그라운드에서 훈련 실행
        training_thread = threading.Thread(
            target=self._run_training,
            args=(model_type, epochs, batch_size, model_name)
        )
        training_thread.daemon = True
        training_thread.start()
        
        return True
    
    def _run_training(self, model_type: str, epochs: int, batch_size: int, model_name: str):
        """백그라운드 모델 훈련 실행"""
        try:
            self.training_status['is_training'] = True
            self.training_status['progress'] = 0
            self.training_status['current_epoch'] = 0
            self.training_status['total_epochs'] = epochs
            self.training_status['status_message'] = '훈련 준비 중...'
            self.training_status['error'] = None
            self.training_status['model_name'] = model_name or f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 데이터셋 생성
            self.training_status['status_message'] = '데이터셋 생성 중...'
            X, y = self.create_dataset_from_uploads()
            
            if X is None or len(X) == 0:
                self.training_status['error'] = '훈련할 데이터가 없습니다. 먼저 오디오 파일을 업로드하고 라벨링해주세요.'
                return
            
            self.training_status['status_message'] = '모델 생성 중...'
            
            if model_type == 'ensemble':
                # 앙상블 모델 훈련
                ensemble = EnsembleDiagnosis(
                    input_shape=(13, 100, 1),
                    num_models=5,
                    ensemble_name=self.training_status['model_name']
                )
                
                # 훈련 실행
                self.training_status['status_message'] = '앙상블 모델 훈련 중...'
                history = ensemble.train_ensemble(
                    X, y,
                    validation_split=0.2,
                    epochs=epochs,
                    batch_size=batch_size,
                    bootstrap_ratio=0.8,
                    verbose=False
                )
                
                # 모델 저장
                model_path = os.path.join(self.models_folder, f"{self.training_status['model_name']}.h5")
                ensemble.save_ensemble(model_path)
                
            else:
                # 단일 CNN 모델 훈련
                cnn = RefrigeratorDiagnosisCNN(
                    input_shape=(13, 100, 1),
                    model_name=self.training_status['model_name']
                )
                cnn.build_model()
                
                # 훈련 실행
                self.training_status['status_message'] = 'CNN 모델 훈련 중...'
                X_processed = np.expand_dims(X, axis=-1)
                y_processed = {}
                for task_name, labels in y.items():
                    y_processed[task_name] = np.eye(2)[labels]
                
                history = cnn.model.fit(
                    X_processed, y_processed,
                    epochs=epochs,
                    batch_size=batch_size,
                    validation_split=0.2,
                    verbose=0
                )
                
                # 모델 저장
                model_path = os.path.join(self.models_folder, f"{self.training_status['model_name']}.h5")
                cnn.save_model(model_path)
            
            # 훈련 완료
            self.training_status['progress'] = 100
            self.training_status['status_message'] = '훈련 완료!'
            self.training_status['is_training'] = False
            
            print(f"모델 훈련 완료: {model_path}")
            
        except Exception as e:
            self.training_status['error'] = f'훈련 오류: {str(e)}'
            self.training_status['is_training'] = False
            print(f"훈련 오류: {e}")
    
    def get_training_status(self) -> Dict:
        """훈련 상태 조회"""
        return self.training_status.copy()
    
    def predict_with_model(self, model_name: str, audio_file_path: str) -> Optional[Dict]:
        """훈련된 모델로 예측"""
        try:
            # 오디오 특성 추출
            features = self.extract_audio_features(audio_file_path)
            if features is None:
                return None
            
            # 모델 로드
            model_path = os.path.join(self.models_folder, f"{model_name}.h5")
            
            if not os.path.exists(model_path):
                return None
            
            # 앙상블 모델인지 확인
            metadata_path = model_path.replace('.h5', '_metadata.json')
            if os.path.exists(metadata_path):
                # 앙상블 모델
                ensemble = EnsembleDiagnosis((13, 100, 1))
                ensemble.load_ensemble(model_path)
                prediction = ensemble.predict_single(features)
            else:
                # 단일 CNN 모델
                cnn = RefrigeratorDiagnosisCNN((13, 100, 1))
                cnn.load_model(model_path)
                prediction = cnn.predict_single(features)
            
            return prediction
            
        except Exception as e:
            print(f"예측 오류: {e}")
            return None
    
    def get_available_models(self) -> List[str]:
        """사용 가능한 모델 목록 조회"""
        models = []
        if os.path.exists(self.models_folder):
            for file in os.listdir(self.models_folder):
                if file.endswith('.h5'):
                    models.append(file.replace('.h5', ''))
        return models

# 전역 AI 훈련 매니저 인스턴스
ai_manager = AITrainingManager()

