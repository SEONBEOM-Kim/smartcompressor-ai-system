#!/usr/bin/env python3
"""
냉장고 상태 진단 앙상블 학습 모듈
RefrigeratorDiagnosisCNN 모델들을 조합하여 더 높은 성능을 달성
"""

import numpy as np
import os
import json
from typing import List, Dict, Tuple, Optional, Union
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# RefrigeratorDiagnosisCNN 모델 import
from .refrigerator_diagnosis_cnn import RefrigeratorDiagnosisCNN

class EnsembleDiagnosis:
    """
    냉장고 상태 진단 앙상블 모델 클래스
    
    여러 개의 RefrigeratorDiagnosisCNN 모델을 조합하여
    더 높은 성능과 안정성을 제공하는 앙상블 시스템
    """
    
    def __init__(self, 
                 input_shape: Tuple[int, int, int],
                 num_models: int = 5,
                 ensemble_name: str = "ensemble_diagnosis",
                 random_state: int = 42):
        """
        앙상블 모델 초기화
        
        Args:
            input_shape: 입력 데이터 shape (height, width, channels)
            num_models: 앙상블에 사용할 모델 개수
            ensemble_name: 앙상블 모델 이름
            random_state: 랜덤 시드
        """
        self.input_shape = input_shape
        self.num_models = num_models
        self.ensemble_name = ensemble_name
        self.random_state = random_state
        
        # 개별 모델들 저장
        self.models: List[RefrigeratorDiagnosisCNN] = []
        self.model_weights: List[float] = []
        self.is_trained = False
        
        # 클래스 레이블 정의
        self.class_labels = {
            'leak_detection': {0: '정상', 1: '냉매 누출'},
            'compressor_frequency': {0: '정상', 1: '비정상'},
            'compressor_sound': {0: '정상', 1: '이상'}
        }
        
        # 앙상블 모델들 초기화
        self._initialize_models()
    
    def _initialize_models(self):
        """개별 모델들 초기화"""
        print(f"앙상블 모델 초기화 중... ({self.num_models}개 모델)")
        
        for i in range(self.num_models):
            model_name = f"{self.ensemble_name}_model_{i+1}"
            model = RefrigeratorDiagnosisCNN(
                input_shape=self.input_shape,
                model_name=model_name
            )
            model.build_model()
            self.models.append(model)
            self.model_weights.append(1.0)  # 초기 가중치는 동일
        
        print(f"앙상블 모델 초기화 완료: {self.num_models}개 모델")
    
    def train_ensemble(self, 
                      X: np.ndarray, 
                      y: Dict[str, np.ndarray],
                      validation_split: float = 0.2,
                      epochs: int = 50,
                      batch_size: int = 32,
                      bootstrap_ratio: float = 0.8,
                      verbose: bool = True) -> Dict:
        """
        앙상블 모델 훈련 (배깅 기법 사용)
        
        Args:
            X: 입력 데이터 (samples, height, width, channels)
            y: 레이블 딕셔너리 {'task_name': labels}
            validation_split: 검증 데이터 비율
            epochs: 훈련 에포크 수
            batch_size: 배치 크기
            bootstrap_ratio: 부트스트랩 샘플 비율
            verbose: 훈련 과정 출력 여부
            
        Returns:
            훈련 히스토리 딕셔너리
        """
        if verbose:
            print("=" * 60)
            print("앙상블 모델 훈련 시작")
            print("=" * 60)
            print(f"입력 데이터 shape: {X.shape}")
            print(f"앙상블 모델 수: {self.num_models}")
            print(f"부트스트랩 비율: {bootstrap_ratio}")
            print(f"훈련 에포크: {epochs}")
            print("=" * 60)
        
        # 데이터 전처리
        X_processed = self._preprocess_data(X)
        y_processed = self._preprocess_labels(y)
        
        # 훈련/검증 데이터 분할
        X_train, X_val, y_train, y_val = self._split_data(
            X_processed, y_processed, validation_split
        )
        
        # 각 모델별 훈련 히스토리 저장
        ensemble_history = {
            'individual_histories': [],
            'ensemble_metrics': {},
            'model_weights': []
        }
        
        # 개별 모델 훈련 (배깅)
        for i, model in enumerate(self.models):
            if verbose:
                print(f"\n모델 {i+1}/{self.num_models} 훈련 중...")
            
            # 부트스트랩 샘플링
            bootstrap_indices = self._bootstrap_sampling(
                len(X_train), bootstrap_ratio
            )
            
            X_bootstrap = X_train[bootstrap_indices]
            y_bootstrap = {k: v[bootstrap_indices] for k, v in y_train.items()}
            
            # 모델 훈련
            history = self._train_single_model(
                model, X_bootstrap, y_bootstrap, X_val, y_val,
                epochs, batch_size, verbose
            )
            
            ensemble_history['individual_histories'].append(history)
            
            # 모델 성능 평가 및 가중치 계산
            model_weight = self._evaluate_model_weight(
                model, X_val, y_val
            )
            self.model_weights[i] = model_weight
            ensemble_history['model_weights'].append(model_weight)
            
            if verbose:
                print(f"모델 {i+1} 훈련 완료 (가중치: {model_weight:.3f})")
        
        # 앙상블 성능 평가
        ensemble_metrics = self._evaluate_ensemble(X_val, y_val)
        ensemble_history['ensemble_metrics'] = ensemble_metrics
        
        self.is_trained = True
        
        if verbose:
            print("\n" + "=" * 60)
            print("앙상블 모델 훈련 완료!")
            print("=" * 60)
            print("개별 모델 가중치:")
            for i, weight in enumerate(self.model_weights):
                print(f"  모델 {i+1}: {weight:.3f}")
            print(f"\n앙상블 성능:")
            for task, metrics in ensemble_metrics.items():
                print(f"  {task}: {metrics['accuracy']:.3f}")
            print("=" * 60)
        
        return ensemble_history
    
    def _preprocess_data(self, X: np.ndarray) -> np.ndarray:
        """입력 데이터 전처리"""
        if len(X.shape) == 3:
            X = np.expand_dims(X, axis=-1)
        return X
    
    def _preprocess_labels(self, y: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """레이블 전처리 (원-핫 인코딩)"""
        y_processed = {}
        for task_name, labels in y.items():
            if len(labels.shape) == 1:
                # 이진 분류를 위한 원-핫 인코딩
                y_processed[task_name] = np.eye(2)[labels]
            else:
                y_processed[task_name] = labels
        return y_processed
    
    def _split_data(self, X: np.ndarray, y: Dict[str, np.ndarray], 
                   validation_split: float) -> Tuple:
        """데이터 분할"""
        # 첫 번째 태스크의 레이블을 기준으로 분할
        first_task = list(y.keys())[0]
        X_train, X_val, y_train, y_val = train_test_split(
            X, y[first_task], test_size=validation_split, 
            random_state=self.random_state, stratify=y[first_task]
        )
        
        # 모든 태스크에 대해 동일한 분할 적용
        y_train_dict = {}
        y_val_dict = {}
        for task_name, labels in y.items():
            y_train_dict[task_name] = labels[train_test_split(
                X, labels, test_size=validation_split, 
                random_state=self.random_state, stratify=labels
            )[2]]
            y_val_dict[task_name] = labels[train_test_split(
                X, labels, test_size=validation_split, 
                random_state=self.random_state, stratify=labels
            )[3]]
        
        return X_train, X_val, y_train_dict, y_val_dict
    
    def _bootstrap_sampling(self, n_samples: int, ratio: float) -> np.ndarray:
        """부트스트랩 샘플링"""
        n_bootstrap = int(n_samples * ratio)
        return np.random.choice(n_samples, n_bootstrap, replace=True)
    
    def _train_single_model(self, model: RefrigeratorDiagnosisCNN,
                           X_train: np.ndarray, y_train: Dict[str, np.ndarray],
                           X_val: np.ndarray, y_val: Dict[str, np.ndarray],
                           epochs: int, batch_size: int, verbose: bool) -> Dict:
        """단일 모델 훈련"""
        try:
            # 모델 훈련
            history = model.model.fit(
                X_train, y_train,
                epochs=epochs,
                batch_size=batch_size,
                validation_data=(X_val, y_val),
                verbose=1 if verbose else 0,
                shuffle=True
            )
            
            return {
                'loss': history.history['loss'],
                'val_loss': history.history['val_loss'],
                'accuracy': history.history.get('leak_detection_accuracy', []),
                'val_accuracy': history.history.get('val_leak_detection_accuracy', [])
            }
            
        except Exception as e:
            print(f"모델 훈련 오류: {e}")
            return {'loss': [], 'val_loss': [], 'accuracy': [], 'val_accuracy': []}
    
    def _evaluate_model_weight(self, model: RefrigeratorDiagnosisCNN,
                              X_val: np.ndarray, y_val: Dict[str, np.ndarray]) -> float:
        """모델 가중치 계산 (성능 기반)"""
        try:
            # 검증 데이터에 대한 예측
            predictions = model.model.predict(X_val)
            
            # 각 태스크별 정확도 계산
            task_accuracies = []
            for i, task_name in enumerate(['leak_detection', 'compressor_frequency', 'compressor_sound']):
                if task_name in y_val:
                    pred_classes = np.argmax(predictions[i], axis=1)
                    true_classes = np.argmax(y_val[task_name], axis=1)
                    accuracy = accuracy_score(true_classes, pred_classes)
                    task_accuracies.append(accuracy)
            
            # 평균 정확도를 가중치로 사용
            return np.mean(task_accuracies) if task_accuracies else 0.5
            
        except Exception as e:
            print(f"모델 가중치 계산 오류: {e}")
            return 0.5
    
    def _evaluate_ensemble(self, X_val: np.ndarray, y_val: Dict[str, np.ndarray]) -> Dict:
        """앙상블 성능 평가"""
        try:
            # 앙상블 예측
            ensemble_predictions = self.predict_ensemble(X_val)
            
            # 각 태스크별 성능 계산
            ensemble_metrics = {}
            for task_name in ['leak_detection', 'compressor_frequency', 'compressor_sound']:
                if task_name in y_val:
                    pred_classes = ensemble_predictions[task_name]['predicted_classes']
                    true_classes = np.argmax(y_val[task_name], axis=1)
                    accuracy = accuracy_score(true_classes, pred_classes)
                    
                    ensemble_metrics[task_name] = {
                        'accuracy': accuracy,
                        'predictions': pred_classes,
                        'true_labels': true_classes
                    }
            
            return ensemble_metrics
            
        except Exception as e:
            print(f"앙상블 성능 평가 오류: {e}")
            return {}
    
    def predict_ensemble(self, X: np.ndarray) -> Dict[str, Dict]:
        """
        앙상블 예측 수행
        
        Args:
            X: 입력 데이터 (samples, height, width, channels)
            
        Returns:
            앙상블 예측 결과 딕셔너리
        """
        if not self.is_trained:
            raise ValueError("앙상블 모델이 훈련되지 않았습니다.")
        
        # 입력 데이터 전처리
        X_processed = self._preprocess_data(X)
        
        # 각 모델별 예측 수집
        all_predictions = []
        for model in self.models:
            predictions = model.model.predict(X_processed)
            all_predictions.append(predictions)
        
        # 앙상블 예측 계산 (가중 평균)
        ensemble_predictions = {}
        task_names = ['leak_detection', 'compressor_frequency', 'compressor_sound']
        
        for i, task_name in enumerate(task_names):
            # 각 모델의 예측을 가중 평균
            weighted_predictions = np.zeros_like(all_predictions[0][i])
            
            for j, (model_pred, weight) in enumerate(zip(all_predictions, self.model_weights)):
                weighted_predictions += model_pred[i] * weight
            
            # 가중치 정규화
            total_weight = sum(self.model_weights)
            weighted_predictions /= total_weight
            
            # 최종 예측 클래스 결정
            predicted_classes = np.argmax(weighted_predictions, axis=1)
            confidences = np.max(weighted_predictions, axis=1)
            
            ensemble_predictions[task_name] = {
                'predicted_classes': predicted_classes,
                'confidences': confidences,
                'probabilities': weighted_predictions,
                'interpretation': self._interpret_ensemble_prediction(
                    task_name, predicted_classes, confidences
                )
            }
        
        return ensemble_predictions
    
    def _interpret_ensemble_prediction(self, task_name: str, 
                                     predicted_classes: np.ndarray, 
                                     confidences: np.ndarray) -> List[str]:
        """앙상블 예측 결과 해석"""
        interpretations = []
        
        for pred_class, confidence in zip(predicted_classes, confidences):
            class_name = self.class_labels[task_name][pred_class]
            
            if confidence > 0.8:
                confidence_level = "매우 높음"
            elif confidence > 0.6:
                confidence_level = "높음"
            elif confidence > 0.4:
                confidence_level = "보통"
            else:
                confidence_level = "낮음"
            
            interpretations.append(
                f"{class_name} (신뢰도: {confidence_level}, {confidence:.2%})"
            )
        
        return interpretations
    
    def predict_single(self, X: np.ndarray) -> Dict[str, Dict]:
        """단일 샘플 앙상블 예측"""
        if len(X.shape) == 3:
            X = np.expand_dims(X, axis=0)
        
        predictions = self.predict_ensemble(X)
        
        # 단일 샘플 결과 반환
        single_result = {}
        for task_name, result in predictions.items():
            single_result[task_name] = {
                'predicted_class': int(result['predicted_classes'][0]),
                'confidence': float(result['confidences'][0]),
                'probabilities': result['probabilities'][0].tolist(),
                'interpretation': result['interpretation'][0]
            }
        
        return single_result
    
    def save_ensemble(self, filepath: str):
        """앙상블 모델 저장"""
        if not self.is_trained:
            raise ValueError("앙상블 모델이 훈련되지 않았습니다.")
        
        # 각 모델 저장
        for i, model in enumerate(self.models):
            model_path = filepath.replace('.h5', f'_model_{i+1}.h5')
            model.save_model(model_path)
        
        # 앙상블 메타데이터 저장
        metadata = {
            'input_shape': self.input_shape,
            'num_models': self.num_models,
            'ensemble_name': self.ensemble_name,
            'model_weights': self.model_weights,
            'class_labels': self.class_labels,
            'is_trained': self.is_trained,
            'created_at': datetime.now().isoformat()
        }
        
        metadata_file = filepath.replace('.h5', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"앙상블 모델 저장 완료: {filepath}")
        print(f"메타데이터 저장 완료: {metadata_file}")
    
    def load_ensemble(self, filepath: str):
        """앙상블 모델 로드"""
        # 메타데이터 로드
        metadata_file = filepath.replace('.h5', '_metadata.json')
        if not os.path.exists(metadata_file):
            raise FileNotFoundError(f"메타데이터 파일을 찾을 수 없습니다: {metadata_file}")
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 앙상블 속성 복원
        self.input_shape = tuple(metadata['input_shape'])
        self.num_models = metadata['num_models']
        self.ensemble_name = metadata['ensemble_name']
        self.model_weights = metadata['model_weights']
        self.class_labels = metadata['class_labels']
        self.is_trained = metadata['is_trained']
        
        # 각 모델 로드
        self.models = []
        for i in range(self.num_models):
            model_path = filepath.replace('.h5', f'_model_{i+1}.h5')
            model = RefrigeratorDiagnosisCNN(self.input_shape)
            model.load_model(model_path)
            self.models.append(model)
        
        print(f"앙상블 모델 로드 완료: {filepath}")
        print(f"로드된 모델 수: {self.num_models}")
    
    def plot_training_history(self, history: Dict, save_path: str = None):
        """훈련 히스토리 시각화"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'{self.ensemble_name} 훈련 히스토리', fontsize=16)
            
            # 개별 모델별 히스토리 플롯
            for i, model_history in enumerate(history['individual_histories']):
                if model_history['loss']:
                    axes[0, 0].plot(model_history['loss'], label=f'모델 {i+1}', alpha=0.7)
                    axes[0, 1].plot(model_history['val_loss'], label=f'모델 {i+1}', alpha=0.7)
                    axes[1, 0].plot(model_history['accuracy'], label=f'모델 {i+1}', alpha=0.7)
                    axes[1, 1].plot(model_history['val_accuracy'], label=f'모델 {i+1}', alpha=0.7)
            
            axes[0, 0].set_title('훈련 손실')
            axes[0, 0].set_xlabel('에포크')
            axes[0, 0].set_ylabel('손실')
            axes[0, 0].legend()
            axes[0, 0].grid(True)
            
            axes[0, 1].set_title('검증 손실')
            axes[0, 1].set_xlabel('에포크')
            axes[0, 1].set_ylabel('손실')
            axes[0, 1].legend()
            axes[0, 1].grid(True)
            
            axes[1, 0].set_title('훈련 정확도')
            axes[1, 0].set_xlabel('에포크')
            axes[1, 0].set_ylabel('정확도')
            axes[1, 0].legend()
            axes[1, 0].grid(True)
            
            axes[1, 1].set_title('검증 정확도')
            axes[1, 1].set_xlabel('에포크')
            axes[1, 1].set_ylabel('정확도')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"훈련 히스토리 저장: {save_path}")
            
            plt.show()
            
        except Exception as e:
            print(f"히스토리 플롯 생성 오류: {e}")

# 사용 예제
if __name__ == "__main__":
    print("앙상블 학습 모듈 테스트")
    print("=" * 40)
    
    # 앙상블 모델 생성
    input_shape = (13, 100, 1)
    ensemble = EnsembleDiagnosis(input_shape, num_models=3)
    
    print(f"앙상블 모델 생성 완료: {ensemble.num_models}개 모델")
    print(f"입력 shape: {ensemble.input_shape}")
    print("=" * 40)
