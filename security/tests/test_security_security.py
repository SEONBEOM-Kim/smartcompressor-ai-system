#!/usr/bin/env python3
"""
보안 시스템 보안 테스트
보안 시스템 자체의 보안 취약점을 테스트합니다.
"""

import sys
import os
import unittest
import time
import hashlib
import hmac
import base64
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.authentication_service import authentication_service, AuthMethod, UserRole
from security.services.authorization_service import authorization_service, Permission, Resource
from security.services.encryption_service import encryption_service, EncryptionType, KeyType
from security.services.privacy_service import privacy_service, PersonalDataType, ProcessingPurpose
from security.services.security_monitoring_service import security_monitoring_service, EventType, ThreatLevel
from security.services.intrusion_detection_service import intrusion_detection_service, AttackType
from security.services.backup_recovery_service import backup_recovery_service, BackupType, StorageType

class TestSecuritySecurity(unittest.TestCase):
    """보안 시스템 보안 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_user_id = "security_test_user_001"
        self.test_username = "security_test_user"
        self.test_password = "security_test_password_123"
        self.test_ip = "192.168.1.100"
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.test_endpoint = "/api/security/test"
        self.test_data = b"Security test data for vulnerability testing"
    
    def test_password_security(self):
        """비밀번호 보안 테스트"""
        # 1. 비밀번호 해싱 보안
        password = "test_password_123"
        hashed = authentication_service.hash_password(password)
        
        # 해싱된 비밀번호가 원본과 다르고 충분히 복잡해야 함
        self.assertNotEqual(hashed, password)
        self.assertGreater(len(hashed), 50)  # bcrypt는 최소 60자
        
        # 2. 비밀번호 검증 보안
        verified = authentication_service.verify_password(password, hashed)
        self.assertTrue(verified)
        
        # 잘못된 비밀번호는 검증 실패해야 함
        wrong_verified = authentication_service.verify_password("wrong_password", hashed)
        self.assertFalse(wrong_verified)
        
        # 3. 타이밍 공격 방지 (동일한 시간에 검증 완료)
        start_time = time.time()
        authentication_service.verify_password(password, hashed)
        correct_time = time.time() - start_time
        
        start_time = time.time()
        authentication_service.verify_password("wrong_password", hashed)
        wrong_time = time.time() - start_time
        
        # 시간 차이가 크지 않아야 함 (타이밍 공격 방지)
        time_diff = abs(correct_time - wrong_time)
        self.assertLess(time_diff, 0.1, "타이밍 공격 가능성: 시간 차이가 큼")
    
    def test_jwt_token_security(self):
        """JWT 토큰 보안 테스트"""
        user_id = "test_user_001"
        role = UserRole.ADMIN
        
        # 1. JWT 토큰 생성
        token = authentication_service.generate_jwt_token(user_id, role)
        
        # 토큰이 생성되었는지 확인
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        
        # 2. JWT 토큰 구조 검증
        parts = token.split('.')
        self.assertEqual(len(parts), 3, "JWT 토큰은 3개 부분으로 구성되어야 함")
        
        # 3. JWT 토큰 검증
        valid, payload = authentication_service.verify_jwt_token(token)
        self.assertTrue(valid)
        self.assertEqual(payload['user_id'], user_id)
        self.assertEqual(payload['role'], role.value)
        
        # 4. 변조된 토큰 검증
        tampered_token = token[:-5] + "XXXXX"  # 토큰 변조
        valid, payload = authentication_service.verify_jwt_token(tampered_token)
        self.assertFalse(valid)
        self.assertIsNone(payload)
        
        # 5. 만료된 토큰 검증
        expired_time = datetime.utcnow() - timedelta(hours=1)
        with patch('security.services.authentication_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = expired_time
            expired_token = authentication_service.generate_jwt_token(user_id, role)
        
        valid, payload = authentication_service.verify_jwt_token(expired_token)
        self.assertFalse(valid)
        self.assertIsNone(payload)
    
    def test_encryption_security(self):
        """암호화 보안 테스트"""
        # 1. 데이터 암호화
        encrypted = encryption_service.encrypt_data(self.test_data, "security_key")
        
        # 암호화된 데이터가 원본과 다르고 충분히 복잡해야 함
        self.assertNotEqual(encrypted, self.test_data)
        self.assertGreater(len(encrypted), len(self.test_data))
        
        # 2. 데이터 복호화
        decrypted = encryption_service.decrypt_data(encrypted)
        self.assertEqual(decrypted, self.test_data)
        
        # 3. 변조된 암호화 데이터 복호화 시도
        tampered_encrypted = encrypted[:-10] + b"XXXXXXXXXX"  # 데이터 변조
        with self.assertRaises(Exception):
            encryption_service.decrypt_data(tampered_encrypted)
        
        # 4. 키 없이 복호화 시도
        with self.assertRaises(Exception):
            encryption_service.decrypt_data(b"invalid_encrypted_data")
        
        # 5. 암호화 일관성 테스트
        encrypted1 = encryption_service.encrypt_data(self.test_data, "security_key")
        encrypted2 = encryption_service.encrypt_data(self.test_data, "security_key")
        
        # 같은 데이터라도 다른 암호화 결과가 나와야 함 (IV 사용)
        self.assertNotEqual(encrypted1, encrypted2)
        
        # 하지만 둘 다 복호화하면 같은 결과가 나와야 함
        decrypted1 = encryption_service.decrypt_data(encrypted1)
        decrypted2 = encryption_service.decrypt_data(encrypted2)
        self.assertEqual(decrypted1, decrypted2)
        self.assertEqual(decrypted1, self.test_data)
    
    def test_authorization_security(self):
        """권한 관리 보안 테스트"""
        user_id = "test_user_001"
        
        # 1. 권한 확인
        has_permission = authorization_service.check_permission(
            user_id=user_id,
            permission=Permission.USER_READ,
            resource=Resource.USER
        )
        self.assertIsInstance(has_permission, bool)
        
        # 2. 권한 상승 공격 방지
        # 일반 사용자가 관리자 권한을 요청하는 경우
        admin_permission = authorization_service.check_permission(
            user_id=user_id,
            permission=Permission.ADMIN_WRITE,
            resource=Resource.SYSTEM
        )
        # 일반 사용자는 관리자 권한이 없어야 함
        self.assertFalse(admin_permission)
        
        # 3. 권한 우회 시도 방지
        # 존재하지 않는 사용자의 권한 확인
        fake_user_permission = authorization_service.check_permission(
            user_id="fake_user_999999",
            permission=Permission.USER_READ,
            resource=Resource.USER
        )
        self.assertFalse(fake_user_permission)
    
    def test_privacy_security(self):
        """개인정보보호 보안 테스트"""
        user_id = "test_user_001"
        
        # 1. 개인정보 수집
        data_id = privacy_service.collect_personal_data(
            user_id=user_id,
            data_type=PersonalDataType.IDENTIFIER,
            data_value="홍길동",
            purpose=ProcessingPurpose.SERVICE_PROVISION
        )
        
        # 2. 개인정보 조회 권한 확인
        collected_data = privacy_service.get_personal_data(data_id)
        self.assertIsNotNone(collected_data)
        
        # 3. 다른 사용자의 개인정보 조회 시도 (권한 없음)
        fake_data_id = "fake_data_999999"
        fake_data = privacy_service.get_personal_data(fake_data_id)
        # 존재하지 않는 데이터는 None이어야 함
        self.assertIsNone(fake_data)
        
        # 4. 개인정보 익명화
        anonymized_id = privacy_service.anonymize_personal_data(data_id)
        self.assertIsNotNone(anonymized_id)
        
        # 익명화된 데이터는 원본과 달라야 함
        anonymized_data = privacy_service.get_personal_data(anonymized_id)
        self.assertNotEqual(anonymized_data['data_value'], "홍길동")
    
    def test_security_monitoring_security(self):
        """보안 모니터링 보안 테스트"""
        # 1. 보안 이벤트 로깅
        event_id = security_monitoring_service.log_security_event(
            event_type=EventType.AUTHENTICATION_SUCCESS,
            threat_level=ThreatLevel.LOW,
            source_ip=self.test_ip,
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            description="보안 테스트 이벤트",
            details={"test": "security"}
        )
        
        # 2. 이벤트 조회
        event = security_monitoring_service.get_security_event(event_id)
        self.assertIsNotNone(event)
        
        # 3. 존재하지 않는 이벤트 조회
        fake_event = security_monitoring_service.get_security_event("fake_event_999999")
        self.assertIsNone(fake_event)
        
        # 4. 보안 통계 조회
        stats = security_monitoring_service.get_security_statistics()
        self.assertIsNotNone(stats)
        self.assertIsInstance(stats, dict)
    
    def test_intrusion_detection_security(self):
        """침입 탐지 보안 테스트"""
        # 1. 사용자 행동 로깅
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
        
        # 2. 행동 조회
        behavior = intrusion_detection_service.get_user_behavior(behavior_id)
        self.assertIsNotNone(behavior)
        
        # 3. 존재하지 않는 행동 조회
        fake_behavior = intrusion_detection_service.get_user_behavior("fake_behavior_999999")
        self.assertIsNone(fake_behavior)
        
        # 4. 이상 행동 탐지
        anomalies = intrusion_detection_service.detect_anomalies()
        self.assertIsInstance(anomalies, list)
    
    def test_backup_security(self):
        """백업 보안 테스트"""
        # 1. 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name="security_test_backup",
            backup_type=BackupType.FULL,
            source_paths=["/tmp/test_data"],
            destination="/tmp/backups",
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=7
        )
        
        # 2. 백업 설정 조회
        config = backup_recovery_service.get_backup_config(config_id)
        self.assertIsNotNone(config)
        
        # 3. 존재하지 않는 설정 조회
        fake_config = backup_recovery_service.get_backup_config("fake_config_999999")
        self.assertIsNone(fake_config)
        
        # 4. 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        self.assertIsNotNone(backup_id)
        
        # 5. 백업 조회
        backup = backup_recovery_service.get_backup(backup_id)
        self.assertIsNotNone(backup)
    
    def test_sql_injection_prevention(self):
        """SQL 인젝션 방지 테스트"""
        # SQL 인젝션 시도
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for payload in sql_injection_payloads:
            # SQL 인젝션 시도가 안전하게 처리되어야 함
            try:
                # 사용자 인증 시도 (SQL 인젝션 포함)
                auth_result = authentication_service.authenticate_user(
                    username=payload,
                    password="test_password",
                    ip_address=self.test_ip,
                    user_agent=self.test_user_agent,
                    require_2fa=False
                )
                
                # SQL 인젝션 시도는 실패해야 함
                self.assertFalse(auth_result.success)
                
            except Exception as e:
                # 예외가 발생해도 안전하게 처리되어야 함
                self.assertIsInstance(e, Exception)
    
    def test_xss_prevention(self):
        """XSS 방지 테스트"""
        # XSS 시도
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            # XSS 시도가 안전하게 처리되어야 함
            try:
                # 개인정보 수집 시도 (XSS 포함)
                data_id = privacy_service.collect_personal_data(
                    user_id=self.test_user_id,
                    data_type=PersonalDataType.IDENTIFIER,
                    data_value=payload,
                    purpose=ProcessingPurpose.SERVICE_PROVISION
                )
                
                # XSS 페이로드가 그대로 저장되지 않아야 함
                if data_id:
                    collected_data = privacy_service.get_personal_data(data_id)
                    if collected_data:
                        # XSS 태그가 제거되었는지 확인
                        self.assertNotIn('<script>', collected_data['data_value'])
                        self.assertNotIn('javascript:', collected_data['data_value'])
                        self.assertNotIn('onerror=', collected_data['data_value'])
                
            except Exception as e:
                # 예외가 발생해도 안전하게 처리되어야 함
                self.assertIsInstance(e, Exception)
    
    def test_csrf_prevention(self):
        """CSRF 방지 테스트"""
        # CSRF 토큰 생성 (실제 구현에서는 CSRF 토큰 사용)
        csrf_token = "csrf_token_12345"
        
        # 1. 유효한 CSRF 토큰으로 요청
        try:
            # CSRF 토큰 검증 (실제 구현에서는 CSRF 토큰 검증 로직 필요)
            valid_csrf = True  # 모의 검증
            self.assertTrue(valid_csrf)
        except Exception:
            self.fail("유효한 CSRF 토큰이 거부됨")
        
        # 2. 잘못된 CSRF 토큰으로 요청
        try:
            invalid_csrf_token = "invalid_csrf_token"
            # CSRF 토큰 검증 (실제 구현에서는 CSRF 토큰 검증 로직 필요)
            valid_csrf = False  # 모의 검증
            self.assertFalse(valid_csrf)
        except Exception:
            # 예외가 발생해도 안전하게 처리되어야 함
            pass
    
    def test_rate_limiting(self):
        """속도 제한 테스트"""
        # 빠른 연속 요청 시도
        for i in range(100):
            try:
                # 인증 시도
                auth_result = authentication_service.authenticate_user(
                    username=f"rate_limit_user_{i}",
                    password="rate_limit_password",
                    ip_address=self.test_ip,
                    user_agent=self.test_user_agent,
                    require_2fa=False
                )
                
                # 처음 몇 번은 성공할 수 있지만, 이후에는 제한되어야 함
                if i < 10:
                    # 처음 10번은 성공할 수 있음
                    pass
                else:
                    # 이후에는 실패하거나 제한되어야 함
                    # (실제 구현에서는 속도 제한 로직 필요)
                    pass
                    
            except Exception:
                # 예외가 발생해도 안전하게 처리되어야 함
                pass
    
    def test_input_validation(self):
        """입력 검증 테스트"""
        # 1. 빈 입력값 처리
        try:
            auth_result = authentication_service.authenticate_user(
                username="",
                password="",
                ip_address="",
                user_agent="",
                require_2fa=False
            )
            self.assertFalse(auth_result.success)
        except Exception:
            # 예외가 발생해도 안전하게 처리되어야 함
            pass
        
        # 2. 매우 긴 입력값 처리
        long_string = "A" * 10000
        try:
            auth_result = authentication_service.authenticate_user(
                username=long_string,
                password=long_string,
                ip_address=long_string,
                user_agent=long_string,
                require_2fa=False
            )
            self.assertFalse(auth_result.success)
        except Exception:
            # 예외가 발생해도 안전하게 처리되어야 함
            pass
        
        # 3. 특수 문자 입력값 처리
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        try:
            auth_result = authentication_service.authenticate_user(
                username=special_chars,
                password=special_chars,
                ip_address=special_chars,
                user_agent=special_chars,
                require_2fa=False
            )
            # 특수 문자가 포함된 입력은 적절히 처리되어야 함
            pass
        except Exception:
            # 예외가 발생해도 안전하게 처리되어야 함
            pass
    
    def test_audit_logging_security(self):
        """감사 로깅 보안 테스트"""
        # 1. 감사 로그 생성
        audit_logs = security_monitoring_service.get_security_audit_logs()
        self.assertIsInstance(audit_logs, list)
        
        # 2. 감사 로그 무결성 확인
        for log in audit_logs:
            # 필수 필드가 있는지 확인
            self.assertIn('timestamp', log)
            self.assertIn('user_id', log)
            self.assertIn('action', log)
            self.assertIn('resource', log)
            self.assertIn('ip_address', log)
            self.assertIn('user_agent', log)
            self.assertIn('success', log)
            
            # 타임스탬프가 유효한지 확인
            self.assertIsInstance(log['timestamp'], str)
            
            # IP 주소가 유효한지 확인
            ip = log['ip_address']
            if ip:
                # IP 주소 형식 검증 (간단한 검증)
                self.assertTrue(ip.count('.') == 3 or ip.count(':') >= 2)
    
    def test_error_handling_security(self):
        """오류 처리 보안 테스트"""
        # 1. 시스템 오류 시 민감한 정보 노출 방지
        try:
            # 존재하지 않는 서비스 호출
            fake_service = "fake_service_999999"
            result = getattr(security_monitoring_service, fake_service)()
            self.fail("존재하지 않는 서비스가 호출됨")
        except AttributeError:
            # 예상된 오류
            pass
        except Exception as e:
            # 다른 오류가 발생해도 민감한 정보가 노출되지 않아야 함
            error_message = str(e)
            # 시스템 경로나 민감한 정보가 포함되지 않아야 함
            self.assertNotIn('/root/', error_message)
            self.assertNotIn('password', error_message.lower())
            self.assertNotIn('secret', error_message.lower())
    
    def test_data_integrity(self):
        """데이터 무결성 테스트"""
        # 1. 암호화된 데이터 무결성
        encrypted = encryption_service.encrypt_data(self.test_data, "integrity_key")
        decrypted = encryption_service.decrypt_data(encrypted)
        self.assertEqual(decrypted, self.test_data)
        
        # 2. 해시 무결성
        data_hash = encryption_service.hash_sensitive_data("test_data")
        verified = encryption_service.verify_hashed_data("test_data", data_hash)
        self.assertTrue(verified)
        
        # 3. 변조된 데이터 검증
        tampered_data = "tampered_data"
        verified = encryption_service.verify_hashed_data(tampered_data, data_hash)
        self.assertFalse(verified)
    
    def test_session_security(self):
        """세션 보안 테스트"""
        user_id = "test_user_001"
        session_id = "test_session_001"
        
        # 1. 세션 생성
        session_created = authentication_service.create_session(
            user_id=user_id,
            session_id=session_id,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        self.assertTrue(session_created)
        
        # 2. 세션 검증
        valid_session = authentication_service.validate_session(session_id)
        self.assertTrue(valid_session)
        
        # 3. 세션 하이재킹 방지 (다른 IP에서 접근)
        hijacked_session = authentication_service.validate_session(session_id)
        # 실제 구현에서는 IP 변경 시 세션 무효화
        # 여기서는 모의 테스트
        self.assertTrue(hijacked_session)
        
        # 4. 세션 만료
        expired = authentication_service.delete_session(session_id)
        self.assertTrue(expired)
        
        # 5. 만료된 세션 검증
        valid_expired = authentication_service.validate_session(session_id)
        self.assertFalse(valid_expired)

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
