#!/usr/bin/env python3
"""
대시보드 시스템 테스트 스크립트
Stripe Dashboard와 AWS CloudWatch 스타일의 대시보드 시스템 테스트
"""

import requests
import time
import json
import random
from datetime import datetime, timedelta

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/dashboard"

def test_dashboard_summary():
    """대시보드 요약 정보 테스트"""
    print("🧪 대시보드 요약 정보 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/summary")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 대시보드 요약 정보 조회 성공")
            print(f"   - 총 매장 수: {data.get('summary', {}).get('overview', {}).get('total_stores', 0)}")
            print(f"   - 온라인 디바이스: {data.get('summary', {}).get('overview', {}).get('online_compressors', 0)}")
            print(f"   - 경고 알림: {data.get('summary', {}).get('overview', {}).get('warning_alerts', 0)}")
            print(f"   - 에너지 비용: ₩{data.get('summary', {}).get('overview', {}).get('total_energy_cost', 0):,.0f}")
            return True
        else:
            print(f"❌ 대시보드 요약 정보 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 대시보드 요약 정보 테스트 오류: {e}")
        return False

def test_store_management():
    """매장 관리 테스트"""
    print("🧪 매장 관리 테스트 시작...")
    
    try:
        # 1. 매장 목록 조회
        print("   📋 매장 목록 조회...")
        response = requests.get(f"{API_BASE}/stores")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 매장 목록 조회 성공: {len(data.get('stores', []))}개 매장")
        else:
            print(f"   ❌ 매장 목록 조회 실패: {response.status_code}")
            return False
        
        # 2. 매장 추가
        print("   ➕ 매장 추가...")
        store_data = {
            "store_name": f"테스트 매장 {int(time.time())}",
            "store_type": "franchise",
            "owner_id": "test_owner_001",
            "address": "서울특별시 강남구 테헤란로 123",
            "city": "서울",
            "state": "서울특별시",
            "zip_code": "12345",
            "country": "KR",
            "phone": "02-1234-5678",
            "email": f"test{int(time.time())}@example.com"
        }
        
        response = requests.post(f"{API_BASE}/stores", json=store_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                store_id = data.get('store_id')
                print(f"   ✅ 매장 추가 성공: {store_id}")
                
                # 3. 매장 정보 조회
                print("   🔍 매장 정보 조회...")
                response = requests.get(f"{API_BASE}/stores/{store_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 매장 정보 조회 성공: {data.get('store', {}).get('store_name')}")
                else:
                    print(f"   ❌ 매장 정보 조회 실패: {response.status_code}")
                
                # 4. 매장 삭제
                print("   🗑️ 매장 삭제...")
                response = requests.delete(f"{API_BASE}/stores/{store_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print("   ✅ 매장 삭제 성공")
                    else:
                        print(f"   ❌ 매장 삭제 실패: {data.get('message')}")
                else:
                    print(f"   ❌ 매장 삭제 실패: {response.status_code}")
                
                return True
            else:
                print(f"   ❌ 매장 추가 실패: {data.get('error')}")
                return False
        else:
            print(f"   ❌ 매장 추가 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 매장 관리 테스트 오류: {e}")
        return False

def test_device_management():
    """디바이스 관리 테스트"""
    print("🧪 디바이스 관리 테스트 시작...")
    
    try:
        # 1. 디바이스 목록 조회
        print("   📋 디바이스 목록 조회...")
        response = requests.get(f"{API_BASE}/devices")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 디바이스 목록 조회 성공: {len(data.get('devices', []))}개 디바이스")
        else:
            print(f"   ❌ 디바이스 목록 조회 실패: {response.status_code}")
            return False
        
        # 2. 매장 목록 조회 (디바이스 추가용)
        response = requests.get(f"{API_BASE}/stores")
        if response.status_code != 200:
            print("   ❌ 매장 목록 조회 실패 (디바이스 추가용)")
            return False
        
        stores = response.json().get('stores', [])
        if not stores:
            print("   ⚠️ 매장이 없어서 디바이스 추가 테스트를 건너뜁니다.")
            return True
        
        store_id = stores[0]['store_id']
        
        # 3. 디바이스 추가
        print("   ➕ 디바이스 추가...")
        device_data = {
            "device_name": f"테스트 디바이스 {int(time.time())}",
            "store_id": store_id,
            "device_type": "compressor",
            "model": "SignalCraft-2024",
            "serial_number": f"SC{int(time.time())}"
        }
        
        response = requests.post(f"{API_BASE}/devices", json=device_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                device_id = data.get('device_id')
                print(f"   ✅ 디바이스 추가 성공: {device_id}")
                
                # 4. 디바이스 정보 조회
                print("   🔍 디바이스 정보 조회...")
                response = requests.get(f"{API_BASE}/devices/{device_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 디바이스 정보 조회 성공: {data.get('device', {}).get('device_name')}")
                else:
                    print(f"   ❌ 디바이스 정보 조회 실패: {response.status_code}")
                
                # 5. 디바이스 삭제
                print("   🗑️ 디바이스 삭제...")
                response = requests.delete(f"{API_BASE}/devices/{device_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print("   ✅ 디바이스 삭제 성공")
                    else:
                        print(f"   ❌ 디바이스 삭제 실패: {data.get('message')}")
                else:
                    print(f"   ❌ 디바이스 삭제 실패: {response.status_code}")
                
                return True
            else:
                print(f"   ❌ 디바이스 추가 실패: {data.get('error')}")
                return False
        else:
            print(f"   ❌ 디바이스 추가 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 디바이스 관리 테스트 오류: {e}")
        return False

def test_analytics():
    """분석 데이터 테스트"""
    print("🧪 분석 데이터 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/analytics?days=7")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 분석 데이터 조회 성공")
            
            analytics = data.get('analytics', {})
            print(f"   - 온도 데이터: {len(analytics.get('temperature', {}).get('values', []))}개")
            print(f"   - 진동 데이터: {len(analytics.get('vibration', {}).get('values', []))}개")
            print(f"   - 전력 데이터: {len(analytics.get('power', {}).get('values', []))}개")
            print(f"   - 이상 감지 데이터: {len(analytics.get('anomaly', {}).get('values', []))}개")
            
            trends = data.get('trends', [])
            print(f"   - 트렌드 분석: {len(trends)}개")
            
            patterns = data.get('patterns', [])
            print(f"   - 이상 패턴: {len(patterns)}개")
            
            performance = data.get('performance', [])
            print(f"   - 성능 메트릭: {len(performance)}개")
            
            return True
        else:
            print(f"❌ 분석 데이터 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 분석 데이터 테스트 오류: {e}")
        return False

def test_notifications():
    """알림 관리 테스트"""
    print("🧪 알림 관리 테스트 시작...")
    
    try:
        # 1. 알림 이력 조회
        print("   📋 알림 이력 조회...")
        response = requests.get(f"{API_BASE}/notifications?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 알림 이력 조회 성공: {len(data.get('notifications', []))}개")
        else:
            print(f"   ❌ 알림 이력 조회 실패: {response.status_code}")
            return False
        
        # 2. 알림 설정 조회
        print("   ⚙️ 알림 설정 조회...")
        response = requests.get(f"{API_BASE}/notification-settings")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 알림 설정 조회 성공")
            settings = data.get('settings', {})
            print(f"   - 이메일 알림: {settings.get('email_enabled', False)}")
            print(f"   - SMS 알림: {settings.get('sms_enabled', False)}")
            print(f"   - 조용한 시간: {settings.get('quiet_hours_start', 'N/A')} - {settings.get('quiet_hours_end', 'N/A')}")
        else:
            print(f"   ❌ 알림 설정 조회 실패: {response.status_code}")
            return False
        
        # 3. 알림 설정 업데이트
        print("   🔧 알림 설정 업데이트...")
        settings_data = {
            "email_enabled": True,
            "sms_enabled": False,
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "07:00",
            "max_notifications_per_hour": 5
        }
        
        response = requests.post(f"{API_BASE}/notification-settings", json=settings_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ 알림 설정 업데이트 성공")
            else:
                print(f"   ❌ 알림 설정 업데이트 실패: {data.get('message')}")
        else:
            print(f"   ❌ 알림 설정 업데이트 실패: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 알림 관리 테스트 오류: {e}")
        return False

def test_user_management():
    """사용자 관리 테스트"""
    print("🧪 사용자 관리 테스트 시작...")
    
    try:
        # 1. 사용자 목록 조회
        print("   📋 사용자 목록 조회...")
        response = requests.get(f"{API_BASE}/users")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 사용자 목록 조회 성공: {len(data.get('users', []))}명")
        else:
            print(f"   ❌ 사용자 목록 조회 실패: {response.status_code}")
            return False
        
        # 2. 사용자 생성
        print("   ➕ 사용자 생성...")
        user_data = {
            "username": f"testuser{int(time.time())}",
            "email": f"testuser{int(time.time())}@example.com",
            "full_name": "테스트 사용자",
            "password": "TestPassword123!",
            "role": "viewer"
        }
        
        response = requests.post(f"{API_BASE}/users", json=user_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_id = data.get('user_id')
                print(f"   ✅ 사용자 생성 성공: {user_id}")
                
                # 3. 사용자 정보 조회
                print("   🔍 사용자 정보 조회...")
                response = requests.get(f"{API_BASE}/users/{user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 사용자 정보 조회 성공: {data.get('user', {}).get('username')}")
                else:
                    print(f"   ❌ 사용자 정보 조회 실패: {response.status_code}")
                
                # 4. 사용자 삭제
                print("   🗑️ 사용자 삭제...")
                response = requests.delete(f"{API_BASE}/users/{user_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print("   ✅ 사용자 삭제 성공")
                    else:
                        print(f"   ❌ 사용자 삭제 실패: {data.get('message')}")
                else:
                    print(f"   ❌ 사용자 삭제 실패: {response.status_code}")
                
                return True
            else:
                print(f"   ❌ 사용자 생성 실패: {data.get('error')}")
                return False
        else:
            print(f"   ❌ 사용자 생성 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 사용자 관리 테스트 오류: {e}")
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
    print("🚀 대시보드 시스템 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("헬스 체크", test_health_check),
        ("대시보드 요약", test_dashboard_summary),
        ("매장 관리", test_store_management),
        ("디바이스 관리", test_device_management),
        ("분석 데이터", test_analytics),
        ("알림 관리", test_notifications),
        ("사용자 관리", test_user_management)
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
        print("🎉 모든 테스트 통과! 대시보드 시스템이 정상 작동합니다.")
    else:
        print("⚠️ 일부 테스트 실패. 시스템을 점검해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행 중이지 않습니다. 먼저 Flask 서버를 시작해주세요.")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ 서버에 연결할 수 없습니다. 먼저 Flask 서버를 시작해주세요.")
        exit(1)
    
    # 테스트 실행
    run_all_tests()
