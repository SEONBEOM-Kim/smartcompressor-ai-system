#!/usr/bin/env python3
"""
빠른 엔지니어 지식 명시화 도구
기계 엔지니어의 지식을 빠르게 명시적 지식으로 변환
"""

import json
import os
from datetime import datetime

class QuickKnowledgeConverter:
    """빠른 지식 명시화 도구"""
    
    def __init__(self):
        self.explicit_knowledge = {}
        print("🚀 빠른 엔지니어 지식 명시화 도구")
        print("   기계 엔지니어의 지식을 빠르게 명시적 지식으로 변환")
    
    def convert_engineer_knowledge(self):
        """엔지니어 지식을 명시적 지식으로 변환"""
        print("\n" + "=" * 60)
        print("🧠 엔지니어 지식 → 명시적 지식 변환")
        print("=" * 60)
        
        # 1. 소리 분류 규칙 생성
        print("\n1️⃣ 소리 분류 규칙 생성")
        sound_rules = self._create_sound_classification_rules()
        
        # 2. 진단 규칙 생성
        print("2️⃣ 진단 규칙 생성")
        diagnostic_rules = self._create_diagnostic_rules()
        
        # 3. 경험 규칙 생성
        print("3️⃣ 경험 규칙 생성")
        experience_rules = self._create_experience_rules()
        
        # 4. 휴리스틱 규칙 생성
        print("4️⃣ 휴리스틱 규칙 생성")
        heuristic_rules = self._create_heuristic_rules()
        
        # 5. 문제 해결 규칙 생성
        print("5️⃣ 문제 해결 규칙 생성")
        troubleshooting_rules = self._create_troubleshooting_rules()
        
        # 6. 통합 지식 생성
        print("6️⃣ 통합 지식 생성")
        self.explicit_knowledge = {
            'sound_classification': sound_rules,
            'diagnostic_methods': diagnostic_rules,
            'experience_rules': experience_rules,
            'heuristic_knowledge': heuristic_rules,
            'troubleshooting_rules': troubleshooting_rules,
            'conversion_timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        print("✅ 엔지니어 지식 → 명시적 지식 변환 완료")
        return self.explicit_knowledge
    
    def _create_sound_classification_rules(self):
        """소리 분류 규칙 생성"""
        print("   🔊 소리 분류 규칙 생성 중...")
        
        sound_rules = {
            'normal_sounds': {
                'compressor_normal': {
                    'description': '정상 압축기 소리',
                    'frequency_range': (20, 200),
                    'amplitude_range': (0.1, 0.3),
                    'pattern_regularity': 0.8,
                    'stability_factor': 0.8,
                    'expert_notes': '일정한 저주파 소음, 안정적',
                    'confidence': 0.9
                },
                'fan_normal': {
                    'description': '정상 팬 소리',
                    'frequency_range': (200, 1000),
                    'amplitude_range': (0.2, 0.4),
                    'pattern_regularity': 0.9,
                    'stability_factor': 0.9,
                    'expert_notes': '부드러운 중주파 소음, 일정한 바람 소리',
                    'confidence': 0.9
                },
                'motor_normal': {
                    'description': '정상 모터 소리',
                    'frequency_range': (1000, 5000),
                    'amplitude_range': (0.15, 0.35),
                    'pattern_regularity': 0.85,
                    'stability_factor': 0.85,
                    'expert_notes': '규칙적인 고주파 소음, 안정적',
                    'confidence': 0.85
                }
            },
            'abnormal_sounds': {
                'bearing_wear': {
                    'description': '베어링 마모 소리',
                    'frequency_range': (2000, 8000),
                    'amplitude_range': (0.4, 1.0),
                    'pattern_regularity': 0.3,
                    'stability_factor': 0.3,
                    'expert_notes': '불규칙한 고주파 진동, 마찰음',
                    'confidence': 0.85
                },
                'unbalance': {
                    'description': '언밸런스 소리',
                    'frequency_range': (50, 500),
                    'amplitude_range': (0.3, 0.8),
                    'pattern_regularity': 0.6,
                    'stability_factor': 0.4,
                    'expert_notes': '주기적 진동, 저주파, 리듬 변화',
                    'confidence': 0.8
                },
                'friction': {
                    'description': '마찰 소리',
                    'frequency_range': (500, 3000),
                    'amplitude_range': (0.25, 0.7),
                    'pattern_regularity': 0.5,
                    'stability_factor': 0.5,
                    'expert_notes': '긁는 소리, 중주파, 불안정',
                    'confidence': 0.75
                },
                'overload': {
                    'description': '과부하 소리',
                    'frequency_range': (20, 8000),
                    'amplitude_range': (0.5, 1.0),
                    'pattern_regularity': 0.2,
                    'stability_factor': 0.2,
                    'expert_notes': '불규칙한 노이즈, 전체 주파수, 과부하',
                    'confidence': 0.9
                }
            }
        }
        
        print("   ✅ 소리 분류 규칙 생성 완료")
        return sound_rules
    
    def _create_diagnostic_rules(self):
        """진단 규칙 생성"""
        print("   🔍 진단 규칙 생성 중...")
        
        diagnostic_rules = {
            'stability_analysis': {
                'description': '안정성 분석',
                'method': 'RMS와 ZCR의 변동계수 계산',
                'formula': 'stability = 1 / (1 + std(rms_windows) / mean(rms_windows))',
                'thresholds': {
                    'excellent': 0.9,
                    'good': 0.8,
                    'fair': 0.6,
                    'poor': 0.4,
                    'critical': 0.2
                },
                'decision_logic': {
                    'excellent': '정상 운영',
                    'good': '정기 모니터링',
                    'fair': '모니터링 강화',
                    'poor': '점검 계획 수립',
                    'critical': '즉시 점검 필요'
                },
                'confidence': 0.9
            },
            'frequency_consistency': {
                'description': '주파수 일관성 분석',
                'method': '스펙트럼 센트로이드의 안정성 측정',
                'formula': 'consistency = 1 / (1 + std(spectral_centroids) / mean(spectral_centroids))',
                'thresholds': {
                    'excellent': 0.8,
                    'good': 0.7,
                    'fair': 0.5,
                    'poor': 0.3,
                    'critical': 0.1
                },
                'decision_logic': {
                    'excellent': '정상 운영',
                    'good': '정기 모니터링',
                    'fair': '주파수 변화 모니터링',
                    'poor': '주파수 분석 강화',
                    'critical': '주파수 이상 원인 분석'
                },
                'confidence': 0.8
            },
            'pattern_regularity': {
                'description': '패턴 규칙성 분석',
                'method': '자기상관 함수를 이용한 주기성 측정',
                'formula': 'regularity = max(autocorr[1:]) / autocorr[0]',
                'thresholds': {
                    'excellent': 0.8,
                    'good': 0.7,
                    'fair': 0.5,
                    'poor': 0.3,
                    'critical': 0.1
                },
                'decision_logic': {
                    'excellent': '정상 운영',
                    'good': '정기 모니터링',
                    'fair': '패턴 변화 모니터링',
                    'poor': '패턴 분석 강화',
                    'critical': '패턴 이상 원인 분석'
                },
                'confidence': 0.8
            }
        }
        
        print("   ✅ 진단 규칙 생성 완료")
        return diagnostic_rules
    
    def _create_experience_rules(self):
        """경험 규칙 생성"""
        print("   📚 경험 규칙 생성 중...")
        
        experience_rules = {
            'bearing_wear_progression': {
                'stage_1': {
                    'description': '초기 단계',
                    'symptoms': ['고주파 진동 미미', '주기적 패턴 유지'],
                    'frequency_range': (2000, 4000),
                    'amplitude_range': (0.4, 0.6),
                    'action': '모니터링 강화',
                    'confidence': 0.8
                },
                'stage_2': {
                    'description': '진행 단계',
                    'symptoms': ['고주파 진동 증가', '패턴 약간 불규칙'],
                    'frequency_range': (3000, 6000),
                    'amplitude_range': (0.6, 0.8),
                    'action': '점검 계획 수립',
                    'confidence': 0.85
                },
                'stage_3': {
                    'description': '심각 단계',
                    'symptoms': ['고주파 진동 심각', '패턴 불규칙'],
                    'frequency_range': (4000, 8000),
                    'amplitude_range': (0.8, 1.0),
                    'action': '즉시 교체 필요',
                    'confidence': 0.9
                }
            },
            'unbalance_development': {
                'stage_1': {
                    'description': '초기 단계',
                    'symptoms': ['저주파 진동 미미', '리듬 유지'],
                    'frequency_range': (50, 200),
                    'amplitude_range': (0.3, 0.5),
                    'action': '모니터링 강화',
                    'confidence': 0.8
                },
                'stage_2': {
                    'description': '진행 단계',
                    'symptoms': ['저주파 진동 증가', '리듬 약간 변화'],
                    'frequency_range': (100, 300),
                    'amplitude_range': (0.5, 0.7),
                    'action': '밸런싱 계획 수립',
                    'confidence': 0.85
                },
                'stage_3': {
                    'description': '심각 단계',
                    'symptoms': ['저주파 진동 심각', '리듬 불안정'],
                    'frequency_range': (150, 500),
                    'amplitude_range': (0.7, 1.0),
                    'action': '즉시 밸런싱 필요',
                    'confidence': 0.9
                }
            }
        }
        
        print("   ✅ 경험 규칙 생성 완료")
        return experience_rules
    
    def _create_heuristic_rules(self):
        """휴리스틱 규칙 생성"""
        print("   💡 휴리스틱 규칙 생성 중...")
        
        heuristic_rules = {
            'noise_level_judgment': {
                'description': '소음 레벨 판단',
                'rule': '소음이 갑자기 증가하면 이상 징후',
                'conditions': ['소음 레벨 변화', '시간적 변화', '환경 변화 없음'],
                'action': '즉시 점검 필요',
                'confidence': 0.8,
                'applicability': 'general'
            },
            'vibration_noise_correlation': {
                'description': '진동과 소음의 상관관계',
                'rule': '진동이 크면 소음도 큰 경우가 많음',
                'conditions': ['진동 증가', '소음 증가', '동시 발생'],
                'action': '진동 원인 분석',
                'confidence': 0.7,
                'applicability': 'general'
            },
            'environmental_factors': {
                'description': '환경 요인 고려',
                'rule': '온도가 높으면 진동 증가, 습도가 높으면 마찰 증가',
                'conditions': ['온도 변화', '습도 변화', '부하 변화'],
                'action': '환경 조건 고려한 진단',
                'confidence': 0.8,
                'applicability': 'environmental'
            },
            'quick_diagnosis': {
                'description': '빠른 진단 기준',
                'rule': 'RMS와 주파수 분포를 먼저 확인',
                'conditions': ['RMS > 0.5', '고주파 에너지 > 0.3'],
                'action': '상세 분석 필요',
                'confidence': 0.8,
                'applicability': 'quick'
            }
        }
        
        print("   ✅ 휴리스틱 규칙 생성 완료")
        return heuristic_rules
    
    def _create_troubleshooting_rules(self):
        """문제 해결 규칙 생성"""
        print("   🔧 문제 해결 규칙 생성 중...")
        
        troubleshooting_rules = {
            'problem_approach': {
                'description': '문제 접근 방법',
                'steps': [
                    '문제 상황 파악',
                    '증상 분석',
                    '원인 추정',
                    '해결책 수립',
                    '실행 및 검증'
                ],
                'confidence': 0.8
            },
            'investigation_order': {
                'description': '조사 순서',
                'steps': [
                    '소음 위치 확인',
                    '주파수 분석',
                    '진동 측정',
                    '부하 상태 확인',
                    '환경 조건 확인'
                ],
                'confidence': 0.8
            },
            'decision_points': {
                'description': '의사결정 포인트',
                'points': [
                    '정상 범위 내?',
                    '점진적 변화?',
                    '급격한 변화?',
                    '다른 증상 동반?',
                    '환경 요인 영향?'
                ],
                'confidence': 0.8
            },
            'emergency_response': {
                'description': '긴급 상황 대응',
                'criteria': ['소음 급격한 증가', '진동 심각', '과부하 신호'],
                'actions': [
                    '즉시 운전 중단',
                    '안전 조치',
                    '전문가 호출',
                    '상세 분석'
                ],
                'confidence': 0.9
            }
        }
        
        print("   ✅ 문제 해결 규칙 생성 완료")
        return troubleshooting_rules
    
    def save_explicit_knowledge(self, filepath: str = "data/explicit_knowledge.json"):
        """명시적 지식 저장"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.explicit_knowledge, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 명시적 지식 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 저장 오류: {e}")
            return False
    
    def print_knowledge_summary(self):
        """지식 요약 출력"""
        print("\n" + "=" * 60)
        print("🧠 명시적 지식 변환 결과")
        print("=" * 60)
        
        if self.explicit_knowledge:
            print(f"\n📊 변환된 지식 통계:")
            print(f"   - 소리 분류: {len(self.explicit_knowledge.get('sound_classification', {}).get('normal_sounds', {})) + len(self.explicit_knowledge.get('sound_classification', {}).get('abnormal_sounds', {}))}개")
            print(f"   - 진단 방법: {len(self.explicit_knowledge.get('diagnostic_methods', {}))}개")
            print(f"   - 경험 규칙: {len(self.explicit_knowledge.get('experience_rules', {}))}개")
            print(f"   - 휴리스틱 규칙: {len(self.explicit_knowledge.get('heuristic_knowledge', {}))}개")
            print(f"   - 문제 해결 규칙: {len(self.explicit_knowledge.get('troubleshooting_rules', {}))}개")
            
            print(f"\n🎯 주요 특징:")
            print(f"   - 모든 규칙이 수치화됨")
            print(f"   - 신뢰도 점수 포함")
            print(f"   - AI에서 직접 사용 가능")
            print(f"   - 검증 및 개선 가능")

def main():
    """메인 함수"""
    print("🚀 빠른 엔지니어 지식 명시화 도구")
    print("=" * 60)
    
    # 지식 변환기 생성
    converter = QuickKnowledgeConverter()
    
    # 지식 변환 실행
    explicit_knowledge = converter.convert_engineer_knowledge()
    
    # 결과 요약 출력
    converter.print_knowledge_summary()
    
    # 결과 저장
    converter.save_explicit_knowledge()
    
    print("\n🎉 엔지니어 지식 명시화 완료!")
    print("   이제 AI 학습에 사용할 수 있는 명시적 지식이 준비되었습니다.")

if __name__ == "__main__":
    main()
