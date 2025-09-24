#!/usr/bin/env python3
"""
Tesla App & Starbucks App 벤치마킹 점주용 모바일 앱 시스템 테스트
"""

import requests
import time
import json
import random
from datetime import datetime, timedelta

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/mobile_app"

def test_mobile_app_health():
    """모바일 앱 서비스 헬스 체크 테스트"""
    print("🧪 모바일 앱 서비스 헬스 체크 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 모바일 앱 서비스 헬스 체크 성공")
            print(f"   - 상태: {data.get('status', 'unknown')}")
            print(f"   - 서비스 수: {len(data.get('services', {}))}")
            return True
        else:
            print(f"❌ 모바일 앱 서비스 헬스 체크 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 모바일 앱 서비스 헬스 체크 테스트 오류: {e}")
        return False

def test_pwa_installation():
    """PWA 설치 테스트"""
    print("🧪 PWA 설치 테스트 시작...")
    
    try:
        data = {
            "user_id": "test_user_001"
        }
        
        response = requests.post(f"{API_BASE}/pwa/install", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ PWA 설치 테스트 성공")
                print(f"   - 사용자 ID: {result['data']['user_id']}")
                print(f"   - 설치 시간: {result['data']['installed_at']}")
                return True
            else:
                print(f"❌ PWA 설치 테스트 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ PWA 설치 테스트 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ PWA 설치 테스트 오류: {e}")
        return False

def test_offline_sync():
    """오프라인 동기화 테스트"""
    print("🧪 오프라인 동기화 테스트 시작...")
    
    try:
        # 오프라인 데이터 저장
        sync_data = {
            "data_type": "dashboard",
            "data": {
                "store_id": "store_001",
                "timestamp": datetime.now().isoformat(),
                "offline_actions": [
                    {"action": "diagnosis", "timestamp": datetime.now().isoformat()},
                    {"action": "payment", "amount": 15000, "timestamp": datetime.now().isoformat()}
                ]
            },
            "priority": 1
        }
        
        response = requests.post(f"{API_BASE}/offline/sync", json=sync_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 오프라인 동기화 테스트 성공")
                print(f"   - 데이터 ID: {result['data_id']}")
                return True
            else:
                print(f"❌ 오프라인 동기화 테스트 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 오프라인 동기화 테스트 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 오프라인 동기화 테스트 오류: {e}")
        return False

def test_push_notification_registration():
    """푸시 알림 구독 등록 테스트"""
    print("🧪 푸시 알림 구독 등록 테스트 시작...")
    
    try:
        data = {
            "user_id": "test_user_001",
            "subscription": {
                "endpoint": "https://fcm.googleapis.com/fcm/send/test-endpoint",
                "keys": {
                    "p256dh": "test-p256dh-key",
                    "auth": "test-auth-key"
                }
            }
        }
        
        response = requests.post(f"{API_BASE}/push/register", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 푸시 알림 구독 등록 테스트 성공")
                return True
            else:
                print(f"❌ 푸시 알림 구독 등록 테스트 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 푸시 알림 구독 등록 테스트 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 푸시 알림 구독 등록 테스트 오류: {e}")
        return False

def test_push_notification_test():
    """푸시 알림 테스트"""
    print("🧪 푸시 알림 테스트 시작...")
    
    try:
        # 진단 알림 테스트
        data = {
            "user_id": "test_user_001",
            "type": "diagnosis"
        }
        
        response = requests.post(f"{API_BASE}/push/test", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 푸시 알림 테스트 성공")
                return True
            else:
                print(f"❌ 푸시 알림 테스트 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 푸시 알림 테스트 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 푸시 알림 테스트 오류: {e}")
        return False

def test_real_time_monitoring():
    """실시간 모니터링 테스트"""
    print("🧪 실시간 모니터링 테스트 시작...")
    
    try:
        # 모니터링 상태 조회
        response = requests.get(f"{API_BASE}/monitoring/status")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 실시간 모니터링 상태 조회 성공")
                status = result['data']
                print(f"   - 모니터링 활성: {status.get('is_monitoring')}")
                print(f"   - 연결된 클라이언트: {status.get('connected_clients')}")
                print(f"   - 데이터 타입: {status.get('data_types')}")
                return True
            else:
                print(f"❌ 실시간 모니터링 상태 조회 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 실시간 모니터링 상태 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 실시간 모니터링 테스트 오류: {e}")
        return False

def test_remote_control_devices():
    """원격 제어 장비 목록 테스트"""
    print("🧪 원격 제어 장비 목록 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/control/devices")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 원격 제어 장비 목록 조회 성공")
                devices = result['data']
                print(f"   - 등록된 장비 수: {len(devices)}")
                for device in devices:
                    print(f"   - {device['device_id']}: {device['device_type']} ({device['status']})")
                return True
            else:
                print(f"❌ 원격 제어 장비 목록 조회 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 원격 제어 장비 목록 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 원격 제어 장비 목록 테스트 오류: {e}")
        return False

def test_remote_control_command():
    """원격 제어 명령 실행 테스트"""
    print("🧪 원격 제어 명령 실행 테스트 시작...")
    
    try:
        data = {
            "command": "start_compressor",
            "device_id": "compressor_001",
            "store_id": "store_001",
            "parameters": {
                "power_level": 80,
                "auto_mode": True
            },
            "executed_by": "test_user"
        }
        
        response = requests.post(f"{API_BASE}/control/command", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 원격 제어 명령 실행 테스트 성공")
                print(f"   - 명령 ID: {result['command_id']}")
                return result['command_id']
            else:
                print(f"❌ 원격 제어 명령 실행 테스트 실패: {result.get('error')}")
                return None
        else:
            print(f"❌ 원격 제어 명령 실행 테스트 실패: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 원격 제어 명령 실행 테스트 오류: {e}")
        return None

def test_payment_creation():
    """결제 생성 테스트"""
    print("🧪 결제 생성 테스트 시작...")
    
    try:
        data = {
            "store_id": "store_001",
            "amount": 15000,
            "currency": "KRW",
            "payment_method": "card",
            "customer_id": "customer_001",
            "order_id": f"order_{int(time.time())}",
            "metadata": {
                "product": "아이스크림",
                "quantity": 2
            }
        }
        
        response = requests.post(f"{API_BASE}/payments", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 결제 생성 테스트 성공")
                print(f"   - 거래 ID: {result['transaction_id']}")
                return result['transaction_id']
            else:
                print(f"❌ 결제 생성 테스트 실패: {result.get('error')}")
                return None
        else:
            print(f"❌ 결제 생성 테스트 실패: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 결제 생성 테스트 오류: {e}")
        return None

def test_payment_summary():
    """결제 요약 조회 테스트"""
    print("🧪 결제 요약 조회 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/payments/summary?store_id=store_001")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 결제 요약 조회 테스트 성공")
                summary = result['data']
                print(f"   - 총 매출: ₩{summary['total_amount']:,.0f}")
                print(f"   - 거래 수: {summary['transaction_count']}건")
                print(f"   - 성공 거래: {summary['successful_count']}건")
                print(f"   - 평균 금액: ₩{summary['average_amount']:,.0f}")
                return True
            else:
                print(f"❌ 결제 요약 조회 테스트 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 결제 요약 조회 테스트 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 결제 요약 조회 테스트 오류: {e}")
        return False

def test_payment_analytics():
    """결제 분석 테스트"""
    print("🧪 결제 분석 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/payments/analytics?store_id=store_001&days=7")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 결제 분석 테스트 성공")
                analytics = result['data']
                summary = analytics['summary']
                print(f"   - 총 매출: ₩{summary['total_revenue']:,.0f}")
                print(f"   - 성공률: {summary['success_rate']:.1f}%")
                print(f"   - 평균 거래: ₩{summary['average_transaction']:,.0f}")
                return True
            else:
                print(f"❌ 결제 분석 테스트 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 결제 분석 테스트 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 결제 분석 테스트 오류: {e}")
        return False

def test_real_time_payment_data():
    """실시간 결제 데이터 테스트"""
    print("🧪 실시간 결제 데이터 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/payments/real-time")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 실시간 결제 데이터 테스트 성공")
                data = result['data']
                print(f"   - 오늘 총 매출: ₩{data.get('today_total', 0):,.0f}")
                print(f"   - 오늘 거래 수: {data.get('today_count', 0)}건")
                print(f"   - 대기 중인 거래: {data.get('pending_count', 0)}건")
                return True
            else:
                print(f"❌ 실시간 결제 데이터 테스트 실패: {result.get('error')}")
                return False
        else:
            print(f"❌ 실시간 결제 데이터 테스트 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 실시간 결제 데이터 테스트 오류: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 Tesla App & Starbucks App 벤치마킹 점주용 모바일 앱 시스템 테스트 시작")
    print("=" * 80)
    
    tests = [
        ("모바일 앱 서비스 헬스 체크", test_mobile_app_health),
        ("PWA 설치", test_pwa_installation),
        ("오프라인 동기화", test_offline_sync),
        ("푸시 알림 구독 등록", test_push_notification_registration),
        ("푸시 알림 테스트", test_push_notification_test),
        ("실시간 모니터링", test_real_time_monitoring),
        ("원격 제어 장비 목록", test_remote_control_devices),
        ("원격 제어 명령 실행", test_remote_control_command),
        ("결제 생성", test_payment_creation),
        ("결제 요약 조회", test_payment_summary),
        ("결제 분석", test_payment_analytics),
        ("실시간 결제 데이터", test_real_time_payment_data)
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
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{test_name:30} : {status}")
        if success:
            passed += 1
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 테스트 통과! Tesla App & Starbucks App 벤치마킹 모바일 앱이 정상 작동합니다.")
    else:
        print("⚠️ 일부 테스트 실패. 시스템을 점검해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/api/mobile_app/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행 중이지 않습니다. 먼저 Flask 서버를 시작해주세요.")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ 서버에 연결할 수 없습니다. 먼저 Flask 서버를 시작해주세요.")
        exit(1)
    
    # 테스트 실행
    run_all_tests()
