#!/usr/bin/env python3
"""
냉장고 상태 진단 AI 모델 사용 예제
"""

import numpy as np
import os
import sys
sys.path.append('..')

from models.refrigerator_diagnosis_cnn import RefrigeratorDiagnosisCNN

def main():
    print("냉장고 상태 진단 AI 모델 사용 예제")
    print("=" * 50)
    
    # 1. 모델 로드
    model_path = "../trained_models/refrigerator_diagnosis.h5"
    
    if not os.path.exists(model_path):
        print(f"모델 파일이 없습니다: {model_path}")
        print("먼저 모델을 훈련해주세요.")
        print("실행 명령: python3 train_refrigerator_model.py --create_sample")
        return
    
    print("1. 모델 로드 중...")
    model = RefrigeratorDiagnosisCNN(input_shape=(13, 100, 1))
    model.load_model(model_path)
    print("모델 로드 완료!")
    
    # 2. 샘플 데이터 생성
    print("2. 샘플 데이터 생성 중...")
    sample_input = np.random.randn(1, 13, 100, 1)
    print(f"입력 데이터 shape: {sample_input.shape}")
    
    # 3. 모델 예측
    print("3. 모델 예측 중...")
    prediction = model.predict_single(sample_input)
    
    # 4. 결과 출력
    print("\n" + "=" * 50)
    print("냉장고 상태 진단 결과")
    print("=" * 50)
    
    for task, result in prediction.items():
        print(f"\n{task.replace('_', ' ').title()}:")
        print(f"  예측 클래스: {result['predicted_class']}")
        print(f"  신뢰도: {result['confidence']:.2%}")
        print(f"  해석: {result['interpretation']}")
        
        # 확률 분포 출력
        print(f"  확률 분포:")
        for i, prob in enumerate(result['probabilities']):
            class_name = model.class_labels[task][i]
            print(f"    {class_name}: {prob:.2%}")
    
    print("\n" + "=" * 50)
    print("진단 완료!")
    print("=" * 50)

if __name__ == "__main__":
    main()
