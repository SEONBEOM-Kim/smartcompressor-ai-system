#!/usr/bin/env python3
"""
AI 훈련 스크립트 (train_ai.py)
라벨링된 스펙트로그램 데이터로 CNN 모델을 훈련합니다.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
from datetime import datetime
import logging
import argparse

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AITrainer:
    """AI 모델 훈련 클래스"""
    
    def __init__(self, image_size=(256, 256), num_classes=3, batch_size=32, epochs=50):
        """
        Args:
            image_size (tuple): 이미지 크기 (width, height)
            num_classes (int): 클래스 수 (정상, 누설, 과부하)
            batch_size (int): 배치 크기
            epochs (int): 훈련 에포크 수
        """
        self.image_size = image_size
        self.num_classes = num_classes
        self.batch_size = batch_size
        self.epochs = epochs
        self.model = None
        self.history = None
        self.label_encoder = LabelEncoder()
        
        # 클래스 매핑
        self.class_names = ['정상 가동음', '냉기 누설 신호', '과부하 신호']
        self.class_mapping = {
            'normal': 0,
            'leak': 1, 
            'overload': 2
        }
    
    def load_labeled_data(self, labeled_data_dir="labeled_data"):
        """
        라벨링된 데이터를 로드합니다.
        
        Args:
            labeled_data_dir (str): 라벨링된 데이터 디렉토리
            
        Returns:
            tuple: (images, labels) - 이미지 배열과 라벨 배열
        """
        try:
            labeled_dir = Path(labeled_data_dir)
            
            if not labeled_dir.exists():
                raise FileNotFoundError(f"라벨링된 데이터 디렉토리를 찾을 수 없습니다: {labeled_data_dir}")
            
            images = []
            labels = []
            
            # 각 클래스별로 데이터 로드
            for class_name, class_key in self.class_mapping.items():
                class_dir = labeled_dir / class_key
                
                if not class_dir.exists():
                    logger.warning(f"클래스 디렉토리가 없습니다: {class_dir}")
                    continue
                
                # 이미지 파일들 로드
                image_files = list(class_dir.glob("*.png")) + list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.jpeg"))
                
                logger.info(f"클래스 '{class_name}': {len(image_files)}개 이미지 로드 중...")
                
                for img_file in image_files:
                    try:
                        # 이미지 로드 및 전처리
                        img = tf.keras.preprocessing.image.load_img(
                            img_file, 
                            target_size=self.image_size,
                            color_mode='rgb'
                        )
                        img_array = tf.keras.preprocessing.image.img_to_array(img)
                        img_array = img_array / 255.0  # 정규화
                        
                        images.append(img_array)
                        labels.append(class_key)
                        
                    except Exception as e:
                        logger.warning(f"이미지 로드 실패: {img_file} - {e}")
                        continue
            
            if not images:
                raise ValueError("로드된 이미지가 없습니다. 라벨링된 데이터를 확인해주세요.")
            
            # numpy 배열로 변환
            images = np.array(images)
            labels = np.array(labels)
            
            logger.info(f"총 {len(images)}개의 이미지와 {len(labels)}개의 라벨을 로드했습니다.")
            logger.info(f"이미지 형태: {images.shape}")
            logger.info(f"클래스 분포: {np.bincount(labels)}")
            
            return images, labels
            
        except Exception as e:
            logger.error(f"데이터 로드 중 오류 발생: {e}")
            raise
    
    def create_cnn_model(self, input_shape):
        """
        CNN 모델을 생성합니다.
        
        Args:
            input_shape (tuple): 입력 이미지 형태
            
        Returns:
            keras.Model: 생성된 CNN 모델
        """
        try:
            model = keras.Sequential([
                # 입력 레이어
                layers.Input(shape=input_shape),
                
                # 첫 번째 컨볼루션 블록
                layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # 두 번째 컨볼루션 블록
                layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # 세 번째 컨볼루션 블록
                layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # 네 번째 컨볼루션 블록
                layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # 전역 평균 풀링
                layers.GlobalAveragePooling2D(),
                
                # 완전 연결 레이어
                layers.Dense(512, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.5),
                
                layers.Dense(256, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.5),
                
                # 출력 레이어
                layers.Dense(self.num_classes, activation='softmax')
            ])
            
            # 모델 컴파일
            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=0.001),
                loss='sparse_categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info("CNN 모델 생성 완료")
            logger.info(f"모델 파라미터 수: {model.count_params():,}")
            
            return model
            
        except Exception as e:
            logger.error(f"모델 생성 중 오류 발생: {e}")
            raise
    
    def train_model(self, images, labels, validation_split=0.2):
        """
        모델을 훈련합니다.
        
        Args:
            images (np.array): 훈련 이미지 배열
            labels (np.array): 훈련 라벨 배열
            validation_split (float): 검증 데이터 비율
            
        Returns:
            keras.Model: 훈련된 모델
        """
        try:
            # 데이터 분할
            X_train, X_val, y_train, y_val = train_test_split(
                images, labels, 
                test_size=validation_split, 
                random_state=42, 
                stratify=labels
            )
            
            logger.info(f"훈련 데이터: {X_train.shape[0]}개")
            logger.info(f"검증 데이터: {X_val.shape[0]}개")
            
            # 모델 생성
            self.model = self.create_cnn_model(X_train.shape[1:])
            
            # 콜백 설정
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=10,
                    restore_best_weights=True
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=5,
                    min_lr=1e-7
                ),
                keras.callbacks.ModelCheckpoint(
                    'best_model.h5',
                    monitor='val_accuracy',
                    save_best_only=True,
                    mode='max'
                )
            ]
            
            # 데이터 증강
            datagen = keras.preprocessing.image.ImageDataGenerator(
                rotation_range=20,
                width_shift_range=0.1,
                height_shift_range=0.1,
                horizontal_flip=True,
                zoom_range=0.1,
                fill_mode='nearest'
            )
            
            # 모델 훈련
            logger.info("모델 훈련 시작...")
            self.history = self.model.fit(
                datagen.flow(X_train, y_train, batch_size=self.batch_size),
                steps_per_epoch=len(X_train) // self.batch_size,
                epochs=self.epochs,
                validation_data=(X_val, y_val),
                callbacks=callbacks,
                verbose=1
            )
            
            logger.info("모델 훈련 완료")
            
            # 최고 성능 모델 로드
            if os.path.exists('best_model.h5'):
                self.model = keras.models.load_model('best_model.h5')
                logger.info("최고 성능 모델 로드 완료")
            
            return self.model
            
        except Exception as e:
            logger.error(f"모델 훈련 중 오류 발생: {e}")
            raise
    
    def plot_training_history(self, output_dir="results"):
        """
        훈련 과정을 시각화합니다.
        
        Args:
            output_dir (str): 결과 저장 디렉토리
        """
        try:
            if self.history is None:
                logger.warning("훈련 히스토리가 없습니다.")
                return
            
            os.makedirs(output_dir, exist_ok=True)
            
            # 훈련 히스토리 플롯
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # 정확도
            ax1.plot(self.history.history['accuracy'], label='훈련 정확도')
            ax1.plot(self.history.history['val_accuracy'], label='검증 정확도')
            ax1.set_title('모델 정확도')
            ax1.set_xlabel('에포크')
            ax1.set_ylabel('정확도')
            ax1.legend()
            ax1.grid(True)
            
            # 손실
            ax2.plot(self.history.history['loss'], label='훈련 손실')
            ax2.plot(self.history.history['val_loss'], label='검증 손실')
            ax2.set_title('모델 손실')
            ax2.set_xlabel('에포크')
            ax2.set_ylabel('손실')
            ax2.legend()
            ax2.grid(True)
            
            plt.tight_layout()
            
            # 결과 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_path = os.path.join(output_dir, f"training_history_{timestamp}.png")
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.show()
            
            logger.info(f"훈련 히스토리 저장: {plot_path}")
            
        except Exception as e:
            logger.error(f"훈련 히스토리 시각화 중 오류 발생: {e}")
    
    def evaluate_model(self, X_test, y_test):
        """
        모델을 평가합니다.
        
        Args:
            X_test (np.array): 테스트 이미지
            y_test (np.array): 테스트 라벨
        """
        try:
            if self.model is None:
                logger.error("훈련된 모델이 없습니다.")
                return
            
            # 예측
            y_pred = self.model.predict(X_test)
            y_pred_classes = np.argmax(y_pred, axis=1)
            
            # 분류 보고서
            print("\n=== 분류 보고서 ===")
            print(classification_report(
                y_test, y_pred_classes, 
                target_names=self.class_names
            ))
            
            # 혼동 행렬
            cm = confusion_matrix(y_test, y_pred_classes)
            
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=self.class_names,
                       yticklabels=self.class_names)
            plt.title('혼동 행렬')
            plt.xlabel('예측 라벨')
            plt.ylabel('실제 라벨')
            plt.tight_layout()
            plt.show()
            
            # 정확도
            test_loss, test_accuracy = self.model.evaluate(X_test, y_test, verbose=0)
            print(f"\n테스트 정확도: {test_accuracy:.4f}")
            print(f"테스트 손실: {test_loss:.4f}")
            
        except Exception as e:
            logger.error(f"모델 평가 중 오류 발생: {e}")
    
    def save_model(self, model_path="model.h5", output_dir="models"):
        """
        훈련된 모델을 저장합니다.
        
        Args:
            model_path (str): 모델 파일명
            output_dir (str): 저장 디렉토리
        """
        try:
            if self.model is None:
                logger.error("저장할 모델이 없습니다.")
                return
            
            os.makedirs(output_dir, exist_ok=True)
            
            # 모델 저장
            full_path = os.path.join(output_dir, model_path)
            self.model.save(full_path)
            
            # 클래스 정보 저장
            class_info_path = os.path.join(output_dir, "class_info.txt")
            with open(class_info_path, 'w', encoding='utf-8') as f:
                f.write("클래스 매핑:\n")
                for i, class_name in enumerate(self.class_names):
                    f.write(f"{i}: {class_name}\n")
            
            logger.info(f"모델 저장 완료: {full_path}")
            logger.info(f"클래스 정보 저장: {class_info_path}")
            
        except Exception as e:
            logger.error(f"모델 저장 중 오류 발생: {e}")

def main():
    """메인 함수 - CLI 인터페이스"""
    parser = argparse.ArgumentParser(description='AI 모델 훈련 스크립트')
    parser.add_argument('--data-dir', default='labeled_data', 
                       help='라벨링된 데이터 디렉토리 (기본값: labeled_data)')
    parser.add_argument('--output-dir', default='models', 
                       help='모델 저장 디렉토리 (기본값: models)')
    parser.add_argument('--results-dir', default='results', 
                       help='결과 저장 디렉토리 (기본값: results)')
    parser.add_argument('--epochs', type=int, default=50, 
                       help='훈련 에포크 수 (기본값: 50)')
    parser.add_argument('--batch-size', type=int, default=32, 
                       help='배치 크기 (기본값: 32)')
    parser.add_argument('--image-size', nargs=2, type=int, default=[256, 256], 
                       help='이미지 크기 (width height, 기본값: 256 256)')
    parser.add_argument('--validation-split', type=float, default=0.2, 
                       help='검증 데이터 비율 (기본값: 0.2)')
    
    args = parser.parse_args()
    
    # 훈련기 초기화
    trainer = AITrainer(
        image_size=tuple(args.image_size),
        batch_size=args.batch_size,
        epochs=args.epochs
    )
    
    try:
        # 1. 데이터 로드
        logger.info("=== 1단계: 라벨링된 데이터 로드 ===")
        images, labels = trainer.load_labeled_data(args.data_dir)
        
        # 2. 모델 훈련
        logger.info("=== 2단계: 모델 훈련 ===")
        model = trainer.train_model(images, labels, args.validation_split)
        
        # 3. 훈련 히스토리 시각화
        logger.info("=== 3단계: 훈련 히스토리 시각화 ===")
        trainer.plot_training_history(args.results_dir)
        
        # 4. 모델 저장
        logger.info("=== 4단계: 모델 저장 ===")
        trainer.save_model(output_dir=args.output_dir)
        
        print(f"\n✅ AI 모델 훈련 완료!")
        print(f"📁 모델 저장 위치: {args.output_dir}/model.h5")
        print(f"📁 결과 저장 위치: {args.results_dir}/")
        
    except Exception as e:
        logger.error(f"훈련 실패: {e}")
        return

if __name__ == "__main__":
    main()
