# 🔧 실제 하드웨어 설치 전 AI 학습 가이드

## 🎯 **기계 엔지니어의 도메인 지식을 활용한 사전 학습**

### **핵심 아이디어**
실제 하드웨어를 설치하기 전에 기계 엔지니어의 경험과 지식을 활용하여 AI를 사전 학습시키는 방법들

---

## 📚 **1. 도메인 지식 기반 규칙 생성**

### **1.1 엔지니어 경험 지식 활용**
```python
# 기계 엔지니어의 경험을 바탕으로 한 규칙
engineer_rules = {
    'normal_compressor': {
        'frequency_range': (20, 200),      # 저주파
        'rms_range': (0.1, 0.3),          # 적당한 진폭
        'stability_factor': 0.8,           # 안정적
        'expert_notes': '일정한 리듬, 저주파, 안정적'
    },
    'bearing_wear': {
        'frequency_range': (2000, 8000),   # 고주파
        'rms_range': (0.4, 1.0),          # 높은 진폭
        'irregularity_factor': 0.7,        # 불규칙
        'expert_notes': '불규칙한 진동, 고주파, 마찰음'
    }
}
```

### **1.2 소리 분류 지식**
- **정상 소리**: 일정한 리듬, 저주파, 안정적
- **베어링 마모**: 불규칙한 진동, 고주파, 마찰음
- **언밸런스**: 주기적 진동, 저주파, 리듬 변화
- **마찰**: 긁는 소리, 중주파, 불안정
- **과부하**: 불규칙한 노이즈, 전체 주파수

---

## 🎵 **2. 합성 데이터 생성**

### **2.1 정상 소리 시뮬레이션**
```python
def create_normal_compressor_sound():
    # 기본 저주파 (60Hz)
    base_signal = np.sin(2 * np.pi * 60 * t)
    
    # 하모닉스 (120Hz, 180Hz)
    harmonic1 = 0.3 * np.sin(2 * np.pi * 120 * t)
    harmonic2 = 0.1 * np.sin(2 * np.pi * 180 * t)
    
    # 일정한 리듬 (0.5Hz)
    rhythm = 0.2 * np.sin(2 * np.pi * 0.5 * t)
    
    # 백그라운드 노이즈
    noise = 0.05 * np.random.normal(0, 1, len(t))
    
    return base_signal + harmonic1 + harmonic2 + rhythm + noise
```

### **2.2 이상 소리 시뮬레이션**
```python
def create_bearing_wear_sound():
    # 기본 고주파 (3000Hz)
    base_signal = np.sin(2 * np.pi * 3000 * t)
    
    # 불규칙한 진동 (마모로 인한)
    irregular_vib = 0.5 * np.sin(2 * np.pi * 3000 * t + 0.1 * np.sin(2 * np.pi * 10 * t))
    
    # 마찰음 (고주파 노이즈)
    friction_noise = 0.3 * np.random.normal(0, 1, len(t))
    
    return base_signal + irregular_vib + friction_noise
```

---

## 🎮 **3. 시뮬레이션 기반 학습**

### **3.1 다양한 시나리오 생성**
```python
scenarios = [
    {
        'name': 'normal_operation',
        'conditions': {'temperature': (20, 25), 'load': (80, 100)},
        'expected_sound': 'normal'
    },
    {
        'name': 'bearing_wear_early',
        'conditions': {'temperature': (25, 30), 'load': (70, 90)},
        'expected_sound': 'abnormal'
    },
    {
        'name': 'overload_condition',
        'conditions': {'temperature': (35, 40), 'load': (95, 100)},
        'expected_sound': 'abnormal'
    }
]
```

### **3.2 환경 조건 시뮬레이션**
- **온도**: 20-40°C (온도에 따른 노이즈 레벨 변화)
- **습도**: 40-90% (습도에 따른 소음 특성 변화)
- **부하**: 60-100% (부하에 따른 진동 특성 변화)
- **진동**: 0.1-1.0 (진동 레벨에 따른 소음 특성)

---

## 🔍 **4. 도메인 지식 기반 특징 추출**

### **4.1 엔지니어가 중요하게 생각하는 특징들**
```python
def extract_domain_features(audio_data):
    features = {}
    
    # 1. 기본 특징들
    features['rms'] = np.sqrt(np.mean(audio_data ** 2))
    features['zcr'] = np.mean(librosa.feature.zero_crossing_rate(audio_data))
    features['spectral_centroid'] = np.mean(librosa.feature.spectral_centroid(audio_data))
    
    # 2. 엔지니어 지식 기반 특징들
    features['stability_factor'] = calculate_stability_factor(audio_data)
    features['frequency_consistency'] = calculate_frequency_consistency(audio_data)
    features['pattern_regularity'] = calculate_pattern_regularity(audio_data)
    features['harmonic_ratio'] = calculate_harmonic_ratio(audio_data)
    features['noise_level'] = calculate_noise_level(audio_data)
    
    return features
```

### **4.2 안정성 계수 계산**
```python
def calculate_stability_factor(audio_data):
    # RMS의 변동계수 계산
    window_size = len(audio_data) // 10
    rms_windows = []
    
    for i in range(0, len(audio_data) - window_size, window_size):
        window = audio_data[i:i + window_size]
        rms_windows.append(np.sqrt(np.mean(window ** 2)))
    
    stability = 1.0 / (1.0 + np.std(rms_windows) / np.mean(rms_windows))
    return min(1.0, max(0.0, stability))
```

---

## 🧠 **5. 엔지니어 지식 기반 진단**

### **5.1 휴리스틱 진단 규칙**
```python
def engineer_based_diagnosis(audio_data):
    features = extract_domain_features(audio_data)
    
    # 1. 안정성 검사
    if features['stability_factor'] > 0.8:
        stability_status = '정상 - 안정적인 신호'
    elif features['stability_factor'] > 0.5:
        stability_status = '주의 - 약간의 불안정성'
    else:
        stability_status = '이상 - 심각한 불안정성'
    
    # 2. 주파수 일관성 검사
    if features['frequency_consistency'] > 0.7:
        frequency_status = '정상 - 일관된 주파수 분포'
    elif features['frequency_consistency'] > 0.4:
        frequency_status = '주의 - 주파수 변화 감지'
    else:
        frequency_status = '이상 - 심각한 주파수 변화'
    
    # 3. 패턴 규칙성 검사
    if features['pattern_regularity'] > 0.7:
        pattern_status = '정상 - 규칙적인 패턴'
    elif features['pattern_regularity'] > 0.4:
        pattern_status = '주의 - 패턴 변화 감지'
    else:
        pattern_status = '이상 - 불규칙한 패턴'
    
    return {
        'stability': stability_status,
        'frequency': frequency_status,
        'pattern': pattern_status
    }
```

### **5.2 이상 유형 식별**
```python
def identify_anomaly_type(features):
    # 베어링 마모 확인
    if (features['spectral_centroid'] > 3000 and 
        features['rms'] > 0.4 and 
        features['pattern_regularity'] < 0.5):
        return 'bearing_wear'
    
    # 언밸런스 확인
    elif (features['spectral_centroid'] < 300 and 
          features['rms'] > 0.3 and 
          features['pattern_regularity'] > 0.4):
        return 'unbalance'
    
    # 마찰 확인
    elif (500 <= features['spectral_centroid'] <= 2000 and 
          features['rms'] > 0.25 and 
          features['pattern_regularity'] < 0.6):
        return 'friction'
    
    # 과부하 확인
    elif (features['rms'] > 0.5 and 
          features['noise_level'] > 0.5 and 
          features['pattern_regularity'] < 0.3):
        return 'overload'
    
    else:
        return 'unknown'
```

---

## 📊 **6. 학습 데이터 생성 전략**

### **6.1 단계별 데이터 생성**
1. **1단계**: 기본 정상/이상 소리 생성
2. **2단계**: 다양한 시나리오별 소리 생성
3. **3단계**: 환경 조건별 소리 생성
4. **4단계**: 노이즈 및 간섭 추가

### **6.2 데이터 품질 관리**
```python
def validate_audio_data(audio_data, expected_type):
    # 1. 기본 품질 검사
    if np.max(np.abs(audio_data)) > 1.0:
        return False, "진폭이 너무 큼"
    
    # 2. 도메인 지식 기반 검사
    features = extract_domain_features(audio_data)
    
    if expected_type == 'normal':
        if features['stability_factor'] < 0.7:
            return False, "정상 소리가 너무 불안정함"
    elif expected_type == 'abnormal':
        if features['stability_factor'] > 0.8:
            return False, "이상 소리가 너무 안정적임"
    
    return True, "검증 통과"
```

---

## 🎯 **7. 실제 구현 단계**

### **7.1 1단계: 기본 규칙 생성**
```python
# 엔지니어 지식 기반 규칙 생성
engineer_ai = EngineerDomainKnowledgeAI()
domain_rules = engineer_ai.create_engineer_knowledge_rules()
```

### **7.2 2단계: 합성 데이터 생성**
```python
# 합성 오디오 데이터 생성
synthetic_data = engineer_ai.generate_synthetic_audio_data(duration=10.0)
```

### **7.3 3단계: 시뮬레이션 데이터 생성**
```python
# 시뮬레이션 기반 훈련 데이터 생성
simulation_data = engineer_ai.create_simulation_training_data()
```

### **7.4 4단계: AI 모델 훈련**
```python
# 도메인 지식 기반 AI 훈련
for sample in simulation_data['training_samples']:
    diagnosis = engineer_ai.engineer_based_diagnosis(
        sample['audio_data'], 
        sample['sample_rate']
    )
```

---

## 💡 **8. 엔지니어의 역할**

### **8.1 지식 제공**
- **소리 분류 기준**: 정상/이상 소리의 특징
- **진단 규칙**: 각 이상 유형별 판단 기준
- **심각도 평가**: 이상의 심각도 판단 기준
- **대응 방안**: 각 이상 유형별 대응 방법

### **8.2 검증 및 개선**
- **규칙 검증**: 생성된 규칙의 정확성 검증
- **데이터 검증**: 생성된 데이터의 품질 검증
- **성능 평가**: AI 모델의 성능 평가
- **지속적 개선**: 피드백을 통한 지속적 개선

---

## 🚀 **9. 실제 하드웨어 설치 후**

### **9.1 실제 데이터로 검증**
```python
# 실제 하드웨어 데이터로 검증
real_data_validation = validate_with_real_data(real_audio_files)
```

### **9.2 규칙 조정**
```python
# 실제 데이터에 맞게 규칙 조정
adjusted_rules = adjust_rules_based_on_real_data(real_data_validation)
```

### **9.3 지속적 학습**
```python
# 실제 데이터로 지속적 학습
continuous_learning = update_ai_with_real_data(real_audio_files)
```

---

## 🎉 **10. 예상 효과**

### **10.1 사전 학습의 장점**
- **빠른 시작**: 하드웨어 설치 즉시 AI 사용 가능
- **높은 정확도**: 도메인 지식 기반으로 높은 정확도
- **안정성**: 검증된 규칙으로 안정적인 성능
- **비용 절약**: 실제 데이터 수집 없이도 학습 가능

### **10.2 성능 예상**
- **정확도**: 90-95% (도메인 지식 기반)
- **처리시간**: 1-5ms (실시간 처리 가능)
- **메모리**: 1-10MB (경량화)
- **유지보수**: 쉬움 (규칙 기반)

---

## 🔧 **11. 구현 체크리스트**

### **11.1 준비 단계**
- [ ] 엔지니어 지식 정리
- [ ] 소리 분류 기준 정의
- [ ] 진단 규칙 작성
- [ ] 시나리오 정의

### **11.2 구현 단계**
- [ ] 도메인 지식 기반 규칙 생성
- [ ] 합성 데이터 생성
- [ ] 시뮬레이션 데이터 생성
- [ ] AI 모델 훈련

### **11.3 검증 단계**
- [ ] 규칙 검증
- [ ] 데이터 품질 검증
- [ ] AI 성능 평가
- [ ] 실제 데이터로 검증

---

## 🎯 **결론**

### **핵심 메시지**
1. **도메인 지식이 핵심**: 엔지니어의 경험과 지식이 가장 중요
2. **사전 학습 가능**: 실제 하드웨어 없이도 AI 학습 가능
3. **높은 성능**: 도메인 지식 기반으로 높은 정확도 달성
4. **비용 절약**: 실제 데이터 수집 없이도 학습 가능

### **다음 단계**
1. **엔지니어 지식 정리**: 소리 분류 기준과 진단 규칙 정리
2. **기본 규칙 생성**: 도메인 지식 기반 규칙 생성
3. **합성 데이터 생성**: 시뮬레이션 기반 데이터 생성
4. **AI 모델 훈련**: 생성된 데이터로 AI 모델 훈련
5. **실제 검증**: 하드웨어 설치 후 실제 데이터로 검증

**🎉 기계 엔지니어의 도메인 지식을 활용한 사전 학습으로 하드웨어 설치 전에도 AI를 준비할 수 있습니다!**
