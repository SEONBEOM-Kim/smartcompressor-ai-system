#!/usr/bin/env python3
"""
ESP32 AI 추론 서비스
Node.js에서 호출되는 Python AI 서비스
"""

import sys
import json
import logging
import traceback
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

class AIInferenceService:
    """AI 추론 서비스 클래스"""
    
    def __init__(self):
        self.detector = CompressorAnomalyDetector()
        self.processor = ESP32DataProcessor()
        self.is_initialized = False
        
    def initialize(self):
        """서비스 초기화"""
        try:
            # 기존 모델 로드 시도
            if self.detector.load_model():
                logger.info("기존 이상 탐지 모델 로드 완료")
                self.is_initialized = True
            else:
                logger.warning("기존 모델이 없습니다. 새로 학습이 필요합니다.")
                # 자동 학습 시도
                self._auto_train()
                
        except Exception as e:
            logger.error(f"서비스 초기화 실패: {e}")
            self.is_initialized = False
    
    def _auto_train(self):
        """자동 학습 (정상 데이터가 있는 경우)"""
        try:
            logger.info("자동 학습 시작")
            
            # 정상 데이터 수집 (최근 24시간)
            normal_data = self.processor.collect_normal_data(hours=24)
            
            if len(normal_data) >= 10:
                # 모델 학습
                result = self.detector.train(normal_data)
                
                if result.get('success', False):
                    logger.info("자동 학습 완료")
                    self.is_initialized = True
                else:
                    logger.error(f"자동 학습 실패: {result.get('error', 'Unknown error')}")
            else:
                logger.warning(f"학습용 데이터 부족: {len(normal_data)}개 (최소 10개 필요)")
                
        except Exception as e:
            logger.error(f"자동 학습 중 오류: {e}")
    
    def analyze_single(self, sensor_data):
        """단일 센서 데이터 분석"""
        try:
            if not self.is_initialized:
                return {
                    "success": False,
                    "error": "AI 서비스가 초기화되지 않았습니다.",
                    "is_anomaly": False,
                    "anomaly_score": 0.0,
                    "confidence": 0.0
                }
            
            # 이상 탐지 수행
            result = self.detector.predict(sensor_data)
            
            # 추가 분석 정보
            result["analysis_type"] = "anomaly_detection"
            result["model_version"] = "1.0"
            result["analyzed_at"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"단일 데이터 분석 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "confidence": 0.0
            }
    
    def analyze_batch(self, sensor_data_list, device_id=None):
        """배치 센서 데이터 분석"""
        try:
            if not self.is_initialized:
                return {
                    "success": False,
                    "error": "AI 서비스가 초기화되지 않았습니다.",
                    "results": []
                }
            
            # 배치 이상 탐지 수행
            results = self.detector.predict_batch(sensor_data_list)
            
            # 결과에 추가 정보 추가
            for i, result in enumerate(results):
                if result.get("success", True):  # 오류가 없는 경우만
                    result["analysis_type"] = "anomaly_detection"
                    result["model_version"] = "1.0"
                    result["analyzed_at"] = datetime.now().isoformat()
                    result["device_id"] = device_id or sensor_data_list[i].get("device_id", "unknown")
            
            return {
                "success": True,
                "results": results,
                "total_samples": len(sensor_data_list),
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"배치 데이터 분석 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }

def main():
    """메인 함수 - Node.js에서 호출됨"""
    try:
        # 입력 데이터 읽기
        input_data = json.loads(sys.stdin.read())
        
        # AI 서비스 초기화
        ai_service = AIInferenceService()
        ai_service.initialize()
        
        # 분석 모드 확인
        if input_data.get("mode") == "batch":
            # 배치 분석
            sensor_data_list = input_data.get("sensor_data_list", [])
            device_id = input_data.get("device_id")
            
            result = ai_service.analyze_batch(sensor_data_list, device_id)
            
        else:
            # 단일 분석
            sensor_data = input_data
            result = ai_service.analyze_single(sensor_data)
        
        # 결과 출력 (JSON)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        logger.error(f"AI 추론 서비스 오류: {e}")
        logger.error(traceback.format_exc())
        
        # 오류 결과 출력
        error_result = {
            "success": False,
            "error": str(e),
            "is_anomaly": False,
            "anomaly_score": 0.0,
            "confidence": 0.0
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
