#!/usr/bin/env python3
"""
엔지니어 지식 활용 AI 학습 시스템 실행
기계 설치 전에 엔지니어의 5년 경력을 활용하여 AI 학습 데이터 생성
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """메인 실행 함수"""
    print("🚀 엔지니어 지식 활용 AI 학습 시스템")
    print("=" * 60)
    print("기계 설치 전에 엔지니어의 5년 경력을 활용하여 AI 학습 데이터 생성")
    print("=" * 60)
    
    try:
        # 1단계: 엔지니어 지식 수집 시뮬레이션
        print("\n1️⃣ 엔지니어 지식 수집 시뮬레이션")
        engineer_knowledge = simulate_engineer_knowledge()
        
        # 2단계: 지식 명시화
        print("\n2️⃣ 지식 명시화")
        explicit_rules = convert_to_explicit_rules(engineer_knowledge)
        
        # 3단계: 합성 데이터 생성
        print("\n3️⃣ 합성 데이터 생성")
        synthetic_data = generate_synthetic_data(explicit_rules)
        
        # 4단계: AI 학습 데이터 준비
        print("\n4️⃣ AI 학습 데이터 준비")
        training_data = prepare_training_data(synthetic_data)
        
        # 5단계: 결과 저장
        print("\n5️⃣ 결과 저장")
        save_results(engineer_knowledge, explicit_rules, synthetic_data, training_data)
        
        print("\n🎉 엔지니어 지식 활용 AI 학습 시스템 완료!")
        print("이제 웹 브라우저에서 http://localhost:3000/static/sound_labeling_tool.html 을 열어서")
        print("실제 오디오 파일을 라벨링할 수 있습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False
    
    return True

def simulate_engineer_knowledge():
    """엔지니어 지식 수집 시뮬레이션 (5년 경력 기반)"""
    print("   📚 5년 경력 엔지니어 지식 수집 중...")
    
    # 실제로는 인터뷰를 통해 수집하지만, 여기서는 시뮬레이션
    engineer_knowledge = {
        "engineer_info": {
            "name": "김기술",
            "experience_years": 5,
            "specialization": "산업용 압축기",
            "company": "스마트압축기",
            "interview_date": datetime.now().isoformat()
        },
        
        "sound_classification": {
            "정상_압축기": {
                "description": "일정한 저주파 소음, 안정적인 작동음",
                "frequency_range": "20-200Hz",
                "amplitude_range": "0.1-0.3",
                "temporal_pattern": "일정한 리듬",
                "stability": "높음",
                "confidence": 0.9
            },
            "정상_팬": {
                "description": "일정한 중주파 소음, 부드러운 회전음",
                "frequency_range": "200-1000Hz",
                "amplitude_range": "0.2-0.4",
                "temporal_pattern": "일정한 리듬",
                "stability": "높음",
                "confidence": 0.9
            },
            "정상_모터": {
                "description": "일정한 저주파 소음, 안정적인 구동음",
                "frequency_range": "50-500Hz",
                "amplitude_range": "0.15-0.35",
                "temporal_pattern": "일정한 리듬",
                "stability": "높음",
                "confidence": 0.9
            },
            "베어링_마모": {
                "description": "불규칙한 고주파 진동, 마찰음",
                "frequency_range": "2000-8000Hz",
                "amplitude_range": "0.6-1.0",
                "temporal_pattern": "불규칙한 진동",
                "stability": "낮음",
                "confidence": 0.85
            },
            "언밸런스": {
                "description": "주기적 진동, 불균형 소음",
                "frequency_range": "50-500Hz",
                "amplitude_range": "0.3-0.8",
                "temporal_pattern": "주기적 진동",
                "stability": "중간",
                "confidence": 0.8
            },
            "마찰": {
                "description": "불규칙한 중주파, 마찰음",
                "frequency_range": "500-3000Hz",
                "amplitude_range": "0.25-0.7",
                "temporal_pattern": "불규칙한 패턴",
                "stability": "낮음",
                "confidence": 0.75
            },
            "과부하": {
                "description": "매우 강한 소음, 불규칙한 노이즈",
                "frequency_range": "20-8000Hz",
                "amplitude_range": "0.5-1.0",
                "temporal_pattern": "불규칙한 노이즈",
                "stability": "매우 낮음",
                "confidence": 0.9
            }
        },
        
        "diagnostic_methods": {
            "안정성_평가": {
                "method": "RMS와 ZCR의 변동계수 계산",
                "criteria": "시간에 따른 변화율",
                "threshold": "0.8 이상이면 안정적",
                "confidence": 0.9
            },
            "주파수_일관성": {
                "method": "스펙트럼 센트로이드의 안정성",
                "criteria": "시간에 따른 주파수 분포 변화",
                "threshold": "0.7 이상이면 일관적",
                "confidence": 0.8
            },
            "패턴_규칙성": {
                "method": "자기상관 함수를 이용한 주기성",
                "criteria": "주기적 패턴의 일관성",
                "threshold": "0.7 이상이면 규칙적",
                "confidence": 0.8
            }
        },
        
        "experience_cases": [
            {
                "situation": "베어링 마모 초기 단계",
                "symptoms": ["고주파 진동", "불규칙한 소음", "진동 증가"],
                "diagnosis": "베어링 마모",
                "solution": "베어링 교체",
                "prevention": "정기 윤활 및 모니터링",
                "confidence": 0.9
            },
            {
                "situation": "언밸런스로 인한 진동",
                "symptoms": ["주기적 진동", "불균형 소음", "진동 증가"],
                "diagnosis": "언밸런스",
                "solution": "밸런싱 작업",
                "prevention": "정기 밸런싱 점검",
                "confidence": 0.8
            }
        ],
        
        "heuristic_knowledge": {
            "abnormal_feeling": "소음이 갑자기 증가하면 이상 징후",
            "quick_judgment": "RMS 변화율과 주파수 일관성 확인",
            "noise_level": "정상: 0.1-0.4, 주의: 0.4-0.7, 위험: 0.7 이상",
            "environment": "온도, 습도, 부하에 따라 임계값 조정 필요"
        }
    }
    
    print(f"   ✅ {len(engineer_knowledge['sound_classification'])}개 소리 분류 수집")
    print(f"   ✅ {len(engineer_knowledge['diagnostic_methods'])}개 진단 방법 수집")
    print(f"   ✅ {len(engineer_knowledge['experience_cases'])}개 경험 사례 수집")
    
    return engineer_knowledge

def convert_to_explicit_rules(engineer_knowledge):
    """지식을 명시적 규칙으로 변환"""
    print("   🔄 암묵적 지식 → 명시적 규칙 변환 중...")
    
    explicit_rules = {
        "if_then_rules": [],
        "fuzzy_rules": [],
        "threshold_rules": [],
        "confidence_rules": []
    }
    
    # 소리 분류 규칙 생성
    for sound_type, sound_info in engineer_knowledge["sound_classification"].items():
        rule = {
            "rule_id": f"R_{len(explicit_rules['if_then_rules']) + 1:03d}",
            "description": f"{sound_type} 판단 규칙",
            "if_conditions": [
                f"frequency_range == '{sound_info['frequency_range']}'",
                f"amplitude_range == '{sound_info['amplitude_range']}'",
                f"temporal_pattern == '{sound_info['temporal_pattern']}'",
                f"stability == '{sound_info['stability']}'"
            ],
            "then_action": f"classify_as_{sound_type}",
            "confidence": sound_info["confidence"],
            "source": "engineer_experience"
        }
        explicit_rules["if_then_rules"].append(rule)
    
    # 진단 방법 규칙 생성
    for method_name, method_info in engineer_knowledge["diagnostic_methods"].items():
        rule = {
            "rule_id": f"T_{len(explicit_rules['threshold_rules']) + 1:03d}",
            "description": f"{method_name} 임계값 규칙",
            "method": method_info["method"],
            "threshold": method_info["threshold"],
            "confidence": method_info["confidence"],
            "source": "engineer_experience"
        }
        explicit_rules["threshold_rules"].append(rule)
    
    # 퍼지 규칙 생성
    fuzzy_rule = {
        "rule_id": "F001",
        "description": "소음 레벨 퍼지 판단",
        "input_variables": {
            "noise_level": {
                "low": [0.0, 0.3],
                "medium": [0.2, 0.7],
                "high": [0.6, 1.0]
            }
        },
        "output_variable": "noise_severity",
        "rules": [
            "IF noise_level IS low THEN noise_severity IS normal",
            "IF noise_level IS medium THEN noise_severity IS warning",
            "IF noise_level IS high THEN noise_severity IS critical"
        ]
    }
    explicit_rules["fuzzy_rules"].append(fuzzy_rule)
    
    print(f"   ✅ {len(explicit_rules['if_then_rules'])}개 IF-THEN 규칙 생성")
    print(f"   ✅ {len(explicit_rules['threshold_rules'])}개 임계값 규칙 생성")
    print(f"   ✅ {len(explicit_rules['fuzzy_rules'])}개 퍼지 규칙 생성")
    
    return explicit_rules

def generate_synthetic_data(explicit_rules):
    """합성 데이터 생성"""
    print("   🎵 합성 오디오 데이터 생성 중...")
    
    synthetic_data = {
        "audio_samples": [],
        "feature_vectors": [],
        "labels": [],
        "metadata": []
    }
    
    # 정상 소리 데이터 생성 (100개)
    normal_samples = generate_normal_samples(100)
    synthetic_data["audio_samples"].extend(normal_samples["samples"])
    synthetic_data["feature_vectors"].extend(normal_samples["features"])
    synthetic_data["labels"].extend(normal_samples["labels"])
    synthetic_data["metadata"].extend(normal_samples["metadata"])
    
    # 이상 소리 데이터 생성 (100개)
    abnormal_samples = generate_abnormal_samples(100)
    synthetic_data["audio_samples"].extend(abnormal_samples["samples"])
    synthetic_data["feature_vectors"].extend(abnormal_samples["features"])
    synthetic_data["labels"].extend(abnormal_samples["labels"])
    synthetic_data["metadata"].extend(abnormal_samples["metadata"])
    
    print(f"   ✅ {len(synthetic_data['audio_samples'])}개 합성 오디오 샘플 생성")
    print(f"   ✅ {len(synthetic_data['feature_vectors'])}개 특징 벡터 생성")
    print(f"   ✅ {len(synthetic_data['labels'])}개 라벨 생성")
    
    return synthetic_data

def generate_normal_samples(count):
    """정상 소리 샘플 생성"""
    samples = []
    features = []
    labels = []
    metadata = []
    
    for i in range(count):
        # 정상 소리 특성 (엔지니어 지식 기반)
        if i < count // 3:
            # 정상 압축기
            sample = generate_compressor_sound()
            label = "normal_compressor"
        elif i < 2 * count // 3:
            # 정상 팬
            sample = generate_fan_sound()
            label = "normal_fan"
        else:
            # 정상 모터
            sample = generate_motor_sound()
            label = "normal_motor"
        
        # 특징 추출
        feature_vector = extract_features(sample)
        
        samples.append(sample)
        features.append(feature_vector)
        labels.append(label)
        metadata.append({
            "type": "synthetic",
            "category": "normal",
            "subcategory": label,
            "generation_time": datetime.now().isoformat()
        })
    
    return {
        "samples": samples,
        "features": features,
        "labels": labels,
        "metadata": metadata
    }

def generate_abnormal_samples(count):
    """이상 소리 샘플 생성"""
    samples = []
    features = []
    labels = []
    metadata = []
    
    for i in range(count):
        # 이상 소리 특성 (엔지니어 지식 기반)
        if i < count // 4:
            # 베어링 마모
            sample = generate_bearing_wear_sound()
            label = "abnormal_bearing"
        elif i < count // 2:
            # 언밸런스
            sample = generate_unbalance_sound()
            label = "abnormal_unbalance"
        elif i < 3 * count // 4:
            # 마찰
            sample = generate_friction_sound()
            label = "abnormal_friction"
        else:
            # 과부하
            sample = generate_overload_sound()
            label = "abnormal_overload"
        
        # 특징 추출
        feature_vector = extract_features(sample)
        
        samples.append(sample)
        features.append(feature_vector)
        labels.append(label)
        metadata.append({
            "type": "synthetic",
            "category": "abnormal",
            "subcategory": label,
            "generation_time": datetime.now().isoformat()
        })
    
    return {
        "samples": samples,
        "features": features,
        "labels": labels,
        "metadata": metadata
    }

def generate_compressor_sound():
    """정상 압축기 소리 생성"""
    # 5초, 22050Hz 샘플링
    duration = 5.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 저주파 기본 신호 (20-200Hz)
    base_freq = 60  # 기본 주파수
    signal = np.sin(2 * np.pi * base_freq * t)
    
    # 하모닉 추가
    signal += 0.3 * np.sin(2 * np.pi * base_freq * 2 * t)
    signal += 0.1 * np.sin(2 * np.pi * base_freq * 3 * t)
    
    # 노이즈 추가 (정상 범위)
    noise = np.random.normal(0, 0.05, len(t))
    signal += noise
    
    # 진폭 조정 (0.1-0.3)
    signal *= 0.2
    
    return signal

def generate_fan_sound():
    """정상 팬 소리 생성"""
    duration = 5.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 중주파 기본 신호 (200-1000Hz)
    base_freq = 400
    signal = np.sin(2 * np.pi * base_freq * t)
    
    # 하모닉 추가
    signal += 0.2 * np.sin(2 * np.pi * base_freq * 2 * t)
    signal += 0.1 * np.sin(2 * np.pi * base_freq * 3 * t)
    
    # 노이즈 추가
    noise = np.random.normal(0, 0.03, len(t))
    signal += noise
    
    # 진폭 조정 (0.2-0.4)
    signal *= 0.3
    
    return signal

def generate_motor_sound():
    """정상 모터 소리 생성"""
    duration = 5.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 저주파 기본 신호 (50-500Hz)
    base_freq = 150
    signal = np.sin(2 * np.pi * base_freq * t)
    
    # 하모닉 추가
    signal += 0.25 * np.sin(2 * np.pi * base_freq * 2 * t)
    signal += 0.1 * np.sin(2 * np.pi * base_freq * 3 * t)
    
    # 노이즈 추가
    noise = np.random.normal(0, 0.04, len(t))
    signal += noise
    
    # 진폭 조정 (0.15-0.35)
    signal *= 0.25
    
    return signal

def generate_bearing_wear_sound():
    """베어링 마모 소리 생성"""
    duration = 5.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 고주파 마찰음 (2000-8000Hz)
    base_freq = 3000
    signal = np.sin(2 * np.pi * base_freq * t)
    
    # 불규칙한 진동 추가
    irregularity = np.random.normal(1, 0.3, len(t))
    signal *= irregularity
    
    # 고주파 노이즈 추가
    noise = np.random.normal(0, 0.2, len(t))
    signal += noise
    
    # 진폭 조정 (0.6-1.0)
    signal *= 0.8
    
    return signal

def generate_unbalance_sound():
    """언밸런스 소리 생성"""
    duration = 5.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 주기적 진동 (50-500Hz)
    base_freq = 200
    signal = np.sin(2 * np.pi * base_freq * t)
    
    # 주기적 진동 추가
    vibration = 0.5 * np.sin(2 * np.pi * 0.5 * t)  # 0.5Hz 진동
    signal *= (1 + vibration)
    
    # 노이즈 추가
    noise = np.random.normal(0, 0.1, len(t))
    signal += noise
    
    # 진폭 조정 (0.3-0.8)
    signal *= 0.5
    
    return signal

def generate_friction_sound():
    """마찰 소리 생성"""
    duration = 5.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 중주파 마찰음 (500-3000Hz)
    base_freq = 1500
    signal = np.sin(2 * np.pi * base_freq * t)
    
    # 불규칙한 마찰 패턴
    friction_pattern = np.random.normal(1, 0.4, len(t))
    signal *= friction_pattern
    
    # 노이즈 추가
    noise = np.random.normal(0, 0.15, len(t))
    signal += noise
    
    # 진폭 조정 (0.25-0.7)
    signal *= 0.45
    
    return signal

def generate_overload_sound():
    """과부하 소리 생성"""
    duration = 5.0
    sample_rate = 22050
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # 전체 주파수 대역 노이즈 (20-8000Hz)
    signal = np.zeros(len(t))
    
    # 여러 주파수 대역의 노이즈
    for freq in [100, 500, 1000, 2000, 4000, 6000]:
        signal += 0.3 * np.sin(2 * np.pi * freq * t)
    
    # 강한 노이즈 추가
    noise = np.random.normal(0, 0.3, len(t))
    signal += noise
    
    # 진폭 조정 (0.5-1.0)
    signal *= 0.7
    
    return signal

def extract_features(signal):
    """오디오 신호에서 특징 추출"""
    # 간단한 특징 추출 (실제로는 더 복잡한 특징 사용)
    features = [
        np.mean(signal),  # 평균
        np.std(signal),   # 표준편차
        np.max(signal),   # 최대값
        np.min(signal),   # 최소값
        np.var(signal),   # 분산
        np.mean(np.abs(signal)),  # 평균 절대값
        np.max(np.abs(signal)),   # 최대 절대값
        np.sum(np.abs(signal)),   # 총 에너지
        np.mean(signal**2),       # 평균 제곱
        np.std(np.diff(signal))   # 차분의 표준편차
    ]
    
    return features

def prepare_training_data(synthetic_data):
    """AI 학습용 데이터 준비"""
    print("   🤖 AI 학습용 데이터 준비 중...")
    
    training_data = {
        "X": np.array(synthetic_data["feature_vectors"]),
        "y": synthetic_data["labels"],
        "metadata": synthetic_data["metadata"],
        "feature_names": [
            "mean", "std", "max", "min", "var",
            "mean_abs", "max_abs", "total_energy",
            "mean_squared", "diff_std"
        ],
        "label_mapping": {
            "normal_compressor": 0,
            "normal_fan": 1,
            "normal_motor": 2,
            "abnormal_bearing": 3,
            "abnormal_unbalance": 4,
            "abnormal_friction": 5,
            "abnormal_overload": 6
        }
    }
    
    print(f"   ✅ {training_data['X'].shape[0]}개 학습 샘플 준비")
    print(f"   ✅ {training_data['X'].shape[1]}개 특징 사용")
    print(f"   ✅ {len(training_data['label_mapping'])}개 클래스 정의")
    
    return training_data

def save_results(engineer_knowledge, explicit_rules, synthetic_data, training_data):
    """결과 저장"""
    print("   💾 결과 저장 중...")
    
    # 결과 디렉토리 생성
    os.makedirs("data/engineer_knowledge", exist_ok=True)
    os.makedirs("data/synthetic_data", exist_ok=True)
    os.makedirs("data/training_data", exist_ok=True)
    
    # 엔지니어 지식 저장
    with open("data/engineer_knowledge/engineer_knowledge.json", "w", encoding="utf-8") as f:
        json.dump(engineer_knowledge, f, indent=2, ensure_ascii=False)
    
    # 명시적 규칙 저장
    with open("data/engineer_knowledge/explicit_rules.json", "w", encoding="utf-8") as f:
        json.dump(explicit_rules, f, indent=2, ensure_ascii=False)
    
    # 합성 데이터 저장 (메타데이터만)
    synthetic_metadata = {
        "total_samples": len(synthetic_data["audio_samples"]),
        "feature_vectors": synthetic_data["feature_vectors"],
        "labels": synthetic_data["labels"],
        "metadata": synthetic_data["metadata"]
    }
    
    with open("data/synthetic_data/synthetic_metadata.json", "w", encoding="utf-8") as f:
        json.dump(synthetic_metadata, f, indent=2, ensure_ascii=False)
    
    # 학습 데이터 저장
    training_metadata = {
        "X_shape": training_data["X"].shape,
        "y": training_data["y"],
        "feature_names": training_data["feature_names"],
        "label_mapping": training_data["label_mapping"],
        "X_data": training_data["X"].tolist()  # numpy 배열을 리스트로 변환
    }
    
    with open("data/training_data/training_metadata.json", "w", encoding="utf-8") as f:
        json.dump(training_metadata, f, indent=2, ensure_ascii=False)
    
    print("   ✅ 모든 결과 저장 완료")
    print("   📁 저장 위치:")
    print("      - data/engineer_knowledge/")
    print("      - data/synthetic_data/")
    print("      - data/training_data/")

if __name__ == "__main__":
    main()
