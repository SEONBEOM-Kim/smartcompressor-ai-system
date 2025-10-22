#!/usr/bin/env python3
"""
시계열 패턴 학습 시스템
맥락 기반 고장 라벨링을 위한 시계열 데이터 수집 및 학습 시스템
"""

import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
import logging
from dataclasses import dataclass
from collections import deque
import sqlite3
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TimeSeriesWindow:
    """시계열 윈도우"""
    data: List[Dict]
    start_time: datetime
    end_time: datetime
    window_size: int
    context: Dict

class TimeSeriesLearningSystem:
    """시계열 패턴 학습 시스템"""
    
    def __init__(self, 
                 db_path: str = "database/smartcompressor.db",
                 learning_config_path: str = "data/learning_config.json"):
        self.db_path = db_path
        self.learning_config_path = learning_config_path
        
        # 학습 설정
        self.window_sizes = [60, 300, 900, 3600]  # 1분, 5분, 15분, 1시간
        self.min_samples_per_window = 10
        self.max_samples_per_window = 1000
        
        # 시계열 버퍼
        self.time_series_buffer = deque(maxlen=10000)  # 최근 10,000개 샘플
        self.context_buffer = deque(maxlen=1000)  # 최근 1,000개 컨텍스트
        
        # 학습 데이터베이스
        self.learning_db_path = "data/learning_database.db"
        self._initialize_learning_database()
        
        # 학습 설정 로드
        self.learning_config = self._load_learning_config()
        
        logger.info("시계열 패턴 학습 시스템 초기화 완료")
    
    def _initialize_learning_database(self):
        """학습 데이터베이스 초기화"""
        try:
            os.makedirs(os.path.dirname(self.learning_db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            # 시계열 윈도우 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS timeseries_windows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    window_id TEXT UNIQUE,
                    start_time TEXT,
                    end_time TEXT,
                    window_size INTEGER,
                    data_count INTEGER,
                    pattern_type TEXT,
                    failure_type TEXT,
                    confidence REAL,
                    features_json TEXT,
                    context_json TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 학습 라벨 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_labels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    window_id TEXT,
                    expert_label TEXT,
                    ai_label TEXT,
                    confidence REAL,
                    feedback TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (window_id) REFERENCES timeseries_windows (window_id)
                )
            ''')
            
            # 패턴 데이터베이스 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pattern_database (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    failure_type TEXT,
                    features_json TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("학습 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"학습 데이터베이스 초기화 실패: {e}")
    
    def _load_learning_config(self) -> Dict:
        """학습 설정 로드"""
        default_config = {
            'learning_enabled': True,
            'auto_labeling': True,
            'expert_review_threshold': 0.7,
            'pattern_update_frequency': 24,  # 시간
            'min_confidence_for_learning': 0.6,
            'max_patterns_per_type': 1000
        }
        
        try:
            if os.path.exists(self.learning_config_path):
                with open(self.learning_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
        except Exception as e:
            logger.warning(f"학습 설정 로드 실패, 기본값 사용: {e}")
        
        return default_config
    
    def collect_time_series_data(self, 
                                sensor_data: List[Dict],
                                context_data: Dict) -> List[TimeSeriesWindow]:
        """시계열 데이터 수집"""
        
        # 센서 데이터를 버퍼에 추가
        for data in sensor_data:
            self.time_series_buffer.append({
                'timestamp': data.get('timestamp', datetime.now().isoformat()),
                'decibel_level': data.get('decibel_level', 0),
                'temperature': data.get('temperature', 20),
                'compressor_state': data.get('compressor_state', 0),
                'power_consumption': data.get('power_consumption', 0),
                'vibration_level': data.get('vibration_level', 0)
            })
        
        # 컨텍스트 데이터 추가
        self.context_buffer.append({
            'timestamp': datetime.now().isoformat(),
            'context': context_data
        })
        
        # 시계열 윈도우 생성
        windows = []
        for window_size in self.window_sizes:
            window = self._create_time_series_window(window_size)
            if window:
                windows.append(window)
        
        return windows
    
    def _create_time_series_window(self, window_size: int) -> Optional[TimeSeriesWindow]:
        """시계열 윈도우 생성"""
        
        if len(self.time_series_buffer) < self.min_samples_per_window:
            return None
        
        # 윈도우 크기에 맞는 데이터 선택
        window_data = list(self.time_series_buffer)[-window_size:]
        
        if len(window_data) < self.min_samples_per_window:
            return None
        
        # 시간 범위 계산
        start_time = datetime.fromisoformat(window_data[0]['timestamp'])
        end_time = datetime.fromisoformat(window_data[-1]['timestamp'])
        
        # 컨텍스트 데이터 가져오기
        context = self._get_context_for_window(start_time, end_time)
        
        # 윈도우 ID 생성
        window_id = f"{start_time.strftime('%Y%m%d_%H%M%S')}_{window_size}"
        
        return TimeSeriesWindow(
            data=window_data,
            start_time=start_time,
            end_time=end_time,
            window_size=window_size,
            context=context
        )
    
    def _get_context_for_window(self, 
                              start_time: datetime,
                              end_time: datetime) -> Dict:
        """윈도우에 해당하는 컨텍스트 데이터 가져오기"""
        
        # 해당 시간 범위의 컨텍스트 찾기
        relevant_contexts = []
        for ctx in self.context_buffer:
            ctx_time = datetime.fromisoformat(ctx['timestamp'])
            if start_time <= ctx_time <= end_time:
                relevant_contexts.append(ctx['context'])
        
        if not relevant_contexts:
            # 가장 최근 컨텍스트 사용
            if self.context_buffer:
                return self.context_buffer[-1]['context']
            return {}
        
        # 컨텍스트 통합
        merged_context = {}
        for ctx in relevant_contexts:
            merged_context.update(ctx)
        
        return merged_context
    
    def extract_pattern_features(self, window: TimeSeriesWindow) -> Dict:
        """패턴 특징 추출"""
        
        if not window.data:
            return {}
        
        # 시계열 데이터 정리
        timestamps = [datetime.fromisoformat(d['timestamp']) for d in window.data]
        decibel_values = [d['decibel_level'] for d in window.data]
        temperature_values = [d['temperature'] for d in window.data]
        compressor_states = [d['compressor_state'] for d in window.data]
        
        # 기본 통계 특징
        features = {
            'window_size': window.window_size,
            'data_count': len(window.data),
            'duration_seconds': (window.end_time - window.start_time).total_seconds(),
            
            # 데시벨 특징
            'decibel_mean': float(np.mean(decibel_values)),
            'decibel_std': float(np.std(decibel_values)),
            'decibel_min': float(np.min(decibel_values)),
            'decibel_max': float(np.max(decibel_values)),
            'decibel_range': float(np.max(decibel_values) - np.min(decibel_values)),
            
            # 온도 특징
            'temperature_mean': float(np.mean(temperature_values)),
            'temperature_std': float(np.std(temperature_values)),
            'temperature_trend': self._calculate_trend(temperature_values),
            
            # 압축기 상태 특징
            'compressor_on_ratio': float(np.mean(compressor_states)),
            'compressor_cycles': self._count_cycles(compressor_states),
            'compressor_avg_cycle_length': self._calculate_avg_cycle_length(compressor_states),
            
            # 시계열 패턴 특징
            'trend_slope': self._calculate_trend(decibel_values),
            'volatility': float(np.std(np.diff(decibel_values))),
            'autocorrelation': self._calculate_autocorrelation(decibel_values),
            'periodicity': self._calculate_periodicity(decibel_values),
            
            # 고장 관련 특징
            'high_decibel_ratio': float(np.mean([1 if db > 60 else 0 for db in decibel_values])),
            'extreme_values_count': int(np.sum([1 if db > 70 or db < 30 else 0 for db in decibel_values])),
            'stability_score': self._calculate_stability_score(decibel_values)
        }
        
        return features
    
    def _calculate_trend(self, values: List[float]) -> float:
        """트렌드 계산"""
        if len(values) < 2:
            return 0.0
        
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        return float(slope)
    
    def _count_cycles(self, states: List[int]) -> int:
        """압축기 사이클 수 계산"""
        if len(states) < 2:
            return 0
        
        cycles = 0
        prev_state = states[0]
        
        for state in states[1:]:
            if prev_state == 0 and state == 1:  # OFF -> ON
                cycles += 1
            prev_state = state
        
        return cycles
    
    def _calculate_avg_cycle_length(self, states: List[int]) -> float:
        """평균 사이클 길이 계산"""
        if len(states) < 2:
            return 0.0
        
        cycle_lengths = []
        current_length = 0
        in_cycle = False
        
        for state in states:
            if state == 1:  # ON
                if not in_cycle:
                    in_cycle = True
                    current_length = 1
                else:
                    current_length += 1
            else:  # OFF
                if in_cycle:
                    cycle_lengths.append(current_length)
                    in_cycle = False
                    current_length = 0
        
        return float(np.mean(cycle_lengths)) if cycle_lengths else 0.0
    
    def _calculate_autocorrelation(self, values: List[float]) -> float:
        """자기상관 계산"""
        if len(values) < 10:
            return 0.0
        
        try:
            autocorr = np.corrcoef(values[:-1], values[1:])[0, 1]
            return float(autocorr) if not np.isnan(autocorr) else 0.0
        except:
            return 0.0
    
    def _calculate_periodicity(self, values: List[float]) -> float:
        """주기성 계산"""
        if len(values) < 10:
            return 0.0
        
        try:
            # FFT를 사용한 주파수 분석
            fft = np.fft.fft(values)
            freqs = np.fft.fftfreq(len(values))
            
            # 주요 주파수 성분 찾기
            power_spectrum = np.abs(fft) ** 2
            dominant_freq_idx = np.argmax(power_spectrum[1:len(power_spectrum)//2]) + 1
            dominant_freq = freqs[dominant_freq_idx]
            
            return float(abs(dominant_freq))
        except:
            return 0.0
    
    def _calculate_stability_score(self, values: List[float]) -> float:
        """안정성 점수 계산"""
        if len(values) < 2:
            return 1.0
        
        # 변동 계수 (CV) 계산
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if mean_val == 0:
            return 1.0
        
        cv = std_val / mean_val
        stability_score = 1.0 / (1.0 + cv)  # 0~1 범위로 정규화
        
        return float(stability_score)
    
    def generate_ai_labels(self, 
                          windows: List[TimeSeriesWindow]) -> List[Dict]:
        """AI 라벨 생성"""
        
        labels = []
        
        for window in windows:
            # 특징 추출
            features = self.extract_pattern_features(window)
            
            # AI 라벨 생성 (간단한 규칙 기반)
            ai_label = self._generate_rule_based_label(features, window.context)
            
            # 윈도우 ID 생성
            window_id = f"{window.start_time.strftime('%Y%m%d_%H%M%S')}_{window.window_size}"
            
            label = {
                'window_id': window_id,
                'pattern_type': ai_label['pattern_type'],
                'failure_type': ai_label['failure_type'],
                'confidence': ai_label['confidence'],
                'features': features,
                'context': window.context,
                'timestamp': datetime.now().isoformat()
            }
            
            labels.append(label)
        
        return labels
    
    def _generate_rule_based_label(self, 
                                  features: Dict,
                                  context: Dict) -> Dict:
        """규칙 기반 라벨 생성"""
        
        # 패턴 유형 결정
        pattern_type = "normal_operation"
        failure_type = "normal"
        confidence = 0.5
        
        # 점진적 성능 저하
        if (features['trend_slope'] > 0.1 and 
            features['stability_score'] > 0.7 and
            features['decibel_mean'] > 50):
            pattern_type = "gradual_degradation"
            failure_type = "bearing_wear"
            confidence = 0.8
        
        # 급격한 고장
        elif (features['volatility'] > 0.3 and 
              features['extreme_values_count'] > 5):
            pattern_type = "sudden_failure"
            failure_type = "electrical_fault"
            confidence = 0.9
        
        # 간헐적 고장
        elif (features['compressor_cycles'] > 10 and 
              features['stability_score'] < 0.5):
            pattern_type = "intermittent_failure"
            failure_type = "mechanical_looseness"
            confidence = 0.7
        
        # 고온 환경에서의 성능 저하
        elif (features['temperature_mean'] > 30 and 
              features['decibel_mean'] > 55):
            pattern_type = "thermal_stress"
            failure_type = "compressor_fatigue"
            confidence = 0.6
        
        return {
            'pattern_type': pattern_type,
            'failure_type': failure_type,
            'confidence': confidence
        }
    
    def store_learning_data(self, 
                           windows: List[TimeSeriesWindow],
                           labels: List[Dict]) -> bool:
        """학습 데이터 저장"""
        
        try:
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            for window, label in zip(windows, labels):
                window_id = label['window_id']
                
                # 시계열 윈도우 저장
                cursor.execute('''
                    INSERT OR REPLACE INTO timeseries_windows 
                    (window_id, start_time, end_time, window_size, data_count,
                     pattern_type, failure_type, confidence, features_json, context_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    window_id,
                    window.start_time.isoformat(),
                    window.end_time.isoformat(),
                    window.window_size,
                    len(window.data),
                    label['pattern_type'],
                    label['failure_type'],
                    label['confidence'],
                    json.dumps(label['features']),
                    json.dumps(window.context)
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"{len(windows)}개의 윈도우 데이터 저장 완료")
            return True
            
        except Exception as e:
            logger.error(f"학습 데이터 저장 실패: {e}")
            return False
    
    def get_learning_statistics(self) -> Dict:
        """학습 통계 조회"""
        
        try:
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            # 전체 통계
            cursor.execute('SELECT COUNT(*) FROM timeseries_windows')
            total_windows = cursor.fetchone()[0]
            
            # 패턴 유형별 통계
            cursor.execute('''
                SELECT pattern_type, COUNT(*) 
                FROM timeseries_windows 
                GROUP BY pattern_type
            ''')
            pattern_stats = dict(cursor.fetchall())
            
            # 고장 유형별 통계
            cursor.execute('''
                SELECT failure_type, COUNT(*) 
                FROM timeseries_windows 
                GROUP BY failure_type
            ''')
            failure_stats = dict(cursor.fetchall())
            
            # 신뢰도 통계
            cursor.execute('''
                SELECT AVG(confidence), MIN(confidence), MAX(confidence)
                FROM timeseries_windows
            ''')
            confidence_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'total_windows': total_windows,
                'pattern_distribution': pattern_stats,
                'failure_distribution': failure_stats,
                'confidence_stats': {
                    'average': confidence_stats[0],
                    'minimum': confidence_stats[1],
                    'maximum': confidence_stats[2]
                }
            }
            
        except Exception as e:
            logger.error(f"학습 통계 조회 실패: {e}")
            return {}
    
    def export_learning_data(self, output_path: str = "data/learning_export.json"):
        """학습 데이터 내보내기"""
        
        try:
            conn = sqlite3.connect(self.learning_db_path)
            cursor = conn.cursor()
            
            # 모든 윈도우 데이터 가져오기
            cursor.execute('''
                SELECT window_id, start_time, end_time, window_size, data_count,
                       pattern_type, failure_type, confidence, features_json, context_json
                FROM timeseries_windows
                ORDER BY created_at DESC
                LIMIT 1000
            ''')
            
            windows_data = []
            for row in cursor.fetchall():
                windows_data.append({
                    'window_id': row[0],
                    'start_time': row[1],
                    'end_time': row[2],
                    'window_size': row[3],
                    'data_count': row[4],
                    'pattern_type': row[5],
                    'failure_type': row[6],
                    'confidence': row[7],
                    'features': json.loads(row[8]),
                    'context': json.loads(row[9])
                })
            
            conn.close()
            
            # 통계 포함하여 내보내기
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'statistics': self.get_learning_statistics(),
                'windows_data': windows_data
            }
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"학습 데이터 내보내기 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"학습 데이터 내보내기 실패: {e}")
            return False

# 사용 예제
if __name__ == "__main__":
    # 시계열 학습 시스템 초기화
    tsl = TimeSeriesLearningSystem()
    
    # 테스트 데이터
    test_sensor_data = [
        {'timestamp': '2024-01-01T10:00:00', 'decibel_level': 45.0, 'temperature': 20.0, 'compressor_state': 1},
        {'timestamp': '2024-01-01T10:01:00', 'decibel_level': 46.0, 'temperature': 20.1, 'compressor_state': 1},
        # ... 더 많은 데이터
    ]
    
    test_context = {
        'current_temperature': 20.0,
        'time_of_day': 10,
        'season': 'winter'
    }
    
    # 시계열 데이터 수집
    windows = tsl.collect_time_series_data(test_sensor_data, test_context)
    
    # AI 라벨 생성
    labels = tsl.generate_ai_labels(windows)
    
    # 학습 데이터 저장
    tsl.store_learning_data(windows, labels)
    
    # 통계 조회
    stats = tsl.get_learning_statistics()
    print(f"학습 통계: {stats}")
