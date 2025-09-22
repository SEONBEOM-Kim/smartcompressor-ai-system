"""
침입 탐지 시스템 - Stripe & AWS 보안 시스템 벤치마킹
실시간 침입 탐지, 이상 행동 분석, 자동 대응 시스템
"""

import logging
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

logger = logging.getLogger(__name__)

class AttackType(Enum):
    """공격 유형"""
    BRUTE_FORCE = "brute_force"
    DDoS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    MALWARE = "malware"
    PHISHING = "phishing"
    INSIDER_THREAT = "insider_threat"

class ThreatLevel(Enum):
    """위협 수준"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResponseAction(Enum):
    """대응 액션"""
    LOG_ONLY = "log_only"
    BLOCK_IP = "block_ip"
    RATE_LIMIT = "rate_limit"
    REQUIRE_2FA = "require_2fa"
    SUSPEND_USER = "suspend_user"
    ALERT_ADMIN = "alert_admin"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"

@dataclass
class NetworkTraffic:
    """네트워크 트래픽"""
    timestamp: datetime
    source_ip: str
    dest_ip: str
    port: int
    protocol: str
    bytes_sent: int
    bytes_received: int
    duration: float
    flags: str

@dataclass
class UserBehavior:
    """사용자 행동"""
    user_id: str
    timestamp: datetime
    action: str
    endpoint: str
    ip_address: str
    user_agent: str
    success: bool
    response_time: float
    data_size: int

@dataclass
class AttackSignature:
    """공격 시그니처"""
    signature_id: str
    attack_type: AttackType
    pattern: str
    threat_level: ThreatLevel
    response_actions: List[ResponseAction]
    is_active: bool = True

@dataclass
class IntrusionEvent:
    """침입 이벤트"""
    event_id: str
    attack_type: AttackType
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: str
    user_id: Optional[str]
    description: str
    confidence: float
    response_actions: List[ResponseAction]
    is_handled: bool = False
    handled_at: Optional[datetime] = None

class IntrusionDetectionService:
    """
    Stripe & AWS 보안 시스템을 벤치마킹한 침입 탐지 시스템
    """
    
    def __init__(self):
        # 데이터 저장소
        self.network_traffic: deque = deque(maxlen=10000)
        self.user_behaviors: deque = deque(maxlen=10000)
        self.intrusion_events: Dict[str, IntrusionEvent] = {}
        
        # 공격 시그니처
        self.attack_signatures: List[AttackSignature] = []
        self._initialize_attack_signatures()
        
        # ML 모델
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.is_training = False
        
        # 통계 데이터
        self.traffic_stats = defaultdict(int)
        self.behavior_stats = defaultdict(int)
        
        # 탐지 스레드
        self.detection_thread = None
        self.is_detecting = False
        
        # 임계값 설정
        self.thresholds = {
            "brute_force_attempts": 5,
            "ddos_requests_per_second": 100,
            "suspicious_data_access": 1000,
            "anomaly_score": 0.7
        }
        
        logger.info("IntrusionDetectionService 초기화 완료")

    def _initialize_attack_signatures(self):
        """공격 시그니처 초기화"""
        signatures = [
            AttackSignature(
                signature_id="sql_injection_1",
                attack_type=AttackType.SQL_INJECTION,
                pattern=r"(?i)(union\s+select|drop\s+table|insert\s+into|delete\s+from)",
                threat_level=ThreatLevel.HIGH,
                response_actions=[ResponseAction.BLOCK_IP, ResponseAction.ALERT_ADMIN]
            ),
            AttackSignature(
                signature_id="xss_1",
                attack_type=AttackType.XSS,
                pattern=r"<script[^>]*>.*?</script>",
                threat_level=ThreatLevel.MEDIUM,
                response_actions=[ResponseAction.RATE_LIMIT, ResponseAction.ALERT_ADMIN]
            ),
            AttackSignature(
                signature_id="path_traversal_1",
                attack_type=AttackType.PRIVILEGE_ESCALATION,
                pattern=r"\.\./",
                threat_level=ThreatLevel.MEDIUM,
                response_actions=[ResponseAction.BLOCK_IP, ResponseAction.ALERT_ADMIN]
            ),
            AttackSignature(
                signature_id="command_injection_1",
                attack_type=AttackType.PRIVILEGE_ESCALATION,
                pattern=r"[;&|`$]",
                threat_level=ThreatLevel.HIGH,
                response_actions=[ResponseAction.BLOCK_IP, ResponseAction.ALERT_ADMIN]
            ),
            AttackSignature(
                signature_id="csrf_1",
                attack_type=AttackType.CSRF,
                pattern=r"csrf",
                threat_level=ThreatLevel.MEDIUM,
                response_actions=[ResponseAction.LOG_ONLY, ResponseAction.ALERT_ADMIN]
            )
        ]
        
        self.attack_signatures.extend(signatures)

    def start_detection(self):
        """침입 탐지 시작"""
        if self.is_detecting:
            return
        
        self.is_detecting = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        
        logger.info("침입 탐지 시스템 시작")

    def stop_detection(self):
        """침입 탐지 중지"""
        self.is_detecting = False
        if self.detection_thread:
            self.detection_thread.join(timeout=5)
        
        logger.info("침입 탐지 시스템 중지")

    def _detection_loop(self):
        """탐지 루프"""
        while self.is_detecting:
            try:
                # 시그니처 기반 탐지
                self._signature_based_detection()
                
                # 행동 기반 탐지
                self._behavior_based_detection()
                
                # ML 기반 이상 탐지
                self._ml_based_detection()
                
                # 통계 업데이트
                self._update_statistics()
                
                time.sleep(1)  # 1초마다 체크
                
            except Exception as e:
                logger.error(f"탐지 루프 오류: {e}")

    def log_network_traffic(self, source_ip: str, dest_ip: str, port: int,
                           protocol: str, bytes_sent: int, bytes_received: int,
                           duration: float, flags: str = ""):
        """네트워크 트래픽 로깅"""
        traffic = NetworkTraffic(
            timestamp=datetime.now(),
            source_ip=source_ip,
            dest_ip=dest_ip,
            port=port,
            protocol=protocol,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            duration=duration,
            flags=flags
        )
        
        self.network_traffic.append(traffic)
        
        # DDoS 탐지
        self._detect_ddos_attack(source_ip)

    def log_user_behavior(self, user_id: str, action: str, endpoint: str,
                         ip_address: str, user_agent: str, success: bool,
                         response_time: float, data_size: int = 0):
        """사용자 행동 로깅"""
        behavior = UserBehavior(
            user_id=user_id,
            timestamp=datetime.now(),
            action=action,
            endpoint=endpoint,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            response_time=response_time,
            data_size=data_size
        )
        
        self.user_behaviors.append(behavior)
        
        # 브루트 포스 공격 탐지
        if not success and action == "login":
            self._detect_brute_force_attack(ip_address, user_id)

    def _signature_based_detection(self):
        """시그니처 기반 탐지"""
        import re
        
        # 최근 사용자 행동 검사
        recent_behaviors = [b for b in self.user_behaviors 
                           if (datetime.now() - b.timestamp).total_seconds() < 60]
        
        for behavior in recent_behaviors:
            for signature in self.attack_signatures:
                if not signature.is_active:
                    continue
                
                # 패턴 매칭
                if re.search(signature.pattern, behavior.action) or \
                   re.search(signature.pattern, behavior.endpoint) or \
                   re.search(signature.pattern, behavior.user_agent):
                    
                    self._create_intrusion_event(
                        attack_type=signature.attack_type,
                        threat_level=signature.threat_level,
                        source_ip=behavior.ip_address,
                        user_id=behavior.user_id,
                        description=f"시그니처 매칭: {signature.signature_id}",
                        confidence=0.9,
                        response_actions=signature.response_actions
                    )

    def _behavior_based_detection(self):
        """행동 기반 탐지"""
        # 비정상적인 데이터 접근 패턴 탐지
        self._detect_data_exfiltration()
        
        # 권한 상승 시도 탐지
        self._detect_privilege_escalation()
        
        # 내부자 위협 탐지
        self._detect_insider_threat()

    def _detect_ddos_attack(self, source_ip: str):
        """DDoS 공격 탐지"""
        now = datetime.now()
        recent_traffic = [t for t in self.network_traffic 
                         if t.source_ip == source_ip and 
                         (now - t.timestamp).total_seconds() < 60]
        
        if len(recent_traffic) > self.thresholds["ddos_requests_per_second"]:
            self._create_intrusion_event(
                attack_type=AttackType.DDoS,
                threat_level=ThreatLevel.HIGH,
                source_ip=source_ip,
                user_id=None,
                description=f"DDoS 공격 의심: {len(recent_traffic)} 요청/분",
                confidence=0.8,
                response_actions=[ResponseAction.BLOCK_IP, ResponseAction.ALERT_ADMIN]
            )

    def _detect_brute_force_attack(self, ip_address: str, user_id: str):
        """브루트 포스 공격 탐지"""
        now = datetime.now()
        recent_failures = [b for b in self.user_behaviors 
                          if b.ip_address == ip_address and 
                          not b.success and 
                          b.action == "login" and
                          (now - b.timestamp).total_seconds() < 300]  # 5분
        
        if len(recent_failures) >= self.thresholds["brute_force_attempts"]:
            self._create_intrusion_event(
                attack_type=AttackType.BRUTE_FORCE,
                threat_level=ThreatLevel.MEDIUM,
                source_ip=ip_address,
                user_id=user_id,
                description=f"브루트 포스 공격 의심: {len(recent_failures)} 실패 시도",
                confidence=0.7,
                response_actions=[ResponseAction.BLOCK_IP, ResponseAction.ALERT_ADMIN]
            )

    def _detect_data_exfiltration(self):
        """데이터 유출 탐지"""
        now = datetime.now()
        recent_behaviors = [b for b in self.user_behaviors 
                           if (now - b.timestamp).total_seconds() < 3600]  # 1시간
        
        # 사용자별 데이터 접근량 계산
        user_data_access = defaultdict(int)
        for behavior in recent_behaviors:
            user_data_access[behavior.user_id] += behavior.data_size
        
        # 임계값 초과 사용자 탐지
        for user_id, data_size in user_data_access.items():
            if data_size > self.thresholds["suspicious_data_access"]:
                self._create_intrusion_event(
                    attack_type=AttackType.DATA_EXFILTRATION,
                    threat_level=ThreatLevel.CRITICAL,
                    source_ip=recent_behaviors[0].ip_address,
                    user_id=user_id,
                    description=f"데이터 유출 의심: {data_size} bytes 접근",
                    confidence=0.8,
                    response_actions=[ResponseAction.SUSPEND_USER, ResponseAction.ALERT_ADMIN]
                )

    def _detect_privilege_escalation(self):
        """권한 상승 시도 탐지"""
        # 관리자 권한 요청 패턴 분석
        recent_behaviors = [b for b in self.user_behaviors 
                           if (datetime.now() - b.timestamp).total_seconds() < 3600]
        
        admin_endpoints = ["/admin/", "/api/admin/", "/manage/"]
        privilege_requests = [b for b in recent_behaviors 
                             if any(ep in b.endpoint for ep in admin_endpoints)]
        
        # 비정상적인 권한 요청 패턴
        if len(privilege_requests) > 10:  # 1시간 내 10회 이상 관리자 기능 접근
            self._create_intrusion_event(
                attack_type=AttackType.PRIVILEGE_ESCALATION,
                threat_level=ThreatLevel.HIGH,
                source_ip=privilege_requests[0].ip_address,
                user_id=privilege_requests[0].user_id,
                description="권한 상승 시도 의심",
                confidence=0.6,
                response_actions=[ResponseAction.REQUIRE_2FA, ResponseAction.ALERT_ADMIN]
            )

    def _detect_insider_threat(self):
        """내부자 위협 탐지"""
        # 비정상적인 시간대 접근
        now = datetime.now()
        if now.hour < 6 or now.hour > 22:  # 새벽 6시 이전 또는 밤 10시 이후
            recent_behaviors = [b for b in self.user_behaviors 
                               if (now - b.timestamp).total_seconds() < 3600]
            
            if recent_behaviors:
                self._create_intrusion_event(
                    attack_type=AttackType.INSIDER_THREAT,
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=recent_behaviors[0].ip_address,
                    user_id=recent_behaviors[0].user_id,
                    description="비정상적인 시간대 접근",
                    confidence=0.5,
                    response_actions=[ResponseAction.LOG_ONLY, ResponseAction.ALERT_ADMIN]
                )

    def _ml_based_detection(self):
        """ML 기반 이상 탐지"""
        if not self.anomaly_detector:
            return
        
        # 최근 행동 데이터 수집
        recent_behaviors = [b for b in self.user_behaviors 
                           if (datetime.now() - b.timestamp).total_seconds() < 3600]
        
        if len(recent_behaviors) < 10:  # 충분한 데이터가 없으면 스킵
            return
        
        # 특성 추출
        features = self._extract_behavior_features(recent_behaviors)
        
        if features is None:
            return
        
        # 이상 점수 계산
        anomaly_scores = self.anomaly_detector.decision_function(features)
        
        # 임계값 초과 시 이상 탐지
        for i, score in enumerate(anomaly_scores):
            if score < -self.thresholds["anomaly_score"]:
                behavior = recent_behaviors[i]
                self._create_intrusion_event(
                    attack_type=AttackType.MALWARE,  # 일반적인 이상 행동
                    threat_level=ThreatLevel.MEDIUM,
                    source_ip=behavior.ip_address,
                    user_id=behavior.user_id,
                    description=f"ML 기반 이상 탐지 (점수: {score:.3f})",
                    confidence=abs(score),
                    response_actions=[ResponseAction.LOG_ONLY, ResponseAction.ALERT_ADMIN]
                )

    def _extract_behavior_features(self, behaviors: List[UserBehavior]) -> Optional[np.ndarray]:
        """행동 특성 추출"""
        try:
            features = []
            for behavior in behaviors:
                feature_vector = [
                    behavior.response_time,
                    behavior.data_size,
                    1 if behavior.success else 0,
                    len(behavior.endpoint),
                    len(behavior.user_agent),
                    behavior.timestamp.hour,
                    behavior.timestamp.weekday()
                ]
                features.append(feature_vector)
            
            return np.array(features)
        except Exception as e:
            logger.error(f"특성 추출 오류: {e}")
            return None

    def train_anomaly_detector(self):
        """이상 탐지 모델 훈련"""
        if self.is_training:
            return
        
        self.is_training = True
        
        try:
            # 훈련 데이터 수집
            training_data = []
            for behavior in self.user_behaviors:
                features = self._extract_behavior_features([behavior])
                if features is not None:
                    training_data.extend(features)
            
            if len(training_data) < 100:  # 충분한 데이터가 없으면 스킵
                logger.warning("훈련 데이터가 부족합니다.")
                return
            
            # 데이터 정규화
            training_data = np.array(training_data)
            training_data = self.scaler.fit_transform(training_data)
            
            # Isolation Forest 모델 훈련
            self.anomaly_detector = IsolationForest(
                contamination=0.1,  # 10% 이상치
                random_state=42
            )
            self.anomaly_detector.fit(training_data)
            
            # 모델 저장
            joblib.dump(self.anomaly_detector, 'models/anomaly_detector.pkl')
            joblib.dump(self.scaler, 'models/scaler.pkl')
            
            logger.info("이상 탐지 모델 훈련 완료")
            
        except Exception as e:
            logger.error(f"모델 훈련 오류: {e}")
        finally:
            self.is_training = False

    def load_anomaly_detector(self):
        """이상 탐지 모델 로드"""
        try:
            self.anomaly_detector = joblib.load('models/anomaly_detector.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            logger.info("이상 탐지 모델 로드 완료")
        except FileNotFoundError:
            logger.warning("훈련된 모델이 없습니다. 훈련을 실행하세요.")
        except Exception as e:
            logger.error(f"모델 로드 오류: {e}")

    def _create_intrusion_event(self, attack_type: AttackType, threat_level: ThreatLevel,
                               source_ip: str, user_id: Optional[str], description: str,
                               confidence: float, response_actions: List[ResponseAction]):
        """침입 이벤트 생성"""
        event_id = self._generate_event_id()
        
        event = IntrusionEvent(
            event_id=event_id,
            attack_type=attack_type,
            threat_level=threat_level,
            timestamp=datetime.now(),
            source_ip=source_ip,
            user_id=user_id,
            description=description,
            confidence=confidence,
            response_actions=response_actions
        )
        
        self.intrusion_events[event_id] = event
        
        # 자동 대응 실행
        self._execute_response_actions(event)
        
        logger.warning(f"침입 이벤트 생성: {attack_type.value} - {description} (IP: {source_ip})")

    def _execute_response_actions(self, event: IntrusionEvent):
        """대응 액션 실행"""
        for action in event.response_actions:
            try:
                if action == ResponseAction.BLOCK_IP:
                    self._block_ip(event.source_ip)
                elif action == ResponseAction.RATE_LIMIT:
                    self._apply_rate_limit(event.source_ip)
                elif action == ResponseAction.REQUIRE_2FA:
                    self._require_2fa(event.user_id)
                elif action == ResponseAction.SUSPEND_USER:
                    self._suspend_user(event.user_id)
                elif action == ResponseAction.ALERT_ADMIN:
                    self._alert_admin(event)
                elif action == ResponseAction.EMERGENCY_SHUTDOWN:
                    self._emergency_shutdown()
                
            except Exception as e:
                logger.error(f"대응 액션 실행 실패 ({action.value}): {e}")

    def _block_ip(self, ip_address: str):
        """IP 차단"""
        # 실제 환경에서는 방화벽이나 로드밸런서에 차단 규칙 추가
        logger.warning(f"IP 차단: {ip_address}")

    def _apply_rate_limit(self, ip_address: str):
        """Rate Limit 적용"""
        # 실제 환경에서는 Rate Limiter에 제한 규칙 추가
        logger.warning(f"Rate Limit 적용: {ip_address}")

    def _require_2fa(self, user_id: str):
        """2FA 요구"""
        # 실제 환경에서는 사용자 세션에 2FA 플래그 설정
        logger.warning(f"2FA 요구: {user_id}")

    def _suspend_user(self, user_id: str):
        """사용자 정지"""
        # 실제 환경에서는 사용자 계정 비활성화
        logger.warning(f"사용자 정지: {user_id}")

    def _alert_admin(self, event: IntrusionEvent):
        """관리자 알림"""
        # 실제 환경에서는 알림 시스템으로 전송
        logger.warning(f"관리자 알림: {event.description}")

    def _emergency_shutdown(self):
        """긴급 종료"""
        # 실제 환경에서는 시스템 종료 또는 서비스 중단
        logger.critical("긴급 종료 실행")

    def get_intrusion_events(self, limit: int = 100, 
                            attack_type: Optional[AttackType] = None,
                            threat_level: Optional[ThreatLevel] = None) -> List[Dict]:
        """침입 이벤트 조회"""
        events = list(self.intrusion_events.values())
        
        # 필터링
        if attack_type:
            events = [e for e in events if e.attack_type == attack_type]
        if threat_level:
            events = [e for e in events if e.threat_level == threat_level]
        
        # 시간순 정렬 (최신순)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 제한
        events = events[:limit]
        
        return [asdict(event) for event in events]

    def get_detection_statistics(self) -> Dict:
        """탐지 통계 조회"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        recent_events = [e for e in self.intrusion_events.values() if e.timestamp > last_24h]
        
        attack_type_stats = defaultdict(int)
        threat_level_stats = defaultdict(int)
        
        for event in self.intrusion_events.values():
            attack_type_stats[event.attack_type.value] += 1
            threat_level_stats[event.threat_level.value] += 1
        
        return {
            "total_events": len(self.intrusion_events),
            "events_24h": len(recent_events),
            "attack_types": dict(attack_type_stats),
            "threat_levels": dict(threat_level_stats),
            "handled_events": len([e for e in self.intrusion_events.values() if e.is_handled]),
            "active_detection": self.is_detecting
        }

    def handle_intrusion_event(self, event_id: str, handled_by: str) -> bool:
        """침입 이벤트 처리"""
        if event_id not in self.intrusion_events:
            return False
        
        event = self.intrusion_events[event_id]
        event.is_handled = True
        event.handled_at = datetime.now()
        
        logger.info(f"침입 이벤트 처리 완료: {event_id} (처리자: {handled_by})")
        return True

    def add_attack_signature(self, signature: AttackSignature) -> bool:
        """공격 시그니처 추가"""
        self.attack_signatures.append(signature)
        logger.info(f"공격 시그니처 추가: {signature.signature_id}")
        return True

    def update_attack_signature(self, signature_id: str, is_active: bool) -> bool:
        """공격 시그니처 업데이트"""
        for signature in self.attack_signatures:
            if signature.signature_id == signature_id:
                signature.is_active = is_active
                logger.info(f"공격 시그니처 업데이트: {signature_id} (활성: {is_active})")
                return True
        return False

    def _update_statistics(self):
        """통계 업데이트"""
        # 실제 환경에서는 더 정교한 통계 계산
        pass

    def _generate_event_id(self) -> str:
        """이벤트 ID 생성"""
        return f"intrusion_{int(time.time() * 1000)}_{hash(str(time.time()))[:8]}"

# 싱글톤 인스턴스
intrusion_detection_service = IntrusionDetectionService()
