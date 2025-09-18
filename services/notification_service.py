#!/usr/bin/env python3
"""
실시간 알림 서비스
ESP32에서 감지된 이상 상황을 실시간으로 알림합니다.
"""

import asyncio
import logging
import smtplib
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import sqlite3
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NotificationChannel:
    """알림 채널 정보"""
    channel_type: str  # 'email', 'sms', 'webhook', 'push'
    config: Dict
    enabled: bool = True
    priority: int = 1  # 1: 낮음, 2: 보통, 3: 높음, 4: 긴급

@dataclass
class Alert:
    """알림 정보"""
    alert_id: str
    device_id: str
    alert_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: float
    data: Dict
    resolved: bool = False

class NotificationService:
    """실시간 알림 서비스"""
    
    def __init__(self, db_path: str = 'notifications.db'):
        self.db_path = db_path
        self.channels: List[NotificationChannel] = []
        self.alert_history: List[Alert] = []
        self.subscribers: List[Callable] = []
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 기본 채널 설정
        self._setup_default_channels()
    
    def _init_database(self):
        """알림 데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 알림 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE,
                    device_id TEXT,
                    alert_type TEXT,
                    severity TEXT,
                    message TEXT,
                    timestamp REAL,
                    data TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 알림 채널 테이블 생성
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_type TEXT,
                    config TEXT,
                    enabled BOOLEAN DEFAULT TRUE,
                    priority INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("알림 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _setup_default_channels(self):
        """기본 알림 채널 설정"""
        # 이메일 채널
        email_channel = NotificationChannel(
            channel_type='email',
            config={
                'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'username': os.getenv('EMAIL_USERNAME', ''),
                'password': os.getenv('EMAIL_PASSWORD', ''),
                'from_email': os.getenv('FROM_EMAIL', ''),
                'to_emails': os.getenv('TO_EMAILS', '').split(',')
            },
            enabled=True,
            priority=2
        )
        self.channels.append(email_channel)
        
        # 웹훅 채널 (슬랙, 디스코드 등)
        webhook_channel = NotificationChannel(
            channel_type='webhook',
            config={
                'webhook_url': os.getenv('WEBHOOK_URL', ''),
                'headers': {
                    'Content-Type': 'application/json'
                }
            },
            enabled=True,
            priority=3
        )
        self.channels.append(webhook_channel)
        
        # 푸시 알림 채널
        push_channel = NotificationChannel(
            channel_type='push',
            config={
                'fcm_server_key': os.getenv('FCM_SERVER_KEY', ''),
                'device_tokens': os.getenv('DEVICE_TOKENS', '').split(',')
            },
            enabled=True,
            priority=4
        )
        self.channels.append(push_channel)
        
        # 카카오톡 알림 채널
        kakao_channel = NotificationChannel(
            channel_type='kakao',
            config={
                'access_token': os.getenv('KAKAO_ACCESS_TOKEN', ''),
                'phone_numbers': os.getenv('KAKAO_PHONE_NUMBERS', '').split(',')
            },
            enabled=True,
            priority=5  # 가장 높은 우선순위
        )
        self.channels.append(kakao_channel)
    
    def add_channel(self, channel: NotificationChannel):
        """알림 채널 추가"""
        self.channels.append(channel)
        self._save_channel_to_db(channel)
        logger.info(f"알림 채널 추가: {channel.channel_type}")
    
    def _save_channel_to_db(self, channel: NotificationChannel):
        """채널을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO notification_channels 
                (channel_type, config, enabled, priority)
                VALUES (?, ?, ?, ?)
            ''', (
                channel.channel_type,
                json.dumps(channel.config),
                channel.enabled,
                channel.priority
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"채널 저장 실패: {e}")
    
    def send_alert(self, device_id: str, alert_type: str, severity: str, 
                   message: str, data: Dict = None) -> bool:
        """알림 전송"""
        try:
            # 알림 생성
            alert = Alert(
                alert_id=f"{device_id}_{int(time.time())}",
                device_id=device_id,
                alert_type=alert_type,
                severity=severity,
                message=message,
                timestamp=time.time(),
                data=data or {}
            )
            
            # 알림 저장
            self._save_alert_to_db(alert)
            self.alert_history.append(alert)
            
            # 구독자들에게 알림
            for subscriber in self.subscribers:
                try:
                    subscriber(alert)
                except Exception as e:
                    logger.error(f"구독자 알림 실패: {e}")
            
            # 활성화된 채널로 전송
            success_count = 0
            for channel in self.channels:
                if channel.enabled and self._should_send_to_channel(alert, channel):
                    try:
                        if self._send_to_channel(alert, channel):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"채널 {channel.channel_type} 전송 실패: {e}")
            
            logger.info(f"알림 전송 완료: {alert.alert_id} ({success_count}/{len(self.channels)} 채널)")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
            return False
    
    def _should_send_to_channel(self, alert: Alert, channel: NotificationChannel) -> bool:
        """채널로 전송할지 결정"""
        severity_priority = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        alert_priority = severity_priority.get(alert.severity, 1)
        return alert_priority >= channel.priority
    
    def _send_to_channel(self, alert: Alert, channel: NotificationChannel) -> bool:
        """특정 채널로 알림 전송"""
        if channel.channel_type == 'email':
            return self._send_email(alert, channel)
        elif channel.channel_type == 'webhook':
            return self._send_webhook(alert, channel)
        elif channel.channel_type == 'push':
            return self._send_push(alert, channel)
        elif channel.channel_type == 'kakao':
            return self._send_kakao(alert, channel)
        else:
            logger.warning(f"지원하지 않는 채널 타입: {channel.channel_type}")
            return False
    
    def _send_email(self, alert: Alert, channel: NotificationChannel) -> bool:
        """이메일 알림 전송"""
        try:
            config = channel.config
            
            # 이메일 내용 생성
            subject = f"[Signalcraft] {alert.alert_type} - {alert.device_id}"
            body = f"""
            디바이스: {alert.device_id}
            알림 유형: {alert.alert_type}
            심각도: {alert.severity}
            메시지: {alert.message}
            시간: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}
            
            추가 정보:
            {json.dumps(alert.data, indent=2, ensure_ascii=False)}
            """
            
            # 이메일 생성
            msg = MIMEMultipart()
            msg['From'] = config['from_email']
            msg['To'] = ', '.join(config['to_emails'])
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # SMTP 서버 연결 및 전송
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            
            for to_email in config['to_emails']:
                server.send_message(msg)
            
            server.quit()
            logger.info(f"이메일 알림 전송 완료: {alert.alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 전송 실패: {e}")
            return False
    
    def _send_webhook(self, alert: Alert, channel: NotificationChannel) -> bool:
        """웹훅 알림 전송"""
        try:
            config = channel.config
            
            # 웹훅 페이로드 생성
            payload = {
                'alert_id': alert.alert_id,
                'device_id': alert.device_id,
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'timestamp': alert.timestamp,
                'data': alert.data
            }
            
            # HTTP POST 요청
            response = requests.post(
                config['webhook_url'],
                json=payload,
                headers=config.get('headers', {}),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"웹훅 알림 전송 완료: {alert.alert_id}")
                return True
            else:
                logger.error(f"웹훅 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"웹훅 전송 실패: {e}")
            return False
    
    def _send_push(self, alert: Alert, channel: NotificationChannel) -> bool:
        """푸시 알림 전송 (FCM)"""
        try:
            config = channel.config
            
            # FCM 메시지 생성
            fcm_message = {
                'to': config['device_tokens'][0],  # 첫 번째 토큰 사용
                'notification': {
                    'title': f"Signalcraft 알림 - {alert.alert_type}",
                    'body': alert.message,
                    'icon': 'ic_notification',
                    'sound': 'default'
                },
                'data': {
                    'alert_id': alert.alert_id,
                    'device_id': alert.device_id,
                    'severity': alert.severity
                }
            }
            
            # FCM 서버로 전송
            headers = {
                'Authorization': f'key={config["fcm_server_key"]}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                'https://fcm.googleapis.com/fcm/send',
                json=fcm_message,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"푸시 알림 전송 완료: {alert.alert_id}")
                return True
            else:
                logger.error(f"푸시 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"푸시 전송 실패: {e}")
            return False
    
    def _send_kakao(self, alert: Alert, channel: NotificationChannel) -> bool:
        """카카오톡 알림 전송"""
        try:
            from services.kakao_notification_service import kakao_notification_service
            
            config = channel.config
            phone_numbers = config.get('phone_numbers', [])
            
            if not phone_numbers:
                logger.warning("카카오톡 전화번호가 설정되지 않았습니다.")
                return False
            
            # 카카오톡 알림 전송
            results = kakao_notification_service.send_bulk_notification(
                phone_numbers=phone_numbers,
                alert_type=alert.alert_type,
                device_id=alert.device_id,
                severity=alert.severity,
                message=alert.message,
                data=alert.data
            )
            
            if results['success']:
                logger.info(f"카카오톡 알림 전송 성공: {alert.alert_id}")
                return True
            else:
                logger.error(f"카카오톡 알림 전송 실패: {alert.alert_id}")
                return False
                
        except Exception as e:
            logger.error(f"카카오톡 전송 실패: {e}")
            return False
    
    def _save_alert_to_db(self, alert: Alert):
        """알림을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO notifications 
                (alert_id, device_id, alert_type, severity, message, timestamp, data, resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert.alert_id,
                alert.device_id,
                alert.alert_type,
                alert.severity,
                alert.message,
                alert.timestamp,
                json.dumps(alert.data),
                alert.resolved
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"알림 저장 실패: {e}")
    
    def subscribe(self, callback: Callable):
        """알림 구독자 추가"""
        self.subscribers.append(callback)
        logger.info(f"알림 구독자 추가: {callback.__name__}")
    
    def get_alert_history(self, device_id: str = None, limit: int = 100) -> List[Dict]:
        """알림 이력 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if device_id:
                cursor.execute('''
                    SELECT * FROM notifications 
                    WHERE device_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (device_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM notifications 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alerts.append({
                    'id': row[0],
                    'alert_id': row[1],
                    'device_id': row[2],
                    'alert_type': row[3],
                    'severity': row[4],
                    'message': row[5],
                    'timestamp': row[6],
                    'data': json.loads(row[7]) if row[7] else {},
                    'resolved': bool(row[8]),
                    'created_at': row[9]
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"알림 이력 조회 실패: {e}")
            return []
    
    def resolve_alert(self, alert_id: str) -> bool:
        """알림 해결 처리"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE notifications 
                SET resolved = TRUE 
                WHERE alert_id = ?
            ''', (alert_id,))
            
            conn.commit()
            conn.close()
            
            # 메모리에서도 업데이트
            for alert in self.alert_history:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    break
            
            logger.info(f"알림 해결 처리: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"알림 해결 처리 실패: {e}")
            return False

# 전역 인스턴스
notification_service = NotificationService()
