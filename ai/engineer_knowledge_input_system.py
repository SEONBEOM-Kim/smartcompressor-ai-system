#!/usr/bin/env python3
"""
엔지니어 지식 입력 시스템
실제 엔지니어가 소리 구분 지식을 입력할 수 있는 인터페이스
"""

import json
import os
from datetime import datetime

class EngineerKnowledgeInputSystem:
    """엔지니어 지식 입력 시스템"""
    
    def __init__(self):
        self.knowledge_data = {}
        print("🎤 엔지니어 지식 입력 시스템")
        print("   실제 소리 구분 지식을 입력해주세요")
    
    def start_knowledge_input(self):
        """지식 입력 시작"""
        print("\n" + "=" * 60)
        print("🎤 엔지니어 소리 구분 지식 입력")
        print("=" * 60)
        print("목적: AI 학습을 위한 소리 구분 지식 수집")
        print("방법: 각 질문에 대해 경험을 바탕으로 답변해주세요")
        print("=" * 60)
        
        # 기본 정보 입력
        self._input_basic_info()
        
        # 소리 분류 지식 입력
        self._input_sound_classification()
        
        # 진단 방법 입력
        self._input_diagnostic_methods()
        
        # 경험 사례 입력
        self._input_experience_cases()
        
        # 휴리스틱 지식 입력
        self._input_heuristic_knowledge()
        
        # 결과 저장
        self._save_knowledge_data()
        
        print("\n🎉 지식 입력 완료! 감사합니다.")
    
    def _input_basic_info(self):
        """기본 정보 입력"""
        print("\n📋 기본 정보")
        print("-" * 30)
        
        self.knowledge_data['basic_info'] = {
            'name': input("이름: "),
            'experience_years': input("압축기 진단 경력 (년): "),
            'specialization': input("전문 분야: "),
            'company': input("회사명: "),
            'input_date': datetime.now().isoformat()
        }
        
        print(f"✅ 기본 정보 입력 완료")
    
    def _input_sound_classification(self):
        """소리 분류 지식 입력"""
        print("\n🎵 소리 분류 지식")
        print("-" * 40)
        print("경험을 바탕으로 각 소리 유형에 대해 설명해주세요")
        
        sound_types = [
            "정상 압축기 소리",
            "정상 팬 소리", 
            "정상 모터 소리",
            "베어링 마모 소리",
            "언밸런스 소리",
            "마찰 소리",
            "과부하 소리"
        ]
        
        self.knowledge_data['sound_classification'] = {}
        
        for i, sound_type in enumerate(sound_types, 1):
            print(f"\n🔊 {i}. {sound_type}")
            print("   경험을 바탕으로 이 소리에 대해 설명해주세요:")
            
            # 기본 설명
            description = input("   설명: ")
            
            # 주파수 특성
            print("   주파수 특성:")
            freq_low = input("     저주파 범위 (Hz, 예: 20-200): ")
            freq_high = input("     고주파 범위 (Hz, 예: 2000-8000): ")
            
            # 진폭 특성
            print("   진폭 특성:")
            amp_low = input("     약한 진폭 (예: 0.1-0.3): ")
            amp_high = input("     강한 진폭 (예: 0.6-1.0): ")
            
            # 패턴 특성
            print("   패턴 특성:")
            pattern = input("     패턴 (예: 일정한, 불규칙한, 주기적): ")
            stability = input("     안정성 (1-10, 10이 가장 안정): ")
            
            # 구별 특징
            distinguishing = input("   다른 소리와 구별되는 특징: ")
            
            # 신뢰도
            confidence = input("   이 지식에 대한 신뢰도 (0-1, 예: 0.9): ")
            
            # 저장
            self.knowledge_data['sound_classification'][sound_type] = {
                'description': description,
                'frequency_range': {
                    'low': freq_low,
                    'high': freq_high
                },
                'amplitude_range': {
                    'low': amp_low,
                    'high': amp_high
                },
                'pattern_characteristics': {
                    'pattern': pattern,
                    'stability': int(stability) if stability.isdigit() else 5
                },
                'distinguishing_features': distinguishing,
                'confidence': float(confidence) if confidence else 0.8
            }
    
    def _input_diagnostic_methods(self):
        """진단 방법 입력"""
        print("\n🔍 진단 방법")
        print("-" * 40)
        print("실제로 사용하는 진단 방법을 설명해주세요")
        
        diagnostic_areas = [
            "안정성 평가 방법",
            "주파수 분석 방법",
            "패턴 분석 방법",
            "소음 레벨 판단 방법"
        ]
        
        self.knowledge_data['diagnostic_methods'] = {}
        
        for i, area in enumerate(diagnostic_areas, 1):
            print(f"\n📊 {i}. {area}")
            
            method = input("   사용하는 방법: ")
            criteria = input("   판단 기준: ")
            threshold = input("   임계값 (예: 0.8): ")
            confidence = input("   이 방법의 신뢰도 (0-1): ")
            
            self.knowledge_data['diagnostic_methods'][area] = {
                'method': method,
                'criteria': criteria,
                'threshold': threshold,
                'confidence': float(confidence) if confidence else 0.8
            }
    
    def _input_experience_cases(self):
        """경험 사례 입력"""
        print("\n📚 경험 사례")
        print("-" * 40)
        print("기억에 남는 고장 사례를 3개 말씀해주세요")
        
        self.knowledge_data['experience_cases'] = []
        
        for i in range(3):
            print(f"\n📖 사례 {i+1}:")
            
            situation = input("   상황: ")
            symptoms = input("   증상 (쉼표로 구분): ")
            diagnosis = input("   진단: ")
            solution = input("   해결 방법: ")
            prevention = input("   예방 방법: ")
            confidence = input("   이 사례의 신뢰도 (0-1): ")
            
            case = {
                'situation': situation,
                'symptoms': [s.strip() for s in symptoms.split(',')],
                'diagnosis': diagnosis,
                'solution': solution,
                'prevention': prevention,
                'confidence': float(confidence) if confidence else 0.8
            }
            
            self.knowledge_data['experience_cases'].append(case)
    
    def _input_heuristic_knowledge(self):
        """휴리스틱 지식 입력"""
        print("\n💡 휴리스틱 지식")
        print("-" * 40)
        print("경험에 기반한 직감적 판단 기준을 말씀해주세요")
        
        print("\n1. 이상하다고 느끼는 순간:")
        abnormal_feeling = input("   언제 이상하다고 느끼나요? ")
        
        print("\n2. 빠른 판단 기준:")
        quick_judgment = input("   빠르게 판단하는 기준은? ")
        
        print("\n3. 소음 레벨 판단:")
        noise_level = input("   소음 레벨을 어떻게 판단하나요? ")
        
        print("\n4. 환경 요인:")
        environment = input("   온도, 습도, 부하에 따른 차이점은? ")
        
        print("\n5. 진동과 소음의 관계:")
        vibration_noise = input("   진동과 소음의 관계는? ")
        
        self.knowledge_data['heuristic_knowledge'] = {
            'abnormal_feeling': abnormal_feeling,
            'quick_judgment': quick_judgment,
            'noise_level': noise_level,
            'environment': environment,
            'vibration_noise': vibration_noise
        }
    
    def _save_knowledge_data(self):
        """지식 데이터 저장"""
        try:
            # 결과 디렉토리 생성
            os.makedirs('data/engineer_input', exist_ok=True)
            
            # 파일명 생성
            name = self.knowledge_data['basic_info']['name']
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/engineer_input/{name}_{date_str}.json"
            
            # 결과 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 지식 데이터 저장 완료: {filename}")
            
            # 요약 출력
            self._print_summary()
            
        except Exception as e:
            print(f"❌ 저장 오류: {e}")
    
    def _print_summary(self):
        """입력 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 입력된 지식 요약")
        print("=" * 60)
        
        info = self.knowledge_data['basic_info']
        print(f"엔지니어: {info['name']}")
        print(f"경력: {info['experience_years']}년")
        print(f"전문 분야: {info['specialization']}")
        print(f"회사: {info['company']}")
        
        print(f"\n수집된 지식:")
        print(f"- 소리 분류: {len(self.knowledge_data['sound_classification'])}개")
        print(f"- 진단 방법: {len(self.knowledge_data['diagnostic_methods'])}개")
        print(f"- 경험 사례: {len(self.knowledge_data['experience_cases'])}개")
        print(f"- 휴리스틱 지식: 5개 영역")
        
        print(f"\n다음 단계:")
        print("1. 입력된 지식을 명시적 규칙으로 변환")
        print("2. 합성 데이터 생성")
        print("3. AI 모델 훈련")

def main():
    """메인 함수"""
    print("🎤 엔지니어 지식 입력 시스템")
    print("=" * 60)
    
    # 지식 입력 시스템 생성
    input_system = EngineerKnowledgeInputSystem()
    
    # 지식 입력 시작
    input_system.start_knowledge_input()

if __name__ == "__main__":
    main()
