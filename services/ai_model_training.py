#!/usr/bin/env python3
"""
AI 모델 훈련 서비스
DecisionTreeClassifier를 사용한 압축기 상태 분류 모델
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
import librosa
import joblib
import os
import logging
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompressorAIModel:
    """압축기 AI 모델 클래스"""
    
    def __init__(self, model_path: str = 'data/models/compressor_model.pkl'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        self.training_history = []
        
        # 모델 디렉토리 생성
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        logger.info("압축기 AI 모델 초기화 완료")
    
    def extract_audio_features(self, audio_file_path: str) -> np.ndarray:
        """오디오 파일에서 특징 추출"""
        try:
            # 오디오 로드
            y, sr = librosa.load(audio_file_path, sr=16000, duration=5.0)
            
            # 기본 특징들
            features = []
            
            # 1. 시간 영역 특징
            rms = librosa.feature.rms(y=y)[0]
            features.extend([
                np.mean(rms),      # 평균 RMS 에너지
                np.std(rms),       # RMS 에너지 표준편차
                np.max(rms),       # 최대 RMS 에너지
                np.min(rms)        # 최소 RMS 에너지
            ])
            
            # 2. 주파수 영역 특징
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            features.extend([
                np.mean(spectral_centroids),  # 평균 스펙트럼 중심
                np.std(spectral_centroids),   # 스펙트럼 중심 표준편차
                np.max(spectral_centroids),   # 최대 스펙트럼 중심
                np.min(spectral_centroids)    # 최소 스펙트럼 중심
            ])
            
            # 3. 제로 크로싱 레이트
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            features.extend([
                np.mean(zcr),      # 평균 ZCR
                np.std(zcr),       # ZCR 표준편차
                np.max(zcr),       # 최대 ZCR
                np.min(zcr)        # 최소 ZCR
            ])
            
            # 4. 스펙트럼 롤오프
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            features.extend([
                np.mean(spectral_rolloff),    # 평균 스펙트럼 롤오프
                np.std(spectral_rolloff),     # 스펙트럼 롤오프 표준편차
                np.max(spectral_rolloff),     # 최대 스펙트럼 롤오프
                np.min(spectral_rolloff)      # 최소 스펙트럼 롤오프
            ])
            
            # 5. 멜 주파수 켑스트럼 계수 (MFCC)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            for i in range(13):
                features.extend([
                    np.mean(mfccs[i]),        # 평균 MFCC
                    np.std(mfccs[i])          # MFCC 표준편차
                ])
            
            # 6. 스펙트럼 대비
            spectral_contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            features.extend([
                np.mean(spectral_contrast),   # 평균 스펙트럼 대비
                np.std(spectral_contrast),    # 스펙트럼 대비 표준편차
                np.max(spectral_contrast),    # 최대 스펙트럼 대비
                np.min(spectral_contrast)     # 최소 스펙트럼 대비
            ])
            
            # 7. 크로마 특징
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            features.extend([
                np.mean(chroma),              # 평균 크로마
                np.std(chroma),               # 크로마 표준편차
                np.max(chroma),               # 최대 크로마
                np.min(chroma)                # 최소 크로마
            ])
            
            # 8. 스펙트럼 폭
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]
            features.extend([
                np.mean(spectral_bandwidth),  # 평균 스펙트럼 폭
                np.std(spectral_bandwidth),   # 스펙트럼 폭 표준편차
                np.max(spectral_bandwidth),   # 최대 스펙트럼 폭
                np.min(spectral_bandwidth)    # 최소 스펙트럼 폭
            ])
            
            # 9. 스펙트럼 평탄도
            spectral_flatness = librosa.feature.spectral_flatness(y=y)[0]
            features.extend([
                np.mean(spectral_flatness),   # 평균 스펙트럼 평탄도
                np.std(spectral_flatness),    # 스펙트럼 평탄도 표준편차
                np.max(spectral_flatness),    # 최대 스펙트럼 평탄도
                np.min(spectral_flatness)     # 최소 스펙트럼 평탄도
            ])
            
            # 10. 스펙트럼 폴리노미얼 특징
            spectral_poly = librosa.feature.poly_features(y=y, sr=sr, order=2)
            features.extend([
                np.mean(spectral_poly[0]),    # 평균 1차 계수
                np.std(spectral_poly[0]),     # 1차 계수 표준편차
                np.mean(spectral_poly[1]),    # 평균 2차 계수
                np.std(spectral_poly[1])      # 2차 계수 표준편차
            ])
            
            return np.array(features)
            
        except Exception as e:
            logger.error(f"오디오 특징 추출 실패: {e}")
            return np.zeros(100)  # 기본값 반환
    
    def create_synthetic_dataset(self, num_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """합성 데이터셋 생성 (실제 데이터가 없을 때 사용)"""
        logger.info(f"합성 데이터셋 생성 중... ({num_samples}개 샘플)")
        
        X = []
        y = []
        
        # 정상 상태 데이터 (70%)
        normal_samples = int(num_samples * 0.7)
        for _ in range(normal_samples):
            # 정상 압축기 소리 특징 (낮은 주파수, 안정적인 패턴)
            features = np.random.normal(0, 1, 100)
            
            # 정상 상태 특징 조정
            features[0:4] += np.random.normal(0.5, 0.2, 4)    # RMS 에너지
            features[4:8] += np.random.normal(2000, 500, 4)   # 스펙트럼 중심
            features[8:12] += np.random.normal(0.1, 0.05, 4)  # ZCR
            features[12:16] += np.random.normal(4000, 1000, 4) # 스펙트럼 롤오프
            
            X.append(features)
            y.append(0)  # 정상 상태
        
        # 문 열림 상태 데이터 (30%)
        door_open_samples = int(num_samples * 0.3)
        for _ in range(door_open_samples):
            # 문 열림 상태 소리 특징 (높은 주파수, 불안정한 패턴)
            features = np.random.normal(0, 1, 100)
            
            # 문 열림 상태 특징 조정
            features[0:4] += np.random.normal(1.5, 0.5, 4)    # 높은 RMS 에너지
            features[4:8] += np.random.normal(4000, 1000, 4)  # 높은 스펙트럼 중심
            features[8:12] += np.random.normal(0.3, 0.1, 4)   # 높은 ZCR
            features[12:16] += np.random.normal(6000, 1500, 4) # 높은 스펙트럼 롤오프
            
            X.append(features)
            y.append(1)  # 문 열림 상태
        
        X = np.array(X)
        y = np.array(y)
        
        # 데이터 셔플
        indices = np.random.permutation(len(X))
        X = X[indices]
        y = y[indices]
        
        logger.info(f"합성 데이터셋 생성 완료: {len(X)}개 샘플")
        return X, y
    
    def train_model(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict:
        """모델 훈련"""
        try:
            logger.info("모델 훈련 시작...")
            
            # 훈련/테스트 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # 특성 스케일링
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # 하이퍼파라미터 튜닝
            param_grid = {
                'max_depth': [3, 5, 7, 10, 15, 20, None],
                'min_samples_split': [2, 5, 10, 20],
                'min_samples_leaf': [1, 2, 4, 8],
                'criterion': ['gini', 'entropy']
            }
            
            # 그리드 서치
            grid_search = GridSearchCV(
                DecisionTreeClassifier(random_state=42),
                param_grid,
                cv=5,
                scoring='accuracy',
                n_jobs=-1
            )
            
            grid_search.fit(X_train_scaled, y_train)
            
            # 최적 모델 선택
            self.model = grid_search.best_estimator_
            
            # 모델 평가
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # 교차 검증
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
            
            # 훈련 결과 저장
            training_result = {
                'accuracy': accuracy,
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'best_params': grid_search.best_params_,
                'classification_report': classification_report(y_test, y_pred, output_dict=True),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'feature_importance': self.model.feature_importances_.tolist(),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'timestamp': datetime.now().isoformat()
            }
            
            self.training_history.append(training_result)
            self.is_trained = True
            
            # 모델 저장
            self.save_model()
            
            logger.info(f"모델 훈련 완료 - 정확도: {accuracy:.4f}")
            logger.info(f"교차 검증 점수: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            
            return training_result
            
        except Exception as e:
            logger.error(f"모델 훈련 실패: {e}")
            raise
    
    def predict(self, audio_file_path: str) -> Dict:
        """새로운 오디오 파일 예측"""
        try:
            if not self.is_trained:
                raise ValueError("모델이 훈련되지 않았습니다.")
            
            # 특징 추출
            features = self.extract_audio_features(audio_file_path)
            features_scaled = self.scaler.transform([features])
            
            # 예측
            prediction = self.model.predict(features_scaled)[0]
            probability = self.model.predict_proba(features_scaled)[0]
            
            # 결과 반환
            result = {
                'prediction': 'door_open' if prediction == 1 else 'normal',
                'probability': {
                    'normal': float(probability[0]),
                    'door_open': float(probability[1])
                },
                'confidence': float(max(probability)),
                'features': features.tolist()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"예측 실패: {e}")
            raise
    
    def save_model(self):
        """모델 저장"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained,
                'training_history': self.training_history
            }
            
            joblib.dump(model_data, self.model_path)
            logger.info(f"모델 저장 완료: {self.model_path}")
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            raise
    
    def load_model(self):
        """모델 로드"""
        try:
            if os.path.exists(self.model_path):
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
                self.is_trained = model_data['is_trained']
                self.training_history = model_data.get('training_history', [])
                
                logger.info(f"모델 로드 완료: {self.model_path}")
                return True
            else:
                logger.warning(f"모델 파일을 찾을 수 없습니다: {self.model_path}")
                return False
                
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def evaluate_model(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """모델 평가"""
        try:
            if not self.is_trained:
                raise ValueError("모델이 훈련되지 않았습니다.")
            
            X_scaled = self.scaler.transform(X)
            y_pred = self.model.predict(X_scaled)
            y_prob = self.model.predict_proba(X_scaled)
            
            # 평가 메트릭
            accuracy = accuracy_score(y, y_pred)
            classification_rep = classification_report(y, y_pred, output_dict=True)
            confusion_mat = confusion_matrix(y, y_pred)
            
            # 특성 중요도
            feature_importance = self.model.feature_importances_
            
            evaluation_result = {
                'accuracy': accuracy,
                'classification_report': classification_rep,
                'confusion_matrix': confusion_mat.tolist(),
                'feature_importance': feature_importance.tolist(),
                'predictions': y_pred.tolist(),
                'probabilities': y_prob.tolist()
            }
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"모델 평가 실패: {e}")
            raise
    
    def plot_training_results(self, save_path: str = None):
        """훈련 결과 시각화"""
        try:
            if not self.training_history:
                logger.warning("훈련 기록이 없습니다.")
                return
            
            latest_result = self.training_history[-1]
            
            # 그래프 생성
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # 1. 혼동 행렬
            cm = np.array(latest_result['confusion_matrix'])
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 0])
            axes[0, 0].set_title('Confusion Matrix')
            axes[0, 0].set_xlabel('Predicted')
            axes[0, 0].set_ylabel('Actual')
            
            # 2. 특성 중요도 (상위 20개)
            feature_importance = np.array(latest_result['feature_importance'])
            top_features = np.argsort(feature_importance)[-20:]
            top_importance = feature_importance[top_features]
            
            axes[0, 1].barh(range(len(top_features)), top_importance)
            axes[0, 1].set_title('Top 20 Feature Importance')
            axes[0, 1].set_xlabel('Importance')
            
            # 3. 클래스별 정확도
            class_report = latest_result['classification_report']
            classes = ['normal', 'door_open']
            precisions = [class_report[cls]['precision'] for cls in classes]
            recalls = [class_report[cls]['recall'] for cls in classes]
            
            x = np.arange(len(classes))
            width = 0.35
            
            axes[1, 0].bar(x - width/2, precisions, width, label='Precision')
            axes[1, 0].bar(x + width/2, recalls, width, label='Recall')
            axes[1, 0].set_title('Precision and Recall by Class')
            axes[1, 0].set_xlabel('Class')
            axes[1, 0].set_ylabel('Score')
            axes[1, 0].set_xticks(x)
            axes[1, 0].set_xticklabels(classes)
            axes[1, 0].legend()
            
            # 4. 훈련 히스토리
            if len(self.training_history) > 1:
                accuracies = [result['accuracy'] for result in self.training_history]
                cv_means = [result['cv_mean'] for result in self.training_history]
                
                axes[1, 1].plot(accuracies, label='Test Accuracy')
                axes[1, 1].plot(cv_means, label='CV Mean')
                axes[1, 1].set_title('Training History')
                axes[1, 1].set_xlabel('Epoch')
                axes[1, 1].set_ylabel('Accuracy')
                axes[1, 1].legend()
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"훈련 결과 그래프 저장: {save_path}")
            
            plt.show()
            
        except Exception as e:
            logger.error(f"훈련 결과 시각화 실패: {e}")
    
    def get_model_info(self) -> Dict:
        """모델 정보 조회"""
        return {
            'is_trained': self.is_trained,
            'model_path': self.model_path,
            'training_count': len(self.training_history),
            'latest_accuracy': self.training_history[-1]['accuracy'] if self.training_history else None,
            'feature_count': len(self.feature_names) if self.feature_names else 100
        }

# 전역 모델 인스턴스
compressor_ai_model = CompressorAIModel()

# 훈련 스크립트
def train_compressor_model():
    """압축기 모델 훈련 스크립트"""
    try:
        logger.info("압축기 AI 모델 훈련 시작")
        
        # 합성 데이터셋 생성
        X, y = compressor_ai_model.create_synthetic_dataset(num_samples=2000)
        
        # 모델 훈련
        training_result = compressor_ai_model.train_model(X, y)
        
        # 결과 출력
        print("\n" + "="*50)
        print("훈련 결과 요약")
        print("="*50)
        print(f"정확도: {training_result['accuracy']:.4f}")
        print(f"교차 검증: {training_result['cv_mean']:.4f} ± {training_result['cv_std']:.4f}")
        print(f"최적 파라미터: {training_result['best_params']}")
        
        # 분류 보고서 출력
        print("\n분류 보고서:")
        print(classification_report(
            [0, 1], [0, 1], 
            target_names=['normal', 'door_open'],
            output_dict=False
        ))
        
        # 특성 중요도 상위 10개 출력
        feature_importance = np.array(training_result['feature_importance'])
        top_features = np.argsort(feature_importance)[-10:]
        print(f"\n상위 10개 특성 중요도:")
        for i, feature_idx in enumerate(reversed(top_features)):
            print(f"{i+1:2d}. 특성 {feature_idx:2d}: {feature_importance[feature_idx]:.4f}")
        
        # 시각화
        compressor_ai_model.plot_training_results('data/models/training_results.png')
        
        logger.info("압축기 AI 모델 훈련 완료")
        
    except Exception as e:
        logger.error(f"모델 훈련 실패: {e}")
        raise

if __name__ == "__main__":
    train_compressor_model()
