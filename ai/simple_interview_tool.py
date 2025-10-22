#!/usr/bin/env python3
"""
간단한 엔지니어 인터뷰 도구
기계 설치 전 AI 학습을 위한 엔지니어 지식 수집 도구
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class SimpleInterviewTool:
    """간단한 엔지니어 인터뷰 도구"""
    
    def __init__(self):
        self.interview_data = {}
        self.current_section = 0
        self.current_question = 0
        self.answers = {}
        
        print("🎤 간단한 엔지니어 인터뷰 도구")
        print("   기계 설치 전 AI 학습을 위한 지식 수집")
    
    def start_interview(self):
        """인터뷰 시작"""
        print("\n" + "=" * 60)
        print("🎤 기계 엔지니어 지식 수집 인터뷰 시작")
        print("=" * 60)
        print("목적: 기계 설치 전 AI 학습을 위한 지식 수집")
        print("시간: 약 30-60분")
        print("방법: 질문에 대해 구체적으로 답변해주세요")
        print("=" * 60)
        
        # 인터뷰 정보 입력
        self._collect_interview_info()
        
        # 섹션별 인터뷰 진행
        self._run_interview_sections()
        
        # 결과 저장
        self._save_interview_results()
        
        print("\n🎉 인터뷰 완료! 감사합니다.")
    
    def _collect_interview_info(self):
        """인터뷰 정보 수집"""
        print("\n📋 인터뷰 정보")
        print("-" * 30)
        
        self.interview_data['interview_info'] = {
            'date': datetime.now().isoformat(),
            'engineer_name': input("엔지니어 이름: "),
            'experience_years': input("경력 (년): "),
            'specialization': input("전문 분야: "),
            'company': input("회사명: "),
            'interviewer': input("인터뷰어: ")
        }
        
        print(f"✅ 인터뷰 정보 수집 완료")
    
    def _run_interview_sections(self):
        """섹션별 인터뷰 진행"""
        sections = [
            self._section1_sound_classification,
            self._section2_diagnostic_methods,
            self._section3_experience_cases,
            self._section4_heuristic_knowledge,
            self._section5_troubleshooting
        ]
        
        for i, section_func in enumerate(sections, 1):
            print(f"\n📝 섹션 {i} 시작")
            section_func()
            print(f"✅ 섹션 {i} 완료")
    
    def _section1_sound_classification(self):
        """섹션 1: 소리 분류"""
        print("\n🎵 섹션 1: 소리 분류 기준")
        print("-" * 40)
        
        sound_types = [
            "정상 압축기 소리",
            "정상 팬 소리", 
            "정상 모터 소리",
            "베어링 마모 소리",
            "언밸런스 소리",
            "마찰 소리",
            "과부하 소리"
        ]
        
        self.interview_data['sound_classification'] = {}
        
        for sound_type in sound_types:
            print(f"\n🔊 {sound_type}에 대해 설명해주세요:")
            
            description = input("  설명: ")
            frequency = input("  주파수 범위 (예: 저주파, 중주파, 고주파): ")
            amplitude = input("  진폭 (예: 약한, 중간, 강한): ")
            pattern = input("  패턴 (예: 일정한, 불규칙한, 주기적): ")
            confidence = input("  신뢰도 (0-1, 예: 0.9): ")
            
            self.interview_data['sound_classification'][sound_type] = {
                'description': description,
                'frequency': frequency,
                'amplitude': amplitude,
                'pattern': pattern,
                'confidence': float(confidence) if confidence else 0.8
            }
    
    def _section2_diagnostic_methods(self):
        """섹션 2: 진단 방법"""
        print("\n🔍 섹션 2: 진단 방법 및 기준")
        print("-" * 40)
        
        diagnostic_areas = [
            "안정성 평가",
            "주파수 일관성 평가", 
            "패턴 규칙성 평가",
            "소음 레벨 평가",
            "진동 분석"
        ]
        
        self.interview_data['diagnostic_methods'] = {}
        
        for area in diagnostic_areas:
            print(f"\n📊 {area}에 대해 설명해주세요:")
            
            method = input("  방법: ")
            criteria = input("  기준: ")
            threshold = input("  임계값: ")
            confidence = input("  신뢰도 (0-1): ")
            
            self.interview_data['diagnostic_methods'][area] = {
                'method': method,
                'criteria': criteria,
                'threshold': threshold,
                'confidence': float(confidence) if confidence else 0.8
            }
    
    def _section3_experience_cases(self):
        """섹션 3: 경험 사례"""
        print("\n📚 섹션 3: 경험 사례")
        print("-" * 40)
        
        print("기억에 남는 고장 사례를 3개 말씀해주세요:")
        
        self.interview_data['experience_cases'] = []
        
        for i in range(3):
            print(f"\n📖 사례 {i+1}:")
            
            situation = input("  상황: ")
            symptoms = input("  증상 (쉼표로 구분): ").split(',')
            diagnosis = input("  진단: ")
            solution = input("  해결 방법: ")
            prevention = input("  예방 방법: ")
            confidence = input("  신뢰도 (0-1): ")
            
            case = {
                'situation': situation,
                'symptoms': [s.strip() for s in symptoms],
                'diagnosis': diagnosis,
                'solution': solution,
                'prevention': prevention,
                'confidence': float(confidence) if confidence else 0.8
            }
            
            self.interview_data['experience_cases'].append(case)
    
    def _section4_heuristic_knowledge(self):
        """섹션 4: 휴리스틱 지식"""
        print("\n💡 섹션 4: 휴리스틱 지식 및 직감")
        print("-" * 40)
        
        print("경험에 기반한 직감적 판단 기준을 말씀해주세요:")
        
        self.interview_data['heuristic_knowledge'] = []
        
        print("\n1. 이상하다고 느끼는 순간:")
        abnormal_feeling = input("  언제 이상하다고 느끼나요? ")
        
        print("\n2. 빠른 판단 기준:")
        quick_judgment = input("  빠르게 판단하는 기준은 무엇인가요? ")
        
        print("\n3. 소음 레벨 판단:")
        noise_level = input("  소음 레벨을 어떻게 판단하나요? ")
        
        print("\n4. 환경 요인:")
        environment = input("  온도, 습도, 부하에 따른 차이점은? ")
        
        self.interview_data['heuristic_knowledge'] = {
            'abnormal_feeling': abnormal_feeling,
            'quick_judgment': quick_judgment,
            'noise_level': noise_level,
            'environment': environment
        }
    
    def _section5_troubleshooting(self):
        """섹션 5: 문제 해결 과정"""
        print("\n🔧 섹션 5: 문제 해결 과정")
        print("-" * 40)
        
        print("문제 해결 과정을 단계별로 설명해주세요:")
        
        self.interview_data['troubleshooting'] = {}
        
        print("\n1. 문제 접근 방법:")
        approach = input("  문제를 어떻게 접근하나요? ")
        
        print("\n2. 조사 순서:")
        investigation = input("  어떤 순서로 조사하나요? ")
        
        print("\n3. 의사결정 포인트:")
        decision_points = input("  의사결정 포인트는 어디인가요? ")
        
        print("\n4. 불확실성 처리:")
        uncertainty = input("  불확실한 경우 어떻게 하나요? ")
        
        print("\n5. 긴급 상황 대응:")
        emergency = input("  긴급 상황에서는 어떻게 하나요? ")
        
        self.interview_data['troubleshooting'] = {
            'approach': approach,
            'investigation': investigation,
            'decision_points': decision_points,
            'uncertainty': uncertainty,
            'emergency': emergency
        }
    
    def _save_interview_results(self):
        """인터뷰 결과 저장"""
        try:
            # 결과 디렉토리 생성
            os.makedirs('data/interviews', exist_ok=True)
            
            # 파일명 생성
            engineer_name = self.interview_data['interview_info']['engineer_name']
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/interviews/{engineer_name}_{date_str}.json"
            
            # 결과 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.interview_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 인터뷰 결과 저장 완료: {filename}")
            
            # 요약 출력
            self._print_summary()
            
        except Exception as e:
            print(f"❌ 저장 오류: {e}")
    
    def _print_summary(self):
        """인터뷰 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 인터뷰 결과 요약")
        print("=" * 60)
        
        info = self.interview_data['interview_info']
        print(f"엔지니어: {info['engineer_name']}")
        print(f"경력: {info['experience_years']}년")
        print(f"전문 분야: {info['specialization']}")
        print(f"회사: {info['company']}")
        
        print(f"\n수집된 지식:")
        print(f"- 소리 분류: {len(self.interview_data['sound_classification'])}개")
        print(f"- 진단 방법: {len(self.interview_data['diagnostic_methods'])}개")
        print(f"- 경험 사례: {len(self.interview_data['experience_cases'])}개")
        print(f"- 휴리스틱 지식: 4개 영역")
        print(f"- 문제 해결 과정: 5개 영역")
        
        print(f"\n다음 단계:")
        print("1. 지식 명시화 시스템으로 변환")
        print("2. 합성 데이터 생성")
        print("3. AI 모델 훈련")
        print("4. 성능 검증")

def main():
    """메인 함수"""
    print("🎤 기계 엔지니어 지식 수집 인터뷰 도구")
    print("=" * 60)
    
    # 인터뷰 도구 생성
    tool = SimpleInterviewTool()
    
    # 인터뷰 시작
    tool.start_interview()

if __name__ == "__main__":
    main()
