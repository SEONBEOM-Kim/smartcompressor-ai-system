"""
고객 분석 서비스
고객 행동 패턴, 구매 트렌드, 세그멘테이션 분석
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class CustomerAnalyticsService:
    """고객 분석 서비스"""
    
    def __init__(self, db_path: str = "data/customer_analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 고객 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100),
                    email VARCHAR(255),
                    phone VARCHAR(20),
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_visit TIMESTAMP,
                    total_visits INTEGER DEFAULT 0,
                    total_spent REAL DEFAULT 0.0,
                    customer_segment VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'active'
                )
            ''')
            
            # 구매 기록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id VARCHAR(50),
                    purchase_date TIMESTAMP,
                    amount REAL,
                    product_category VARCHAR(100),
                    payment_method VARCHAR(50),
                    store_id VARCHAR(50),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            ''')
            
            # 고객 행동 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customer_behavior (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id VARCHAR(50),
                    action_type VARCHAR(50),
                    action_date TIMESTAMP,
                    session_duration INTEGER,
                    pages_visited INTEGER,
                    device_type VARCHAR(50),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            ''')
            
            # 고객 세그먼트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customer_segments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    segment_name VARCHAR(100),
                    criteria JSON,
                    customer_count INTEGER,
                    avg_value REAL,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("고객 분석 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def add_customer(self, customer_data: Dict) -> bool:
        """고객 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO customers 
                (customer_id, name, email, phone, registration_date, last_visit, total_visits, total_spent, customer_segment, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                customer_data.get('customer_id'),
                customer_data.get('name'),
                customer_data.get('email'),
                customer_data.get('phone'),
                customer_data.get('registration_date', datetime.now()),
                customer_data.get('last_visit'),
                customer_data.get('total_visits', 0),
                customer_data.get('total_spent', 0.0),
                customer_data.get('customer_segment', 'new'),
                customer_data.get('status', 'active')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"고객 추가 실패: {e}")
            return False
    
    def add_purchase(self, purchase_data: Dict) -> bool:
        """구매 기록 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO purchases 
                (customer_id, purchase_date, amount, product_category, payment_method, store_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                purchase_data.get('customer_id'),
                purchase_data.get('purchase_date', datetime.now()),
                purchase_data.get('amount'),
                purchase_data.get('product_category'),
                purchase_data.get('payment_method'),
                purchase_data.get('store_id')
            ))
            
            # 고객 총 구매액 업데이트
            cursor.execute('''
                UPDATE customers 
                SET total_spent = total_spent + ?, 
                    last_visit = ?,
                    total_visits = total_visits + 1
                WHERE customer_id = ?
            ''', (
                purchase_data.get('amount', 0),
                purchase_data.get('purchase_date', datetime.now()),
                purchase_data.get('customer_id')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"구매 기록 추가 실패: {e}")
            return False
    
    def add_behavior(self, behavior_data: Dict) -> bool:
        """고객 행동 기록 추가"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO customer_behavior 
                (customer_id, action_type, action_date, session_duration, pages_visited, device_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                behavior_data.get('customer_id'),
                behavior_data.get('action_type'),
                behavior_data.get('action_date', datetime.now()),
                behavior_data.get('session_duration', 0),
                behavior_data.get('pages_visited', 0),
                behavior_data.get('device_type')
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"행동 기록 추가 실패: {e}")
            return False
    
    def get_customer_metrics(self, days: int = 30) -> Dict:
        """고객 지표 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            # 총 고객 수
            cursor.execute('SELECT COUNT(*) FROM customers WHERE status = "active"')
            total_customers = cursor.fetchone()[0]
            
            # 신규 고객 수
            cursor.execute('SELECT COUNT(*) FROM customers WHERE registration_date >= ?', (since_date,))
            new_customers = cursor.fetchone()[0]
            
            # 활성 고객 수 (최근 30일 내 구매)
            cursor.execute('''
                SELECT COUNT(DISTINCT customer_id) FROM purchases 
                WHERE purchase_date >= ?
            ''', (since_date,))
            active_customers = cursor.fetchone()[0]
            
            # 평균 구매 금액
            cursor.execute('''
                SELECT AVG(amount) FROM purchases 
                WHERE purchase_date >= ?
            ''', (since_date,))
            avg_purchase = cursor.fetchone()[0] or 0
            
            # 총 매출
            cursor.execute('''
                SELECT SUM(amount) FROM purchases 
                WHERE purchase_date >= ?
            ''', (since_date,))
            total_revenue = cursor.fetchone()[0] or 0
            
            # 고객 생애 가치 (CLV)
            cursor.execute('''
                SELECT AVG(total_spent) FROM customers 
                WHERE status = "active" AND total_visits > 0
            ''')
            avg_clv = cursor.fetchone()[0] or 0
            
            # 고객 이탈률
            cursor.execute('''
                SELECT COUNT(*) FROM customers 
                WHERE last_visit < ? AND status = "active"
            ''', (since_date,))
            churned_customers = cursor.fetchone()[0]
            churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0
            
            # 재구매율
            cursor.execute('''
                SELECT COUNT(DISTINCT customer_id) FROM purchases 
                WHERE customer_id IN (
                    SELECT customer_id FROM purchases 
                    WHERE purchase_date < ?
                ) AND purchase_date >= ?
            ''', (since_date, since_date))
            repeat_customers = cursor.fetchone()[0]
            repeat_rate = (repeat_customers / active_customers * 100) if active_customers > 0 else 0
            
            conn.close()
            
            return {
                'total_customers': total_customers,
                'new_customers': new_customers,
                'active_customers': active_customers,
                'avg_purchase': round(avg_purchase, 2),
                'total_revenue': round(total_revenue, 2),
                'avg_clv': round(avg_clv, 2),
                'churn_rate': round(churn_rate, 2),
                'repeat_rate': round(repeat_rate, 2),
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"고객 지표 조회 실패: {e}")
            return {}
    
    def get_customer_segments(self) -> List[Dict]:
        """고객 세그먼트 분석"""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # RFM 분석 (Recency, Frequency, Monetary)
            query = '''
                SELECT 
                    c.customer_id,
                    c.name,
                    c.total_visits as frequency,
                    c.total_spent as monetary,
                    julianday('now') - julianday(MAX(p.purchase_date)) as recency_days
                FROM customers c
                LEFT JOIN purchases p ON c.customer_id = p.customer_id
                WHERE c.status = "active"
                GROUP BY c.customer_id
                HAVING recency_days IS NOT NULL
            '''
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                conn.close()
                return []
            
            # RFM 점수 계산
            df['recency_score'] = pd.qcut(df['recency_days'], 5, labels=[5,4,3,2,1])
            df['frequency_score'] = pd.qcut(df['frequency'], 5, labels=[1,2,3,4,5])
            df['monetary_score'] = pd.qcut(df['monetary'], 5, labels=[1,2,3,4,5])
            
            # 세그먼트 분류
            def classify_segment(row):
                r, f, m = int(row['recency_score']), int(row['frequency_score']), int(row['monetary_score'])
                
                if r >= 4 and f >= 4 and m >= 4:
                    return 'Champions'
                elif r >= 3 and f >= 3 and m >= 3:
                    return 'Loyal Customers'
                elif r >= 4 and f <= 2 and m <= 2:
                    return 'New Customers'
                elif r <= 2 and f >= 3 and m >= 3:
                    return 'At Risk'
                elif r <= 2 and f <= 2 and m <= 2:
                    return 'Lost Customers'
                else:
                    return 'Potential Loyalists'
            
            df['segment'] = df.apply(classify_segment, axis=1)
            
            # 세그먼트별 통계
            segments = df.groupby('segment').agg({
                'customer_id': 'count',
                'monetary': 'mean',
                'frequency': 'mean',
                'recency_days': 'mean'
            }).round(2).reset_index()
            
            segments.columns = ['segment_name', 'customer_count', 'avg_value', 'avg_frequency', 'avg_recency']
            
            conn.close()
            return segments.to_dict('records')
            
        except Exception as e:
            logger.error(f"고객 세그먼트 분석 실패: {e}")
            return []
    
    def get_purchase_trends(self, days: int = 30) -> Dict:
        """구매 트렌드 분석"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            # 일별 매출 트렌드
            cursor.execute('''
                SELECT DATE(purchase_date) as date, SUM(amount) as revenue, COUNT(*) as orders
                FROM purchases 
                WHERE purchase_date >= ?
                GROUP BY DATE(purchase_date)
                ORDER BY date
            ''', (since_date,))
            
            daily_trends = cursor.fetchall()
            
            # 카테고리별 매출
            cursor.execute('''
                SELECT product_category, SUM(amount) as revenue, COUNT(*) as orders
                FROM purchases 
                WHERE purchase_date >= ?
                GROUP BY product_category
                ORDER BY revenue DESC
            ''', (since_date,))
            
            category_trends = cursor.fetchall()
            
            # 결제 방법별 분석
            cursor.execute('''
                SELECT payment_method, SUM(amount) as revenue, COUNT(*) as orders
                FROM purchases 
                WHERE purchase_date >= ?
                GROUP BY payment_method
                ORDER BY revenue DESC
            ''', (since_date,))
            
            payment_trends = cursor.fetchall()
            
            conn.close()
            
            return {
                'daily_trends': [{'date': str(row[0]), 'revenue': row[1], 'orders': row[2]} for row in daily_trends],
                'category_trends': [{'category': row[0], 'revenue': row[1], 'orders': row[2]} for row in category_trends],
                'payment_trends': [{'method': row[0], 'revenue': row[1], 'orders': row[2]} for row in payment_trends]
            }
            
        except Exception as e:
            logger.error(f"구매 트렌드 분석 실패: {e}")
            return {}
    
    def get_behavior_insights(self, days: int = 30) -> Dict:
        """고객 행동 인사이트"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = datetime.now() - timedelta(days=days)
            
            # 평균 세션 시간
            cursor.execute('''
                SELECT AVG(session_duration) FROM customer_behavior 
                WHERE action_date >= ?
            ''', (since_date,))
            avg_session_duration = cursor.fetchone()[0] or 0
            
            # 평균 페이지 방문 수
            cursor.execute('''
                SELECT AVG(pages_visited) FROM customer_behavior 
                WHERE action_date >= ?
            ''', (since_date,))
            avg_pages_visited = cursor.fetchone()[0] or 0
            
            # 디바이스별 사용률
            cursor.execute('''
                SELECT device_type, COUNT(*) as count
                FROM customer_behavior 
                WHERE action_date >= ?
                GROUP BY device_type
                ORDER BY count DESC
            ''', (since_date,))
            
            device_usage = cursor.fetchall()
            
            # 행동 패턴 분석
            cursor.execute('''
                SELECT action_type, COUNT(*) as count
                FROM customer_behavior 
                WHERE action_date >= ?
                GROUP BY action_type
                ORDER BY count DESC
            ''', (since_date,))
            
            action_patterns = cursor.fetchall()
            
            conn.close()
            
            return {
                'avg_session_duration': round(avg_session_duration, 2),
                'avg_pages_visited': round(avg_pages_visited, 2),
                'device_usage': [{'device': row[0], 'count': row[1]} for row in device_usage],
                'action_patterns': [{'action': row[0], 'count': row[1]} for row in action_patterns]
            }
            
        except Exception as e:
            logger.error(f"행동 인사이트 분석 실패: {e}")
            return {}
    
    def generate_customer_report(self, days: int = 30) -> Dict:
        """고객 분석 종합 리포트 생성"""
        try:
            metrics = self.get_customer_metrics(days)
            segments = self.get_customer_segments()
            trends = self.get_purchase_trends(days)
            behavior = self.get_behavior_insights(days)
            
            return {
                'period': f"{days}일",
                'generated_at': datetime.now().isoformat(),
                'metrics': metrics,
                'segments': segments,
                'trends': trends,
                'behavior': behavior,
                'insights': self._generate_insights(metrics, segments, trends, behavior)
            }
            
        except Exception as e:
            logger.error(f"고객 리포트 생성 실패: {e}")
            return {}
    
    def _generate_insights(self, metrics: Dict, segments: List[Dict], trends: Dict, behavior: Dict) -> List[str]:
        """인사이트 생성"""
        insights = []
        
        # 고객 증가율
        if metrics.get('new_customers', 0) > 0:
            growth_rate = (metrics['new_customers'] / metrics['total_customers'] * 100) if metrics['total_customers'] > 0 else 0
            insights.append(f"고객 증가율: {growth_rate:.1f}% ({metrics['new_customers']}명 신규 가입)")
        
        # 이탈률 경고
        if metrics.get('churn_rate', 0) > 10:
            insights.append(f"⚠️ 고객 이탈률이 높습니다: {metrics['churn_rate']:.1f}%")
        elif metrics.get('churn_rate', 0) < 5:
            insights.append(f"✅ 고객 이탈률이 낮습니다: {metrics['churn_rate']:.1f}%")
        
        # 재구매율 분석
        if metrics.get('repeat_rate', 0) > 50:
            insights.append(f"✅ 고객 충성도가 높습니다: 재구매율 {metrics['repeat_rate']:.1f}%")
        elif metrics.get('repeat_rate', 0) < 30:
            insights.append(f"⚠️ 고객 충성도 개선 필요: 재구매율 {metrics['repeat_rate']:.1f}%")
        
        # 세그먼트 분석
        if segments:
            champions = next((s for s in segments if s['segment_name'] == 'Champions'), None)
            if champions and champions['customer_count'] > 0:
                insights.append(f"💎 VIP 고객: {champions['customer_count']}명 (평균 구매액: {champions['avg_value']:.0f}원)")
        
        return insights
