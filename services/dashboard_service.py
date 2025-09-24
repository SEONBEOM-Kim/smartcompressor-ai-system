#!/usr/bin/env python3
"""
대시보드 데이터 서비스
Stripe Dashboard와 AWS CloudWatch 스타일의 실시간 대시보드 데이터 제공
"""

import time
import logging
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict
import pandas as pd
import numpy as np
from sqlite3 import connect
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StoreMetrics:
    """매장 메트릭 데이터 클래스"""
    store_id: str
    store_name: str
    total_compressors: int
    online_compressors: int
    offline_compressors: int
    critical_alerts: int
    warning_alerts: int
    total_energy_consumption: float
    energy_cost: float
    uptime_percentage: float
    last_updated: float

@dataclass
class CompressorStatus:
    """압축기 상태 데이터 클래스"""
    compressor_id: str
    store_id: str
    status: str  # online, offline, warning, critical
    temperature: float
    vibration_level: float
    power_consumption: float
    audio_level: int
    health_score: float
    last_maintenance: str
    next_maintenance: str
    anomaly_count: int
    uptime_hours: float

@dataclass
class EnergyAnalytics:
    """에너지 분석 데이터 클래스"""
    store_id: str
    date: str
    total_consumption: float
    peak_consumption: float
    average_consumption: float
    cost: float
    efficiency_score: float
    comparison_previous_day: float
    comparison_previous_week: float

class DashboardDataService:
    """대시보드 데이터 서비스 (Stripe Dashboard 스타일)"""
    
    def __init__(self, db_path: str = 'data/sensor_data.db'):
        self.db_path = db_path
        self.cache = {}
        self.cache_ttl = 300  # 5분 캐시
        self.last_cache_update = {}
        
        # 실시간 데이터 업데이트 스레드
        self.update_thread = None
        self.is_running = False
        
        logger.info("대시보드 데이터 서비스 초기화 완료")
    
    def start_realtime_updates(self):
        """실시간 데이터 업데이트 시작"""
        if not self.is_running:
            self.is_running = True
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()
            logger.info("실시간 데이터 업데이트 시작")
    
    def stop_realtime_updates(self):
        """실시간 데이터 업데이트 중지"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("실시간 데이터 업데이트 중지")
    
    def _update_loop(self):
        """실시간 데이터 업데이트 루프"""
        while self.is_running:
            try:
                # 캐시된 데이터 업데이트
                self._update_cache()
                time.sleep(30)  # 30초마다 업데이트
            except Exception as e:
                logger.error(f"실시간 데이터 업데이트 오류: {e}")
                time.sleep(60)
    
    def _update_cache(self):
        """캐시 데이터 업데이트"""
        try:
            current_time = time.time()
            
            # 매장 메트릭 업데이트
            self.cache['store_metrics'] = self._get_store_metrics()
            self.last_cache_update['store_metrics'] = current_time
            
            # 압축기 상태 업데이트
            self.cache['compressor_status'] = self._get_compressor_status()
            self.last_cache_update['compressor_status'] = current_time
            
            # 에너지 분석 업데이트
            self.cache['energy_analytics'] = self._get_energy_analytics()
            self.last_cache_update['energy_analytics'] = current_time
            
        except Exception as e:
            logger.error(f"캐시 업데이트 오류: {e}")
    
    def _is_cache_valid(self, key: str) -> bool:
        """캐시 유효성 검사"""
        if key not in self.cache or key not in self.last_cache_update:
            return False
        
        return time.time() - self.last_cache_update[key] < self.cache_ttl
    
    def get_store_metrics(self, store_id: str = None, force_refresh: bool = False) -> List[StoreMetrics]:
        """매장 메트릭 조회"""
        try:
            cache_key = f'store_metrics_{store_id or "all"}'
            
            if not force_refresh and self._is_cache_valid(cache_key):
                return self.cache.get(cache_key, [])
            
            metrics = self._get_store_metrics(store_id)
            
            if not force_refresh:
                self.cache[cache_key] = metrics
                self.last_cache_update[cache_key] = time.time()
            
            return metrics
            
        except Exception as e:
            logger.error(f"매장 메트릭 조회 실패: {e}")
            return []
    
    def _get_store_metrics(self, store_id: str = None) -> List[StoreMetrics]:
        """매장 메트릭 데이터 조회"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 매장별 압축기 수 조회
                if store_id:
                    cursor.execute('''
                        SELECT 
                            d.device_id as store_id,
                            d.device_name as store_name,
                            COUNT(*) as total_compressors,
                            SUM(CASE WHEN d.status = 'online' THEN 1 ELSE 0 END) as online_compressors,
                            SUM(CASE WHEN d.status = 'offline' THEN 1 ELSE 0 END) as offline_compressors
                        FROM devices d
                        WHERE d.device_id = ?
                        GROUP BY d.device_id, d.device_name
                    ''', (store_id,))
                else:
                    cursor.execute('''
                        SELECT 
                            d.device_id as store_id,
                            d.device_name as store_name,
                            COUNT(*) as total_compressors,
                            SUM(CASE WHEN d.status = 'online' THEN 1 ELSE 0 END) as online_compressors,
                            SUM(CASE WHEN d.status = 'offline' THEN 1 ELSE 0 END) as offline_compressors
                        FROM devices d
                        GROUP BY d.device_id, d.device_name
                    ''')
                
                stores = cursor.fetchall()
                metrics_list = []
                
                for store in stores:
                    store_id, store_name, total, online, offline = store
                    
                    # 알림 수 조회
                    cursor.execute('''
                        SELECT 
                            SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical_alerts,
                            SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as warning_alerts
                        FROM anomalies 
                        WHERE device_id = ? AND timestamp > ?
                    ''', (store_id, time.time() - 86400))  # 24시간 내
                    
                    alerts = cursor.fetchone()
                    critical_alerts = alerts[0] or 0
                    warning_alerts = alerts[1] or 0
                    
                    # 에너지 소비량 조회
                    cursor.execute('''
                        SELECT 
                            AVG(power_consumption) as avg_power,
                            MAX(power_consumption) as max_power
                        FROM sensor_readings 
                        WHERE device_id = ? AND timestamp > ?
                    ''', (store_id, time.time() - 3600))  # 1시간 내
                    
                    power_data = cursor.fetchone()
                    avg_power = power_data[0] or 0
                    max_power = power_data[1] or 0
                    
                    # 에너지 비용 계산 (kWh당 150원 가정)
                    energy_cost = (avg_power * 24 * 30) / 100 * 150  # 월간 비용
                    
                    # 가동률 계산
                    uptime_percentage = (online / total * 100) if total > 0 else 0
                    
                    metrics = StoreMetrics(
                        store_id=store_id,
                        store_name=store_name,
                        total_compressors=total,
                        online_compressors=online,
                        offline_compressors=offline,
                        critical_alerts=critical_alerts,
                        warning_alerts=warning_alerts,
                        total_energy_consumption=avg_power,
                        energy_cost=energy_cost,
                        uptime_percentage=uptime_percentage,
                        last_updated=time.time()
                    )
                    
                    metrics_list.append(metrics)
                
                return metrics_list
                
        except Exception as e:
            logger.error(f"매장 메트릭 데이터 조회 실패: {e}")
            return []
    
    def get_compressor_status(self, store_id: str = None, force_refresh: bool = False) -> List[CompressorStatus]:
        """압축기 상태 조회"""
        try:
            cache_key = f'compressor_status_{store_id or "all"}'
            
            if not force_refresh and self._is_cache_valid(cache_key):
                return self.cache.get(cache_key, [])
            
            status_list = self._get_compressor_status(store_id)
            
            if not force_refresh:
                self.cache[cache_key] = status_list
                self.last_cache_update[cache_key] = time.time()
            
            return status_list
            
        except Exception as e:
            logger.error(f"압축기 상태 조회 실패: {e}")
            return []
    
    def _get_compressor_status(self, store_id: str = None) -> List[CompressorStatus]:
        """압축기 상태 데이터 조회"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 압축기별 최신 상태 조회
                if store_id:
                    cursor.execute('''
                        SELECT 
                            s.device_id as compressor_id,
                            s.device_id as store_id,
                            d.status,
                            s.temperature,
                            s.vibration_x,
                            s.vibration_y,
                            s.vibration_z,
                            s.power_consumption,
                            s.audio_level,
                            s.sensor_quality,
                            s.timestamp
                        FROM sensor_readings s
                        JOIN devices d ON s.device_id = d.device_id
                        WHERE s.device_id = ?
                        ORDER BY s.timestamp DESC
                        LIMIT 1
                    ''', (store_id,))
                else:
                    cursor.execute('''
                        SELECT 
                            s.device_id as compressor_id,
                            s.device_id as store_id,
                            d.status,
                            s.temperature,
                            s.vibration_x,
                            s.vibration_y,
                            s.vibration_z,
                            s.power_consumption,
                            s.audio_level,
                            s.sensor_quality,
                            s.timestamp
                        FROM sensor_readings s
                        JOIN devices d ON s.device_id = d.device_id
                        WHERE s.timestamp > ?
                        GROUP BY s.device_id
                        HAVING s.timestamp = MAX(s.timestamp)
                        ORDER BY s.timestamp DESC
                    ''', (time.time() - 3600,))  # 1시간 내
                
                compressors = cursor.fetchall()
                status_list = []
                
                for comp in compressors:
                    compressor_id, store_id, status, temp, vib_x, vib_y, vib_z, power, audio, quality, timestamp = comp
                    
                    # 진동 레벨 계산
                    vibration_level = np.sqrt(vib_x**2 + vib_y**2 + vib_z**2)
                    
                    # 건강도 점수 계산 (0-100)
                    health_score = self._calculate_health_score(temp, vibration_level, power, audio, quality)
                    
                    # 이상 감지 수 조회
                    cursor.execute('''
                        SELECT COUNT(*) 
                        FROM anomalies 
                        WHERE device_id = ? AND timestamp > ?
                    ''', (compressor_id, time.time() - 86400))  # 24시간 내
                    
                    anomaly_count = cursor.fetchone()[0] or 0
                    
                    # 가동 시간 계산
                    uptime_hours = self._calculate_uptime_hours(compressor_id)
                    
                    compressor_status = CompressorStatus(
                        compressor_id=compressor_id,
                        store_id=store_id,
                        status=status,
                        temperature=temp,
                        vibration_level=vibration_level,
                        power_consumption=power,
                        audio_level=audio,
                        health_score=health_score,
                        last_maintenance="2024-01-15",  # 실제로는 DB에서 조회
                        next_maintenance="2024-04-15",   # 실제로는 DB에서 조회
                        anomaly_count=anomaly_count,
                        uptime_hours=uptime_hours
                    )
                    
                    status_list.append(compressor_status)
                
                return status_list
                
        except Exception as e:
            logger.error(f"압축기 상태 데이터 조회 실패: {e}")
            return []
    
    def _calculate_health_score(self, temperature: float, vibration: float, power: float, audio: int, quality: float) -> float:
        """건강도 점수 계산 (0-100)"""
        try:
            # 온도 점수 (0-25점)
            temp_score = max(0, 25 - abs(temperature + 20) * 2)  # -20도가 최적
            
            # 진동 점수 (0-25점)
            vib_score = max(0, 25 - vibration * 10)
            
            # 전력 점수 (0-25점)
            power_score = max(0, 25 - (power - 50) * 0.5)  # 50%가 최적
            
            # 오디오 점수 (0-25점)
            audio_score = max(0, 25 - audio * 0.025)
            
            # 품질 가중치 적용
            total_score = (temp_score + vib_score + power_score + audio_score) * quality
            
            return min(100, max(0, total_score))
            
        except Exception as e:
            logger.error(f"건강도 점수 계산 실패: {e}")
            return 50.0
    
    def _calculate_uptime_hours(self, compressor_id: str) -> float:
        """가동 시간 계산 (시간)"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 24시간 내 온라인 상태 시간 계산
                cursor.execute('''
                    SELECT COUNT(*) * 0.1 as uptime_hours
                    FROM sensor_readings 
                    WHERE device_id = ? AND timestamp > ? AND sensor_quality > 0.8
                ''', (compressor_id, time.time() - 86400))
                
                result = cursor.fetchone()
                return result[0] if result else 0.0
                
        except Exception as e:
            logger.error(f"가동 시간 계산 실패: {e}")
            return 0.0
    
    def get_energy_analytics(self, store_id: str = None, days: int = 30, force_refresh: bool = False) -> List[EnergyAnalytics]:
        """에너지 분석 조회"""
        try:
            cache_key = f'energy_analytics_{store_id or "all"}_{days}'
            
            if not force_refresh and self._is_cache_valid(cache_key):
                return self.cache.get(cache_key, [])
            
            analytics = self._get_energy_analytics(store_id, days)
            
            if not force_refresh:
                self.cache[cache_key] = analytics
                self.last_cache_update[cache_key] = time.time()
            
            return analytics
            
        except Exception as e:
            logger.error(f"에너지 분석 조회 실패: {e}")
            return []
    
    def _get_energy_analytics(self, store_id: str = None, days: int = 30) -> List[EnergyAnalytics]:
        """에너지 분석 데이터 조회"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 일별 에너지 소비량 조회
                start_date = datetime.now() - timedelta(days=days)
                start_timestamp = start_date.timestamp()
                
                if store_id:
                    cursor.execute('''
                        SELECT 
                            DATE(datetime(timestamp, 'unixepoch')) as date,
                            AVG(power_consumption) as avg_consumption,
                            MAX(power_consumption) as peak_consumption,
                            SUM(power_consumption) as total_consumption
                        FROM sensor_readings 
                        WHERE device_id = ? AND timestamp > ?
                        GROUP BY DATE(datetime(timestamp, 'unixepoch'))
                        ORDER BY date DESC
                    ''', (store_id, start_timestamp))
                else:
                    cursor.execute('''
                        SELECT 
                            DATE(datetime(timestamp, 'unixepoch')) as date,
                            AVG(power_consumption) as avg_consumption,
                            MAX(power_consumption) as peak_consumption,
                            SUM(power_consumption) as total_consumption
                        FROM sensor_readings 
                        WHERE timestamp > ?
                        GROUP BY DATE(datetime(timestamp, 'unixepoch'))
                        ORDER BY date DESC
                    ''', (start_timestamp,))
                
                energy_data = cursor.fetchall()
                analytics_list = []
                
                for data in energy_data:
                    date, avg_consumption, peak_consumption, total_consumption = data
                    
                    # 비용 계산 (kWh당 150원)
                    cost = total_consumption * 0.15  # 0.15원 per unit
                    
                    # 효율성 점수 계산
                    efficiency_score = min(100, max(0, 100 - (avg_consumption - 50) * 2))
                    
                    # 전일 대비 비교
                    prev_day_consumption = self._get_previous_day_consumption(store_id, date)
                    comparison_previous_day = ((avg_consumption - prev_day_consumption) / prev_day_consumption * 100) if prev_day_consumption > 0 else 0
                    
                    # 전주 대비 비교
                    prev_week_consumption = self._get_previous_week_consumption(store_id, date)
                    comparison_previous_week = ((avg_consumption - prev_week_consumption) / prev_week_consumption * 100) if prev_week_consumption > 0 else 0
                    
                    analytics = EnergyAnalytics(
                        store_id=store_id or "all",
                        date=date,
                        total_consumption=total_consumption,
                        peak_consumption=peak_consumption,
                        average_consumption=avg_consumption,
                        cost=cost,
                        efficiency_score=efficiency_score,
                        comparison_previous_day=comparison_previous_day,
                        comparison_previous_week=comparison_previous_week
                    )
                    
                    analytics_list.append(analytics)
                
                return analytics_list
                
        except Exception as e:
            logger.error(f"에너지 분석 데이터 조회 실패: {e}")
            return []
    
    def _get_previous_day_consumption(self, store_id: str, current_date: str) -> float:
        """전일 소비량 조회"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 전일 날짜 계산
                prev_date = (datetime.strptime(current_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
                
                if store_id:
                    cursor.execute('''
                        SELECT AVG(power_consumption)
                        FROM sensor_readings 
                        WHERE device_id = ? AND DATE(datetime(timestamp, 'unixepoch')) = ?
                    ''', (store_id, prev_date))
                else:
                    cursor.execute('''
                        SELECT AVG(power_consumption)
                        FROM sensor_readings 
                        WHERE DATE(datetime(timestamp, 'unixepoch')) = ?
                    ''', (prev_date,))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0.0
                
        except Exception as e:
            logger.error(f"전일 소비량 조회 실패: {e}")
            return 0.0
    
    def _get_previous_week_consumption(self, store_id: str, current_date: str) -> float:
        """전주 소비량 조회"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 전주 날짜 계산
                prev_week_date = (datetime.strptime(current_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
                
                if store_id:
                    cursor.execute('''
                        SELECT AVG(power_consumption)
                        FROM sensor_readings 
                        WHERE device_id = ? AND DATE(datetime(timestamp, 'unixepoch')) = ?
                    ''', (store_id, prev_week_date))
                else:
                    cursor.execute('''
                        SELECT AVG(power_consumption)
                        FROM sensor_readings 
                        WHERE DATE(datetime(timestamp, 'unixepoch')) = ?
                    ''', (prev_week_date,))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0.0
                
        except Exception as e:
            logger.error(f"전주 소비량 조회 실패: {e}")
            return 0.0
    
    def get_dashboard_summary(self, store_id: str = None) -> Dict:
        """대시보드 요약 정보 조회"""
        try:
            # 매장 메트릭 조회
            store_metrics = self.get_store_metrics(store_id)
            
            # 압축기 상태 조회
            compressor_status = self.get_compressor_status(store_id)
            
            # 에너지 분석 조회
            energy_analytics = self.get_energy_analytics(store_id, days=7)
            
            # 요약 통계 계산
            total_stores = len(store_metrics)
            total_compressors = sum(m.total_compressors for m in store_metrics)
            online_compressors = sum(m.online_compressors for m in store_metrics)
            critical_alerts = sum(m.critical_alerts for m in store_metrics)
            warning_alerts = sum(m.warning_alerts for m in store_metrics)
            total_energy_cost = sum(m.energy_cost for m in store_metrics)
            avg_uptime = np.mean([m.uptime_percentage for m in store_metrics]) if store_metrics else 0
            
            # 건강도 분포
            health_scores = [c.health_score for c in compressor_status]
            healthy_compressors = len([h for h in health_scores if h >= 80])
            warning_compressors = len([h for h in health_scores if 60 <= h < 80])
            critical_compressors = len([h for h in health_scores if h < 60])
            
            return {
                'overview': {
                    'total_stores': total_stores,
                    'total_compressors': total_compressors,
                    'online_compressors': online_compressors,
                    'offline_compressors': total_compressors - online_compressors,
                    'critical_alerts': critical_alerts,
                    'warning_alerts': warning_alerts,
                    'total_energy_cost': total_energy_cost,
                    'avg_uptime_percentage': avg_uptime
                },
                'health_distribution': {
                    'healthy': healthy_compressors,
                    'warning': warning_compressors,
                    'critical': critical_compressors
                },
                'recent_trends': {
                    'energy_cost_trend': self._calculate_energy_trend(energy_analytics),
                    'uptime_trend': self._calculate_uptime_trend(store_metrics),
                    'alert_trend': self._calculate_alert_trend(store_metrics)
                },
                'last_updated': time.time()
            }
            
        except Exception as e:
            logger.error(f"대시보드 요약 조회 실패: {e}")
            return {}
    
    def _calculate_energy_trend(self, energy_analytics: List[EnergyAnalytics]) -> float:
        """에너지 비용 트렌드 계산"""
        if len(energy_analytics) < 2:
            return 0.0
        
        recent_costs = [e.cost for e in energy_analytics[:3]]
        older_costs = [e.cost for e in energy_analytics[3:6]]
        
        if not older_costs:
            return 0.0
        
        recent_avg = np.mean(recent_costs)
        older_avg = np.mean(older_costs)
        
        return ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0.0
    
    def _calculate_uptime_trend(self, store_metrics: List[StoreMetrics]) -> float:
        """가동률 트렌드 계산"""
        if len(store_metrics) < 2:
            return 0.0
        
        uptimes = [m.uptime_percentage for m in store_metrics]
        return np.mean(uptimes)
    
    def _calculate_alert_trend(self, store_metrics: List[StoreMetrics]) -> float:
        """알림 트렌드 계산"""
        if len(store_metrics) < 2:
            return 0.0
        
        total_alerts = sum(m.critical_alerts + m.warning_alerts for m in store_metrics)
        return total_alerts

# 전역 서비스 인스턴스
dashboard_data_service = DashboardDataService()
