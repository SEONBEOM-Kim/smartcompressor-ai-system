#!/usr/bin/env python3
"""
간단한 소리 분류기
고장 소리 vs 정상 소리를 최대한 많이 분류할 수 있는 프로그램
"""

import json
import os
from datetime import datetime
from typing import Dict, List

class SimpleSoundClassifier:
    """간단한 소리 분류기"""
    
    def __init__(self):
        self.classification_data = {
            'normal_sounds': [],
            'fault_sounds': [],
            'classification_rules': {},
            'statistics': {}
        }
        print("🎵 간단한 소리 분류기")
        print("   고장 소리 vs 정상 소리 분류 프로그램")
    
    def start_classification(self):
        """소리 분류 시작"""
        print("\n" + "=" * 60)
        print("🎵 소리 분류 프로그램")
        print("=" * 60)
        print("목적: 고장 소리 vs 정상 소리 분류")
        print("방법: 소리 설명을 듣고 정상/고장으로 분류")
        print("=" * 60)
        
        # 기본 정보 입력
        self._input_basic_info()
        
        # 소리 분류 시작
        self._classify_sounds()
        
        # 분류 규칙 생성
        self._generate_classification_rules()
        
        # 통계 생성
        self._generate_statistics()
        
        # 결과 저장
        self._save_classification_data()
        
        print("\n🎉 소리 분류 완료!")
    
    def _input_basic_info(self):
        """기본 정보 입력"""
        print("\n📋 기본 정보")
        print("-" * 30)
        
        self.classification_data['basic_info'] = {
            'name': input("이름: "),
            'experience_years': input("압축기 경험 (년): "),
            'company': input("회사명: "),
            'input_date': datetime.now().isoformat()
        }
        
        print(f"✅ 기본 정보 입력 완료")
    
    def _classify_sounds(self):
        """소리 분류"""
        print("\n🎵 소리 분류")
        print("-" * 40)
        print("소리 설명을 듣고 정상/고장으로 분류해주세요")
        print("(정상: n, 고장: f, 종료: q)")
        
        sound_count = 0
        
        while True:
            sound_count += 1
            print(f"\n🔊 소리 {sound_count}:")
            
            # 소리 설명 입력
            description = input("   소리 설명: ")
            if description.lower() == 'q':
                break
            
            # 분류 입력
            while True:
                classification = input("   분류 (정상:n, 고장:f): ").lower()
                if classification in ['n', 'f']:
                    break
                print("   n 또는 f를 입력해주세요")
            
            # 신뢰도 입력
            confidence = input("   신뢰도 (1-10, 10이 가장 확실): ")
            confidence = int(confidence) if confidence.isdigit() else 5
            
            # 특징 입력
            features = input("   특징 (쉼표로 구분, 예: 큰소리,불규칙,고주파): ")
            features_list = [f.strip() for f in features.split(',')] if features else []
            
            # 분류 결과 저장
            sound_data = {
                'id': sound_count,
                'description': description,
                'classification': 'normal' if classification == 'n' else 'fault',
                'confidence': confidence,
                'features': features_list,
                'timestamp': datetime.now().isoformat()
            }
            
            if classification == 'n':
                self.classification_data['normal_sounds'].append(sound_data)
            else:
                self.classification_data['fault_sounds'].append(sound_data)
            
            print(f"   ✅ 분류 완료: {'정상' if classification == 'n' else '고장'}")
            
            # 계속할지 물어보기
            continue_input = input("   계속 분류하시겠습니까? (y/n): ").lower()
            if continue_input == 'n':
                break
        
        print(f"\n✅ 소리 분류 완료: 총 {sound_count-1}개 소리 분류")
    
    def _generate_classification_rules(self):
        """분류 규칙 생성"""
        print("\n🔍 분류 규칙 생성")
        print("-" * 40)
        
        # 정상 소리 특징 분석
        normal_features = []
        for sound in self.classification_data['normal_sounds']:
            normal_features.extend(sound['features'])
        
        # 고장 소리 특징 분석
        fault_features = []
        for sound in self.classification_data['fault_sounds']:
            fault_features.extend(sound['features'])
        
        # 특징 빈도 계산
        normal_feature_count = {}
        for feature in normal_features:
            normal_feature_count[feature] = normal_feature_count.get(feature, 0) + 1
        
        fault_feature_count = {}
        for feature in fault_features:
            fault_feature_count[feature] = fault_feature_count.get(feature, 0) + 1
        
        # 분류 규칙 생성
        rules = {
            'normal_sound_indicators': [],
            'fault_sound_indicators': [],
            'ambiguous_features': []
        }
        
        # 정상 소리 지표
        for feature, count in normal_feature_count.items():
            if count >= 2:  # 2번 이상 나타난 특징
                rules['normal_sound_indicators'].append({
                    'feature': feature,
                    'frequency': count,
                    'confidence': min(1.0, count / len(self.classification_data['normal_sounds']))
                })
        
        # 고장 소리 지표
        for feature, count in fault_feature_count.items():
            if count >= 2:  # 2번 이상 나타난 특징
                rules['fault_sound_indicators'].append({
                    'feature': feature,
                    'frequency': count,
                    'confidence': min(1.0, count / len(self.classification_data['fault_sounds']))
                })
        
        # 모호한 특징 (양쪽 모두 나타남)
        all_features = set(normal_features + fault_features)
        for feature in all_features:
            normal_count = normal_feature_count.get(feature, 0)
            fault_count = fault_feature_count.get(feature, 0)
            if normal_count > 0 and fault_count > 0:
                rules['ambiguous_features'].append({
                    'feature': feature,
                    'normal_frequency': normal_count,
                    'fault_frequency': fault_count
                })
        
        self.classification_data['classification_rules'] = rules
        
        print("   ✅ 분류 규칙 생성 완료")
    
    def _generate_statistics(self):
        """통계 생성"""
        print("\n📊 통계 생성")
        print("-" * 40)
        
        total_sounds = len(self.classification_data['normal_sounds']) + len(self.classification_data['fault_sounds'])
        normal_count = len(self.classification_data['normal_sounds'])
        fault_count = len(self.classification_data['fault_sounds'])
        
        # 신뢰도 통계
        normal_confidence = [sound['confidence'] for sound in self.classification_data['normal_sounds']]
        fault_confidence = [sound['confidence'] for sound in self.classification_data['fault_sounds']]
        
        statistics = {
            'total_sounds': total_sounds,
            'normal_sounds': normal_count,
            'fault_sounds': fault_count,
            'normal_percentage': (normal_count / total_sounds * 100) if total_sounds > 0 else 0,
            'fault_percentage': (fault_count / total_sounds * 100) if total_sounds > 0 else 0,
            'average_normal_confidence': sum(normal_confidence) / len(normal_confidence) if normal_confidence else 0,
            'average_fault_confidence': sum(fault_confidence) / len(fault_confidence) if fault_confidence else 0,
            'total_features': len(set([f for sound in self.classification_data['normal_sounds'] + self.classification_data['fault_sounds'] for f in sound['features']]))
        }
        
        self.classification_data['statistics'] = statistics
        
        print("   ✅ 통계 생성 완료")
    
    def _save_classification_data(self):
        """분류 데이터 저장"""
        try:
            # 결과 디렉토리 생성
            os.makedirs('data/sound_classification', exist_ok=True)
            
            # 파일명 생성
            name = self.classification_data['basic_info']['name']
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"data/sound_classification/{name}_{date_str}.json"
            
            # 결과 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.classification_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 분류 데이터 저장 완료: {filename}")
            
            # 요약 출력
            self._print_summary()
            
        except Exception as e:
            print(f"❌ 저장 오류: {e}")
    
    def _print_summary(self):
        """분류 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📋 소리 분류 결과 요약")
        print("=" * 60)
        
        stats = self.classification_data['statistics']
        print(f"총 분류된 소리: {stats['total_sounds']}개")
        print(f"정상 소리: {stats['normal_sounds']}개 ({stats['normal_percentage']:.1f}%)")
        print(f"고장 소리: {stats['fault_sounds']}개 ({stats['fault_percentage']:.1f}%)")
        print(f"평균 정상 소리 신뢰도: {stats['average_normal_confidence']:.1f}/10")
        print(f"평균 고장 소리 신뢰도: {stats['average_fault_confidence']:.1f}/10")
        print(f"총 특징 수: {stats['total_features']}개")
        
        # 분류 규칙 요약
        rules = self.classification_data['classification_rules']
        print(f"\n🔍 분류 규칙:")
        print(f"정상 소리 지표: {len(rules['normal_sound_indicators'])}개")
        print(f"고장 소리 지표: {len(rules['fault_sound_indicators'])}개")
        print(f"모호한 특징: {len(rules['ambiguous_features'])}개")
        
        # 상위 특징 출력
        if rules['normal_sound_indicators']:
            print(f"\n정상 소리 주요 특징:")
            for indicator in sorted(rules['normal_sound_indicators'], key=lambda x: x['frequency'], reverse=True)[:5]:
                print(f"  - {indicator['feature']}: {indicator['frequency']}회 ({indicator['confidence']:.2f})")
        
        if rules['fault_sound_indicators']:
            print(f"\n고장 소리 주요 특징:")
            for indicator in sorted(rules['fault_sound_indicators'], key=lambda x: x['frequency'], reverse=True)[:5]:
                print(f"  - {indicator['feature']}: {indicator['frequency']}회 ({indicator['confidence']:.2f})")
        
        print(f"\n다음 단계:")
        print("1. 더 많은 소리 분류 (데이터 확장)")
        print("2. 분류 규칙 정제")
        print("3. AI 모델 훈련용 데이터 생성")

def main():
    """메인 함수"""
    print("🎵 간단한 소리 분류기")
    print("=" * 60)
    
    # 분류기 생성
    classifier = SimpleSoundClassifier()
    
    # 분류 시작
    classifier.start_classification()

if __name__ == "__main__":
    main()
