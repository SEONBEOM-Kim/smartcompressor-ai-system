#!/usr/bin/env python3
"""
SMS 알림 시스템
Twilio와 네이버 클라우드 플랫폼 지원
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import base64
import urllib.parse

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMSProvider(Enum):
    """SMS 제공업체"""
    TWILIO = "twilio"
    NAVER_CLOUD = "naver_cloud"
    AWS_SNS = "aws_sns"

class SMSStatus(Enum):
    """SMS 상태"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"

@dataclass
class SMSMessage:
    """SMS 메시지 데이터 클래스"""
    to: str
    content: str
    from_number: Optional[str] = None
    provider: SMSProvider = SMSProvider.TWILIO
    priority: str = "normal"
    scheduled_time: Optional[datetime] = None
    template_id: Optional[str] = None
    variables: Dict = None

@dataclass
class SMSResult:
    """SMS 전송 결과"""
    message_id: str
    status: SMSStatus
    provider: SMSProvider
    sent_at: datetime
    cost: float = 0.0
    error_message: Optional[str] = None

class TwilioSMSService:
    """Twilio SMS 서비스"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}"
        
        logger.info("Twilio SMS 서비스 초기화 완료")
    
    def send_sms(self, message: SMSMessage) -> SMSResult:
        """SMS 전송"""
        try:
            url = f"{self.base_url}/Messages.json"
            
            data = {
                'From': message.from_number or self.from_number,
                'To': message.to,
                'Body': message.content
            }
            
            response = requests.post(
                url,
                data=data,
                auth=(self.account_sid, self.auth_token)
            )
            
            if response.status_code == 201:
                result_data = response.json()
                return SMSResult(
                    message_id=result_data['sid'],
                    status=SMSStatus.SENT,
                    provider=SMSProvider.TWILIO,
                    sent_at=datetime.now(),
                    cost=float(result_data.get('price', 0))
                )
            else:
                return SMSResult(
                    message_id="",
                    status=SMSStatus.FAILED,
                    provider=SMSProvider.TWILIO,
                    sent_at=datetime.now(),
                    error_message=f"Twilio API 오류: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            logger.error(f"Twilio SMS 전송 오류: {e}")
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=SMSProvider.TWILIO,
                sent_at=datetime.now(),
                error_message=str(e)
            )
    
    def get_message_status(self, message_id: str) -> SMSResult:
        """메시지 상태 조회"""
        try:
            url = f"{self.base_url}/Messages/{message_id}.json"
            
            response = requests.get(
                url,
                auth=(self.account_sid, self.auth_token)
            )
            
            if response.status_code == 200:
                data = response.json()
                status_map = {
                    'queued': SMSStatus.PENDING,
                    'sending': SMSStatus.PENDING,
                    'sent': SMSStatus.SENT,
                    'delivered': SMSStatus.DELIVERED,
                    'failed': SMSStatus.FAILED,
                    'undelivered': SMSStatus.FAILED
                }
                
                return SMSResult(
                    message_id=message_id,
                    status=status_map.get(data['status'], SMSStatus.PENDING),
                    provider=SMSProvider.TWILIO,
                    sent_at=datetime.fromisoformat(data['date_sent'].replace('Z', '+00:00')),
                    cost=float(data.get('price', 0))
                )
            else:
                return SMSResult(
                    message_id=message_id,
                    status=SMSStatus.FAILED,
                    provider=SMSProvider.TWILIO,
                    sent_at=datetime.now(),
                    error_message=f"상태 조회 실패: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"Twilio 메시지 상태 조회 오류: {e}")
            return SMSResult(
                message_id=message_id,
                status=SMSStatus.FAILED,
                provider=SMSProvider.TWILIO,
                sent_at=datetime.now(),
                error_message=str(e)
            )

class NaverCloudSMSService:
    """네이버 클라우드 플랫폼 SMS 서비스"""
    
    def __init__(self, access_key: str, secret_key: str, service_id: str):
        self.access_key = access_key
        self.secret_key = secret_key
        self.service_id = service_id
        self.base_url = "https://sens.apigw.ntruss.com"
        
        logger.info("네이버 클라우드 SMS 서비스 초기화 완료")
    
    def _make_signature(self, method: str, uri: str, timestamp: str) -> str:
        """API 서명 생성"""
        message = f"{method} {uri}\n{timestamp}\n{self.access_key}"
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        return signature
    
    def send_sms(self, message: SMSMessage) -> SMSResult:
        """SMS 전송"""
        try:
            timestamp = str(int(datetime.now().timestamp() * 1000))
            uri = f"/sms/v2/services/{self.service_id}/messages"
            url = f"{self.base_url}{uri}"
            
            signature = self._make_signature("POST", uri, timestamp)
            
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'x-ncp-apigw-timestamp': timestamp,
                'x-ncp-iam-access-key': self.access_key,
                'x-ncp-apigw-signature-v2': signature
            }
            
            data = {
                'type': 'SMS',
                'from': message.from_number or '01012345678',
                'content': message.content,
                'messages': [{'to': message.to}]
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 202:
                result_data = response.json()
                return SMSResult(
                    message_id=result_data['requestId'],
                    status=SMSStatus.SENT,
                    provider=SMSProvider.NAVER_CLOUD,
                    sent_at=datetime.now()
                )
            else:
                return SMSResult(
                    message_id="",
                    status=SMSStatus.FAILED,
                    provider=SMSProvider.NAVER_CLOUD,
                    sent_at=datetime.now(),
                    error_message=f"네이버 클라우드 API 오류: {response.status_code} - {response.text}"
                )
                
        except Exception as e:
            logger.error(f"네이버 클라우드 SMS 전송 오류: {e}")
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=SMSProvider.NAVER_CLOUD,
                sent_at=datetime.now(),
                error_message=str(e)
            )
    
    def get_message_status(self, message_id: str) -> SMSResult:
        """메시지 상태 조회"""
        try:
            timestamp = str(int(datetime.now().timestamp() * 1000))
            uri = f"/sms/v2/services/{self.service_id}/messages/{message_id}"
            url = f"{self.base_url}{uri}"
            
            signature = self._make_signature("GET", uri, timestamp)
            
            headers = {
                'x-ncp-apigw-timestamp': timestamp,
                'x-ncp-iam-access-key': self.access_key,
                'x-ncp-apigw-signature-v2': signature
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                status_map = {
                    'READY': SMSStatus.PENDING,
                    'SENDING': SMSStatus.PENDING,
                    'COMPLETED': SMSStatus.DELIVERED,
                    'FAILED': SMSStatus.FAILED
                }
                
                return SMSResult(
                    message_id=message_id,
                    status=status_map.get(data['status'], SMSStatus.PENDING),
                    provider=SMSProvider.NAVER_CLOUD,
                    sent_at=datetime.fromisoformat(data['requestTime'].replace('Z', '+00:00'))
                )
            else:
                return SMSResult(
                    message_id=message_id,
                    status=SMSStatus.FAILED,
                    provider=SMSProvider.NAVER_CLOUD,
                    sent_at=datetime.now(),
                    error_message=f"상태 조회 실패: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"네이버 클라우드 메시지 상태 조회 오류: {e}")
            return SMSResult(
                message_id=message_id,
                status=SMSStatus.FAILED,
                provider=SMSProvider.NAVER_CLOUD,
                sent_at=datetime.now(),
                error_message=str(e)
            )

class SMSNotificationService:
    """통합 SMS 알림 서비스"""
    
    def __init__(self):
        self.providers = {}
        self.message_history = []
        self.templates = {}
        self.rate_limits = {
            SMSProvider.TWILIO: {'limit': 100, 'window': 60},  # 1분에 100개
            SMSProvider.NAVER_CLOUD: {'limit': 1000, 'window': 60}  # 1분에 1000개
        }
        
        logger.info("SMS 알림 서비스 초기화 완료")
    
    def register_provider(self, provider: SMSProvider, service_instance) -> bool:
        """SMS 제공업체 등록"""
        try:
            self.providers[provider] = service_instance
            logger.info(f"SMS 제공업체 등록 완료: {provider.value}")
            return True
        except Exception as e:
            logger.error(f"SMS 제공업체 등록 오류: {e}")
            return False
    
    def send_sms(self, message: SMSMessage) -> SMSResult:
        """SMS 전송"""
        try:
            # 제공업체 확인
            provider_service = self.providers.get(message.provider)
            if not provider_service:
                return SMSResult(
                    message_id="",
                    status=SMSStatus.FAILED,
                    provider=message.provider,
                    sent_at=datetime.now(),
                    error_message=f"지원하지 않는 제공업체: {message.provider.value}"
                )
            
            # Rate limiting 확인
            if not self._check_rate_limit(message.provider):
                return SMSResult(
                    message_id="",
                    status=SMSStatus.FAILED,
                    provider=message.provider,
                    sent_at=datetime.now(),
                    error_message="Rate limit 초과"
                )
            
            # SMS 전송
            result = provider_service.send_sms(message)
            
            # 히스토리에 저장
            self.message_history.append({
                'message_id': result.message_id,
                'to': message.to,
                'content': message.content,
                'provider': message.provider.value,
                'status': result.status.value,
                'sent_at': result.sent_at.isoformat(),
                'cost': result.cost,
                'error_message': result.error_message
            })
            
            logger.info(f"SMS 전송 완료: {message.to} - {result.status.value}")
            return result
            
        except Exception as e:
            logger.error(f"SMS 전송 오류: {e}")
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=message.provider,
                sent_at=datetime.now(),
                error_message=str(e)
            )
    
    def send_bulk_sms(self, messages: List[SMSMessage]) -> List[SMSResult]:
        """대량 SMS 전송"""
        try:
            results = []
            
            for message in messages:
                result = self.send_sms(message)
                results.append(result)
                
                # Rate limiting을 위한 지연
                import time
                time.sleep(0.1)
            
            logger.info(f"대량 SMS 전송 완료: {len(messages)}개")
            return results
            
        except Exception as e:
            logger.error(f"대량 SMS 전송 오류: {e}")
            return []
    
    def send_template_sms(self, to: str, template_id: str, variables: Dict = None, provider: SMSProvider = SMSProvider.TWILIO) -> SMSResult:
        """템플릿 SMS 전송"""
        try:
            template = self.templates.get(template_id)
            if not template:
                return SMSResult(
                    message_id="",
                    status=SMSStatus.FAILED,
                    provider=provider,
                    sent_at=datetime.now(),
                    error_message=f"템플릿을 찾을 수 없습니다: {template_id}"
                )
            
            # 변수 치환
            content = template['content']
            if variables:
                for key, value in variables.items():
                    content = content.replace(f'{{{key}}}', str(value))
            
            # SMS 메시지 생성
            sms_message = SMSMessage(
                to=to,
                content=content,
                provider=provider,
                template_id=template_id,
                variables=variables
            )
            
            return self.send_sms(sms_message)
            
        except Exception as e:
            logger.error(f"템플릿 SMS 전송 오류: {e}")
            return SMSResult(
                message_id="",
                status=SMSStatus.FAILED,
                provider=provider,
                sent_at=datetime.now(),
                error_message=str(e)
            )
    
    def create_template(self, template_id: str, content: str, variables: List[str] = None) -> bool:
        """SMS 템플릿 생성"""
        try:
            self.templates[template_id] = {
                'content': content,
                'variables': variables or [],
                'created_at': datetime.now(),
                'usage_count': 0
            }
            
            logger.info(f"SMS 템플릿 생성 완료: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"SMS 템플릿 생성 오류: {e}")
            return False
    
    def get_message_status(self, message_id: str, provider: SMSProvider) -> SMSResult:
        """메시지 상태 조회"""
        try:
            provider_service = self.providers.get(provider)
            if not provider_service:
                return SMSResult(
                    message_id=message_id,
                    status=SMSStatus.FAILED,
                    provider=provider,
                    sent_at=datetime.now(),
                    error_message=f"지원하지 않는 제공업체: {provider.value}"
                )
            
            return provider_service.get_message_status(message_id)
            
        except Exception as e:
            logger.error(f"메시지 상태 조회 오류: {e}")
            return SMSResult(
                message_id=message_id,
                status=SMSStatus.FAILED,
                provider=provider,
                sent_at=datetime.now(),
                error_message=str(e)
            )
    
    def get_message_history(self, limit: int = 100, status: SMSStatus = None) -> List[Dict]:
        """메시지 히스토리 조회"""
        try:
            history = self.message_history.copy()
            
            if status:
                history = [msg for msg in history if msg['status'] == status.value]
            
            # 최신순으로 정렬
            history.sort(key=lambda x: x['sent_at'], reverse=True)
            
            return history[:limit]
            
        except Exception as e:
            logger.error(f"메시지 히스토리 조회 오류: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """SMS 통계 조회"""
        try:
            total_messages = len(self.message_history)
            
            status_counts = {}
            provider_counts = {}
            total_cost = 0.0
            
            for msg in self.message_history:
                # 상태별 카운트
                status = msg['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                
                # 제공업체별 카운트
                provider = msg['provider']
                provider_counts[provider] = provider_counts.get(provider, 0) + 1
                
                # 총 비용
                total_cost += msg.get('cost', 0.0)
            
            return {
                'total_messages': total_messages,
                'status_counts': status_counts,
                'provider_counts': provider_counts,
                'total_cost': total_cost,
                'success_rate': (status_counts.get('sent', 0) + status_counts.get('delivered', 0)) / max(total_messages, 1) * 100
            }
            
        except Exception as e:
            logger.error(f"SMS 통계 조회 오류: {e}")
            return {}
    
    def _check_rate_limit(self, provider: SMSProvider) -> bool:
        """Rate limiting 확인"""
        try:
            limit_info = self.rate_limits.get(provider)
            if not limit_info:
                return True
            
            # 최근 1분간의 메시지 수 확인
            now = datetime.now()
            recent_messages = [
                msg for msg in self.message_history
                if (now - datetime.fromisoformat(msg['sent_at'])).total_seconds() < limit_info['window']
                and msg['provider'] == provider.value
            ]
            
            return len(recent_messages) < limit_info['limit']
            
        except Exception as e:
            logger.error(f"Rate limiting 확인 오류: {e}")
            return True

# 전역 인스턴스
sms_notification_service = SMSNotificationService()

# 기본 제공업체 등록 (실제 키는 환경변수에서 가져와야 함)
# twilio_service = TwilioSMSService(
#     account_sid="your_twilio_account_sid",
#     auth_token="your_twilio_auth_token",
#     from_number="+1234567890"
# )
# sms_notification_service.register_provider(SMSProvider.TWILIO, twilio_service)

# naver_service = NaverCloudSMSService(
#     access_key="your_naver_access_key",
#     secret_key="your_naver_secret_key",
#     service_id="your_service_id"
# )
# sms_notification_service.register_provider(SMSProvider.NAVER_CLOUD, naver_service)
