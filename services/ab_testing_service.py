#!/usr/bin/env python3
"""
A/B 테스트 프레임워크
Google Analytics와 Mixpanel 스타일의 A/B 테스트 시스템
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
from scipy import stats
import random
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    """테스트 상태"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class VariantType(Enum):
    """변형 타입"""
    CONTROL = "control"
    TREATMENT = "treatment"

class MetricType(Enum):
    """지표 타입"""
    CONVERSION = "conversion"
    REVENUE = "revenue"
    EFFICIENCY = "efficiency"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    POWER_CONSUMPTION = "power_consumption"

@dataclass
class ABTest:
    """A/B 테스트 데이터 클래스"""
    test_id: str
    test_name: str
    description: str
    store_id: str
    start_date: datetime
    end_date: Optional[datetime]
    status: TestStatus
    variants: List[Dict]
    primary_metric: MetricType
    secondary_metrics: List[MetricType]
    target_sample_size: int
    confidence_level: float
    minimum_effect_size: float

@dataclass
class TestResult:
    """테스트 결과 데이터 클래스"""
    test_id: str
    variant: str
    sample_size: int
    conversion_rate: float
    revenue_per_user: float
    confidence_interval: Tuple[float, float]
    p_value: float
    is_significant: bool
    effect_size: float
    power: float

class ABTestingService:
    """A/B 테스트 서비스"""
    
    def __init__(self, db_path: str = "data/analytics.db"):
        self.db_path = db_path
        self.conn = None
        self.active_tests = {}
        
        # 초기화
        self._init_database()
        
        logger.info("A/B 테스트 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # A/B 테스트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ab_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT UNIQUE NOT NULL,
                    test_name TEXT NOT NULL,
                    description TEXT,
                    store_id TEXT NOT NULL,
                    start_date DATETIME NOT NULL,
                    end_date DATETIME,
                    status TEXT NOT NULL,
                    variants TEXT NOT NULL,
                    primary_metric TEXT NOT NULL,
                    secondary_metrics TEXT,
                    target_sample_size INTEGER,
                    confidence_level REAL,
                    minimum_effect_size REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 테스트 참여자 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    variant TEXT NOT NULL,
                    assigned_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(test_id, user_id)
                )
            ''')
            
            # 테스트 이벤트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    event_value REAL,
                    timestamp DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 테스트 결과 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    variant TEXT NOT NULL,
                    sample_size INTEGER,
                    conversion_rate REAL,
                    revenue_per_user REAL,
                    confidence_interval_lower REAL,
                    confidence_interval_upper REAL,
                    p_value REAL,
                    is_significant BOOLEAN,
                    effect_size REAL,
                    power REAL,
                    calculated_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("A/B 테스트 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def create_test(self, test: ABTest) -> bool:
        """A/B 테스트 생성"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO ab_tests 
                (test_id, test_name, description, store_id, start_date, end_date, status,
                 variants, primary_metric, secondary_metrics, target_sample_size,
                 confidence_level, minimum_effect_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                test.test_id,
                test.test_name,
                test.description,
                test.store_id,
                test.start_date,
                test.end_date,
                test.status.value,
                json.dumps(test.variants),
                test.primary_metric.value,
                json.dumps([m.value for m in test.secondary_metrics]),
                test.target_sample_size,
                test.confidence_level,
                test.minimum_effect_size
            ))
            
            self.conn.commit()
            logger.info(f"A/B 테스트 생성 완료: {test.test_id}")
            return True
            
        except Exception as e:
            logger.error(f"A/B 테스트 생성 오류: {e}")
            return False
    
    def start_test(self, test_id: str) -> bool:
        """테스트 시작"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                UPDATE ab_tests 
                SET status = ?, start_date = ?
                WHERE test_id = ?
            ''', (TestStatus.ACTIVE.value, datetime.now(), test_id))
            
            self.conn.commit()
            
            # 활성 테스트에 추가
            self.active_tests[test_id] = self.get_test(test_id)
            
            logger.info(f"A/B 테스트 시작: {test_id}")
            return True
            
        except Exception as e:
            logger.error(f"A/B 테스트 시작 오류: {e}")
            return False
    
    def stop_test(self, test_id: str) -> bool:
        """테스트 중지"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                UPDATE ab_tests 
                SET status = ?, end_date = ?
                WHERE test_id = ?
            ''', (TestStatus.COMPLETED.value, datetime.now(), test_id))
            
            self.conn.commit()
            
            # 활성 테스트에서 제거
            if test_id in self.active_tests:
                del self.active_tests[test_id]
            
            logger.info(f"A/B 테스트 중지: {test_id}")
            return True
            
        except Exception as e:
            logger.error(f"A/B 테스트 중지 오류: {e}")
            return False
    
    def assign_user_to_variant(self, test_id: str, user_id: str) -> str:
        """사용자를 변형에 할당"""
        try:
            # 이미 할당된 경우 기존 할당 반환
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT variant FROM test_participants 
                WHERE test_id = ? AND user_id = ?
            ''', (test_id, user_id))
            
            result = cursor.fetchone()
            if result:
                return result[0]
            
            # 테스트 정보 조회
            test = self.get_test(test_id)
            if not test or test.status != TestStatus.ACTIVE:
                return "control"  # 기본값
            
            # 변형 할당 (해시 기반 일관된 할당)
            assignment_hash = hashlib.md5(f"{test_id}_{user_id}".encode()).hexdigest()
            assignment_value = int(assignment_hash[:8], 16) / (16**8)
            
            # 변형별 할당 비율 계산
            total_weight = sum(variant.get('weight', 1) for variant in test.variants)
            cumulative_weight = 0
            
            for variant in test.variants:
                cumulative_weight += variant.get('weight', 1)
                if assignment_value < cumulative_weight / total_weight:
                    assigned_variant = variant['name']
                    break
            else:
                assigned_variant = test.variants[-1]['name']
            
            # 할당 저장
            cursor.execute('''
                INSERT INTO test_participants (test_id, user_id, variant, assigned_at)
                VALUES (?, ?, ?, ?)
            ''', (test_id, user_id, assigned_variant, datetime.now()))
            
            self.conn.commit()
            
            logger.info(f"사용자 할당 완료: {user_id} -> {assigned_variant}")
            return assigned_variant
            
        except Exception as e:
            logger.error(f"사용자 할당 오류: {e}")
            return "control"
    
    def track_event(self, test_id: str, user_id: str, event_name: str, event_value: float = 1.0) -> bool:
        """테스트 이벤트 추적"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO test_events (test_id, user_id, event_name, event_value, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (test_id, user_id, event_name, event_value, datetime.now()))
            
            self.conn.commit()
            logger.info(f"테스트 이벤트 추적: {test_id} - {event_name}")
            return True
            
        except Exception as e:
            logger.error(f"테스트 이벤트 추적 오류: {e}")
            return False
    
    def get_test(self, test_id: str) -> Optional[ABTest]:
        """테스트 정보 조회"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ab_tests WHERE test_id = ?
            ''', (test_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            return ABTest(
                test_id=result[1],
                test_name=result[2],
                description=result[3],
                store_id=result[4],
                start_date=datetime.fromisoformat(result[5]),
                end_date=datetime.fromisoformat(result[6]) if result[6] else None,
                status=TestStatus(result[7]),
                variants=json.loads(result[8]),
                primary_metric=MetricType(result[9]),
                secondary_metrics=[MetricType(m) for m in json.loads(result[10] or '[]')],
                target_sample_size=result[11],
                confidence_level=result[12],
                minimum_effect_size=result[13]
            )
            
        except Exception as e:
            logger.error(f"테스트 정보 조회 오류: {e}")
            return None
    
    def get_test_results(self, test_id: str) -> List[TestResult]:
        """테스트 결과 조회"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT * FROM test_results 
                WHERE test_id = ? 
                ORDER BY calculated_at DESC
            ''', (test_id,))
            
            results = []
            for result in cursor.fetchall():
                results.append(TestResult(
                    test_id=result[1],
                    variant=result[2],
                    sample_size=result[3],
                    conversion_rate=result[4],
                    revenue_per_user=result[5],
                    confidence_interval=(result[6], result[7]),
                    p_value=result[8],
                    is_significant=bool(result[9]),
                    effect_size=result[10],
                    power=result[11]
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"테스트 결과 조회 오류: {e}")
            return []
    
    def calculate_test_results(self, test_id: str) -> List[TestResult]:
        """테스트 결과 계산"""
        try:
            test = self.get_test(test_id)
            if not test:
                return []
            
            # 테스트 데이터 조회
            query = '''
                SELECT tp.variant, te.event_name, te.event_value, te.timestamp
                FROM test_participants tp
                JOIN test_events te ON tp.test_id = te.test_id AND tp.user_id = te.user_id
                WHERE tp.test_id = ?
            '''
            
            df = pd.read_sql_query(query, self.conn, params=(test_id,))
            
            if df.empty:
                return []
            
            results = []
            
            # 변형별 결과 계산
            for variant in test.variants:
                variant_name = variant['name']
                variant_data = df[df['variant'] == variant_name]
                
                if variant_data.empty:
                    continue
                
                # 기본 지표 계산
                sample_size = len(variant_data['user_id'].unique())
                
                # 전환율 계산
                if test.primary_metric == MetricType.CONVERSION:
                    conversion_events = variant_data[variant_data['event_name'] == 'conversion']
                    conversion_rate = len(conversion_events) / sample_size if sample_size > 0 else 0
                else:
                    conversion_rate = 0
                
                # 사용자당 수익 계산
                if test.primary_metric == MetricType.REVENUE:
                    revenue_events = variant_data[variant_data['event_name'] == 'purchase']
                    total_revenue = revenue_events['event_value'].sum()
                    revenue_per_user = total_revenue / sample_size if sample_size > 0 else 0
                else:
                    revenue_per_user = 0
                
                # 통계적 유의성 검정
                p_value, is_significant, effect_size, power = self._calculate_statistical_significance(
                    test_id, variant_name, test.confidence_level
                )
                
                # 신뢰구간 계산
                confidence_interval = self._calculate_confidence_interval(
                    conversion_rate, sample_size, test.confidence_level
                )
                
                result = TestResult(
                    test_id=test_id,
                    variant=variant_name,
                    sample_size=sample_size,
                    conversion_rate=conversion_rate,
                    revenue_per_user=revenue_per_user,
                    confidence_interval=confidence_interval,
                    p_value=p_value,
                    is_significant=is_significant,
                    effect_size=effect_size,
                    power=power
                )
                
                results.append(result)
                
                # 결과 저장
                self._save_test_result(result)
            
            return results
            
        except Exception as e:
            logger.error(f"테스트 결과 계산 오류: {e}")
            return []
    
    def _calculate_statistical_significance(self, test_id: str, variant: str, confidence_level: float) -> Tuple[float, bool, float, float]:
        """통계적 유의성 계산"""
        try:
            # 변형별 데이터 조회
            query = '''
                SELECT tp.variant, te.event_value
                FROM test_participants tp
                JOIN test_events te ON tp.test_id = te.test_id AND tp.user_id = te.user_id
                WHERE tp.test_id = ? AND te.event_name = 'conversion'
            '''
            
            df = pd.read_sql_query(query, self.conn, params=(test_id,))
            
            if df.empty:
                return 1.0, False, 0.0, 0.0
            
            # 변형별 그룹
            groups = {}
            for variant_name in df['variant'].unique():
                groups[variant_name] = df[df['variant'] == variant_name]['event_value'].values
            
            if len(groups) < 2:
                return 1.0, False, 0.0, 0.0
            
            # t-검정 수행
            variant_names = list(groups.keys())
            group1 = groups[variant_names[0]]
            group2 = groups[variant_names[1]]
            
            t_stat, p_value = stats.ttest_ind(group1, group2)
            
            # 유의성 판정
            alpha = 1 - confidence_level
            is_significant = p_value < alpha
            
            # 효과 크기 (Cohen's d)
            pooled_std = np.sqrt(((len(group1) - 1) * np.var(group1, ddof=1) + 
                                 (len(group2) - 1) * np.var(group2, ddof=1)) / 
                                (len(group1) + len(group2) - 2))
            effect_size = (np.mean(group1) - np.mean(group2)) / pooled_std if pooled_std > 0 else 0
            
            # 검정력 계산
            power = self._calculate_power(effect_size, len(group1), len(group2), alpha)
            
            return p_value, is_significant, abs(effect_size), power
            
        except Exception as e:
            logger.error(f"통계적 유의성 계산 오류: {e}")
            return 1.0, False, 0.0, 0.0
    
    def _calculate_confidence_interval(self, proportion: float, sample_size: int, confidence_level: float) -> Tuple[float, float]:
        """신뢰구간 계산"""
        try:
            if sample_size == 0:
                return (0.0, 0.0)
            
            # 정규 근사 사용
            z_score = stats.norm.ppf(1 - (1 - confidence_level) / 2)
            margin_of_error = z_score * np.sqrt(proportion * (1 - proportion) / sample_size)
            
            lower_bound = max(0, proportion - margin_of_error)
            upper_bound = min(1, proportion + margin_of_error)
            
            return (lower_bound, upper_bound)
            
        except Exception as e:
            logger.error(f"신뢰구간 계산 오류: {e}")
            return (0.0, 0.0)
    
    def _calculate_power(self, effect_size: float, n1: int, n2: int, alpha: float) -> float:
        """검정력 계산"""
        try:
            # Cohen's d를 사용한 검정력 계산
            n_eff = (n1 * n2) / (n1 + n2)  # 유효 표본 크기
            power = stats.power.ttest_power(effect_size, n_eff, alpha)
            return power
            
        except Exception as e:
            logger.error(f"검정력 계산 오류: {e}")
            return 0.0
    
    def _save_test_result(self, result: TestResult) -> bool:
        """테스트 결과 저장"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO test_results 
                (test_id, variant, sample_size, conversion_rate, revenue_per_user,
                 confidence_interval_lower, confidence_interval_upper, p_value,
                 is_significant, effect_size, power, calculated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.test_id,
                result.variant,
                result.sample_size,
                result.conversion_rate,
                result.revenue_per_user,
                result.confidence_interval[0],
                result.confidence_interval[1],
                result.p_value,
                result.is_significant,
                result.effect_size,
                result.power,
                datetime.now()
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"테스트 결과 저장 오류: {e}")
            return False
    
    def get_active_tests(self) -> List[ABTest]:
        """활성 테스트 목록 조회"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT test_id FROM ab_tests WHERE status = ?
            ''', (TestStatus.ACTIVE.value,))
            
            active_test_ids = [row[0] for row in cursor.fetchall()]
            active_tests = []
            
            for test_id in active_test_ids:
                test = self.get_test(test_id)
                if test:
                    active_tests.append(test)
            
            return active_tests
            
        except Exception as e:
            logger.error(f"활성 테스트 조회 오류: {e}")
            return []
    
    def get_test_summary(self, test_id: str) -> Dict:
        """테스트 요약 정보 조회"""
        try:
            test = self.get_test(test_id)
            if not test:
                return {'error': '테스트를 찾을 수 없습니다'}
            
            results = self.get_test_results(test_id)
            
            # 기본 통계
            total_participants = sum(r.sample_size for r in results)
            total_events = len(pd.read_sql_query(
                'SELECT * FROM test_events WHERE test_id = ?', 
                self.conn, params=(test_id,)
            ))
            
            # 변형별 성과
            variant_performance = {}
            for result in results:
                variant_performance[result.variant] = {
                    'sample_size': result.sample_size,
                    'conversion_rate': result.conversion_rate,
                    'revenue_per_user': result.revenue_per_user,
                    'is_significant': result.is_significant,
                    'p_value': result.p_value
                }
            
            summary = {
                'test_id': test_id,
                'test_name': test.test_name,
                'status': test.status.value,
                'total_participants': total_participants,
                'total_events': total_events,
                'start_date': test.start_date.isoformat(),
                'end_date': test.end_date.isoformat() if test.end_date else None,
                'variant_performance': variant_performance,
                'primary_metric': test.primary_metric.value
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"테스트 요약 조회 오류: {e}")
            return {'error': str(e)}

# 전역 인스턴스
ab_testing_service = ABTestingService()
