#!/usr/bin/env python3
"""
데이터 분석 및 통계 서비스
AWS CloudWatch 스타일의 로그 분석 및 통계 제공
"""

import time
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
from sqlite3 import connect
import json
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrendAnalysis:
    """트렌드 분석 결과"""
    metric_name: str
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0-1
    change_percentage: float
    confidence: float
    prediction_next_week: float
    recommendation: str

@dataclass
class AnomalyPattern:
    """이상 패턴 분석"""
    pattern_type: str
    frequency: int
    severity: str
    affected_devices: List[str]
    time_pattern: str
    description: str
    recommendation: str

@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    metric_name: str
    current_value: float
    average_value: float
    min_value: float
    max_value: float
    standard_deviation: float
    percentile_95: float
    percentile_99: float
    trend: str

class AnalyticsService:
    """데이터 분석 및 통계 서비스 (AWS CloudWatch 스타일)"""
    
    def __init__(self, db_path: str = 'data/sensor_data.db'):
        self.db_path = db_path
        self.cache = {}
        self.cache_ttl = 600  # 10분 캐시
        
        logger.info("분석 서비스 초기화 완료")
    
    def analyze_trends(self, store_id: str = None, days: int = 30) -> List[TrendAnalysis]:
        """트렌드 분석"""
        try:
            # 센서 데이터 조회
            sensor_data = self._get_sensor_data_for_analysis(store_id, days)
            
            if not sensor_data:
                return []
            
            trends = []
            
            # 온도 트렌드 분석
            temp_trend = self._analyze_metric_trend(sensor_data, 'temperature', '온도')
            if temp_trend:
                trends.append(temp_trend)
            
            # 진동 트렌드 분석
            vib_trend = self._analyze_metric_trend(sensor_data, 'vibration', '진동')
            if vib_trend:
                trends.append(vib_trend)
            
            # 전력 소비 트렌드 분석
            power_trend = self._analyze_metric_trend(sensor_data, 'power_consumption', '전력 소비')
            if power_trend:
                trends.append(power_trend)
            
            # 오디오 레벨 트렌드 분석
            audio_trend = self._analyze_metric_trend(sensor_data, 'audio_level', '오디오 레벨')
            if audio_trend:
                trends.append(audio_trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"트렌드 분석 실패: {e}")
            return []
    
    def _get_sensor_data_for_analysis(self, store_id: str = None, days: int = 30) -> pd.DataFrame:
        """분석용 센서 데이터 조회"""
        try:
            with connect(self.db_path) as conn:
                start_timestamp = time.time() - (days * 86400)
                
                if store_id:
                    query = '''
                        SELECT 
                            timestamp,
                            temperature,
                            vibration_x,
                            vibration_y,
                            vibration_z,
                            power_consumption,
                            audio_level,
                            sensor_quality
                        FROM sensor_readings 
                        WHERE device_id = ? AND timestamp > ?
                        ORDER BY timestamp
                    '''
                    df = pd.read_sql_query(query, conn, params=(store_id, start_timestamp))
                else:
                    query = '''
                        SELECT 
                            timestamp,
                            temperature,
                            vibration_x,
                            vibration_y,
                            vibration_z,
                            power_consumption,
                            audio_level,
                            sensor_quality
                        FROM sensor_readings 
                        WHERE timestamp > ?
                        ORDER BY timestamp
                    '''
                    df = pd.read_sql_query(query, conn, params=(start_timestamp,))
                
                # 진동 레벨 계산
                df['vibration'] = np.sqrt(df['vibration_x']**2 + df['vibration_y']**2 + df['vibration_z']**2)
                
                # 시간 컬럼 추가
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df['hour'] = df['datetime'].dt.hour
                df['day_of_week'] = df['datetime'].dt.dayofweek
                
                return df
                
        except Exception as e:
            logger.error(f"센서 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def _analyze_metric_trend(self, df: pd.DataFrame, metric: str, metric_name: str) -> Optional[TrendAnalysis]:
        """개별 메트릭 트렌드 분석"""
        try:
            if metric not in df.columns or df[metric].isna().all():
                return None
            
            # 데이터 정리
            data = df[metric].dropna()
            if len(data) < 10:
                return None
            
            # 선형 회귀 분석
            X = np.arange(len(data)).reshape(-1, 1)
            y = data.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # 트렌드 방향 결정
            slope = model.coef_[0]
            if slope > 0.1:
                trend_direction = "increasing"
            elif slope < -0.1:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
            
            # 트렌드 강도 계산
            trend_strength = min(1.0, abs(slope) / np.std(y))
            
            # 변화율 계산
            first_half = data[:len(data)//2].mean()
            second_half = data[len(data)//2:].mean()
            change_percentage = ((second_half - first_half) / first_half * 100) if first_half != 0 else 0
            
            # 신뢰도 계산 (R²)
            y_pred = model.predict(X)
            r2 = model.score(X, y)
            confidence = max(0, min(1, r2))
            
            # 다음 주 예측
            next_week_value = model.predict([[len(data) + 7 * 24 * 6]])[0]  # 7일 후 (10분 간격)
            
            # 권장사항 생성
            recommendation = self._generate_recommendation(metric, trend_direction, change_percentage, next_week_value)
            
            return TrendAnalysis(
                metric_name=metric_name,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                change_percentage=change_percentage,
                confidence=confidence,
                prediction_next_week=next_week_value,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"메트릭 트렌드 분석 실패: {e}")
            return None
    
    def _generate_recommendation(self, metric: str, trend_direction: str, change_percentage: float, predicted_value: float) -> str:
        """권장사항 생성"""
        try:
            if metric == 'temperature':
                if trend_direction == "increasing" and change_percentage > 10:
                    return "냉동고 온도가 상승하고 있습니다. 냉각 시스템 점검이 필요합니다."
                elif trend_direction == "decreasing" and change_percentage < -20:
                    return "냉동고 온도가 급격히 하락했습니다. 시스템 점검이 필요합니다."
                else:
                    return "온도가 안정적으로 유지되고 있습니다."
            
            elif metric == 'vibration':
                if trend_direction == "increasing" and change_percentage > 15:
                    return "압축기 진동이 증가하고 있습니다. 베어링 점검이 필요합니다."
                elif predicted_value > 2.0:
                    return "압축기 진동이 위험 수준입니다. 즉시 점검이 필요합니다."
                else:
                    return "진동 레벨이 정상 범위입니다."
            
            elif metric == 'power_consumption':
                if trend_direction == "increasing" and change_percentage > 20:
                    return "전력 소비가 증가하고 있습니다. 에너지 효율성 점검이 필요합니다."
                elif predicted_value > 90:
                    return "전력 소비가 위험 수준입니다. 부하 분산이 필요합니다."
                else:
                    return "전력 소비가 효율적으로 관리되고 있습니다."
            
            elif metric == 'audio_level':
                if trend_direction == "increasing" and change_percentage > 25:
                    return "압축기 소음이 증가하고 있습니다. 소음 원인 점검이 필요합니다."
                elif predicted_value > 1000:
                    return "압축기 소음이 위험 수준입니다. 즉시 점검이 필요합니다."
                else:
                    return "소음 레벨이 정상 범위입니다."
            
            else:
                return "시스템이 정상적으로 작동하고 있습니다."
                
        except Exception as e:
            logger.error(f"권장사항 생성 실패: {e}")
            return "시스템을 점검해주세요."
    
    def detect_anomaly_patterns(self, store_id: str = None, days: int = 30) -> List[AnomalyPattern]:
        """이상 패턴 감지"""
        try:
            # 이상 감지 데이터 조회
            anomaly_data = self._get_anomaly_data(store_id, days)
            
            if anomaly_data.empty:
                return []
            
            patterns = []
            
            # 시간대별 패턴 분석
            time_patterns = self._analyze_time_patterns(anomaly_data)
            patterns.extend(time_patterns)
            
            # 디바이스별 패턴 분석
            device_patterns = self._analyze_device_patterns(anomaly_data)
            patterns.extend(device_patterns)
            
            # 심각도별 패턴 분석
            severity_patterns = self._analyze_severity_patterns(anomaly_data)
            patterns.extend(severity_patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"이상 패턴 감지 실패: {e}")
            return []
    
    def _get_anomaly_data(self, store_id: str = None, days: int = 30) -> pd.DataFrame:
        """이상 감지 데이터 조회"""
        try:
            with connect(self.db_path) as conn:
                start_timestamp = time.time() - (days * 86400)
                
                if store_id:
                    query = '''
                        SELECT 
                            device_id,
                            timestamp,
                            anomaly_type,
                            severity,
                            confidence,
                            description
                        FROM anomalies 
                        WHERE device_id = ? AND timestamp > ?
                        ORDER BY timestamp
                    '''
                    df = pd.read_sql_query(query, conn, params=(store_id, start_timestamp))
                else:
                    query = '''
                        SELECT 
                            device_id,
                            timestamp,
                            anomaly_type,
                            severity,
                            confidence,
                            description
                        FROM anomalies 
                        WHERE timestamp > ?
                        ORDER BY timestamp
                    '''
                    df = pd.read_sql_query(query, conn, params=(start_timestamp,))
                
                # 시간 컬럼 추가
                df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
                df['hour'] = df['datetime'].dt.hour
                df['day_of_week'] = df['datetime'].dt.dayofweek
                df['date'] = df['datetime'].dt.date
                
                return df
                
        except Exception as e:
            logger.error(f"이상 감지 데이터 조회 실패: {e}")
            return pd.DataFrame()
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> List[AnomalyPattern]:
        """시간대별 패턴 분석"""
        try:
            patterns = []
            
            # 시간대별 이상 발생 빈도
            hourly_counts = df.groupby('hour').size()
            peak_hours = hourly_counts.nlargest(3)
            
            for hour, count in peak_hours.items():
                if count > hourly_counts.mean() * 1.5:  # 평균의 1.5배 이상
                    patterns.append(AnomalyPattern(
                        pattern_type="시간대별 집중",
                        frequency=count,
                        severity="medium",
                        affected_devices=df[df['hour'] == hour]['device_id'].unique().tolist(),
                        time_pattern=f"{hour}시대 집중 발생",
                        description=f"{hour}시대에 이상이 {count}회 발생했습니다.",
                        recommendation=f"{hour}시대에 집중 모니터링을 강화하세요."
                    ))
            
            # 요일별 패턴
            daily_counts = df.groupby('day_of_week').size()
            if len(daily_counts) > 0:
                peak_day = daily_counts.idxmax()
                day_names = ['월', '화', '수', '목', '금', '토', '일']
                
                if daily_counts[peak_day] > daily_counts.mean() * 1.3:
                    patterns.append(AnomalyPattern(
                        pattern_type="요일별 패턴",
                        frequency=daily_counts[peak_day],
                        severity="low",
                        affected_devices=df[df['day_of_week'] == peak_day]['device_id'].unique().tolist(),
                        time_pattern=f"{day_names[peak_day]}요일 집중 발생",
                        description=f"{day_names[peak_day]}요일에 이상이 {daily_counts[peak_day]}회 발생했습니다.",
                        recommendation=f"{day_names[peak_day]}요일에 예방 점검을 실시하세요."
                    ))
            
            return patterns
            
        except Exception as e:
            logger.error(f"시간 패턴 분석 실패: {e}")
            return []
    
    def _analyze_device_patterns(self, df: pd.DataFrame) -> List[AnomalyPattern]:
        """디바이스별 패턴 분석"""
        try:
            patterns = []
            
            # 디바이스별 이상 발생 빈도
            device_counts = df.groupby('device_id').size()
            problematic_devices = device_counts[device_counts > device_counts.mean() * 2]
            
            for device_id, count in problematic_devices.items():
                # 해당 디바이스의 이상 유형 분석
                device_anomalies = df[df['device_id'] == device_id]
                anomaly_types = device_anomalies['anomaly_type'].value_counts()
                most_common_type = anomaly_types.index[0]
                
                patterns.append(AnomalyPattern(
                    pattern_type="디바이스별 반복",
                    frequency=count,
                    severity="high",
                    affected_devices=[device_id],
                    time_pattern="지속적 발생",
                    description=f"디바이스 {device_id}에서 {count}회 이상 발생 (주요 유형: {most_common_type})",
                    recommendation=f"디바이스 {device_id}의 {most_common_type} 문제를 즉시 점검하세요."
                ))
            
            return patterns
            
        except Exception as e:
            logger.error(f"디바이스 패턴 분석 실패: {e}")
            return []
    
    def _analyze_severity_patterns(self, df: pd.DataFrame) -> List[AnomalyPattern]:
        """심각도별 패턴 분석"""
        try:
            patterns = []
            
            # 심각도별 분포
            severity_counts = df['severity'].value_counts()
            
            if 'critical' in severity_counts and severity_counts['critical'] > 0:
                critical_devices = df[df['severity'] == 'critical']['device_id'].unique()
                
                patterns.append(AnomalyPattern(
                    pattern_type="심각한 이상",
                    frequency=severity_counts['critical'],
                    severity="critical",
                    affected_devices=critical_devices.tolist(),
                    time_pattern="즉시 대응 필요",
                    description=f"심각한 이상이 {severity_counts['critical']}회 발생했습니다.",
                    recommendation="즉시 해당 디바이스들을 점검하고 필요시 서비스를 중단하세요."
                ))
            
            # 이상 유형별 패턴
            anomaly_type_counts = df['anomaly_type'].value_counts()
            for anomaly_type, count in anomaly_type_counts.head(3).items():
                if count > 5:  # 5회 이상 발생
                    affected_devices = df[df['anomaly_type'] == anomaly_type]['device_id'].unique()
                    
                    patterns.append(AnomalyPattern(
                        pattern_type="이상 유형별 집중",
                        frequency=count,
                        severity="medium",
                        affected_devices=affected_devices.tolist(),
                        time_pattern="반복 발생",
                        description=f"{anomaly_type} 유형의 이상이 {count}회 발생했습니다.",
                        recommendation=f"{anomaly_type} 문제의 근본 원인을 파악하고 해결하세요."
                    ))
            
            return patterns
            
        except Exception as e:
            logger.error(f"심각도 패턴 분석 실패: {e}")
            return []
    
    def calculate_performance_metrics(self, store_id: str = None, days: int = 30) -> List[PerformanceMetrics]:
        """성능 메트릭 계산"""
        try:
            # 센서 데이터 조회
            sensor_data = self._get_sensor_data_for_analysis(store_id, days)
            
            if sensor_data.empty:
                return []
            
            metrics = []
            
            # 각 메트릭별 성능 지표 계산
            metric_columns = ['temperature', 'vibration', 'power_consumption', 'audio_level']
            
            for metric in metric_columns:
                if metric in sensor_data.columns:
                    data = sensor_data[metric].dropna()
                    
                    if len(data) > 0:
                        # 기본 통계
                        current_value = data.iloc[-1] if len(data) > 0 else 0
                        average_value = data.mean()
                        min_value = data.min()
                        max_value = data.max()
                        std_value = data.std()
                        percentile_95 = data.quantile(0.95)
                        percentile_99 = data.quantile(0.99)
                        
                        # 트렌드 계산
                        if len(data) >= 10:
                            recent_avg = data.tail(10).mean()
                            older_avg = data.head(10).mean()
                            if recent_avg > older_avg * 1.05:
                                trend = "increasing"
                            elif recent_avg < older_avg * 0.95:
                                trend = "decreasing"
                            else:
                                trend = "stable"
                        else:
                            trend = "insufficient_data"
                        
                        performance_metric = PerformanceMetrics(
                            metric_name=metric,
                            current_value=current_value,
                            average_value=average_value,
                            min_value=min_value,
                            max_value=max_value,
                            standard_deviation=std_value,
                            percentile_95=percentile_95,
                            percentile_99=percentile_99,
                            trend=trend
                        )
                        
                        metrics.append(performance_metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"성능 메트릭 계산 실패: {e}")
            return []
    
    def generate_analytics_report(self, store_id: str = None, days: int = 30) -> Dict:
        """종합 분석 리포트 생성"""
        try:
            # 각종 분석 수행
            trends = self.analyze_trends(store_id, days)
            patterns = self.detect_anomaly_patterns(store_id, days)
            performance = self.calculate_performance_metrics(store_id, days)
            
            # 요약 통계
            total_anomalies = sum(p.frequency for p in patterns)
            critical_patterns = [p for p in patterns if p.severity == 'critical']
            increasing_trends = [t for t in trends if t.trend_direction == 'increasing']
            
            # 위험도 점수 계산
            risk_score = self._calculate_risk_score(trends, patterns, performance)
            
            # 권장사항 생성
            recommendations = self._generate_recommendations(trends, patterns, performance)
            
            return {
                'summary': {
                    'analysis_period_days': days,
                    'total_anomalies': total_anomalies,
                    'critical_patterns': len(critical_patterns),
                    'increasing_trends': len(increasing_trends),
                    'risk_score': risk_score,
                    'overall_health': 'good' if risk_score < 30 else 'warning' if risk_score < 60 else 'critical'
                },
                'trends': [asdict(t) for t in trends],
                'patterns': [asdict(p) for p in patterns],
                'performance': [asdict(p) for p in performance],
                'recommendations': recommendations,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"분석 리포트 생성 실패: {e}")
            return {}
    
    def _calculate_risk_score(self, trends: List[TrendAnalysis], patterns: List[AnomalyPattern], performance: List[PerformanceMetrics]) -> float:
        """위험도 점수 계산 (0-100)"""
        try:
            score = 0
            
            # 트렌드 기반 점수
            for trend in trends:
                if trend.trend_direction == 'increasing' and trend.trend_strength > 0.5:
                    score += 20
                elif trend.trend_direction == 'increasing':
                    score += 10
            
            # 패턴 기반 점수
            for pattern in patterns:
                if pattern.severity == 'critical':
                    score += 30
                elif pattern.severity == 'high':
                    score += 20
                elif pattern.severity == 'medium':
                    score += 10
            
            # 성능 기반 점수
            for perf in performance:
                if perf.trend == 'increasing' and perf.current_value > perf.percentile_95:
                    score += 15
                elif perf.trend == 'increasing':
                    score += 5
            
            return min(100, score)
            
        except Exception as e:
            logger.error(f"위험도 점수 계산 실패: {e}")
            return 50.0
    
    def _generate_recommendations(self, trends: List[TrendAnalysis], patterns: List[AnomalyPattern], performance: List[PerformanceMetrics]) -> List[str]:
        """종합 권장사항 생성"""
        try:
            recommendations = []
            
            # 트렌드 기반 권장사항
            for trend in trends:
                if trend.trend_direction == 'increasing' and trend.trend_strength > 0.7:
                    recommendations.append(f"{trend.metric_name}이 급격히 증가하고 있습니다. {trend.recommendation}")
            
            # 패턴 기반 권장사항
            critical_patterns = [p for p in patterns if p.severity == 'critical']
            if critical_patterns:
                recommendations.append("심각한 이상 패턴이 감지되었습니다. 즉시 점검이 필요합니다.")
            
            # 성능 기반 권장사항
            high_performance_issues = [p for p in performance if p.trend == 'increasing' and p.current_value > p.percentile_95]
            if high_performance_issues:
                recommendations.append("일부 성능 지표가 위험 수준에 도달했습니다. 예방 조치가 필요합니다.")
            
            # 일반 권장사항
            if not recommendations:
                recommendations.append("시스템이 안정적으로 작동하고 있습니다. 정기 점검을 계속하세요.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"권장사항 생성 실패: {e}")
            return ["시스템을 점검해주세요."]

# 전역 서비스 인스턴스
analytics_service = AnalyticsService()
