#!/usr/bin/env python3
"""
모바일 결제 관리 서비스
Starbucks App을 벤치마킹한 결제 관리 시스템
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
import statistics

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """결제 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(Enum):
    """결제 방법"""
    CARD = "card"
    KAKAO_PAY = "kakao_pay"
    TOSS = "toss"
    CASH = "cash"
    MOBILE_PAYMENT = "mobile_payment"

class TransactionType(Enum):
    """거래 타입"""
    PURCHASE = "purchase"
    REFUND = "refund"
    PARTIAL_REFUND = "partial_refund"
    VOID = "void"

@dataclass
class PaymentTransaction:
    """결제 거래 클래스"""
    id: str
    store_id: str
    amount: float
    currency: str = "KRW"
    payment_method: PaymentMethod = PaymentMethod.CARD
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_type: TransactionType = TransactionType.PURCHASE
    customer_id: Optional[str] = None
    order_id: Optional[str] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class PaymentSummary:
    """결제 요약 클래스"""
    store_id: str
    date: datetime
    total_amount: float
    transaction_count: int
    successful_count: int
    failed_count: int
    refund_count: int
    average_amount: float
    payment_methods: Dict[str, int]
    hourly_breakdown: Dict[str, float]

class MobilePaymentService:
    """모바일 결제 관리 서비스"""
    
    def __init__(self):
        self.transactions: Dict[str, PaymentTransaction] = {}
        self.payment_callbacks: List[Callable] = []
        self.real_time_data: Dict[str, Any] = {}
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # 결제 통계
        self.daily_stats: Dict[str, PaymentSummary] = {}
        
        # 실시간 모니터링 데이터
        self.real_time_queue = deque(maxlen=1000)
        
        # 결제 처리 시뮬레이션
        self.payment_processors = {
            PaymentMethod.CARD: self._process_card_payment,
            PaymentMethod.KAKAO_PAY: self._process_kakao_pay,
            PaymentMethod.TOSS: self._process_toss_payment,
            PaymentMethod.CASH: self._process_cash_payment,
            PaymentMethod.MOBILE_PAYMENT: self._process_mobile_payment
        }
        
        # 실시간 모니터링 시작
        self._start_real_time_monitoring()
    
    def _start_real_time_monitoring(self):
        """실시간 모니터링 시작"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
        self.monitoring_thread.start()
        logger.info("결제 실시간 모니터링 시작")
    
    def _monitoring_worker(self):
        """모니터링 워커"""
        while self.is_monitoring:
            try:
                # 실시간 데이터 업데이트
                self._update_real_time_data()
                
                # 콜백 실행
                self._notify_real_time_update()
                
                time.sleep(5)  # 5초마다 업데이트
                
            except Exception as e:
                logger.error(f"결제 모니터링 워커 오류: {e}")
                time.sleep(10)
    
    def _update_real_time_data(self):
        """실시간 데이터 업데이트"""
        current_time = datetime.now()
        today = current_time.date()
        
        # 오늘의 거래 데이터
        today_transactions = [
            t for t in self.transactions.values()
            if t.created_at.date() == today
        ]
        
        # 실시간 통계 계산
        self.real_time_data = {
            'timestamp': current_time.isoformat(),
            'today_total': sum(t.amount for t in today_transactions if t.status == PaymentStatus.COMPLETED),
            'today_count': len([t for t in today_transactions if t.status == PaymentStatus.COMPLETED]),
            'pending_count': len([t for t in today_transactions if t.status == PaymentStatus.PENDING]),
            'failed_count': len([t for t in today_transactions if t.status == PaymentStatus.FAILED]),
            'average_amount': statistics.mean([t.amount for t in today_transactions if t.status == PaymentStatus.COMPLETED]) if today_transactions else 0,
            'recent_transactions': [
                {
                    'id': t.id,
                    'amount': t.amount,
                    'method': t.payment_method.value,
                    'status': t.status.value,
                    'timestamp': t.created_at.isoformat()
                }
                for t in sorted(today_transactions, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }
    
    def _notify_real_time_update(self):
        """실시간 업데이트 알림"""
        for callback in self.payment_callbacks:
            try:
                callback({
                    'type': 'real_time_update',
                    'data': self.real_time_data
                })
            except Exception as e:
                logger.error(f"실시간 업데이트 알림 오류: {e}")
    
    async def process_payment(self, transaction: PaymentTransaction) -> bool:
        """결제 처리"""
        try:
            # 결제 유효성 검사
            if not self._validate_payment(transaction):
                return False
            
            # 결제 상태 업데이트
            transaction.status = PaymentStatus.PROCESSING
            
            # 결제 처리기 선택
            processor = self.payment_processors.get(transaction.payment_method)
            if not processor:
                transaction.status = PaymentStatus.FAILED
                transaction.error_message = "지원하지 않는 결제 방법"
                return False
            
            # 결제 처리 실행
            success = await processor(transaction)
            
            if success:
                transaction.status = PaymentStatus.COMPLETED
                transaction.completed_at = datetime.now()
                logger.info(f"결제 완료: {transaction.id} - {transaction.amount}원")
            else:
                transaction.status = PaymentStatus.FAILED
                transaction.failed_at = datetime.now()
                logger.error(f"결제 실패: {transaction.id}")
            
            # 거래 저장
            self.transactions[transaction.id] = transaction
            
            # 실시간 데이터에 추가
            self.real_time_queue.append(transaction)
            
            # 콜백 실행
            self._notify_payment_completed(transaction)
            
            return success
            
        except Exception as e:
            transaction.status = PaymentStatus.FAILED
            transaction.error_message = str(e)
            logger.error(f"결제 처리 오류: {e}")
            return False
    
    def _validate_payment(self, transaction: PaymentTransaction) -> bool:
        """결제 유효성 검사"""
        if transaction.amount <= 0:
            transaction.error_message = "결제 금액이 유효하지 않습니다"
            return False
        
        if not transaction.store_id:
            transaction.error_message = "매장 ID가 필요합니다"
            return False
        
        if transaction.amount > 1000000:  # 100만원 이상
            transaction.error_message = "결제 한도를 초과했습니다"
            return False
        
        return True
    
    async def _process_card_payment(self, transaction: PaymentTransaction) -> bool:
        """카드 결제 처리"""
        # 카드 결제 시뮬레이션
        await asyncio.sleep(2)  # 실제로는 카드 결제 API 호출
        
        # 95% 성공률 시뮬레이션
        import random
        return random.random() < 0.95
    
    async def _process_kakao_pay(self, transaction: PaymentTransaction) -> bool:
        """카카오페이 결제 처리"""
        await asyncio.sleep(1.5)
        
        # 98% 성공률 시뮬레이션
        import random
        return random.random() < 0.98
    
    async def _process_toss_payment(self, transaction: PaymentTransaction) -> bool:
        """토스 결제 처리"""
        await asyncio.sleep(1.2)
        
        # 97% 성공률 시뮬레이션
        import random
        return random.random() < 0.97
    
    async def _process_cash_payment(self, transaction: PaymentTransaction) -> bool:
        """현금 결제 처리"""
        await asyncio.sleep(0.5)
        
        # 현금은 항상 성공
        return True
    
    async def _process_mobile_payment(self, transaction: PaymentTransaction) -> bool:
        """모바일 결제 처리"""
        await asyncio.sleep(1.8)
        
        # 96% 성공률 시뮬레이션
        import random
        return random.random() < 0.96
    
    def _notify_payment_completed(self, transaction: PaymentTransaction):
        """결제 완료 알림"""
        for callback in self.payment_callbacks:
            try:
                callback({
                    'type': 'payment_completed',
                    'transaction': asdict(transaction)
                })
            except Exception as e:
                logger.error(f"결제 완료 알림 오류: {e}")
    
    async def refund_payment(self, transaction_id: str, amount: Optional[float] = None) -> bool:
        """결제 환불"""
        try:
            if transaction_id not in self.transactions:
                logger.error(f"존재하지 않는 거래: {transaction_id}")
                return False
            
            original_transaction = self.transactions[transaction_id]
            
            if original_transaction.status != PaymentStatus.COMPLETED:
                logger.error(f"환불 불가능한 거래 상태: {original_transaction.status}")
                return False
            
            # 환불 금액 결정
            refund_amount = amount if amount is not None else original_transaction.amount
            
            if refund_amount > original_transaction.amount:
                logger.error("환불 금액이 원래 결제 금액을 초과합니다")
                return False
            
            # 환불 거래 생성
            refund_transaction = PaymentTransaction(
                id=f"refund_{transaction_id}_{int(time.time())}",
                store_id=original_transaction.store_id,
                amount=refund_amount,
                currency=original_transaction.currency,
                payment_method=original_transaction.payment_method,
                status=PaymentStatus.PROCESSING,
                transaction_type=TransactionType.REFUND if refund_amount == original_transaction.amount else TransactionType.PARTIAL_REFUND,
                customer_id=original_transaction.customer_id,
                order_id=original_transaction.order_id,
                metadata={
                    'original_transaction_id': transaction_id,
                    'refund_reason': 'customer_request'
                }
            )
            
            # 환불 처리
            success = await self.process_payment(refund_transaction)
            
            if success:
                # 원래 거래 상태 업데이트
                if refund_amount == original_transaction.amount:
                    original_transaction.status = PaymentStatus.REFUNDED
                else:
                    original_transaction.metadata = original_transaction.metadata or {}
                    original_transaction.metadata['partial_refund'] = True
                    original_transaction.metadata['refunded_amount'] = refund_amount
                
                logger.info(f"환불 완료: {transaction_id} - {refund_amount}원")
            
            return success
            
        except Exception as e:
            logger.error(f"환불 처리 오류: {e}")
            return False
    
    def get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """거래 조회"""
        return self.transactions.get(transaction_id)
    
    def get_transactions(self, store_id: str = None, 
                        start_date: datetime = None, 
                        end_date: datetime = None,
                        status: PaymentStatus = None,
                        limit: int = 100) -> List[PaymentTransaction]:
        """거래 목록 조회"""
        transactions = list(self.transactions.values())
        
        # 필터링
        if store_id:
            transactions = [t for t in transactions if t.store_id == store_id]
        
        if start_date:
            transactions = [t for t in transactions if t.created_at >= start_date]
        
        if end_date:
            transactions = [t for t in transactions if t.created_at <= end_date]
        
        if status:
            transactions = [t for t in transactions if t.status == status]
        
        # 정렬 및 제한
        transactions.sort(key=lambda x: x.created_at, reverse=True)
        return transactions[:limit]
    
    def get_payment_summary(self, store_id: str, date: datetime = None) -> PaymentSummary:
        """결제 요약 조회"""
        if date is None:
            date = datetime.now()
        
        # 해당 날짜의 거래들
        transactions = [
            t for t in self.transactions.values()
            if t.store_id == store_id and t.created_at.date() == date.date()
        ]
        
        # 통계 계산
        total_amount = sum(t.amount for t in transactions if t.status == PaymentStatus.COMPLETED)
        transaction_count = len(transactions)
        successful_count = len([t for t in transactions if t.status == PaymentStatus.COMPLETED])
        failed_count = len([t for t in transactions if t.status == PaymentStatus.FAILED])
        refund_count = len([t for t in transactions if t.transaction_type in [TransactionType.REFUND, TransactionType.PARTIAL_REFUND]])
        
        # 결제 방법별 통계
        payment_methods = {}
        for transaction in transactions:
            method = transaction.payment_method.value
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        # 시간대별 분석
        hourly_breakdown = {}
        for transaction in transactions:
            hour = transaction.created_at.hour
            hourly_breakdown[str(hour)] = hourly_breakdown.get(str(hour), 0) + transaction.amount
        
        return PaymentSummary(
            store_id=store_id,
            date=date,
            total_amount=total_amount,
            transaction_count=transaction_count,
            successful_count=successful_count,
            failed_count=failed_count,
            refund_count=refund_count,
            average_amount=total_amount / successful_count if successful_count > 0 else 0,
            payment_methods=payment_methods,
            hourly_breakdown=hourly_breakdown
        )
    
    def get_real_time_data(self) -> Dict[str, Any]:
        """실시간 데이터 조회"""
        return self.real_time_data
    
    def get_payment_analytics(self, store_id: str, days: int = 30) -> Dict[str, Any]:
        """결제 분석 데이터 조회"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        transactions = self.get_transactions(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # 일별 매출
        daily_revenue = {}
        for transaction in transactions:
            if transaction.status == PaymentStatus.COMPLETED:
                date_str = transaction.created_at.date().isoformat()
                daily_revenue[date_str] = daily_revenue.get(date_str, 0) + transaction.amount
        
        # 결제 방법별 분석
        method_analysis = {}
        for transaction in transactions:
            if transaction.status == PaymentStatus.COMPLETED:
                method = transaction.payment_method.value
                if method not in method_analysis:
                    method_analysis[method] = {'count': 0, 'amount': 0}
                method_analysis[method]['count'] += 1
                method_analysis[method]['amount'] += transaction.amount
        
        # 성공률 계산
        total_attempts = len(transactions)
        successful_attempts = len([t for t in transactions if t.status == PaymentStatus.COMPLETED])
        success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'summary': {
                'total_revenue': sum(daily_revenue.values()),
                'total_transactions': total_attempts,
                'successful_transactions': successful_attempts,
                'success_rate': success_rate,
                'average_transaction': sum(daily_revenue.values()) / successful_attempts if successful_attempts > 0 else 0
            },
            'daily_revenue': daily_revenue,
            'method_analysis': method_analysis,
            'trends': {
                'growth_rate': self._calculate_growth_rate(daily_revenue),
                'peak_hours': self._find_peak_hours(transactions),
                'peak_days': self._find_peak_days(transactions)
            }
        }
    
    def _calculate_growth_rate(self, daily_revenue: Dict[str, float]) -> float:
        """성장률 계산"""
        if len(daily_revenue) < 2:
            return 0.0
        
        sorted_dates = sorted(daily_revenue.keys())
        first_week = sum(daily_revenue[date] for date in sorted_dates[:7])
        last_week = sum(daily_revenue[date] for date in sorted_dates[-7:])
        
        if first_week == 0:
            return 0.0
        
        return ((last_week - first_week) / first_week) * 100
    
    def _find_peak_hours(self, transactions: List[PaymentTransaction]) -> List[int]:
        """피크 시간대 찾기"""
        hourly_counts = {}
        for transaction in transactions:
            if transaction.status == PaymentStatus.COMPLETED:
                hour = transaction.created_at.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        if not hourly_counts:
            return []
        
        max_count = max(hourly_counts.values())
        return [hour for hour, count in hourly_counts.items() if count == max_count]
    
    def _find_peak_days(self, transactions: List[PaymentTransaction]) -> List[str]:
        """피크 요일 찾기"""
        daily_counts = {}
        for transaction in transactions:
            if transaction.status == PaymentStatus.COMPLETED:
                day = transaction.created_at.strftime('%A')
                daily_counts[day] = daily_counts.get(day, 0) + 1
        
        if not daily_counts:
            return []
        
        max_count = max(daily_counts.values())
        return [day for day, count in daily_counts.items() if count == max_count]
    
    def add_payment_callback(self, callback: Callable):
        """결제 콜백 함수 추가"""
        self.payment_callbacks.append(callback)
    
    def remove_payment_callback(self, callback: Callable):
        """결제 콜백 함수 제거"""
        if callback in self.payment_callbacks:
            self.payment_callbacks.remove(callback)
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'is_monitoring': self.is_monitoring,
            'total_transactions': len(self.transactions),
            'real_time_queue_size': len(self.real_time_queue),
            'callbacks_count': len(self.payment_callbacks),
            'last_update': self.real_time_data.get('timestamp')
        }
    
    def stop_service(self):
        """서비스 중지"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("모바일 결제 서비스 중지")

# 전역 인스턴스
mobile_payment_service = MobilePaymentService()
