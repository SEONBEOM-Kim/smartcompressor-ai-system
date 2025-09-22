"""
보안 모니터링 서비스 - Stripe & AWS 보안 시스템 벤치마킹
실시간 보안 이벤트 모니터링, 위협 탐지, 알림 시스템
"""

import logging
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """위협 수준"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EventType(Enum):
    """이벤트 유형"""
    AUTHENTICATION_FAILURE = "auth_failure"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE_DETECTED = "malware_detected"
    DDoS_ATTACK = "ddos_attack"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"

class AlertChannel(Enum):
    """알림 채널"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"

@dataclass
class SecurityEvent:
    """보안 이벤트"""
    event_id: str
    event_type: EventType
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: str
    user_id: Optional[str]
    endpoint: str
    description: str
    details: Dict[str, Any]
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

@dataclass
class SecurityAlert:
    """보안 알림"""
    alert_id: str
    event_id: str
    channels: List[AlertChannel]
    message: str
    created_at: datetime
    sent_at: Optional[datetime] = None
    is_sent: bool = False

@dataclass
class ThreatPattern:
    """위협 패턴"""
    pattern_id: str
    name: str
    pattern_type: str
    pattern: str
    threat_level: ThreatLevel
    is_active: bool = True

class SecurityMonitoringService:
    """
    Stripe & AWS 보안 시스템을 벤치마킹한 보안 모니터링 서비스
    """
    
    def __init__(self):
        # 이벤트 저장소
        self.events: Dict[str, SecurityEvent] = {}
        self.alerts: Dict[str, SecurityAlert] = {}
        
        # 위협 패턴
        self.threat_patterns: List[ThreatPattern] = []
        self._initialize_threat_patterns()
        
        # 통계 데이터
        self.event_stats = defaultdict(int)
        self.threat_stats = defaultdict(int)
        
        # 알림 설정
        self.alert_config = self._initialize_alert_config()
        
        # 모니터링 스레드
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # 이벤트 큐
        self.event_queue = deque()
        self.queue_lock = threading.Lock()
        
        logger.info("SecurityMonitoringService 초기화 완료")

    def _initialize_threat_patterns(self):
        """위협 패턴 초기화"""
        patterns = [
            ThreatPattern(
                pattern_id="sql_injection_1",
                name="SQL Injection - Union Select",
                pattern_type="regex",
                pattern=r"(?i)union\s+select",
                threat_level=ThreatLevel.HIGH
            ),
            ThreatPattern(
                pattern_id="xss_1",
                name="XSS Attack - Script Tag",
                pattern_type="regex",
                pattern=r"<script[^>]*>.*?</script>",
                threat_level=ThreatLevel.MEDIUM
            ),
            ThreatPattern(
                pattern_id="path_traversal_1",
                name="Path Traversal",
                pattern_type="regex",
                pattern=r"\.\./",
                threat_level=ThreatLevel.MEDIUM
            ),
            ThreatPattern(
                pattern_id="command_injection_1",
                name="Command Injection",
                pattern_type="regex",
                pattern=r"[;&|`$]",
                threat_level=ThreatLevel.HIGH
            ),
            ThreatPattern(
                pattern_id="brute_force_1",
                name="Brute Force Attack",
                pattern_type="behavior",
                pattern="multiple_auth_failures",
                threat_level=ThreatLevel.MEDIUM
            ),
            ThreatPattern(
                pattern_id="data_exfiltration_1",
                name="Data Exfiltration",
                pattern_type="behavior",
                pattern="large_data_download",
                threat_level=ThreatLevel.CRITICAL
            )
        ]
        
        self.threat_patterns.extend(patterns)

    def _initialize_alert_config(self) -> Dict:
        """알림 설정 초기화"""
        return {
            "email": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "alerts@smartcompressor-ai.com",
                "password": "your_app_password",
                "recipients": ["security@smartcompressor-ai.com", "admin@smartcompressor-ai.com"]
            },
            "slack": {
                "enabled": True,
                "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                "channel": "#security-alerts"
            },
            "webhook": {
                "enabled": True,
                "url": "https://your-monitoring-system.com/webhook",
                "headers": {"Authorization": "Bearer your-token"}
            },
            "threat_levels": {
                ThreatLevel.LOW: [AlertChannel.DASHBOARD],
                ThreatLevel.MEDIUM: [AlertChannel.DASHBOARD, AlertChannel.EMAIL],
                ThreatLevel.HIGH: [AlertChannel.DASHBOARD, AlertChannel.EMAIL, AlertChannel.SLACK],
                ThreatLevel.CRITICAL: [AlertChannel.DASHBOARD, AlertChannel.EMAIL, AlertChannel.SLACK, AlertChannel.WEBHOOK]
            }
        }

    def start_monitoring(self):
        """보안 모니터링 시작"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("보안 모니터링 시작")

    def stop_monitoring(self):
        """보안 모니터링 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("보안 모니터링 중지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                # 이벤트 큐 처리
                with self.queue_lock:
                    while self.event_queue:
                        event = self.event_queue.popleft()
                        self._process_event(event)
                
                # 통계 업데이트
                self._update_statistics()
                
                # 정리 작업
                self._cleanup_old_events()
                
                time.sleep(1)  # 1초마다 체크
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")

    def log_security_event(self, event_type: EventType, threat_level: ThreatLevel,
                          source_ip: str, user_id: Optional[str], endpoint: str,
                          description: str, details: Dict[str, Any] = None) -> str:
        """보안 이벤트 로깅"""
        event_id = self._generate_event_id()
        
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            threat_level=threat_level,
            timestamp=datetime.now(),
            source_ip=source_ip,
            user_id=user_id,
            endpoint=endpoint,
            description=description,
            details=details or {}
        )
        
        # 이벤트 큐에 추가
        with self.queue_lock:
            self.event_queue.append(event)
        
        logger.warning(f"보안 이벤트 로깅: {event_type.value} - {description} (IP: {source_ip})")
        return event_id

    def _process_event(self, event: SecurityEvent):
        """이벤트 처리"""
        # 이벤트 저장
        self.events[event.event_id] = event
        
        # 통계 업데이트
        self.event_stats[event.event_type.value] += 1
        self.threat_stats[event.threat_level.value] += 1
        
        # 위협 패턴 매칭
        self._check_threat_patterns(event)
        
        # 알림 생성
        if event.threat_level in [ThreatLevel.MEDIUM, ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            self._create_alert(event)

    def _check_threat_patterns(self, event: SecurityEvent):
        """위협 패턴 확인"""
        for pattern in self.threat_patterns:
            if not pattern.is_active:
                continue
            
            if pattern.pattern_type == "regex":
                if self._match_regex_pattern(event, pattern):
                    self._handle_pattern_match(event, pattern)
            elif pattern.pattern_type == "behavior":
                if self._match_behavior_pattern(event, pattern):
                    self._handle_pattern_match(event, pattern)

    def _match_regex_pattern(self, event: SecurityEvent, pattern: ThreatPattern) -> bool:
        """정규식 패턴 매칭"""
        import re
        
        # 이벤트 세부사항에서 패턴 검색
        for key, value in event.details.items():
            if isinstance(value, str) and re.search(pattern.pattern, value):
                return True
        
        # 설명에서 패턴 검색
        if re.search(pattern.pattern, event.description):
            return True
        
        return False

    def _match_behavior_pattern(self, event: SecurityEvent, pattern: ThreatPattern) -> bool:
        """행동 패턴 매칭"""
        if pattern.pattern == "multiple_auth_failures":
            # 최근 5분 내 동일 IP에서 인증 실패 5회 이상
            recent_failures = [
                e for e in self.events.values()
                if (e.event_type == EventType.AUTHENTICATION_FAILURE and
                    e.source_ip == event.source_ip and
                    (event.timestamp - e.timestamp).total_seconds() < 300)
            ]
            return len(recent_failures) >= 5
        
        elif pattern.pattern == "large_data_download":
            # 대용량 데이터 다운로드 (10MB 이상)
            return event.details.get("data_size", 0) > 10 * 1024 * 1024
        
        return False

    def _handle_pattern_match(self, event: SecurityEvent, pattern: ThreatPattern):
        """패턴 매칭 처리"""
        # 위협 수준 업데이트
        if pattern.threat_level.value > event.threat_level.value:
            event.threat_level = pattern.threat_level
        
        # 추가 이벤트 생성
        self.log_security_event(
            EventType.SUSPICIOUS_ACTIVITY,
            pattern.threat_level,
            event.source_ip,
            event.user_id,
            event.endpoint,
            f"위협 패턴 감지: {pattern.name}",
            {"pattern_id": pattern.pattern_id, "original_event": event.event_id}
        )

    def _create_alert(self, event: SecurityEvent):
        """알림 생성"""
        alert_id = self._generate_alert_id()
        channels = self.alert_config["threat_levels"].get(event.threat_level, [])
        
        message = self._format_alert_message(event)
        
        alert = SecurityAlert(
            alert_id=alert_id,
            event_id=event.event_id,
            channels=channels,
            message=message,
            created_at=datetime.now()
        )
        
        self.alerts[alert_id] = alert
        
        # 알림 전송
        self._send_alert(alert)

    def _format_alert_message(self, event: SecurityEvent) -> str:
        """알림 메시지 포맷팅"""
        return f"""
🚨 보안 알림

이벤트 ID: {event.event_id}
유형: {event.event_type.value}
위협 수준: {event.threat_level.value.upper()}
시간: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
소스 IP: {event.source_ip}
사용자: {event.user_id or 'N/A'}
엔드포인트: {event.endpoint}
설명: {event.description}

세부사항:
{json.dumps(event.details, indent=2, ensure_ascii=False)}
        """.strip()

    def _send_alert(self, alert: SecurityAlert):
        """알림 전송"""
        for channel in alert.channels:
            try:
                if channel == AlertChannel.EMAIL:
                    self._send_email_alert(alert)
                elif channel == AlertChannel.SLACK:
                    self._send_slack_alert(alert)
                elif channel == AlertChannel.WEBHOOK:
                    self._send_webhook_alert(alert)
                elif channel == AlertChannel.DASHBOARD:
                    self._send_dashboard_alert(alert)
                
                alert.is_sent = True
                alert.sent_at = datetime.now()
                
            except Exception as e:
                logger.error(f"알림 전송 실패 ({channel.value}): {e}")

    def _send_email_alert(self, alert: SecurityAlert):
        """이메일 알림 전송"""
        config = self.alert_config["email"]
        
        msg = MIMEMultipart()
        msg['From'] = config["username"]
        msg['To'] = ", ".join(config["recipients"])
        msg['Subject'] = f"보안 알림 - {alert.event_id}"
        
        msg.attach(MIMEText(alert.message, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(config["smtp_server"], config["smtp_port"])
        server.starttls()
        server.login(config["username"], config["password"])
        server.send_message(msg)
        server.quit()

    def _send_slack_alert(self, alert: SecurityAlert):
        """Slack 알림 전송"""
        config = self.alert_config["slack"]
        
        payload = {
            "channel": config["channel"],
            "text": alert.message,
            "username": "Security Bot",
            "icon_emoji": ":warning:"
        }
        
        requests.post(config["webhook_url"], json=payload)

    def _send_webhook_alert(self, alert: SecurityAlert):
        """웹훅 알림 전송"""
        config = self.alert_config["webhook"]
        
        payload = {
            "alert_id": alert.alert_id,
            "event_id": alert.event_id,
            "message": alert.message,
            "timestamp": alert.created_at.isoformat()
        }
        
        requests.post(config["url"], json=payload, headers=config["headers"])

    def _send_dashboard_alert(self, alert: SecurityAlert):
        """대시보드 알림 전송"""
        # 실제 환경에서는 WebSocket이나 Server-Sent Events 사용
        logger.info(f"대시보드 알림: {alert.message}")

    def get_security_events(self, limit: int = 100, 
                           threat_level: Optional[ThreatLevel] = None,
                           event_type: Optional[EventType] = None) -> List[Dict]:
        """보안 이벤트 조회"""
        events = list(self.events.values())
        
        # 필터링
        if threat_level:
            events = [e for e in events if e.threat_level == threat_level]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # 시간순 정렬 (최신순)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 제한
        events = events[:limit]
        
        return [asdict(event) for event in events]

    def get_security_statistics(self) -> Dict:
        """보안 통계 조회"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # 최근 24시간 이벤트
        recent_events = [e for e in self.events.values() if e.timestamp > last_24h]
        
        # 최근 7일 이벤트
        weekly_events = [e for e in self.events.values() if e.timestamp > last_7d]
        
        return {
            "total_events": len(self.events),
            "events_24h": len(recent_events),
            "events_7d": len(weekly_events),
            "threat_levels": dict(self.threat_stats),
            "event_types": dict(self.event_stats),
            "active_alerts": len([a for a in self.alerts.values() if not a.is_sent]),
            "resolved_events": len([e for e in self.events.values() if e.is_resolved])
        }

    def resolve_event(self, event_id: str, resolved_by: str) -> bool:
        """이벤트 해결"""
        if event_id not in self.events:
            return False
        
        event = self.events[event_id]
        event.is_resolved = True
        event.resolved_at = datetime.now()
        event.resolved_by = resolved_by
        
        logger.info(f"보안 이벤트 해결: {event_id} (해결자: {resolved_by})")
        return True

    def add_threat_pattern(self, pattern: ThreatPattern) -> bool:
        """위협 패턴 추가"""
        self.threat_patterns.append(pattern)
        logger.info(f"위협 패턴 추가: {pattern.name}")
        return True

    def update_threat_pattern(self, pattern_id: str, is_active: bool) -> bool:
        """위협 패턴 업데이트"""
        for pattern in self.threat_patterns:
            if pattern.pattern_id == pattern_id:
                pattern.is_active = is_active
                logger.info(f"위협 패턴 업데이트: {pattern_id} (활성: {is_active})")
                return True
        return False

    def _update_statistics(self):
        """통계 업데이트"""
        # 실제 환경에서는 더 정교한 통계 계산
        pass

    def _cleanup_old_events(self):
        """오래된 이벤트 정리"""
        cutoff_time = datetime.now() - timedelta(days=30)
        
        old_events = [eid for eid, event in self.events.items() 
                     if event.timestamp < cutoff_time and event.is_resolved]
        
        for event_id in old_events:
            del self.events[event_id]
        
        if old_events:
            logger.info(f"오래된 이벤트 {len(old_events)}개 정리 완료")

    def _generate_event_id(self) -> str:
        """이벤트 ID 생성"""
        return f"evt_{int(time.time() * 1000)}_{hash(str(time.time()))[:8]}"

    def _generate_alert_id(self) -> str:
        """알림 ID 생성"""
        return f"alert_{int(time.time() * 1000)}_{hash(str(time.time()))[:8]}"

# 싱글톤 인스턴스
security_monitoring_service = SecurityMonitoringService()
