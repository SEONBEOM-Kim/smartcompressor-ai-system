#!/usr/bin/env python3
"""
도메인 지식 기반 규칙 생성기
1단계에서 정리한 엔지니어 지식을 바탕으로 실제 AI에서 사용할 수 있는 규칙 생성
"""

import numpy as np
import librosa
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

class DomainBasedRulesGenerator:
    """도메인 지식 기반 규칙 생성기"""
    
    def __init__(self):
        self.generated_rules = {}
        self.rule_engine = {}
        self.thresholds = {}
        self.expert_heuristics = {}
        
        print("🔧 도메인 지식 기반 규칙 생성기 초기화")
        self._load_engineer_knowledge()
        self._generate_domain_rules()
    
    def _load_engineer_knowledge(self):
        """1단계에서 정리한 엔지니어 지식 로드"""
        try:
            print("📚 엔지니어 지식 로드 중...")
            
            # 1단계에서 정리한 지식 베이스 (실제로는 파일에서 로드)
            self.engineer_knowledge = {
                'sound_classification': {
                    'normal_compressor': {
                        'frequency_range': (20, 200),
                        'rms_range': (0.1, 0.3),
                        'stability_factor': 0.8,
                        'pattern_regularity': 0.8
                    },
                    'bearing_wear': {
                        'frequency_range': (2000, 8000),
                        'rms_range': (0.4, 1.0),
                        'stability_factor': 0.3,
                        'pattern_regularity': 0.3
                    }
                },
                'diagnostic_criteria': {
                    'stability_analysis': {
                        'thresholds': {'excellent': 0.9, 'good': 0.8, 'fair': 0.6, 'poor': 0.4, 'critical': 0.2}
                    },
                    'frequency_consistency': {
                        'thresholds': {'excellent': 0.8, 'good': 0.7, 'fair': 0.5, 'poor': 0.3, 'critical': 0.1}
                    }
                }
            }
            
            print("✅ 엔지니어 지식 로드 완료")
            
        except Exception as e:
            print(f"❌ 엔지니어 지식 로드 오류: {e}")
            self.engineer_knowledge = {}
    
    def _generate_domain_rules(self):
        """도메인 지식 기반 규칙 생성"""
        try:
            print("🔧 도메인 지식 기반 규칙 생성 시작")
            
            # 1. 기본 진단 규칙 생성
            self._generate_basic_diagnostic_rules()
            
            # 2. 고급 분석 규칙 생성
            self._generate_advanced_analysis_rules()
            
            # 3. 이상 유형 식별 규칙 생성
            self._generate_anomaly_identification_rules()
            
            # 4. 심각도 평가 규칙 생성
            self._generate_severity_assessment_rules()
            
            # 5. 엔지니어 휴리스틱 규칙 생성
            self._generate_expert_heuristic_rules()
            
            print("✅ 도메인 지식 기반 규칙 생성 완료")
            
        except Exception as e:
            print(f"❌ 도메인 규칙 생성 오류: {e}")
    
    def _generate_basic_diagnostic_rules(self):
        """기본 진단 규칙 생성"""
        try:
            print("1️⃣ 기본 진단 규칙 생성")
            
            self.generated_rules['basic_diagnostic'] = {
                'normal_sound_detection': {
                    'description': '정상 소리 감지 규칙',
                    'conditions': {
                        'rms_range': (0.1, 0.4),
                        'zcr_range': (0.05, 0.25),
                        'stability_factor': 0.7,
                        'pattern_regularity': 0.6,
                        'frequency_consistency': 0.6
                    },
                    'logic': 'AND(AND(rms >= 0.1, rms <= 0.4), AND(zcr >= 0.05, zcr <= 0.25), stability_factor >= 0.7, pattern_regularity >= 0.6, frequency_consistency >= 0.6)',
                    'confidence_weight': 0.8,
                    'expert_notes': '모든 조건이 정상 범위 내에 있으면 정상 소리로 판단'
                },
                'abnormal_sound_detection': {
                    'description': '이상 소리 감지 규칙',
                    'conditions': {
                        'rms_range': (0.4, 1.0),
                        'zcr_range': (0.3, 0.9),
                        'stability_factor': 0.5,
                        'pattern_regularity': 0.4,
                        'frequency_consistency': 0.4
                    },
                    'logic': 'OR(OR(rms > 0.4, zcr > 0.3), OR(stability_factor < 0.5, pattern_regularity < 0.4, frequency_consistency < 0.4))',
                    'confidence_weight': 0.9,
                    'expert_notes': '하나라도 이상 범위에 있으면 이상 소리로 판단'
                }
            }
            
            print("✅ 기본 진단 규칙 생성 완료")
            
        except Exception as e:
            print(f"⚠️ 기본 진단 규칙 생성 오류: {e}")
    
    def _generate_advanced_analysis_rules(self):
        """고급 분석 규칙 생성"""
        try:
            print("2️⃣ 고급 분석 규칙 생성")
            
            self.generated_rules['advanced_analysis'] = {
                'stability_analysis': {
                    'description': '안정성 분석 규칙',
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
                    }
                },
                'frequency_consistency_analysis': {
                    'description': '주파수 일관성 분석 규칙',
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
                    }
                },
                'pattern_regularity_analysis': {
                    'description': '패턴 규칙성 분석 규칙',
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
                    }
                }
            }
            
            print("✅ 고급 분석 규칙 생성 완료")
            
        except Exception as e:
            print(f"⚠️ 고급 분석 규칙 생성 오류: {e}")
    
    def _generate_anomaly_identification_rules(self):
        """이상 유형 식별 규칙 생성"""
        try:
            print("3️⃣ 이상 유형 식별 규칙 생성")
            
            self.generated_rules['anomaly_identification'] = {
                'bearing_wear_detection': {
                    'description': '베어링 마모 감지 규칙',
                    'conditions': {
                        'spectral_centroid_range': (2000, 8000),
                        'rms_threshold': 0.4,
                        'pattern_regularity_threshold': 0.5,
                        'stability_factor_threshold': 0.5
                    },
                    'logic': 'AND(AND(spectral_centroid >= 2000, spectral_centroid <= 8000), AND(rms > 0.4, pattern_regularity < 0.5, stability_factor < 0.5))',
                    'confidence_weight': 0.85,
                    'expert_notes': '고주파, 높은 진폭, 불규칙한 패턴이면 베어링 마모'
                },
                'unbalance_detection': {
                    'description': '언밸런스 감지 규칙',
                    'conditions': {
                        'spectral_centroid_range': (50, 500),
                        'rms_threshold': 0.3,
                        'pattern_regularity_threshold': 0.6,
                        'stability_factor_threshold': 0.6
                    },
                    'logic': 'AND(AND(spectral_centroid >= 50, spectral_centroid <= 500), AND(rms > 0.3, pattern_regularity > 0.4, stability_factor < 0.6))',
                    'confidence_weight': 0.8,
                    'expert_notes': '저주파, 높은 진폭, 주기적 진동이면 언밸런스'
                },
                'friction_detection': {
                    'description': '마찰 감지 규칙',
                    'conditions': {
                        'spectral_centroid_range': (500, 3000),
                        'rms_threshold': 0.25,
                        'pattern_regularity_threshold': 0.6,
                        'stability_factor_threshold': 0.6
                    },
                    'logic': 'AND(AND(spectral_centroid >= 500, spectral_centroid <= 3000), AND(rms > 0.25, pattern_regularity < 0.6, stability_factor < 0.6))',
                    'confidence_weight': 0.75,
                    'expert_notes': '중주파, 중간 진폭, 불규칙한 패턴이면 마찰'
                },
                'overload_detection': {
                    'description': '과부하 감지 규칙',
                    'conditions': {
                        'rms_threshold': 0.5,
                        'noise_level_threshold': 0.5,
                        'pattern_regularity_threshold': 0.3,
                        'stability_factor_threshold': 0.3
                    },
                    'logic': 'AND(AND(rms > 0.5, noise_level > 0.5), AND(pattern_regularity < 0.3, stability_factor < 0.3))',
                    'confidence_weight': 0.9,
                    'expert_notes': '높은 진폭, 높은 노이즈, 불규칙한 패턴이면 과부하'
                }
            }
            
            print("✅ 이상 유형 식별 규칙 생성 완료")
            
        except Exception as e:
            print(f"⚠️ 이상 유형 식별 규칙 생성 오류: {e}")
    
    def _generate_severity_assessment_rules(self):
        """심각도 평가 규칙 생성"""
        try:
            print("4️⃣ 심각도 평가 규칙 생성")
            
            self.generated_rules['severity_assessment'] = {
                'mild_anomaly': {
                    'description': '경미한 이상 평가 규칙',
                    'conditions': {
                        'stability_factor_range': (0.6, 0.8),
                        'pattern_regularity_range': (0.5, 0.7),
                        'frequency_consistency_range': (0.5, 0.7),
                        'noise_level_range': (0.2, 0.4)
                    },
                    'logic': 'AND(AND(stability_factor >= 0.6, stability_factor < 0.8), AND(pattern_regularity >= 0.5, pattern_regularity < 0.7), AND(frequency_consistency >= 0.5, frequency_consistency < 0.7), AND(noise_level >= 0.2, noise_level < 0.4))',
                    'severity_score': 2,
                    'action': '모니터링 강화, 정기 점검 유지',
                    'urgency': 'low',
                    'response_time': '1-2주 내'
                },
                'moderate_anomaly': {
                    'description': '중간 정도 이상 평가 규칙',
                    'conditions': {
                        'stability_factor_range': (0.4, 0.6),
                        'pattern_regularity_range': (0.3, 0.5),
                        'frequency_consistency_range': (0.3, 0.5),
                        'noise_level_range': (0.4, 0.6)
                    },
                    'logic': 'AND(AND(stability_factor >= 0.4, stability_factor < 0.6), AND(pattern_regularity >= 0.3, pattern_regularity < 0.5), AND(frequency_consistency >= 0.3, frequency_consistency < 0.5), AND(noise_level >= 0.4, noise_level < 0.6))',
                    'severity_score': 5,
                    'action': '점검 계획 수립, 모니터링 강화',
                    'urgency': 'medium',
                    'response_time': '3-5일 내'
                },
                'severe_anomaly': {
                    'description': '심각한 이상 평가 규칙',
                    'conditions': {
                        'stability_factor_range': (0.0, 0.4),
                        'pattern_regularity_range': (0.0, 0.3),
                        'frequency_consistency_range': (0.0, 0.3),
                        'noise_level_range': (0.6, 1.0)
                    },
                    'logic': 'OR(OR(stability_factor < 0.4, pattern_regularity < 0.3), OR(frequency_consistency < 0.3, noise_level > 0.6))',
                    'severity_score': 8,
                    'action': '즉시 점검 필요, 운전 중단 고려',
                    'urgency': 'high',
                    'response_time': '24시간 내'
                }
            }
            
            print("✅ 심각도 평가 규칙 생성 완료")
            
        except Exception as e:
            print(f"⚠️ 심각도 평가 규칙 생성 오류: {e}")
    
    def _generate_expert_heuristic_rules(self):
        """엔지니어 휴리스틱 규칙 생성"""
        try:
            print("5️⃣ 엔지니어 휴리스틱 규칙 생성")
            
            self.generated_rules['expert_heuristics'] = {
                'stability_check': {
                    'description': '안정성 검사 휴리스틱',
                    'method': 'RMS와 ZCR의 변동계수 계산',
                    'threshold': 0.2,
                    'expert_rule': '변동계수가 0.2 미만이면 정상, 이상이면 이상',
                    'implementation': 'stability = 1 / (1 + np.std(rms_windows) / np.mean(rms_windows))'
                },
                'frequency_consistency_check': {
                    'description': '주파수 일관성 검사 휴리스틱',
                    'method': '스펙트럼 센트로이드의 안정성 측정',
                    'threshold': 0.3,
                    'expert_rule': '주파수 분포가 일정하면 정상, 변화가 크면 이상',
                    'implementation': 'consistency = 1 / (1 + np.std(spectral_centroids) / np.mean(spectral_centroids))'
                },
                'pattern_regularity_check': {
                    'description': '패턴 규칙성 검사 휴리스틱',
                    'method': '자기상관 함수를 이용한 주기성 측정',
                    'threshold': 0.7,
                    'expert_rule': '주기성이 높으면 정상, 낮으면 이상',
                    'implementation': 'regularity = np.max(autocorr[1:]) / autocorr[0]'
                },
                'harmonic_analysis_check': {
                    'description': '하모닉스 분석 휴리스틱',
                    'method': '기본 주파수의 하모닉스 존재 여부 확인',
                    'threshold': 0.5,
                    'expert_rule': '하모닉스가 정상적이면 정상, 비정상적이면 이상',
                    'implementation': 'harmonic_ratio = (H2 + H3) / (2 * H1)'
                },
                'noise_level_check': {
                    'description': '노이즈 레벨 검사 휴리스틱',
                    'method': '백그라운드 노이즈 레벨 측정',
                    'threshold': 0.1,
                    'expert_rule': '노이즈 레벨이 낮으면 정상, 높으면 이상',
                    'implementation': 'noise_level = np.std(high_freq_component) / 0.5'
                }
            }
            
            print("✅ 엔지니어 휴리스틱 규칙 생성 완료")
            
        except Exception as e:
            print(f"⚠️ 엔지니어 휴리스틱 규칙 생성 오류: {e}")
    
    def create_rule_engine(self) -> Dict:
        """실제 AI에서 사용할 수 있는 규칙 엔진 생성"""
        try:
            print("🔧 규칙 엔진 생성 시작")
            
            self.rule_engine = {
                'rule_engine_version': '1.0.0',
                'created_at': datetime.now().isoformat(),
                'rules': self.generated_rules,
                'execution_order': [
                    'basic_diagnostic',
                    'advanced_analysis',
                    'anomaly_identification',
                    'severity_assessment',
                    'expert_heuristics'
                ],
                'confidence_calculation': {
                    'method': 'weighted_average',
                    'weights': {
                        'basic_diagnostic': 0.3,
                        'advanced_analysis': 0.25,
                        'anomaly_identification': 0.25,
                        'severity_assessment': 0.15,
                        'expert_heuristics': 0.05
                    }
                }
            }
            
            print("✅ 규칙 엔진 생성 완료")
            return self.rule_engine
            
        except Exception as e:
            print(f"❌ 규칙 엔진 생성 오류: {e}")
            return {}
    
    def save_generated_rules(self, filepath: str = "data/generated_domain_rules.json"):
        """생성된 규칙 저장"""
        try:
            import os
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.rule_engine, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 생성된 규칙 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 규칙 저장 오류: {e}")
            return False
    
    def print_rules_summary(self):
        """생성된 규칙 요약 출력"""
        print("\n" + "=" * 60)
        print("🔧 도메인 지식 기반 규칙 생성 결과")
        print("=" * 60)
        
        for category, rules in self.generated_rules.items():
            print(f"\n📋 {category}:")
            for rule_name, rule_data in rules.items():
                print(f"   - {rule_name}: {rule_data.get('description', 'N/A')}")
        
        print(f"\n📊 총 규칙 수: {sum(len(rules) for rules in self.generated_rules.values())}개")
        print(f"📊 규칙 카테고리: {len(self.generated_rules)}개")

# 사용 예제
if __name__ == "__main__":
    # 도메인 지식 기반 규칙 생성기 테스트
    rules_generator = DomainBasedRulesGenerator()
    
    print("🔧 도메인 지식 기반 규칙 생성기 테스트")
    print("=" * 60)
    
    # 규칙 엔진 생성
    rule_engine = rules_generator.create_rule_engine()
    
    # 생성된 규칙 요약 출력
    rules_generator.print_rules_summary()
    
    # 규칙 저장
    rules_generator.save_generated_rules()
    
    print("\n🎉 2단계: 기본 규칙 생성 완료!")
    print("   도메인 지식 기반 규칙이 실제 AI에서 사용할 수 있도록 생성되었습니다.")
