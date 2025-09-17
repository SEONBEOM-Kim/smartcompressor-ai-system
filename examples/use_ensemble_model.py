#!/usr/bin/env python3
"""
앙상블 냉장고 진단 모델 사용 예제
"""

import numpy as np
import os
import sys
sys.path.append('..')

from models.ensemble_learning import EnsembleDiagnosis

def create_sample_data(n_samples=1000):
    """샘플 데이터 생성"""
    print(f"샘플 데이터 생성 중... ({n_samples}개 샘플)")
    
    # MFCC 특성 생성 (13, 100, 1)
    X = np.random.randn(n_samples, 13, 100, 1)
    
    # 레이블 생성
    y = {
        'leak_detection': np.random.randint(0, 2, n_samples),
        'compressor_frequency': np.random.randint(0, 2, n_samples),
        'compressor_sound': np.random.randint(0, 2, n_samples)
    }
    
    print(f"데이터 생성 완료:")
    print(f"  입력 shape: {X.shape}")
    print(f"  냉매 누출 레이블 분포: {np.bincount(y['leak_detection'])}")
    print(f"  압축기 빈도 레이블 분포: {np.bincount(y['compressor_frequency'])}")
    print(f"  압축기 소리 레이블 분포: {np.bincount(y['compressor_sound'])}")
    
    return X, y

def main():
    print("앙상블 냉장고 진단 모델 사용 예제")
    print("=" * 60)
    
    # 1. 앙상블 모델 생성
    print("1. 앙상블 모델 생성 중...")
    input_shape = (13, 100, 1)
    ensemble = EnsembleDiagnosis(
        input_shape=input_shape,
        num_models=5,  # 5개 모델로 앙상블 구성
        ensemble_name="refrigerator_ensemble"
    )
    print(f"앙상블 모델 생성 완료: {ensemble.num_models}개 모델")
    
    # 2. 샘플 데이터 생성
    print("\n2. 샘플 데이터 생성 중...")
    X, y = create_sample_data(1000)
    
    # 3. 앙상블 모델 훈련
    print("\n3. 앙상블 모델 훈련 중...")
    history = ensemble.train_ensemble(
        X, y,
        validation_split=0.2,
        epochs=20,  # 빠른 테스트를 위해 에포크 수 줄임
        batch_size=32,
        bootstrap_ratio=0.8,
        verbose=True
    )
    
    # 4. 앙상블 모델 저장
    print("\n4. 앙상블 모델 저장 중...")
    os.makedirs('../trained_models', exist_ok=True)
    ensemble.save_ensemble('../trained_models/refrigerator_ensemble.h5')
    
    # 5. 단일 샘플 예측 테스트
    print("\n5. 단일 샘플 예측 테스트...")
    test_sample = np.random.randn(1, 13, 100, 1)
    prediction = ensemble.predict_single(test_sample)
    
    print("\n" + "=" * 60)
    print("앙상블 예측 결과")
    print("=" * 60)
    
    for task, result in prediction.items():
        print(f"\n{task.replace('_', ' ').title()}:")
        print(f"  예측 클래스: {result['predicted_class']}")
        print(f"  신뢰도: {result['confidence']:.2%}")
        print(f"  해석: {result['interpretation']}")
        
        # 확률 분포 출력
        print(f"  확률 분포:")
        for i, prob in enumerate(result['probabilities']):
            class_name = ensemble.class_labels[task][i]
            print(f"    {class_name}: {prob:.2%}")
    
    # 6. 배치 예측 테스트
    print("\n6. 배치 예측 테스트...")
    test_batch = np.random.randn(5, 13, 100, 1)
    batch_predictions = ensemble.predict_ensemble(test_batch)
    
    print(f"\n배치 예측 결과 ({len(test_batch)}개 샘플):")
    for i in range(len(test_batch)):
        print(f"\n샘플 {i+1}:")
        for task, result in batch_predictions.items():
            pred_class = result['predicted_classes'][i]
            confidence = result['confidences'][i]
            class_name = ensemble.class_labels[task][pred_class]
            print(f"  {task}: {class_name} (신뢰도: {confidence:.2%})")
    
    # 7. 훈련 히스토리 시각화
    print("\n7. 훈련 히스토리 시각화...")
    try:
        ensemble.plot_training_history(history, '../trained_models/ensemble_training_history.png')
    except Exception as e:
        print(f"히스토리 시각화 오류: {e}")
    
    print("\n" + "=" * 60)
    print("앙상블 모델 테스트 완료!")
    print("=" * 60)
    
    # 8. 모델 로드 테스트
    print("\n8. 모델 로드 테스트...")
    try:
        new_ensemble = EnsembleDiagnosis(input_shape)
        new_ensemble.load_ensemble('../trained_models/refrigerator_ensemble.h5')
        
        # 로드된 모델로 예측 테스트
        test_sample = np.random.randn(1, 13, 100, 1)
        loaded_prediction = new_ensemble.predict_single(test_sample)
        
        print("모델 로드 및 예측 테스트 성공!")
        print(f"로드된 모델 수: {new_ensemble.num_models}")
        print(f"모델 가중치: {new_ensemble.model_weights}")
        
    except Exception as e:
        print(f"모델 로드 테스트 오류: {e}")

if __name__ == "__main__":
    main()
