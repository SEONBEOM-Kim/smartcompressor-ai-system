#!/usr/bin/env python3
"""
통합 결제 서비스
다양한 결제 시스템을 지원하는 확장 가능한 결제 서비스
"""

import os
import time
import hashlib
import json
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentProvider(ABC):
    """결제 제공자 추상 클래스"""
    
    @abstractmethod
    def create_payment(self, amount: int, order_id: str, user_info: Dict) -> Dict:
        """결제 생성"""
        pass
    
    @abstractmethod
    def verify_payment(self, payment_id: str) -> Dict:
        """결제 검증"""
        pass
    
    @abstractmethod
    def cancel_payment(self, payment_id: str) -> Dict:
        """결제 취소"""
        pass

class TossPaymentsProvider(PaymentProvider):
    """토스페이먼츠 결제 제공자"""
    
    def __init__(self, secret_key: str, client_key: str):
        self.secret_key = secret_key
        self.client_key = client_key
        self.base_url = "https://api.tosspayments.com/v1"
        self.headers = {
            "Authorization": f"Basic {secret_key}",
            "Content-Type": "application/json"
        }
    
    def create_payment(self, amount: int, order_id: str, user_info: Dict) -> Dict:
        """토스페이먼츠 결제 생성"""
        try:
            payment_data = {
                "orderId": order_id,
                "amount": amount,
                "currency": "KRW",
                "successUrl": f"{os.getenv('BASE_URL', 'http://localhost:5000')}/payment/success",
                "failUrl": f"{os.getenv('BASE_URL', 'http://localhost:5000')}/payment/fail",
                "customerName": user_info.get('name', '고객'),
                "customerEmail": user_info.get('email', ''),
                "customerMobilePhone": user_info.get('phone', ''),
                "orderName": user_info.get('plan_name', 'Signalcraft 구독'),
                "validHours": 24
            }
            
            response = requests.post(
                f"{self.base_url}/payments/online",
                headers=self.headers,
                json=payment_data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'payment_id': result.get('paymentKey'),
                    'checkout_url': result.get('checkoutUrl'),
                    'provider': 'toss'
                }
            else:
                return {
                    'success': False,
                    'error': f"토스페이먼츠 API 오류: {response.status_code}",
                    'provider': 'toss'
                }
                
        except Exception as e:
            logger.error(f"토스페이먼츠 결제 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'toss'
            }
    
    def verify_payment(self, payment_id: str) -> Dict:
        """토스페이먼츠 결제 검증"""
        try:
            response = requests.get(
                f"{self.base_url}/payments/{payment_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('status'),
                    'amount': result.get('totalAmount'),
                    'provider': 'toss'
                }
            else:
                return {
                    'success': False,
                    'error': f"토스페이먼츠 검증 오류: {response.status_code}",
                    'provider': 'toss'
                }
                
        except Exception as e:
            logger.error(f"토스페이먼츠 결제 검증 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'toss'
            }
    
    def cancel_payment(self, payment_id: str) -> Dict:
        """토스페이먼츠 결제 취소"""
        try:
            cancel_data = {
                "cancelReason": "고객 요청"
            }
            
            response = requests.post(
                f"{self.base_url}/payments/{payment_id}/cancel",
                headers=self.headers,
                json=cancel_data
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'provider': 'toss'
                }
            else:
                return {
                    'success': False,
                    'error': f"토스페이먼츠 취소 오류: {response.status_code}",
                    'provider': 'toss'
                }
                
        except Exception as e:
            logger.error(f"토스페이먼츠 결제 취소 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'toss'
            }

class BankTransferProvider(PaymentProvider):
    """계좌이체 결제 제공자"""
    
    def __init__(self, bank_info: Dict):
        self.bank_info = bank_info
    
    def create_payment(self, amount: int, order_id: str, user_info: Dict) -> Dict:
        """계좌이체 결제 생성"""
        try:
            return {
                'success': True,
                'payment_id': f"BANK_{order_id}",
                'bank_info': self.bank_info,
                'amount': amount,
                'order_id': order_id,
                'provider': 'bank_transfer'
            }
        except Exception as e:
            logger.error(f"계좌이체 결제 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'bank_transfer'
            }
    
    def verify_payment(self, payment_id: str) -> Dict:
        """계좌이체 결제 검증 (수동 확인 필요)"""
        return {
            'success': True,
            'status': 'PENDING',
            'provider': 'bank_transfer',
            'message': '입금 확인 대기 중'
        }
    
    def cancel_payment(self, payment_id: str) -> Dict:
        """계좌이체 결제 취소"""
        return {
            'success': True,
            'provider': 'bank_transfer',
            'message': '계좌이체는 취소할 수 없습니다'
        }

class UnifiedPaymentService:
    """통합 결제 서비스"""
    
    def __init__(self):
        self.providers = {}
        self.payment_plans = self._load_payment_plans()
        self.payment_history = []
        
        # 결제 제공자 초기화
        self._initialize_providers()
        
        logger.info("통합 결제 서비스 초기화 완료")
    
    def _initialize_providers(self):
        """결제 제공자 초기화"""
        try:
            # 토스페이먼츠
            toss_secret = os.getenv('TOSS_SECRET_KEY')
            toss_client = os.getenv('TOSS_CLIENT_KEY')
            if toss_secret and toss_client:
                self.providers['toss'] = TossPaymentsProvider(toss_secret, toss_client)
                logger.info("토스페이먼츠 제공자 초기화 완료")
            
            # 계좌이체
            bank_info = {
                'bank_name': '국민은행',
                'account_number': '101401-04-197042',
                'account_holder': '김선범'
            }
            self.providers['bank_transfer'] = BankTransferProvider(bank_info)
            logger.info("계좌이체 제공자 초기화 완료")
            
        except Exception as e:
            logger.error(f"결제 제공자 초기화 실패: {e}")
    
    def _load_payment_plans(self) -> Dict:
        """결제 플랜 로드"""
        return {
            'essential': {
                'name': '에센셜',
                'price': 29000,
                'features': ['핵심 냉동고 3대', '고장 징후 알림', '이메일 & 챗봇 지원'],
                'ai_models': ['lightweight']
            },
            'standard': {
                'name': '스탠다드',
                'price': 49000,
                'features': ['매장 전체 (최대 10대)', '고장 원인 분석', '유선 기술 지원'],
                'ai_models': ['lightweight', 'ensemble']
            },
            'premium': {
                'name': '프리미엄',
                'price': 99000,
                'features': ['최대 25대 (3개 매장)', '고장 원인 분석', '전력 사용량 비교', '전담 매니저'],
                'ai_models': ['lightweight', 'ensemble', 'mimii']
            }
        }
    
    def create_payment(self, plan_id: str, user_info: Dict, 
                      provider: str = 'auto') -> Dict:
        """결제 생성"""
        try:
            if plan_id not in self.payment_plans:
                return {
                    'success': False,
                    'error': f'존재하지 않는 플랜: {plan_id}'
                }
            
            plan = self.payment_plans[plan_id]
            amount = plan['price']
            order_id = self._generate_order_id()
            
            # 제공자 선택
            if provider == 'auto':
                provider = self._select_best_provider(user_info)
            
            if provider not in self.providers:
                return {
                    'success': False,
                    'error': f'지원하지 않는 결제 제공자: {provider}'
                }
            
            # 결제 생성
            payment_provider = self.providers[provider]
            result = payment_provider.create_payment(amount, order_id, {
                **user_info,
                'plan_name': plan['name']
            })
            
            if result['success']:
                # 결제 기록 저장
                payment_record = {
                    'order_id': order_id,
                    'plan_id': plan_id,
                    'amount': amount,
                    'provider': provider,
                    'user_info': user_info,
                    'status': 'PENDING',
                    'created_at': datetime.now().isoformat()
                }
                self.payment_history.append(payment_record)
                
                # 실시간 알림 전송
                self._send_payment_notification(payment_record)
            
            return result
            
        except Exception as e:
            logger.error(f"결제 생성 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id: str, provider: str) -> Dict:
        """결제 검증"""
        try:
            if provider not in self.providers:
                return {
                    'success': False,
                    'error': f'지원하지 않는 결제 제공자: {provider}'
                }
            
            payment_provider = self.providers[provider]
            result = payment_provider.verify_payment(payment_id)
            
            if result['success']:
                # 결제 상태 업데이트
                self._update_payment_status(payment_id, result.get('status', 'COMPLETED'))
                
                # 완료 알림 전송
                self._send_payment_completion_notification(payment_id)
            
            return result
            
        except Exception as e:
            logger.error(f"결제 검증 실패: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_payment_plans(self) -> Dict:
        """결제 플랜 조회"""
        return {
            'success': True,
            'plans': self.payment_plans
        }
    
    def _generate_order_id(self) -> str:
        """주문 ID 생성"""
        timestamp = int(time.time())
        random_str = hashlib.md5(f"{timestamp}{os.urandom(8)}".encode()).hexdigest()[:8]
        return f"SC_{timestamp}_{random_str}"
    
    def _select_best_provider(self, user_info: Dict) -> str:
        """최적의 결제 제공자 선택"""
        # 기본적으로 토스페이먼츠 사용
        return 'toss' if 'toss' in self.providers else 'bank_transfer'
    
    def _update_payment_status(self, payment_id: str, status: str):
        """결제 상태 업데이트"""
        for payment in self.payment_history:
            if payment.get('order_id') == payment_id or payment.get('payment_id') == payment_id:
                payment['status'] = status
                payment['updated_at'] = datetime.now().isoformat()
                break
    
    def _send_payment_notification(self, payment_record: Dict):
        """결제 알림 전송"""
        try:
            # 통합 알림 서비스를 통한 알림 전송
            from services.notification_service import unified_notification_service
            
            user_info = payment_record.get('user_info', {})
            unified_notification_service.send_payment_notification(
                payment_data=payment_record,
                user_email=user_info.get('email'),
                user_kakao_id=user_info.get('kakao_id')
            )
                
        except Exception as e:
            logger.error(f"결제 알림 전송 실패: {e}")
    
    def _send_payment_completion_notification(self, payment_id: str):
        """결제 완료 알림 전송"""
        try:
            # 통합 알림 서비스를 통한 알림 전송
            from services.notification_service import unified_notification_service
            
            # 결제 기록에서 사용자 정보 찾기
            payment_record = None
            for payment in self.payment_history:
                if payment.get('order_id') == payment_id or payment.get('payment_id') == payment_id:
                    payment_record = payment
                    break
            
            if payment_record:
                user_info = payment_record.get('user_info', {})
                unified_notification_service.send_payment_notification(
                    payment_data=payment_record,
                    user_email=user_info.get('email'),
                    user_kakao_id=user_info.get('kakao_id')
                )
            
        except Exception as e:
            logger.error(f"결제 완료 알림 전송 실패: {e}")
    
    def get_service_status(self) -> Dict:
        """서비스 상태 확인"""
        return {
            'status': 'healthy',
            'providers': list(self.providers.keys()),
            'plans_count': len(self.payment_plans),
            'total_payments': len(self.payment_history)
        }

# 전역 서비스 인스턴스
unified_payment_service = UnifiedPaymentService()