#!/usr/bin/env python3
"""
앙상블 냉장고 진단 모델 훈련 스크립트
"""

import os
import sys
import numpy as np
import argparse
from datetime import datetime
from models.ensemble_learning import EnsembleDiagnosis

def create_sample_dataset(num_samples=2000):
    """샘플 데이터셋 생성"""
    print(f"샘플 데이터셋 생성 중... ({num_samples}개 샘플)")
    
    # MFCC 특성 생성
    mfccs = np.random.randn(num_samples, 13, 100)
    
    # 레이블 생성 (실제로는 데이터셋에서 가져와야 함)
    leak_labels = np.random.randint(0, 2, num_samples)
    frequency_labels = np.random.randint(0, 2, num_samples)
    sound_labels = np.random.randint(0, 2, num_samples)
    
    # 데이터셋 저장
    np.savez_compressed('ensemble_dataset.npz',
        mfccs=mfccs,
        leak_labels=leak_labels,
        frequency_labels=frequency_labels,
        sound_labels=sound_labels
    )
    
    print(f"샘플 데이터셋 생성 완료: {num_samples}개 샘플")
    return 'ensemble_dataset.npz'

def load_dataset(dataset_file):
    """데이터셋 로드"""
    try:
        data = np.load(dataset_file, allow_pickle=True)
        
        dataset = {
            'mfccs': data['mfccs'],
            'leak_labels': data['leak_labels'],
            'frequency_labels': data['frequency_labels'],
            'sound_labels': data['sound_labels']
        }
        
        print(f"데이터셋 로드 완료: {dataset_file}")
        print(f"총 샘플 수: {len(dataset['mfccs'])}")
        print(f"냉매 누출 레이블 분포: {np.bincount(dataset['leak_labels'])}")
        print(f"압축기 빈도 레이블 분포: {np.bincount(dataset['frequency_labels'])}")
        print(f"압축기 소리 레이블 분포: {np.bincount(dataset['sound_labels'])}")
        
        return dataset
        
    except Exception as e:
        print(f"데이터셋 로드 오류: {e}")
        return {}

def prepare_training_data(dataset):
    """훈련 데이터 준비"""
    try:
        # 입력 데이터
        X = dataset['mfccs']
        
        # 레이블 딕셔너리
        y = {
            'leak_detection': dataset['leak_labels'],
            'compressor_frequency': dataset['frequency_labels'],
            'compressor_sound': dataset['sound_labels']
        }
        
        print(f"훈련 데이터 준비 완료:")
        print(f"  입력 shape: {X.shape}")
        print(f"  냉매 누출 레이블 분포: {np.bincount(y['leak_detection'])}")
        print(f"  압축기 빈도 레이블 분포: {np.bincount(y['compressor_frequency'])}")
        print(f"  압축기 소리 레이블 분포: {np.bincount(y['compressor_sound'])}")
        
        return X, y
        
    except Exception as e:
        print(f"훈련 데이터 준비 오류: {e}")
        return None, {}

def main():
    parser = argparse.ArgumentParser(description='앙상블 냉장고 진단 모델 훈련')
    parser.add_argument('--dataset', type=str, default='ensemble_dataset.npz',
                       help='데이터셋 파일 경로')
    parser.add_argument('--num_models', type=int, default=5,
                       help='앙상블 모델 개수')
    parser.add_argument('--epochs', type=int, default=50,
                       help='훈련 에포크 수')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='배치 크기')
    parser.add_argument('--bootstrap_ratio', type=float, default=0.8,
                       help='부트스트랩 샘플 비율')
    parser.add_argument('--validation_split', type=float, default=0.2,
                       help='검증 데이터 비율')
    parser.add_argument('--ensemble_name', type=str, default='refrigerator_ensemble',
                       help='앙상블 모델 이름')
    parser.add_argument('--output_dir', type=str, default='trained_models',
                       help='출력 디렉토리')
    parser.add_argument('--create_sample', action='store_true',
                       help='샘플 데이터셋 생성')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("앙상블 냉장고 진단 모델 훈련 시작")
    print("=" * 70)
    print(f"데이터셋: {args.dataset}")
    print(f"앙상블 모델 수: {args.num_models}")
    print(f"에포크: {args.epochs}")
    print(f"배치 크기: {args.batch_size}")
    print(f"부트스트랩 비율: {args.bootstrap_ratio}")
    print(f"검증 데이터 비율: {args.validation_split}")
    print(f"앙상블 이름: {args.ensemble_name}")
    print(f"출력 디렉토리: {args.output_dir}")
    print("=" * 70)
    
    try:
        # 출력 디렉토리 생성
        os.makedirs(args.output_dir, exist_ok=True)
        
        # 샘플 데이터셋 생성 (옵션)
        if args.create_sample or not os.path.exists(args.dataset):
            dataset_file = create_sample_dataset(2000)
        else:
            dataset_file = args.dataset
        
        # 데이터셋 로드
        print("1. 데이터셋 로드 중...")
        dataset = load_dataset(dataset_file)
        
        if not dataset:
            print("데이터셋 로드 실패!")
            return
        
        # 훈련 데이터 준비
        print("2. 훈련 데이터 준비 중...")
        X, y = prepare_training_data(dataset)
        
        if X is None:
            print("훈련 데이터 준비 실패!")
            return
        
        # 앙상블 모델 생성
        print("3. 앙상블 모델 생성 중...")
        input_shape = (13, 100, 1)
        ensemble = EnsembleDiagnosis(
            input_shape=input_shape,
            num_models=args.num_models,
            ensemble_name=args.ensemble_name
        )
        
        # 앙상블 모델 훈련
        print("4. 앙상블 모델 훈련 시작...")
        history = ensemble.train_ensemble(
            X, y,
            validation_split=args.validation_split,
            epochs=args.epochs,
            batch_size=args.batch_size,
            bootstrap_ratio=args.bootstrap_ratio,
            verbose=True
        )
        
        # 앙상블 모델 저장
        print("5. 앙상블 모델 저장 중...")
        model_path = os.path.join(args.output_dir, f'{args.ensemble_name}.h5')
        ensemble.save_ensemble(model_path)
        
        # 훈련 히스토리 시각화
        print("6. 훈련 히스토리 시각화...")
        try:
            history_path = os.path.join(args.output_dir, f'{args.ensemble_name}_training_history.png')
            ensemble.plot_training_history(history, history_path)
        except Exception as e:
            print(f"히스토리 시각화 오류: {e}")
        
        print("=" * 70)
        print("앙상블 모델 훈련 완료!")
        print(f"모델 파일: {model_path}")
        print(f"앙상블 모델 수: {ensemble.num_models}")
        print(f"모델 가중치: {ensemble.model_weights}")
        print("=" * 70)
        
    except Exception as e:
        print(f"훈련 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
