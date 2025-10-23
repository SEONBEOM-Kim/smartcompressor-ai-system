#!/usr/bin/env python3
"""
ESP32 AI 학습 서비스
모델 재학습을 위한 Python 서비스
"""

import sys
import json
import logging
import argparse
from datetime import datetime
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.anomaly_detector import CompressorAnomalyDetector
from services.esp32_data_processor import ESP32DataProcessor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AITrainingService:
    """AI 학습 서비스 클래스"""
    
    def __init__(self):
        self.detector = CompressorAnomalyDetector()
        self.processor = ESP32DataProcessor()
    
    def train_model(self, hours=24, device_id=None, contamination=0.1):
        """모델 학습"""
        try:
            logger.info(f"AI 모델 학습 시작 - {hours}시간, 디바이스: {device_id}")
            
            # 정상 데이터 수집
            normal_data = self.processor.collect_normal_data(hours=hours, device_id=device_id)
            
            if len(normal_data) < 10:
                return {
                    "success": False,
                    "error": f"학습용 데이터 부족: {len(normal_data)}개 (최소 10개 필요)",
                    "n_samples": len(normal_data)
                }
            
            # 데이터 요약 정보
            data_summary = self.processor.get_data_summary(normal_data)
            logger.info(f"수집된 데이터 요약: {data_summary}")
            
            # 모델 학습
            training_result = self.detector.train(normal_data, contamination=contamination)
            
            if training_result.get("success", False):
                # 모델 정보 조회
                model_info = self.detector.get_model_info()
                
                logger.info("AI 모델 학습 완료")
                
                return {
                    "success": True,
                    "message": "AI 모델 학습이 성공적으로 완료되었습니다.",
                    "training_result": training_result,
                    "model_info": model_info,
                    "data_summary": data_summary,
                    "trained_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": training_result.get("error", "모델 학습 실패"),
                    "training_result": training_result
                }
                
        except Exception as e:
            logger.error(f"모델 학습 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def evaluate_model(self, hours=24, device_id=None):
        """모델 성능 평가"""
        try:
            logger.info(f"모델 성능 평가 시작 - {hours}시간, 디바이스: {device_id}")
            
            # 기존 모델 로드
            if not self.detector.load_model():
                return {
                    "success": False,
                    "error": "평가할 모델이 없습니다. 먼저 모델을 학습하세요."
                }
            
            # 테스트 데이터 수집
            test_data = self.processor.collect_normal_data(hours=hours, device_id=device_id)
            
            if len(test_data) < 5:
                return {
                    "success": False,
                    "error": f"평가용 데이터 부족: {len(test_data)}개 (최소 5개 필요)"
                }
            
            # 모델 평가
            evaluation_result = self.detector.evaluate_model(test_data)
            
            logger.info("모델 성능 평가 완료")
            
            return {
                "success": True,
                "evaluation_result": evaluation_result,
                "test_samples": len(test_data),
                "evaluated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"모델 평가 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_model_status(self):
        """모델 상태 조회"""
        try:
            # 모델 정보 조회
            model_info = self.detector.get_model_info()
            
            # 데이터 상태 조회
            normal_data = self.processor.collect_normal_data(hours=24)
            data_summary = self.processor.get_data_summary(normal_data)
            
            return {
                "success": True,
                "model_info": model_info,
                "data_status": {
                    "available_data": len(normal_data),
                    "data_summary": data_summary
                },
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"모델 상태 조회 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='ESP32 AI 학습 서비스')
    parser.add_argument('--mode', choices=['train', 'evaluate', 'status'], default='train',
                       help='실행 모드 (기본값: train)')
    parser.add_argument('--hours', type=int, default=24,
                       help='데이터 수집 시간 범위 (기본값: 24)')
    parser.add_argument('--device-id', type=str, default=None,
                       help='특정 디바이스 ID (기본값: 모든 디바이스)')
    parser.add_argument('--contamination', type=float, default=0.1,
                       help='이상치 비율 (기본값: 0.1)')
    
    args = parser.parse_args()
    
    # AI 학습 서비스 초기화
    training_service = AITrainingService()
    
    try:
        if args.mode == 'train':
            # 모델 학습
            result = training_service.train_model(
                hours=args.hours,
                device_id=args.device_id,
                contamination=args.contamination
            )
            
        elif args.mode == 'evaluate':
            # 모델 평가
            result = training_service.evaluate_model(
                hours=args.hours,
                device_id=args.device_id
            )
            
        elif args.mode == 'status':
            # 모델 상태 조회
            result = training_service.get_model_status()
        
        # 결과 출력 (JSON)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"AI 학습 서비스 오류: {e}")
        
        error_result = {
            "success": False,
            "error": str(e),
            "mode": args.mode
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
