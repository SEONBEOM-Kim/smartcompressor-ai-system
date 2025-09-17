import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
import numpy as np
from typing import Tuple, Dict, List, Optional
import os
import json
from datetime import datetime
import matplotlib.pyplot as plt

class RefrigeratorDiagnosisCNN:
    def __init__(self, input_shape: Tuple[int, int, int], 
                 num_classes: int = 2, model_name: str = "refrigerator_diagnosis"):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model_name = model_name
        self.model = None
        self.history = None
        
        # 클래스 레이블 정의
        self.class_labels = {
            'leak_detection': {0: '정상', 1: '냉매 누출'},
            'compressor_frequency': {0: '정상', 1: '비정상'},
            'compressor_sound': {0: '정상', 1: '이상'}
        }
    
    def build_model(self) -> Model:
        """다중 출력 CNN 모델 구축"""
        # 입력 레이어
        inputs = layers.Input(shape=self.input_shape, name='audio_features')
        
        # 공통 특성 추출 백본
        x = layers.Conv2D(32, (3, 3), activation='relu', padding='same', name='conv1')(inputs)
        x = layers.BatchNormalization(name='bn1')(x)
        x = layers.MaxPooling2D((2, 2), name='pool1')(x)
        x = layers.Dropout(0.25, name='dropout1')(x)
        
        x = layers.Conv2D(64, (3, 3), activation='relu', padding='same', name='conv2')(x)
        x = layers.BatchNormalization(name='bn2')(x)
        x = layers.MaxPooling2D((2, 2), name='pool2')(x)
        x = layers.Dropout(0.25, name='dropout2')(x)
        
        x = layers.Conv2D(128, (3, 3), activation='relu', padding='same', name='conv3')(x)
        x = layers.BatchNormalization(name='bn3')(x)
        x = layers.MaxPooling2D((2, 2), name='pool3')(x)
        x = layers.Dropout(0.25, name='dropout3')(x)
        
        x = layers.Conv2D(256, (3, 3), activation='relu', padding='same', name='conv4')(x)
        x = layers.BatchNormalization(name='bn4')(x)
        x = layers.GlobalAveragePooling2D(name='global_avg_pool')(x)
        x = layers.Dropout(0.5, name='dropout4')(x)
        
        # 공통 특성 벡터
        common_features = layers.Dense(512, activation='relu', name='common_dense1')(x)
        common_features = layers.BatchNormalization(name='common_bn1')(common_features)
        common_features = layers.Dropout(0.5, name='common_dropout1')(common_features)
        
        common_features = layers.Dense(256, activation='relu', name='common_dense2')(common_features)
        common_features = layers.BatchNormalization(name='common_bn2')(common_features)
        common_features = layers.Dropout(0.3, name='common_dropout2')(common_features)
        
        # 출력 1: 냉매 누출 감지 (이진 분류)
        leak_output = layers.Dense(128, activation='relu', name='leak_dense1')(common_features)
        leak_output = layers.Dropout(0.3, name='leak_dropout')(leak_output)
        leak_output = layers.Dense(self.num_classes, activation='softmax', name='leak_detection')(leak_output)
        
        # 출력 2: 압축기 작동 빈도 (이진 분류)
        frequency_output = layers.Dense(128, activation='relu', name='frequency_dense1')(common_features)
        frequency_output = layers.Dropout(0.3, name='frequency_dropout')(frequency_output)
        frequency_output = layers.Dense(self.num_classes, activation='softmax', name='compressor_frequency')(frequency_output)
        
        # 출력 3: 압축기 압축음 이상 (이진 분류)
        sound_output = layers.Dense(128, activation='relu', name='sound_dense1')(common_features)
        sound_output = layers.Dropout(0.3, name='sound_dropout')(sound_output)
        sound_output = layers.Dense(self.num_classes, activation='softmax', name='compressor_sound')(sound_output)
        
        # 모델 생성
        model = Model(
            inputs=inputs,
            outputs=[leak_output, frequency_output, sound_output],
            name=self.model_name
        )
        
        # 모델 컴파일
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss={
                'leak_detection': 'categorical_crossentropy',
                'compressor_frequency': 'categorical_crossentropy',
                'compressor_sound': 'categorical_crossentropy'
            },
            loss_weights={
                'leak_detection': 1.0,
                'compressor_frequency': 0.8,
                'compressor_sound': 0.8
            },
            metrics={
                'leak_detection': ['accuracy', 'precision', 'recall'],
                'compressor_frequency': ['accuracy', 'precision', 'recall'],
                'compressor_sound': ['accuracy', 'precision', 'recall']
            }
        )
        
        self.model = model
        return model
    
    def prepare_data(self, features: Dict[str, np.ndarray], labels: Dict[str, np.ndarray]) -> Tuple[Dict, Dict]:
        """데이터 전처리"""
        try:
            # MFCC 특성을 3D로 변환
            if 'mfccs_original' in features:
                mfccs = features['mfccs_original']
                if len(mfccs.shape) == 2:
                    mfccs = np.expand_dims(mfccs, axis=-1)
                features['mfccs_original'] = mfccs
            
            # 레이블을 원-핫 인코딩
            processed_labels = {}
            for task_name, task_labels in labels.items():
                if len(task_labels.shape) == 1:
                    processed_labels[task_name] = keras.utils.to_categorical(task_labels, self.num_classes)
                else:
                    processed_labels[task_name] = task_labels
            
            return features, processed_labels
            
        except Exception as e:
            print(f"데이터 전처리 오류: {e}")
            return features, labels
    
    def train(self, X: np.ndarray, y: Dict[str, np.ndarray], 
              validation_split: float = 0.2, epochs: int = 100, 
              batch_size: int = 32, callbacks: List = None) -> keras.callbacks.History:
        """모델 훈련"""
        if self.model is None:
            self.build_model()
        
        # 데이터 전처리
        features = {'mfccs_original': X}
        processed_features, processed_labels = self.prepare_data(features, y)
        
        # 입력 데이터
        X_processed = processed_features['mfccs_original']
        
        # 콜백 설정
        if callbacks is None:
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=15,
                    restore_best_weights=True,
                    verbose=1
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=8,
                    min_lr=1e-7,
                    verbose=1
                ),
                keras.callbacks.ModelCheckpoint(
                    filepath=f'{self.model_name}_best.h5',
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                )
            ]
        
        # 모델 훈련
        print("모델 훈련 시작...")
        self.history = self.model.fit(
            X_processed, processed_labels,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        print("모델 훈련 완료!")
        return self.history
    
    def predict(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """예측 수행"""
        if self.model is None:
            raise ValueError("모델이 훈련되지 않았습니다.")
        
        # 입력 데이터 전처리
        if len(X.shape) == 2:
            X = np.expand_dims(X, axis=-1)
        
        # 예측 수행
        predictions = self.model.predict(X)
        
        # 결과 정리
        result = {
            'leak_detection': predictions[0],
            'compressor_frequency': predictions[1],
            'compressor_sound': predictions[2]
        }
        
        return result
    
    def predict_single(self, X: np.ndarray) -> Dict[str, Dict]:
        """단일 샘플 예측 (해석 가능한 결과)"""
        predictions = self.predict(X)
        
        result = {}
        for task_name, pred in predictions.items():
            # 확률과 클래스 예측
            probabilities = pred[0] if len(pred.shape) > 1 else pred
            predicted_class = np.argmax(probabilities)
            confidence = np.max(probabilities)
            
            result[task_name] = {
                'predicted_class': predicted_class,
                'confidence': float(confidence),
                'probabilities': probabilities.tolist(),
                'interpretation': self._interpret_prediction(task_name, predicted_class, confidence)
            }
        
        return result
    
    def _interpret_prediction(self, task_name: str, predicted_class: int, confidence: float) -> str:
        """예측 결과 해석"""
        class_name = self.class_labels[task_name][predicted_class]
        
        if confidence > 0.8:
            confidence_level = "매우 높음"
        elif confidence > 0.6:
            confidence_level = "높음"
        elif confidence > 0.4:
            confidence_level = "보통"
        else:
            confidence_level = "낮음"
        
        return f"{class_name} (신뢰도: {confidence_level}, {confidence:.2%})"
    
    def evaluate(self, X: np.ndarray, y: Dict[str, np.ndarray]) -> Dict[str, Dict]:
        """모델 평가"""
        if self.model is None:
            raise ValueError("모델이 훈련되지 않았습니다.")
        
        # 데이터 전처리
        features = {'mfccs_original': X}
        processed_features, processed_labels = self.prepare_data(features, y)
        
        # 평가 수행
        X_processed = processed_features['mfccs_original']
        evaluation = self.model.evaluate(X_processed, processed_labels, verbose=0)
        
        # 결과 정리
        result = {}
        task_names = ['leak_detection', 'compressor_frequency', 'compressor_sound']
        
        for i, task_name in enumerate(task_names):
            result[task_name] = {
                'loss': evaluation[i * 4 + 0],
                'accuracy': evaluation[i * 4 + 1],
                'precision': evaluation[i * 4 + 2],
                'recall': evaluation[i * 4 + 3]
            }
        
        return result
    
    def save_model(self, filepath: str):
        """모델 저장"""
        if self.model is None:
            raise ValueError("모델이 훈련되지 않았습니다.")
        
        # 모델 저장
        self.model.save(filepath)
        
        # 메타데이터 저장
        metadata = {
            'input_shape': self.input_shape,
            'num_classes': self.num_classes,
            'model_name': self.model_name,
            'class_labels': self.class_labels,
            'created_at': datetime.now().isoformat()
        }
        
        metadata_file = filepath.replace('.h5', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"모델 저장 완료: {filepath}")
        print(f"메타데이터 저장 완료: {metadata_file}")
    
    def load_model(self, filepath: str):
        """모델 로드"""
        # 모델 로드
        self.model = keras.models.load_model(filepath)
        
        # 메타데이터 로드
        metadata_file = filepath.replace('.h5', '_metadata.json')
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.input_shape = tuple(metadata['input_shape'])
            self.num_classes = metadata['num_classes']
            self.model_name = metadata['model_name']
            self.class_labels = metadata['class_labels']
        
        print(f"모델 로드 완료: {filepath}")
    
    def plot_training_history(self, save_path: str = None):
        """훈련 히스토리 시각화"""
        if self.history is None:
            print("훈련 히스토리가 없습니다.")
            return
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # 손실 그래프
        axes[0, 0].plot(self.history.history['loss'], label='Training Loss')
        axes[0, 0].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[0, 0].set_title('Model Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        
        # 정확도 그래프
        axes[0, 1].plot(self.history.history['leak_detection_accuracy'], label='Leak Detection')
        axes[0, 1].plot(self.history.history['compressor_frequency_accuracy'], label='Frequency')
        axes[0, 1].plot(self.history.history['compressor_sound_accuracy'], label='Sound')
        axes[0, 1].set_title('Model Accuracy')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy')
        axes[0, 1].legend()
        
        # 각 태스크별 손실
        task_names = ['leak_detection', 'compressor_frequency', 'compressor_sound']
        for i, task_name in enumerate(task_names):
            row = 1
            col = i
            
            axes[row, col].plot(self.history.history[f'{task_name}_loss'], label='Training')
            axes[row, col].plot(self.history.history[f'val_{task_name}_loss'], label='Validation')
            axes[row, col].set_title(f'{task_name.replace("_", " ").title()} Loss')
            axes[row, col].set_xlabel('Epoch')
            axes[row, col].set_ylabel('Loss')
            axes[row, col].legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"훈련 히스토리 저장 완료: {save_path}")
        
        plt.show()
    
    def get_model_summary(self):
        """모델 요약 정보"""
        if self.model is None:
            return "모델이 구축되지 않았습니다."
        
        return self.model.summary()

# 사용 예제
if __name__ == "__main__":
    # 모델 생성
    input_shape = (13, 100, 1)  # MFCC 특성 shape
    model = RefrigeratorDiagnosisCNN(input_shape)
    
    # 모델 구축
    cnn_model = model.build_model()
    
    print("냉장고 진단 CNN 모델 구조:")
    print(cnn_model.summary())
    
    # 샘플 데이터 생성 (실제로는 전처리된 데이터 사용)
    num_samples = 1000
    X_sample = np.random.randn(num_samples, 13, 100, 1)
    y_sample = {
        'leak_detection': np.random.randint(0, 2, num_samples),
        'compressor_frequency': np.random.randint(0, 2, num_samples),
        'compressor_sound': np.random.randint(0, 2, num_samples)
    }
    
    # 모델 훈련
    history = model.train(X_sample, y_sample, epochs=10)
    
    # 모델 저장
    model.save_model('refrigerator_diagnosis_model.h5')
    
    # 예측 예제
    sample_input = np.random.randn(1, 13, 100, 1)
    prediction = model.predict_single(sample_input)
    
    print("\n예측 결과:")
    for task, result in prediction.items():
        print(f"{task}: {result['interpretation']}")
