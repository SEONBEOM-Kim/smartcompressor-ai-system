#!/usr/bin/env python3
"""
알림 관리 및 설정 서비스
Stripe Dashboard 스타일의 알림 관리 시스템
"""

import time
import logging
import json
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from sqlite3 import connect
import threading
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """알림 채널 열거형"""
    EMAIL = "email"
    SMS = "sms"
    KAKAO = "kakao"
    WEBSOCKET = "websocket"
    PUSH = "push"

class NotificationPriority(Enum):
    """알림 우선순위 열거형"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationStatus(Enum):
    """알림 상태 열거형"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

@dataclass
class NotificationRule:
    """알림 규칙"""
    rule_id: str
    name: str
    description: str
    event_type: str  # temperature_high, vibration_critical, power_high, etc.
    conditions: Dict  # 조건 설정
    channels: List[NotificationChannel]
    priority: NotificationPriority
    enabled: bool
    created_at: str
    updated_at: str

@dataclass
class NotificationTemplate:
    """알림 템플릿"""
    template_id: str
    name: str
    event_type: str
    channel: NotificationChannel
    subject: str
    content: str
    variables: List[str]  # 사용 가능한 변수들
    enabled: bool

@dataclass
class NotificationHistory:
    """알림 이력"""
    notification_id: str
    user_id: str
    store_id: str
    event_type: str
    channel: NotificationChannel
    priority: NotificationPriority
    status: NotificationStatus
    subject: str
    content: str
    sent_at: str
    delivered_at: str
    read_at: str
    error_message: str

@dataclass
class UserNotificationSettings:
    """사용자 알림 설정"""
    user_id: str
    email_enabled: bool
    sms_enabled: bool
    kakao_enabled: bool
    websocket_enabled: bool
    push_enabled: bool
    quiet_hours_start: str  # "22:00"
    quiet_hours_end: str    # "08:00"
    max_notifications_per_hour: int
    priority_filter: List[NotificationPriority]
    store_filters: List[str]  # 특정 매장만 알림 받기

class NotificationManagementService:
    """알림 관리 및 설정 서비스 (Stripe Dashboard 스타일)"""
    
    def __init__(self, db_path: str = 'data/notification_management.db'):
        self.db_path = db_path
        self.rules = {}
        self.templates = {}
        self.user_settings = {}
        self.notification_queue = []
        self.is_processing = False
        
        # 알림 처리 스레드
        self.processing_thread = None
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 기본 규칙 및 템플릿 로드
        self._load_default_rules()
        self._load_default_templates()
        
        logger.info("알림 관리 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 알림 규칙 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notification_rules (
                        rule_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT,
                        event_type TEXT NOT NULL,
                        conditions TEXT NOT NULL,
                        channels TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT 1,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # 알림 템플릿 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notification_templates (
                        template_id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        channel TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        content TEXT NOT NULL,
                        variables TEXT NOT NULL,
                        enabled BOOLEAN DEFAULT 1
                    )
                ''')
                
                # 사용자 알림 설정 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_notification_settings (
                        user_id TEXT PRIMARY KEY,
                        email_enabled BOOLEAN DEFAULT 1,
                        sms_enabled BOOLEAN DEFAULT 1,
                        kakao_enabled BOOLEAN DEFAULT 1,
                        websocket_enabled BOOLEAN DEFAULT 1,
                        push_enabled BOOLEAN DEFAULT 1,
                        quiet_hours_start TEXT DEFAULT "22:00",
                        quiet_hours_end TEXT DEFAULT "08:00",
                        max_notifications_per_hour INTEGER DEFAULT 10,
                        priority_filter TEXT DEFAULT "[]",
                        store_filters TEXT DEFAULT "[]"
                    )
                ''')
                
                # 알림 이력 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS notification_history (
                        notification_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        store_id TEXT,
                        event_type TEXT NOT NULL,
                        channel TEXT NOT NULL,
                        priority TEXT NOT NULL,
                        status TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        content TEXT NOT NULL,
                        sent_at TEXT,
                        delivered_at TEXT,
                        read_at TEXT,
                        error_message TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_user ON notification_history(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_store ON notification_history(store_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_status ON notification_history(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_created ON notification_history(created_at)')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _load_default_rules(self):
        """기본 알림 규칙 로드"""
        try:
            default_rules = [
                {
                    'rule_id': 'temp_high_critical',
                    'name': '온도 높음 (위험)',
                    'description': '냉동고 온도가 위험 수준에 도달했을 때',
                    'event_type': 'temperature_critical',
                    'conditions': {'threshold': 5, 'duration': 300},  # 5도 이상 5분간
                    'channels': [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.KAKAO],
                    'priority': NotificationPriority.CRITICAL
                },
                {
                    'rule_id': 'vibration_high',
                    'name': '진동 높음',
                    'description': '압축기 진동이 높은 수준에 도달했을 때',
                    'event_type': 'vibration_high',
                    'conditions': {'threshold': 2.0, 'duration': 60},  # 2.0g 이상 1분간
                    'channels': [NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET],
                    'priority': NotificationPriority.HIGH
                },
                {
                    'rule_id': 'power_high',
                    'name': '전력 소비 높음',
                    'description': '전력 소비가 높은 수준에 도달했을 때',
                    'event_type': 'power_high',
                    'conditions': {'threshold': 90, 'duration': 180},  # 90% 이상 3분간
                    'channels': [NotificationChannel.EMAIL, NotificationChannel.WEBSOCKET],
                    'priority': NotificationPriority.MEDIUM
                },
                {
                    'rule_id': 'device_offline',
                    'name': '디바이스 오프라인',
                    'description': '디바이스가 오프라인 상태가 되었을 때',
                    'event_type': 'device_offline',
                    'conditions': {'duration': 300},  # 5분간
                    'channels': [NotificationChannel.EMAIL, NotificationChannel.SMS],
                    'priority': NotificationPriority.HIGH
                }
            ]
            
            for rule_data in default_rules:
                rule = NotificationRule(
                    rule_id=rule_data['rule_id'],
                    name=rule_data['name'],
                    description=rule_data['description'],
                    event_type=rule_data['event_type'],
                    conditions=rule_data['conditions'],
                    channels=rule_data['channels'],
                    priority=rule_data['priority'],
                    enabled=True,
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                
                self.rules[rule.rule_id] = rule
                self._save_rule(rule)
                
        except Exception as e:
            logger.error(f"기본 규칙 로드 실패: {e}")
    
    def _load_default_templates(self):
        """기본 알림 템플릿 로드"""
        try:
            default_templates = [
                {
                    'template_id': 'temp_critical_email',
                    'name': '온도 위험 이메일',
                    'event_type': 'temperature_critical',
                    'channel': NotificationChannel.EMAIL,
                    'subject': '[긴급] 냉동고 온도 위험 - {store_name}',
                    'content': '''
                    <h2>🚨 냉동고 온도 위험 알림</h2>
                    <p><strong>매장:</strong> {store_name}</p>
                    <p><strong>디바이스:</strong> {device_id}</p>
                    <p><strong>현재 온도:</strong> {temperature}°C</p>
                    <p><strong>발생 시간:</strong> {timestamp}</p>
                    <p><strong>권장 조치:</strong> 즉시 냉각 시스템을 점검하고 필요시 서비스를 중단하세요.</p>
                    ''',
                    'variables': ['store_name', 'device_id', 'temperature', 'timestamp']
                },
                {
                    'template_id': 'vibration_high_websocket',
                    'name': '진동 높음 웹소켓',
                    'event_type': 'vibration_high',
                    'channel': NotificationChannel.WEBSOCKET,
                    'subject': '압축기 진동 높음',
                    'content': '압축기 진동이 높은 수준입니다. 점검이 필요합니다.',
                    'variables': ['device_id', 'vibration_level', 'timestamp']
                },
                {
                    'template_id': 'device_offline_sms',
                    'name': '디바이스 오프라인 SMS',
                    'event_type': 'device_offline',
                    'channel': NotificationChannel.SMS,
                    'subject': '디바이스 오프라인',
                    'content': '[Signalcraft] 디바이스 {device_id}가 오프라인 상태입니다. 확인이 필요합니다.',
                    'variables': ['device_id', 'timestamp']
                }
            ]
            
            for template_data in default_templates:
                template = NotificationTemplate(
                    template_id=template_data['template_id'],
                    name=template_data['name'],
                    event_type=template_data['event_type'],
                    channel=template_data['channel'],
                    subject=template_data['subject'],
                    content=template_data['content'],
                    variables=template_data['variables'],
                    enabled=True
                )
                
                self.templates[template.template_id] = template
                self._save_template(template)
                
        except Exception as e:
            logger.error(f"기본 템플릿 로드 실패: {e}")
    
    def create_notification_rule(self, rule_data: Dict) -> bool:
        """알림 규칙 생성"""
        try:
            rule = NotificationRule(
                rule_id=rule_data['rule_id'],
                name=rule_data['name'],
                description=rule_data.get('description', ''),
                event_type=rule_data['event_type'],
                conditions=rule_data['conditions'],
                channels=[NotificationChannel(ch) for ch in rule_data['channels']],
                priority=NotificationPriority(rule_data['priority']),
                enabled=rule_data.get('enabled', True),
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.rules[rule.rule_id] = rule
            self._save_rule(rule)
            
            logger.info(f"알림 규칙 생성 완료: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"알림 규칙 생성 실패: {e}")
            return False
    
    def update_notification_rule(self, rule_id: str, updates: Dict) -> bool:
        """알림 규칙 업데이트"""
        try:
            if rule_id not in self.rules:
                return False
            
            rule = self.rules[rule_id]
            
            # 업데이트할 필드들
            for field, value in updates.items():
                if hasattr(rule, field):
                    if field == 'channels':
                        setattr(rule, field, [NotificationChannel(ch) for ch in value])
                    elif field == 'priority':
                        setattr(rule, field, NotificationPriority(value))
                    else:
                        setattr(rule, field, value)
            
            rule.updated_at = datetime.now().isoformat()
            self._save_rule(rule)
            
            logger.info(f"알림 규칙 업데이트 완료: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"알림 규칙 업데이트 실패: {e}")
            return False
    
    def delete_notification_rule(self, rule_id: str) -> bool:
        """알림 규칙 삭제"""
        try:
            if rule_id not in self.rules:
                return False
            
            # 데이터베이스에서 삭제
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM notification_rules WHERE rule_id = ?', (rule_id,))
                conn.commit()
            
            # 메모리에서 삭제
            del self.rules[rule_id]
            
            logger.info(f"알림 규칙 삭제 완료: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"알림 규칙 삭제 실패: {e}")
            return False
    
    def get_notification_rules(self, event_type: str = None) -> List[Dict]:
        """알림 규칙 조회"""
        try:
            rules = []
            
            for rule in self.rules.values():
                if event_type is None or rule.event_type == event_type:
                    rule_dict = asdict(rule)
                    # Enum을 문자열로 변환
                    rule_dict['channels'] = [ch.value for ch in rule.channels]
                    rule_dict['priority'] = rule.priority.value
                    rules.append(rule_dict)
            
            return rules
            
        except Exception as e:
            logger.error(f"알림 규칙 조회 실패: {e}")
            return []
    
    def create_notification_template(self, template_data: Dict) -> bool:
        """알림 템플릿 생성"""
        try:
            template = NotificationTemplate(
                template_id=template_data['template_id'],
                name=template_data['name'],
                event_type=template_data['event_type'],
                channel=NotificationChannel(template_data['channel']),
                subject=template_data['subject'],
                content=template_data['content'],
                variables=template_data['variables'],
                enabled=template_data.get('enabled', True)
            )
            
            self.templates[template.template_id] = template
            self._save_template(template)
            
            logger.info(f"알림 템플릿 생성 완료: {template.template_id}")
            return True
            
        except Exception as e:
            logger.error(f"알림 템플릿 생성 실패: {e}")
            return False
    
    def get_notification_templates(self, event_type: str = None, channel: str = None) -> List[Dict]:
        """알림 템플릿 조회"""
        try:
            templates = []
            
            for template in self.templates.values():
                if (event_type is None or template.event_type == event_type) and \
                   (channel is None or template.channel.value == channel):
                    template_dict = asdict(template)
                    template_dict['channel'] = template.channel.value
                    templates.append(template_dict)
            
            return templates
            
        except Exception as e:
            logger.error(f"알림 템플릿 조회 실패: {e}")
            return []
    
    def update_user_notification_settings(self, user_id: str, settings: Dict) -> bool:
        """사용자 알림 설정 업데이트"""
        try:
            user_settings = UserNotificationSettings(
                user_id=user_id,
                email_enabled=settings.get('email_enabled', True),
                sms_enabled=settings.get('sms_enabled', True),
                kakao_enabled=settings.get('kakao_enabled', True),
                websocket_enabled=settings.get('websocket_enabled', True),
                push_enabled=settings.get('push_enabled', True),
                quiet_hours_start=settings.get('quiet_hours_start', '22:00'),
                quiet_hours_end=settings.get('quiet_hours_end', '08:00'),
                max_notifications_per_hour=settings.get('max_notifications_per_hour', 10),
                priority_filter=[NotificationPriority(p) for p in settings.get('priority_filter', [])],
                store_filters=settings.get('store_filters', [])
            )
            
            self.user_settings[user_id] = user_settings
            self._save_user_settings(user_settings)
            
            logger.info(f"사용자 알림 설정 업데이트 완료: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"사용자 알림 설정 업데이트 실패: {e}")
            return False
    
    def get_user_notification_settings(self, user_id: str) -> Optional[Dict]:
        """사용자 알림 설정 조회"""
        try:
            if user_id in self.user_settings:
                settings = self.user_settings[user_id]
                settings_dict = asdict(settings)
                settings_dict['priority_filter'] = [p.value for p in settings.priority_filter]
                return settings_dict
            
            return None
            
        except Exception as e:
            logger.error(f"사용자 알림 설정 조회 실패: {e}")
            return None
    
    def send_notification(self, event_data: Dict) -> bool:
        """알림 전송"""
        try:
            event_type = event_data.get('event_type')
            store_id = event_data.get('store_id')
            device_id = event_data.get('device_id')
            
            # 해당 이벤트에 대한 규칙들 찾기
            applicable_rules = [rule for rule in self.rules.values() 
                              if rule.event_type == event_type and rule.enabled]
            
            if not applicable_rules:
                logger.warning(f"적용 가능한 알림 규칙이 없습니다: {event_type}")
                return False
            
            # 각 규칙에 대해 알림 전송
            for rule in applicable_rules:
                if self._check_rule_conditions(rule, event_data):
                    self._process_notification(rule, event_data)
            
            return True
            
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
            return False
    
    def _check_rule_conditions(self, rule: NotificationRule, event_data: Dict) -> bool:
        """규칙 조건 확인"""
        try:
            conditions = rule.conditions
            
            # 임계값 확인
            if 'threshold' in conditions:
                metric_value = event_data.get('value', 0)
                if metric_value < conditions['threshold']:
                    return False
            
            # 지속 시간 확인
            if 'duration' in conditions:
                # 실제로는 이벤트가 지속된 시간을 확인해야 함
                # 여기서는 단순화
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"규칙 조건 확인 실패: {e}")
            return False
    
    def _process_notification(self, rule: NotificationRule, event_data: Dict):
        """알림 처리"""
        try:
            # 각 채널에 대해 알림 전송
            for channel in rule.channels:
                # 템플릿 찾기
                template = self._find_template(rule.event_type, channel)
                if not template:
                    continue
                
                # 알림 내용 생성
                notification_content = self._generate_notification_content(template, event_data)
                
                # 알림 큐에 추가
                notification = {
                    'rule_id': rule.rule_id,
                    'event_type': rule.event_type,
                    'channel': channel,
                    'priority': rule.priority,
                    'content': notification_content,
                    'event_data': event_data,
                    'created_at': time.time()
                }
                
                self.notification_queue.append(notification)
            
            # 알림 처리 시작
            if not self.is_processing:
                self._start_notification_processing()
                
        except Exception as e:
            logger.error(f"알림 처리 실패: {e}")
    
    def _find_template(self, event_type: str, channel: NotificationChannel) -> Optional[NotificationTemplate]:
        """템플릿 찾기"""
        for template in self.templates.values():
            if template.event_type == event_type and template.channel == channel and template.enabled:
                return template
        return None
    
    def _generate_notification_content(self, template: NotificationTemplate, event_data: Dict) -> Dict:
        """알림 내용 생성"""
        try:
            # 변수 치환
            subject = template.subject
            content = template.content
            
            for variable in template.variables:
                value = event_data.get(variable, f'{{{variable}}}')
                subject = subject.replace(f'{{{variable}}}', str(value))
                content = content.replace(f'{{{variable}}}', str(value))
            
            return {
                'subject': subject,
                'content': content
            }
            
        except Exception as e:
            logger.error(f"알림 내용 생성 실패: {e}")
            return {'subject': '알림', 'content': '알림이 발생했습니다.'}
    
    def _start_notification_processing(self):
        """알림 처리 시작"""
        if not self.is_processing:
            self.is_processing = True
            self.processing_thread = threading.Thread(target=self._process_notification_queue, daemon=True)
            self.processing_thread.start()
    
    def _process_notification_queue(self):
        """알림 큐 처리"""
        while self.notification_queue or self.is_processing:
            if self.notification_queue:
                notification = self.notification_queue.pop(0)
                self._send_single_notification(notification)
            else:
                time.sleep(1)
        
        self.is_processing = False
    
    def _send_single_notification(self, notification: Dict):
        """단일 알림 전송"""
        try:
            # 실제 알림 전송 로직 (여기서는 시뮬레이션)
            logger.info(f"알림 전송: {notification['event_type']} via {notification['channel'].value}")
            
            # 알림 이력 저장
            self._save_notification_history(notification)
            
        except Exception as e:
            logger.error(f"단일 알림 전송 실패: {e}")
    
    def get_notification_history(self, user_id: str = None, store_id: str = None, 
                               limit: int = 100) -> List[Dict]:
        """알림 이력 조회"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = 'SELECT * FROM notification_history WHERE 1=1'
                params = []
                
                if user_id:
                    query += ' AND user_id = ?'
                    params.append(user_id)
                
                if store_id:
                    query += ' AND store_id = ?'
                    params.append(store_id)
                
                query += ' ORDER BY created_at DESC LIMIT ?'
                params.append(limit)
                
                cursor.execute(query, params)
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'notification_id': row[0],
                        'user_id': row[1],
                        'store_id': row[2],
                        'event_type': row[3],
                        'channel': row[4],
                        'priority': row[5],
                        'status': row[6],
                        'subject': row[7],
                        'content': row[8],
                        'sent_at': row[9],
                        'delivered_at': row[10],
                        'read_at': row[11],
                        'error_message': row[12],
                        'created_at': row[13]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"알림 이력 조회 실패: {e}")
            return []
    
    def _save_rule(self, rule: NotificationRule):
        """규칙 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO notification_rules 
                    (rule_id, name, description, event_type, conditions, channels, priority, enabled, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    rule.rule_id,
                    rule.name,
                    rule.description,
                    rule.event_type,
                    json.dumps(rule.conditions),
                    json.dumps([ch.value for ch in rule.channels]),
                    rule.priority.value,
                    rule.enabled,
                    rule.created_at,
                    rule.updated_at
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"규칙 저장 실패: {e}")
    
    def _save_template(self, template: NotificationTemplate):
        """템플릿 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO notification_templates 
                    (template_id, name, event_type, channel, subject, content, variables, enabled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template.template_id,
                    template.name,
                    template.event_type,
                    template.channel.value,
                    template.subject,
                    template.content,
                    json.dumps(template.variables),
                    template.enabled
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"템플릿 저장 실패: {e}")
    
    def _save_user_settings(self, settings: UserNotificationSettings):
        """사용자 설정 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_notification_settings 
                    (user_id, email_enabled, sms_enabled, kakao_enabled, websocket_enabled, push_enabled,
                     quiet_hours_start, quiet_hours_end, max_notifications_per_hour, priority_filter, store_filters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    settings.user_id,
                    settings.email_enabled,
                    settings.sms_enabled,
                    settings.kakao_enabled,
                    settings.websocket_enabled,
                    settings.push_enabled,
                    settings.quiet_hours_start,
                    settings.quiet_hours_end,
                    settings.max_notifications_per_hour,
                    json.dumps([p.value for p in settings.priority_filter]),
                    json.dumps(settings.store_filters)
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"사용자 설정 저장 실패: {e}")
    
    def _save_notification_history(self, notification: Dict):
        """알림 이력 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                notification_id = f"notif_{int(time.time() * 1000)}"
                
                cursor.execute('''
                    INSERT INTO notification_history 
                    (notification_id, user_id, store_id, event_type, channel, priority, status, subject, content, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    notification_id,
                    notification['event_data'].get('user_id', 'system'),
                    notification['event_data'].get('store_id'),
                    notification['event_type'],
                    notification['channel'].value,
                    notification['priority'].value,
                    NotificationStatus.SENT.value,
                    notification['content']['subject'],
                    notification['content']['content'],
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"알림 이력 저장 실패: {e}")

# 전역 서비스 인스턴스
notification_management_service = NotificationManagementService()
