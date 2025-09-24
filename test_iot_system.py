#!/usr/bin/env python3
"""
IoT 센서 시스템 통합 테스트
Tesla와 Nest 스타일의 센서 시스템 테스트
"""

import time
import json
import requests
import threading
import asyncio
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/iot"

def test_sensor_data_reception():
    """센서 데이터 수신 테스트"""
    print("🧪 센서 데이터 수신 테스트 시작...")
    
    # 테스트 센서 데이터
    test_data = {
        "device_id": "ESP32_TEST_001",
        "timestamp": time.time(),
        "temperature": -18.5,
        "vibration": {
            "x": 0.2,
            "y": 0.1,
            "z": 0.3
        },
        "power_consumption": 45.2,
        "audio_level": 150,
        "sensor_quality": 0.95
    }
    
    try:
        response = requests.post(f"{API_BASE}/sensors/data", json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 센서 데이터 수신 성공: {result['message']}")
            return True
        else:
            print(f"❌ 센서 데이터 수신 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 센서 데이터 수신 오류: {e}")
        return False

def test_device_health():
    """디바이스 건강 상태 테스트"""
    print("🧪 디바이스 건강 상태 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/sensors/health/ESP32_TEST_001")
        
        if response.status_code == 200:
            result = response.json()
            health = result['health']
            print(f"✅ 디바이스 건강 상태 조회 성공:")
            print(f"   - 상태: {health['status']}")
            print(f"   - 전체 건강도: {health['overall_health']:.1f}%")
            print(f"   - 온도 상태: {health['temperature_status']}")
            print(f"   - 진동 상태: {health['vibration_status']}")
            return True
        else:
            print(f"❌ 디바이스 건강 상태 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 디바이스 건강 상태 조회 오류: {e}")
        return False

def test_sensor_data_retrieval():
    """센서 데이터 조회 테스트"""
    print("🧪 센서 데이터 조회 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/sensors/data/ESP32_TEST_001?hours=1&limit=10")
        
        if response.status_code == 200:
            result = response.json()
            data = result['data']
            print(f"✅ 센서 데이터 조회 성공: {len(data)}개 데이터")
            if data:
                latest = data[0]
                print(f"   - 최신 온도: {latest['temperature']}°C")
                print(f"   - 최신 전력: {latest['power_consumption']}%")
            return True
        else:
            print(f"❌ 센서 데이터 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 센서 데이터 조회 오류: {e}")
        return False

def test_anomaly_detection():
    """이상 감지 테스트"""
    print("🧪 이상 감지 테스트 시작...")
    
    # 이상 데이터 전송
    anomaly_data = {
        "device_id": "ESP32_TEST_001",
        "timestamp": time.time(),
        "temperature": 5.0,  # 높은 온도 (이상)
        "vibration": {
            "x": 2.5,  # 높은 진동 (이상)
            "y": 1.8,
            "z": 2.1
        },
        "power_consumption": 95.0,  # 높은 전력 (이상)
        "audio_level": 1500,  # 높은 소음 (이상)
        "sensor_quality": 0.9
    }
    
    try:
        # 이상 데이터 전송
        response = requests.post(f"{API_BASE}/sensors/data", json=anomaly_data)
        
        if response.status_code == 200:
            print("✅ 이상 데이터 전송 성공")
            
            # 잠시 대기 (이상 감지 처리 시간)
            time.sleep(2)
            
            # 이상 감지 결과 조회
            response = requests.get(f"{API_BASE}/sensors/anomalies?device_id=ESP32_TEST_001&hours=1")
            
            if response.status_code == 200:
                result = response.json()
                anomalies = result['anomalies']
                print(f"✅ 이상 감지 결과 조회 성공: {len(anomalies)}개 이상 감지")
                
                for anomaly in anomalies[:3]:  # 최근 3개만 출력
                    print(f"   - {anomaly['anomaly_type']}: {anomaly['description']}")
                
                return True
            else:
                print(f"❌ 이상 감지 결과 조회 실패: {response.status_code} - {response.text}")
                return False
        else:
            print(f"❌ 이상 데이터 전송 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 이상 감지 테스트 오류: {e}")
        return False

def test_firmware_management():
    """펌웨어 관리 테스트"""
    print("🧪 펌웨어 관리 테스트 시작...")
    
    try:
        # 펌웨어 버전 조회
        response = requests.get(f"{API_BASE}/firmware/versions")
        
        if response.status_code == 200:
            result = response.json()
            versions = result['versions']
            print(f"✅ 펌웨어 버전 조회 성공: {len(versions)}개 버전")
            
            if versions:
                latest = versions[0]
                print(f"   - 최신 버전: {latest['version']}")
                print(f"   - 안정 버전: {latest['is_stable']}")
            
            return True
        else:
            print(f"❌ 펌웨어 버전 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 펌웨어 관리 테스트 오류: {e}")
        return False

def test_system_status():
    """시스템 상태 테스트"""
    print("🧪 시스템 상태 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/sensors/status")
        
        if response.status_code == 200:
            result = response.json()
            system_status = result['system_status']
            
            print("✅ 시스템 상태 조회 성공:")
            print(f"   - 모니터링: {system_status['monitoring']['is_monitoring']}")
            print(f"   - 온라인 디바이스: {system_status['monitoring']['online_devices']}")
            print(f"   - 데이터베이스 크기: {system_status['database']['database_size_mb']:.2f}MB")
            print(f"   - 연결된 클라이언트: {system_status['streaming']['connected_clients']}")
            
            return True
        else:
            print(f"❌ 시스템 상태 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 시스템 상태 테스트 오류: {e}")
        return False

def test_continuous_data_stream():
    """연속 데이터 스트림 테스트"""
    print("🧪 연속 데이터 스트림 테스트 시작...")
    
    def send_continuous_data():
        """연속 데이터 전송"""
        for i in range(10):
            data = {
                "device_id": "ESP32_TEST_001",
                "timestamp": time.time(),
                "temperature": -20 + (i * 0.5),  # 온도 변화
                "vibration": {
                    "x": 0.1 + (i * 0.05),
                    "y": 0.1 + (i * 0.03),
                    "z": 0.1 + (i * 0.04)
                },
                "power_consumption": 40 + (i * 2),
                "audio_level": 100 + (i * 10),
                "sensor_quality": 0.95
            }
            
            try:
                response = requests.post(f"{API_BASE}/sensors/data", json=data)
                if response.status_code == 200:
                    print(f"   📊 데이터 전송 {i+1}/10: 온도 {data['temperature']:.1f}°C")
                else:
                    print(f"   ❌ 데이터 전송 실패 {i+1}/10")
            except Exception as e:
                print(f"   ❌ 데이터 전송 오류 {i+1}/10: {e}")
            
            time.sleep(1)  # 1초 간격
    
    try:
        # 백그라운드에서 연속 데이터 전송
        thread = threading.Thread(target=send_continuous_data)
        thread.start()
        
        # 데이터 전송 완료 대기
        thread.join()
        
        print("✅ 연속 데이터 스트림 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 연속 데이터 스트림 테스트 오류: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 IoT 센서 시스템 통합 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("센서 데이터 수신", test_sensor_data_reception),
        ("디바이스 건강 상태", test_device_health),
        ("센서 데이터 조회", test_sensor_data_retrieval),
        ("이상 감지", test_anomaly_detection),
        ("펌웨어 관리", test_firmware_management),
        ("시스템 상태", test_system_status),
        ("연속 데이터 스트림", test_continuous_data_stream)
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
        print("🎉 모든 테스트 통과! IoT 센서 시스템이 정상 작동합니다.")
    else:
        print("⚠️  일부 테스트 실패. 시스템을 점검해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/api/iot/sensors/status", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행 중이지 않습니다. 먼저 Flask 서버를 시작해주세요.")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ 서버에 연결할 수 없습니다. 먼저 Flask 서버를 시작해주세요.")
        exit(1)
    
    # 테스트 실행
    run_all_tests()
