#!/usr/bin/env python3
"""
제품 카탈로그 서비스
Uber Eats와 DoorDash 스타일의 제품 관리 시스템
"""

import time
import logging
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
# from sqlite3 import connect
import json
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductStatus(Enum):
    """제품 상태 열거형"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

class ProductCategory(Enum):
    """제품 카테고리 열거형"""
    NEW = "new"
    ICE_CREAM = "ice_cream"
    FROZEN = "frozen"
    BAKERY = "bakery"
    BEVERAGE = "beverage"
    DESSERT = "dessert"
    HEALTHY = "healthy"
    OTHER = "other"

class ProductBadge(Enum):
    """제품 배지 열거형"""
    NEW = "NEW"
    HOT = "HOT"
    BEST = "BEST"
    SALE = "SALE"
    LIMITED = "LIMITED"

@dataclass
class Product:
    """제품 정보"""
    id: str
    name: str
    description: str
    category: ProductCategory
    price: float
    original_price: float
    image_url: str
    rating: float
    review_count: int
    status: ProductStatus
    badge: Optional[ProductBadge]
    ingredients: List[str]
    allergens: List[str]
    nutrition_info: Dict
    preparation_time: int  # 분
    is_available: bool
    created_at: str
    updated_at: str

@dataclass
class ProductOption:
    """제품 옵션"""
    id: str
    product_id: str
    name: str
    type: str  # size, topping, flavor, etc.
    options: List[Dict]  # 옵션 목록
    required: bool
    max_selections: int

@dataclass
class ProductReview:
    """제품 리뷰"""
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    comment: str
    images: List[str]
    created_at: str

class ProductCatalogService:
    """제품 카탈로그 서비스 (Uber Eats & DoorDash 스타일)"""
    
    def __init__(self):
        self.conn = None # 데이터베이스 연결 객체 (PostgreSQL)
        self.products = {}
        self.categories = {}
        self.options = {}
        self.reviews = {}
        
        logger.info("제품 카탈로그 서비스 초기화 완료")

    def _init_database(self):
        """데이터베이스 초기화 (SQLite) - PostgreSQL로 마이그레이션 필요"""
        logger.warning("이 함수는 더 이상 사용되지 않습니다. PostgreSQL 연결을 사용해야 합니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 제품 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS products (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        category TEXT NOT NULL,
                        price REAL NOT NULL,
                        original_price REAL,
                        image_url TEXT NOT NULL,
                        rating REAL DEFAULT 0,
                        review_count INTEGER DEFAULT 0,
                        status TEXT NOT NULL,
                        badge TEXT,
                        ingredients TEXT DEFAULT '[]',
                        allergens TEXT DEFAULT '[]',
                        nutrition_info TEXT DEFAULT '{}',
                        preparation_time INTEGER DEFAULT 5,
                        is_available BOOLEAN DEFAULT 1,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # 제품 옵션 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS product_options (
                        id TEXT PRIMARY KEY,
                        product_id TEXT NOT NULL,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        options TEXT NOT NULL,
                        required BOOLEAN DEFAULT 0,
                        max_selections INTEGER DEFAULT 1,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                # 제품 리뷰 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS product_reviews (
                        id TEXT PRIMARY KEY,
                        product_id TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        user_name TEXT NOT NULL,
                        rating INTEGER NOT NULL,
                        comment TEXT,
                        images TEXT DEFAULT '[]',
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )
                ''')
                
                # 카테고리 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS categories (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        icon TEXT NOT NULL,
                        color TEXT NOT NULL,
                        description TEXT,
                        sort_order INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_status ON products(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_products_rating ON products(rating)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_options_product ON product_options(product_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_product_reviews_product ON product_reviews(product_id)')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
        """
        pass

    def _load_products(self):
        """제품 데이터 로드"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM products')
                
                for row in cursor.fetchall():
                    product = Product(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        category=ProductCategory(row[3]),
                        price=row[4],
                        original_price=row[5] or row[4],
                        image_url=row[6],
                        rating=row[7] or 0,
                        review_count=row[8] or 0,
                        status=ProductStatus(row[9]),
                        badge=ProductBadge(row[10]) if row[10] else None,
                        ingredients=json.loads(row[11]) if row[11] else [],
                        allergens=json.loads(row[12]) if row[12] else [],
                        nutrition_info=json.loads(row[13]) if row[13] else {},
                        preparation_time=row[14] or 5,
                        is_available=bool(row[15]),
                        created_at=row[16],
                        updated_at=row[17]
                    )
                    
                    self.products[product.id] = product
                
                logger.info(f"제품 데이터 로드 완료: {len(self.products)}개")
                
        except Exception as e:
            logger.error(f"제품 데이터 로드 실패: {e}")
        """
        pass

    def _load_categories(self):
        """카테고리 데이터 로드"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM categories ORDER BY sort_order')
                
                for row in cursor.fetchall():
                    category = {
                        'id': row[0],
                        'name': row[1],
                        'icon': row[2],
                        'color': row[3],
                        'description': row[4],
                        'sort_order': row[5],
                        'is_active': bool(row[6])
                    }
                    
                    self.categories[category['id']] = category
                
                logger.info(f"카테고리 데이터 로드 완료: {len(self.categories)}개")
                
        except Exception as e:
            logger.error(f"카테고리 데이터 로드 실패: {e}")
        """
        pass

    def _load_options(self):
        """제품 옵션 데이터 로드"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM product_options')
                
                for row in cursor.fetchall():
                    option = ProductOption(
                        id=row[0],
                        product_id=row[1],
                        name=row[2],
                        type=row[3],
                        options=json.loads(row[4]),
                        required=bool(row[5]),
                        max_selections=row[6] or 1
                    )
                    
                    self.options[option.id] = option
                
                logger.info(f"제품 옵션 데이터 로드 완료: {len(self.options)}개")
                
        except Exception as e:
            logger.error(f"제품 옵션 데이터 로드 실패: {e}")
        """
        pass

    def _load_reviews(self):
        """제품 리뷰 데이터 로드"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM product_reviews ORDER BY created_at DESC')
                
                for row in cursor.fetchall():
                    review = ProductReview(
                        id=row[0],
                        product_id=row[1],
                        user_id=row[2],
                        user_name=row[3],
                        rating=row[4],
                        comment=row[5] or '',
                        images=json.loads(row[6]) if row[6] else [],
                        created_at=row[7]
                    )
                    
                    self.reviews[review.id] = review
                
                logger.info(f"제품 리뷰 데이터 로드 완료: {len(self.reviews)}개")
                
        except Exception as e:
            logger.error(f"제품 리뷰 데이터 로드 실패: {e}")
        """
        pass

    def create_product(self, product_data: Dict) -> Tuple[bool, str]:
        """제품 생성"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            # 제품 ID 생성
            product_id = str(uuid.uuid4())
            
            # 제품 객체 생성
            product = Product(
                id=product_id,
                name=product_data['name'],
                description=product_data['description'],
                category=ProductCategory(product_data['category']),
                price=product_data['price'],
                original_price=product_data.get('original_price', product_data['price']),
                image_url=product_data['image_url'],
                rating=0.0,
                review_count=0,
                status=ProductStatus.ACTIVE,
                badge=ProductBadge(product_data['badge']) if product_data.get('badge') else None,
                ingredients=product_data.get('ingredients', []),
                allergens=product_data.get('allergens', []),
                nutrition_info=product_data.get('nutrition_info', {}),
                preparation_time=product_data.get('preparation_time', 5),
                is_available=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # 데이터베이스에 저장
            self._save_product(product)
            
            # 메모리에 추가
            self.products[product.id] = product
            
            logger.info(f"제품 생성 완료: {product.id} - {product.name}")
            return True, product_id
            
        except Exception as e:
            logger.error(f"제품 생성 실패: {e}")
            return False, str(e)
        """
        return False, "데이터베이스 연결이 구현되지 않았습니다."

    def update_product(self, product_id: str, updates: Dict) -> bool:
        """제품 정보 업데이트"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            if product_id not in self.products:
                return False
            
            product = self.products[product_id]
            
            # 업데이트할 필드들
            for field, value in updates.items():
                if hasattr(product, field):
                    if field == 'category':
                        setattr(product, field, ProductCategory(value))
                    elif field == 'status':
                        setattr(product, field, ProductStatus(value))
                    elif field == 'badge':
                        setattr(product, field, ProductBadge(value) if value else None)
                    else:
                        setattr(product, field, value)
            
            product.updated_at = datetime.now().isoformat()
            
            # 데이터베이스 업데이트
            self._save_product(product)
            
            logger.info(f"제품 정보 업데이트 완료: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"제품 정보 업데이트 실패: {e}")
            return False
        """
        return False

    def delete_product(self, product_id: str) -> bool:
        """제품 삭제"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            if product_id not in self.products:
                return False
            
            # 관련 데이터 삭제
            self._delete_product_options(product_id)
            self._delete_product_reviews(product_id)
            
            # 데이터베이스에서 삭제
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
                conn.commit()
            
            # 메모리에서 삭제
            del self.products[product_id]
            
            logger.info(f"제품 삭제 완료: {product_id}")
            return True
            
        except Exception as e:
            logger.error(f"제품 삭제 실패: {e}")
            return False
        """
        return False

    def get_product(self, product_id: str) -> Optional[Dict]:
        """제품 정보 조회"""
        if product_id in self.products:
            product = self.products[product_id]
            product_dict = asdict(product)
            product_dict['category'] = product.category.value
            product_dict['status'] = product.status.value
            product_dict['badge'] = product.badge.value if product.badge else None
            return product_dict
        return None

    def get_products_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """카테고리별 제품 목록 조회"""
        products = []
        for product in self.products.values():
            if product.category.value == category and product.status == ProductStatus.ACTIVE:
                product_dict = asdict(product)
                product_dict['category'] = product.category.value
                product_dict['status'] = product.status.value
                product_dict['badge'] = product.badge.value if product.badge else None
                products.append(product_dict)
                if len(products) >= limit:
                    break
        return products

    def get_recommended_products(self, limit: int = 10) -> List[Dict]:
        """추천 제품 목록 조회"""
        products = []
        for product in self.products.values():
            if product.status == ProductStatus.ACTIVE and product.is_available:
                product_dict = asdict(product)
                product_dict['category'] = product.category.value
                product_dict['status'] = product.status.value
                product_dict['badge'] = product.badge.value if product.badge else None
                products.append(product_dict)
        products.sort(key=lambda x: (x['rating'], x['review_count']), reverse=True)
        return products[:limit]

    def get_popular_products(self, limit: int = 10) -> List[Dict]:
        """인기 제품 목록 조회"""
        products = []
        for product in self.products.values():
            if product.status == ProductStatus.ACTIVE and product.is_available:
                product_dict = asdict(product)
                product_dict['category'] = product.category.value
                product_dict['status'] = product.status.value
                product_dict['badge'] = product.badge.value if product.badge else None
                products.append(product_dict)
        products.sort(key=lambda x: x['review_count'], reverse=True)
        return products[:limit]

    def search_products(self, query: str, limit: int = 20) -> List[Dict]:
        """제품 검색"""
        query = query.lower()
        products = []
        for product in self.products.values():
            if product.status == ProductStatus.ACTIVE and product.is_available:
                if (query in product.name.lower() or 
                    query in product.description.lower() or
                    any(query in ingredient.lower() for ingredient in product.ingredients)):
                    product_dict = asdict(product)
                    product_dict['category'] = product.category.value
                    product_dict['status'] = product.status.value
                    product_dict['badge'] = product.badge.value if product.badge else None
                    products.append(product_dict)
                    if len(products) >= limit:
                        break
        return products

    def get_product_options(self, product_id: str) -> List[Dict]:
        """제품 옵션 조회"""
        options = []
        for option in self.options.values():
            if option.product_id == product_id:
                option_dict = asdict(option)
                options.append(option_dict)
        return options

    def get_product_reviews(self, product_id: str, limit: int = 10) -> List[Dict]:
        """제품 리뷰 조회"""
        reviews = []
        for review in self.reviews.values():
            if review.product_id == product_id:
                review_dict = asdict(review)
                reviews.append(review_dict)
                if len(reviews) >= limit:
                    break
        return reviews

    def add_product_review(self, review_data: Dict) -> Tuple[bool, str]:
        """제품 리뷰 추가"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            # 리뷰 ID 생성
            review_id = str(uuid.uuid4())
            
            # 리뷰 객체 생성
            review = ProductReview(
                id=review_id,
                product_id=review_data['product_id'],
                user_id=review_data['user_id'],
                user_name=review_data['user_name'],
                rating=review_data['rating'],
                comment=review_data.get('comment', ''),
                images=review_data.get('images', []),
                created_at=datetime.now().isoformat()
            )
            
            # 데이터베이스에 저장
            self._save_product_review(review)
            
            # 메모리에 추가
            self.reviews[review.id] = review
            
            # 제품 평점 업데이트
            self._update_product_rating(review.product_id)
            
            logger.info(f"제품 리뷰 추가 완료: {review.id}")
            return True, review_id
            
        except Exception as e:
            logger.error(f"제품 리뷰 추가 실패: {e}")
            return False, str(e)
        """
        return False, "데이터베이스 연결이 구현되지 않았습니다."

    def get_categories(self) -> List[Dict]:
        """카테고리 목록 조회"""
        categories = []
        for category in self.categories.values():
            if category['is_active']:
                categories.append(category)
        return categories

    def _save_product(self, product: Product):
        """제품 저장"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO products 
                    (id, name, description, category, price, original_price, image_url, rating, review_count, 
                     status, badge, ingredients, allergens, nutrition_info, preparation_time, is_available, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    product.id,
                    product.name,
                    product.description,
                    product.category.value,
                    product.price,
                    product.original_price,
                    product.image_url,
                    product.rating,
                    product.review_count,
                    product.status.value,
                    product.badge.value if product.badge else None,
                    json.dumps(product.ingredients),
                    json.dumps(product.allergens),
                    json.dumps(product.nutrition_info),
                    product.preparation_time,
                    product.is_available,
                    product.created_at,
                    product.updated_at
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"제품 저장 실패: {e}")
        """
        pass

    def _save_product_review(self, review: ProductReview):
        """제품 리뷰 저장"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO product_reviews 
                    (id, product_id, user_id, user_name, rating, comment, images, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    review.id,
                    review.product_id,
                    review.user_id,
                    review.user_name,
                    review.rating,
                    review.comment,
                    json.dumps(review.images),
                    review.created_at
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"제품 리뷰 저장 실패: {e}")
        """
        pass

    def _update_product_rating(self, product_id: str):
        """제품 평점 업데이트"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            if product_id not in self.products:
                return
            
            # 해당 제품의 모든 리뷰 조회
            product_reviews = [review for review in self.reviews.values() if review.product_id == product_id]
            
            if not product_reviews:
                return
            
            # 평점 계산
            total_rating = sum(review.rating for review in product_reviews)
            average_rating = total_rating / len(product_reviews)
            
            # 제품 정보 업데이트
            product = self.products[product_id]
            product.rating = round(average_rating, 1)
            product.review_count = len(product_reviews)
            
            # 데이터베이스 업데이트
            self._save_product(product)
            
        except Exception as e:
            logger.error(f"제품 평점 업데이트 실패: {e}")
        """
        pass

    def _delete_product_options(self, product_id: str):
        """제품의 모든 옵션 삭제"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM product_options WHERE product_id = ?', (product_id,))
                conn.commit()
            
            # 메모리에서도 삭제
            options_to_remove = [option_id for option_id, option in self.options.items() 
                               if option.product_id == product_id]
            
            for option_id in options_to_remove:
                del self.options[option_id]
                
        except Exception as e:
            logger.error(f"제품 옵션 삭제 실패: {e}")
        """
        pass

    def _delete_product_reviews(self, product_id: str):
        """제품의 모든 리뷰 삭제"""
        logger.warning("데이터베이스 연결이 구현되지 않았습니다. 아래는 이전 SQLite 로직입니다.")
        """
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM product_reviews WHERE product_id = ?', (product_id,))
                conn.commit()
            
            # 메모리에서도 삭제
            reviews_to_remove = [review_id for review_id, review in self.reviews.items() 
                               if review.product_id == product_id]
            
            for review_id in reviews_to_remove:
                del self.reviews[review_id]
                
        except Exception as e:
            logger.error(f"제품 리뷰 삭제 실패: {e}")
        """
        pass

# 전역 서비스 인스턴스
product_catalog_service = ProductCatalogService()
