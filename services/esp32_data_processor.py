"""
ESP32 센서 데이터 전처리 및 특징 추출 모듈
"""

import json
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ESP32DataProcessor:
    """ESP32 센서 데이터 전처리 및 특징 추출 클래스"""
    
    def __init__(self, data_dir: str = "data/esp32_features"):
        self.data_dir = data_dir
        self.feature_columns = [
            'rms_energy', 'spectral_centroid', 'zero_crossing_rate', 
            'decibel_level', 'compressor_state', 'anomaly_score', 
            'efficiency_score', 'sound_type', 'intensity_level',
            'spectral_rolloff', 'spectral_bandwidth', 'spectral_contrast',
            'spectral_flatness', 'spectral_skewness', 'spectral_kurtosis',
            'harmonic_ratio', 'inharmonicity', 'attack_time', 'decay_time',
            'sustain_level', 'release_time', 'frequency_dominance'
        ]
        
    def collect_normal_data(self, hours: int = 24, device_id: Optional[str] = None) -> List[Dict]:
        """
        정상 운영 데이터 수집
        
        Args:
            hours: 수집할 시간 범위 (시간)
            device_id: 특정 디바이스 ID (None이면 모든 디바이스)
            
        Returns:
            정상 데이터 리스트
        """
        try:
            logger.info(f"정상 데이터 수집 시작 - {hours}시간, 디바이스: {device_id}")
            
            # 데이터 디렉토리 확인
            if not os.path.exists(self.data_dir):
                logger.warning(f"데이터 디렉토리가 존재하지 않습니다: {self.data_dir}")
                return []
            
            # JSON 파일들 읽기
            all_data = []
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.data_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # 배열인 경우 각 항목을 개별적으로 추가
                        if isinstance(data, list):
                            all_data.extend(data)
                        else:
                            all_data.append(data)
                            
                    except Exception as e:
                        logger.error(f"파일 읽기 오류 {filename}: {e}")
                        continue
            
            if not all_data:
                logger.warning("수집된 데이터가 없습니다.")
                return []
            
            # 시간 필터링
            cutoff_time = datetime.now() - timedelta(hours=hours)
            filtered_data = []
            
            for item in all_data:
                try:
                    # 타임스탬프 변환
                    timestamp = item.get('timestamp') or item.get('server_timestamp')
                    if timestamp:
                        item_time = datetime.fromtimestamp(timestamp / 1000)
                        if item_time >= cutoff_time:
                            # 디바이스 ID 필터링
                            if device_id is None or item.get('device_id') == device_id:
                                filtered_data.append(item)
                except Exception as e:
                    logger.error(f"데이터 필터링 오류: {e}")
                    continue
            
            # 정상 데이터만 필터링 (compressor_state와 decibel_level 기반)
            normal_data = self._filter_normal_data(filtered_data)
            
            logger.info(f"정상 데이터 수집 완료: {len(normal_data)}개")
            return normal_data
            
        except Exception as e:
            logger.error(f"정상 데이터 수집 실패: {e}")
            return []
    
    def _filter_normal_data(self, data: List[Dict]) -> List[Dict]:
        """
        정상 데이터 필터링
        
        Args:
            data: 원본 데이터
            
        Returns:
            정상 데이터만 필터링된 리스트
        """
        normal_data = []
        
        for item in data:
            try:
                # 기본 유효성 검사
                if not self._is_valid_data(item):
                    continue
                
                # 압축기 상태가 정상 범위인지 확인
                compressor_state = item.get('compressor_state', 0)
                decibel_level = item.get('decibel_level', 0)
                
                # 정상 범위 정의 (실제 운영 데이터에 따라 조정 필요)
                if (0 <= compressor_state <= 1 and 
                    20 <= decibel_level <= 80 and
                    item.get('rms_energy', 0) > 0):
                    normal_data.append(item)
                    
            except Exception as e:
                logger.error(f"데이터 필터링 중 오류: {e}")
                continue
        
        return normal_data
    
    def _is_valid_data(self, item: Dict) -> bool:
        """데이터 유효성 검사"""
        required_fields = ['rms_energy', 'decibel_level', 'timestamp']
        return all(field in item for field in required_fields)
    
    def extract_features(self, data: List[Dict]) -> np.ndarray:
        """
        통계적 특징 추출
        
        Args:
            data: 센서 데이터 리스트
            
        Returns:
            추출된 특징 배열 (n_samples, n_features)
        """
        try:
            if not data:
                logger.warning("추출할 데이터가 없습니다.")
                return np.array([])
            
            logger.info(f"특징 추출 시작 - {len(data)}개 데이터")
            
            # DataFrame으로 변환
            df = pd.DataFrame(data)
            
            # 기본 특징 추출
            features = []
            
            for _, row in df.iterrows():
                feature_vector = self._extract_single_features(row)
                features.append(feature_vector)
            
            features_array = np.array(features)
            
            # 통계적 특징 추가 (시계열 데이터가 충분한 경우)
            if len(data) >= 10:
                statistical_features = self._extract_statistical_features(data)
                if statistical_features is not None:
                    # 각 샘플에 통계적 특징 추가
                    features_array = np.column_stack([features_array, statistical_features])
            
            logger.info(f"특징 추출 완료 - 형태: {features_array.shape}")
            return features_array
            
        except Exception as e:
            logger.error(f"특징 추출 실패: {e}")
            return np.array([])
    
    def _extract_single_features(self, row: pd.Series) -> np.ndarray:
        """단일 데이터 포인트의 특징 추출"""
        features = []
        
        # 기본 센서 값들
        for col in self.feature_columns:
            value = row.get(col, 0)
            if pd.isna(value):
                value = 0
            features.append(float(value))
        
        # 파생 특징들
        rms_energy = row.get('rms_energy', 0)
        decibel_level = row.get('decibel_level', 0)
        compressor_state = row.get('compressor_state', 0)
        
        # RMS를 데시벨로 변환 (일관성 확인)
        rms_to_db = 20 * np.log10(rms_energy) if rms_energy > 0 else 0
        features.append(rms_to_db)
        
        # 데시벨과 RMS의 차이 (센서 보정 확인)
        db_diff = abs(decibel_level - rms_to_db)
        features.append(db_diff)
        
        # 압축기 상태 기반 특징
        features.append(1 if compressor_state > 0.5 else 0)
        
        # 효율성 점수 (0-1 범위로 정규화)
        efficiency = row.get('efficiency_score', 0.5)
        features.append(max(0, min(1, efficiency)))
        
        # 이상 점수 (0-1 범위로 정규화)
        anomaly = row.get('anomaly_score', 0.5)
        features.append(max(0, min(1, anomaly)))
        
        return np.array(features)
    
    def _extract_statistical_features(self, data: List[Dict]) -> Optional[np.ndarray]:
        """통계적 특징 추출 (시계열 데이터 기반)"""
        try:
            if len(data) < 5:
                return None
            
            # 최근 데이터로 통계 계산
            recent_data = data[-10:]  # 최근 10개 데이터
            
            df = pd.DataFrame(recent_data)
            
            statistical_features = []
            
            # RMS 통계
            rms_values = df['rms_energy'].values
            statistical_features.extend([
                np.mean(rms_values),
                np.std(rms_values),
                np.max(rms_values) - np.min(rms_values),  # 범위
                np.percentile(rms_values, 75) - np.percentile(rms_values, 25)  # IQR
            ])
            
            # 데시벨 통계
            db_values = df['decibel_level'].values
            statistical_features.extend([
                np.mean(db_values),
                np.std(db_values),
                np.max(db_values) - np.min(db_values),
                np.percentile(db_values, 75) - np.percentile(db_values, 25)
            ])
            
            # 압축기 상태 통계
            compressor_states = df['compressor_state'].values
            on_ratio = np.mean(compressor_states > 0.5)
            statistical_features.append(on_ratio)
            
            # 변화율 계산
            if len(rms_values) > 1:
                rms_change = np.diff(rms_values)
                db_change = np.diff(db_values)
                
                statistical_features.extend([
                    np.mean(np.abs(rms_change)),
                    np.std(rms_change),
                    np.mean(np.abs(db_change)),
                    np.std(db_change)
                ])
            else:
                statistical_features.extend([0, 0, 0, 0])
            
            # 모든 샘플에 동일한 통계적 특징 적용
            n_samples = len(data)
            return np.tile(statistical_features, (n_samples, 1))
            
        except Exception as e:
            logger.error(f"통계적 특징 추출 실패: {e}")
            return None
    
    def prepare_training_data(self, hours: int = 24, device_id: Optional[str] = None) -> Tuple[np.ndarray, List[Dict]]:
        """
        학습용 데이터 준비
        
        Args:
            hours: 수집할 시간 범위
            device_id: 특정 디바이스 ID
            
        Returns:
            (특징 배열, 원본 데이터)
        """
        try:
            # 정상 데이터 수집
            normal_data = self.collect_normal_data(hours, device_id)
            
            if not normal_data:
                logger.warning("학습용 정상 데이터가 없습니다.")
                return np.array([]), []
            
            # 특징 추출
            features = self.extract_features(normal_data)
            
            logger.info(f"학습용 데이터 준비 완료 - {len(normal_data)}개 샘플, {features.shape[1]}개 특징")
            return features, normal_data
            
        except Exception as e:
            logger.error(f"학습용 데이터 준비 실패: {e}")
            return np.array([]), []
    
    def get_data_summary(self, data: List[Dict]) -> Dict:
        """데이터 요약 정보 반환"""
        if not data:
            return {"count": 0, "devices": [], "time_range": None}
        
        df = pd.DataFrame(data)
        
        summary = {
            "count": len(data),
            "devices": df['device_id'].unique().tolist() if 'device_id' in df.columns else [],
            "time_range": {
                "start": df['timestamp'].min() if 'timestamp' in df.columns else None,
                "end": df['timestamp'].max() if 'timestamp' in df.columns else None
            },
            "features": {
                "rms_energy": {
                    "mean": df['rms_energy'].mean() if 'rms_energy' in df.columns else 0,
                    "std": df['rms_energy'].std() if 'rms_energy' in df.columns else 0,
                    "min": df['rms_energy'].min() if 'rms_energy' in df.columns else 0,
                    "max": df['rms_energy'].max() if 'rms_energy' in df.columns else 0
                },
                "decibel_level": {
                    "mean": df['decibel_level'].mean() if 'decibel_level' in df.columns else 0,
                    "std": df['decibel_level'].std() if 'decibel_level' in df.columns else 0,
                    "min": df['decibel_level'].min() if 'decibel_level' in df.columns else 0,
                    "max": df['decibel_level'].max() if 'decibel_level' in df.columns else 0
                }
            }
        }
        
        return summary

# 사용 예제
if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 데이터 프로세서 초기화
    processor = ESP32DataProcessor()
    
    # 정상 데이터 수집 (최근 24시간)
    normal_data = processor.collect_normal_data(hours=24)
    print(f"수집된 정상 데이터: {len(normal_data)}개")
    
    # 특징 추출
    if normal_data:
        features = processor.extract_features(normal_data)
        print(f"추출된 특징 형태: {features.shape}")
        
        # 데이터 요약
        summary = processor.get_data_summary(normal_data)
        print(f"데이터 요약: {summary}")
