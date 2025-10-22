#!/usr/bin/env python3
"""
기계 엔지니어 지식 명시화 시스템
기계 설치 전에 엔지니어의 암묵적 지식을 명시적 지식으로 환산하여 AI 학습에 활용
"""

import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class KnowledgeExplicitConverter:
    """기계 엔지니어 지식 명시화 시스템"""
    
    def __init__(self):
        self.explicit_knowledge = {}
        self.knowledge_rules = {}
        self.synthetic_data_generator = {}
        self.ai_learning_system = {}
        
        print("🧠 기계 엔지니어 지식 명시화 시스템 초기화")
        print("   기계 설치 전 AI 학습을 위한 지식 환산 시스템")
    
    def convert_implicit_to_explicit_knowledge(self, engineer_interviews: List[Dict]):
        """암묵적 지식을 명시적 지식으로 환산"""
        try:
            print("🔄 암묵적 지식 → 명시적 지식 환산 시작")
            
            # 1. 인터뷰 데이터 분석
            analyzed_knowledge = self._analyze_engineer_interviews(engineer_interviews)
            
            # 2. 지식 구조화
            structured_knowledge = self._structure_knowledge(analyzed_knowledge)
            
            # 3. 규칙 생성
            knowledge_rules = self._generate_knowledge_rules(structured_knowledge)
            
            # 4. 검증 및 정제
            validated_knowledge = self._validate_and_refine_knowledge(knowledge_rules)
            
            self.explicit_knowledge = validated_knowledge
            print("✅ 암묵적 지식 → 명시적 지식 환산 완료")
            
            return validated_knowledge
            
        except Exception as e:
            print(f"❌ 지식 환산 오류: {e}")
            return {}
    
    def _analyze_engineer_interviews(self, interviews: List[Dict]) -> Dict:
        """엔지니어 인터뷰 데이터 분석"""
        try:
            print("1️⃣ 엔지니어 인터뷰 데이터 분석")
            
            analysis_results = {
                'sound_patterns': {},
                'diagnostic_criteria': {},
                'experience_rules': {},
                'heuristic_knowledge': {},
                'troubleshooting_flows': {}
            }
            
            for interview in interviews:
                # 소리 패턴 분석
                if 'sound_descriptions' in interview:
                    sound_patterns = self._extract_sound_patterns(interview['sound_descriptions'])
                    analysis_results['sound_patterns'].update(sound_patterns)
                
                # 진단 기준 분석
                if 'diagnostic_methods' in interview:
                    diagnostic_criteria = self._extract_diagnostic_criteria(interview['diagnostic_methods'])
                    analysis_results['diagnostic_criteria'].update(diagnostic_criteria)
                
                # 경험 규칙 분석
                if 'experience_stories' in interview:
                    experience_rules = self._extract_experience_rules(interview['experience_stories'])
                    analysis_results['experience_rules'].update(experience_rules)
                
                # 휴리스틱 지식 분석
                if 'heuristic_tips' in interview:
                    heuristic_knowledge = self._extract_heuristic_knowledge(interview['heuristic_tips'])
                    analysis_results['heuristic_knowledge'].update(heuristic_knowledge)
                
                # 문제 해결 흐름 분석
                if 'troubleshooting_stories' in interview:
                    troubleshooting_flows = self._extract_troubleshooting_flows(interview['troubleshooting_stories'])
                    analysis_results['troubleshooting_flows'].update(troubleshooting_flows)
            
            print("✅ 인터뷰 데이터 분석 완료")
            return analysis_results
            
        except Exception as e:
            print(f"⚠️ 인터뷰 데이터 분석 오류: {e}")
            return {}
    
    def _extract_sound_patterns(self, sound_descriptions: List[Dict]) -> Dict:
        """소리 패턴 추출"""
        patterns = {}
        
        for description in sound_descriptions:
            pattern_name = description.get('name', 'unknown')
            patterns[pattern_name] = {
                'description': description.get('description', ''),
                'frequency_characteristics': self._parse_frequency_description(description.get('frequency', '')),
                'amplitude_characteristics': self._parse_amplitude_description(description.get('amplitude', '')),
                'temporal_characteristics': self._parse_temporal_description(description.get('temporal', '')),
                'expert_notes': description.get('expert_notes', ''),
                'confidence_level': description.get('confidence', 0.8)
            }
        
        return patterns
    
    def _parse_frequency_description(self, freq_desc: str) -> Dict:
        """주파수 설명 파싱"""
        # "저주파", "중주파", "고주파" 등을 수치로 변환
        freq_ranges = {
            '저주파': (20, 200),
            '중주파': (200, 1000),
            '고주파': (1000, 5000),
            '초고주파': (5000, 8000)
        }
        
        for key, value in freq_ranges.items():
            if key in freq_desc:
                return {'range': value, 'description': freq_desc}
        
        return {'range': (100, 1000), 'description': freq_desc}
    
    def _parse_amplitude_description(self, amp_desc: str) -> Dict:
        """진폭 설명 파싱"""
        # "약한", "중간", "강한" 등을 수치로 변환
        amp_ranges = {
            '약한': (0.1, 0.3),
            '중간': (0.3, 0.6),
            '강한': (0.6, 1.0)
        }
        
        for key, value in amp_ranges.items():
            if key in amp_desc:
                return {'range': value, 'description': amp_desc}
        
        return {'range': (0.2, 0.5), 'description': amp_desc}
    
    def _parse_temporal_description(self, temp_desc: str) -> Dict:
        """시간적 특성 설명 파싱"""
        # "일정한", "불규칙한", "주기적" 등을 수치로 변환
        temporal_characteristics = {
            '일정한': {'regularity': 0.9, 'stability': 0.9},
            '불규칙한': {'regularity': 0.3, 'stability': 0.3},
            '주기적': {'regularity': 0.7, 'stability': 0.6},
            '안정적': {'regularity': 0.8, 'stability': 0.9},
            '불안정한': {'regularity': 0.4, 'stability': 0.4}
        }
        
        for key, value in temporal_characteristics.items():
            if key in temp_desc:
                return {**value, 'description': temp_desc}
        
        return {'regularity': 0.5, 'stability': 0.5, 'description': temp_desc}
    
    def _extract_diagnostic_criteria(self, diagnostic_methods: List[Dict]) -> Dict:
        """진단 기준 추출"""
        criteria = {}
        
        for method in diagnostic_methods:
            method_name = method.get('name', 'unknown')
            criteria[method_name] = {
                'description': method.get('description', ''),
                'steps': method.get('steps', []),
                'thresholds': method.get('thresholds', {}),
                'decision_logic': method.get('decision_logic', ''),
                'confidence_factors': method.get('confidence_factors', {}),
                'expert_notes': method.get('expert_notes', '')
            }
        
        return criteria
    
    def _extract_experience_rules(self, experience_stories: List[Dict]) -> Dict:
        """경험 규칙 추출"""
        rules = {}
        
        for story in experience_stories:
            rule_name = story.get('situation', 'unknown')
            rules[rule_name] = {
                'context': story.get('context', ''),
                'symptoms': story.get('symptoms', []),
                'diagnosis': story.get('diagnosis', ''),
                'solution': story.get('solution', ''),
                'prevention': story.get('prevention', ''),
                'confidence': story.get('confidence', 0.7),
                'frequency': story.get('frequency', 'rare')  # rare, common, frequent
            }
        
        return rules
    
    def _extract_heuristic_knowledge(self, heuristic_tips: List[Dict]) -> Dict:
        """휴리스틱 지식 추출"""
        heuristics = {}
        
        for tip in heuristic_tips:
            tip_name = tip.get('name', 'unknown')
            heuristics[tip_name] = {
                'rule': tip.get('rule', ''),
                'conditions': tip.get('conditions', []),
                'action': tip.get('action', ''),
                'confidence': tip.get('confidence', 0.8),
                'expert_notes': tip.get('expert_notes', ''),
                'applicability': tip.get('applicability', 'general')
            }
        
        return heuristics
    
    def _extract_troubleshooting_flows(self, troubleshooting_stories: List[Dict]) -> Dict:
        """문제 해결 흐름 추출"""
        flows = {}
        
        for story in troubleshooting_stories:
            flow_name = story.get('problem_type', 'unknown')
            flows[flow_name] = {
                'problem_description': story.get('problem_description', ''),
                'investigation_steps': story.get('investigation_steps', []),
                'decision_points': story.get('decision_points', []),
                'solution_paths': story.get('solution_paths', []),
                'success_criteria': story.get('success_criteria', []),
                'lessons_learned': story.get('lessons_learned', [])
            }
        
        return flows
    
    def _structure_knowledge(self, analyzed_knowledge: Dict) -> Dict:
        """지식 구조화"""
        try:
            print("2️⃣ 지식 구조화")
            
            structured = {
                'knowledge_hierarchy': {
                    'level_1': 'sound_classification',
                    'level_2': 'diagnostic_methods',
                    'level_3': 'experience_rules',
                    'level_4': 'heuristic_tips',
                    'level_5': 'troubleshooting_flows'
                },
                'knowledge_relationships': self._build_knowledge_relationships(analyzed_knowledge),
                'confidence_mapping': self._build_confidence_mapping(analyzed_knowledge),
                'applicability_matrix': self._build_applicability_matrix(analyzed_knowledge)
            }
            
            print("✅ 지식 구조화 완료")
            return structured
            
        except Exception as e:
            print(f"⚠️ 지식 구조화 오류: {e}")
            return {}
    
    def _build_knowledge_relationships(self, knowledge: Dict) -> Dict:
        """지식 간 관계 구축"""
        relationships = {
            'sound_to_diagnosis': {},
            'diagnosis_to_solution': {},
            'experience_to_heuristic': {},
            'heuristic_to_troubleshooting': {}
        }
        
        # 소리 패턴 → 진단 방법 관계
        for sound_name, sound_info in knowledge.get('sound_patterns', {}).items():
            relationships['sound_to_diagnosis'][sound_name] = []
            for diag_name, diag_info in knowledge.get('diagnostic_criteria', {}).items():
                if self._is_related(sound_info, diag_info):
                    relationships['sound_to_diagnosis'][sound_name].append(diag_name)
        
        return relationships
    
    def _is_related(self, sound_info: Dict, diag_info: Dict) -> bool:
        """지식 간 관련성 판단"""
        # 간단한 키워드 매칭으로 관련성 판단
        sound_desc = sound_info.get('description', '').lower()
        diag_desc = diag_info.get('description', '').lower()
        
        common_keywords = ['진동', '소음', '주파수', '진폭', '패턴']
        return any(keyword in sound_desc and keyword in diag_desc for keyword in common_keywords)
    
    def _build_confidence_mapping(self, knowledge: Dict) -> Dict:
        """신뢰도 매핑 구축"""
        confidence_map = {}
        
        for category, items in knowledge.items():
            confidence_map[category] = {}
            for item_name, item_info in items.items():
                confidence_map[category][item_name] = item_info.get('confidence', 0.5)
        
        return confidence_map
    
    def _build_applicability_matrix(self, knowledge: Dict) -> Dict:
        """적용 가능성 매트릭스 구축"""
        applicability = {
            'general': [],
            'specific': [],
            'rare': [],
            'common': []
        }
        
        for category, items in knowledge.items():
            for item_name, item_info in items.items():
                freq = item_info.get('frequency', 'common')
                if freq in applicability:
                    applicability[freq].append(f"{category}.{item_name}")
        
        return applicability
    
    def _generate_knowledge_rules(self, structured_knowledge: Dict) -> Dict:
        """지식 규칙 생성"""
        try:
            print("3️⃣ 지식 규칙 생성")
            
            rules = {
                'if_then_rules': [],
                'fuzzy_rules': [],
                'probabilistic_rules': [],
                'temporal_rules': [],
                'contextual_rules': []
        }
        
        # IF-THEN 규칙 생성
        if_then_rules = self._generate_if_then_rules(structured_knowledge)
        rules['if_then_rules'] = if_then_rules
        
        # 퍼지 규칙 생성
        fuzzy_rules = self._generate_fuzzy_rules(structured_knowledge)
        rules['fuzzy_rules'] = fuzzy_rules
        
        # 확률적 규칙 생성
        prob_rules = self._generate_probabilistic_rules(structured_knowledge)
        rules['probabilistic_rules'] = prob_rules
        
        print("✅ 지식 규칙 생성 완료")
        return rules
        
        except Exception as e:
            print(f"⚠️ 지식 규칙 생성 오류: {e}")
            return {}
    
    def _generate_if_then_rules(self, structured_knowledge: Dict) -> List[Dict]:
        """IF-THEN 규칙 생성"""
        rules = []
        
        # 예시 규칙들
        example_rules = [
            {
                'rule_id': 'R001',
                'description': '정상 압축기 소리 판단',
                'if_conditions': [
                    'frequency_range == "저주파"',
                    'amplitude_range == "중간"',
                    'regularity > 0.8',
                    'stability > 0.8'
                ],
                'then_action': 'classify_as_normal_compressor',
                'confidence': 0.9,
                'source': 'engineer_experience'
            },
            {
                'rule_id': 'R002',
                'description': '베어링 마모 소리 판단',
                'if_conditions': [
                    'frequency_range == "고주파"',
                    'amplitude_range == "강한"',
                    'regularity < 0.5',
                    'stability < 0.5'
                ],
                'then_action': 'classify_as_bearing_wear',
                'confidence': 0.85,
                'source': 'engineer_experience'
            }
        ]
        
        rules.extend(example_rules)
        return rules
    
    def _generate_fuzzy_rules(self, structured_knowledge: Dict) -> List[Dict]:
        """퍼지 규칙 생성"""
        rules = []
        
        # 예시 퍼지 규칙들
        example_fuzzy_rules = [
            {
                'rule_id': 'F001',
                'description': '소음 레벨 퍼지 판단',
                'input_variables': {
                    'noise_level': {
                        'low': (0.0, 0.3),
                        'medium': (0.2, 0.7),
                        'high': (0.6, 1.0)
                    }
                },
                'output_variable': 'noise_severity',
                'rules': [
                    'IF noise_level IS low THEN noise_severity IS normal',
                    'IF noise_level IS medium THEN noise_severity IS warning',
                    'IF noise_level IS high THEN noise_severity IS critical'
                ],
                'confidence': 0.8
            }
        ]
        
        rules.extend(example_fuzzy_rules)
        return rules
    
    def _generate_probabilistic_rules(self, structured_knowledge: Dict) -> List[Dict]:
        """확률적 규칙 생성"""
        rules = []
        
        # 예시 확률적 규칙들
        example_prob_rules = [
            {
                'rule_id': 'P001',
                'description': '베어링 마모 확률 계산',
                'conditions': {
                    'high_frequency_energy': 0.7,
                    'irregular_pattern': 0.8,
                    'increased_vibration': 0.6
                },
                'probabilities': {
                    'bearing_wear': 0.85,
                    'normal_wear': 0.10,
                    'other_issue': 0.05
                },
                'confidence': 0.8
            }
        ]
        
        rules.extend(example_prob_rules)
        return rules
    
    def _validate_and_refine_knowledge(self, knowledge_rules: Dict) -> Dict:
        """지식 검증 및 정제"""
        try:
            print("4️⃣ 지식 검증 및 정제")
            
            validated = {
                'validated_rules': {},
                'confidence_scores': {},
                'consistency_check': {},
                'completeness_check': {},
                'refined_knowledge': {}
            }
            
            # 규칙 검증
            for rule_type, rules in knowledge_rules.items():
                validated['validated_rules'][rule_type] = []
                for rule in rules:
                    if self._validate_rule(rule):
                        validated['validated_rules'][rule_type].append(rule)
            
            # 신뢰도 점수 계산
            validated['confidence_scores'] = self._calculate_confidence_scores(validated['validated_rules'])
            
            # 일관성 검사
            validated['consistency_check'] = self._check_consistency(validated['validated_rules'])
            
            # 완전성 검사
            validated['completeness_check'] = self._check_completeness(validated['validated_rules'])
            
            print("✅ 지식 검증 및 정제 완료")
            return validated
            
        except Exception as e:
            print(f"⚠️ 지식 검증 및 정제 오류: {e}")
            return {}
    
    def _validate_rule(self, rule: Dict) -> bool:
        """개별 규칙 검증"""
        required_fields = ['rule_id', 'description', 'confidence']
        return all(field in rule for field in required_fields) and rule['confidence'] > 0.5
    
    def _calculate_confidence_scores(self, validated_rules: Dict) -> Dict:
        """신뢰도 점수 계산"""
        confidence_scores = {}
        
        for rule_type, rules in validated_rules.items():
            if rules:
                avg_confidence = sum(rule['confidence'] for rule in rules) / len(rules)
                confidence_scores[rule_type] = {
                    'average': avg_confidence,
                    'min': min(rule['confidence'] for rule in rules),
                    'max': max(rule['confidence'] for rule in rules),
                    'count': len(rules)
                }
        
        return confidence_scores
    
    def _check_consistency(self, validated_rules: Dict) -> Dict:
        """일관성 검사"""
        consistency_issues = []
        
        # 규칙 간 충돌 검사
        for rule_type, rules in validated_rules.items():
            for i, rule1 in enumerate(rules):
                for j, rule2 in enumerate(rules[i+1:], i+1):
                    if self._rules_conflict(rule1, rule2):
                        consistency_issues.append({
                            'type': 'rule_conflict',
                            'rule1': rule1['rule_id'],
                            'rule2': rule2['rule_id'],
                            'severity': 'medium'
                        })
        
        return {
            'issues': consistency_issues,
            'consistency_score': max(0, 1.0 - len(consistency_issues) * 0.1)
        }
    
    def _rules_conflict(self, rule1: Dict, rule2: Dict) -> bool:
        """규칙 충돌 검사"""
        # 간단한 충돌 검사 (실제로는 더 복잡한 로직 필요)
        return (rule1.get('then_action') == rule2.get('then_action') and 
                rule1.get('confidence') > 0.8 and rule2.get('confidence') > 0.8)
    
    def _check_completeness(self, validated_rules: Dict) -> Dict:
        """완전성 검사"""
        completeness_score = 0.0
        missing_areas = []
        
        # 필수 규칙 영역 검사
        required_areas = ['sound_classification', 'diagnostic_methods', 'troubleshooting']
        for area in required_areas:
            if not any(area in str(rules) for rules in validated_rules.values()):
                missing_areas.append(area)
        
        completeness_score = 1.0 - len(missing_areas) / len(required_areas)
        
        return {
            'completeness_score': completeness_score,
            'missing_areas': missing_areas,
            'recommendations': [f"Add rules for {area}" for area in missing_areas]
        }
    
    def create_synthetic_data_from_knowledge(self, explicit_knowledge: Dict) -> Dict:
        """명시적 지식으로부터 합성 데이터 생성"""
        try:
            print("🎵 명시적 지식 기반 합성 데이터 생성")
            
            synthetic_data = {
                'audio_samples': {},
                'feature_vectors': {},
                'labels': {},
                'metadata': {}
            }
            
            # 지식 기반 오디오 샘플 생성
            for rule_type, rules in explicit_knowledge.get('validated_rules', {}).items():
                if rule_type == 'if_then_rules':
                    samples = self._generate_samples_from_if_then_rules(rules)
                    synthetic_data['audio_samples'][rule_type] = samples
                elif rule_type == 'fuzzy_rules':
                    samples = self._generate_samples_from_fuzzy_rules(rules)
                    synthetic_data['audio_samples'][rule_type] = samples
            
            # 특징 벡터 생성
            synthetic_data['feature_vectors'] = self._generate_feature_vectors(synthetic_data['audio_samples'])
            
            # 라벨 생성
            synthetic_data['labels'] = self._generate_labels(synthetic_data['audio_samples'])
            
            # 메타데이터 생성
            synthetic_data['metadata'] = {
                'generation_timestamp': datetime.now().isoformat(),
                'knowledge_source': 'engineer_explicit_knowledge',
                'total_samples': sum(len(samples) for samples in synthetic_data['audio_samples'].values()),
                'feature_count': 10
            }
            
            print("✅ 합성 데이터 생성 완료")
            return synthetic_data
            
        except Exception as e:
            print(f"❌ 합성 데이터 생성 오류: {e}")
            return {}
    
    def _generate_samples_from_if_then_rules(self, rules: List[Dict]) -> List[Dict]:
        """IF-THEN 규칙으로부터 샘플 생성"""
        samples = []
        
        for rule in rules:
            if 'if_conditions' in rule:
                # 조건에 맞는 오디오 샘플 생성
                sample = self._create_audio_sample_from_conditions(rule['if_conditions'])
                sample['rule_id'] = rule['rule_id']
                sample['confidence'] = rule['confidence']
                samples.append(sample)
        
        return samples
    
    def _create_audio_sample_from_conditions(self, conditions: List[str]) -> Dict:
        """조건으로부터 오디오 샘플 생성"""
        # 조건을 파싱하여 오디오 파라미터 생성
        audio_params = {
            'frequency': 1000,  # 기본값
            'amplitude': 0.5,   # 기본값
            'duration': 5.0,    # 5초
            'sample_rate': 16000
        }
        
        for condition in conditions:
            if 'frequency_range' in condition:
                if '저주파' in condition:
                    audio_params['frequency'] = np.random.uniform(60, 200)
                elif '고주파' in condition:
                    audio_params['frequency'] = np.random.uniform(2000, 5000)
            elif 'amplitude_range' in condition:
                if '중간' in condition:
                    audio_params['amplitude'] = np.random.uniform(0.3, 0.6)
                elif '강한' in condition:
                    audio_params['amplitude'] = np.random.uniform(0.6, 1.0)
        
        # 오디오 데이터 생성
        t = np.linspace(0, audio_params['duration'], int(audio_params['sample_rate'] * audio_params['duration']))
        audio_data = audio_params['amplitude'] * np.sin(2 * np.pi * audio_params['frequency'] * t)
        
        return {
            'audio_data': audio_data,
            'parameters': audio_params,
            'sample_rate': audio_params['sample_rate']
        }
    
    def _generate_samples_from_fuzzy_rules(self, rules: List[Dict]) -> List[Dict]:
        """퍼지 규칙으로부터 샘플 생성"""
        samples = []
        
        for rule in rules:
            if 'input_variables' in rule:
                # 퍼지 변수에 따른 샘플 생성
                sample = self._create_audio_sample_from_fuzzy_variables(rule['input_variables'])
                sample['rule_id'] = rule['rule_id']
                sample['confidence'] = rule['confidence']
                samples.append(sample)
        
        return samples
    
    def _create_audio_sample_from_fuzzy_variables(self, variables: Dict) -> Dict:
        """퍼지 변수로부터 오디오 샘플 생성"""
        audio_params = {
            'frequency': 1000,
            'amplitude': 0.5,
            'duration': 5.0,
            'sample_rate': 16000
        }
        
        # 노이즈 레벨에 따른 파라미터 조정
        if 'noise_level' in variables:
            noise_levels = variables['noise_level']
            if 'low' in noise_levels:
                audio_params['amplitude'] = np.random.uniform(0.1, 0.3)
            elif 'high' in noise_levels:
                audio_params['amplitude'] = np.random.uniform(0.7, 1.0)
        
        # 오디오 데이터 생성
        t = np.linspace(0, audio_params['duration'], int(audio_params['sample_rate'] * audio_params['duration']))
        audio_data = audio_params['amplitude'] * np.sin(2 * np.pi * audio_params['frequency'] * t)
        
        return {
            'audio_data': audio_data,
            'parameters': audio_params,
            'sample_rate': audio_params['sample_rate']
        }
    
    def _generate_feature_vectors(self, audio_samples: Dict) -> Dict:
        """특징 벡터 생성"""
        feature_vectors = {}
        
        for rule_type, samples in audio_samples.items():
            feature_vectors[rule_type] = []
            for sample in samples:
                # 간단한 특징 추출 (실제로는 더 복잡한 특징 추출)
                features = self._extract_simple_features(sample['audio_data'])
                feature_vectors[rule_type].append(features)
        
        return feature_vectors
    
    def _extract_simple_features(self, audio_data: np.ndarray) -> np.ndarray:
        """간단한 특징 추출"""
        features = [
            np.sqrt(np.mean(audio_data ** 2)),  # RMS
            np.mean(np.diff(np.sign(audio_data))),  # ZCR
            np.mean(audio_data),  # Mean
            np.std(audio_data),   # Std
            np.max(np.abs(audio_data)),  # Peak
            np.var(audio_data),   # Variance
            np.mean(np.abs(audio_data)),  # Mean absolute value
            np.median(audio_data),  # Median
            np.percentile(audio_data, 75) - np.percentile(audio_data, 25),  # IQR
            np.sum(audio_data > 0) / len(audio_data)  # Positive ratio
        ]
        
        return np.array(features)
    
    def _generate_labels(self, audio_samples: Dict) -> Dict:
        """라벨 생성"""
        labels = {}
        
        for rule_type, samples in audio_samples.items():
            labels[rule_type] = []
            for sample in samples:
                # 규칙 ID를 기반으로 라벨 생성
                rule_id = sample.get('rule_id', 'unknown')
                label = {
                    'rule_id': rule_id,
                    'category': 'normal' if 'normal' in rule_id.lower() else 'abnormal',
                    'confidence': sample.get('confidence', 0.5)
                }
                labels[rule_type].append(label)
        
        return labels
    
    def save_explicit_knowledge(self, filepath: str = "data/explicit_knowledge.json"):
        """명시적 지식 저장"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.explicit_knowledge, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 명시적 지식 저장 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ 명시적 지식 저장 오류: {e}")
            return False
    
    def print_knowledge_summary(self):
        """지식 요약 출력"""
        print("\n" + "=" * 60)
        print("🧠 기계 엔지니어 지식 명시화 결과")
        print("=" * 60)
        
        if 'validated_rules' in self.explicit_knowledge:
            rules = self.explicit_knowledge['validated_rules']
            print(f"\n📋 검증된 규칙 수:")
            for rule_type, rule_list in rules.items():
                print(f"   - {rule_type}: {len(rule_list)}개")
        
        if 'confidence_scores' in self.explicit_knowledge:
            scores = self.explicit_knowledge['confidence_scores']
            print(f"\n🎯 신뢰도 점수:")
            for rule_type, score_info in scores.items():
                print(f"   - {rule_type}: 평균 {score_info['average']:.3f}")

# 사용 예제
if __name__ == "__main__":
    # 기계 엔지니어 지식 명시화 시스템 테스트
    converter = KnowledgeExplicitConverter()
    
    print("🧠 기계 엔지니어 지식 명시화 시스템 테스트")
    print("=" * 60)
    
    # 가상의 엔지니어 인터뷰 데이터
    sample_interviews = [
        {
            'sound_descriptions': [
                {
                    'name': '정상_압축기',
                    'description': '일정한 저주파 소음',
                    'frequency': '저주파',
                    'amplitude': '중간',
                    'temporal': '일정한',
                    'expert_notes': '정상적인 압축기 작동 소리',
                    'confidence': 0.9
                },
                {
                    'name': '베어링_마모',
                    'description': '불규칙한 고주파 진동',
                    'frequency': '고주파',
                    'amplitude': '강한',
                    'temporal': '불규칙한',
                    'expert_notes': '베어링 마모로 인한 마찰음',
                    'confidence': 0.85
                }
            ],
            'diagnostic_methods': [
                {
                    'name': '안정성_검사',
                    'description': 'RMS와 ZCR의 변동계수 계산',
                    'steps': ['RMS 계산', 'ZCR 계산', '변동계수 계산', '임계값 비교'],
                    'thresholds': {'stability_threshold': 0.8},
                    'decision_logic': 'stability > 0.8이면 정상',
                    'confidence_factors': {'experience': 0.9, 'data_quality': 0.8},
                    'expert_notes': '가장 중요한 진단 기준'
                }
            ],
            'experience_stories': [
                {
                    'situation': '베어링_마모_초기',
                    'context': '압축기 베어링 마모 초기 단계',
                    'symptoms': ['고주파 진동', '불규칙한 소음', '진동 증가'],
                    'diagnosis': '베어링 마모',
                    'solution': '베어링 교체',
                    'prevention': '정기 윤활 및 모니터링',
                    'confidence': 0.9,
                    'frequency': 'common'
                }
            ],
            'heuristic_tips': [
                {
                    'name': '소음_레벨_판단',
                    'rule': '소음이 갑자기 증가하면 이상 징후',
                    'conditions': ['소음 레벨 변화', '시간적 변화'],
                    'action': '즉시 점검 필요',
                    'confidence': 0.8,
                    'expert_notes': '경험상 가장 효과적인 휴리스틱',
                    'applicability': 'general'
                }
            ],
            'troubleshooting_stories': [
                {
                    'problem_type': '압축기_이상',
                    'problem_description': '압축기에서 이상 소음 발생',
                    'investigation_steps': ['소음 위치 확인', '주파수 분석', '진동 측정'],
                    'decision_points': ['정상 범위 내?', '점진적 변화?', '급격한 변화?'],
                    'solution_paths': ['정기 점검', '부품 교체', '전체 교체'],
                    'success_criteria': ['소음 감소', '진동 정상화', '성능 회복'],
                    'lessons_learned': ['조기 발견 중요', '정기 모니터링 필요']
                }
            ]
        }
    ]
    
    # 암묵적 지식을 명시적 지식으로 환산
    explicit_knowledge = converter.convert_implicit_to_explicit_knowledge(sample_interviews)
    
    # 명시적 지식으로부터 합성 데이터 생성
    synthetic_data = converter.create_synthetic_data_from_knowledge(explicit_knowledge)
    
    # 지식 요약 출력
    converter.print_knowledge_summary()
    
    # 명시적 지식 저장
    converter.save_explicit_knowledge()
    
    print("\n🎉 기계 엔지니어 지식 명시화 완료!")
    print("   암묵적 지식이 명시적 지식으로 성공적으로 환산되었습니다.")
