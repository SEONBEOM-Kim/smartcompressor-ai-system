#!/usr/bin/env python3
"""
기계 엔지니어 도메인 지식 데이터베이스
실제 하드웨어 설치 전 AI 학습을 위한 엔지니어 지식 체계화
"""

import numpy as np
import json
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class EngineerKnowledgeDatabase:
    """기계 엔지니어 도메인 지식 데이터베이스"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.sound_classification_rules = {}
        self.diagnostic_criteria = {}
        self.severity_assessment = {}
        
        print("🔧 기계 엔지니어 도메인 지식 데이터베이스 초기화")
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """지식 베이스 초기화"""
        try:
            print("📚 엔지니어 지식 베이스 구축 시작")
            
            # 1. 소리 분류 기준 정의
            self._define_sound_classification()
            
            # 2. 진단 규칙 정의
            self._define_diagnostic_rules()
            
            # 3. 심각도 평가 기준 정의
            self._define_severity_criteria()
            
            # 4. 엔지니어 경험 지식 정리
            self._organize_expert_experience()
            
            print("✅ 엔지니어 지식 베이스 구축 완료")
            
        except Exception as e:
            print(f"❌ 지식 베이스 초기화 오류: {e}")
    
    def _define_sound_classification(self):
        """소리 분류 기준 정의"""
        self.sound_classification_rules = {
            'normal_sounds': {
                'compressor_normal': {
                    'description': '정상 압축기 소리',
                    'frequency_characteristics': {
                        'primary_range': (20, 200),
                        'harmonic_ratios': [1.0, 0.3, 0.1, 0.05],
                        'stability_factor': 0.8,
                        'consistency_threshold': 0.7
                    },
                    'amplitude_characteristics': {
                        'rms_range': (0.1, 0.3),
                        'peak_range': (0.5, 1.0),
                        'crest_factor_range': (2.0, 5.0)
                    },
                    'temporal_characteristics': {
                        'pattern_regularity': 0.8,
                        'rhythm_consistency': 0.9,
                        'noise_level': 0.1
                    },
                    'expert_notes': {
                        'visual_description': '일정한 리듬의 저주파 소음',
                        'auditory_description': '부드럽고 안정적인 소음',
                        'mechanical_meaning': '정상적인 압축기 작동 상태',
                        'maintenance_implication': '정상 운영, 정기 점검 유지'
                    }
                },
                'fan_normal': {
                    'description': '정상 팬 소리',
                    'frequency_characteristics': {
                        'primary_range': (200, 1000),
                        'harmonic_ratios': [1.0, 0.4, 0.2, 0.1],
                        'stability_factor': 0.9,
                        'consistency_threshold': 0.8
                    },
                    'amplitude_characteristics': {
                        'rms_range': (0.2, 0.4),
                        'peak_range': (0.6, 1.2),
                        'crest_factor_range': (2.5, 4.0)
                    },
                    'temporal_characteristics': {
                        'pattern_regularity': 0.9,
                        'rhythm_consistency': 0.95,
                        'noise_level': 0.15
                    },
                    'expert_notes': {
                        'visual_description': '부드러운 중주파 소음',
                        'auditory_description': '일정한 바람 소리',
                        'mechanical_meaning': '정상적인 팬 회전',
                        'maintenance_implication': '정상 운영, 청소 주기 확인'
                    }
                },
                'motor_normal': {
                    'description': '정상 모터 소리',
                    'frequency_characteristics': {
                        'primary_range': (1000, 5000),
                        'harmonic_ratios': [1.0, 0.3, 0.15, 0.08],
                        'stability_factor': 0.85,
                        'consistency_threshold': 0.75
                    },
                    'amplitude_characteristics': {
                        'rms_range': (0.15, 0.35),
                        'peak_range': (0.4, 0.8),
                        'crest_factor_range': (2.0, 4.5)
                    },
                    'temporal_characteristics': {
                        'pattern_regularity': 0.85,
                        'rhythm_consistency': 0.9,
                        'noise_level': 0.12
                    },
                    'expert_notes': {
                        'visual_description': '규칙적인 고주파 소음',
                        'auditory_description': '일정한 모터 소음',
                        'mechanical_meaning': '정상적인 모터 회전',
                        'maintenance_implication': '정상 운영, 베어링 점검 주기 확인'
                    }
                }
            },
            'abnormal_sounds': {
                'bearing_wear': {
                    'description': '베어링 마모 소리',
                    'frequency_characteristics': {
                        'primary_range': (2000, 8000),
                        'harmonic_ratios': [1.0, 0.6, 0.4, 0.3],
                        'stability_factor': 0.3,
                        'consistency_threshold': 0.4
                    },
                    'amplitude_characteristics': {
                        'rms_range': (0.4, 1.0),
                        'peak_range': (0.8, 2.0),
                        'crest_factor_range': (1.5, 3.0)
                    },
                    'temporal_characteristics': {
                        'pattern_regularity': 0.3,
                        'rhythm_consistency': 0.4,
                        'noise_level': 0.6
                    },
                    'expert_notes': {
                        'visual_description': '불규칙한 고주파 진동',
                        'auditory_description': '마찰음과 진동음',
                        'mechanical_meaning': '베어링 마모로 인한 마찰',
                        'maintenance_implication': '즉시 베어링 교체 필요',
                        'severity_indicators': ['고주파 진동 증가', '불규칙한 패턴', '마찰음']
                    }
                },
                'unbalance': {
                    'description': '언밸런스 소리',
                    'frequency_characteristics': {
                        'primary_range': (50, 500),
                        'harmonic_ratios': [1.0, 0.8, 0.6, 0.4],
                        'stability_factor': 0.4,
                        'consistency_threshold': 0.5
                    },
                    'amplitude_characteristics': {
                        'rms_range': (0.3, 0.8),
                        'peak_range': (0.6, 1.5),
                        'crest_factor_range': (1.8, 3.5)
                    },
                    'temporal_characteristics': {
                        'pattern_regularity': 0.6,
                        'rhythm_consistency': 0.5,
                        'noise_level': 0.4
                    },
                    'expert_notes': {
                        'visual_description': '주기적인 저주파 진동',
                        'auditory_description': '리듬이 변하는 소음',
                        'mechanical_meaning': '회전체의 불균형',
                        'maintenance_implication': '밸런싱 작업 필요',
                        'severity_indicators': ['주기적 진동', '저주파 증가', '리듬 불안정']
                    }
                },
                'friction': {
                    'description': '마찰 소리',
                    'frequency_characteristics': {
                        'primary_range': (500, 3000),
                        'harmonic_ratios': [1.0, 0.7, 0.5, 0.3],
                        'stability_factor': 0.5,
                        'consistency_threshold': 0.6
                    },
                    'amplitude_characteristics': {
                        'rms_range': (0.25, 0.7),
                        'peak_range': (0.5, 1.2),
                        'crest_factor_range': (1.5, 4.0)
                    },
                    'temporal_characteristics': {
                        'pattern_regularity': 0.5,
                        'rhythm_consistency': 0.6,
                        'noise_level': 0.5
                    },
                    'expert_notes': {
                        'visual_description': '긁는 소리와 중주파 노이즈',
                        'auditory_description': '마찰음과 스크래치 소리',
                        'mechanical_meaning': '부품 간 마찰 발생',
                        'maintenance_implication': '마찰 부위 점검 및 윤활 필요',
                        'severity_indicators': ['긁는 소리', '중주파 노이즈', '불안정한 진동']
                    }
                },
                'overload': {
                    'description': '과부하 소리',
                    'frequency_characteristics': {
                        'primary_range': (20, 8000),
                        'harmonic_ratios': [1.0, 0.9, 0.8, 0.7],
                        'stability_factor': 0.2,
                        'consistency_threshold': 0.3
                    },
                    'amplitude_characteristics': {
                        'rms_range': (0.5, 1.0),
                        'peak_range': (1.0, 2.5),
                        'crest_factor_range': (1.2, 2.5)
                    },
                    'temporal_characteristics': {
                        'pattern_regularity': 0.2,
                        'rhythm_consistency': 0.3,
                        'noise_level': 0.8
                    },
                    'expert_notes': {
                        'visual_description': '전체 주파수 범위의 불규칙한 노이즈',
                        'auditory_description': '과부하로 인한 소음',
                        'mechanical_meaning': '시스템 과부하 상태',
                        'maintenance_implication': '즉시 부하 감소 및 점검 필요',
                        'severity_indicators': ['전체 주파수 노이즈', '불규칙한 진동', '과부하 신호']
                    }
                }
            }
        }
    
    def _define_diagnostic_rules(self):
        """진단 규칙 정의"""
        self.diagnostic_criteria = {
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
                'expert_rule': '변동계수가 0.2 미만이면 정상, 이상이면 이상',
                'maintenance_action': {
                    'excellent': '정상 운영',
                    'good': '정기 모니터링',
                    'fair': '모니터링 강화',
                    'poor': '점검 계획 수립',
                    'critical': '즉시 점검 필요'
                }
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
                'expert_rule': '주파수 분포가 일정하면 정상, 변화가 크면 이상',
                'maintenance_action': {
                    'excellent': '정상 운영',
                    'good': '정기 모니터링',
                    'fair': '주파수 변화 모니터링',
                    'poor': '주파수 분석 강화',
                    'critical': '주파수 이상 원인 분석'
                }
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
                'expert_rule': '주기성이 높으면 정상, 낮으면 이상',
                'maintenance_action': {
                    'excellent': '정상 운영',
                    'good': '정기 모니터링',
                    'fair': '패턴 변화 모니터링',
                    'poor': '패턴 분석 강화',
                    'critical': '패턴 이상 원인 분석'
                }
            },
            'harmonic_analysis': {
                'description': '하모닉스 분석',
                'method': '기본 주파수의 하모닉스 존재 여부 확인',
                'formula': 'harmonic_ratio = (H2 + H3) / (2 * H1)',
                'thresholds': {
                    'excellent': 0.7,
                    'good': 0.5,
                    'fair': 0.3,
                    'poor': 0.1,
                    'critical': 0.0
                },
                'expert_rule': '하모닉스가 정상적이면 정상, 비정상적이면 이상',
                'maintenance_action': {
                    'excellent': '정상 운영',
                    'good': '정기 모니터링',
                    'fair': '하모닉스 모니터링',
                    'poor': '하모닉스 분석 강화',
                    'critical': '하모닉스 이상 원인 분석'
                }
            },
            'noise_level_analysis': {
                'description': '노이즈 레벨 분석',
                'method': '백그라운드 노이즈 레벨 측정',
                'formula': 'noise_level = std(high_freq_component) / 0.5',
                'thresholds': {
                    'excellent': 0.1,
                    'good': 0.2,
                    'fair': 0.4,
                    'poor': 0.6,
                    'critical': 0.8
                },
                'expert_rule': '노이즈 레벨이 낮으면 정상, 높으면 이상',
                'maintenance_action': {
                    'excellent': '정상 운영',
                    'good': '정기 모니터링',
                    'fair': '노이즈 모니터링',
                    'poor': '노이즈 분석 강화',
                    'critical': '노이즈 원인 분석 및 제거'
                }
            }
        }
    
    def _define_severity_criteria(self):
        """심각도 평가 기준 정의"""
        self.severity_assessment = {
            'mild': {
                'description': '경미한 이상',
                'score_range': (1, 3),
                'indicators': [
                    '약간의 불규칙성 감지',
                    '주파수 변화 미미',
                    '안정성 유지',
                    '노이즈 레벨 약간 증가'
                ],
                'expert_observation': '정상 범위 내에서 약간의 변화 감지',
                'maintenance_action': '모니터링 강화, 정기 점검 유지',
                'urgency': 'low',
                'response_time': '1-2주 내'
            },
            'moderate': {
                'description': '중간 정도 이상',
                'score_range': (4, 6),
                'indicators': [
                    '명확한 불규칙성 감지',
                    '주파수 변화 감지',
                    '안정성 저하',
                    '노이즈 레벨 증가',
                    '패턴 변화 감지'
                ],
                'expert_observation': '정상 범위를 벗어난 변화 감지',
                'maintenance_action': '점검 계획 수립, 모니터링 강화',
                'urgency': 'medium',
                'response_time': '3-5일 내'
            },
            'severe': {
                'description': '심각한 이상',
                'score_range': (7, 10),
                'indicators': [
                    '심각한 불규칙성 감지',
                    '주파수 변화 심각',
                    '안정성 상실',
                    '노이즈 레벨 높음',
                    '패턴 완전 파괴',
                    '마찰음 감지',
                    '진동 증가'
                ],
                'expert_observation': '심각한 이상 상태, 즉시 조치 필요',
                'maintenance_action': '즉시 점검 필요, 운전 중단 고려',
                'urgency': 'high',
                'response_time': '24시간 내'
            }
        }
    
    def _organize_expert_experience(self):
        """엔지니어 경험 지식 정리"""
        self.knowledge_base = {
            'expert_experience': {
                'common_failure_patterns': {
                    'bearing_wear_progression': {
                        'stage_1': '고주파 진동 미미, 주기적 패턴 유지',
                        'stage_2': '고주파 진동 증가, 패턴 약간 불규칙',
                        'stage_3': '고주파 진동 심각, 패턴 불규칙',
                        'stage_4': '마찰음 감지, 패턴 완전 파괴'
                    },
                    'unbalance_development': {
                        'stage_1': '저주파 진동 미미, 리듬 유지',
                        'stage_2': '저주파 진동 증가, 리듬 약간 변화',
                        'stage_3': '저주파 진동 심각, 리듬 불안정',
                        'stage_4': '진동 심각, 리듬 완전 파괴'
                    }
                },
                'environmental_factors': {
                    'temperature_impact': {
                        'low_temp': '진동 감소, 안정성 증가',
                        'normal_temp': '정상 범위',
                        'high_temp': '진동 증가, 안정성 감소'
                    },
                    'humidity_impact': {
                        'low_humidity': '마찰 감소, 소음 감소',
                        'normal_humidity': '정상 범위',
                        'high_humidity': '마찰 증가, 소음 증가'
                    },
                    'load_impact': {
                        'low_load': '진동 감소, 안정성 증가',
                        'normal_load': '정상 범위',
                        'high_load': '진동 증가, 안정성 감소'
                    }
                },
                'maintenance_guidelines': {
                    'preventive_maintenance': {
                        'daily': '기본 소음 및 진동 확인',
                        'weekly': '주파수 분석 및 패턴 확인',
                        'monthly': '상세 분석 및 트렌드 확인',
                        'quarterly': '종합 분석 및 예방 정비'
                    },
                    'corrective_maintenance': {
                        'mild_anomaly': '모니터링 강화, 정기 점검',
                        'moderate_anomaly': '점검 계획 수립, 예방 정비',
                        'severe_anomaly': '즉시 점검, 부품 교체'
                    }
                }
            }
        }
    
    def get_sound_classification_rules(self) -> Dict:
        """소리 분류 규칙 반환"""
        return self.sound_classification_rules
    
    def get_diagnostic_criteria(self) -> Dict:
        """진단 기준 반환"""
        return self.diagnostic_criteria
    
    def get_severity_assessment(self) -> Dict:
        """심각도 평가 기준 반환"""
        return self.severity_assessment
    
    def get_expert_experience(self) -> Dict:
        """엔지니어 경험 지식 반환"""
        return self.knowledge_base['expert_experience']
    
    def save_knowledge_base(self, filepath: str = "data/engineer_knowledge_base.json"):
        """지식 베이스 저장"""
        try:
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            knowledge_data = {
                'sound_classification_rules': self.sound_classification_rules,
                'diagnostic_criteria': self.diagnostic_criteria,
                'severity_assessment': self.severity_assessment,
                'expert_experience': self.knowledge_base['expert_experience'],
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 지식 베이스 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 지식 베이스 저장 오류: {e}")
            return False
    
    def load_knowledge_base(self, filepath: str = "data/engineer_knowledge_base.json") -> bool:
        """지식 베이스 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                knowledge_data = json.load(f)
            
            self.sound_classification_rules = knowledge_data.get('sound_classification_rules', {})
            self.diagnostic_criteria = knowledge_data.get('diagnostic_criteria', {})
            self.severity_assessment = knowledge_data.get('severity_assessment', {})
            self.knowledge_base['expert_experience'] = knowledge_data.get('expert_experience', {})
            
            print(f"✅ 지식 베이스 로드 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 지식 베이스 로드 오류: {e}")
            return False
    
    def print_knowledge_summary(self):
        """지식 베이스 요약 출력"""
        print("\n" + "=" * 60)
        print("📚 기계 엔지니어 도메인 지식 데이터베이스 요약")
        print("=" * 60)
        
        # 소리 분류 규칙 요약
        print(f"\n🔊 소리 분류 규칙:")
        print(f"   정상 소리: {len(self.sound_classification_rules.get('normal_sounds', {}))}개")
        print(f"   이상 소리: {len(self.sound_classification_rules.get('abnormal_sounds', {}))}개")
        
        # 진단 기준 요약
        print(f"\n🔍 진단 기준:")
        print(f"   분석 방법: {len(self.diagnostic_criteria)}개")
        for method, criteria in self.diagnostic_criteria.items():
            print(f"   - {criteria['description']}: {len(criteria['thresholds'])}개 레벨")
        
        # 심각도 평가 요약
        print(f"\n⚠️ 심각도 평가:")
        print(f"   심각도 레벨: {len(self.severity_assessment)}개")
        for level, assessment in self.severity_assessment.items():
            print(f"   - {level}: {assessment['description']}")
        
        # 엔지니어 경험 요약
        print(f"\n👨‍🔧 엔지니어 경험:")
        expert_exp = self.knowledge_base.get('expert_experience', {})
        print(f"   실패 패턴: {len(expert_exp.get('common_failure_patterns', {}))}개")
        print(f"   환경 요인: {len(expert_exp.get('environmental_factors', {}))}개")
        print(f"   유지보수 가이드: {len(expert_exp.get('maintenance_guidelines', {}))}개")

# 사용 예제
if __name__ == "__main__":
    # 기계 엔지니어 도메인 지식 데이터베이스 테스트
    knowledge_db = EngineerKnowledgeDatabase()
    
    print("🔧 기계 엔지니어 도메인 지식 데이터베이스 테스트")
    print("=" * 60)
    
    # 지식 베이스 요약 출력
    knowledge_db.print_knowledge_summary()
    
    # 지식 베이스 저장
    knowledge_db.save_knowledge_base()
    
    print("\n🎉 1단계: 엔지니어 지식 정리 완료!")
    print("   소리 분류 기준과 진단 규칙이 체계적으로 정리되었습니다.")
