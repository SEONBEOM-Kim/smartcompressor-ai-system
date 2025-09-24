#!/usr/bin/env python3
"""
실시간 진단 스크립트 (run_diagnosis.py)
새로운 오디오 파일을 분석하여 AI 진단을 수행합니다.
"""

import os
import sys
import numpy as np
import tensorflow as tf
from pathlib import Path
import argparse
import logging
from datetime import datetime
import json

# 로컬 모듈 임포트
from preprocessor import AudioPreprocessor

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiagnosisEngine:
    """실시간 진단 엔진"""
    
    def __init__(self, model_path="models/model.h5", class_info_path="models/class_info.txt"):
        """
        Args:
            model_path (str): 훈련된 모델 파일 경로
            class_info_path (str): 클래스 정보 파일 경로
        """
        self.model_path = model_path
        self.class_info_path = class_info_path
        self.model = None
        self.class_names = None
        self.preprocessor = AudioPreprocessor()
        
        # 클래스 매핑 (기본값)
        self.class_mapping = {
            0: "정상 가동음",
            1: "냉기 누설 신호", 
            2: "과부하 신호"
        }
    
    def load_model(self):
        """훈련된 모델을 로드합니다."""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {self.model_path}")
            
            logger.info(f"모델 로딩 중: {self.model_path}")
            self.model = tf.keras.models.load_model(self.model_path)
            
            # 클래스 정보 로드
            self._load_class_info()
            
            logger.info("모델 로드 완료")
            logger.info(f"클래스: {list(self.class_mapping.values())}")
            
        except Exception as e:
            logger.error(f"모델 로드 중 오류 발생: {e}")
            raise
    
    def _load_class_info(self):
        """클래스 정보를 로드합니다."""
        try:
            if os.path.exists(self.class_info_path):
                with open(self.class_info_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 클래스 매핑 업데이트
                for line in lines[1:]:  # 첫 번째 줄은 헤더
                    if ':' in line:
                        idx, class_name = line.strip().split(': ', 1)
                        self.class_mapping[int(idx)] = class_name
                
                logger.info(f"클래스 정보 로드: {self.class_mapping}")
            else:
                logger.warning(f"클래스 정보 파일을 찾을 수 없습니다: {self.class_info_path}")
                logger.info("기본 클래스 매핑을 사용합니다.")
                
        except Exception as e:
            logger.warning(f"클래스 정보 로드 실패: {e}")
    
    def preprocess_audio(self, target_audio_path, noise_audio_path, temp_dir="temp"):
        """
        오디오를 전처리하고 스펙트로그램을 생성합니다.
        
        Args:
            target_audio_path (str): 타겟 오디오 파일 경로
            noise_audio_path (str): 노이즈 오디오 파일 경로
            temp_dir (str): 임시 파일 저장 디렉토리
            
        Returns:
            str: 생성된 스펙트로그램 이미지 경로
        """
        try:
            # 임시 디렉토리 생성
            os.makedirs(temp_dir, exist_ok=True)
            
            # 1. 노이즈 제거
            logger.info("노이즈 제거 수행 중...")
            clean_audio_path = self.preprocessor.noise_cancel(
                target_audio_path, noise_audio_path, temp_dir
            )
            
            # 2. 스펙트로그램 생성
            logger.info("스펙트로그램 생성 중...")
            spectrogram_path = self.preprocessor.create_spectrogram(
                clean_audio_path, temp_dir
            )
            
            logger.info(f"전처리 완료: {spectrogram_path}")
            return spectrogram_path
            
        except Exception as e:
            logger.error(f"오디오 전처리 중 오류 발생: {e}")
            raise
    
    def predict(self, spectrogram_path):
        """
        스펙트로그램을 분석하여 진단을 수행합니다.
        
        Args:
            spectrogram_path (str): 스펙트로그램 이미지 파일 경로
            
        Returns:
            tuple: (predicted_class, confidence, all_probabilities)
        """
        try:
            if self.model is None:
                raise ValueError("모델이 로드되지 않았습니다. load_model()을 먼저 호출하세요.")
            
            # 이미지 로드 및 전처리
            img = tf.keras.preprocessing.image.load_img(
                spectrogram_path, 
                target_size=(256, 256),
                color_mode='rgb'
            )
            img_array = tf.keras.preprocessing.image.img_to_array(img)
            img_array = img_array / 255.0  # 정규화
            img_array = np.expand_dims(img_array, axis=0)  # 배치 차원 추가
            
            # 예측 수행
            predictions = self.model.predict(img_array, verbose=0)
            probabilities = predictions[0]
            
            # 가장 높은 확률의 클래스 찾기
            predicted_class_idx = np.argmax(probabilities)
            confidence = probabilities[predicted_class_idx]
            
            # 클래스 이름 변환
            predicted_class = self.class_mapping.get(predicted_class_idx, f"Unknown_{predicted_class_idx}")
            
            logger.info(f"진단 완료: {predicted_class} (신뢰도: {confidence:.4f})")
            
            return predicted_class, confidence, probabilities
            
        except Exception as e:
            logger.error(f"예측 중 오류 발생: {e}")
            raise
    
    def diagnose(self, target_audio_path, noise_audio_path, output_dir="diagnosis_results"):
        """
        전체 진단 프로세스를 수행합니다.
        
        Args:
            target_audio_path (str): 타겟 오디오 파일 경로
            noise_audio_path (str): 노이즈 오디오 파일 경로
            output_dir (str): 결과 저장 디렉토리
            
        Returns:
            dict: 진단 결과
        """
        try:
            # 출력 디렉토리 생성
            os.makedirs(output_dir, exist_ok=True)
            
            # 1. 오디오 전처리
            logger.info("=== 1단계: 오디오 전처리 ===")
            spectrogram_path = self.preprocess_audio(target_audio_path, noise_audio_path)
            
            # 2. AI 진단
            logger.info("=== 2단계: AI 진단 ===")
            predicted_class, confidence, all_probabilities = self.predict(spectrogram_path)
            
            # 3. 결과 정리
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 모든 클래스별 확률 계산
            class_probabilities = {}
            for idx, class_name in self.class_mapping.items():
                if idx < len(all_probabilities):
                    class_probabilities[class_name] = float(all_probabilities[idx])
            
            # 진단 결과
            diagnosis_result = {
                "timestamp": timestamp,
                "input_files": {
                    "target_audio": target_audio_path,
                    "noise_audio": noise_audio_path
                },
                "preprocessing": {
                    "spectrogram_path": spectrogram_path
                },
                "diagnosis": {
                    "predicted_class": predicted_class,
                    "confidence": float(confidence),
                    "all_probabilities": class_probabilities
                },
                "status": "정상" if predicted_class == "정상 가동음" else "이상"
            }
            
            # 결과 저장
            result_file = os.path.join(output_dir, f"diagnosis_result_{timestamp}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(diagnosis_result, f, ensure_ascii=False, indent=2)
            
            # 스펙트로그램을 결과 디렉토리로 복사
            result_spectrogram = os.path.join(output_dir, f"spectrogram_{timestamp}.png")
            import shutil
            shutil.copy2(spectrogram_path, result_spectrogram)
            diagnosis_result["preprocessing"]["spectrogram_path"] = result_spectrogram
            
            logger.info(f"진단 결과 저장: {result_file}")
            
            return diagnosis_result
            
        except Exception as e:
            logger.error(f"진단 중 오류 발생: {e}")
            raise
    
    def print_diagnosis_report(self, diagnosis_result):
        """진단 결과를 콘솔에 출력합니다."""
        try:
            print("\n" + "="*60)
            print("🔍 AI 오디오 진단 결과")
            print("="*60)
            
            # 기본 정보
            print(f"📅 진단 시간: {diagnosis_result['timestamp']}")
            print(f"📁 타겟 오디오: {diagnosis_result['input_files']['target_audio']}")
            print(f"📁 노이즈 오디오: {diagnosis_result['input_files']['noise_audio']}")
            
            # 진단 결과
            predicted_class = diagnosis_result['diagnosis']['predicted_class']
            confidence = diagnosis_result['diagnosis']['confidence']
            status = diagnosis_result['status']
            
            print(f"\n🎯 진단 결과:")
            print(f"   상태: {status}")
            print(f"   분류: {predicted_class}")
            print(f"   신뢰도: {confidence:.2%}")
            
            # 모든 클래스별 확률
            print(f"\n📊 모든 클래스별 확률:")
            all_probabilities = diagnosis_result['diagnosis']['all_probabilities']
            for class_name, prob in sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True):
                bar_length = int(prob * 20)  # 20자 길이의 바
                bar = "█" * bar_length + "░" * (20 - bar_length)
                print(f"   {class_name:15s}: {prob:.2%} {bar}")
            
            # 권장사항
            print(f"\n💡 권장사항:")
            if predicted_class == "정상 가동음":
                print("   ✅ 압축기가 정상적으로 작동하고 있습니다.")
                print("   📋 정기적인 점검을 계속 진행하세요.")
            elif predicted_class == "냉기 누설 신호":
                print("   ⚠️ 냉매 누설이 의심됩니다.")
                print("   🔧 즉시 전문가에게 점검을 요청하세요.")
                print("   🚨 안전을 위해 압축기를 중단하는 것을 고려하세요.")
            elif predicted_class == "과부하 신호":
                print("   🚨 과부하 상태가 감지되었습니다.")
                print("   ⚡ 전기 시스템을 점검하세요.")
                print("   🔧 부하를 줄이거나 전문가에게 문의하세요.")
            
            print("="*60)
            
        except Exception as e:
            logger.error(f"진단 보고서 출력 중 오류 발생: {e}")

def main():
    """메인 함수 - CLI 인터페이스"""
    parser = argparse.ArgumentParser(description='AI 오디오 진단 도구')
    parser.add_argument('--target', required=True, help='타겟 오디오 파일 경로')
    parser.add_argument('--noise', required=True, help='노이즈 오디오 파일 경로')
    parser.add_argument('--model', default='models/model.h5', help='훈련된 모델 파일 경로')
    parser.add_argument('--output', default='diagnosis_results', help='결과 저장 디렉토리')
    parser.add_argument('--verbose', action='store_true', help='상세 로그 출력')
    
    args = parser.parse_args()
    
    # 로깅 레벨 설정
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 파일 존재 확인
    if not os.path.exists(args.target):
        logger.error(f"타겟 오디오 파일을 찾을 수 없습니다: {args.target}")
        return
    
    if not os.path.exists(args.noise):
        logger.error(f"노이즈 오디오 파일을 찾을 수 없습니다: {args.noise}")
        return
    
    if not os.path.exists(args.model):
        logger.error(f"모델 파일을 찾을 수 없습니다: {args.model}")
        logger.error("먼저 train_ai.py를 실행하여 모델을 훈련하세요.")
        return
    
    try:
        # 진단 엔진 초기화
        diagnosis_engine = DiagnosisEngine(model_path=args.model)
        
        # 모델 로드
        logger.info("모델 로딩 중...")
        diagnosis_engine.load_model()
        
        # 진단 수행
        logger.info("진단 시작...")
        diagnosis_result = diagnosis_engine.diagnose(
            args.target, args.noise, args.output
        )
        
        # 결과 출력
        diagnosis_engine.print_diagnosis_report(diagnosis_result)
        
        print(f"\n✅ 진단 완료!")
        print(f"📁 결과 저장 위치: {args.output}/")
        
    except Exception as e:
        logger.error(f"진단 실패: {e}")
        return

if __name__ == "__main__":
    main()
