#!/usr/bin/env python3
"""
AI 모델 테스트 스크립트
DecisionTreeClassifier 모델의 성능과 오탐 시나리오 테스트
"""

import requests
import time
import json
import numpy as np
import librosa
import tempfile
import os
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def create_test_audio_file(audio_type: str = "normal", duration: float = 5.0) -> str:
    """테스트용 오디오 파일 생성"""
    try:
        # 샘플링 레이트
        sr = 16000
        
        if audio_type == "normal":
            # 정상 압축기 소리 (낮은 주파수, 안정적인 패턴)
            t = np.linspace(0, duration, int(sr * duration))
            # 기본 톤 + 약간의 노이즈
            audio = 0.5 * np.sin(2 * np.pi * 100 * t) + 0.3 * np.sin(2 * np.pi * 200 * t)
            audio += 0.1 * np.random.normal(0, 1, len(t))
            
        elif audio_type == "door_open":
            # 문 열림 상태 소리 (높은 주파수, 불안정한 패턴)
            t = np.linspace(0, duration, int(sr * duration))
            # 높은 주파수 톤 + 많은 노이즈
            audio = 0.8 * np.sin(2 * np.pi * 1000 * t) + 0.6 * np.sin(2 * np.pi * 2000 * t)
            audio += 0.4 * np.random.normal(0, 1, len(t))
            
        else:
            # 기본 소리
            t = np.linspace(0, duration, int(sr * duration))
            audio = 0.3 * np.sin(2 * np.pi * 500 * t)
            audio += 0.2 * np.random.normal(0, 1, len(t))
        
        # 정규화
        audio = audio / np.max(np.abs(audio))
        
        # 임시 파일로 저장
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        librosa.output.write_wav(temp_file.name, audio, sr)
        
        return temp_file.name
        
    except Exception as e:
        print(f"테스트 오디오 파일 생성 실패: {e}")
        return None

def test_model_training():
    """모델 훈련 테스트"""
    print("🧪 AI 모델 훈련 테스트 시작...")
    
    try:
        response = requests.post(f"{API_BASE}/train-compressor-model", json={
            "num_samples": 1000
        })
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 모델 훈련 성공")
            print(f"   - 정확도: {result['training_result']['accuracy']:.4f}")
            print(f"   - 교차 검증: {result['training_result']['cv_mean']:.4f} ± {result['training_result']['cv_std']:.4f}")
            return True
        else:
            print(f"❌ 모델 훈련 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 모델 훈련 테스트 오류: {e}")
        return False

def test_model_info():
    """모델 정보 조회 테스트"""
    print("🧪 모델 정보 조회 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/compressor-model-info")
        
        if response.status_code == 200:
            result = response.json()
            model_info = result['model_info']
            print("✅ 모델 정보 조회 성공")
            print(f"   - 훈련 상태: {model_info['is_trained']}")
            print(f"   - 훈련 횟수: {model_info['training_count']}")
            print(f"   - 최신 정확도: {model_info['latest_accuracy']:.4f}")
            return True
        else:
            print(f"❌ 모델 정보 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 모델 정보 조회 테스트 오류: {e}")
        return False

def test_door_analysis(audio_type: str, expected_result: str):
    """문 상태 분석 테스트"""
    print(f"🧪 {audio_type} 오디오 분석 테스트 시작...")
    
    try:
        # 테스트 오디오 파일 생성
        audio_file_path = create_test_audio_file(audio_type)
        if not audio_file_path:
            print(f"❌ {audio_type} 오디오 파일 생성 실패")
            return False
        
        # API 호출
        with open(audio_file_path, 'rb') as f:
            files = {'audio': f}
            response = requests.post(f"{API_BASE}/compressor-door-analyze", files=files)
        
        # 임시 파일 삭제
        os.unlink(audio_file_path)
        
        if response.status_code == 200:
            result = response.json()
            prediction = result['prediction']
            confidence = result['confidence']
            is_door_open = result['is_door_open']
            
            print(f"✅ {audio_type} 오디오 분석 완료")
            print(f"   - 예측 결과: {prediction}")
            print(f"   - 신뢰도: {confidence:.4f}")
            print(f"   - 문 열림 여부: {is_door_open}")
            
            # 예상 결과와 비교
            if expected_result == "normal" and prediction == "normal":
                print("   ✅ 예상 결과와 일치 (정상)")
                return True
            elif expected_result == "door_open" and prediction == "door_open":
                print("   ✅ 예상 결과와 일치 (문 열림)")
                return True
            else:
                print(f"   ⚠️  예상 결과와 불일치 (예상: {expected_result}, 실제: {prediction})")
                return False
        else:
            print(f"❌ {audio_type} 오디오 분석 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ {audio_type} 오디오 분석 테스트 오류: {e}")
        return False

def test_false_positive_scenarios():
    """오탐 시나리오 테스트"""
    print("🧪 오탐 시나리오 테스트 시작...")
    
    # 다양한 오디오 타입으로 테스트
    test_cases = [
        ("normal", "normal", "정상 압축기 소리"),
        ("door_open", "door_open", "문 열림 소리"),
        ("normal", "normal", "정상 압축기 소리 (반복)"),
        ("normal", "normal", "정상 압축기 소리 (반복)"),
        ("normal", "normal", "정상 압축기 소리 (반복)")
    ]
    
    results = []
    false_positives = 0
    
    for i, (audio_type, expected, description) in enumerate(test_cases):
        print(f"\n📊 테스트 케이스 {i+1}: {description}")
        
        # 테스트 오디오 파일 생성
        audio_file_path = create_test_audio_file(audio_type)
        if not audio_file_path:
            print(f"   ❌ 오디오 파일 생성 실패")
            continue
        
        try:
            # API 호출
            with open(audio_file_path, 'rb') as f:
                files = {'audio': f}
                response = requests.post(f"{API_BASE}/compressor-door-analyze", files=files)
            
            # 임시 파일 삭제
            os.unlink(audio_file_path)
            
            if response.status_code == 200:
                result = response.json()
                prediction = result['prediction']
                confidence = result['confidence']
                
                print(f"   - 예측: {prediction}, 신뢰도: {confidence:.4f}")
                
                # 오탐 확인
                if expected == "normal" and prediction == "door_open":
                    false_positives += 1
                    print(f"   ⚠️  오탐 발생! (정상을 문 열림으로 잘못 분류)")
                elif expected == "door_open" and prediction == "normal":
                    print(f"   ⚠️  미탐 발생! (문 열림을 정상으로 잘못 분류)")
                else:
                    print(f"   ✅ 정확한 분류")
                
                results.append({
                    'case': i+1,
                    'expected': expected,
                    'prediction': prediction,
                    'confidence': confidence,
                    'correct': expected == prediction
                })
            else:
                print(f"   ❌ API 호출 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 테스트 오류: {e}")
    
    # 결과 요약
    print(f"\n📊 오탐 시나리오 테스트 결과:")
    print(f"   - 총 테스트: {len(results)}개")
    print(f"   - 정확한 분류: {len([r for r in results if r['correct']])}개")
    print(f"   - 오탐 (False Positive): {false_positives}개")
    print(f"   - 미탐 (False Negative): {len([r for r in results if not r['correct'] and r['expected'] == 'door_open'])}개")
    print(f"   - 정확도: {len([r for r in results if r['correct']]) / len(results) * 100:.1f}%")
    
    if false_positives > 0:
        print(f"\n⚠️  오탐이 {false_positives}개 발생했습니다!")
        print("   이는 점주에게 다음과 같은 불편함을 줄 수 있습니다:")
        print("   - 새벽 시간대 잘못된 알림으로 인한 수면 방해")
        print("   - 고객과의 대화 중 방해받는 상황")
        print("   - 가족과의 시간 중 중단되는 상황")
        print("   - 중요한 업무 중 방해받는 상황")
    
    return len(results), false_positives

def test_confidence_threshold():
    """신뢰도 임계값 테스트"""
    print("🧪 신뢰도 임계값 테스트 시작...")
    
    # 다양한 신뢰도로 테스트
    confidence_thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
    
    for threshold in confidence_thresholds:
        print(f"\n📊 신뢰도 임계값: {threshold}")
        
        # 정상 오디오로 테스트
        audio_file_path = create_test_audio_file("normal")
        if not audio_file_path:
            continue
        
        try:
            with open(audio_file_path, 'rb') as f:
                files = {'audio': f}
                response = requests.post(f"{API_BASE}/compressor-door-analyze", files=files)
            
            os.unlink(audio_file_path)
            
            if response.status_code == 200:
                result = response.json()
                confidence = result['confidence']
                prediction = result['prediction']
                
                print(f"   - 예측: {prediction}, 신뢰도: {confidence:.4f}")
                
                if confidence >= threshold:
                    print(f"   - 임계값 {threshold} 이상: 알림 전송됨")
                else:
                    print(f"   - 임계값 {threshold} 미만: 알림 전송 안됨")
            else:
                print(f"   ❌ API 호출 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 테스트 오류: {e}")

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 AI 모델 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("모델 훈련", test_model_training),
        ("모델 정보 조회", test_model_info),
        ("정상 오디오 분석", lambda: test_door_analysis("normal", "normal")),
        ("문 열림 오디오 분석", lambda: test_door_analysis("door_open", "door_open")),
        ("오탐 시나리오", test_false_positive_scenarios),
        ("신뢰도 임계값", test_confidence_threshold)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} 테스트...")
        try:
            if test_name == "오탐 시나리오":
                total, false_positives = test_func()
                success = total > 0
                if success:
                    print(f"   📊 총 {total}개 테스트 중 {false_positives}개 오탐 발생")
            else:
                success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 테스트 예외: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # 테스트 간 간격
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{test_name:20} : {status}")
        if success:
            passed += 1
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 테스트 통과! AI 모델이 정상 작동합니다.")
    else:
        print("⚠️  일부 테스트 실패. 모델을 점검해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/api/compressor-model-info", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행 중이지 않습니다. 먼저 Flask 서버를 시작해주세요.")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ 서버에 연결할 수 없습니다. 먼저 Flask 서버를 시작해주세요.")
        exit(1)
    
    # 테스트 실행
    run_all_tests()
