#!/usr/bin/env python3
"""
예측 유지보수 서비스
Tesla 스타일의 예측 유지보수 시스템
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error
import joblib
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaintenanceType(Enum):
    """유지보수 타입"""
    PREVENTIVE = "preventive"
    PREDICTIVE = "predictive"
    CORRECTIVE = "corrective"
    EMERGENCY = "emergency"

class EquipmentStatus(Enum):
    """장비 상태"""
    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILED = "failed"

@dataclass
class MaintenanceRecord:
    """유지보수 기록 데이터 클래스"""
    equipment_id: str
    maintenance_type: MaintenanceType
    description: str
    cost: float
    duration_hours: float
    technician: str
    timestamp: datetime
    status: EquipmentStatus

@dataclass
class MaintenancePrediction:
    """유지보수 예측 결과"""
    equipment_id: str
    predicted_failure_date: datetime
    confidence: float
    maintenance_type: MaintenanceType
    recommended_actions: List[str]
    estimated_cost: float
    priority: str

class PredictiveMaintenanceService:
    """예측 유지보수 서비스"""
    
    def __init__(self, db_path: str = "data/analytics.db"):
        self.db_path = db_path
        self.conn = None
        self.models = {}
        self.scalers = {}
        self.equipment_thresholds = {}
        
        # 모델 저장 경로
        self.model_dir = "data/models/maintenance"
        os.makedirs(self.model_dir, exist_ok=True)
        
        # 초기화
        self._init_database()
        self._load_models()
        self._load_equipment_thresholds()
        
        logger.info("예측 유지보수 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # 유지보수 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maintenance_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipment_id TEXT NOT NULL,
                    maintenance_type TEXT NOT NULL,
                    description TEXT,
                    cost REAL,
                    duration_hours REAL,
                    technician TEXT,
                    timestamp DATETIME NOT NULL,
                    status TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 장비 상태 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS equipment_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipment_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    temperature REAL,
                    vibration REAL,
                    power_consumption REAL,
                    efficiency REAL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 예측 결과 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS maintenance_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    equipment_id TEXT NOT NULL,
                    predicted_failure_date DATETIME NOT NULL,
                    confidence REAL NOT NULL,
                    maintenance_type TEXT NOT NULL,
                    recommended_actions TEXT NOT NULL,
                    estimated_cost REAL,
                    priority TEXT NOT NULL,
                    generated_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("유지보수 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_models(self):
        """기존 모델 로드"""
        try:
            # 실제 구현에서는 저장된 모델을 로드
            # 여기서는 기본 모델 초기화
            self.models = {
                'failure_prediction': RandomForestClassifier(n_estimators=100, random_state=42),
                'maintenance_cost': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'equipment_lifecycle': GradientBoostingRegressor(n_estimators=100, random_state=42)
            }
            
            self.scalers = {
                'features': StandardScaler(),
                'targets': StandardScaler()
            }
            
            logger.info("유지보수 모델 로드 완료")
            
        except Exception as e:
            logger.error(f"모델 로드 오류: {e}")
    
    def _load_equipment_thresholds(self):
        """장비 임계값 로드"""
        try:
            # 기본 임계값 설정
            self.equipment_thresholds = {
                'compressor': {
                    'temperature': {'warning': 25, 'critical': 30},
                    'vibration': {'warning': 5.0, 'critical': 8.0},
                    'efficiency': {'warning': 0.8, 'critical': 0.7},
                    'power_consumption': {'warning': 1000, 'critical': 1200}
                },
                'refrigeration': {
                    'temperature': {'warning': 2, 'critical': 5},
                    'vibration': {'warning': 3.0, 'critical': 5.0},
                    'efficiency': {'warning': 0.85, 'critical': 0.75},
                    'power_consumption': {'warning': 800, 'critical': 1000}
                }
            }
            
            logger.info("장비 임계값 로드 완료")
            
        except Exception as e:
            logger.error(f"장비 임계값 로드 오류: {e}")
    
    def record_maintenance(self, record: MaintenanceRecord) -> bool:
        """유지보수 기록 저장"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO maintenance_records 
                (equipment_id, maintenance_type, description, cost, duration_hours, 
                 technician, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.equipment_id,
                record.maintenance_type.value,
                record.description,
                record.cost,
                record.duration_hours,
                record.technician,
                record.timestamp,
                record.status.value
            ))
            
            self.conn.commit()
            logger.info(f"유지보수 기록 저장 완료: {record.equipment_id}")
            return True
            
        except Exception as e:
            logger.error(f"유지보수 기록 저장 오류: {e}")
            return False
    
    def update_equipment_status(self, equipment_id: str, status: EquipmentStatus,
                               temperature: float = None, vibration: float = None,
                               power_consumption: float = None, efficiency: float = None) -> bool:
        """장비 상태 업데이트"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO equipment_status 
                (equipment_id, status, temperature, vibration, power_consumption, efficiency, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                equipment_id,
                status.value,
                temperature,
                vibration,
                power_consumption,
                efficiency,
                datetime.now()
            ))
            
            self.conn.commit()
            logger.info(f"장비 상태 업데이트 완료: {equipment_id}")
            return True
            
        except Exception as e:
            logger.error(f"장비 상태 업데이트 오류: {e}")
            return False
    
    def predict_maintenance(self, equipment_id: str, days_ahead: int = 30) -> MaintenancePrediction:
        """유지보수 예측"""
        try:
            # 장비 상태 데이터 조회
            query = '''
                SELECT * FROM equipment_status 
                WHERE equipment_id = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            '''
            
            start_date = datetime.now() - timedelta(days=90)
            df = pd.read_sql_query(query, self.conn, params=(equipment_id, start_date))
            
            if df.empty:
                return self._create_default_prediction(equipment_id)
            
            # 특성 추출
            features = self._extract_features(df)
            
            # 모델 예측
            failure_probability = self._predict_failure_probability(features)
            predicted_date = self._predict_failure_date(features, days_ahead)
            maintenance_type = self._determine_maintenance_type(failure_probability)
            recommended_actions = self._generate_recommendations(features, maintenance_type)
            estimated_cost = self._estimate_maintenance_cost(features, maintenance_type)
            priority = self._determine_priority(failure_probability, predicted_date)
            
            prediction = MaintenancePrediction(
                equipment_id=equipment_id,
                predicted_failure_date=predicted_date,
                confidence=failure_probability,
                maintenance_type=maintenance_type,
                recommended_actions=recommended_actions,
                estimated_cost=estimated_cost,
                priority=priority
            )
            
            # 예측 결과 저장
            self._save_prediction(prediction)
            
            return prediction
            
        except Exception as e:
            logger.error(f"유지보수 예측 오류: {e}")
            return self._create_default_prediction(equipment_id)
    
    def get_maintenance_schedule(self, store_id: str = None, days_ahead: int = 30) -> List[Dict]:
        """유지보수 스케줄 조회"""
        try:
            query = '''
                SELECT mp.*, es.equipment_id, es.status
                FROM maintenance_predictions mp
                JOIN equipment_status es ON mp.equipment_id = es.equipment_id
                WHERE mp.predicted_failure_date <= ?
                ORDER BY mp.predicted_failure_date ASC
            '''
            
            end_date = datetime.now() + timedelta(days=days_ahead)
            df = pd.read_sql_query(query, self.conn, params=(end_date,))
            
            schedule = []
            for _, row in df.iterrows():
                schedule.append({
                    'equipment_id': row['equipment_id'],
                    'predicted_date': row['predicted_failure_date'],
                    'confidence': row['confidence'],
                    'maintenance_type': row['maintenance_type'],
                    'priority': row['priority'],
                    'estimated_cost': row['estimated_cost'],
                    'recommended_actions': json.loads(row['recommended_actions']),
                    'current_status': row['status']
                })
            
            return schedule
            
        except Exception as e:
            logger.error(f"유지보수 스케줄 조회 오류: {e}")
            return []
    
    def analyze_maintenance_costs(self, store_id: str = None, months: int = 12) -> Dict:
        """유지보수 비용 분석"""
        try:
            query = '''
                SELECT * FROM maintenance_records 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            '''
            
            start_date = datetime.now() - timedelta(days=months * 30)
            df = pd.read_sql_query(query, self.conn, params=(start_date,))
            
            if df.empty:
                return {'error': '데이터가 없습니다'}
            
            # 기본 통계
            total_cost = df['cost'].sum()
            avg_cost = df['cost'].mean()
            total_duration = df['duration_hours'].sum()
            avg_duration = df['duration_hours'].mean()
            
            # 유지보수 타입별 분석
            type_analysis = df.groupby('maintenance_type').agg({
                'cost': ['sum', 'mean', 'count'],
                'duration_hours': ['sum', 'mean']
            }).round(2)
            
            # 월별 트렌드
            df['month'] = pd.to_datetime(df['timestamp']).dt.to_period('M')
            monthly_costs = df.groupby('month')['cost'].sum().to_dict()
            
            # 장비별 분석
            equipment_analysis = df.groupby('equipment_id').agg({
                'cost': ['sum', 'mean', 'count'],
                'duration_hours': ['sum', 'mean']
            }).round(2)
            
            # 비용 예측
            cost_trend = self._predict_future_costs(df)
            
            analysis = {
                'summary': {
                    'total_cost': total_cost,
                    'avg_cost': avg_cost,
                    'total_duration': total_duration,
                    'avg_duration': avg_duration
                },
                'type_analysis': type_analysis.to_dict(),
                'monthly_trends': monthly_costs,
                'equipment_analysis': equipment_analysis.to_dict(),
                'cost_prediction': cost_trend
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"유지보수 비용 분석 오류: {e}")
            return {'error': str(e)}
    
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        """특성 추출"""
        try:
            features = []
            
            # 기본 통계 특성
            if 'temperature' in df.columns:
                features.extend([
                    df['temperature'].mean(),
                    df['temperature'].std(),
                    df['temperature'].max(),
                    df['temperature'].min()
                ])
            
            if 'vibration' in df.columns:
                features.extend([
                    df['vibration'].mean(),
                    df['vibration'].std(),
                    df['vibration'].max()
                ])
            
            if 'efficiency' in df.columns:
                features.extend([
                    df['efficiency'].mean(),
                    df['efficiency'].std(),
                    df['efficiency'].min()
                ])
            
            if 'power_consumption' in df.columns:
                features.extend([
                    df['power_consumption'].mean(),
                    df['power_consumption'].std(),
                    df['power_consumption'].max()
                ])
            
            # 트렌드 특성
            if len(df) > 1:
                if 'temperature' in df.columns:
                    temp_trend = np.polyfit(range(len(df)), df['temperature'], 1)[0]
                    features.append(temp_trend)
                
                if 'efficiency' in df.columns:
                    eff_trend = np.polyfit(range(len(df)), df['efficiency'], 1)[0]
                    features.append(eff_trend)
            
            # 이상치 특성
            if 'temperature' in df.columns:
                temp_anomalies = self._count_anomalies(df['temperature'])
                features.append(temp_anomalies)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"특성 추출 오류: {e}")
            return np.array([]).reshape(1, -1)
    
    def _predict_failure_probability(self, features: np.ndarray) -> float:
        """고장 확률 예측"""
        try:
            if features.size == 0:
                return 0.5  # 기본값
            
            # 실제 구현에서는 훈련된 모델 사용
            # 여기서는 간단한 규칙 기반 예측
            if features.size >= 4:
                temp_mean = features[0][0] if len(features[0]) > 0 else 25
                temp_std = features[0][1] if len(features[0]) > 1 else 2
                eff_mean = features[0][4] if len(features[0]) > 4 else 0.8
                
                # 온도가 높고 효율성이 낮을수록 고장 확률 증가
                temp_factor = max(0, (temp_mean - 25) / 10)
                eff_factor = max(0, (0.8 - eff_mean) / 0.2)
                std_factor = max(0, (temp_std - 2) / 2)
                
                probability = min(0.95, 0.1 + temp_factor * 0.3 + eff_factor * 0.4 + std_factor * 0.2)
                return probability
            
            return 0.5
            
        except Exception as e:
            logger.error(f"고장 확률 예측 오류: {e}")
            return 0.5
    
    def _predict_failure_date(self, features: np.ndarray, days_ahead: int) -> datetime:
        """고장 예상 날짜 예측"""
        try:
            failure_probability = self._predict_failure_probability(features)
            
            # 확률에 따라 예상 날짜 계산
            if failure_probability > 0.8:
                days = 1
            elif failure_probability > 0.6:
                days = 7
            elif failure_probability > 0.4:
                days = 14
            else:
                days = 30
            
            return datetime.now() + timedelta(days=min(days, days_ahead))
            
        except Exception as e:
            logger.error(f"고장 날짜 예측 오류: {e}")
            return datetime.now() + timedelta(days=30)
    
    def _determine_maintenance_type(self, failure_probability: float) -> MaintenanceType:
        """유지보수 타입 결정"""
        if failure_probability > 0.8:
            return MaintenanceType.EMERGENCY
        elif failure_probability > 0.6:
            return MaintenanceType.CORRECTIVE
        elif failure_probability > 0.4:
            return MaintenanceType.PREDICTIVE
        else:
            return MaintenanceType.PREVENTIVE
    
    def _generate_recommendations(self, features: np.ndarray, maintenance_type: MaintenanceType) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        try:
            if features.size >= 4:
                temp_mean = features[0][0] if len(features[0]) > 0 else 25
                eff_mean = features[0][4] if len(features[0]) > 4 else 0.8
                
                if temp_mean > 30:
                    recommendations.append("온도가 높습니다. 냉각 시스템을 점검하세요.")
                
                if eff_mean < 0.7:
                    recommendations.append("효율성이 낮습니다. 압축기를 점검하세요.")
                
                if maintenance_type == MaintenanceType.EMERGENCY:
                    recommendations.append("긴급 점검이 필요합니다. 즉시 조치하세요.")
                elif maintenance_type == MaintenanceType.CORRECTIVE:
                    recommendations.append("수정 작업이 필요합니다. 1주일 내 점검하세요.")
                elif maintenance_type == MaintenanceType.PREDICTIVE:
                    recommendations.append("예방 점검이 필요합니다. 2주일 내 점검하세요.")
                else:
                    recommendations.append("정기 점검을 권장합니다.")
            
        except Exception as e:
            logger.error(f"권장사항 생성 오류: {e}")
        
        return recommendations
    
    def _estimate_maintenance_cost(self, features: np.ndarray, maintenance_type: MaintenanceType) -> float:
        """유지보수 비용 추정"""
        base_costs = {
            MaintenanceType.PREVENTIVE: 100,
            MaintenanceType.PREDICTIVE: 200,
            MaintenanceType.CORRECTIVE: 500,
            MaintenanceType.EMERGENCY: 1000
        }
        
        base_cost = base_costs.get(maintenance_type, 200)
        
        # 특성에 따른 비용 조정
        if features.size >= 4:
            temp_mean = features[0][0] if len(features[0]) > 0 else 25
            if temp_mean > 30:
                base_cost *= 1.5
        
        return base_cost
    
    def _determine_priority(self, failure_probability: float, predicted_date: datetime) -> str:
        """우선순위 결정"""
        days_until_failure = (predicted_date - datetime.now()).days
        
        if failure_probability > 0.8 or days_until_failure <= 1:
            return "urgent"
        elif failure_probability > 0.6 or days_until_failure <= 7:
            return "high"
        elif failure_probability > 0.4 or days_until_failure <= 14:
            return "medium"
        else:
            return "low"
    
    def _save_prediction(self, prediction: MaintenancePrediction) -> bool:
        """예측 결과 저장"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO maintenance_predictions 
                (equipment_id, predicted_failure_date, confidence, maintenance_type,
                 recommended_actions, estimated_cost, priority, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.equipment_id,
                prediction.predicted_failure_date,
                prediction.confidence,
                prediction.maintenance_type.value,
                json.dumps(prediction.recommended_actions),
                prediction.estimated_cost,
                prediction.priority,
                datetime.now()
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"예측 결과 저장 오류: {e}")
            return False
    
    def _create_default_prediction(self, equipment_id: str) -> MaintenancePrediction:
        """기본 예측 결과 생성"""
        return MaintenancePrediction(
            equipment_id=equipment_id,
            predicted_failure_date=datetime.now() + timedelta(days=30),
            confidence=0.5,
            maintenance_type=MaintenanceType.PREVENTIVE,
            recommended_actions=["정기 점검을 권장합니다."],
            estimated_cost=100.0,
            priority="low"
        )
    
    def _count_anomalies(self, series: pd.Series) -> int:
        """이상치 개수 계산"""
        try:
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            anomalies = series[(series < lower_bound) | (series > upper_bound)]
            return len(anomalies)
            
        except Exception as e:
            logger.error(f"이상치 계산 오류: {e}")
            return 0
    
    def _predict_future_costs(self, df: pd.DataFrame) -> Dict:
        """미래 비용 예측"""
        try:
            if len(df) < 3:
                return {'next_month': 0, 'trend': 'stable'}
            
            # 월별 비용 트렌드
            df['month'] = pd.to_datetime(df['timestamp']).dt.to_period('M')
            monthly_costs = df.groupby('month')['cost'].sum()
            
            if len(monthly_costs) >= 2:
                # 간단한 선형 트렌드
                x = np.arange(len(monthly_costs))
                y = monthly_costs.values
                trend = np.polyfit(x, y, 1)[0]
                
                next_month_cost = monthly_costs.iloc[-1] + trend
                trend_direction = 'increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable'
                
                return {
                    'next_month': max(0, next_month_cost),
                    'trend': trend_direction,
                    'trend_value': trend
                }
            
            return {'next_month': monthly_costs.iloc[-1], 'trend': 'stable'}
            
        except Exception as e:
            logger.error(f"미래 비용 예측 오류: {e}")
            return {'next_month': 0, 'trend': 'stable'}

# 전역 인스턴스
predictive_maintenance_service = PredictiveMaintenanceService()
