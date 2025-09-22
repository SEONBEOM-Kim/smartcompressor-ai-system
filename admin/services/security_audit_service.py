#!/usr/bin/env python3
"""
감사 로그 및 보안 관리 시스템
GitHub를 벤치마킹한 보안 및 감사 시스템
"""

import asyncio
import json
import logging
import time
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque
import ipaddress
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """보안 이벤트 타입"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_CHANGE = "permission_change"
    ROLE_CHANGE = "role_change"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    BRUTE_FORCE_ATTACK = "brute_force_attack"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    CSRF_ATTACK = "csrf_attack"
    FILE_UPLOAD = "file_upload"
    API_ACCESS = "api_access"
    SYSTEM_CONFIG_CHANGE = "system_config_change"

class SecurityLevel(Enum):
    """보안 레벨"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditAction(Enum):
    """감사 액션"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    BACKUP = "backup"
    RESTORE = "restore"

@dataclass
class SecurityEvent:
    """보안 이벤트 클래스"""
    id: str
    event_type: SecurityEventType
    security_level: SecurityLevel
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    description: str
    resource_type: str
    resource_id: str
    success: bool
    failure_reason: Optional[str] = None
    metadata: Dict[str, Any] = None
    geolocation: Optional[Dict[str, Any]] = None
    risk_score: float = 0.0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class AuditLog:
    """감사 로그 클래스"""
    id: str
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

@dataclass
class SecurityRule:
    """보안 규칙 클래스"""
    id: str
    name: str
    description: str
    pattern: str
    event_type: SecurityEventType
    security_level: SecurityLevel
    is_active: bool = True
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class SecurityAlert:
    """보안 알림 클래스"""
    id: str
    event_id: str
    rule_id: str
    severity: SecurityLevel
    title: str
    description: str
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class SecurityAuditService:
    """보안 감사 서비스"""
    
    def __init__(self):
        self.security_events: deque = deque(maxlen=100000)  # 최대 10만개 이벤트 유지
        self.audit_logs: deque = deque(maxlen=100000)
        self.security_rules: Dict[str, SecurityRule] = {}
        self.security_alerts: Dict[str, SecurityAlert] = {}
        self.security_callbacks: List[Callable] = []
        
        # 보안 설정
        self.max_login_attempts = 5
        self.login_attempt_window = 300  # 5분
        self.session_timeout = 3600  # 1시간
        self.password_min_length = 8
        self.password_require_special = True
        
        # IP 화이트리스트/블랙리스트
        self.ip_whitelist: set = set()
        self.ip_blacklist: set = set()
        
        # 의심스러운 IP 추적
        self.suspicious_ips: Dict[str, List[datetime]] = {}
        
        # 초기화
        self._initialize_security_rules()
        self._start_security_monitoring()
    
    def _initialize_security_rules(self):
        """보안 규칙 초기화"""
        # 로그인 실패 규칙
        self.security_rules["login_failure"] = SecurityRule(
            id="login_failure",
            name="로그인 실패",
            description="연속된 로그인 실패 감지",
            pattern="login_failure",
            event_type=SecurityEventType.LOGIN_FAILURE,
            security_level=SecurityLevel.MEDIUM
        )
        
        # 무차별 대입 공격 규칙
        self.security_rules["brute_force"] = SecurityRule(
            id="brute_force",
            name="무차별 대입 공격",
            description="짧은 시간 내 다수의 로그인 실패",
            pattern="multiple_login_failures",
            event_type=SecurityEventType.BRUTE_FORCE_ATTACK,
            security_level=SecurityLevel.HIGH
        )
        
        # SQL 인젝션 규칙
        self.security_rules["sql_injection"] = SecurityRule(
            id="sql_injection",
            name="SQL 인젝션",
            description="SQL 인젝션 시도 감지",
            pattern="(union|select|insert|update|delete|drop|create|alter).*from",
            event_type=SecurityEventType.SQL_INJECTION,
            security_level=SecurityLevel.CRITICAL
        )
        
        # XSS 공격 규칙
        self.security_rules["xss_attack"] = SecurityRule(
            id="xss_attack",
            name="XSS 공격",
            description="XSS 공격 시도 감지",
            pattern="<script|javascript:|onload=|onerror=",
            event_type=SecurityEventType.XSS_ATTACK,
            security_level=SecurityLevel.HIGH
        )
        
        # 권한 변경 규칙
        self.security_rules["permission_change"] = SecurityRule(
            id="permission_change",
            name="권한 변경",
            description="사용자 권한 변경 감지",
            pattern="permission_change|role_change",
            event_type=SecurityEventType.PERMISSION_CHANGE,
            security_level=SecurityLevel.MEDIUM
        )
        
        # 의심스러운 활동 규칙
        self.security_rules["suspicious_activity"] = SecurityRule(
            id="suspicious_activity",
            name="의심스러운 활동",
            description="비정상적인 활동 패턴 감지",
            pattern="unusual_access|off_hours_access",
            event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
            security_level=SecurityLevel.MEDIUM
        )
    
    def _start_security_monitoring(self):
        """보안 모니터링 시작"""
        def security_monitor():
            while True:
                try:
                    self._check_security_rules()
                    self._cleanup_old_data()
                    time.sleep(60)  # 1분마다 체크
                except Exception as e:
                    logger.error(f"보안 모니터링 오류: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=security_monitor, daemon=True)
        thread.start()
        logger.info("보안 모니터링 시작")
    
    def _check_security_rules(self):
        """보안 규칙 확인"""
        # 최근 이벤트들에 대해 규칙 적용
        recent_events = list(self.security_events)[-1000:]  # 최근 1000개 이벤트
        
        for event in recent_events:
            for rule in self.security_rules.values():
                if not rule.is_active:
                    continue
                
                if self._match_rule(event, rule):
                    self._trigger_security_alert(event, rule)
    
    def _match_rule(self, event: SecurityEvent, rule: SecurityRule) -> bool:
        """규칙 매칭 확인"""
        try:
            # 이벤트 타입 확인
            if event.event_type != rule.event_type:
                return False
            
            # 패턴 매칭
            if rule.pattern:
                if re.search(rule.pattern, event.description, re.IGNORECASE):
                    return True
            
            # 특별한 규칙들
            if rule.id == "brute_force":
                return self._check_brute_force_attack(event)
            elif rule.id == "suspicious_activity":
                return self._check_suspicious_activity(event)
            
            return False
            
        except Exception as e:
            logger.error(f"규칙 매칭 오류: {e}")
            return False
    
    def _check_brute_force_attack(self, event: SecurityEvent) -> bool:
        """무차별 대입 공격 확인"""
        if event.event_type != SecurityEventType.LOGIN_FAILURE:
            return False
        
        # 같은 IP에서 최근 로그인 실패 횟수 확인
        recent_failures = [
            e for e in self.security_events
            if (e.event_type == SecurityEventType.LOGIN_FAILURE and
                e.ip_address == event.ip_address and
                (event.timestamp - e.timestamp).total_seconds() <= self.login_attempt_window)
        ]
        
        return len(recent_failures) >= self.max_login_attempts
    
    def _check_suspicious_activity(self, event: SecurityEvent) -> bool:
        """의심스러운 활동 확인"""
        # 비정상적인 시간대 접근 (새벽 2시-6시)
        hour = event.timestamp.hour
        if 2 <= hour <= 6:
            return True
        
        # 의심스러운 IP 확인
        if event.ip_address in self.suspicious_ips:
            recent_activities = [
                t for t in self.suspicious_ips[event.ip_address]
                if (event.timestamp - t).total_seconds() <= 3600  # 1시간 내
            ]
            if len(recent_activities) > 10:  # 1시간 내 10회 이상
                return True
        
        return False
    
    def _trigger_security_alert(self, event: SecurityEvent, rule: SecurityRule):
        """보안 알림 트리거"""
        alert_id = f"alert_{int(time.time() * 1000)}"
        
        alert = SecurityAlert(
            id=alert_id,
            event_id=event.id,
            rule_id=rule.id,
            severity=rule.security_level,
            title=f"{rule.name} 감지",
            description=f"{rule.description}: {event.description}",
            timestamp=datetime.now(),
            metadata={
                'ip_address': event.ip_address,
                'user_id': event.user_id,
                'resource_type': event.resource_type,
                'resource_id': event.resource_id
            }
        )
        
        self.security_alerts[alert_id] = alert
        
        # 규칙 통계 업데이트
        rule.last_triggered = datetime.now()
        rule.trigger_count += 1
        
        # 콜백 실행
        self._notify_security_alert(alert)
        
        logger.warning(f"보안 알림 트리거: {alert_id} - {rule.name}")
    
    def _notify_security_alert(self, alert: SecurityAlert):
        """보안 알림 알림"""
        for callback in self.security_callbacks:
            try:
                callback({
                    'type': 'security_alert',
                    'alert': asdict(alert)
                })
            except Exception as e:
                logger.error(f"보안 알림 알림 오류: {e}")
    
    def _cleanup_old_data(self):
        """오래된 데이터 정리"""
        cutoff_time = datetime.now() - timedelta(days=30)
        
        # 오래된 의심스러운 IP 데이터 정리
        for ip in list(self.suspicious_ips.keys()):
            self.suspicious_ips[ip] = [
                t for t in self.suspicious_ips[ip]
                if t >= cutoff_time
            ]
            if not self.suspicious_ips[ip]:
                del self.suspicious_ips[ip]
    
    def log_security_event(self, event_type: SecurityEventType, user_id: str,
                          ip_address: str, user_agent: str, description: str,
                          resource_type: str = "", resource_id: str = "",
                          success: bool = True, failure_reason: str = None,
                          metadata: Dict[str, Any] = None) -> str:
        """보안 이벤트 로깅"""
        try:
            event_id = f"sec_{int(time.time() * 1000000)}"
            
            # 보안 레벨 결정
            security_level = self._determine_security_level(event_type, success)
            
            # 위험 점수 계산
            risk_score = self._calculate_risk_score(event_type, ip_address, user_id)
            
            # 지리적 위치 정보 (시뮬레이션)
            geolocation = self._get_geolocation(ip_address)
            
            # 보안 이벤트 생성
            event = SecurityEvent(
                id=event_id,
                event_type=event_type,
                security_level=security_level,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.now(),
                description=description,
                resource_type=resource_type,
                resource_id=resource_id,
                success=success,
                failure_reason=failure_reason,
                metadata=metadata or {},
                geolocation=geolocation,
                risk_score=risk_score
            )
            
            # 이벤트 저장
            self.security_events.append(event)
            
            # 의심스러운 IP 추적
            if not success or risk_score > 0.5:
                if ip_address not in self.suspicious_ips:
                    self.suspicious_ips[ip_address] = []
                self.suspicious_ips[ip_address].append(event.timestamp)
            
            # 콜백 실행
            self._notify_security_event(event)
            
            logger.info(f"보안 이벤트 로깅: {event_id} - {event_type.value}")
            return event_id
            
        except Exception as e:
            logger.error(f"보안 이벤트 로깅 오류: {e}")
            return None
    
    def _determine_security_level(self, event_type: SecurityEventType, success: bool) -> SecurityLevel:
        """보안 레벨 결정"""
        if not success:
            if event_type in [SecurityEventType.UNAUTHORIZED_ACCESS, SecurityEventType.BRUTE_FORCE_ATTACK]:
                return SecurityLevel.CRITICAL
            elif event_type in [SecurityEventType.SQL_INJECTION, SecurityEventType.XSS_ATTACK]:
                return SecurityLevel.CRITICAL
            else:
                return SecurityLevel.HIGH
        else:
            if event_type in [SecurityEventType.PERMISSION_CHANGE, SecurityEventType.ROLE_CHANGE]:
                return SecurityLevel.MEDIUM
            else:
                return SecurityLevel.LOW
    
    def _calculate_risk_score(self, event_type: SecurityEventType, ip_address: str, user_id: str) -> float:
        """위험 점수 계산"""
        score = 0.0
        
        # 이벤트 타입별 점수
        if event_type == SecurityEventType.BRUTE_FORCE_ATTACK:
            score += 0.8
        elif event_type == SecurityEventType.SQL_INJECTION:
            score += 0.9
        elif event_type == SecurityEventType.XSS_ATTACK:
            score += 0.7
        elif event_type == SecurityEventType.UNAUTHORIZED_ACCESS:
            score += 0.6
        
        # IP 기반 점수
        if ip_address in self.ip_blacklist:
            score += 0.5
        elif ip_address in self.suspicious_ips:
            recent_activities = len([
                t for t in self.suspicious_ips[ip_address]
                if (datetime.now() - t).total_seconds() <= 3600
            ])
            score += min(0.3, recent_activities * 0.05)
        
        # 사용자 기반 점수 (시뮬레이션)
        if user_id and user_id.startswith('suspicious_'):
            score += 0.4
        
        return min(1.0, score)
    
    def _get_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """지리적 위치 정보 조회 (시뮬레이션)"""
        # 실제로는 GeoIP 서비스를 사용
        return {
            'country': 'KR',
            'city': 'Seoul',
            'latitude': 37.5665,
            'longitude': 126.9780,
            'timezone': 'Asia/Seoul'
        }
    
    def _notify_security_event(self, event: SecurityEvent):
        """보안 이벤트 알림"""
        for callback in self.security_callbacks:
            try:
                callback({
                    'type': 'security_event',
                    'event': asdict(event)
                })
            except Exception as e:
                logger.error(f"보안 이벤트 알림 오류: {e}")
    
    def log_audit_event(self, user_id: str, action: AuditAction, resource_type: str,
                       resource_id: str, ip_address: str, user_agent: str,
                       success: bool = True, details: Dict[str, Any] = None,
                       session_id: str = None, request_id: str = None) -> str:
        """감사 이벤트 로깅"""
        try:
            audit_id = f"audit_{int(time.time() * 1000000)}"
            
            audit_log = AuditLog(
                id=audit_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                timestamp=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                details=details or {},
                session_id=session_id,
                request_id=request_id
            )
            
            self.audit_logs.append(audit_log)
            
            logger.info(f"감사 이벤트 로깅: {audit_id} - {action.value}")
            return audit_id
            
        except Exception as e:
            logger.error(f"감사 이벤트 로깅 오류: {e}")
            return None
    
    def get_security_events(self, event_type: SecurityEventType = None,
                           security_level: SecurityLevel = None,
                           start_time: datetime = None, end_time: datetime = None,
                           limit: int = 1000) -> List[SecurityEvent]:
        """보안 이벤트 조회"""
        events = list(self.security_events)
        
        # 필터링
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if security_level:
            events = [e for e in events if e.security_level == security_level]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # 정렬 및 제한
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]
    
    def get_audit_logs(self, user_id: str = None, action: AuditAction = None,
                      start_time: datetime = None, end_time: datetime = None,
                      limit: int = 1000) -> List[AuditLog]:
        """감사 로그 조회"""
        logs = list(self.audit_logs)
        
        # 필터링
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        if action:
            logs = [l for l in logs if l.action == action]
        
        if start_time:
            logs = [l for l in logs if l.timestamp >= start_time]
        
        if end_time:
            logs = [l for l in logs if l.timestamp <= end_time]
        
        # 정렬 및 제한
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
    
    def get_security_alerts(self, severity: SecurityLevel = None,
                           acknowledged: bool = None, resolved: bool = None,
                           limit: int = 100) -> List[SecurityAlert]:
        """보안 알림 조회"""
        alerts = list(self.security_alerts.values())
        
        # 필터링
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if acknowledged is not None:
            alerts = [a for a in alerts if a.acknowledged == acknowledged]
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        # 정렬 및 제한
        alerts.sort(key=lambda x: x.timestamp, reverse=True)
        return alerts[:limit]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """알림 확인"""
        alert = self.security_alerts.get(alert_id)
        if not alert:
            return False
        
        alert.acknowledged = True
        alert.acknowledged_by = acknowledged_by
        alert.acknowledged_at = datetime.now()
        
        logger.info(f"보안 알림 확인: {alert_id} - {acknowledged_by}")
        return True
    
    def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """알림 해결"""
        alert = self.security_alerts.get(alert_id)
        if not alert:
            return False
        
        alert.resolved = True
        alert.resolved_by = resolved_by
        alert.resolved_at = datetime.now()
        
        logger.info(f"보안 알림 해결: {alert_id} - {resolved_by}")
        return True
    
    def add_ip_to_blacklist(self, ip_address: str, reason: str = None):
        """IP 블랙리스트 추가"""
        self.ip_blacklist.add(ip_address)
        logger.warning(f"IP 블랙리스트 추가: {ip_address} - {reason}")
    
    def remove_ip_from_blacklist(self, ip_address: str):
        """IP 블랙리스트 제거"""
        self.ip_blacklist.discard(ip_address)
        logger.info(f"IP 블랙리스트 제거: {ip_address}")
    
    def add_ip_to_whitelist(self, ip_address: str, reason: str = None):
        """IP 화이트리스트 추가"""
        self.ip_whitelist.add(ip_address)
        logger.info(f"IP 화이트리스트 추가: {ip_address} - {reason}")
    
    def get_security_statistics(self, days: int = 30) -> Dict[str, Any]:
        """보안 통계 조회"""
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_events = [e for e in self.security_events if e.timestamp >= cutoff_time]
        recent_logs = [l for l in self.audit_logs if l.timestamp >= cutoff_time]
        
        # 이벤트 타입별 통계
        event_type_stats = {}
        for event_type in SecurityEventType:
            event_type_stats[event_type.value] = len([
                e for e in recent_events if e.event_type == event_type
            ])
        
        # 보안 레벨별 통계
        security_level_stats = {}
        for level in SecurityLevel:
            security_level_stats[level.value] = len([
                e for e in recent_events if e.security_level == level
            ])
        
        # 액션별 통계
        action_stats = {}
        for action in AuditAction:
            action_stats[action.value] = len([
                l for l in recent_logs if l.action == action
            ])
        
        # 활성 알림 통계
        active_alerts = [a for a in self.security_alerts.values() if not a.resolved]
        critical_alerts = [a for a in active_alerts if a.severity == SecurityLevel.CRITICAL]
        
        return {
            'total_security_events': len(recent_events),
            'total_audit_logs': len(recent_logs),
            'event_type_stats': event_type_stats,
            'security_level_stats': security_level_stats,
            'action_stats': action_stats,
            'active_alerts': len(active_alerts),
            'critical_alerts': len(critical_alerts),
            'blacklisted_ips': len(self.ip_blacklist),
            'whitelisted_ips': len(self.ip_whitelist),
            'suspicious_ips': len(self.suspicious_ips),
            'time_range': {
                'start': cutoff_time.isoformat(),
                'end': datetime.now().isoformat()
            }
        }
    
    def add_security_callback(self, callback: Callable):
        """보안 콜백 함수 추가"""
        self.security_callbacks.append(callback)
    
    def remove_security_callback(self, callback: Callable):
        """보안 콜백 함수 제거"""
        if callback in self.security_callbacks:
            self.security_callbacks.remove(callback)
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'total_security_events': len(self.security_events),
            'total_audit_logs': len(self.audit_logs),
            'security_rules': len(self.security_rules),
            'active_alerts': len([a for a in self.security_alerts.values() if not a.resolved]),
            'blacklisted_ips': len(self.ip_blacklist),
            'whitelisted_ips': len(self.ip_whitelist),
            'suspicious_ips': len(self.suspicious_ips),
            'max_login_attempts': self.max_login_attempts,
            'login_attempt_window': self.login_attempt_window
        }

# 전역 인스턴스
security_audit_service = SecurityAuditService()
