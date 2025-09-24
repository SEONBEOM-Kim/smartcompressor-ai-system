#!/usr/bin/env python3
"""
알림 시스템 테스트 스크립트
Slack과 Discord 스타일의 실시간 커뮤니케이션 시스템 테스트
"""

import requests
import time
import json
import random
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/notifications"

def test_notification_status():
    """알림 서비스 상태 테스트"""
    print("🧪 알림 서비스 상태 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/status")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 알림 서비스 상태 조회 성공")
            print(f"   - 서비스 상태: {data.get('status', {}).get('status', 'unknown')}")
            print(f"   - 활성 채널: {len(data.get('status', {}).get('channels', []))}")
            print(f"   - 큐 크기: {data.get('status', {}).get('queue_size', 0)}")
            return True
        else:
            print(f"❌ 알림 서비스 상태 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 알림 서비스 상태 테스트 오류: {e}")
        return False

def test_channels():
    """알림 채널 테스트"""
    print("🧪 알림 채널 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/channels")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 알림 채널 조회 성공")
            print(f"   - 총 채널 수: {data.get('channels', {}).get('total_channels', 0)}")
            
            channels = data.get('channels', {}).get('channels', {})
            for name, info in channels.items():
                print(f"   - {name}: {info.get('status', 'unknown')}")
            
            return True
        else:
            print(f"❌ 알림 채널 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 알림 채널 테스트 오류: {e}")
        return False

def test_channel_testing():
    """채널 테스트 기능 테스트"""
    print("🧪 채널 테스트 기능 테스트 시작...")
    
    try:
        # WebSocket 채널 테스트
        response = requests.post(f"{API_BASE}/test/websocket")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WebSocket 채널 테스트 성공")
            print(f"   - 결과: {data.get('message', 'unknown')}")
        else:
            print(f"❌ WebSocket 채널 테스트 실패: {response.status_code}")
            return False
        
        # 이메일 채널 테스트 (있는 경우)
        response = requests.post(f"{API_BASE}/test/email")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 이메일 채널 테스트 성공")
            print(f"   - 결과: {data.get('message', 'unknown')}")
        else:
            print("⚠️ 이메일 채널 테스트 실패 (설정되지 않음)")
        
        return True
        
    except Exception as e:
        print(f"❌ 채널 테스트 기능 테스트 오류: {e}")
        return False

def test_send_notification():
    """알림 전송 테스트"""
    print("🧪 알림 전송 테스트 시작...")
    
    try:
        notification_data = {
            "type": "general",
            "content": "테스트 알림 메시지입니다.",
            "channels": ["websocket"],
            "priority": "normal"
        }
        
        response = requests.post(f"{API_BASE}/send", json=notification_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 알림 전송 성공")
            print(f"   - 결과: {data.get('message', 'unknown')}")
            return True
        else:
            print(f"❌ 알림 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 알림 전송 테스트 오류: {e}")
        return False

def test_emergency_alert():
    """긴급 알림 테스트"""
    print("🧪 긴급 알림 테스트 시작...")
    
    try:
        alert_data = {
            "alert_data": {
                "message": "긴급 상황이 발생했습니다!",
                "severity": "high",
                "location": "테스트 매장",
                "timestamp": datetime.now().isoformat()
            },
            "channels": ["websocket", "slack", "discord"]
        }
        
        response = requests.post(f"{API_BASE}/emergency", json=alert_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 긴급 알림 전송 성공")
            print(f"   - 결과: {data.get('message', 'unknown')}")
            return True
        else:
            print(f"❌ 긴급 알림 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 긴급 알림 테스트 오류: {e}")
        return False

def test_equipment_alert():
    """장비 알림 테스트"""
    print("🧪 장비 알림 테스트 시작...")
    
    try:
        equipment_data = {
            "equipment_data": {
                "equipment_name": "냉동고 #1",
                "equipment_id": "freezer_001",
                "status": "error",
                "message": "온도가 비정상적으로 높습니다.",
                "temperature": 25.5,
                "timestamp": datetime.now().isoformat()
            },
            "user_email": "test@example.com",
            "user_kakao_id": "test_user_001"
        }
        
        response = requests.post(f"{API_BASE}/equipment", json=equipment_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 장비 알림 전송 성공")
            print(f"   - 결과: {data.get('message', 'unknown')}")
            return True
        else:
            print(f"❌ 장비 알림 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 장비 알림 테스트 오류: {e}")
        return False

def test_order_notification():
    """주문 알림 테스트"""
    print("🧪 주문 알림 테스트 시작...")
    
    try:
        order_data = {
            "order_data": {
                "order_id": f"order_{int(time.time())}",
                "order_number": f"ORD-{int(time.time())}",
                "customer_name": "테스트 고객",
                "customer_phone": "010-1234-5678",
                "items": [
                    {
                        "name": "바닐라 아이스크림",
                        "quantity": 2,
                        "price": 5000
                    }
                ],
                "total_amount": 10000,
                "timestamp": datetime.now().isoformat()
            },
            "user_email": "test@example.com",
            "user_kakao_id": "test_user_001"
        }
        
        response = requests.post(f"{API_BASE}/order", json=order_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 주문 알림 전송 성공")
            print(f"   - 결과: {data.get('message', 'unknown')}")
            return True
        else:
            print(f"❌ 주문 알림 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 주문 알림 테스트 오류: {e}")
        return False

def test_notification_history():
    """알림 히스토리 테스트"""
    print("🧪 알림 히스토리 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/history?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 알림 히스토리 조회 성공")
            print(f"   - 히스토리 수: {len(data.get('history', []))}")
            
            for notification in data.get('history', [])[:3]:
                print(f"   - {notification.get('sent_at')}: {notification.get('content', '')[:50]}...")
            
            return True
        else:
            print(f"❌ 알림 히스토리 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 알림 히스토리 테스트 오류: {e}")
        return False

def test_kakao_business():
    """카카오톡 비즈니스 API 테스트"""
    print("🧪 카카오톡 비즈니스 API 테스트 시작...")
    
    try:
        # 사용자 등록
        user_data = {
            "user_id": f"test_user_{int(time.time())}",
            "kakao_id": f"kakao_{int(time.time())}",
            "nickname": "테스트 사용자",
            "phone": "010-1234-5678",
            "email": "test@example.com"
        }
        
        response = requests.post(f"{API_BASE}/kakao/register", json=user_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 카카오톡 사용자 등록 성공")
            print(f"   - 사용자 ID: {data.get('user_id', 'unknown')}")
        else:
            print(f"❌ 카카오톡 사용자 등록 실패: {response.status_code}")
            return False
        
        # 메시지 전송
        message_data = {
            "user_id": user_data["user_id"],
            "message_type": "text",
            "content": "카카오톡 테스트 메시지입니다.",
            "priority": "normal"
        }
        
        response = requests.post(f"{API_BASE}/kakao/send", json=message_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 카카오톡 메시지 전송 성공")
            print(f"   - 결과: {data.get('message', 'unknown')}")
            return True
        else:
            print(f"❌ 카카오톡 메시지 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 카카오톡 비즈니스 API 테스트 오류: {e}")
        return False

def test_sms_notification():
    """SMS 알림 테스트"""
    print("🧪 SMS 알림 테스트 시작...")
    
    try:
        # SMS 전송
        sms_data = {
            "to": "010-1234-5678",
            "content": "SMS 테스트 메시지입니다.",
            "provider": "twilio",
            "priority": "normal"
        }
        
        response = requests.post(f"{API_BASE}/sms/send", json=sms_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SMS 전송 성공")
            print(f"   - 메시지 ID: {data.get('message_id', 'unknown')}")
            print(f"   - 상태: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ SMS 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SMS 알림 테스트 오류: {e}")
        return False

def test_email_templates():
    """이메일 템플릿 테스트"""
    print("🧪 이메일 템플릿 테스트 시작...")
    
    try:
        # 템플릿 목록 조회
        response = requests.get(f"{API_BASE}/email/templates")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 이메일 템플릿 목록 조회 성공")
            print(f"   - 템플릿 수: {len(data.get('templates', []))}")
            
            for template in data.get('templates', [])[:3]:
                print(f"   - {template.get('template_id')}: {template.get('name')}")
            
            return True
        else:
            print(f"❌ 이메일 템플릿 목록 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 이메일 템플릿 테스트 오류: {e}")
        return False

def test_sms_statistics():
    """SMS 통계 테스트"""
    print("🧪 SMS 통계 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/sms/statistics")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SMS 통계 조회 성공")
            
            stats = data.get('statistics', {})
            print(f"   - 총 메시지 수: {stats.get('total_messages', 0)}")
            print(f"   - 성공률: {stats.get('success_rate', 0):.1f}%")
            print(f"   - 총 비용: ${stats.get('total_cost', 0):.2f}")
            
            return True
        else:
            print(f"❌ SMS 통계 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ SMS 통계 테스트 오류: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 알림 시스템 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("알림 서비스 상태", test_notification_status),
        ("알림 채널", test_channels),
        ("채널 테스트", test_channel_testing),
        ("알림 전송", test_send_notification),
        ("긴급 알림", test_emergency_alert),
        ("장비 알림", test_equipment_alert),
        ("주문 알림", test_order_notification),
        ("알림 히스토리", test_notification_history),
        ("카카오톡 비즈니스", test_kakao_business),
        ("SMS 알림", test_sms_notification),
        ("이메일 템플릿", test_email_templates),
        ("SMS 통계", test_sms_statistics)
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
        print("🎉 모든 테스트 통과! 알림 시스템이 정상 작동합니다.")
    else:
        print("⚠️ 일부 테스트 실패. 시스템을 점검해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/api/notifications/status", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행 중이지 않습니다. 먼저 Flask 서버를 시작해주세요.")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ 서버에 연결할 수 없습니다. 먼저 Flask 서버를 시작해주세요.")
        exit(1)
    
    # 테스트 실행
    run_all_tests()
