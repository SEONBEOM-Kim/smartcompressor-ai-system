#!/usr/bin/env python3
"""
관리자 시스템 테스트 스크립트
AWS Management Console & GitHub 벤치마킹한 서비스 운영 관리 시스템을 테스트합니다.
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta

# 서버 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/admin"

def print_section(title):
    """섹션 제목을 출력합니다."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_test(test_name, success, message=""):
    """테스트 결과를 출력합니다."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"    {message}")

def test_api_endpoint(method, endpoint, data=None, expected_status=200):
    """API 엔드포인트를 테스트합니다."""
    try:
        url = f"{API_BASE}{endpoint}"
        
        if method.upper() == "GET":
            response = requests.get(url, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            return False, f"지원하지 않는 HTTP 메서드: {method}"
        
        success = response.status_code == expected_status
        message = f"Status: {response.status_code}"
        
        if success and response.content:
            try:
                json_data = response.json()
                if 'message' in json_data:
                    message += f", Message: {json_data['message']}"
            except:
                pass
        
        return success, message
        
    except requests.exceptions.ConnectionError:
        return False, "서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요."
    except requests.exceptions.Timeout:
        return False, "요청 시간 초과"
    except Exception as e:
        return False, f"오류: {str(e)}"

def test_system_overview():
    """시스템 개요 테스트"""
    print_section("시스템 개요 테스트")
    
    # 개요 데이터 조회
    success, message = test_api_endpoint("GET", "/overview")
    print_test("시스템 개요 조회", success, message)
    
    return success

def test_store_management():
    """매장 관리 테스트"""
    print_section("매장 관리 테스트")
    
    # 매장 목록 조회
    success1, message1 = test_api_endpoint("GET", "/stores")
    print_test("매장 목록 조회", success1, message1)
    
    # 새 매장 생성
    store_data = {
        "name": "테스트 매장",
        "owner_name": "홍길동",
        "owner_email": "test@example.com",
        "owner_phone": "010-1234-5678",
        "address": "서울시 강남구 테스트로 123",
        "city": "서울",
        "state": "강남구",
        "zip_code": "12345",
        "type": "unmanned_ice_cream"
    }
    success2, message2 = test_api_endpoint("POST", "/stores", store_data, 201)
    print_test("매장 생성", success2, message2)
    
    return success1 and success2

def test_user_management():
    """사용자 관리 테스트"""
    print_section("사용자 관리 테스트")
    
    # 사용자 목록 조회
    success1, message1 = test_api_endpoint("GET", "/users")
    print_test("사용자 목록 조회", success1, message1)
    
    # 새 사용자 생성
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "full_name": "테스트 사용자",
        "role": "store_owner",
        "password": "testpassword123",
        "phone": "010-9876-5432"
    }
    success2, message2 = test_api_endpoint("POST", "/users", user_data, 201)
    print_test("사용자 생성", success2, message2)
    
    return success1 and success2

def test_monitoring():
    """서비스 모니터링 테스트"""
    print_section("서비스 모니터링 테스트")
    
    # 모니터링 데이터 조회
    success1, message1 = test_api_endpoint("GET", "/monitoring")
    print_test("모니터링 데이터 조회", success1, message1)
    
    # 서비스 상태 조회
    success2, message2 = test_api_endpoint("GET", "/monitoring/services")
    print_test("서비스 상태 조회", success2, message2)
    
    # 시스템 메트릭 조회
    success3, message3 = test_api_endpoint("GET", "/monitoring/metrics")
    print_test("시스템 메트릭 조회", success3, message3)
    
    return success1 and success2 and success3

def test_log_management():
    """로그 관리 테스트"""
    print_section("로그 관리 테스트")
    
    # 로그 조회
    success1, message1 = test_api_endpoint("GET", "/logs")
    print_test("로그 조회", success1, message1)
    
    # 로그 내보내기
    export_data = {
        "filters": {
            "level": "ERROR",
            "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
            "end_time": datetime.now().isoformat()
        },
        "format": "csv"
    }
    success2, message2 = test_api_endpoint("POST", "/logs/export", export_data)
    print_test("로그 내보내기", success2, message2)
    
    # 로그 정리
    cleanup_data = {
        "days_to_keep": 30
    }
    success3, message3 = test_api_endpoint("POST", "/logs/cleanup", cleanup_data)
    print_test("로그 정리", success3, message3)
    
    return success1 and success2 and success3

def test_ticket_system():
    """고객 지원 티켓 시스템 테스트"""
    print_section("고객 지원 티켓 시스템 테스트")
    
    # 티켓 목록 조회
    success1, message1 = test_api_endpoint("GET", "/tickets")
    print_test("티켓 목록 조회", success1, message1)
    
    # 새 티켓 생성
    ticket_data = {
        "title": "테스트 티켓",
        "description": "테스트용 티켓입니다.",
        "customer_name": "고객명",
        "customer_email": "customer@example.com",
        "priority": "medium",
        "category": "technical"
    }
    success2, message2 = test_api_endpoint("POST", "/tickets", ticket_data, 201)
    print_test("티켓 생성", success2, message2)
    
    return success1 and success2

def test_security_management():
    """보안 관리 테스트"""
    print_section("보안 관리 테스트")
    
    # 보안 데이터 조회
    success1, message1 = test_api_endpoint("GET", "/security")
    print_test("보안 데이터 조회", success1, message1)
    
    # 보안 이벤트 조회
    success2, message2 = test_api_endpoint("GET", "/security/events")
    print_test("보안 이벤트 조회", success2, message2)
    
    # 차단된 IP 조회
    success3, message3 = test_api_endpoint("GET", "/security/blocked-ips")
    print_test("차단된 IP 조회", success3, message3)
    
    # IP 차단 (테스트용)
    block_data = {
        "ip_address": "192.168.1.100",
        "reason": "테스트용 차단",
        "duration": 3600
    }
    success4, message4 = test_api_endpoint("POST", "/security/block-ip", block_data)
    print_test("IP 차단", success4, message4)
    
    return success1 and success2 and success3 and success4

def test_backup_management():
    """백업 관리 테스트"""
    print_section("백업 관리 테스트")
    
    # 백업 목록 조회
    success1, message1 = test_api_endpoint("GET", "/backups")
    print_test("백업 목록 조회", success1, message1)
    
    # 새 백업 생성
    backup_data = {
        "type": "full",
        "description": "테스트용 백업"
    }
    success2, message2 = test_api_endpoint("POST", "/backups", backup_data, 201)
    print_test("백업 생성", success2, message2)
    
    return success1 and success2

def test_performance_monitoring():
    """성능 모니터링 테스트"""
    print_section("성능 모니터링 테스트")
    
    # 성능 데이터 조회
    success1, message1 = test_api_endpoint("GET", "/performance")
    print_test("성능 데이터 조회", success1, message1)
    
    # 성능 메트릭 조회
    success2, message2 = test_api_endpoint("GET", "/performance/metrics")
    print_test("성능 메트릭 조회", success2, message2)
    
    # 성능 알림 조회
    success3, message3 = test_api_endpoint("GET", "/performance/alerts")
    print_test("성능 알림 조회", success3, message3)
    
    return success1 and success2 and success3

def test_admin_dashboard():
    """관리자 대시보드 페이지 테스트"""
    print_section("관리자 대시보드 페이지 테스트")
    
    try:
        response = requests.get(f"{BASE_URL}/admin", timeout=10)
        success = response.status_code == 200
        message = f"Status: {response.status_code}"
        print_test("관리자 대시보드 페이지", success, message)
        return success
    except Exception as e:
        print_test("관리자 대시보드 페이지", False, f"오류: {str(e)}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 관리자 시스템 테스트 시작")
    print(f"테스트 대상: {BASE_URL}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 응답하지 않습니다. 서버를 먼저 시작하세요.")
            sys.exit(1)
    except:
        print("❌ 서버에 연결할 수 없습니다. 서버를 먼저 시작하세요.")
        sys.exit(1)
    
    # 테스트 실행
    test_results = []
    
    test_results.append(("시스템 개요", test_system_overview()))
    test_results.append(("매장 관리", test_store_management()))
    test_results.append(("사용자 관리", test_user_management()))
    test_results.append(("서비스 모니터링", test_monitoring()))
    test_results.append(("로그 관리", test_log_management()))
    test_results.append(("고객 지원 티켓", test_ticket_system()))
    test_results.append(("보안 관리", test_security_management()))
    test_results.append(("백업 관리", test_backup_management()))
    test_results.append(("성능 모니터링", test_performance_monitoring()))
    test_results.append(("관리자 대시보드", test_admin_dashboard()))
    
    # 결과 요약
    print_section("테스트 결과 요약")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return 0
    else:
        print("⚠️  일부 테스트가 실패했습니다. 로그를 확인하세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
