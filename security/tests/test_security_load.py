#!/usr/bin/env python3
"""
보안 시스템 부하 테스트
높은 부하 상황에서의 보안 시스템 성능을 테스트합니다.
"""

import sys
import os
import unittest
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.authentication_service import authentication_service, AuthMethod, UserRole
from security.services.encryption_service import encryption_service, EncryptionType, KeyType
from security.services.privacy_service import privacy_service, PersonalDataType, ProcessingPurpose
from security.services.security_monitoring_service import security_monitoring_service, EventType, ThreatLevel
from security.services.intrusion_detection_service import intrusion_detection_service, AttackType
from security.services.backup_recovery_service import backup_recovery_service, BackupType, StorageType

class TestSecurityLoad(unittest.TestCase):
    """보안 시스템 부하 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_user_id = "load_test_user_001"
        self.test_username = "load_test_user"
        self.test_password = "load_test_password_123"
        self.test_ip = "192.168.1.100"
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.test_endpoint = "/api/load/test"
        self.test_data = b"Load test data for security system testing"
        
        # 부하 테스트 설정
        self.load_test_configs = {
            'light': {'threads': 10, 'operations': 100, 'duration': 30},
            'medium': {'threads': 50, 'operations': 500, 'duration': 60},
            'heavy': {'threads': 100, 'operations': 1000, 'duration': 120},
            'extreme': {'threads': 200, 'operations': 2000, 'duration': 180}
        }
    
    def test_light_load_authentication(self):
        """경량 부하 인증 테스트"""
        self._run_load_test('light', self._authentication_workload)
    
    def test_medium_load_authentication(self):
        """중간 부하 인증 테스트"""
        self._run_load_test('medium', self._authentication_workload)
    
    def test_heavy_load_authentication(self):
        """중량 부하 인증 테스트"""
        self._run_load_test('heavy', self._authentication_workload)
    
    def test_light_load_encryption(self):
        """경량 부하 암호화 테스트"""
        self._run_load_test('light', self._encryption_workload)
    
    def test_medium_load_encryption(self):
        """중간 부하 암호화 테스트"""
        self._run_load_test('medium', self._encryption_workload)
    
    def test_heavy_load_encryption(self):
        """중량 부하 암호화 테스트"""
        self._run_load_test('heavy', self._encryption_workload)
    
    def test_light_load_monitoring(self):
        """경량 부하 모니터링 테스트"""
        self._run_load_test('light', self._monitoring_workload)
    
    def test_medium_load_monitoring(self):
        """중간 부하 모니터링 테스트"""
        self._run_load_test('medium', self._monitoring_workload)
    
    def test_heavy_load_monitoring(self):
        """중량 부하 모니터링 테스트"""
        self._run_load_test('heavy', self._monitoring_workload)
    
    def test_mixed_load_security_operations(self):
        """혼합 부하 보안 작업 테스트"""
        self._run_load_test('heavy', self._mixed_security_workload)
    
    def test_extreme_load_stress_test(self):
        """극한 부하 스트레스 테스트"""
        self._run_load_test('extreme', self._stress_test_workload)
    
    def _run_load_test(self, load_level, workload_func):
        """부하 테스트 실행"""
        config = self.load_test_configs[load_level]
        threads = config['threads']
        operations = config['operations']
        duration = config['duration']
        
        print(f"\n🚀 {load_level.upper()} 부하 테스트 시작")
        print(f"스레드 수: {threads}, 작업 수: {operations}, 지속 시간: {duration}초")
        
        # 부하 테스트 실행
        start_time = time.time()
        results = self._execute_load_test(threads, operations, duration, workload_func)
        total_time = time.time() - start_time
        
        # 결과 분석
        self._analyze_load_test_results(load_level, results, total_time)
    
    def _execute_load_test(self, threads, operations, duration, workload_func):
        """부하 테스트 실행"""
        results = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'operation_times': [],
            'errors': [],
            'start_time': time.time(),
            'end_time': None
        }
        
        def worker():
            """워커 스레드 함수"""
            thread_id = threading.current_thread().ident
            local_operations = 0
            
            while time.time() - results['start_time'] < duration and local_operations < operations:
                try:
                    start_op_time = time.time()
                    success = workload_func(thread_id, local_operations)
                    op_time = time.time() - start_op_time
                    
                    results['total_operations'] += 1
                    results['operation_times'].append(op_time)
                    
                    if success:
                        results['successful_operations'] += 1
                    else:
                        results['failed_operations'] += 1
                    
                    local_operations += 1
                    
                    # 짧은 대기 시간 (시스템 부하 조절)
                    time.sleep(0.001)
                    
                except Exception as e:
                    results['failed_operations'] += 1
                    results['errors'].append(str(e))
                    local_operations += 1
        
        # 스레드 풀 실행
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(worker) for _ in range(threads)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    results['errors'].append(str(e))
        
        results['end_time'] = time.time()
        return results
    
    def _analyze_load_test_results(self, load_level, results, total_time):
        """부하 테스트 결과 분석"""
        total_ops = results['total_operations']
        successful_ops = results['successful_operations']
        failed_ops = results['failed_operations']
        operation_times = results['operation_times']
        errors = results['errors']
        
        # 기본 통계
        success_rate = (successful_ops / total_ops * 100) if total_ops > 0 else 0
        ops_per_second = total_ops / total_time if total_time > 0 else 0
        
        # 응답 시간 통계
        if operation_times:
            avg_response_time = sum(operation_times) / len(operation_times)
            min_response_time = min(operation_times)
            max_response_time = max(operation_times)
            p95_response_time = sorted(operation_times)[int(len(operation_times) * 0.95)]
            p99_response_time = sorted(operation_times)[int(len(operation_times) * 0.99)]
        else:
            avg_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        # 결과 출력
        print(f"\n📊 {load_level.upper()} 부하 테스트 결과:")
        print(f"  총 작업 수: {total_ops}")
        print(f"  성공한 작업: {successful_ops}")
        print(f"  실패한 작업: {failed_ops}")
        print(f"  성공률: {success_rate:.2f}%")
        print(f"  초당 작업 수: {ops_per_second:.2f}")
        print(f"  평균 응답 시간: {avg_response_time:.3f}초")
        print(f"  최소 응답 시간: {min_response_time:.3f}초")
        print(f"  최대 응답 시간: {max_response_time:.3f}초")
        print(f"  95% 응답 시간: {p95_response_time:.3f}초")
        print(f"  99% 응답 시간: {p99_response_time:.3f}초")
        print(f"  오류 수: {len(errors)}")
        
        # 성능 기준 검증
        self._validate_performance_standards(load_level, success_rate, ops_per_second, 
                                           avg_response_time, p95_response_time, p99_response_time)
    
    def _validate_performance_standards(self, load_level, success_rate, ops_per_second, 
                                      avg_response_time, p95_response_time, p99_response_time):
        """성능 기준 검증"""
        # 성공률 기준
        min_success_rate = {
            'light': 99.0,
            'medium': 95.0,
            'heavy': 90.0,
            'extreme': 80.0
        }
        
        self.assertGreaterEqual(success_rate, min_success_rate[load_level],
                              f"{load_level} 부하에서 성공률이 기준치 미만: {success_rate:.2f}% < {min_success_rate[load_level]}%")
        
        # 초당 작업 수 기준
        min_ops_per_second = {
            'light': 10.0,
            'medium': 50.0,
            'heavy': 100.0,
            'extreme': 200.0
        }
        
        self.assertGreaterEqual(ops_per_second, min_ops_per_second[load_level],
                              f"{load_level} 부하에서 초당 작업 수가 기준치 미만: {ops_per_second:.2f} < {min_ops_per_second[load_level]}")
        
        # 평균 응답 시간 기준
        max_avg_response_time = {
            'light': 0.5,
            'medium': 1.0,
            'heavy': 2.0,
            'extreme': 5.0
        }
        
        self.assertLessEqual(avg_response_time, max_avg_response_time[load_level],
                           f"{load_level} 부하에서 평균 응답 시간이 기준치 초과: {avg_response_time:.3f}초 > {max_avg_response_time[load_level]}초")
        
        # 95% 응답 시간 기준
        max_p95_response_time = {
            'light': 1.0,
            'medium': 2.0,
            'heavy': 5.0,
            'extreme': 10.0
        }
        
        self.assertLessEqual(p95_response_time, max_p95_response_time[load_level],
                           f"{load_level} 부하에서 95% 응답 시간이 기준치 초과: {p95_response_time:.3f}초 > {max_p95_response_time[load_level]}초")
    
    def _authentication_workload(self, thread_id, operation_id):
        """인증 작업 부하"""
        try:
            # 사용자 인증
            auth_result = authentication_service.authenticate_user(
                username=f"load_user_{thread_id}_{operation_id}",
                password="load_password_123",
                ip_address=f"192.168.1.{100 + (thread_id + operation_id) % 100}",
                user_agent=self.test_user_agent,
                require_2fa=False
            )
            
            if auth_result.success:
                # JWT 토큰 검증
                valid, payload = authentication_service.verify_jwt_token(auth_result.token)
                return valid
            else:
                return False
                
        except Exception:
            return False
    
    def _encryption_workload(self, thread_id, operation_id):
        """암호화 작업 부하"""
        try:
            # 데이터 암호화
            encrypted_data = encryption_service.encrypt_data(
                self.test_data, 
                f"load_key_{thread_id}_{operation_id}"
            )
            
            # 데이터 복호화
            decrypted_data = encryption_service.decrypt_data(encrypted_data)
            
            return decrypted_data == self.test_data
            
        except Exception:
            return False
    
    def _monitoring_workload(self, thread_id, operation_id):
        """모니터링 작업 부하"""
        try:
            # 보안 이벤트 로깅
            event_id = security_monitoring_service.log_security_event(
                event_type=EventType.AUTHENTICATION_SUCCESS,
                threat_level=ThreatLevel.LOW,
                source_ip=f"192.168.1.{100 + (thread_id + operation_id) % 100}",
                user_id=f"load_user_{thread_id}_{operation_id}",
                endpoint=self.test_endpoint,
                description=f"부하 테스트 이벤트 {thread_id}-{operation_id}",
                details={"thread_id": thread_id, "operation_id": operation_id}
            )
            
            return event_id is not None
            
        except Exception:
            return False
    
    def _mixed_security_workload(self, thread_id, operation_id):
        """혼합 보안 작업 부하"""
        try:
            # 랜덤하게 보안 작업 선택
            operation_type = random.choice(['auth', 'encrypt', 'monitor', 'privacy'])
            
            if operation_type == 'auth':
                return self._authentication_workload(thread_id, operation_id)
            elif operation_type == 'encrypt':
                return self._encryption_workload(thread_id, operation_id)
            elif operation_type == 'monitor':
                return self._monitoring_workload(thread_id, operation_id)
            elif operation_type == 'privacy':
                return self._privacy_workload(thread_id, operation_id)
            else:
                return False
                
        except Exception:
            return False
    
    def _privacy_workload(self, thread_id, operation_id):
        """개인정보보호 작업 부하"""
        try:
            # 개인정보 수집
            data_id = privacy_service.collect_personal_data(
                user_id=f"load_user_{thread_id}_{operation_id}",
                data_type=PersonalDataType.IDENTIFIER,
                data_value=f"홍길동_{thread_id}_{operation_id}",
                purpose=ProcessingPurpose.SERVICE_PROVISION
            )
            
            return data_id is not None
            
        except Exception:
            return False
    
    def _stress_test_workload(self, thread_id, operation_id):
        """스트레스 테스트 작업 부하"""
        try:
            # 여러 보안 작업을 연속으로 실행
            operations = [
                self._authentication_workload(thread_id, operation_id),
                self._encryption_workload(thread_id, operation_id),
                self._monitoring_workload(thread_id, operation_id),
                self._privacy_workload(thread_id, operation_id)
            ]
            
            # 모든 작업이 성공했는지 확인
            return all(operations)
            
        except Exception:
            return False
    
    def test_memory_leak_detection(self):
        """메모리 누수 탐지 테스트"""
        import psutil
        import gc
        
        # 초기 메모리 사용량 측정
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 대량의 보안 작업 실행
        for i in range(1000):
            # 인증
            auth_result = authentication_service.authenticate_user(
                username=f"memory_test_user_{i:04d}",
                password="memory_test_password_123",
                ip_address=f"192.168.1.{i % 100}",
                user_agent=self.test_user_agent,
                require_2fa=False
            )
            
            # 암호화
            encrypted = encryption_service.encrypt_data(self.test_data, f"memory_key_{i}")
            
            # 모니터링
            security_monitoring_service.log_security_event(
                event_type=EventType.AUTHENTICATION_SUCCESS,
                threat_level=ThreatLevel.LOW,
                source_ip=f"192.168.1.{i % 100}",
                user_id=f"memory_test_user_{i:04d}",
                endpoint=self.test_endpoint,
                description=f"메모리 테스트 이벤트 {i}",
                details={"test": "memory", "index": i}
            )
            
            # 가비지 컬렉션 강제 실행
            if i % 100 == 0:
                gc.collect()
        
        # 최종 메모리 사용량 측정
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가량이 200MB 이내여야 함 (메모리 누수 방지)
        self.assertLess(memory_increase, 200.0, 
                       f"메모리 누수 가능성: {memory_increase:.2f}MB 증가")
        
        print(f"\n💾 메모리 사용량 테스트 결과:")
        print(f"  초기 메모리: {initial_memory:.2f}MB")
        print(f"  최종 메모리: {final_memory:.2f}MB")
        print(f"  메모리 증가: {memory_increase:.2f}MB")
    
    def test_concurrent_user_sessions(self):
        """동시 사용자 세션 테스트"""
        def create_user_session(thread_id):
            """사용자 세션 생성"""
            try:
                # 사용자 인증
                auth_result = authentication_service.authenticate_user(
                    username=f"session_user_{thread_id}",
                    password="session_password_123",
                    ip_address=f"192.168.1.{100 + thread_id % 100}",
                    user_agent=self.test_user_agent,
                    require_2fa=False
                )
                
                if auth_result.success:
                    # 세션 생성
                    session_id = f"session_{thread_id}_{int(time.time())}"
                    session_created = authentication_service.create_session(
                        user_id=auth_result.user_id,
                        session_id=session_id,
                        ip_address=f"192.168.1.{100 + thread_id % 100}",
                        user_agent=self.test_user_agent
                    )
                    
                    return session_created
                else:
                    return False
                    
            except Exception:
                return False
        
        # 동시 세션 생성 테스트 (100개 스레드)
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(create_user_session, i) for i in range(100)]
            results = [future.result() for future in as_completed(futures)]
        
        total_time = time.time() - start_time
        successful_sessions = sum(1 for r in results if r)
        
        # 성공률이 90% 이상이어야 함
        success_rate = successful_sessions / len(results) * 100
        self.assertGreaterEqual(success_rate, 90.0, 
                              f"동시 세션 생성 성공률이 낮음: {success_rate:.1f}%")
        
        # 전체 시간이 10초 이내여야 함
        self.assertLess(total_time, 10.0, 
                       f"동시 세션 생성 시간이 너무 오래 걸림: {total_time:.3f}초")
        
        print(f"\n👥 동시 사용자 세션 테스트 결과:")
        print(f"  총 세션 수: {len(results)}")
        print(f"  성공한 세션: {successful_sessions}")
        print(f"  성공률: {success_rate:.1f}%")
        print(f"  총 시간: {total_time:.3f}초")

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
