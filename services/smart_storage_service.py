"""
스마트 데이터 저장 서비스
- AI 분석 결과만 저장 (정상 제외, 주의/긴급만)
- 특징 데이터 압축 저장 (MFCC 등)
- 긍정적 신호 요약 저장
"""

import sqlite3
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

class SmartStorageService:
    def __init__(self, db_path: str = "data/smart_storage.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_database()
    
    def _init_database(self):
        """데이터베이스 초기화"""
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # AI 분석 결과 테이블 (주의/긴급만 저장)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    diagnosis_type TEXT NOT NULL,  -- 'warning', 'critical'
                    confidence REAL NOT NULL,
                    is_overload BOOLEAN NOT NULL,
                    risk_level TEXT NOT NULL,  -- 'low', 'medium', 'high', 'critical'
                    features_json TEXT NOT NULL,  -- 압축된 특징 데이터
                    quality_metrics_json TEXT,  -- 품질 지표
                    noise_info_json TEXT,  -- 노이즈 정보
                    processing_time_ms INTEGER,
                    file_size_bytes INTEGER,
                    file_hash TEXT,  -- 파일 해시 (중복 방지)
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 특징 데이터 테이블 (압축 저장)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compressed_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id INTEGER,
                    feature_type TEXT NOT NULL,  -- 'mfcc', 'spectral', 'temporal'
                    compressed_data BLOB NOT NULL,  -- 압축된 특징 데이터
                    original_shape TEXT NOT NULL,  -- 원본 shape 정보
                    compression_ratio REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES ai_analysis_results (id)
                )
            ''')
            
            # 긍정적 신호 요약 테이블 (하루 1-2회)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positive_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id TEXT NOT NULL,
                    summary_date DATE NOT NULL,
                    total_analyses INTEGER DEFAULT 0,
                    normal_count INTEGER DEFAULT 0,
                    avg_confidence REAL,
                    avg_quality_score REAL,
                    peak_quality_score REAL,
                    summary_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(store_id, summary_date)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_store_time ON ai_analysis_results(store_id, analysis_timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_diagnosis ON ai_analysis_results(diagnosis_type, risk_level)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_positive_summary ON positive_summaries(store_id, summary_date)')
            
            conn.commit()
    
    def should_store_analysis(self, analysis_result: Dict) -> bool:
        """분석 결과를 저장할지 판단"""
        # 정상이 아닌 경우만 저장 (주의, 긴급)
        if analysis_result.get('is_overload', False):
            return True
        
        # 신뢰도가 낮은 경우 (주의)
        confidence = analysis_result.get('confidence', 0)
        if confidence < 0.8:
            return True
        
        # 품질이 매우 낮은 경우
        quality_metrics = analysis_result.get('quality_metrics', {})
        overall_quality = quality_metrics.get('overall_quality', 100)
        if overall_quality < 30:
            return True
        
        return False
    
    def compress_features(self, features: Dict) -> Dict:
        """특징 데이터 압축"""
        compressed = {}
        
        for key, value in features.items():
            if isinstance(value, (list, np.ndarray)):
                # NumPy 배열로 변환
                if isinstance(value, list):
                    value = np.array(value)
                
                # 압축 (간단한 양자화)
                if value.dtype == np.float64:
                    # 32비트로 변환하여 용량 절반으로
                    compressed_value = value.astype(np.float32)
                else:
                    compressed_value = value
                
                compressed[key] = {
                    'data': compressed_value.tolist(),
                    'shape': list(compressed_value.shape),
                    'dtype': str(compressed_value.dtype)
                }
            else:
                compressed[key] = value
        
        return compressed
    
    def store_analysis_result(self, store_id: str, device_id: str, 
                            analysis_result: Dict, file_info: Dict = None) -> Optional[int]:
        """AI 분석 결과 저장 (주의/긴급만)"""
        
        if not self.should_store_analysis(analysis_result):
            self.logger.info(f"정상 분석 결과 - 저장하지 않음: {store_id}")
            return None
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 위험도 계산
                risk_level = self._calculate_risk_level(analysis_result)
                diagnosis_type = 'critical' if risk_level == 'critical' else 'warning'
                
                # 특징 데이터 압축
                compressed_features = self.compress_features(
                    analysis_result.get('features', {})
                )
                
                # 파일 해시 계산 (중복 방지)
                file_hash = self._calculate_file_hash(file_info) if file_info else None
                
                cursor.execute('''
                    INSERT INTO ai_analysis_results 
                    (store_id, device_id, diagnosis_type, confidence, is_overload, 
                     risk_level, features_json, quality_metrics_json, noise_info_json,
                     processing_time_ms, file_size_bytes, file_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    store_id,
                    device_id,
                    diagnosis_type,
                    analysis_result.get('confidence', 0),
                    analysis_result.get('is_overload', False),
                    risk_level,
                    json.dumps(compressed_features),
                    json.dumps(analysis_result.get('quality_metrics', {})),
                    json.dumps(analysis_result.get('noise_info', {})),
                    analysis_result.get('processing_time_ms', 0),
                    file_info.get('size', 0) if file_info else 0,
                    file_hash
                ))
                
                analysis_id = cursor.lastrowid
                
                # 압축된 특징 데이터 저장
                self._store_compressed_features(cursor, analysis_id, compressed_features)
                
                conn.commit()
                
                self.logger.info(f"분석 결과 저장 완료: {store_id} - {diagnosis_type}")
                return analysis_id
                
        except Exception as e:
            self.logger.error(f"분석 결과 저장 실패: {e}")
            return None
    
    def _calculate_risk_level(self, analysis_result: Dict) -> str:
        """위험도 계산"""
        confidence = analysis_result.get('confidence', 0)
        is_overload = analysis_result.get('is_overload', False)
        quality_metrics = analysis_result.get('quality_metrics', {})
        overall_quality = quality_metrics.get('overall_quality', 100)
        
        if is_overload and confidence > 0.9:
            return 'critical'
        elif is_overload or confidence < 0.6 or overall_quality < 20:
            return 'high'
        elif confidence < 0.8 or overall_quality < 40:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_file_hash(self, file_info: Dict) -> str:
        """파일 해시 계산"""
        import hashlib
        content = f"{file_info.get('name', '')}{file_info.get('size', 0)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _store_compressed_features(self, cursor, analysis_id: int, features: Dict):
        """압축된 특징 데이터 저장"""
        for feature_type, data in features.items():
            if isinstance(data, dict) and 'data' in data:
                compressed_data = json.dumps(data).encode('utf-8')
                original_shape = json.dumps(data.get('shape', []))
                compression_ratio = len(compressed_data) / (len(str(data)) * 8) if data else 1.0
                
                cursor.execute('''
                    INSERT INTO compressed_features 
                    (analysis_id, feature_type, compressed_data, original_shape, compression_ratio)
                    VALUES (?, ?, ?, ?, ?)
                ''', (analysis_id, feature_type, compressed_data, original_shape, compression_ratio))
    
    def update_positive_summary(self, store_id: str, analysis_result: Dict):
        """긍정적 신호 요약 업데이트"""
        today = datetime.now().date()
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 오늘의 요약 데이터 조회
                cursor.execute('''
                    SELECT * FROM positive_summaries 
                    WHERE store_id = ? AND summary_date = ?
                ''', (store_id, today))
                
                existing = cursor.fetchone()
                
                if existing:
                    # 기존 요약 업데이트
                    cursor.execute('''
                        UPDATE positive_summaries 
                        SET total_analyses = total_analyses + 1,
                            normal_count = normal_count + 1,
                            avg_confidence = (avg_confidence * total_analyses + ?) / (total_analyses + 1),
                            avg_quality_score = (avg_quality_score * total_analyses + ?) / (total_analyses + 1),
                            peak_quality_score = MAX(peak_quality_score, ?)
                        WHERE store_id = ? AND summary_date = ?
                    ''', (
                        analysis_result.get('confidence', 0),
                        analysis_result.get('quality_metrics', {}).get('overall_quality', 0),
                        analysis_result.get('quality_metrics', {}).get('overall_quality', 0),
                        store_id, today
                    ))
                else:
                    # 새로운 요약 생성
                    quality_metrics = analysis_result.get('quality_metrics', {})
                    summary_message = self._generate_positive_message(analysis_result)
                    
                    cursor.execute('''
                        INSERT INTO positive_summaries 
                        (store_id, summary_date, total_analyses, normal_count, 
                         avg_confidence, avg_quality_score, peak_quality_score, summary_message)
                        VALUES (?, ?, 1, 1, ?, ?, ?, ?)
                    ''', (
                        store_id, today,
                        analysis_result.get('confidence', 0),
                        quality_metrics.get('overall_quality', 0),
                        quality_metrics.get('overall_quality', 0),
                        summary_message
                    ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"긍정적 요약 업데이트 실패: {e}")
    
    def _generate_positive_message(self, analysis_result: Dict) -> str:
        """긍정적 메시지 생성"""
        quality_metrics = analysis_result.get('quality_metrics', {})
        overall_quality = quality_metrics.get('overall_quality', 0)
        
        if overall_quality > 80:
            return "오늘도 냉동고 상태가 매우 좋습니다! 🎉"
        elif overall_quality > 60:
            return "냉동고가 정상적으로 작동하고 있습니다. 👍"
        else:
            return "냉동고 상태를 확인해주세요. ⚠️"
    
    def get_analysis_history(self, store_id: str, days: int = 7) -> List[Dict]:
        """분석 이력 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                start_date = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    SELECT * FROM ai_analysis_results 
                    WHERE store_id = ? AND analysis_timestamp >= ?
                    ORDER BY analysis_timestamp DESC
                ''', (store_id, start_date))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'store_id': row[1],
                        'device_id': row[2],
                        'analysis_timestamp': row[3],
                        'diagnosis_type': row[4],
                        'confidence': row[5],
                        'is_overload': bool(row[6]),
                        'risk_level': row[7],
                        'features': json.loads(row[8]) if row[8] else {},
                        'quality_metrics': json.loads(row[9]) if row[9] else {},
                        'noise_info': json.loads(row[10]) if row[10] else {},
                        'processing_time_ms': row[11],
                        'file_size_bytes': row[12]
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"분석 이력 조회 실패: {e}")
            return []
    
    def get_positive_summaries(self, store_id: str, days: int = 7) -> List[Dict]:
        """긍정적 요약 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                start_date = datetime.now() - timedelta(days=days)
                
                cursor.execute('''
                    SELECT * FROM positive_summaries 
                    WHERE store_id = ? AND summary_date >= ?
                    ORDER BY summary_date DESC
                ''', (store_id, start_date))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'id': row[0],
                        'store_id': row[1],
                        'summary_date': row[2],
                        'total_analyses': row[3],
                        'normal_count': row[4],
                        'avg_confidence': row[5],
                        'avg_quality_score': row[6],
                        'peak_quality_score': row[7],
                        'summary_message': row[8],
                        'created_at': row[9]
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"긍정적 요약 조회 실패: {e}")
            return []
    
    def get_storage_stats(self) -> Dict:
        """저장소 통계 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 분석 결과 통계
                cursor.execute('SELECT COUNT(*) FROM ai_analysis_results')
                total_analyses = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM ai_analysis_results WHERE diagnosis_type = "critical"')
                critical_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM ai_analysis_results WHERE diagnosis_type = "warning"')
                warning_count = cursor.fetchone()[0]
                
                # 압축 특징 데이터 통계
                cursor.execute('SELECT COUNT(*) FROM compressed_features')
                compressed_features_count = cursor.fetchone()[0]
                
                # 긍정적 요약 통계
                cursor.execute('SELECT COUNT(*) FROM positive_summaries')
                positive_summaries_count = cursor.fetchone()[0]
                
                return {
                    'total_analyses': total_analyses,
                    'critical_count': critical_count,
                    'warning_count': warning_count,
                    'compressed_features_count': compressed_features_count,
                    'positive_summaries_count': positive_summaries_count,
                    'storage_efficiency': f"{(total_analyses - compressed_features_count) / max(total_analyses, 1) * 100:.1f}%"
                }
                
        except Exception as e:
            self.logger.error(f"저장소 통계 조회 실패: {e}")
            return {}
