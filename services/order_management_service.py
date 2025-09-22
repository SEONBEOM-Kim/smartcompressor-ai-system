#!/usr/bin/env python3
"""
주문 관리 서비스
Uber Eats와 DoorDash 스타일의 주문 관리 시스템
"""

import time
import logging
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from sqlite3 import connect
import json
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    """주문 상태 열거형"""
    PENDING = "pending"           # 주문 대기
    CONFIRMED = "confirmed"       # 주문 확인
    PREPARING = "preparing"       # 제조 중
    READY = "ready"              # 준비 완료
    COMPLETED = "completed"       # 완료
    CANCELLED = "cancelled"       # 취소됨
    REFUNDED = "refunded"         # 환불됨

class PaymentStatus(Enum):
    """결제 상태 열거형"""
    PENDING = "pending"           # 결제 대기
    PROCESSING = "processing"     # 결제 처리 중
    COMPLETED = "completed"       # 결제 완료
    FAILED = "failed"            # 결제 실패
    REFUNDED = "refunded"         # 환불됨

class PaymentMethod(Enum):
    """결제 방법 열거형"""
    CARD = "card"                # 카드 결제
    KAKAO = "kakao"              # 카카오페이
    TOSS = "toss"                # 토스페이먼츠
    CASH = "cash"                # 현금 결제

@dataclass
class OrderItem:
    """주문 아이템"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    options: List[Dict]
    special_instructions: str

@dataclass
class Order:
    """주문 정보"""
    id: str
    order_number: str
    user_id: str
    user_name: str
    user_phone: str
    user_email: str
    store_id: str
    store_name: str
    items: List[OrderItem]
    subtotal: float
    delivery_fee: float
    tax: float
    total: float
    status: OrderStatus
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    payment_id: str
    special_instructions: str
    estimated_preparation_time: int  # 분
    actual_preparation_time: int     # 분
    created_at: str
    updated_at: str
    completed_at: str

@dataclass
class OrderTracking:
    """주문 추적"""
    order_id: str
    status: OrderStatus
    timestamp: str
    message: str
    location: Optional[Dict]

class OrderManagementService:
    """주문 관리 서비스 (Uber Eats & DoorDash 스타일)"""
    
    def __init__(self, db_path: str = 'data/order_management.db'):
        self.db_path = db_path
        self.orders = {}
        self.order_tracking = {}
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 기존 데이터 로드
        self._load_orders()
        self._load_order_tracking()
        
        logger.info("주문 관리 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 주문 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id TEXT PRIMARY KEY,
                        order_number TEXT UNIQUE NOT NULL,
                        user_id TEXT NOT NULL,
                        user_name TEXT NOT NULL,
                        user_phone TEXT NOT NULL,
                        user_email TEXT NOT NULL,
                        store_id TEXT NOT NULL,
                        store_name TEXT NOT NULL,
                        items TEXT NOT NULL,
                        subtotal REAL NOT NULL,
                        delivery_fee REAL NOT NULL,
                        tax REAL NOT NULL,
                        total REAL NOT NULL,
                        status TEXT NOT NULL,
                        payment_method TEXT NOT NULL,
                        payment_status TEXT NOT NULL,
                        payment_id TEXT,
                        special_instructions TEXT,
                        estimated_preparation_time INTEGER DEFAULT 10,
                        actual_preparation_time INTEGER,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        completed_at TEXT
                    )
                ''')
                
                # 주문 추적 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS order_tracking (
                        id TEXT PRIMARY KEY,
                        order_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        message TEXT NOT NULL,
                        location TEXT,
                        FOREIGN KEY (order_id) REFERENCES orders (id)
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_store ON orders(store_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracking_order ON order_tracking(order_id)')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _load_orders(self):
        """주문 데이터 로드"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
                
                for row in cursor.fetchall():
                    # OrderItem 객체 생성
                    items_data = json.loads(row[8])
                    items = []
                    for item_data in items_data:
                        item = OrderItem(
                            product_id=item_data['product_id'],
                            product_name=item_data['product_name'],
                            quantity=item_data['quantity'],
                            unit_price=item_data['unit_price'],
                            total_price=item_data['total_price'],
                            options=item_data['options'],
                            special_instructions=item_data.get('special_instructions', '')
                        )
                        items.append(item)
                    
                    order = Order(
                        id=row[0],
                        order_number=row[1],
                        user_id=row[2],
                        user_name=row[3],
                        user_phone=row[4],
                        user_email=row[5],
                        store_id=row[6],
                        store_name=row[7],
                        items=items,
                        subtotal=row[9],
                        delivery_fee=row[10],
                        tax=row[11],
                        total=row[12],
                        status=OrderStatus(row[13]),
                        payment_method=PaymentMethod(row[14]),
                        payment_status=PaymentStatus(row[15]),
                        payment_id=row[16] or '',
                        special_instructions=row[17] or '',
                        estimated_preparation_time=row[18] or 10,
                        actual_preparation_time=row[19],
                        created_at=row[20],
                        updated_at=row[21],
                        completed_at=row[22] or ''
                    )
                    
                    self.orders[order.id] = order
                
                logger.info(f"주문 데이터 로드 완료: {len(self.orders)}개")
                
        except Exception as e:
            logger.error(f"주문 데이터 로드 실패: {e}")
    
    def _load_order_tracking(self):
        """주문 추적 데이터 로드"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM order_tracking ORDER BY timestamp DESC')
                
                for row in cursor.fetchall():
                    tracking = OrderTracking(
                        id=row[0],
                        order_id=row[1],
                        status=OrderStatus(row[2]),
                        timestamp=row[3],
                        message=row[4],
                        location=json.loads(row[5]) if row[5] else None
                    )
                    
                    if order_id not in self.order_tracking:
                        self.order_tracking[order_id] = []
                    self.order_tracking[order_id].append(tracking)
                
                logger.info(f"주문 추적 데이터 로드 완료: {len(self.order_tracking)}개")
                
        except Exception as e:
            logger.error(f"주문 추적 데이터 로드 실패: {e}")
    
    def create_order(self, order_data: Dict) -> Tuple[bool, str]:
        """주문 생성"""
        try:
            # 주문 ID 생성
            order_id = str(uuid.uuid4())
            order_number = self._generate_order_number()
            
            # OrderItem 객체 생성
            items = []
            for item_data in order_data['items']:
                item = OrderItem(
                    product_id=item_data['product_id'],
                    product_name=item_data['product_name'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                    options=item_data.get('options', []),
                    special_instructions=item_data.get('special_instructions', '')
                )
                items.append(item)
            
            # 주문 객체 생성
            order = Order(
                id=order_id,
                order_number=order_number,
                user_id=order_data['user_id'],
                user_name=order_data['user_name'],
                user_phone=order_data['user_phone'],
                user_email=order_data['user_email'],
                store_id=order_data['store_id'],
                store_name=order_data['store_name'],
                items=items,
                subtotal=order_data['subtotal'],
                delivery_fee=order_data['delivery_fee'],
                tax=order_data['tax'],
                total=order_data['total'],
                status=OrderStatus.PENDING,
                payment_method=PaymentMethod(order_data['payment_method']),
                payment_status=PaymentStatus.PENDING,
                payment_id=order_data.get('payment_id', ''),
                special_instructions=order_data.get('special_instructions', ''),
                estimated_preparation_time=order_data.get('estimated_preparation_time', 10),
                actual_preparation_time=None,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                completed_at=''
            )
            
            # 데이터베이스에 저장
            self._save_order(order)
            
            # 메모리에 추가
            self.orders[order.id] = order
            
            # 주문 추적 추가
            self._add_order_tracking(order.id, OrderStatus.PENDING, "주문이 접수되었습니다.")
            
            logger.info(f"주문 생성 완료: {order.id} - {order.order_number}")
            return True, order_id
            
        except Exception as e:
            logger.error(f"주문 생성 실패: {e}")
            return False, str(e)
    
    def _generate_order_number(self) -> str:
        """주문 번호 생성"""
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        return f"SC{timestamp}{random_num}"
    
    def update_order_status(self, order_id: str, status: OrderStatus, message: str = None) -> bool:
        """주문 상태 업데이트"""
        try:
            if order_id not in self.orders:
                return False
            
            order = self.orders[order_id]
            old_status = order.status
            order.status = status
            order.updated_at = datetime.now().isoformat()
            
            # 완료 시간 설정
            if status == OrderStatus.COMPLETED:
                order.completed_at = datetime.now().isoformat()
                if order.actual_preparation_time is None:
                    # 실제 제조 시간 계산
                    created_time = datetime.fromisoformat(order.created_at)
                    completed_time = datetime.now()
                    order.actual_preparation_time = int((completed_time - created_time).total_seconds() / 60)
            
            # 데이터베이스 업데이트
            self._save_order(order)
            
            # 주문 추적 추가
            if message is None:
                message = self._get_status_message(status)
            self._add_order_tracking(order_id, status, message)
            
            logger.info(f"주문 상태 업데이트 완료: {order_id} - {old_status.value} -> {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"주문 상태 업데이트 실패: {e}")
            return False
    
    def _get_status_message(self, status: OrderStatus) -> str:
        """상태별 메시지"""
        messages = {
            OrderStatus.PENDING: "주문이 접수되었습니다.",
            OrderStatus.CONFIRMED: "주문이 확인되었습니다.",
            OrderStatus.PREPARING: "제조를 시작했습니다.",
            OrderStatus.READY: "준비가 완료되었습니다.",
            OrderStatus.COMPLETED: "주문이 완료되었습니다.",
            OrderStatus.CANCELLED: "주문이 취소되었습니다.",
            OrderStatus.REFUNDED: "환불이 처리되었습니다."
        }
        return messages.get(status, "상태가 업데이트되었습니다.")
    
    def update_payment_status(self, order_id: str, payment_status: PaymentStatus, payment_id: str = None) -> bool:
        """결제 상태 업데이트"""
        try:
            if order_id not in self.orders:
                return False
            
            order = self.orders[order_id]
            order.payment_status = payment_status
            order.payment_id = payment_id or order.payment_id
            order.updated_at = datetime.now().isoformat()
            
            # 데이터베이스 업데이트
            self._save_order(order)
            
            # 주문 추적 추가
            payment_messages = {
                PaymentStatus.PROCESSING: "결제를 처리하고 있습니다.",
                PaymentStatus.COMPLETED: "결제가 완료되었습니다.",
                PaymentStatus.FAILED: "결제에 실패했습니다.",
                PaymentStatus.REFUNDED: "환불이 처리되었습니다."
            }
            message = payment_messages.get(payment_status, "결제 상태가 업데이트되었습니다.")
            self._add_order_tracking(order_id, order.status, message)
            
            logger.info(f"결제 상태 업데이트 완료: {order_id} - {payment_status.value}")
            return True
            
        except Exception as e:
            logger.error(f"결제 상태 업데이트 실패: {e}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """주문 정보 조회"""
        try:
            if order_id not in self.orders:
                return None
            
            order = self.orders[order_id]
            order_dict = asdict(order)
            
            # OrderItem 객체를 딕셔너리로 변환
            order_dict['items'] = [asdict(item) for item in order.items]
            order_dict['status'] = order.status.value
            order_dict['payment_method'] = order.payment_method.value
            order_dict['payment_status'] = order.payment_status.value
            
            return order_dict
            
        except Exception as e:
            logger.error(f"주문 정보 조회 실패: {e}")
            return None
    
    def get_orders_by_user(self, user_id: str, limit: int = 20) -> List[Dict]:
        """사용자별 주문 목록 조회"""
        try:
            orders = []
            
            for order in self.orders.values():
                if order.user_id == user_id:
                    order_dict = asdict(order)
                    order_dict['items'] = [asdict(item) for item in order.items]
                    order_dict['status'] = order.status.value
                    order_dict['payment_method'] = order.payment_method.value
                    order_dict['payment_status'] = order.payment_status.value
                    orders.append(order_dict)
                    
                    if len(orders) >= limit:
                        break
            
            return orders
            
        except Exception as e:
            logger.error(f"사용자별 주문 목록 조회 실패: {e}")
            return []
    
    def get_orders_by_store(self, store_id: str, limit: int = 20) -> List[Dict]:
        """매장별 주문 목록 조회"""
        try:
            orders = []
            
            for order in self.orders.values():
                if order.store_id == store_id:
                    order_dict = asdict(order)
                    order_dict['items'] = [asdict(item) for item in order.items]
                    order_dict['status'] = order.status.value
                    order_dict['payment_method'] = order.payment_method.value
                    order_dict['payment_status'] = order.payment_status.value
                    orders.append(order_dict)
                    
                    if len(orders) >= limit:
                        break
            
            return orders
            
        except Exception as e:
            logger.error(f"매장별 주문 목록 조회 실패: {e}")
            return []
    
    def get_order_tracking(self, order_id: str) -> List[Dict]:
        """주문 추적 정보 조회"""
        try:
            if order_id not in self.order_tracking:
                return []
            
            tracking_list = []
            for tracking in self.order_tracking[order_id]:
                tracking_dict = asdict(tracking)
                tracking_dict['status'] = tracking.status.value
                tracking_list.append(tracking_dict)
            
            return tracking_list
            
        except Exception as e:
            logger.error(f"주문 추적 정보 조회 실패: {e}")
            return []
    
    def cancel_order(self, order_id: str, reason: str = None) -> bool:
        """주문 취소"""
        try:
            if order_id not in self.orders:
                return False
            
            order = self.orders[order_id]
            
            # 취소 가능한 상태인지 확인
            if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.REFUNDED]:
                return False
            
            # 주문 상태를 취소로 변경
            self.update_order_status(order_id, OrderStatus.CANCELLED, reason or "주문이 취소되었습니다.")
            
            # 결제 상태도 취소로 변경 (환불 처리)
            self.update_payment_status(order_id, PaymentStatus.REFUNDED)
            
            logger.info(f"주문 취소 완료: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"주문 취소 실패: {e}")
            return False
    
    def get_order_statistics(self, store_id: str = None, days: int = 30) -> Dict:
        """주문 통계 조회"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            orders = []
            if store_id:
                orders = [order for order in self.orders.values() 
                         if order.store_id == store_id and 
                         datetime.fromisoformat(order.created_at) >= start_date]
            else:
                orders = [order for order in self.orders.values() 
                         if datetime.fromisoformat(order.created_at) >= start_date]
            
            # 통계 계산
            total_orders = len(orders)
            total_revenue = sum(order.total for order in orders)
            completed_orders = len([order for order in orders if order.status == OrderStatus.COMPLETED])
            cancelled_orders = len([order for order in orders if order.status == OrderStatus.CANCELLED])
            
            # 평균 주문 금액
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            # 평균 제조 시간
            completed_orders_with_time = [order for order in orders 
                                        if order.status == OrderStatus.COMPLETED and order.actual_preparation_time]
            avg_preparation_time = (sum(order.actual_preparation_time for order in completed_orders_with_time) / 
                                  len(completed_orders_with_time)) if completed_orders_with_time else 0
            
            # 상태별 분포
            status_distribution = {}
            for order in orders:
                status = order.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            return {
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'avg_order_value': avg_order_value,
                'avg_preparation_time': avg_preparation_time,
                'completion_rate': (completed_orders / total_orders * 100) if total_orders > 0 else 0,
                'cancellation_rate': (cancelled_orders / total_orders * 100) if total_orders > 0 else 0,
                'status_distribution': status_distribution
            }
            
        except Exception as e:
            logger.error(f"주문 통계 조회 실패: {e}")
            return {}
    
    def _add_order_tracking(self, order_id: str, status: OrderStatus, message: str):
        """주문 추적 추가"""
        try:
            tracking_id = str(uuid.uuid4())
            tracking = OrderTracking(
                id=tracking_id,
                order_id=order_id,
                status=status,
                timestamp=datetime.now().isoformat(),
                message=message,
                location=None
            )
            
            # 데이터베이스에 저장
            self._save_order_tracking(tracking)
            
            # 메모리에 추가
            if order_id not in self.order_tracking:
                self.order_tracking[order_id] = []
            self.order_tracking[order_id].append(tracking)
            
        except Exception as e:
            logger.error(f"주문 추적 추가 실패: {e}")
    
    def _save_order(self, order: Order):
        """주문 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # OrderItem 객체를 딕셔너리로 변환
                items_data = [asdict(item) for item in order.items]
                
                cursor.execute('''
                    INSERT OR REPLACE INTO orders 
                    (id, order_number, user_id, user_name, user_phone, user_email, store_id, store_name, 
                     items, subtotal, delivery_fee, tax, total, status, payment_method, payment_status, 
                     payment_id, special_instructions, estimated_preparation_time, actual_preparation_time, 
                     created_at, updated_at, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order.id,
                    order.order_number,
                    order.user_id,
                    order.user_name,
                    order.user_phone,
                    order.user_email,
                    order.store_id,
                    order.store_name,
                    json.dumps(items_data),
                    order.subtotal,
                    order.delivery_fee,
                    order.tax,
                    order.total,
                    order.status.value,
                    order.payment_method.value,
                    order.payment_status.value,
                    order.payment_id,
                    order.special_instructions,
                    order.estimated_preparation_time,
                    order.actual_preparation_time,
                    order.created_at,
                    order.updated_at,
                    order.completed_at
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"주문 저장 실패: {e}")
    
    def _save_order_tracking(self, tracking: OrderTracking):
        """주문 추적 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO order_tracking 
                    (id, order_id, status, timestamp, message, location)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    tracking.id,
                    tracking.order_id,
                    tracking.status.value,
                    tracking.timestamp,
                    tracking.message,
                    json.dumps(tracking.location) if tracking.location else None
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"주문 추적 저장 실패: {e}")

# 전역 서비스 인스턴스
order_management_service = OrderManagementService()
