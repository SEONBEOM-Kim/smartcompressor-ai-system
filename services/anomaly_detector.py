"""
ESP32 센서 데이터 기반 압축기 이상 탐지 모델
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class CompressorAnomalyDetector:
    """압축기 이상 탐지 모델 클래스"""
    
    def __init__(self, model_dir: str = "data/ai_models"):
        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.feature_names = []
        self.training_stats = {}
        
        # 모델 하이퍼파라미터
        self.contamination = 0.1  # 10% 이상치 허용
        self.random_state = 42
        
        # 모델 파일 경로
        self.model_path = os.path.join(model_dir, "anomaly_detector.pkl")
        self.scaler_path = os.path.join(model_dir, "anomaly_scaler.pkl")
        self.config_path = os.path.join(model_dir, "model_config.json")
        
        # 모델 디렉토리 생성
        os.makedirs(model_dir, exist_ok=True)
    
    def train(self, normal_data: List[Dict], contamination: float = 0.1) -> Dict:
        """
        정상 데이터로 이상 탐지 모델 학습
        
        Args:
            normal_data: 정상 센서 데이터 리스트
            contamination: 이상치 비율 (0.0 ~ 0.5)
            
        Returns:
            학습 결과 딕셔너리
        """
        try:
            logger.info(f"이상 탐지 모델 학습 시작 - {len(normal_data)}개 정상 데이터")
            
            if len(normal_data) < 10:
                raise ValueError("학습에 충분한 데이터가 없습니다. 최소 10개 이상 필요합니다.")
            
            # 데이터 전처리
            from .esp32_data_processor import ESP32DataProcessor
            processor = ESP32DataProcessor()
            
            # 특징 추출
            features = processor.extract_features(normal_data)
            
            if features.size == 0:
                raise ValueError("특징 추출에 실패했습니다.")
            
            logger.info(f"추출된 특징 형태: {features.shape}")
            
            # 데이터 정규화
            self.scaler = StandardScaler()
            features_scaled = self.scaler.fit_transform(features)
            
            # Isolation Forest 모델 학습
            self.model = IsolationForest(
                contamination=contamination,
                random_state=self.random_state,
                n_estimators=100,
                max_samples='auto',
                max_features=1.0,
                bootstrap=False,
                n_jobs=-1
            )
            
            # 모델 학습
            self.model.fit(features_scaled)
            
            # 학습 통계 저장
            self.training_stats = {
                "n_samples": len(normal_data),
                "n_features": features.shape[1],
                "contamination": contamination,
                "feature_means": np.mean(features, axis=0).tolist(),
                "feature_stds": np.std(features, axis=0).tolist(),
                "training_date": datetime.now().isoformat()
            }
            
            # 모델 저장
            self.save_model()
            
            self.is_trained = True
            self.contamination = contamination
            
            logger.info("이상 탐지 모델 학습 완료")
            
            return {
                "success": True,
                "n_samples": len(normal_data),
                "n_features": features.shape[1],
                "contamination": contamination,
                "model_path": self.model_path
            }
            
        except Exception as e:
            logger.error(f"모델 학습 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def predict(self, sensor_data: Dict) -> Dict:
        """
        실시간 이상 감지
        
        Args:
            sensor_data: 센서 데이터 딕셔너리
            
        Returns:
            예측 결과 딕셔너리
        """
        try:
            if not self.is_trained or self.model is None:
                return {
                    "is_anomaly": False,
                    "anomaly_score": 0.0,
                    "confidence": 0.0,
                    "error": "모델이 학습되지 않았습니다."
                }
            
            # 단일 데이터를 리스트로 변환
            data_list = [sensor_data]
            
            # 특징 추출
            from .esp32_data_processor import ESP32DataProcessor
            processor = ESP32DataProcessor()
            features = processor.extract_features(data_list)
            
            if features.size == 0:
                return {
                    "is_anomaly": False,
                    "anomaly_score": 0.0,
                    "confidence": 0.0,
                    "error": "특징 추출 실패"
                }
            
            # 데이터 정규화
            features_scaled = self.scaler.transform(features)
            
            # 이상 탐지 예측
            prediction = self.model.predict(features_scaled)[0]  # -1: 이상, 1: 정상
            anomaly_score = self.model.decision_function(features_scaled)[0]  # 이상 점수
            
            # 결과 해석
            is_anomaly = prediction == -1
            confidence = abs(anomaly_score)  # 절댓값이 클수록 확신도 높음
            
            # 이상 점수를 0-1 범위로 정규화
            normalized_score = self._normalize_anomaly_score(anomaly_score)
            
            result = {
                "is_anomaly": is_anomaly,
                "anomaly_score": normalized_score,
                "raw_anomaly_score": float(anomaly_score),
                "confidence": float(confidence),
                "prediction": int(prediction),
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
            # 이상 감지 시 추가 정보
            if is_anomaly:
                result["severity"] = self._calculate_severity(normalized_score)
                result["recommendation"] = self._get_recommendation(sensor_data, normalized_score)
            
            return result
            
        except Exception as e:
            logger.error(f"이상 탐지 예측 실패: {e}")
            return {
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "confidence": 0.0,
                "error": str(e),
                "success": False
            }
    
    def predict_batch(self, sensor_data_list: List[Dict]) -> List[Dict]:
        """
        배치 이상 감지
        
        Args:
            sensor_data_list: 센서 데이터 리스트
            
        Returns:
            예측 결과 리스트
        """
        try:
            if not self.is_trained or self.model is None:
                return [{"error": "모델이 학습되지 않았습니다."} for _ in sensor_data_list]
            
            # 특징 추출
            from .esp32_data_processor import ESP32DataProcessor
            processor = ESP32DataProcessor()
            features = processor.extract_features(sensor_data_list)
            
            if features.size == 0:
                return [{"error": "특징 추출 실패"} for _ in sensor_data_list]
            
            # 데이터 정규화
            features_scaled = self.scaler.transform(features)
            
            # 배치 예측
            predictions = self.model.predict(features_scaled)
            anomaly_scores = self.model.decision_function(features_scaled)
            
            # 결과 변환
            results = []
            for i, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
                is_anomaly = pred == -1
                confidence = abs(score)
                normalized_score = self._normalize_anomaly_score(score)
                
                result = {
                    "is_anomaly": is_anomaly,
                    "anomaly_score": normalized_score,
                    "raw_anomaly_score": float(score),
                    "confidence": float(confidence),
                    "prediction": int(pred),
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
                
                if is_anomaly:
                    result["severity"] = self._calculate_severity(normalized_score)
                    result["recommendation"] = self._get_recommendation(sensor_data_list[i], normalized_score)
                
                results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"배치 이상 탐지 실패: {e}")
            return [{"error": str(e), "success": False} for _ in sensor_data_list]
    
    def _normalize_anomaly_score(self, raw_score: float) -> float:
        """이상 점수를 0-1 범위로 정규화"""
        # Isolation Forest의 decision_function은 음수 값이 이상을 나타냄
        # 더 음수일수록 더 이상적
        normalized = max(0, min(1, (raw_score + 0.5) / 1.0))
        return 1 - normalized  # 1에 가까울수록 이상
    
    def _calculate_severity(self, anomaly_score: float) -> str:
        """이상 심각도 계산"""
        if anomaly_score >= 0.8:
            return "critical"
        elif anomaly_score >= 0.6:
            return "high"
        elif anomaly_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _get_recommendation(self, sensor_data: Dict, anomaly_score: float) -> str:
        """이상 감지 시 권장사항 제공"""
        rms_energy = sensor_data.get('rms_energy', 0)
        decibel_level = sensor_data.get('decibel_level', 0)
        compressor_state = sensor_data.get('compressor_state', 0)
        
        recommendations = []
        
        if anomaly_score >= 0.8:
            recommendations.append("즉시 압축기 점검 필요")
        elif anomaly_score >= 0.6:
            recommendations.append("압축기 상태 모니터링 강화")
        
        if rms_energy > 2000:
            recommendations.append("RMS 에너지가 높음 - 진동 점검")
        
        if decibel_level > 70:
            recommendations.append("소음 레벨이 높음 - 베어링 점검")
        
        if compressor_state > 0.5 and decibel_level < 40:
            recommendations.append("압축기 작동 중이지만 소음이 낮음 - 냉매 부족 가능성")
        
        return "; ".join(recommendations) if recommendations else "정상 범위 내"
    
    def save_model(self) -> bool:
        """모델 저장"""
        try:
            if self.model is None or self.scaler is None:
                logger.warning("저장할 모델이 없습니다.")
                return False
            
            # 모델 저장
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            # 설정 저장
            config = {
                "contamination": self.contamination,
                "random_state": self.random_state,
                "is_trained": self.is_trained,
                "training_stats": self.training_stats,
                "model_type": "IsolationForest",
                "created_at": datetime.now().isoformat()
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"모델 저장 완료: {self.model_path}")
            return True
            
        except Exception as e:
            logger.error(f"모델 저장 실패: {e}")
            return False
    
    def load_model(self) -> bool:
        """모델 로드"""
        try:
            if not os.path.exists(self.model_path) or not os.path.exists(self.scaler_path):
                logger.warning("저장된 모델이 없습니다.")
                return False
            
            # 모델 로드
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            
            # 설정 로드
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.contamination = config.get('contamination', 0.1)
                    self.is_trained = config.get('is_trained', False)
                    self.training_stats = config.get('training_stats', {})
            
            logger.info("모델 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            return False
    
    def get_model_info(self) -> Dict:
        """모델 정보 반환"""
        return {
            "is_trained": self.is_trained,
            "contamination": self.contamination,
            "model_type": "IsolationForest",
            "training_stats": self.training_stats,
            "model_path": self.model_path,
            "scaler_path": self.scaler_path
        }
    
    def evaluate_model(self, test_data: List[Dict], known_anomalies: Optional[List[int]] = None) -> Dict:
        """
        모델 성능 평가
        
        Args:
            test_data: 테스트 데이터
            known_anomalies: 알려진 이상 데이터 인덱스 (선택적)
            
        Returns:
            평가 결과
        """
        try:
            if not self.is_trained:
                return {"error": "모델이 학습되지 않았습니다."}
            
            # 배치 예측
            results = self.predict_batch(test_data)
            
            # 예측 결과 추출
            predictions = [1 if r.get('is_anomaly', False) else 0 for r in results]
            
            if known_anomalies is not None:
                # 실제 라벨과 비교
                true_labels = [1 if i in known_anomalies else 0 for i in range(len(test_data))]
                
                # 성능 지표 계산
                from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
                
                accuracy = accuracy_score(true_labels, predictions)
                precision = precision_score(true_labels, predictions, zero_division=0)
                recall = recall_score(true_labels, predictions, zero_division=0)
                f1 = f1_score(true_labels, predictions, zero_division=0)
                
                return {
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1_score": f1,
                    "n_samples": len(test_data),
                    "n_anomalies_detected": sum(predictions),
                    "n_true_anomalies": len(known_anomalies) if known_anomalies else 0
                }
            else:
                return {
                    "n_samples": len(test_data),
                    "n_anomalies_detected": sum(predictions),
                    "anomaly_rate": sum(predictions) / len(test_data)
                }
                
        except Exception as e:
            logger.error(f"모델 평가 실패: {e}")
            return {"error": str(e)}

# 사용 예제
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 이상 탐지 모델 초기화
    detector = CompressorAnomalyDetector()
    
    # 기존 모델 로드 시도
    if detector.load_model():
        print("기존 모델 로드 완료")
        print(f"모델 정보: {detector.get_model_info()}")
    else:
        print("새 모델 학습 필요")
        
        # 정상 데이터 수집 및 학습 (실제 구현에서는 데이터를 수집해야 함)
        from .esp32_data_processor import ESP32DataProcessor
        processor = ESP32DataProcessor()
        normal_data = processor.collect_normal_data(hours=24)
        
        if normal_data:
            result = detector.train(normal_data)
            print(f"학습 결과: {result}")
        else:
            print("학습용 데이터가 없습니다.")
