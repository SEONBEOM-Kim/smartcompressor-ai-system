"""
개인정보보호법 준수 서비스 - Stripe & AWS 보안 시스템 벤치마킹
개인정보 처리방침, 동의 관리, 데이터 주체 권리 보장
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import hashlib

logger = logging.getLogger(__name__)

class PersonalDataType(Enum):
    """개인정보 유형"""
    IDENTIFIER = "identifier"  # 식별정보
    SENSITIVE = "sensitive"    # 민감정보
    FINANCIAL = "financial"    # 금융정보
    HEALTH = "health"         # 건강정보
    LOCATION = "location"     # 위치정보
    BEHAVIOR = "behavior"     # 행태정보

class ProcessingPurpose(Enum):
    """처리목적"""
    SERVICE_PROVISION = "service_provision"  # 서비스 제공
    PAYMENT_PROCESSING = "payment_processing"  # 결제 처리
    CUSTOMER_SUPPORT = "customer_support"    # 고객 지원
    MARKETING = "marketing"                  # 마케팅
    ANALYTICS = "analytics"                  # 분석
    LEGAL_COMPLIANCE = "legal_compliance"    # 법적 준수

class ConsentStatus(Enum):
    """동의 상태"""
    GRANTED = "granted"        # 동의
    DENIED = "denied"          # 거부
    WITHDRAWN = "withdrawn"    # 철회
    EXPIRED = "expired"        # 만료

@dataclass
class PersonalData:
    """개인정보"""
    data_id: str
    user_id: str
    data_type: PersonalDataType
    data_value: str
    processing_purpose: ProcessingPurpose
    collected_at: datetime
    retention_period: int  # 보유기간 (일)
    is_encrypted: bool = True
    consent_id: Optional[str] = None

@dataclass
class ConsentRecord:
    """동의 기록"""
    consent_id: str
    user_id: str
    purpose: ProcessingPurpose
    data_types: List[PersonalDataType]
    status: ConsentStatus
    granted_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    ip_address: str = ""
    user_agent: str = ""

@dataclass
class DataSubjectRequest:
    """데이터 주체 요청"""
    request_id: str
    user_id: str
    request_type: str  # access, rectification, erasure, portability, restriction
    description: str
    status: str  # pending, processing, completed, rejected
    created_at: datetime
    completed_at: Optional[datetime] = None
    response_data: Optional[Dict] = None

class PrivacyService:
    """
    개인정보보호법 준수를 위한 개인정보 관리 서비스
    """
    
    def __init__(self):
        # 개인정보 저장소 (실제 환경에서는 암호화된 DB 사용)
        self.personal_data: Dict[str, PersonalData] = {}
        self.consent_records: Dict[str, ConsentRecord] = {}
        self.data_subject_requests: Dict[str, DataSubjectRequest] = {}
        
        # 개인정보 처리방침
        self.privacy_policy = self._initialize_privacy_policy()
        
        # 데이터 보유 정책
        self.retention_policies = {
            PersonalDataType.IDENTIFIER: 365,  # 1년
            PersonalDataType.SENSITIVE: 90,    # 3개월
            PersonalDataType.FINANCIAL: 1095,  # 3년
            PersonalDataType.HEALTH: 30,       # 1개월
            PersonalDataType.LOCATION: 30,     # 1개월
            PersonalDataType.BEHAVIOR: 90      # 3개월
        }
        
        logger.info("PrivacyService 초기화 완료")

    def _initialize_privacy_policy(self) -> Dict:
        """개인정보 처리방침 초기화"""
        return {
            "version": "1.0",
            "effective_date": "2024-01-01",
            "company_name": "Smart Compressor AI",
            "contact_info": {
                "privacy_officer": "privacy@smartcompressor-ai.com",
                "phone": "02-1234-5678",
                "address": "서울시 강남구 테헤란로 123"
            },
            "data_collection": {
                "purposes": [
                    "서비스 제공 및 운영",
                    "결제 처리",
                    "고객 지원",
                    "서비스 개선 및 분석"
                ],
                "data_types": [
                    "이름, 이메일, 전화번호",
                    "결제 정보",
                    "서비스 이용 기록",
                    "기기 정보 및 로그"
                ]
            },
            "data_processing": {
                "legal_basis": "동의",
                "retention_periods": self.retention_policies,
                "third_party_sharing": False
            },
            "data_subject_rights": [
                "개인정보 열람권",
                "개인정보 정정·삭제권",
                "개인정보 처리정지권",
                "개인정보 이전권"
            ]
        }

    def collect_personal_data(self, user_id: str, data_type: PersonalDataType, 
                            data_value: str, purpose: ProcessingPurpose,
                            consent_id: str = None) -> str:
        """개인정보 수집"""
        # 동의 확인
        if consent_id and not self._verify_consent(consent_id, purpose, data_type):
            raise ValueError("필요한 동의가 없습니다.")
        
        data_id = self._generate_data_id()
        
        personal_data = PersonalData(
            data_id=data_id,
            user_id=user_id,
            data_type=data_type,
            data_value=data_value,
            processing_purpose=purpose,
            collected_at=datetime.now(),
            retention_period=self.retention_policies[data_type],
            consent_id=consent_id
        )
        
        self.personal_data[data_id] = personal_data
        
        logger.info(f"개인정보 수집 완료: {data_id} (사용자: {user_id}, 유형: {data_type.value})")
        return data_id

    def grant_consent(self, user_id: str, purpose: ProcessingPurpose, 
                     data_types: List[PersonalDataType], 
                     ip_address: str = "", user_agent: str = "",
                     expires_in_days: int = 365) -> str:
        """동의 제공"""
        consent_id = self._generate_consent_id()
        
        consent = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            purpose=purpose,
            data_types=data_types,
            status=ConsentStatus.GRANTED,
            granted_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=expires_in_days),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.consent_records[consent_id] = consent
        
        logger.info(f"동의 제공 완료: {consent_id} (사용자: {user_id}, 목적: {purpose.value})")
        return consent_id

    def withdraw_consent(self, consent_id: str) -> bool:
        """동의 철회"""
        if consent_id not in self.consent_records:
            return False
        
        consent = self.consent_records[consent_id]
        consent.status = ConsentStatus.WITHDRAWN
        consent.withdrawn_at = datetime.now()
        
        # 관련 개인정보 처리 중지
        self._stop_processing_for_consent(consent_id)
        
        logger.info(f"동의 철회 완료: {consent_id}")
        return True

    def _verify_consent(self, consent_id: str, purpose: ProcessingPurpose, 
                       data_type: PersonalDataType) -> bool:
        """동의 확인"""
        if consent_id not in self.consent_records:
            return False
        
        consent = self.consent_records[consent_id]
        
        # 동의 상태 확인
        if consent.status != ConsentStatus.GRANTED:
            return False
        
        # 만료 확인
        if consent.expires_at and datetime.now() > consent.expires_at:
            consent.status = ConsentStatus.EXPIRED
            return False
        
        # 목적 및 데이터 유형 확인
        return (consent.purpose == purpose and 
                data_type in consent.data_types)

    def _stop_processing_for_consent(self, consent_id: str):
        """동의 철회에 따른 처리 중지"""
        # 해당 동의와 관련된 개인정보 처리 중지
        for data_id, data in self.personal_data.items():
            if data.consent_id == consent_id:
                # 처리 중지 로직 (실제 환경에서는 처리 큐에서 제거)
                logger.info(f"개인정보 {data_id} 처리 중지")

    def request_data_access(self, user_id: str, description: str = "") -> str:
        """개인정보 열람 요청"""
        request_id = self._generate_request_id()
        
        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            request_type="access",
            description=description,
            status="pending",
            created_at=datetime.now()
        )
        
        self.data_subject_requests[request_id] = request
        
        logger.info(f"개인정보 열람 요청: {request_id} (사용자: {user_id})")
        return request_id

    def request_data_rectification(self, user_id: str, data_id: str, 
                                  new_value: str, description: str = "") -> str:
        """개인정보 정정 요청"""
        if data_id not in self.personal_data:
            raise ValueError("개인정보를 찾을 수 없습니다.")
        
        if self.personal_data[data_id].user_id != user_id:
            raise ValueError("본인의 개인정보가 아닙니다.")
        
        request_id = self._generate_request_id()
        
        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            request_type="rectification",
            description=f"{description} (데이터 ID: {data_id}, 새 값: {new_value})",
            status="pending",
            created_at=datetime.now()
        )
        
        self.data_subject_requests[request_id] = request
        
        logger.info(f"개인정보 정정 요청: {request_id} (사용자: {user_id}, 데이터: {data_id})")
        return request_id

    def request_data_erasure(self, user_id: str, data_ids: List[str], 
                            description: str = "") -> str:
        """개인정보 삭제 요청"""
        # 데이터 소유권 확인
        for data_id in data_ids:
            if data_id not in self.personal_data:
                raise ValueError(f"개인정보 {data_id}를 찾을 수 없습니다.")
            if self.personal_data[data_id].user_id != user_id:
                raise ValueError(f"개인정보 {data_id}는 본인의 것이 아닙니다.")
        
        request_id = self._generate_request_id()
        
        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            request_type="erasure",
            description=f"{description} (데이터 IDs: {', '.join(data_ids)})",
            status="pending",
            created_at=datetime.now()
        )
        
        self.data_subject_requests[request_id] = request
        
        logger.info(f"개인정보 삭제 요청: {request_id} (사용자: {user_id}, 데이터: {data_ids})")
        return request_id

    def request_data_portability(self, user_id: str, format: str = "json") -> str:
        """개인정보 이전 요청"""
        request_id = self._generate_request_id()
        
        request = DataSubjectRequest(
            request_id=request_id,
            user_id=user_id,
            request_type="portability",
            description=f"개인정보 이전 요청 (형식: {format})",
            status="pending",
            created_at=datetime.now()
        )
        
        self.data_subject_requests[request_id] = request
        
        logger.info(f"개인정보 이전 요청: {request_id} (사용자: {user_id})")
        return request_id

    def process_data_subject_request(self, request_id: str, 
                                   admin_user_id: str) -> Dict:
        """데이터 주체 요청 처리"""
        if request_id not in self.data_subject_requests:
            raise ValueError("요청을 찾을 수 없습니다.")
        
        request = self.data_subject_requests[request_id]
        request.status = "processing"
        
        try:
            if request.request_type == "access":
                result = self._process_access_request(request)
            elif request.request_type == "rectification":
                result = self._process_rectification_request(request)
            elif request.request_type == "erasure":
                result = self._process_erasure_request(request)
            elif request.request_type == "portability":
                result = self._process_portability_request(request)
            else:
                raise ValueError("지원하지 않는 요청 유형입니다.")
            
            request.status = "completed"
            request.completed_at = datetime.now()
            request.response_data = result
            
            logger.info(f"데이터 주체 요청 처리 완료: {request_id}")
            return result
            
        except Exception as e:
            request.status = "rejected"
            request.response_data = {"error": str(e)}
            logger.error(f"데이터 주체 요청 처리 실패: {request_id} - {e}")
            raise

    def _process_access_request(self, request: DataSubjectRequest) -> Dict:
        """열람 요청 처리"""
        user_data = [data for data in self.personal_data.values() 
                    if data.user_id == request.user_id]
        
        return {
            "user_id": request.user_id,
            "data_count": len(user_data),
            "data": [
                {
                    "data_id": data.data_id,
                    "data_type": data.data_type.value,
                    "processing_purpose": data.processing_purpose.value,
                    "collected_at": data.collected_at.isoformat(),
                    "retention_period": data.retention_period
                }
                for data in user_data
            ]
        }

    def _process_rectification_request(self, request: DataSubjectRequest) -> Dict:
        """정정 요청 처리"""
        # 요청 설명에서 데이터 ID와 새 값 추출
        description = request.description
        # 실제 구현에서는 더 정교한 파싱 필요
        
        return {
            "message": "개인정보 정정 요청이 접수되었습니다. 검토 후 처리됩니다.",
            "request_id": request.request_id
        }

    def _process_erasure_request(self, request: DataSubjectRequest) -> Dict:
        """삭제 요청 처리"""
        # 요청 설명에서 데이터 IDs 추출
        description = request.description
        # 실제 구현에서는 더 정교한 파싱 필요
        
        return {
            "message": "개인정보 삭제 요청이 접수되었습니다. 검토 후 처리됩니다.",
            "request_id": request.request_id
        }

    def _process_portability_request(self, request: DataSubjectRequest) -> Dict:
        """이전 요청 처리"""
        user_data = [data for data in self.personal_data.values() 
                    if data.user_id == request.user_id]
        
        # JSON 형식으로 데이터 반환
        portable_data = {
            "user_id": request.user_id,
            "exported_at": datetime.now().isoformat(),
            "data": [
                {
                    "data_type": data.data_type.value,
                    "data_value": data.data_value,
                    "collected_at": data.collected_at.isoformat()
                }
                for data in user_data
            ]
        }
        
        return portable_data

    def get_privacy_policy(self) -> Dict:
        """개인정보 처리방침 조회"""
        return self.privacy_policy

    def get_user_consents(self, user_id: str) -> List[Dict]:
        """사용자 동의 목록 조회"""
        user_consents = [consent for consent in self.consent_records.values() 
                        if consent.user_id == user_id]
        
        return [
            {
                "consent_id": consent.consent_id,
                "purpose": consent.purpose.value,
                "data_types": [dt.value for dt in consent.data_types],
                "status": consent.status.value,
                "granted_at": consent.granted_at.isoformat() if consent.granted_at else None,
                "expires_at": consent.expires_at.isoformat() if consent.expires_at else None
            }
            for consent in user_consents
        ]

    def get_user_personal_data(self, user_id: str) -> List[Dict]:
        """사용자 개인정보 목록 조회"""
        user_data = [data for data in self.personal_data.values() 
                    if data.user_id == user_id]
        
        return [
            {
                "data_id": data.data_id,
                "data_type": data.data_type.value,
                "processing_purpose": data.processing_purpose.value,
                "collected_at": data.collected_at.isoformat(),
                "retention_period": data.retention_period,
                "is_encrypted": data.is_encrypted
            }
            for data in user_data
        ]

    def cleanup_expired_data(self) -> int:
        """만료된 개인정보 정리"""
        now = datetime.now()
        expired_data = []
        
        for data_id, data in self.personal_data.items():
            if now - data.collected_at > timedelta(days=data.retention_period):
                expired_data.append(data_id)
        
        for data_id in expired_data:
            del self.personal_data[data_id]
        
        logger.info(f"만료된 개인정보 {len(expired_data)}개 정리 완료")
        return len(expired_data)

    def _generate_data_id(self) -> str:
        """데이터 ID 생성"""
        return f"data_{hashlib.md5(f'{datetime.now()}{secrets.token_hex(8)}'.encode()).hexdigest()[:16]}"

    def _generate_consent_id(self) -> str:
        """동의 ID 생성"""
        return f"consent_{hashlib.md5(f'{datetime.now()}{secrets.token_hex(8)}'.encode()).hexdigest()[:16]}"

    def _generate_request_id(self) -> str:
        """요청 ID 생성"""
        return f"req_{hashlib.md5(f'{datetime.now()}{secrets.token_hex(8)}'.encode()).hexdigest()[:16]}"

# 싱글톤 인스턴스
privacy_service = PrivacyService()
