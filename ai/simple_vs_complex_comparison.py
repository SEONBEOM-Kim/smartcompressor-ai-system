#!/usr/bin/env python3
"""
간단한 공식 vs 복잡한 AI 성능 비교
실제 데이터로 간단한 규칙 기반 방법이 복잡한 AI보다 나은지 검증
"""

import numpy as np
import librosa
import time
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report
from typing import Dict, List, Tuple
warnings.filterwarnings('ignore')

class SimpleVsComplexComparison:
    """간단한 공식 vs 복잡한 AI 성능 비교"""
    
    def __init__(self):
        self.simple_rules = {}
        self.complex_models = {}
        self.performance_results = {}
        
        print("🔍 간단한 공식 vs 복잡한 AI 성능 비교 시작")
    
    # ===== 1. 간단한 규칙 기반 방법 =====
    
    def create_simple_rules(self) -> Dict:
        """간단한 규칙 기반 진단 시스템 생성"""
        rules = {
            'rms_threshold': 0.1,
            'zcr_threshold': 0.15,
            'spectral_centroid_threshold': 2000,
            'spectral_rolloff_threshold': 0.4,
            'spectral_bandwidth_threshold': 500
        }
        
        self.simple_rules = rules
        print("✅ 간단한 규칙 기반 시스템 생성 완료")
        return rules
    
    def simple_diagnosis(self, audio_data: np.ndarray, sr: int) -> Dict:
        """간단한 규칙 기반 진단"""
        try:
            start_time = time.time()
            
            # 기본 특징 추출
            rms = np.sqrt(np.mean(audio_data ** 2))
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr))
            spectral_bandwidth = np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sr))
            
            # 규칙 기반 판단
            anomaly_score = 0
            reasons = []
            
            # RMS 규칙
            if rms > self.simple_rules['rms_threshold']:
                anomaly_score += 1
                reasons.append(f"RMS 높음: {rms:.3f} > {self.simple_rules['rms_threshold']}")
            
            # ZCR 규칙
            if zcr > self.simple_rules['zcr_threshold']:
                anomaly_score += 1
                reasons.append(f"ZCR 높음: {zcr:.3f} > {self.simple_rules['zcr_threshold']}")
            
            # Spectral Centroid 규칙
            if spectral_centroid > self.simple_rules['spectral_centroid_threshold']:
                anomaly_score += 1
                reasons.append(f"Spectral Centroid 높음: {spectral_centroid:.1f} > {self.simple_rules['spectral_centroid_threshold']}")
            
            # Spectral Rolloff 규칙
            if spectral_rolloff > self.simple_rules['spectral_rolloff_threshold']:
                anomaly_score += 1
                reasons.append(f"Spectral Rolloff 높음: {spectral_rolloff:.3f} > {self.simple_rules['spectral_rolloff_threshold']}")
            
            # Spectral Bandwidth 규칙
            if spectral_bandwidth > self.simple_rules['spectral_bandwidth_threshold']:
                anomaly_score += 1
                reasons.append(f"Spectral Bandwidth 높음: {spectral_bandwidth:.1f} > {self.simple_rules['spectral_bandwidth_threshold']}")
            
            # 최종 판단
            if anomaly_score >= 3:  # 3개 이상의 규칙에 해당하면 이상
                prediction = 1  # 이상
                confidence = min(0.9, 0.5 + (anomaly_score * 0.1))
            else:
                prediction = 0  # 정상
                confidence = min(0.9, 0.5 + ((5 - anomaly_score) * 0.1))
            
            processing_time = time.time() - start_time
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'anomaly_score': anomaly_score,
                'reasons': reasons,
                'features': {
                    'rms': rms,
                    'zcr': zcr,
                    'spectral_centroid': spectral_centroid,
                    'spectral_rolloff': spectral_rolloff,
                    'spectral_bandwidth': spectral_bandwidth
                },
                'processing_time': processing_time,
                'method': 'simple_rules'
            }
            
        except Exception as e:
            print(f"⚠️ 간단한 진단 중 오류: {e}")
            return {
                'prediction': 0,
                'confidence': 0.0,
                'anomaly_score': 0,
                'reasons': [],
                'features': {},
                'processing_time': 0.0,
                'method': 'simple_rules',
                'error': str(e)
            }
    
    # ===== 2. 복잡한 AI 방법 =====
    
    def create_complex_models(self) -> Dict:
        """복잡한 AI 모델들 생성"""
        models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=2,
                min_samples_leaf=1,
                random_state=42
            ),
            'neural_network': MLPClassifier(
                hidden_layer_sizes=(100, 50, 25),
                activation='relu',
                solver='adam',
                alpha=0.001,
                learning_rate='adaptive',
                max_iter=1000,
                random_state=42
            )
        }
        
        self.complex_models = models
        print("✅ 복잡한 AI 모델들 생성 완료")
        return models
    
    def extract_complex_features(self, audio_data: np.ndarray, sr: int) -> np.ndarray:
        """복잡한 특징 추출"""
        try:
            features = []
            
            # 기본 특징들
            features.append(np.sqrt(np.mean(audio_data ** 2)))  # RMS
            features.append(np.mean(librosa.feature.zero_crossing_rate(audio_data)))  # ZCR
            features.append(np.mean(librosa.feature.spectral_centroid(y=audio_data, sr=sr)))  # Spectral Centroid
            features.append(np.mean(librosa.feature.spectral_rolloff(y=audio_data, sr=sr)))  # Spectral Rolloff
            features.append(np.mean(librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)))  # Spectral Bandwidth
            
            # MFCC (13개 계수)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
            features.extend(np.mean(mfccs, axis=1))
            features.extend(np.std(mfccs, axis=1))
            
            # Chroma (12개 계수)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
            features.extend(np.mean(chroma, axis=1))
            features.extend(np.std(chroma, axis=1))
            
            # Spectral Contrast (7개 계수)
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
            features.extend(np.mean(contrast, axis=1))
            features.extend(np.std(contrast, axis=1))
            
            # Tonnetz (6개 계수)
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sr)
            features.extend(np.mean(tonnetz, axis=1))
            
            # Poly Features (2개 계수)
            poly_features = librosa.feature.poly_features(y=audio_data, sr=sr)
            features.extend(np.mean(poly_features, axis=1))
            
            # Zero Crossing Rate (고급)
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            features.append(np.mean(zcr))
            features.append(np.std(zcr))
            
            # Spectral Flatness
            flatness = librosa.feature.spectral_flatness(y=audio_data)
            features.append(np.mean(flatness))
            features.append(np.std(flatness))
            
            # Tempo
            try:
                tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)
                features.append(tempo if tempo is not None else 0.0)
            except:
                features.append(0.0)
            
            return np.array(features)
            
        except Exception as e:
            print(f"⚠️ 복잡한 특징 추출 중 오류: {e}")
            return np.zeros(50)  # 기본값
    
    def complex_diagnosis(self, audio_data: np.ndarray, sr: int, model_name: str = 'random_forest') -> Dict:
        """복잡한 AI 진단"""
        try:
            start_time = time.time()
            
            # 복잡한 특징 추출
            features = self.extract_complex_features(audio_data, sr)
            
            # 모델 예측
            if model_name in self.complex_models:
                model = self.complex_models[model_name]
                
                # 예측 수행
                prediction = model.predict([features])[0]
                
                # 신뢰도 계산 (확률 기반)
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba([features])[0]
                    confidence = np.max(proba)
                else:
                    confidence = 0.5  # 기본값
                
                processing_time = time.time() - start_time
                
                return {
                    'prediction': prediction,
                    'confidence': confidence,
                    'features': features,
                    'processing_time': processing_time,
                    'method': f'complex_{model_name}',
                    'feature_count': len(features)
                }
            else:
                raise ValueError(f"모델 {model_name}을 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"⚠️ 복잡한 진단 중 오류: {e}")
            return {
                'prediction': 0,
                'confidence': 0.0,
                'features': np.zeros(50),
                'processing_time': 0.0,
                'method': f'complex_{model_name}',
                'error': str(e)
            }
    
    # ===== 3. 성능 비교 =====
    
    def compare_performance(self, audio_files: List[str], labels: List[int]) -> Dict:
        """성능 비교 실행"""
        try:
            print("🔍 성능 비교 시작")
            
            # 간단한 규칙 기반 시스템 생성
            self.create_simple_rules()
            
            # 복잡한 AI 모델들 생성
            self.create_complex_models()
            
            # 테스트 데이터 준비
            X_simple = []
            X_complex = []
            y_true = []
            
            for audio_file, label in zip(audio_files, labels):
                try:
                    audio_data, sr = librosa.load(audio_file, sr=16000)
                    
                    # 간단한 특징 (규칙 기반에서 사용)
                    simple_features = self.simple_diagnosis(audio_data, sr)['features']
                    X_simple.append(simple_features)
                    
                    # 복잡한 특징 (AI 모델에서 사용)
                    complex_features = self.extract_complex_features(audio_data, sr)
                    X_complex.append(complex_features)
                    
                    y_true.append(label)
                    
                except Exception as e:
                    print(f"⚠️ 파일 처리 오류 {audio_file}: {e}")
                    continue
            
            X_simple = np.array(X_simple)
            X_complex = np.array(X_complex)
            y_true = np.array(y_true)
            
            # 복잡한 모델들 훈련
            for name, model in self.complex_models.items():
                try:
                    model.fit(X_complex, y_true)
                    print(f"✅ {name} 모델 훈련 완료")
                except Exception as e:
                    print(f"❌ {name} 모델 훈련 실패: {e}")
            
            # 성능 테스트
            results = {}
            
            # 1. 간단한 규칙 기반 테스트
            print("1️⃣ 간단한 규칙 기반 테스트")
            simple_results = self._test_simple_rules(audio_files, y_true)
            results['simple_rules'] = simple_results
            
            # 2. 복잡한 AI 모델들 테스트
            for name, model in self.complex_models.items():
                print(f"2️⃣ {name} 모델 테스트")
                complex_results = self._test_complex_model(audio_files, y_true, name)
                results[f'complex_{name}'] = complex_results
            
            # 3. 결과 비교
            comparison = self._compare_results(results)
            
            self.performance_results = {
                'individual_results': results,
                'comparison': comparison,
                'test_data_count': len(audio_files)
            }
            
            print("✅ 성능 비교 완료")
            return self.performance_results
            
        except Exception as e:
            print(f"❌ 성능 비교 중 오류: {e}")
            return {'error': str(e)}
    
    def _test_simple_rules(self, audio_files: List[str], y_true: List[int]) -> Dict:
        """간단한 규칙 기반 테스트"""
        try:
            predictions = []
            confidences = []
            processing_times = []
            
            for audio_file in audio_files:
                try:
                    audio_data, sr = librosa.load(audio_file, sr=16000)
                    result = self.simple_diagnosis(audio_data, sr)
                    
                    predictions.append(result['prediction'])
                    confidences.append(result['confidence'])
                    processing_times.append(result['processing_time'])
                    
                except Exception as e:
                    print(f"⚠️ 간단한 규칙 테스트 오류 {audio_file}: {e}")
                    predictions.append(0)
                    confidences.append(0.0)
                    processing_times.append(0.0)
            
            accuracy = accuracy_score(y_true, predictions)
            avg_confidence = np.mean(confidences)
            avg_processing_time = np.mean(processing_times)
            
            return {
                'accuracy': accuracy,
                'avg_confidence': avg_confidence,
                'avg_processing_time': avg_processing_time,
                'predictions': predictions,
                'confidences': confidences,
                'processing_times': processing_times
            }
            
        except Exception as e:
            print(f"⚠️ 간단한 규칙 테스트 중 오류: {e}")
            return {
                'accuracy': 0.0,
                'avg_confidence': 0.0,
                'avg_processing_time': 0.0,
                'error': str(e)
            }
    
    def _test_complex_model(self, audio_files: List[str], y_true: List[int], model_name: str) -> Dict:
        """복잡한 AI 모델 테스트"""
        try:
            predictions = []
            confidences = []
            processing_times = []
            
            for audio_file in audio_files:
                try:
                    audio_data, sr = librosa.load(audio_file, sr=16000)
                    result = self.complex_diagnosis(audio_data, sr, model_name)
                    
                    predictions.append(result['prediction'])
                    confidences.append(result['confidence'])
                    processing_times.append(result['processing_time'])
                    
                except Exception as e:
                    print(f"⚠️ 복잡한 모델 테스트 오류 {audio_file}: {e}")
                    predictions.append(0)
                    confidences.append(0.0)
                    processing_times.append(0.0)
            
            accuracy = accuracy_score(y_true, predictions)
            avg_confidence = np.mean(confidences)
            avg_processing_time = np.mean(processing_times)
            
            return {
                'accuracy': accuracy,
                'avg_confidence': avg_confidence,
                'avg_processing_time': avg_processing_time,
                'predictions': predictions,
                'confidences': confidences,
                'processing_times': processing_times
            }
            
        except Exception as e:
            print(f"⚠️ 복잡한 모델 테스트 중 오류: {e}")
            return {
                'accuracy': 0.0,
                'avg_confidence': 0.0,
                'avg_processing_time': 0.0,
                'error': str(e)
            }
    
    def _compare_results(self, results: Dict) -> Dict:
        """결과 비교"""
        try:
            comparison = {
                'accuracy_ranking': [],
                'speed_ranking': [],
                'confidence_ranking': [],
                'summary': {}
            }
            
            # 정확도 순위
            accuracy_scores = [(name, result['accuracy']) for name, result in results.items()]
            accuracy_scores.sort(key=lambda x: x[1], reverse=True)
            comparison['accuracy_ranking'] = accuracy_scores
            
            # 속도 순위 (빠른 순)
            speed_scores = [(name, result['avg_processing_time']) for name, result in results.items()]
            speed_scores.sort(key=lambda x: x[1])
            comparison['speed_ranking'] = speed_scores
            
            # 신뢰도 순위
            confidence_scores = [(name, result['avg_confidence']) for name, result in results.items()]
            confidence_scores.sort(key=lambda x: x[1], reverse=True)
            comparison['confidence_ranking'] = confidence_scores
            
            # 요약
            best_accuracy = accuracy_scores[0]
            fastest = speed_scores[0]
            most_confident = confidence_scores[0]
            
            comparison['summary'] = {
                'best_accuracy': best_accuracy,
                'fastest': fastest,
                'most_confident': most_confident,
                'simple_vs_complex': {
                    'simple_accuracy': results.get('simple_rules', {}).get('accuracy', 0),
                    'complex_accuracy': max([result.get('accuracy', 0) for name, result in results.items() if 'complex' in name]),
                    'simple_speed': results.get('simple_rules', {}).get('avg_processing_time', 0),
                    'complex_speed': min([result.get('avg_processing_time', float('inf')) for name, result in results.items() if 'complex' in name])
                }
            }
            
            return comparison
            
        except Exception as e:
            print(f"⚠️ 결과 비교 중 오류: {e}")
            return {'error': str(e)}
    
    def print_comparison_results(self):
        """비교 결과 출력"""
        if not self.performance_results:
            print("❌ 비교 결과가 없습니다.")
            return
        
        print("\n" + "=" * 60)
        print("📊 간단한 공식 vs 복잡한 AI 성능 비교 결과")
        print("=" * 60)
        
        comparison = self.performance_results['comparison']
        
        # 정확도 순위
        print("\n🏆 정확도 순위:")
        for i, (name, accuracy) in enumerate(comparison['accuracy_ranking'], 1):
            print(f"   {i}. {name}: {accuracy:.3f}")
        
        # 속도 순위
        print("\n⚡ 속도 순위 (빠른 순):")
        for i, (name, speed) in enumerate(comparison['speed_ranking'], 1):
            print(f"   {i}. {name}: {speed*1000:.1f}ms")
        
        # 신뢰도 순위
        print("\n🎯 신뢰도 순위:")
        for i, (name, confidence) in enumerate(comparison['confidence_ranking'], 1):
            print(f"   {i}. {name}: {confidence:.3f}")
        
        # 요약
        summary = comparison['summary']
        print("\n📋 요약:")
        print(f"   최고 정확도: {summary['best_accuracy'][0]} ({summary['best_accuracy'][1]:.3f})")
        print(f"   가장 빠름: {summary['fastest'][0]} ({summary['fastest'][1]*1000:.1f}ms)")
        print(f"   가장 신뢰도 높음: {summary['most_confident'][0]} ({summary['most_confident'][1]:.3f})")
        
        # 간단한 vs 복잡한 비교
        simple_vs_complex = summary['simple_vs_complex']
        print("\n🔍 간단한 vs 복잡한 비교:")
        print(f"   간단한 공식 정확도: {simple_vs_complex['simple_accuracy']:.3f}")
        print(f"   복잡한 AI 정확도: {simple_vs_complex['complex_accuracy']:.3f}")
        print(f"   간단한 공식 속도: {simple_vs_complex['simple_speed']*1000:.1f}ms")
        print(f"   복잡한 AI 속도: {simple_vs_complex['complex_speed']*1000:.1f}ms")
        
        # 결론
        if simple_vs_complex['simple_accuracy'] >= simple_vs_complex['complex_accuracy']:
            print("\n🎉 결론: 간단한 공식이 더 나은 성능을 보입니다!")
        else:
            print("\n🤔 결론: 복잡한 AI가 더 나은 성능을 보입니다.")

# 사용 예제
if __name__ == "__main__":
    # 간단한 vs 복잡한 AI 성능 비교 테스트
    comparator = SimpleVsComplexComparison()
    
    print("🔍 간단한 공식 vs 복잡한 AI 성능 비교 테스트")
    print("=" * 60)
    
    # 가상의 테스트 데이터
    test_audio_files = ["test1.wav", "test2.wav", "test3.wav", "test4.wav", "test5.wav"]
    test_labels = [0, 1, 0, 1, 0]  # 0: 정상, 1: 이상
    
    # 성능 비교 실행
    results = comparator.compare_performance(test_audio_files, test_labels)
    
    if 'error' not in results:
        # 결과 출력
        comparator.print_comparison_results()
    else:
        print(f"❌ 성능 비교 실패: {results['error']}")
