import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from models.refrigerator_diagnosis_cnn import RefrigeratorDiagnosisCNN
import json
from datetime import datetime

class ModelTrainingUtils:
    def __init__(self, input_shape: Tuple[int, int, int]):
        self.input_shape = input_shape
        self.model = None
        self.training_data = None
        self.test_data = None
    
    def load_dataset(self, dataset_file: str) -> Dict:
        """데이터셋 로드"""
        try:
            data = np.load(dataset_file, allow_pickle=True)
            
            dataset = {
                'mfccs_original': data['mfccs_original'],
                'mfccs_compressor': data['mfccs_compressor'],
                'mfccs_refrigerant': data['mfccs_refrigerant'],
                'compressor_cycles': data['compressor_cycles'],
                'spectral_features': data['spectral_features'],
                'temporal_features': data['temporal_features'],
                'labels': data['labels'],
                'file_paths': data['file_paths']
            }
            
            print(f"데이터셋 로드 완료: {dataset_file}")
            print(f"총 샘플 수: {len(dataset['labels'])}")
            print(f"레이블 분포: {np.bincount(dataset['labels'])}")
            
            return dataset
            
        except Exception as e:
            print(f"데이터셋 로드 오류: {e}")
            return {}
    
    def prepare_training_data(self, dataset: Dict, 
                            leak_labels: Optional[np.ndarray] = None,
                            frequency_labels: Optional[np.ndarray] = None,
                            sound_labels: Optional[np.ndarray] = None) -> Tuple[np.ndarray, Dict]:
        """훈련 데이터 준비"""
        try:
            # MFCC 특성 추출
            X = dataset['mfccs_original']
            
            # 레이블 생성 (실제로는 데이터셋에서 가져와야 함)
            if leak_labels is None:
                leak_labels = np.random.randint(0, 2, len(X))
            if frequency_labels is None:
                frequency_labels = np.random.randint(0, 2, len(X))
            if sound_labels is None:
                sound_labels = np.random.randint(0, 2, len(X))
            
            # 레이블 딕셔너리 생성
            y = {
                'leak_detection': leak_labels,
                'compressor_frequency': frequency_labels,
                'compressor_sound': sound_labels
            }
            
            print(f"훈련 데이터 준비 완료:")
            print(f"  입력 shape: {X.shape}")
            print(f"  냉매 누출 레이블 분포: {np.bincount(leak_labels)}")
            print(f"  압축기 빈도 레이블 분포: {np.bincount(frequency_labels)}")
            print(f"  압축기 소리 레이블 분포: {np.bincount(sound_labels)}")
            
            return X, y
            
        except Exception as e:
            print(f"훈련 데이터 준비 오류: {e}")
            return None, {}
    
    def train_model(self, X: np.ndarray, y: Dict[str, np.ndarray],
                   validation_split: float = 0.2, epochs: int = 100,
                   batch_size: int = 32, model_name: str = "refrigerator_diagnosis") -> RefrigeratorDiagnosisCNN:
        """모델 훈련"""
        try:
            # 모델 생성
            self.model = RefrigeratorDiagnosisCNN(self.input_shape, model_name=model_name)
            cnn_model = self.model.build_model()
            
            # 훈련/검증 데이터 분할
            X_train, X_val, y_train, y_val = self._split_data(X, y, validation_split)
            
            # 콜백 설정
            callbacks = [
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=20,
                    restore_best_weights=True,
                    verbose=1
                ),
                tf.keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=10,
                    min_lr=1e-7,
                    verbose=1
                ),
                tf.keras.callbacks.ModelCheckpoint(
                    filepath=f'{model_name}_best.h5',
                    monitor='val_loss',
                    save_best_only=True,
                    verbose=1
                )
            ]
            
            # 모델 훈련
            print("모델 훈련 시작...")
            history = self.model.train(
                X_train, y_train,
                validation_split=0.0,  # 이미 분할했으므로
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks
            )
            
            # 훈련 데이터 저장
            self.training_data = {
                'X_train': X_train,
                'X_val': X_val,
                'y_train': y_train,
                'y_val': y_val
            }
            
            print("모델 훈련 완료!")
            return self.model
            
        except Exception as e:
            print(f"모델 훈련 오류: {e}")
            return None
    
    def _split_data(self, X: np.ndarray, y: Dict[str, np.ndarray], 
                   validation_split: float) -> Tuple[np.ndarray, np.ndarray, Dict, Dict]:
        """데이터 분할"""
        # 첫 번째 태스크의 레이블로 분할
        first_task = list(y.keys())[0]
        X_train, X_val, y_train, y_val = train_test_split(
            X, y[first_task], test_size=validation_split, random_state=42, stratify=y[first_task]
        )
        
        # 모든 태스크의 레이블 분할
        y_train_dict = {}
        y_val_dict = {}
        
        for task_name, task_labels in y.items():
            _, _, y_train_task, y_val_task = train_test_split(
                X, task_labels, test_size=validation_split, random_state=42, stratify=task_labels
            )
            y_train_dict[task_name] = y_train_task
            y_val_dict[task_name] = y_val_task
        
        return X_train, X_val, y_train_dict, y_val_dict
    
    def evaluate_model(self, X_test: np.ndarray, y_test: Dict[str, np.ndarray]) -> Dict:
        """모델 평가"""
        if self.model is None:
            raise ValueError("모델이 훈련되지 않았습니다.")
        
        try:
            # 모델 평가
            evaluation = self.model.evaluate(X_test, y_test)
            
            # 예측 수행
            predictions = self.model.predict(X_test)
            
            # 각 태스크별 상세 평가
            detailed_evaluation = {}
            task_names = ['leak_detection', 'compressor_frequency', 'compressor_sound']
            
            for i, task_name in enumerate(task_names):
                # 예측 클래스
                y_pred = np.argmax(predictions[task_name], axis=1)
                y_true = y_test[task_name]
                
                # 분류 보고서
                report = classification_report(y_true, y_pred, output_dict=True)
                
                # 혼동 행렬
                cm = confusion_matrix(y_true, y_pred)
                
                detailed_evaluation[task_name] = {
                    'classification_report': report,
                    'confusion_matrix': cm.tolist(),
                    'accuracy': report['accuracy'],
                    'precision': report['weighted avg']['precision'],
                    'recall': report['weighted avg']['recall'],
                    'f1_score': report['weighted avg']['f1-score']
                }
            
            return detailed_evaluation
            
        except Exception as e:
            print(f"모델 평가 오류: {e}")
            return {}
    
    def plot_evaluation_results(self, evaluation: Dict, save_path: str = None):
        """평가 결과 시각화"""
        try:
            fig, axes = plt.subplots(2, 3, figsize=(18, 12))
            
            task_names = ['leak_detection', 'compressor_frequency', 'compressor_sound']
            
            for i, task_name in enumerate(task_names):
                if task_name not in evaluation:
                    continue
                
                # 혼동 행렬
                cm = np.array(evaluation[task_name]['confusion_matrix'])
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, i])
                axes[0, i].set_title(f'{task_name.replace("_", " ").title()} Confusion Matrix')
                axes[0, i].set_xlabel('Predicted')
                axes[0, i].set_ylabel('Actual')
                
                # 성능 메트릭
                metrics = ['accuracy', 'precision', 'recall', 'f1_score']
                values = [evaluation[task_name][metric] for metric in metrics]
                
                axes[1, i].bar(metrics, values, color=['skyblue', 'lightgreen', 'lightcoral', 'lightyellow'])
                axes[1, i].set_title(f'{task_name.replace("_", " ").title()} Performance Metrics')
                axes[1, i].set_ylabel('Score')
                axes[1, i].set_ylim(0, 1)
                
                # 값 표시
                for j, v in enumerate(values):
                    axes[1, i].text(j, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                print(f"평가 결과 저장 완료: {save_path}")
            
            plt.show()
            
        except Exception as e:
            print(f"평가 결과 시각화 오류: {e}")
    
    def save_training_report(self, evaluation: Dict, save_path: str = "training_report.json"):
        """훈련 보고서 저장"""
        try:
            report = {
                'model_info': {
                    'input_shape': self.input_shape,
                    'model_name': self.model.model_name if self.model else 'unknown',
                    'created_at': datetime.now().isoformat()
                },
                'evaluation_results': evaluation,
                'summary': {
                    'avg_accuracy': np.mean([evaluation[task]['accuracy'] for task in evaluation]),
                    'avg_precision': np.mean([evaluation[task]['precision'] for task in evaluation]),
                    'avg_recall': np.mean([evaluation[task]['recall'] for task in evaluation]),
                    'avg_f1_score': np.mean([evaluation[task]['f1_score'] for task in evaluation])
                }
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"훈련 보고서 저장 완료: {save_path}")
            
        except Exception as e:
            print(f"훈련 보고서 저장 오류: {e}")

# 사용 예제
if __name__ == "__main__":
    # 훈련 유틸리티 생성
    input_shape = (13, 100, 1)
    trainer = ModelTrainingUtils(input_shape)
    
    # 데이터셋 로드 (실제 파일 경로로 변경)
    dataset_file = "refrigerant_dataset.npz"
    
    if os.path.exists(dataset_file):
        dataset = trainer.load_dataset(dataset_file)
        
        if dataset:
            # 훈련 데이터 준비
            X, y = trainer.prepare_training_data(dataset)
            
            if X is not None:
                # 모델 훈련
                model = trainer.train_model(X, y, epochs=50)
                
                if model:
                    # 모델 저장
                    model.save_model('refrigerator_diagnosis_model.h5')
                    
                    # 훈련 히스토리 시각화
                    model.plot_training_history('training_history.png')
                    
                    print("모델 훈련 및 저장 완료!")
    else:
        print("데이터셋 파일이 없습니다.")
        print("먼저 데이터셋을 생성해주세요.")
