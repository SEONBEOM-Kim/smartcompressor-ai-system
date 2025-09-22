#!/usr/bin/env python3
"""
보안 시스템 성능 테스트
보안 서비스들의 성능과 확장성을 테스트합니다.
"""

import sys
import os
import unittest
import time
import threading
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

class TestSecurityPerformance(unittest.TestCase):
    """보안 시스템 성능 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_user_id = "perf_test_user_001"
        self.test_username = "perf_test_user"
        self.test_password = "perf_test_password_123"
        self.test_ip = "192.168.1.100"
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.test_endpoint = "/api/performance/test"
        self.test_data = b"Performance test data for encryption and security testing"
    
    def test_authentication_performance(self):
        """인증 성능 테스트"""
        # 단일 인증 성능
        start_time = time.time()
        auth_result = authentication_service.authenticate_user(
            username=self.test_username,
            password=self.test_password,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent,
            require_2fa=False
        )
        single_auth_time = time.time() - start_time
        
        # 단일 인증 시간이 1초 이내여야 함
        self.assertLess(single_auth_time, 1.0, f"단일 인증 시간이 너무 오래 걸림: {single_auth_time:.3f}초")
        
        # JWT 토큰 검증 성능
        start_time = time.time()
        valid, payload = authentication_service.verify_jwt_token(auth_result.token)
        token_verify_time = time.time() - start_time
        
        # 토큰 검증 시간이 0.1초 이내여야 함
        self.assertLess(token_verify_time, 0.1, f"토큰 검증 시간이 너무 오래 걸림: {token_verify_time:.3f}초")
        self.assertTrue(valid)
    
    def test_encryption_performance(self):
        """암호화 성능 테스트"""
        # 데이터 암호화 성능
        start_time = time.time()
        encrypted_data = encryption_service.encrypt_data(self.test_data, "perf_key")
        encrypt_time = time.time() - start_time
        
        # 암호화 시간이 1초 이내여야 함
        self.assertLess(encrypt_time, 1.0, f"암호화 시간이 너무 오래 걸림: {encrypt_time:.3f}초")
        
        # 데이터 복호화 성능
        start_time = time.time()
        decrypted_data = encryption_service.decrypt_data(encrypted_data)
        decrypt_time = time.time() - start_time
        
        # 복호화 시간이 1초 이내여야 함
        self.assertLess(decrypt_time, 1.0, f"복호화 시간이 너무 오래 걸림: {decrypt_time:.3f}초")
        
        # 원본과 동일한지 확인
        self.assertEqual(decrypted_data, self.test_data)
        
        # 대용량 데이터 암호화 성능
        large_data = self.test_data * 1000  # 약 50KB
        start_time = time.time()
        encrypted_large = encryption_service.encrypt_data(large_data, "perf_key")
        large_encrypt_time = time.time() - start_time
        
        # 대용량 암호화 시간이 5초 이내여야 함
        self.assertLess(large_encrypt_time, 5.0, f"대용량 암호화 시간이 너무 오래 걸림: {large_encrypt_time:.3f}초")
    
    def test_privacy_performance(self):
        """개인정보보호 성능 테스트"""
        # 개인정보 수집 성능
        start_time = time.time()
        data_id = privacy_service.collect_personal_data(
            user_id=self.test_user_id,
            data_type=PersonalDataType.IDENTIFIER,
            data_value="홍길동",
            purpose=ProcessingPurpose.SERVICE_PROVISION
        )
        collect_time = time.time() - start_time
        
        # 개인정보 수집 시간이 0.5초 이내여야 함
        self.assertLess(collect_time, 0.5, f"개인정보 수집 시간이 너무 오래 걸림: {collect_time:.3f}초")
        
        # 동의 부여 성능
        start_time = time.time()
        consent_id = privacy_service.grant_consent(
            user_id=self.test_user_id,
            purpose=ProcessingPurpose.SERVICE_PROVISION,
            data_types=[PersonalDataType.IDENTIFIER],
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        consent_time = time.time() - start_time
        
        # 동의 부여 시간이 0.5초 이내여야 함
        self.assertLess(consent_time, 0.5, f"동의 부여 시간이 너무 오래 걸림: {consent_time:.3f}초")
    
    def test_security_monitoring_performance(self):
        """보안 모니터링 성능 테스트"""
        # 보안 이벤트 로깅 성능
        start_time = time.time()
        event_id = security_monitoring_service.log_security_event(
            event_type=EventType.AUTHENTICATION_SUCCESS,
            threat_level=ThreatLevel.LOW,
            source_ip=self.test_ip,
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            description="성능 테스트 이벤트",
            details={"test": "performance"}
        )
        log_time = time.time() - start_time
        
        # 이벤트 로깅 시간이 0.1초 이내여야 함
        self.assertLess(log_time, 0.1, f"이벤트 로깅 시간이 너무 오래 걸림: {log_time:.3f}초")
        
        # 보안 통계 조회 성능
        start_time = time.time()
        stats = security_monitoring_service.get_security_statistics()
        stats_time = time.time() - start_time
        
        # 통계 조회 시간이 1초 이내여야 함
        self.assertLess(stats_time, 1.0, f"통계 조회 시간이 너무 오래 걸림: {stats_time:.3f}초")
        self.assertIsNotNone(stats)
    
    def test_intrusion_detection_performance(self):
        """침입 탐지 성능 테스트"""
        # 사용자 행동 로깅 성능
        start_time = time.time()
        behavior_id = intrusion_detection_service.log_user_behavior(
            user_id=self.test_user_id,
            action="login",
            endpoint=self.test_endpoint,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent,
            success=True,
            response_time=0.5,
            data_size=1024
        )
        behavior_log_time = time.time() - start_time
        
        # 행동 로깅 시간이 0.1초 이내여야 함
        self.assertLess(behavior_log_time, 0.1, f"행동 로깅 시간이 너무 오래 걸림: {behavior_log_time:.3f}초")
        
        # 이상 행동 탐지 성능
        start_time = time.time()
        anomalies = intrusion_detection_service.detect_anomalies()
        anomaly_detection_time = time.time() - start_time
        
        # 이상 행동 탐지 시간이 2초 이내여야 함
        self.assertLess(anomaly_detection_time, 2.0, f"이상 행동 탐지 시간이 너무 오래 걸림: {anomaly_detection_time:.3f}초")
        self.assertIsInstance(anomalies, list)
    
    def test_backup_performance(self):
        """백업 성능 테스트"""
        # 백업 설정 생성 성능
        start_time = time.time()
        config_id = backup_recovery_service.create_backup_config(
            name="perf_test_backup",
            backup_type=BackupType.FULL,
            source_paths=["/tmp/test_data"],
            destination="/tmp/backups",
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=7
        )
        config_create_time = time.time() - start_time
        
        # 설정 생성 시간이 0.5초 이내여야 함
        self.assertLess(config_create_time, 0.5, f"설정 생성 시간이 너무 오래 걸림: {config_create_time:.3f}초")
        
        # 백업 실행 성능
        start_time = time.time()
        backup_id = backup_recovery_service.execute_backup(config_id)
        backup_execute_time = time.time() - start_time
        
        # 백업 실행 시간이 5초 이내여야 함
        self.assertLess(backup_execute_time, 5.0, f"백업 실행 시간이 너무 오래 걸림: {backup_execute_time:.3f}초")
    
    def test_concurrent_authentication(self):
        """동시 인증 성능 테스트"""
        def authenticate_user():
            """사용자 인증 함수"""
            return authentication_service.authenticate_user(
                username=f"concurrent_user_{threading.current_thread().ident}",
                password="concurrent_password_123",
                ip_address=f"192.168.1.{100 + threading.current_thread().ident % 100}",
                user_agent=self.test_user_agent,
                require_2fa=False
            )
        
        # 동시 인증 테스트 (10개 스레드)
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(authenticate_user) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        concurrent_time = time.time() - start_time
        
        # 동시 인증 시간이 5초 이내여야 함
        self.assertLess(concurrent_time, 5.0, f"동시 인증 시간이 너무 오래 걸림: {concurrent_time:.3f}초")
        
        # 모든 인증이 성공했는지 확인
        self.assertEqual(len(results), 10)
        for result in results:
            self.assertTrue(result.success)
    
    def test_concurrent_encryption(self):
        """동시 암호화 성능 테스트"""
        def encrypt_data():
            """데이터 암호화 함수"""
            return encryption_service.encrypt_data(
                self.test_data, 
                f"concurrent_key_{threading.current_thread().ident}"
            )
        
        # 동시 암호화 테스트 (20개 스레드)
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(encrypt_data) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
        
        concurrent_time = time.time() - start_time
        
        # 동시 암호화 시간이 10초 이내여야 함
        self.assertLess(concurrent_time, 10.0, f"동시 암호화 시간이 너무 오래 걸림: {concurrent_time:.3f}초")
        
        # 모든 암호화가 성공했는지 확인
        self.assertEqual(len(results), 20)
        for result in results:
            self.assertIsNotNone(result)
            self.assertIsInstance(result, bytes)
    
    def test_concurrent_monitoring(self):
        """동시 모니터링 성능 테스트"""
        def log_security_event():
            """보안 이벤트 로깅 함수"""
            return security_monitoring_service.log_security_event(
                event_type=EventType.AUTHENTICATION_SUCCESS,
                threat_level=ThreatLevel.LOW,
                source_ip=f"192.168.1.{100 + threading.current_thread().ident % 100}",
                user_id=f"concurrent_user_{threading.current_thread().ident}",
                endpoint=self.test_endpoint,
                description="동시 모니터링 테스트",
                details={"thread_id": threading.current_thread().ident}
            )
        
        # 동시 모니터링 테스트 (50개 스레드)
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(log_security_event) for _ in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        concurrent_time = time.time() - start_time
        
        # 동시 모니터링 시간이 10초 이내여야 함
        self.assertLess(concurrent_time, 10.0, f"동시 모니터링 시간이 너무 오래 걸림: {concurrent_time:.3f}초")
        
        # 모든 로깅이 성공했는지 확인
        self.assertEqual(len(results), 50)
        for result in results:
            self.assertIsNotNone(result)
            self.assertIsInstance(result, str)
    
    def test_memory_usage(self):
        """메모리 사용량 테스트"""
        import psutil
        import os
        
        # 현재 프로세스의 메모리 사용량 측정
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 대량의 보안 이벤트 로깅
        for i in range(1000):
            security_monitoring_service.log_security_event(
                event_type=EventType.AUTHENTICATION_SUCCESS,
                threat_level=ThreatLevel.LOW,
                source_ip=f"192.168.1.{i % 100}",
                user_id=f"memory_test_user_{i:04d}",
                endpoint=self.test_endpoint,
                description=f"메모리 테스트 이벤트 {i}",
                details={"test": "memory", "index": i}
            )
        
        # 메모리 사용량 재측정
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가량이 100MB 이내여야 함
        self.assertLess(memory_increase, 100.0, f"메모리 사용량이 너무 많이 증가함: {memory_increase:.2f}MB")
    
    def test_database_performance(self):
        """데이터베이스 성능 테스트"""
        # 대량의 데이터 조회 성능
        start_time = time.time()
        events = security_monitoring_service.get_security_events(limit=1000)
        query_time = time.time() - start_time
        
        # 데이터 조회 시간이 2초 이내여야 함
        self.assertLess(query_time, 2.0, f"데이터 조회 시간이 너무 오래 걸림: {query_time:.3f}초")
        self.assertIsInstance(events, list)
        
        # 통계 조회 성능
        start_time = time.time()
        stats = security_monitoring_service.get_security_statistics()
        stats_time = time.time() - start_time
        
        # 통계 조회 시간이 1초 이내여야 함
        self.assertLess(stats_time, 1.0, f"통계 조회 시간이 너무 오래 걸림: {stats_time:.3f}초")
        self.assertIsNotNone(stats)
    
    def test_scalability(self):
        """확장성 테스트"""
        # 점진적으로 증가하는 부하 테스트
        thread_counts = [1, 5, 10, 20, 50]
        results = []
        
        for thread_count in thread_counts:
            def perform_security_operations():
                """보안 작업 수행 함수"""
                # 인증
                auth_result = authentication_service.authenticate_user(
                    username=f"scale_user_{threading.current_thread().ident}",
                    password="scale_password_123",
                    ip_address=f"192.168.1.{100 + threading.current_thread().ident % 100}",
                    user_agent=self.test_user_agent,
                    require_2fa=False
                )
                
                # 암호화
                encrypted = encryption_service.encrypt_data(self.test_data, "scale_key")
                
                # 모니터링
                event_id = security_monitoring_service.log_security_event(
                    event_type=EventType.AUTHENTICATION_SUCCESS,
                    threat_level=ThreatLevel.LOW,
                    source_ip=f"192.168.1.{100 + threading.current_thread().ident % 100}",
                    user_id=f"scale_user_{threading.current_thread().ident}",
                    endpoint=self.test_endpoint,
                    description="확장성 테스트",
                    details={"thread_count": thread_count}
                )
                
                return {
                    'auth_success': auth_result.success,
                    'encryption_success': encrypted is not None,
                    'monitoring_success': event_id is not None
                }
            
            # 동시 작업 실행
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(perform_security_operations) for _ in range(thread_count)]
                results_batch = [future.result() for future in as_completed(futures)]
            
            execution_time = time.time() - start_time
            
            # 결과 저장
            results.append({
                'thread_count': thread_count,
                'execution_time': execution_time,
                'success_rate': sum(1 for r in results_batch if all(r.values())) / len(results_batch) * 100
            })
        
        # 확장성 확인
        for result in results:
            # 성공률이 90% 이상이어야 함
            self.assertGreaterEqual(result['success_rate'], 90.0, 
                                  f"스레드 수 {result['thread_count']}에서 성공률이 낮음: {result['success_rate']:.1f}%")
            
            # 실행 시간이 스레드 수에 비례해서 증가하지 않아야 함 (선형 증가 허용)
            max_expected_time = result['thread_count'] * 2.0  # 스레드당 최대 2초
            self.assertLess(result['execution_time'], max_expected_time,
                          f"스레드 수 {result['thread_count']}에서 실행 시간이 너무 오래 걸림: {result['execution_time']:.3f}초")

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
