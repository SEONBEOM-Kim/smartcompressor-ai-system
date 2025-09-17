#!/usr/bin/env python3
"""
앙상블 모듈 단위 테스트
"""

import numpy as np
import os
import sys
sys.path.append('.')

from models.ensemble_learning import EnsembleDiagnosis

def test_ensemble_creation():
    """앙상블 모델 생성 테스트"""
    print("테스트 1: 앙상블 모델 생성")
    
    input_shape = (13, 100, 1)
    ensemble = EnsembleDiagnosis(input_shape, num_models=3)
    
    assert ensemble.num_models == 3
    assert ensemble.input_shape == input_shape
    assert len(ensemble.models) == 3
    assert len(ensemble.model_weights) == 3
    
    print("✓ 앙상블 모델 생성 성공")
    return ensemble

def test_ensemble_training(ensemble):
    """앙상블 모델 훈련 테스트"""
    print("\n테스트 2: 앙상블 모델 훈련")
    
    # 샘플 데이터 생성
    X = np.random.randn(100, 13, 100, 1)
    y = {
        'leak_detection': np.random.randint(0, 2, 100),
        'compressor_frequency': np.random.randint(0, 2, 100),
        'compressor_sound': np.random.randint(0, 2, 100)
    }
    
    # 훈련 실행
    history = ensemble.train_ensemble(
        X, y,
        validation_split=0.2,
        epochs=5,  # 빠른 테스트
        batch_size=16,
        bootstrap_ratio=0.8,
        verbose=False
    )
    
    assert ensemble.is_trained == True
    assert len(history['individual_histories']) == 3
    assert len(history['model_weights']) == 3
    
    print("✓ 앙상블 모델 훈련 성공")
    return history

def test_ensemble_prediction(ensemble):
    """앙상블 모델 예측 테스트"""
    print("\n테스트 3: 앙상블 모델 예측")
    
    # 단일 샘플 예측
    test_sample = np.random.randn(1, 13, 100, 1)
    prediction = ensemble.predict_single(test_sample)
    
    assert 'leak_detection' in prediction
    assert 'compressor_frequency' in prediction
    assert 'compressor_sound' in prediction
    
    for task, result in prediction.items():
        assert 'predicted_class' in result
        assert 'confidence' in result
        assert 'probabilities' in result
        assert 'interpretation' in result
    
    print("✓ 단일 샘플 예측 성공")
    
    # 배치 예측
    test_batch = np.random.randn(5, 13, 100, 1)
    batch_predictions = ensemble.predict_ensemble(test_batch)
    
    assert 'leak_detection' in batch_predictions
    assert 'compressor_frequency' in batch_predictions
    assert 'compressor_sound' in batch_predictions
    
    for task, result in batch_predictions.items():
        assert len(result['predicted_classes']) == 5
        assert len(result['confidences']) == 5
    
    print("✓ 배치 예측 성공")

def test_ensemble_save_load(ensemble):
    """앙상블 모델 저장/로드 테스트"""
    print("\n테스트 4: 앙상블 모델 저장/로드")
    
    # 모델 저장
    os.makedirs('test_models', exist_ok=True)
    save_path = 'test_models/test_ensemble.h5'
    ensemble.save_ensemble(save_path)
    
    assert os.path.exists(save_path)
    assert os.path.exists(save_path.replace('.h5', '_metadata.json'))
    
    print("✓ 앙상블 모델 저장 성공")
    
    # 모델 로드
    new_ensemble = EnsembleDiagnosis((13, 100, 1))
    new_ensemble.load_ensemble(save_path)
    
    assert new_ensemble.num_models == ensemble.num_models
    assert new_ensemble.input_shape == ensemble.input_shape
    assert new_ensemble.is_trained == True
    
    print("✓ 앙상블 모델 로드 성공")
    
    # 로드된 모델로 예측 테스트
    test_sample = np.random.randn(1, 13, 100, 1)
    prediction = new_ensemble.predict_single(test_sample)
    
    assert 'leak_detection' in prediction
    print("✓ 로드된 모델 예측 성공")
    
    # 테스트 파일 정리
    import shutil
    shutil.rmtree('test_models')
    print("✓ 테스트 파일 정리 완료")

def main():
    print("앙상블 모듈 단위 테스트 시작")
    print("=" * 50)
    
    try:
        # 테스트 실행
        ensemble = test_ensemble_creation()
        history = test_ensemble_training(ensemble)
        test_ensemble_prediction(ensemble)
        test_ensemble_save_load(ensemble)
        
        print("\n" + "=" * 50)
        print("모든 테스트 통과! ✓")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
