#!/usr/bin/env python3
"""
분석 시스템 테스트 스크립트
Google Analytics와 Mixpanel을 벤치마킹한 매장 운영 데이터 분석 시스템 테스트
"""

import requests
import time
import json
import random
from datetime import datetime, timedelta

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/analytics"

def test_analytics_health():
    """분석 서비스 헬스 체크 테스트"""
    print("🧪 분석 서비스 헬스 체크 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/health")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 분석 서비스 헬스 체크 성공")
            print(f"   - 상태: {data.get('status', 'unknown')}")
            print(f"   - 서비스 수: {len(data.get('services', {}))}")
            return True
        else:
            print(f"❌ 분석 서비스 헬스 체크 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 분석 서비스 헬스 체크 테스트 오류: {e}")
        return False

def test_event_tracking():
    """이벤트 추적 테스트 (Mixpanel 스타일)"""
    print("🧪 이벤트 추적 테스트 시작...")
    
    try:
        events = [
            {
                "event_name": "store_visit",
                "store_id": "store_001",
                "user_id": "user_001",
                "properties": {
                    "visit_duration": 300,
                    "page_views": 5,
                    "device": "mobile"
                }
            },
            {
                "event_name": "purchase",
                "store_id": "store_001",
                "user_id": "user_001",
                "properties": {
                    "amount": 15000,
                    "items": ["아이스크림", "음료"],
                    "payment_method": "card"
                }
            },
            {
                "event_name": "compressor_alert",
                "store_id": "store_001",
                "properties": {
                    "temperature": 25.5,
                    "efficiency": 0.75,
                    "severity": "warning"
                }
            }
        ]
        
        success_count = 0
        for event in events:
            response = requests.post(f"{API_BASE}/track-event", json=event)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    success_count += 1
                    print(f"   ✅ 이벤트 추적 성공: {event['event_name']}")
                else:
                    print(f"   ❌ 이벤트 추적 실패: {event['event_name']}")
            else:
                print(f"   ❌ 이벤트 추적 실패: {response.status_code}")
        
        print(f"✅ 이벤트 추적 테스트 완료: {success_count}/{len(events)} 성공")
        return success_count == len(events)
        
    except Exception as e:
        print(f"❌ 이벤트 추적 테스트 오류: {e}")
        return False

def test_store_metrics():
    """매장 지표 저장 테스트"""
    print("🧪 매장 지표 저장 테스트 시작...")
    
    try:
        # 테스트 데이터 생성
        test_metrics = []
        for i in range(10):
            timestamp = datetime.now() - timedelta(hours=i)
            test_metrics.append({
                "store_id": "store_001",
                "timestamp": timestamp.isoformat(),
                "revenue": random.randint(50000, 150000),
                "power_consumption": random.uniform(800, 1200),
                "compressor_efficiency": random.uniform(0.7, 0.95),
                "temperature": random.uniform(20, 30),
                "customer_count": random.randint(10, 50),
                "order_count": random.randint(5, 25),
                "maintenance_cost": random.randint(1000, 5000),
                "energy_cost": random.randint(5000, 15000)
            })
        
        success_count = 0
        for metrics in test_metrics:
            response = requests.post(f"{API_BASE}/store-metrics", json=metrics)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    success_count += 1
                else:
                    print(f"   ❌ 매장 지표 저장 실패: {data.get('error')}")
            else:
                print(f"   ❌ 매장 지표 저장 실패: {response.status_code}")
        
        print(f"✅ 매장 지표 저장 테스트 완료: {success_count}/{len(test_metrics)} 성공")
        return success_count == len(test_metrics)
        
    except Exception as e:
        print(f"❌ 매장 지표 저장 테스트 오류: {e}")
        return False

def test_store_performance_analysis():
    """매장 성능 분석 테스트"""
    print("🧪 매장 성능 분석 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/performance/store_001?days=7")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                performance_data = data.get('data', {})
                print("✅ 매장 성능 분석 성공")
                print(f"   - 매장 ID: {performance_data.get('store_id', 'unknown')}")
                print(f"   - 분석 기간: {performance_data.get('period', 'unknown')}")
                
                summary = performance_data.get('summary', {})
                print(f"   - 총 매출: {summary.get('total_revenue', 0):,.0f}원")
                print(f"   - 평균 효율성: {summary.get('avg_efficiency', 0):.1%}")
                print(f"   - 총 고객 수: {summary.get('total_customers', 0):,}명")
                
                return True
            else:
                print(f"❌ 매장 성능 분석 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 매장 성능 분석 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 매장 성능 분석 테스트 오류: {e}")
        return False

def test_compressor_efficiency_analysis():
    """압축기 효율성 분석 테스트"""
    print("🧪 압축기 효율성 분석 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/efficiency/store_001?days=7")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                efficiency_data = data.get('data', {})
                print("✅ 압축기 효율성 분석 성공")
                print(f"   - 매장 ID: {efficiency_data.get('store_id', 'unknown')}")
                
                metrics = efficiency_data.get('efficiency_metrics', {})
                print(f"   - 평균 효율성: {metrics.get('average', 0):.1%}")
                print(f"   - 최대 효율성: {metrics.get('maximum', 0):.1%}")
                print(f"   - 효율성 등급: {metrics.get('grade', 'unknown')}")
                
                return True
            else:
                print(f"❌ 압축기 효율성 분석 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 압축기 효율성 분석 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 압축기 효율성 분석 테스트 오류: {e}")
        return False

def test_power_optimization_analysis():
    """전력 최적화 분석 테스트"""
    print("🧪 전력 최적화 분석 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/power-optimization/store_001?days=7")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                power_data = data.get('data', {})
                print("✅ 전력 최적화 분석 성공")
                print(f"   - 매장 ID: {power_data.get('store_id', 'unknown')}")
                
                metrics = power_data.get('power_metrics', {})
                print(f"   - 평균 전력 사용량: {metrics.get('average', 0):.1f}W")
                print(f"   - 피크 전력 사용량: {metrics.get('peak', 0):.1f}W")
                
                cost_savings = power_data.get('cost_savings', {})
                print(f"   - 일일 절약 비용: ${cost_savings.get('daily_savings', 0):.2f}")
                print(f"   - 월간 절약 비용: ${cost_savings.get('monthly_savings', 0):.2f}")
                
                return True
            else:
                print(f"❌ 전력 최적화 분석 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 전력 최적화 분석 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 전력 최적화 분석 테스트 오류: {e}")
        return False

def test_maintenance_prediction():
    """유지보수 예측 테스트"""
    print("🧪 유지보수 예측 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/maintenance/predict/compressor_001?days_ahead=30")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                prediction = data.get('data', {})
                print("✅ 유지보수 예측 성공")
                print(f"   - 장비 ID: {prediction.get('equipment_id', 'unknown')}")
                print(f"   - 예상 고장일: {prediction.get('predicted_failure_date', 'unknown')}")
                print(f"   - 신뢰도: {prediction.get('confidence', 0):.1%}")
                print(f"   - 유지보수 타입: {prediction.get('maintenance_type', 'unknown')}")
                print(f"   - 우선순위: {prediction.get('priority', 'unknown')}")
                
                return True
            else:
                print(f"❌ 유지보수 예측 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 유지보수 예측 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 유지보수 예측 테스트 오류: {e}")
        return False

def test_maintenance_schedule():
    """유지보수 스케줄 조회 테스트"""
    print("🧪 유지보수 스케줄 조회 테스트 시작...")
    
    try:
        response = requests.get(f"{API_BASE}/maintenance/schedule?store_id=store_001&days_ahead=30")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                schedule = data.get('data', [])
                print("✅ 유지보수 스케줄 조회 성공")
                print(f"   - 예정된 유지보수 수: {len(schedule)}")
                
                for maintenance in schedule[:3]:
                    print(f"   - {maintenance.get('equipment_id')}: {maintenance.get('predicted_date')} ({maintenance.get('priority')})")
                
                return True
            else:
                print(f"❌ 유지보수 스케줄 조회 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 유지보수 스케줄 조회 실패: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 유지보수 스케줄 조회 테스트 오류: {e}")
        return False

def test_ab_test_creation():
    """A/B 테스트 생성 테스트"""
    print("🧪 A/B 테스트 생성 테스트 시작...")
    
    try:
        test_data = {
            "test_id": f"test_{int(time.time())}",
            "test_name": "압축기 효율성 개선 테스트",
            "description": "압축기 설정 변경이 효율성에 미치는 영향 테스트",
            "store_id": "store_001",
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "status": "draft",
            "variants": [
                {"name": "control", "weight": 1, "description": "기존 설정"},
                {"name": "treatment", "weight": 1, "description": "새로운 설정"}
            ],
            "primary_metric": "efficiency",
            "secondary_metrics": ["power_consumption", "customer_satisfaction"],
            "target_sample_size": 1000,
            "confidence_level": 0.95,
            "minimum_effect_size": 0.1
        }
        
        response = requests.post(f"{API_BASE}/ab-tests", json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ A/B 테스트 생성 성공")
                print(f"   - 테스트 ID: {test_data['test_id']}")
                print(f"   - 테스트명: {test_data['test_name']}")
                return test_data['test_id']
            else:
                print(f"❌ A/B 테스트 생성 실패: {data.get('error')}")
                return None
        else:
            print(f"❌ A/B 테스트 생성 실패: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ A/B 테스트 생성 테스트 오류: {e}")
        return None

def test_ab_test_workflow(test_id):
    """A/B 테스트 워크플로우 테스트"""
    print("🧪 A/B 테스트 워크플로우 테스트 시작...")
    
    try:
        if not test_id:
            print("❌ 테스트 ID가 없습니다")
            return False
        
        # 테스트 시작
        response = requests.post(f"{API_BASE}/ab-tests/{test_id}/start")
        if response.status_code != 200:
            print(f"❌ A/B 테스트 시작 실패: {response.status_code}")
            return False
        
        print("   ✅ A/B 테스트 시작 성공")
        
        # 사용자 할당
        user_ids = [f"user_{i:03d}" for i in range(10)]
        for user_id in user_ids:
            response = requests.post(f"{API_BASE}/ab-tests/{test_id}/assign", json={"user_id": user_id})
            if response.status_code == 200:
                data = response.json()
                variant = data.get('variant', 'unknown')
                print(f"   ✅ 사용자 할당: {user_id} -> {variant}")
        
        # 이벤트 추적
        for user_id in user_ids[:5]:
            events = [
                {"event_name": "conversion", "event_value": 1.0},
                {"event_name": "purchase", "event_value": random.randint(10000, 50000)}
            ]
            
            for event in events:
                response = requests.post(f"{API_BASE}/ab-tests/{test_id}/track", json={
                    "user_id": user_id,
                    "event_name": event["event_name"],
                    "event_value": event["event_value"]
                })
                if response.status_code == 200:
                    print(f"   ✅ 이벤트 추적: {user_id} - {event['event_name']}")
        
        # 결과 계산
        response = requests.post(f"{API_BASE}/ab-tests/{test_id}/calculate")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('data', [])
                print("   ✅ A/B 테스트 결과 계산 성공")
                for result in results:
                    print(f"   - {result['variant']}: 전환율 {result['conversion_rate']:.1%}, p-value {result['p_value']:.3f}")
        
        # 테스트 중지
        response = requests.post(f"{API_BASE}/ab-tests/{test_id}/stop")
        if response.status_code == 200:
            print("   ✅ A/B 테스트 중지 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ A/B 테스트 워크플로우 테스트 오류: {e}")
        return False

def test_report_creation():
    """리포트 생성 테스트"""
    print("🧪 리포트 생성 테스트 시작...")
    
    try:
        # 리포트 설정 생성
        report_config = {
            "report_id": f"report_{int(time.time())}",
            "report_name": "일일 매장 운영 리포트",
            "report_type": "daily",
            "store_ids": ["store_001"],
            "metrics": ["revenue", "efficiency", "power_consumption"],
            "recipients": ["admin@example.com"],
            "schedule": "daily",
            "format": "html",
            "is_active": True
        }
        
        response = requests.post(f"{API_BASE}/reports/config", json=report_config)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 리포트 설정 생성 성공")
                report_id = report_config['report_id']
                
                # 리포트 생성
                response = requests.post(f"{API_BASE}/reports/{report_id}/generate")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print("✅ 리포트 생성 성공")
                        report_data = data.get('data', {})
                        print(f"   - 리포트 ID: {report_data.get('report_id')}")
                        print(f"   - 생성 시간: {report_data.get('generated_at')}")
                        print(f"   - 인사이트 수: {len(report_data.get('insights', []))}")
                        return True
                    else:
                        print(f"❌ 리포트 생성 실패: {data.get('error')}")
                        return False
                else:
                    print(f"❌ 리포트 생성 실패: {response.status_code}")
                    return False
            else:
                print(f"❌ 리포트 설정 생성 실패: {data.get('error')}")
                return False
        else:
            print(f"❌ 리포트 설정 생성 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 리포트 생성 테스트 오류: {e}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 분석 시스템 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("분석 서비스 헬스 체크", test_analytics_health),
        ("이벤트 추적", test_event_tracking),
        ("매장 지표 저장", test_store_metrics),
        ("매장 성능 분석", test_store_performance_analysis),
        ("압축기 효율성 분석", test_compressor_efficiency_analysis),
        ("전력 최적화 분석", test_power_optimization_analysis),
        ("유지보수 예측", test_maintenance_prediction),
        ("유지보수 스케줄 조회", test_maintenance_schedule),
        ("리포트 생성", test_report_creation)
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
    
    # A/B 테스트 워크플로우 테스트
    print(f"\n🔍 A/B 테스트 생성 테스트...")
    try:
        test_id = test_ab_test_creation()
        if test_id:
            print(f"\n🔍 A/B 테스트 워크플로우 테스트...")
            try:
                success = test_ab_test_workflow(test_id)
                results.append(("A/B 테스트 워크플로우", success))
            except Exception as e:
                print(f"❌ A/B 테스트 워크플로우 테스트 예외: {e}")
                results.append(("A/B 테스트 워크플로우", False))
        else:
            results.append(("A/B 테스트 워크플로우", False))
    except Exception as e:
        print(f"❌ A/B 테스트 생성 테스트 예외: {e}")
        results.append(("A/B 테스트 워크플로우", False))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{test_name:30} : {status}")
        if success:
            passed += 1
    
    print(f"\n총 {total}개 테스트 중 {passed}개 통과 ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 분석 시스템이 정상 작동합니다.")
    else:
        print("⚠️ 일부 테스트 실패. 시스템을 점검해주세요.")
    
    return passed == total

if __name__ == "__main__":
    # 서버가 실행 중인지 확인
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/health", timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 실행 중이지 않습니다. 먼저 Flask 서버를 시작해주세요.")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ 서버에 연결할 수 없습니다. 먼저 Flask 서버를 시작해주세요.")
        exit(1)
    
    # 테스트 실행
    run_all_tests()
