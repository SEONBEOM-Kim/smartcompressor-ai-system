#!/usr/bin/env python3
"""
매장 등록 및 승인 시스템
AWS Management Console을 벤치마킹한 매장 관리 시스템
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

class StoreStatus(Enum):
    """매장 상태"""
    PENDING = "pending"           # 승인 대기
    APPROVED = "approved"         # 승인됨
    REJECTED = "rejected"         # 거부됨
    SUSPENDED = "suspended"       # 정지됨
    ACTIVE = "active"             # 활성
    INACTIVE = "inactive"         # 비활성
    MAINTENANCE = "maintenance"   # 유지보수

class ApprovalStatus(Enum):
    """승인 상태"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"

class StoreType(Enum):
    """매장 타입"""
    FRANCHISE = "franchise"       # 프랜차이즈
    CORPORATE = "corporate"       # 직영
    PARTNER = "partner"           # 파트너
    TEST = "test"                 # 테스트

@dataclass
class StoreApplication:
    """매장 신청 클래스"""
    id: str
    store_name: str
    owner_name: str
    owner_email: str
    owner_phone: str
    business_license: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    store_type: StoreType
    expected_devices: int
    application_date: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    approval_notes: Optional[str] = None
    documents: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.documents is None:
            self.documents = []
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Store:
    """매장 클래스"""
    id: str
    store_name: str
    owner_id: str
    owner_name: str
    owner_email: str
    owner_phone: str
    business_license: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    store_type: StoreType
    status: StoreStatus
    created_at: datetime
    activated_at: Optional[datetime] = None
    suspended_at: Optional[datetime] = None
    device_count: int = 0
    max_devices: int = 10
    subscription_plan: str = "basic"
    monthly_fee: float = 0.0
    last_payment: Optional[datetime] = None
    next_payment: Optional[datetime] = None
    settings: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
        if self.metadata is None:
            self.metadata = {}

class StoreApprovalService:
    """매장 승인 서비스"""
    
    def __init__(self):
        self.applications: Dict[str, StoreApplication] = {}
        self.stores: Dict[str, Store] = {}
        self.approval_callbacks: List[Callable] = []
        self.approval_queue: deque = deque()
        self.is_processing = False
        self.processing_thread = None
        
        # 승인 규칙
        self.approval_rules = {
            'min_business_license_length': 10,
            'required_documents': ['business_license', 'identity_verification', 'bank_account'],
            'max_devices_per_store': 50,
            'approval_timeout_hours': 72
        }
        
        # 자동 승인 조건
        self.auto_approval_conditions = {
            'corporate_stores': True,
            'verified_business_license': True,
            'complete_documents': True,
            'no_previous_rejections': True
        }
        
        # 승인 처리 시작
        self._start_approval_processing()
    
    def _start_approval_processing(self):
        """승인 처리 시작"""
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._approval_processing_worker, daemon=True)
        self.processing_thread.start()
        logger.info("매장 승인 처리 서비스 시작")
    
    def _approval_processing_worker(self):
        """승인 처리 워커"""
        while self.is_processing:
            try:
                if self.approval_queue:
                    application_id = self.approval_queue.popleft()
                    self._process_application(application_id)
                
                time.sleep(5)  # 5초마다 체크
                
            except Exception as e:
                logger.error(f"승인 처리 워커 오류: {e}")
                time.sleep(10)
    
    def submit_application(self, application_data: Dict[str, Any]) -> str:
        """매장 신청 제출"""
        try:
            # 신청 ID 생성
            application_id = f"app_{int(time.time() * 1000)}"
            
            # 신청서 생성
            application = StoreApplication(
                id=application_id,
                store_name=application_data['store_name'],
                owner_name=application_data['owner_name'],
                owner_email=application_data['owner_email'],
                owner_phone=application_data['owner_phone'],
                business_license=application_data['business_license'],
                address=application_data['address'],
                city=application_data['city'],
                state=application_data['state'],
                zip_code=application_data['zip_code'],
                country=application_data['country'],
                store_type=StoreType(application_data['store_type']),
                expected_devices=application_data.get('expected_devices', 1),
                application_date=datetime.now(),
                documents=application_data.get('documents', []),
                metadata=application_data.get('metadata', {})
            )
            
            # 유효성 검사
            if not self._validate_application(application):
                return None
            
            # 신청서 저장
            self.applications[application_id] = application
            
            # 자동 승인 검사
            if self._check_auto_approval(application):
                self._auto_approve_application(application_id)
            else:
                # 승인 큐에 추가
                self.approval_queue.append(application_id)
                logger.info(f"매장 신청 제출: {application_id} - {application.store_name}")
            
            return application_id
            
        except Exception as e:
            logger.error(f"매장 신청 제출 오류: {e}")
            return None
    
    def _validate_application(self, application: StoreApplication) -> bool:
        """신청서 유효성 검사"""
        # 필수 필드 검사
        required_fields = ['store_name', 'owner_name', 'owner_email', 'business_license', 'address']
        for field in required_fields:
            if not getattr(application, field):
                logger.error(f"필수 필드 누락: {field}")
                return False
        
        # 사업자등록번호 길이 검사
        if len(application.business_license) < self.approval_rules['min_business_license_length']:
            logger.error("사업자등록번호가 너무 짧습니다")
            return False
        
        # 이메일 형식 검사
        if '@' not in application.owner_email:
            logger.error("유효하지 않은 이메일 형식")
            return False
        
        # 중복 신청 검사
        for existing_app in self.applications.values():
            if (existing_app.owner_email == application.owner_email and 
                existing_app.status == ApprovalStatus.PENDING):
                logger.error("이미 처리 중인 신청이 있습니다")
                return False
        
        return True
    
    def _check_auto_approval(self, application: StoreApplication) -> bool:
        """자동 승인 조건 검사"""
        # 직영 매장은 자동 승인
        if application.store_type == StoreType.CORPORATE:
            return True
        
        # 모든 필수 서류가 있는 경우
        if len(application.documents) >= len(self.approval_rules['required_documents']):
            return True
        
        # 사업자등록번호가 검증된 경우 (실제로는 외부 API 호출)
        if self._verify_business_license(application.business_license):
            return True
        
        return False
    
    def _verify_business_license(self, business_license: str) -> bool:
        """사업자등록번호 검증 (시뮬레이션)"""
        # 실제로는 정부 API를 호출하여 검증
        # 여기서는 간단한 형식 검사만 수행
        return len(business_license) >= 10 and business_license.isdigit()
    
    def _auto_approve_application(self, application_id: str):
        """자동 승인 처리"""
        application = self.applications.get(application_id)
        if not application:
            return
        
        application.status = ApprovalStatus.APPROVED
        application.reviewed_at = datetime.now()
        application.reviewed_by = "system"
        application.approval_notes = "자동 승인됨"
        
        # 매장 생성
        store = self._create_store_from_application(application)
        self.stores[store.id] = store
        
        logger.info(f"매장 자동 승인: {application_id} - {application.store_name}")
        
        # 콜백 실행
        self._notify_approval_completed(application, store)
    
    def _create_store_from_application(self, application: StoreApplication) -> Store:
        """신청서에서 매장 생성"""
        store_id = f"store_{int(time.time() * 1000)}"
        
        return Store(
            id=store_id,
            store_name=application.store_name,
            owner_id=f"owner_{application.id}",
            owner_name=application.owner_name,
            owner_email=application.owner_email,
            owner_phone=application.owner_phone,
            business_license=application.business_license,
            address=application.address,
            city=application.city,
            state=application.state,
            zip_code=application.zip_code,
            country=application.country,
            store_type=application.store_type,
            status=StoreStatus.APPROVED,
            created_at=datetime.now(),
            activated_at=datetime.now(),
            max_devices=application.expected_devices,
            subscription_plan="basic",
            monthly_fee=self._calculate_monthly_fee(application.store_type, application.expected_devices),
            next_payment=datetime.now() + timedelta(days=30)
        )
    
    def _calculate_monthly_fee(self, store_type: StoreType, device_count: int) -> float:
        """월 사용료 계산"""
        base_fee = 50000  # 기본 5만원
        
        if store_type == StoreType.CORPORATE:
            return base_fee * 0.8  # 20% 할인
        elif store_type == StoreType.FRANCHISE:
            return base_fee * 1.2  # 20% 추가
        elif store_type == StoreType.PARTNER:
            return base_fee * 0.9  # 10% 할인
        else:
            return base_fee
    
    def _process_application(self, application_id: str):
        """신청서 처리"""
        application = self.applications.get(application_id)
        if not application:
            return
        
        # 수동 검토 필요
        application.status = ApprovalStatus.UNDER_REVIEW
        logger.info(f"매장 신청 검토 시작: {application_id} - {application.store_name}")
        
        # 실제로는 관리자가 검토하지만, 여기서는 시뮬레이션
        time.sleep(2)
        
        # 승인/거부 결정 (시뮬레이션)
        if self._should_approve_application(application):
            self._approve_application(application_id, "admin")
        else:
            self._reject_application(application_id, "admin", "서류 미비")
    
    def _should_approve_application(self, application: StoreApplication) -> bool:
        """신청서 승인 여부 결정 (시뮬레이션)"""
        # 90% 확률로 승인
        import random
        return random.random() < 0.9
    
    def approve_application(self, application_id: str, reviewer_id: str, notes: str = None) -> bool:
        """신청서 승인"""
        return self._approve_application(application_id, reviewer_id, notes)
    
    def _approve_application(self, application_id: str, reviewer_id: str, notes: str = None) -> bool:
        """신청서 승인 처리"""
        application = self.applications.get(application_id)
        if not application:
            return False
        
        application.status = ApprovalStatus.APPROVED
        application.reviewed_at = datetime.now()
        application.reviewed_by = reviewer_id
        application.approval_notes = notes or "승인됨"
        
        # 매장 생성
        store = self._create_store_from_application(application)
        self.stores[store.id] = store
        
        logger.info(f"매장 승인: {application_id} - {application.store_name}")
        
        # 콜백 실행
        self._notify_approval_completed(application, store)
        
        return True
    
    def reject_application(self, application_id: str, reviewer_id: str, reason: str) -> bool:
        """신청서 거부"""
        return self._reject_application(application_id, reviewer_id, reason)
    
    def _reject_application(self, application_id: str, reviewer_id: str, reason: str) -> bool:
        """신청서 거부 처리"""
        application = self.applications.get(application_id)
        if not application:
            return False
        
        application.status = ApprovalStatus.REJECTED
        application.reviewed_at = datetime.now()
        application.reviewed_by = reviewer_id
        application.rejection_reason = reason
        
        logger.info(f"매장 거부: {application_id} - {application.store_name} - {reason}")
        
        # 콜백 실행
        self._notify_approval_completed(application, None)
        
        return True
    
    def _notify_approval_completed(self, application: StoreApplication, store: Optional[Store]):
        """승인 완료 알림"""
        for callback in self.approval_callbacks:
            try:
                callback({
                    'type': 'approval_completed',
                    'application': asdict(application),
                    'store': asdict(store) if store else None
                })
            except Exception as e:
                logger.error(f"승인 완료 알림 오류: {e}")
    
    def get_application(self, application_id: str) -> Optional[StoreApplication]:
        """신청서 조회"""
        return self.applications.get(application_id)
    
    def get_applications(self, status: ApprovalStatus = None, limit: int = 100) -> List[StoreApplication]:
        """신청서 목록 조회"""
        applications = list(self.applications.values())
        
        if status:
            applications = [app for app in applications if app.status == status]
        
        # 최신순 정렬
        applications.sort(key=lambda x: x.application_date, reverse=True)
        return applications[:limit]
    
    def get_store(self, store_id: str) -> Optional[Store]:
        """매장 조회"""
        return self.stores.get(store_id)
    
    def get_stores(self, status: StoreStatus = None, limit: int = 100) -> List[Store]:
        """매장 목록 조회"""
        stores = list(self.stores.values())
        
        if status:
            stores = [store for store in stores if store.status == status]
        
        # 최신순 정렬
        stores.sort(key=lambda x: x.created_at, reverse=True)
        return stores[:limit]
    
    def update_store_status(self, store_id: str, status: StoreStatus, reason: str = None) -> bool:
        """매장 상태 업데이트"""
        store = self.stores.get(store_id)
        if not store:
            return False
        
        old_status = store.status
        store.status = status
        
        if status == StoreStatus.ACTIVE:
            store.activated_at = datetime.now()
        elif status == StoreStatus.SUSPENDED:
            store.suspended_at = datetime.now()
        
        logger.info(f"매장 상태 변경: {store_id} - {old_status.value} -> {status.value}")
        
        # 콜백 실행
        self._notify_store_status_changed(store, old_status, reason)
        
        return True
    
    def _notify_store_status_changed(self, store: Store, old_status: StoreStatus, reason: str = None):
        """매장 상태 변경 알림"""
        for callback in self.approval_callbacks:
            try:
                callback({
                    'type': 'store_status_changed',
                    'store': asdict(store),
                    'old_status': old_status.value,
                    'reason': reason
                })
            except Exception as e:
                logger.error(f"매장 상태 변경 알림 오류: {e}")
    
    def add_approval_callback(self, callback: Callable):
        """승인 콜백 함수 추가"""
        self.approval_callbacks.append(callback)
    
    def remove_approval_callback(self, callback: Callable):
        """승인 콜백 함수 제거"""
        if callback in self.approval_callbacks:
            self.approval_callbacks.remove(callback)
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'is_processing': self.is_processing,
            'total_applications': len(self.applications),
            'pending_applications': len([app for app in self.applications.values() if app.status == ApprovalStatus.PENDING]),
            'approved_applications': len([app for app in self.applications.values() if app.status == ApprovalStatus.APPROVED]),
            'rejected_applications': len([app for app in self.applications.values() if app.status == ApprovalStatus.REJECTED]),
            'total_stores': len(self.stores),
            'active_stores': len([store for store in self.stores.values() if store.status == StoreStatus.ACTIVE]),
            'suspended_stores': len([store for store in self.stores.values() if store.status == StoreStatus.SUSPENDED])
        }
    
    def stop_service(self):
        """서비스 중지"""
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("매장 승인 서비스 중지")

# 전역 인스턴스
store_approval_service = StoreApprovalService()
