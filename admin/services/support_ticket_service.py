#!/usr/bin/env python3
"""
고객 지원 티켓 시스템
Stripe Dashboard를 벤치마킹한 고객 지원 시스템
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TicketStatus(Enum):
    """티켓 상태"""
    OPEN = "open"                 # 열림
    IN_PROGRESS = "in_progress"   # 진행 중
    PENDING_CUSTOMER = "pending_customer"  # 고객 대기
    PENDING_INTERNAL = "pending_internal"  # 내부 대기
    RESOLVED = "resolved"         # 해결됨
    CLOSED = "closed"             # 닫힘
    CANCELLED = "cancelled"       # 취소됨

class TicketPriority(Enum):
    """티켓 우선순위"""
    LOW = "low"                   # 낮음
    NORMAL = "normal"             # 보통
    HIGH = "high"                 # 높음
    URGENT = "urgent"             # 긴급
    CRITICAL = "critical"         # 위험

class TicketCategory(Enum):
    """티켓 카테고리"""
    TECHNICAL = "technical"       # 기술적 문제
    BILLING = "billing"           # 결제 문제
    ACCOUNT = "account"           # 계정 문제
    FEATURE_REQUEST = "feature_request"  # 기능 요청
    BUG_REPORT = "bug_report"     # 버그 신고
    GENERAL = "general"           # 일반 문의
    COMPLAINT = "complaint"       # 불만사항
    PRAISE = "praise"             # 칭찬

class TicketSource(Enum):
    """티켓 소스"""
    EMAIL = "email"               # 이메일
    PHONE = "phone"               # 전화
    WEB = "web"                   # 웹사이트
    MOBILE_APP = "mobile_app"     # 모바일 앱
    API = "api"                   # API
    CHAT = "chat"                 # 채팅

@dataclass
class Ticket:
    """티켓 클래스"""
    id: str
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    source: TicketSource
    customer_id: str
    customer_name: str
    customer_email: str
    assigned_to: Optional[str] = None
    assigned_agent: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    tags: List[str] = None
    attachments: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.tags is None:
            self.tags = []
        if self.attachments is None:
            self.attachments = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class TicketComment:
    """티켓 댓글 클래스"""
    id: str
    ticket_id: str
    author_id: str
    author_name: str
    author_type: str  # 'customer' or 'agent'
    content: str
    is_internal: bool = False
    created_at: datetime = None
    attachments: List[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.attachments is None:
            self.attachments = []

@dataclass
class TicketTemplate:
    """티켓 템플릿 클래스"""
    id: str
    name: str
    category: TicketCategory
    priority: TicketPriority
    title_template: str
    description_template: str
    tags: List[str] = None
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.tags is None:
            self.tags = []

class SupportTicketService:
    """고객 지원 티켓 서비스"""
    
    def __init__(self):
        self.tickets: Dict[str, Ticket] = {}
        self.comments: Dict[str, List[TicketComment]] = {}
        self.templates: Dict[str, TicketTemplate] = {}
        self.ticket_callbacks: List[Callable] = []
        
        # 자동 할당 설정
        self.auto_assign_enabled = True
        self.auto_assign_rules = {
            TicketCategory.TECHNICAL: "technical_team",
            TicketCategory.BILLING: "billing_team",
            TicketCategory.ACCOUNT: "account_team",
            TicketCategory.BUG_REPORT: "technical_team"
        }
        
        # SLA 설정 (시간)
        self.sla_settings = {
            TicketPriority.CRITICAL: 1,    # 1시간
            TicketPriority.URGENT: 4,      # 4시간
            TicketPriority.HIGH: 24,       # 24시간
            TicketPriority.NORMAL: 72,     # 72시간
            TicketPriority.LOW: 168        # 168시간 (1주일)
        }
        
        # 초기화
        self._initialize_templates()
        self._start_sla_monitoring()
    
    def _initialize_templates(self):
        """티켓 템플릿 초기화"""
        # 기술적 문제 템플릿
        self.templates["technical_issue"] = TicketTemplate(
            id="technical_issue",
            name="기술적 문제",
            category=TicketCategory.TECHNICAL,
            priority=TicketPriority.HIGH,
            title_template="기술적 문제: {issue_type}",
            description_template="문제 유형: {issue_type}\n상세 설명: {description}\n발생 시간: {occurred_at}\n재현 단계: {steps}",
            tags=["technical", "bug"]
        )
        
        # 결제 문제 템플릿
        self.templates["billing_issue"] = TicketTemplate(
            id="billing_issue",
            name="결제 문제",
            category=TicketCategory.BILLING,
            priority=TicketPriority.NORMAL,
            title_template="결제 문제: {payment_type}",
            description_template="결제 유형: {payment_type}\n거래 ID: {transaction_id}\n문제 설명: {description}\n요청 금액: {amount}",
            tags=["billing", "payment"]
        )
        
        # 계정 문제 템플릿
        self.templates["account_issue"] = TicketTemplate(
            id="account_issue",
            name="계정 문제",
            category=TicketCategory.ACCOUNT,
            priority=TicketPriority.NORMAL,
            title_template="계정 문제: {issue_type}",
            description_template="문제 유형: {issue_type}\n사용자 ID: {user_id}\n문제 설명: {description}",
            tags=["account", "access"]
        )
        
        # 기능 요청 템플릿
        self.templates["feature_request"] = TicketTemplate(
            id="feature_request",
            name="기능 요청",
            category=TicketCategory.FEATURE_REQUEST,
            priority=TicketPriority.LOW,
            title_template="기능 요청: {feature_name}",
            description_template="요청 기능: {feature_name}\n상세 설명: {description}\n예상 효과: {expected_benefit}",
            tags=["feature", "enhancement"]
        )
    
    def _start_sla_monitoring(self):
        """SLA 모니터링 시작"""
        def sla_monitor():
            while True:
                try:
                    self._check_sla_violations()
                    time.sleep(300)  # 5분마다 체크
                except Exception as e:
                    logger.error(f"SLA 모니터링 오류: {e}")
                    time.sleep(60)
        
        thread = threading.Thread(target=sla_monitor, daemon=True)
        thread.start()
        logger.info("SLA 모니터링 시작")
    
    def _check_sla_violations(self):
        """SLA 위반 확인"""
        current_time = datetime.now()
        
        for ticket in self.tickets.values():
            if ticket.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED, TicketStatus.CANCELLED]:
                continue
            
            sla_hours = self.sla_settings.get(ticket.priority, 72)
            due_time = ticket.created_at + timedelta(hours=sla_hours)
            
            if current_time > due_time and ticket.status != TicketStatus.IN_PROGRESS:
                # SLA 위반 알림
                self._notify_sla_violation(ticket)
    
    def _notify_sla_violation(self, ticket: Ticket):
        """SLA 위반 알림"""
        logger.warning(f"SLA 위반: 티켓 {ticket.id} - {ticket.title}")
        
        # 콜백 실행
        for callback in self.ticket_callbacks:
            try:
                callback({
                    'type': 'sla_violation',
                    'ticket': asdict(ticket)
                })
            except Exception as e:
                logger.error(f"SLA 위반 알림 오류: {e}")
    
    def create_ticket(self, ticket_data: Dict[str, Any]) -> str:
        """티켓 생성"""
        try:
            # 티켓 ID 생성
            ticket_id = f"TKT-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
            
            # 우선순위 자동 설정
            priority = self._determine_priority(ticket_data)
            
            # 카테고리 자동 설정
            category = self._determine_category(ticket_data)
            
            # 티켓 생성
            ticket = Ticket(
                id=ticket_id,
                title=ticket_data['title'],
                description=ticket_data['description'],
                status=TicketStatus.OPEN,
                priority=priority,
                category=category,
                source=TicketSource(ticket_data.get('source', 'web')),
                customer_id=ticket_data['customer_id'],
                customer_name=ticket_data['customer_name'],
                customer_email=ticket_data['customer_email'],
                tags=ticket_data.get('tags', []),
                metadata=ticket_data.get('metadata', {})
            )
            
            # SLA 기반 마감일 설정
            sla_hours = self.sla_settings.get(priority, 72)
            ticket.due_date = ticket.created_at + timedelta(hours=sla_hours)
            
            # 자동 할당
            if self.auto_assign_enabled:
                assigned_team = self.auto_assign_rules.get(category)
                if assigned_team:
                    ticket.assigned_to = assigned_team
            
            # 티켓 저장
            self.tickets[ticket_id] = ticket
            self.comments[ticket_id] = []
            
            # 콜백 실행
            self._notify_ticket_created(ticket)
            
            logger.info(f"티켓 생성: {ticket_id} - {ticket.title}")
            return ticket_id
            
        except Exception as e:
            logger.error(f"티켓 생성 오류: {e}")
            return None
    
    def _determine_priority(self, ticket_data: Dict[str, Any]) -> TicketPriority:
        """우선순위 자동 결정"""
        title = ticket_data.get('title', '').lower()
        description = ticket_data.get('description', '').lower()
        
        # 긴급 키워드 확인
        urgent_keywords = ['urgent', 'critical', 'emergency', 'urgent', '긴급', '위험', '중대']
        if any(keyword in title or keyword in description for keyword in urgent_keywords):
            return TicketPriority.URGENT
        
        # 높은 우선순위 키워드 확인
        high_keywords = ['error', 'bug', 'broken', 'not working', '오류', '버그', '작동안함']
        if any(keyword in title or keyword in description for keyword in high_keywords):
            return TicketPriority.HIGH
        
        # 카테고리별 기본 우선순위
        category = ticket_data.get('category', 'general')
        if category == 'technical':
            return TicketPriority.HIGH
        elif category == 'billing':
            return TicketPriority.NORMAL
        else:
            return TicketPriority.NORMAL
    
    def _determine_category(self, ticket_data: Dict[str, Any]) -> TicketCategory:
        """카테고리 자동 결정"""
        title = ticket_data.get('title', '').lower()
        description = ticket_data.get('description', '').lower()
        
        # 기술적 문제 키워드
        technical_keywords = ['error', 'bug', 'technical', 'system', '오류', '버그', '기술']
        if any(keyword in title or keyword in description for keyword in technical_keywords):
            return TicketCategory.TECHNICAL
        
        # 결제 문제 키워드
        billing_keywords = ['payment', 'billing', 'charge', 'refund', '결제', '청구', '환불']
        if any(keyword in title or keyword in description for keyword in billing_keywords):
            return TicketCategory.BILLING
        
        # 계정 문제 키워드
        account_keywords = ['account', 'login', 'password', 'access', '계정', '로그인', '비밀번호']
        if any(keyword in title or keyword in description for keyword in account_keywords):
            return TicketCategory.ACCOUNT
        
        # 기능 요청 키워드
        feature_keywords = ['feature', 'request', 'enhancement', 'improvement', '기능', '요청', '개선']
        if any(keyword in title or keyword in description for keyword in feature_keywords):
            return TicketCategory.FEATURE_REQUEST
        
        return TicketCategory.GENERAL
    
    def _notify_ticket_created(self, ticket: Ticket):
        """티켓 생성 알림"""
        for callback in self.ticket_callbacks:
            try:
                callback({
                    'type': 'ticket_created',
                    'ticket': asdict(ticket)
                })
            except Exception as e:
                logger.error(f"티켓 생성 알림 오류: {e}")
    
    def update_ticket_status(self, ticket_id: str, status: TicketStatus, 
                           updated_by: str, comment: str = None) -> bool:
        """티켓 상태 업데이트"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        
        old_status = ticket.status
        ticket.status = status
        ticket.updated_at = datetime.now()
        
        # 상태별 특별 처리
        if status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now()
        elif status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.now()
        
        # 댓글 추가
        if comment:
            self.add_comment(ticket_id, updated_by, "system", comment, is_internal=True)
        
        # 콜백 실행
        self._notify_ticket_updated(ticket, old_status)
        
        logger.info(f"티켓 상태 업데이트: {ticket_id} - {old_status.value} -> {status.value}")
        return True
    
    def assign_ticket(self, ticket_id: str, agent_id: str, assigned_by: str) -> bool:
        """티켓 할당"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        
        ticket.assigned_to = agent_id
        ticket.assigned_agent = agent_id
        ticket.updated_at = datetime.now()
        
        # 댓글 추가
        self.add_comment(ticket_id, assigned_by, "system", 
                        f"티켓이 {agent_id}에게 할당되었습니다.", is_internal=True)
        
        # 콜백 실행
        self._notify_ticket_updated(ticket, None)
        
        logger.info(f"티켓 할당: {ticket_id} -> {agent_id}")
        return True
    
    def add_comment(self, ticket_id: str, author_id: str, author_name: str, 
                   content: str, is_internal: bool = False, 
                   attachments: List[str] = None) -> str:
        """댓글 추가"""
        try:
            comment_id = f"comment_{int(time.time() * 1000)}"
            
            comment = TicketComment(
                id=comment_id,
                ticket_id=ticket_id,
                author_id=author_id,
                author_name=author_name,
                author_type="agent" if is_internal else "customer",
                content=content,
                is_internal=is_internal,
                attachments=attachments or []
            )
            
            if ticket_id not in self.comments:
                self.comments[ticket_id] = []
            
            self.comments[ticket_id].append(comment)
            
            # 티켓 업데이트 시간 갱신
            if ticket_id in self.tickets:
                self.tickets[ticket_id].updated_at = datetime.now()
            
            # 콜백 실행
            self._notify_comment_added(comment)
            
            logger.info(f"댓글 추가: {ticket_id} - {comment_id}")
            return comment_id
            
        except Exception as e:
            logger.error(f"댓글 추가 오류: {e}")
            return None
    
    def _notify_ticket_updated(self, ticket: Ticket, old_status: TicketStatus):
        """티켓 업데이트 알림"""
        for callback in self.ticket_callbacks:
            try:
                callback({
                    'type': 'ticket_updated',
                    'ticket': asdict(ticket),
                    'old_status': old_status.value if old_status else None
                })
            except Exception as e:
                logger.error(f"티켓 업데이트 알림 오류: {e}")
    
    def _notify_comment_added(self, comment: TicketComment):
        """댓글 추가 알림"""
        for callback in self.ticket_callbacks:
            try:
                callback({
                    'type': 'comment_added',
                    'comment': asdict(comment)
                })
            except Exception as e:
                logger.error(f"댓글 추가 알림 오류: {e}")
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """티켓 조회"""
        return self.tickets.get(ticket_id)
    
    def get_tickets(self, status: TicketStatus = None, priority: TicketPriority = None,
                   category: TicketCategory = None, assigned_to: str = None,
                   customer_id: str = None, limit: int = 100) -> List[Ticket]:
        """티켓 목록 조회"""
        tickets = list(self.tickets.values())
        
        # 필터링
        if status:
            tickets = [t for t in tickets if t.status == status]
        
        if priority:
            tickets = [t for t in tickets if t.priority == priority]
        
        if category:
            tickets = [t for t in tickets if t.category == category]
        
        if assigned_to:
            tickets = [t for t in tickets if t.assigned_to == assigned_to]
        
        if customer_id:
            tickets = [t for t in tickets if t.customer_id == customer_id]
        
        # 정렬 및 제한
        tickets.sort(key=lambda x: x.created_at, reverse=True)
        return tickets[:limit]
    
    def get_ticket_comments(self, ticket_id: str, include_internal: bool = False) -> List[TicketComment]:
        """티켓 댓글 조회"""
        comments = self.comments.get(ticket_id, [])
        
        if not include_internal:
            comments = [c for c in comments if not c.is_internal]
        
        return sorted(comments, key=lambda x: x.created_at)
    
    def search_tickets(self, query: str, limit: int = 100) -> List[Ticket]:
        """티켓 검색"""
        tickets = []
        query_lower = query.lower()
        
        for ticket in self.tickets.values():
            if (query_lower in ticket.title.lower() or 
                query_lower in ticket.description.lower() or
                query_lower in ticket.customer_name.lower() or
                query_lower in ticket.customer_email.lower()):
                tickets.append(ticket)
        
        return sorted(tickets, key=lambda x: x.created_at, reverse=True)[:limit]
    
    def get_ticket_statistics(self, days: int = 30) -> Dict[str, Any]:
        """티켓 통계 조회"""
        cutoff_time = datetime.now() - timedelta(days=days)
        recent_tickets = [t for t in self.tickets.values() if t.created_at >= cutoff_time]
        
        # 상태별 통계
        status_stats = {}
        for status in TicketStatus:
            status_stats[status.value] = len([t for t in recent_tickets if t.status == status])
        
        # 우선순위별 통계
        priority_stats = {}
        for priority in TicketPriority:
            priority_stats[priority.value] = len([t for t in recent_tickets if t.priority == priority])
        
        # 카테고리별 통계
        category_stats = {}
        for category in TicketCategory:
            category_stats[category.value] = len([t for t in recent_tickets if t.category == category])
        
        # 해결 시간 통계
        resolved_tickets = [t for t in recent_tickets if t.resolved_at]
        resolution_times = []
        for ticket in resolved_tickets:
            resolution_time = (ticket.resolved_at - ticket.created_at).total_seconds() / 3600  # 시간
            resolution_times.append(resolution_time)
        
        avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            'total_tickets': len(recent_tickets),
            'status_stats': status_stats,
            'priority_stats': priority_stats,
            'category_stats': category_stats,
            'avg_resolution_time_hours': avg_resolution_time,
            'resolution_rate': len(resolved_tickets) / len(recent_tickets) * 100 if recent_tickets else 0,
            'time_range': {
                'start': cutoff_time.isoformat(),
                'end': datetime.now().isoformat()
            }
        }
    
    def add_ticket_callback(self, callback: Callable):
        """티켓 콜백 함수 추가"""
        self.ticket_callbacks.append(callback)
    
    def remove_ticket_callback(self, callback: Callable):
        """티켓 콜백 함수 제거"""
        if callback in self.ticket_callbacks:
            self.ticket_callbacks.remove(callback)
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'total_tickets': len(self.tickets),
            'open_tickets': len([t for t in self.tickets.values() if t.status == TicketStatus.OPEN]),
            'in_progress_tickets': len([t for t in self.tickets.values() if t.status == TicketStatus.IN_PROGRESS]),
            'resolved_tickets': len([t for t in self.tickets.values() if t.status == TicketStatus.RESOLVED]),
            'total_comments': sum(len(comments) for comments in self.comments.values()),
            'templates': len(self.templates),
            'auto_assign_enabled': self.auto_assign_enabled
        }

# 전역 인스턴스
support_ticket_service = SupportTicketService()
