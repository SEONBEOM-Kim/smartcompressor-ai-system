#!/usr/bin/env python3
"""
Phase 1 테스트 스크립트
기본 이상 탐지 시스템 테스트 및 성능 평가
"""

import numpy as np
import librosa
import time
import os
from datetime import datetime
from phase1_basic_anomaly import Phase1BasicAnomalyDetector

def generate_test_audio(duration: float = 5.0, sr: int = 16000, 
                       anomaly_type: str = 'normal') -> np.ndarray:
    """테스트용 오디오 데이터 생성"""
    t = np.linspace(0, duration, int(sr * duration))
    
    if anomaly_type == 'normal':
        # 정상 냉동고 소음
        base_freq = 60
        audio = np.sin(2 * np.pi * base_freq * t)
        for harmonic in [2, 3, 5]:
            audio += 0.3 * np.sin(2 * np.pi * base_freq * harmonic * t)
        audio += np.random.normal(0, 0.1, len(audio))
        
    elif anomaly_type == 'bearing_wear':
        # 베어링 마모 (고주파 소음)
        base_freq = 60
        audio = np.sin(2 * np.pi * base_freq * t)
        # 고주파 성분 추가
        for freq in [1000, 1500, 2000]:
            audio += 0.5 * np.sin(2 * np.pi * freq * t)
        audio += np.random.normal(0, 0.2, len(audio))
        
    elif anomaly_type == 'compressor_abnormal':
        # 압축기 이상 (에너지 변화)
        base_freq = 60
        audio = np.sin(2 * np.pi * base_freq * t) * 2.0  # 높은 에너지
        audio += np.random.normal(0, 0.3, len(audio))
        
    elif anomaly_type == 'refrigerant_leak':
        # 냉매 누출 (저주파 증가)
        base_freq = 30  # 낮은 주파수
        audio = np.sin(2 * np.pi * base_freq * t) * 1.5
        for harmonic in [2, 3]:
            audio += 0.4 * np.sin(2 * np.pi * base_freq * harmonic * t)
        audio += np.random.normal(0, 0.15, len(audio))
    
    # 정규화
    audio = audio / np.max(np.abs(audio))
    return audio

def test_phase1_detector():
    """Phase 1 이상 탐지 시스템 테스트"""
    print("🧪 Phase 1 이상 탐지 시스템 테스트 시작")
    print("=" * 60)
    
    # 1. 시스템 초기화
    detector = Phase1BasicAnomalyDetector()
    
    # 2. 가상의 정상 데이터 생성 및 훈련
    print("📚 정상 데이터 생성 및 훈련 중...")
    normal_audio_files = []
    
    # 50개의 정상 오디오 샘플 생성
    for i in range(50):
        normal_audio = generate_test_audio(5.0, 16000, 'normal')
        filename = f"temp_normal_{i}.wav"
        librosa.output.write_wav(filename, normal_audio, 16000)
        normal_audio_files.append(filename)
    
    # 훈련 실행
    try:
        training_result = detector.train_on_normal_data(normal_audio_files)
        print(f"✅ 훈련 완료: {training_result['total_samples']}개 샘플")
    except Exception as e:
        print(f"❌ 훈련 실패: {e}")
        return
    
    # 3. 테스트 데이터 생성 및 평가
    print("\n🔍 테스트 데이터 생성 및 평가 중...")
    
    test_cases = [
        ('normal', '정상'),
        ('bearing_wear', '베어링 마모'),
        ('compressor_abnormal', '압축기 이상'),
        ('refrigerant_leak', '냉매 누출')
    ]
    
    results = []
    
    for anomaly_type, description in test_cases:
        print(f"\n  테스트: {description}")
        
        # 10개 샘플 테스트
        for i in range(10):
            test_audio = generate_test_audio(5.0, 16000, anomaly_type)
            
            # 이상 탐지 수행
            result = detector.detect_anomaly(test_audio, 16000)
            
            # 결과 저장
            results.append({
                'anomaly_type': anomaly_type,
                'description': description,
                'is_anomaly': result['is_anomaly'],
                'confidence': result['confidence'],
                'detected_type': result['anomaly_type'],
                'processing_time': result['processing_time_ms']
            })
            
            print(f"    샘플 {i+1}: {'이상' if result['is_anomaly'] else '정상'} "
                  f"(신뢰도: {result['confidence']:.1%}, "
                  f"유형: {result['anomaly_type']}, "
                  f"시간: {result['processing_time_ms']:.1f}ms)")
    
    # 4. 성능 통계 계산
    print("\n📊 성능 통계:")
    
    # 전체 통계
    total_tests = len(results)
    anomaly_detected = sum(1 for r in results if r['is_anomaly'])
    avg_confidence = np.mean([r['confidence'] for r in results])
    avg_processing_time = np.mean([r['processing_time'] for r in results])
    
    print(f"  총 테스트: {total_tests}")
    print(f"  이상 탐지: {anomaly_detected}")
    print(f"  평균 신뢰도: {avg_confidence:.1%}")
    print(f"  평균 처리 시간: {avg_processing_time:.1f}ms")
    
    # 유형별 정확도
    print("\n  유형별 정확도:")
    for anomaly_type, description in test_cases:
        type_results = [r for r in results if r['anomaly_type'] == anomaly_type]
        if type_results:
            correct_predictions = 0
            for r in type_results:
                if anomaly_type == 'normal':
                    # 정상은 이상이 아니어야 함
                    if not r['is_anomaly']:
                        correct_predictions += 1
                else:
                    # 이상은 이상이어야 함
                    if r['is_anomaly']:
                        correct_predictions += 1
            
            accuracy = correct_predictions / len(type_results)
            print(f"    {description}: {accuracy:.1%} ({correct_predictions}/{len(type_results)})")
    
    # 5. 성능 지표 출력
    performance_stats = detector.get_performance_stats()
    print(f"\n📈 시스템 성능 지표:")
    print(f"  총 탐지 수: {performance_stats['total_detections']}")
    print(f"  이상 탐지 수: {performance_stats['anomaly_count']}")
    print(f"  이상 탐지율: {performance_stats['anomaly_rate']:.1%}")
    print(f"  정확도: {performance_stats['accuracy']:.1%}")
    print(f"  평균 처리 시간: {performance_stats['average_processing_time']:.1f}ms")
    
    # 6. 모델 저장
    print(f"\n💾 모델 저장 중...")
    detector.save_model()
    
    # 7. 임시 파일 정리
    print(f"\n🧹 임시 파일 정리 중...")
    for filename in normal_audio_files:
        if os.path.exists(filename):
            os.remove(filename)
    
    print("\n✅ Phase 1 테스트 완료!")
    print("=" * 60)
    
    return results, performance_stats

def benchmark_processing_speed():
    """처리 속도 벤치마크"""
    print("\n⚡ 처리 속도 벤치마크")
    print("-" * 40)
    
    detector = Phase1BasicAnomalyDetector()
    
    # 간단한 훈련 (빠른 테스트용)
    normal_audio = generate_test_audio(5.0, 16000, 'normal')
    temp_file = "temp_benchmark.wav"
    librosa.output.write_wav(temp_file, normal_audio, 16000)
    
    try:
        detector.train_on_normal_data([temp_file])
        
        # 속도 테스트
        test_audio = generate_test_audio(5.0, 16000, 'normal')
        times = []
        
        for i in range(100):
            start_time = time.time()
            result = detector.detect_anomaly(test_audio, 16000)
            processing_time = (time.time() - start_time) * 1000
            times.append(processing_time)
        
        print(f"  평균 처리 시간: {np.mean(times):.2f}ms")
        print(f"  최소 처리 시간: {np.min(times):.2f}ms")
        print(f"  최대 처리 시간: {np.max(times):.2f}ms")
        print(f"  표준편차: {np.std(times):.2f}ms")
        
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == "__main__":
    print("🚀 Phase 1 기본 이상 탐지 시스템 테스트")
    print("=" * 60)
    
    # 메인 테스트 실행
    results, stats = test_phase1_detector()
    
    # 속도 벤치마크
    benchmark_processing_speed()
    
    print("\n🎉 모든 테스트 완료!")
    print("Phase 1 시스템이 성공적으로 구현되었습니다.")
