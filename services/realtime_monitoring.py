#!/usr/bin/env python3
"""
24시간 무인 냉동고 모니터링 서비스
실시간 소음 센서 데이터 처리 및 이상 감지
"""

import os
import time
import threading
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 수정된 임포트: services/ai_service.py 파일에서 앙상블 AI 서비스를 가져옵니다.
from services.ai_service import ensemble_ai_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeMonitoringService:
    """실시간 모니터링 서비스"""

    def __init__(self, db_path='monitoring.db', check_interval=60):
        # 데이터베이스 파일 경로를 안전하게 설정
        self.db_path = os.path.join(os.getcwd(), 'data', db_path)
        
        self.check_interval = check_interval  # 초 단위
        self.is_running = False
        self.monitoring_thread = None
        self.alert_threshold = 0.7  # 이상 감지 임계값
        self.warning_threshold = 0.5  # 주의 감지 임계값

        # 데이터베이스 초기화
        self._init_database()

    def _init_database(self):
        """모니터링 데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 모니터링 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    audio_file_path TEXT,
                    prediction INTEGER,
                    probability REAL,
                    confidence TEXT,
                    is_anomaly BOOLEAN,
                    models_used TEXT,
                    features_used INTEGER,
                    status TEXT
                )
            ''')

            # 알림 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT,
                    message TEXT,
                    severity TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("모니터링 데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")

    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_running:
            logger.warning("모니터링이 이미 실행 중입니다.")
            return

        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        logger.info("24시간 모니터링 서비스 시작")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

        logger.info("24시간 모니터링 서비스 중지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_running:
            try:
                # 실제 환경에서는 소음 센서에서 데이터를 받아옴
                # 여기서는 시뮬레이션용으로 랜덤 데이터 생성
                self._process_sensor_data()

                # 다음 체크까지 대기
                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(10)  # 오류 시 10초 대기

    def _process_sensor_data(self):
        """센서 데이터 처리"""
        try:
            # 시뮬레이션용 랜덤 데이터 생성
            import numpy as np
            import librosa
            import soundfile as sf
            
            # 랜덤 오디오 데이터 생성 (실제로는 센서에서 받아옴)
            duration = 5  # 5초
            sr = 16000 # AI 모델의 샘플링 레이트와 동일하게 설정
            t = np.linspace(0, duration, int(sr * duration))

            # 정상 소음 (60Hz 기본 주파수 + 노이즈)
            normal_freq = 60
            normal_audio = np.sin(2 * np.pi * normal_freq * t) * 0.5

            # 이상 소음 (고주파 + 불규칙한 패턴)
            if np.random.random() < 0.1:  # 10% 확률로 이상 소음
                anomaly_freq = 120 + np.random.random() * 100
                anomaly_audio = np.sin(2 * np.pi * anomaly_freq * t) * 0.8
                audio_data = normal_audio + anomaly_audio
            else:
                audio_data = normal_audio

            # 노이즈 추가
            noise = np.random.normal(0, 0.1, len(audio_data))
            audio_data = audio_data + noise

            # AI 분석 (파일을 디스크에 저장하지 않고 직접 전달)
            # ensemble_ai_service의 predict_ensemble 함수가 numpy array를 받을 수 있도록 수정해야 합니다.
            # 현재는 파일 경로를 받으므로, 임시 파일 생성 로직은 유지합니다.
            temp_file = f"temp_sensor_{int(time.time())}.wav"
            sf.write(temp_file, audio_data, sr)
            
            result = ensemble_ai_service.predict_ensemble(temp_file)

            if result:
                # 결과를 데이터베이스에 저장
                self._save_monitoring_result(temp_file, result)

                # 이상 감지 시 알림 처리
                if result['is_anomaly']:
                    self._handle_anomaly_alert(result)

            # 임시 파일 삭제
            if os.path.exists(temp_file):
                os.remove(temp_file)

        except Exception as e:
            logger.error(f"센서 데이터 처리 오류: {e}")

    def _save_monitoring_result(self, audio_file_path: str, result: Dict):
        """모니터링 결과 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO monitoring_logs
                (audio_file_path, prediction, probability, confidence, is_anomaly,
                 models_used, features_used, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audio_file_path,
                result['prediction'],
                result['probability'],
                result['confidence'],
                result['is_anomaly'],
                ','.join(result['models_used']),
                result['features_used'],
                'completed'
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"모니터링 결과 저장 오류: {e}")

    def _handle_anomaly_alert(self, result: Dict):
        """이상 감지 알림 처리"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 알림 타입 결정
            if result['probability'] > self.alert_threshold:
                alert_type = 'CRITICAL'
                severity = 'high'
                message = f"위험: 냉동고 이상 소음 감지 (확률: {result['probability']:.2%})"
            elif result['probability'] > self.warning_threshold:
                alert_type = 'WARNING'
                severity = 'medium'
                message = f"주의: 냉동고 이상 소음 감지 (확률: {result['probability']:.2%})"
            else:
                alert_type = 'INFO'
                severity = 'low'
                message = f"정보: 냉동고 상태 확인 필요 (확률: {result['probability']:.2%})"

            # 알림 저장
            cursor.execute('''
                INSERT INTO alerts (alert_type, message, severity)
                VALUES (?, ?, ?)
            ''', (alert_type, message, severity))

            conn.commit()
            conn.close()

            # 실제 환경에서는 여기서 알림 전송 (이메일, SMS, 푸시 등)
            logger.warning(f"알림: {message}")

        except Exception as e:
            logger.error(f"알림 처리 오류: {e}")

    def get_monitoring_stats(self, hours: int = 24) -> Dict:
        """모니터링 통계 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 시간 범위 계산
            since_time = datetime.now() - timedelta(hours=hours)

            # 전체 분석 수
            cursor.execute('''
                SELECT COUNT(*) FROM monitoring_logs
                WHERE timestamp >= ?
            ''', (since_time,))
            total_analyses = cursor.fetchone()[0]

            # 이상 감지 수
            cursor.execute('''
                SELECT COUNT(*) FROM monitoring_logs
                WHERE timestamp >= ? AND is_anomaly = 1
            ''', (since_time,))
            anomaly_count = cursor.fetchone()[0]

            # 정상 감지 수
            cursor.execute('''
                SELECT COUNT(*) FROM monitoring_logs
                WHERE timestamp >= ? AND is_anomaly = 0
            ''', (since_time,))
            normal_count = cursor.fetchone()[0]

            # 최근 알림 수
            cursor.execute('''
                SELECT COUNT(*) FROM alerts
                WHERE timestamp >= ? AND resolved = 0
            ''', (since_time,))
            active_alerts = cursor.fetchone()[0]

            conn.close()

            return {
                'total_analyses': total_analyses,
                'anomaly_count': anomaly_count,
                'normal_count': normal_count,
                'active_alerts': active_alerts,
                'anomaly_rate': (anomaly_count / total_analyses * 100) if total_analyses > 0 else 0,
                'time_range_hours': hours
            }

        except Exception as e:
            logger.error(f"통계 조회 오류: {e}")
            return {}

    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """최근 알림 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT alert_type, message, severity, timestamp, resolved
                FROM alerts
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))

            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'type': row[0],
                    'message': row[1],
                    'severity': row[2],
                    'timestamp': row[3],
                    'resolved': bool(row[4])
                })

            conn.close()
            return alerts

        except Exception as e:
            logger.error(f"알림 조회 오류: {e}")
            return []

# 전역 모니터링 서비스 인스턴스
monitoring_service = RealtimeMonitoringService()
