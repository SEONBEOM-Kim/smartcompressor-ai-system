#!/usr/bin/env python3
"""
모바일 앱 테스트 스크립트
Uber Eats와 DoorDash 스타일의 모바일 앱 테스트
"""

import requests
import time
import json
import random
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/mobile"

def test_categories():
    """카테고리 목록 테스트"""
    print("🧪 카테고리 목록 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/categories")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 카테고리 목록 조회 성공")
            print(f"   - 카테고리 수: {len(data.get('categories', []))}")
            
            for category in data.get('categories', [])[:3]:
                print(f"   - {category.get('name')}: {category.get('description')}")
            
            return True
        else:
            print(f"❌ 카테고리 목록 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 카테고리 목록 테스트 오류: {e}")
        return False

def test_recommended_products():
    """추천 제품 테스트"""
    print("🧪 추천 제품 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/products/recommended?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 추천 제품 조회 성공")
            print(f"   - 제품 수: {len(data.get('products', []))}")
            
            for product in data.get('products', [])[:3]:
                print(f"   - {product.get('name')}: ₩{product.get('price', 0):,}")
            
            return True
        else:
            print(f"❌ 추천 제품 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 추천 제품 테스트 오류: {e}")
        return False

def test_popular_products():
    """인기 제품 테스트"""
    print("🧪 인기 제품 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/products/popular?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 인기 제품 조회 성공")
            print(f"   - 제품 수: {len(data.get('products', []))}")
            
            for product in data.get('products', [])[:3]:
                print(f"   - {product.get('name')}: ₩{product.get('price', 0):,} (평점: {product.get('rating', 0)})")
            
            return True
        else:
            print(f"❌ 인기 제품 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 인기 제품 테스트 오류: {e}")
        return False

def test_product_search():
    """제품 검색 테스트"""
    print("🧪 제품 검색 테스트 시작...")
    
    try:
        search_queries = ['아이스크림', '초콜릿', '바닐라']
        
        for query in search_queries:
            response = requests.get(f"{API_BASE}/products/search?q={query}&limit=5")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ '{query}' 검색 성공: {len(data.get('products', []))}개 결과")
            else:
                print(f"❌ '{query}' 검색 실패: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 제품 검색 테스트 오류: {e}")
        return False

def test_product_detail():
    """제품 상세 정보 테스트"""
    print("🧪 제품 상세 정보 테스트 시작...")
    
    try:
        # 먼저 제품 목록을 가져와서 첫 번째 제품의 ID 사용
        response = requests.get(f"{API_BASE}/products/recommended?limit=1")
        
        if response.status_code != 200:
            print("❌ 제품 목록 조회 실패")
            return False
        
        products = response.json().get('products', [])
        if not products:
            print("❌ 제품이 없습니다")
            return False
        
        product_id = products[0]['id']
        
        # 제품 상세 정보 조회
        response = requests.get(f"{API_BASE}/products/{product_id}")
        
        if response.status_code == 200:
            data = response.json()
            product = data.get('product', {})
            print("✅ 제품 상세 정보 조회 성공")
            print(f"   - 제품명: {product.get('name')}")
            print(f"   - 가격: ₩{product.get('price', 0):,}")
            print(f"   - 평점: {product.get('rating', 0)}")
            print(f"   - 리뷰 수: {product.get('review_count', 0)}")
            return True
        else:
            print(f"❌ 제품 상세 정보 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 제품 상세 정보 테스트 오류: {e}")
        return False

def test_product_options():
    """제품 옵션 테스트"""
    print("🧪 제품 옵션 테스트 시작...")
    
    try:
        # 먼저 제품 목록을 가져와서 첫 번째 제품의 ID 사용
        response = requests.get(f"{API_BASE}/products/recommended?limit=1")
        
        if response.status_code != 200:
            print("❌ 제품 목록 조회 실패")
            return False
        
        products = response.json().get('products', [])
        if not products:
            print("❌ 제품이 없습니다")
            return False
        
        product_id = products[0]['id']
        
        # 제품 옵션 조회
        response = requests.get(f"{API_BASE}/products/{product_id}/options")
        
        if response.status_code == 200:
            data = response.json()
            options = data.get('options', [])
            print("✅ 제품 옵션 조회 성공")
            print(f"   - 옵션 수: {len(options)}")
            
            for option in options[:2]:
                print(f"   - {option.get('name')}: {len(option.get('options', []))}개 선택지")
            
            return True
        else:
            print(f"❌ 제품 옵션 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 제품 옵션 테스트 오류: {e}")
        return False

def test_create_order():
    """주문 생성 테스트"""
    print("🧪 주문 생성 테스트 시작...")
    
    try:
        # 먼저 제품 목록을 가져와서 주문 아이템 생성
        response = requests.get(f"{API_BASE}/products/recommended?limit=2")
        
        if response.status_code != 200:
            print("❌ 제품 목록 조회 실패")
            return False
        
        products = response.json().get('products', [])
        if len(products) < 2:
            print("❌ 주문할 제품이 부족합니다")
            return False
        
        # 주문 데이터 생성
        order_data = {
            "user_id": f"test_user_{int(time.time())}",
            "user_name": "테스트 사용자",
            "user_phone": "010-1234-5678",
            "user_email": "test@example.com",
            "store_id": "test_store_001",
            "store_name": "테스트 매장",
            "items": [
                {
                    "product_id": products[0]["id"],
                    "product_name": products[0]["name"],
                    "quantity": 2,
                    "unit_price": products[0]["price"],
                    "total_price": products[0]["price"] * 2,
                    "options": [],
                    "special_instructions": "테스트 주문입니다"
                },
                {
                    "product_id": products[1]["id"],
                    "product_name": products[1]["name"],
                    "quantity": 1,
                    "unit_price": products[1]["price"],
                    "total_price": products[1]["price"],
                    "options": [],
                    "special_instructions": ""
                }
            ],
            "subtotal": products[0]["price"] * 2 + products[1]["price"],
            "delivery_fee": 3000,
            "tax": 0,
            "total": products[0]["price"] * 2 + products[1]["price"] + 3000,
            "payment_method": "card",
            "special_instructions": "테스트 주문입니다"
        }
        
        # 주문 생성
        response = requests.post(f"{API_BASE}/orders", json=order_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                order_id = data.get('order_id')
                print("✅ 주문 생성 성공")
                print(f"   - 주문 ID: {order_id}")
                print(f"   - 주문 번호: {data.get('order', {}).get('order_number')}")
                print(f"   - 총 금액: ₩{data.get('order', {}).get('total', 0):,}")
                return order_id
            else:
                print(f"❌ 주문 생성 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 주문 생성 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 주문 생성 테스트 오류: {e}")
        return False

def test_order_tracking(order_id):
    """주문 추적 테스트"""
    print("🧪 주문 추적 테스트 시작...")
    
    try:
        if not order_id:
            print("❌ 주문 ID가 없습니다")
            return False
        
        response = requests.get(f"{API_BASE}/orders/{order_id}/tracking")
        
        if response.status_code == 200:
            data = response.json()
            tracking = data.get('tracking', [])
            print("✅ 주문 추적 조회 성공")
            print(f"   - 추적 이벤트 수: {len(tracking)}")
            
            for event in tracking[:3]:
                print(f"   - {event.get('timestamp')}: {event.get('message')}")
            
            return True
        else:
            print(f"❌ 주문 추적 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 주문 추적 테스트 오류: {e}")
        return False

def test_payment_processing(order_id):
    """결제 처리 테스트"""
    print("🧪 결제 처리 테스트 시작...")
    
    try:
        if not order_id:
            print("❌ 주문 ID가 없습니다")
            return False
        
        # 주문 정보 조회
        response = requests.get(f"{API_BASE}/orders/{order_id}")
        
        if response.status_code != 200:
            print("❌ 주문 정보 조회 실패")
            return False
        
        order = response.json().get('order', {})
        
        # 결제 데이터 생성
        payment_data = {
            "order_id": order_id,
            "payment_method": "card",
            "amount": order.get('total', 0)
        }
        
        # 결제 처리
        response = requests.post(f"{API_BASE}/payment/process", json=payment_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                payment = data.get('payment', {})
                print("✅ 결제 처리 성공")
                print(f"   - 결제 ID: {payment.get('payment_id')}")
                print(f"   - 거래 ID: {payment.get('transaction_id')}")
                print(f"   - 결제 금액: ₩{payment.get('amount', 0):,}")
                return True
            else:
                print(f"❌ 결제 처리 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 결제 처리 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 결제 처리 테스트 오류: {e}")
        return False

def test_notifications():
    """알림 테스트"""
    print("🧪 알림 테스트 시작...")
    
    try:
        # 푸시 알림 등록
        notification_data = {
            "user_id": f"test_user_{int(time.time())}",
            "device_token": f"test_token_{int(time.time())}",
            "platform": "web"
        }
        
        response = requests.post(f"{API_BASE}/notifications/register", json=notification_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 푸시 알림 등록 성공")
            else:
                print(f"❌ 푸시 알림 등록 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 푸시 알림 등록 실패: {response.status_code}")
            return False
        
        # 알림 전송
        send_data = {
            "user_id": notification_data["user_id"],
            "title": "테스트 알림",
            "message": "모바일 앱 테스트 알림입니다."
        }
        
        response = requests.post(f"{API_BASE}/notifications/send", json=send_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 알림 전송 성공")
                return True
            else:
                print(f"❌ 알림 전송 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 알림 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 알림 테스트 오류: {e}")
        return False

def test_health_check():
    """헬스 체크 테스트"""
    print("🧪 헬스 체크 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 헬스 체크 성공")
            print(f"   - 전체 상태: {data.get('status', 'unknown')}")
            
            services = data.get('services', {})
            for service, status in services.items():
                print(f"   - {service}: {status}")
            
            return True
        else:
            print(f"❌ 헬스 체크 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 헬스 체크 테스트 오류: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 모바일 앱 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("헬스 체크", test_health_check),
        ("카테고리 목록", test_categories),
        ("추천 제품", test_recommended_products),
        ("인기 제품", test_popular_products),
        ("제품 검색", test_product_search),
        ("제품 상세 정보", test_product_detail),
        ("제품 옵션", test_product_options),
        ("알림 시스템", test_notifications)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name} 테스트...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} 테스트 예외: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # 테스트 간 간격
    
    # 주문 관련 테스트 (순서대로 실행)
    print(f"\n🔍 주문 생성 테스트...")
    try:
        order_id = test_create_order()
        results.append(("주문 생성", order_id is not False))
        
        if order_id:
            print(f"\n🔍 주문 추적 테스트...")
            try:
                success = test_order_tracking(order_id)
                results.append(("주문 추적", success))
            except Exception as e:
                print(f"❌ 주문 추적 테스트 예외: {e}")
                results.append(("주문 추적", False))
            
            print(f"\n🔍 결제 처리 테스트...")
            try:
                success = test_payment_processing(order_id)
                results.append(("결제 처리", success))
            except Exception as e:
                print(f"❌ 결제 처리 테스트 예외: {e}")
                results.append(("결제 처리", False))
        else:
            results.append(("주문 추적", False))
            results.append(("결제 처리", False))
            
    except Exception as e:
        print(f"❌ 주문 생성 테스트 예외: {e}")
        results.append(("주문 생성", False))
        results.append(("주문 추적", False))
        results.append(("결제 처리", False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{test_name:20} : {status}")
        if success:
            passed += 1
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 모바일 앱이 정상 작동합니다.")
    else:
        print("⚠️ 일부 테스트 실패. 시스템을 점검해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/api/mobile/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행 중이지 않습니다. 먼저 Flask 서버를 시작해주세요.")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ 서버에 연결할 수 없습니다. 먼저 Flask 서버를 시작해주세요.")
        exit(1)
    
    # 테스트 실행
    run_all_tests()
