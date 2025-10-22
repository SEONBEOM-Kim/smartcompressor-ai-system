#!/usr/bin/env python3
"""
현장 데이터 수집 및 모델 개선 서비스
실제 매장 환경에서의 데이터를 수집하여 AI 정확도를 향상시킴
"""

import os
import json
import numpy as np
import librosa
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import sqlite3

@dataclass
class FieldDataPoint:
    """현장 데이터 포인트"""
    timestamp: datetime
    store_id: str
    device_id: str
    audio_file_path: str
    ground_truth_label: str  # 'normal', 'leak', 'overload', 'door_open'
    confidence_score: float
    environmental_conditions: Dict
    operator_notes: str
    ai_prediction: str
    ai_confidence: float

class FieldDataCollector:
    """현장 데이터 수집기"""
    
    def __init__(self, db_path: str = "data/field_data.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
        
        # 데이터 수집 설정
        self.min_confidence_threshold = 0.7
        self.uncertainty_threshold = 0.3  # 불확실한 예측 수집
        
    def _init_database(self):
        """현장 데이터베이스 초기화"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 현장 데이터 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS field_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    store_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    audio_file_path TEXT NOT NULL,
                    ground_truth_label TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    environmental_conditions TEXT NOT NULL,
                    operator_notes TEXT,
                    ai_prediction TEXT NOT NULL,
                    ai_confidence REAL NOT NULL,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 환경 조건 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS environmental_conditions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_id INTEGER NOT NULL,
                    temperature REAL,
                    humidity REAL,
                    noise_level REAL,
                    vibration_level REAL,
                    power_consumption REAL,
                    FOREIGN KEY (data_id) REFERENCES field_data (id)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_field_data_timestamp ON field_data(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_field_data_store ON field_data(store_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_field_data_label ON field_data(ground_truth_label)')
            
            conn.commit()
    
    def collect_uncertain_predictions(self, 
                                    store_id: str, 
                                    device_id: str, 
                                    audio_file_path: str,
                                    ai_prediction: str,
                                    ai_confidence: float,
                                    environmental_conditions: Dict = None) -> bool:
        """불확실한 예측 수집 (사람 검증 필요)"""
        
        # 불확실한 예측인지 확인
        if ai_confidence > self.min_confidence_threshold:
            return False  # 확실한 예측이므로 수집하지 않음
        
        try:
            data_point = FieldDataPoint(
                timestamp=datetime.now(),
                store_id=store_id,
                device_id=device_id,
                audio_file_path=audio_file_path,
                ground_truth_label="",  # 나중에 사람이 라벨링
                confidence_score=0.0,  # 나중에 사람이 평가
                environmental_conditions=environmental_conditions or {},
                operator_notes="",
                ai_prediction=ai_prediction,
                ai_confidence=ai_confidence
            )
            
            self._store_data_point(data_point)
            self.logger.info(f"불확실한 예측 수집: {store_id} - {ai_prediction} ({ai_confidence:.3f})")
            return True
            
        except Exception as e:
            self.logger.error(f"데이터 수집 실패: {e}")
            return False
    
    def collect_verified_data(self, 
                            store_id: str,
                            device_id: str,
                            audio_file_path: str,
                            ground_truth_label: str,
                            confidence_score: float,
                            environmental_conditions: Dict = None,
                            operator_notes: str = "",
                            ai_prediction: str = "",
                            ai_confidence: float = 0.0) -> bool:
        """검증된 데이터 수집"""
        
        try:
            data_point = FieldDataPoint(
                timestamp=datetime.now(),
                store_id=store_id,
                device_id=device_id,
                audio_file_path=audio_file_path,
                ground_truth_label=ground_truth_label,
                confidence_score=confidence_score,
                environmental_conditions=environmental_conditions or {},
                operator_notes=operator_notes,
                ai_prediction=ai_prediction,
                ai_confidence=ai_confidence
            )
            
            self._store_data_point(data_point, is_verified=True)
            self.logger.info(f"검증된 데이터 수집: {store_id} - {ground_truth_label}")
            return True
            
        except Exception as e:
            self.logger.error(f"검증된 데이터 수집 실패: {e}")
            return False
    
    def _store_data_point(self, data_point: FieldDataPoint, is_verified: bool = False):
        """데이터 포인트 저장"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO field_data 
                (timestamp, store_id, device_id, audio_file_path, ground_truth_label,
                 confidence_score, environmental_conditions, operator_notes,
                 ai_prediction, ai_confidence, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data_point.timestamp,
                data_point.store_id,
                data_point.device_id,
                data_point.audio_file_path,
                data_point.ground_truth_label,
                data_point.confidence_score,
                json.dumps(data_point.environmental_conditions),
                data_point.operator_notes,
                data_point.ai_prediction,
                data_point.ai_confidence,
                is_verified
            ))
            
            data_id = cursor.lastrowid
            
            # 환경 조건 저장
            if data_point.environmental_conditions:
                env = data_point.environmental_conditions
                cursor.execute('''
                    INSERT INTO environmental_conditions 
                    (data_id, temperature, humidity, noise_level, vibration_level, power_consumption)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    data_id,
                    env.get('temperature'),
                    env.get('humidity'),
                    env.get('noise_level'),
                    env.get('vibration_level'),
                    env.get('power_consumption')
                ))
            
            conn.commit()
    
    def get_pending_verification_data(self, limit: int = 100) -> List[Dict]:
        """검증 대기 중인 데이터 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            
            cursor.execute('''
                SELECT * FROM field_data 
                WHERE is_verified = FALSE 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_verified_data(self, 
                         store_id: str = None, 
                         days: int = 30) -> List[Dict]:
        """검증된 데이터 조회"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.row_factory = sqlite3.Row
            
            start_date = datetime.now() - timedelta(days=days)
            
            if store_id:
                cursor.execute('''
                    SELECT * FROM field_data 
                    WHERE is_verified = TRUE 
                    AND store_id = ? 
                    AND timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (store_id, start_date))
            else:
                cursor.execute('''
                    SELECT * FROM field_data 
                    WHERE is_verified = TRUE 
                    AND timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (start_date,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_ground_truth(self, data_id: int, ground_truth_label: str, 
                           confidence_score: float, operator_notes: str = ""):
        """지상 진실 라벨 업데이트"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE field_data 
                SET ground_truth_label = ?, 
                    confidence_score = ?, 
                    operator_notes = ?,
                    is_verified = TRUE
                WHERE id = ?
            ''', (ground_truth_label, confidence_score, operator_notes, data_id))
            
            conn.commit()
            self.logger.info(f"지상 진실 라벨 업데이트: ID {data_id} - {ground_truth_label}")
    
    def get_ai_accuracy_stats(self, days: int = 30) -> Dict:
        """AI 정확도 통계"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            cursor.execute('''
                SELECT 
                    ground_truth_label,
                    ai_prediction,
                    COUNT(*) as count
                FROM field_data 
                WHERE is_verified = TRUE 
                AND timestamp >= ?
                GROUP BY ground_truth_label, ai_prediction
            ''', (start_date,))
            
            results = cursor.fetchall()
            
            # 정확도 계산
            total_correct = 0
            total_samples = 0
            confusion_matrix = {}
            
            for ground_truth, ai_pred, count in results:
                total_samples += count
                if ground_truth == ai_pred:
                    total_correct += count
                
                if ground_truth not in confusion_matrix:
                    confusion_matrix[ground_truth] = {}
                confusion_matrix[ground_truth][ai_pred] = count
            
            accuracy = total_correct / total_samples if total_samples > 0 else 0
            
            return {
                'accuracy': accuracy,
                'total_samples': total_samples,
                'correct_predictions': total_correct,
                'confusion_matrix': confusion_matrix
            }

class ModelImprovementService:
    """모델 개선 서비스"""
    
    def __init__(self, field_collector: FieldDataCollector):
        self.field_collector = field_collector
        self.logger = logging.getLogger(__name__)
    
    def identify_problematic_patterns(self) -> List[Dict]:
        """문제가 되는 패턴 식별"""
        try:
            # 검증된 데이터에서 AI가 틀린 케이스 분석
            verified_data = self.field_collector.get_verified_data()
            
            problematic_cases = []
            for data in verified_data:
                if data['ground_truth_label'] != data['ai_prediction']:
                    problematic_cases.append({
                        'data_id': data['id'],
                        'audio_file': data['audio_file_path'],
                        'ground_truth': data['ground_truth_label'],
                        'ai_prediction': data['ai_prediction'],
                        'ai_confidence': data['ai_confidence'],
                        'environmental_conditions': json.loads(data['environmental_conditions']),
                        'operator_notes': data['operator_notes']
                    })
            
            self.logger.info(f"문제가 되는 패턴 {len(problematic_cases)}개 식별")
            return problematic_cases
            
        except Exception as e:
            self.logger.error(f"문제 패턴 식별 실패: {e}")
            return []
    
    def suggest_model_improvements(self) -> Dict:
        """모델 개선 제안"""
        try:
            accuracy_stats = self.field_collector.get_ai_accuracy_stats()
            problematic_cases = self.identify_problematic_patterns()
            
            suggestions = {
                'current_accuracy': accuracy_stats['accuracy'],
                'total_samples': accuracy_stats['total_samples'],
                'improvements': []
            }
            
            # 정확도가 낮은 경우
            if accuracy_stats['accuracy'] < 0.8:
                suggestions['improvements'].append({
                    'type': 'data_collection',
                    'priority': 'high',
                    'description': '더 많은 검증된 데이터 수집 필요',
                    'action': '현장에서 더 많은 라벨링된 데이터 수집'
                })
            
            # 특정 클래스에서 성능이 낮은 경우
            confusion_matrix = accuracy_stats['confusion_matrix']
            for true_label, predictions in confusion_matrix.items():
                total_true = sum(predictions.values())
                correct = predictions.get(true_label, 0)
                class_accuracy = correct / total_true if total_true > 0 else 0
                
                if class_accuracy < 0.7:
                    suggestions['improvements'].append({
                        'type': 'class_imbalance',
                        'priority': 'medium',
                        'description': f'{true_label} 클래스 정확도 낮음 ({class_accuracy:.2f})',
                        'action': f'{true_label} 클래스의 더 많은 샘플 수집'
                    })
            
            # 환경 조건별 성능 분석
            env_conditions = {}
            for case in problematic_cases:
                env = case['environmental_conditions']
                for key, value in env.items():
                    if key not in env_conditions:
                        env_conditions[key] = []
                    env_conditions[key].append(value)
            
            for env_key, values in env_conditions.items():
                if len(values) > 5:  # 충분한 샘플이 있는 경우
                    suggestions['improvements'].append({
                        'type': 'environmental_factor',
                        'priority': 'low',
                        'description': f'{env_key} 환경 조건이 AI 성능에 영향',
                        'action': f'{env_key}를 특징으로 추가 고려'
                    })
            
            return suggestions
            
        except Exception as e:
            self.logger.error(f"모델 개선 제안 생성 실패: {e}")
            return {'current_accuracy': 0, 'total_samples': 0, 'improvements': []}

# 전역 인스턴스
field_data_collector = FieldDataCollector()
model_improvement_service = ModelImprovementService(field_data_collector)
