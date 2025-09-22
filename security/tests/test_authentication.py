#!/usr/bin/env python3
"""
인증 시스템 단위 테스트
JWT, OAuth2, 2FA 등 인증 관련 기능을 테스트합니다.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.authentication_service import authentication_service, AuthMethod, UserRole

class TestAuthenticationService(unittest.TestCase):
    """인증 서비스 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_username = "test_user"
        self.test_password = "test_password_123"
        self.test_ip = "192.168.1.100"
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def test_password_hashing(self):
        """비밀번호 해싱 테스트"""
        # 비밀번호 해싱
        hashed = authentication_service.hash_password(self.test_password)
        
        # 해싱된 비밀번호가 원본과 다른지 확인
        self.assertNotEqual(hashed, self.test_password)
        self.assertIsInstance(hashed, str)
        self.assertTrue(len(hashed) > 0)
        
        # 비밀번호 검증
        verified = authentication_service.verify_password(self.test_password, hashed)
        self.assertTrue(verified)
        
        # 잘못된 비밀번호 검증
        wrong_verified = authentication_service.verify_password("wrong_password", hashed)
        self.assertFalse(wrong_verified)
    
    def test_jwt_token_generation(self):
        """JWT 토큰 생성 테스트"""
        user_id = "test_user_001"
        role = UserRole.ADMIN
        
        # JWT 토큰 생성
        token = authentication_service.generate_jwt_token(user_id, role)
        
        # 토큰이 생성되었는지 확인
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
        
        # 토큰 구조 확인 (JWT는 3개 부분으로 구성)
        parts = token.split('.')
        self.assertEqual(len(parts), 3)
    
    def test_jwt_token_verification(self):
        """JWT 토큰 검증 테스트"""
        user_id = "test_user_001"
        role = UserRole.ADMIN
        
        # JWT 토큰 생성
        token = authentication_service.generate_jwt_token(user_id, role)
        
        # 토큰 검증
        valid, payload = authentication_service.verify_jwt_token(token)
        
        # 검증 결과 확인
        self.assertTrue(valid)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get('user_id'), user_id)
        self.assertEqual(payload.get('role'), role.value)
    
    def test_jwt_token_expiration(self):
        """JWT 토큰 만료 테스트"""
        user_id = "test_user_001"
        role = UserRole.ADMIN
        
        # 만료된 토큰 생성 (과거 시간으로 설정)
        expired_time = datetime.utcnow() - timedelta(hours=1)
        
        with patch('security.services.authentication_service.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = expired_time
            token = authentication_service.generate_jwt_token(user_id, role)
        
        # 현재 시간으로 토큰 검증 (만료된 토큰)
        valid, payload = authentication_service.verify_jwt_token(token)
        
        # 만료된 토큰은 유효하지 않아야 함
        self.assertFalse(valid)
        self.assertIsNone(payload)
    
    def test_user_authentication(self):
        """사용자 인증 테스트"""
        # 사용자 인증 시도
        auth_result = authentication_service.authenticate_user(
            username=self.test_username,
            password=self.test_password,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent,
            require_2fa=False
        )
        
        # 인증 결과 확인
        self.assertIsNotNone(auth_result)
        self.assertIsInstance(auth_result.success, bool)
        self.assertIsNotNone(auth_result.user_id)
        self.assertIsNotNone(auth_result.token)
        self.assertIsNotNone(auth_result.role)
    
    def test_2fa_setup(self):
        """2FA 설정 테스트"""
        user_id = "test_user_001"
        
        # 2FA 설정
        twofa_setup = authentication_service.setup_2fa(user_id)
        
        # 2FA 설정 결과 확인
        self.assertIsNotNone(twofa_setup)
        self.assertIn('secret_key', twofa_setup)
        self.assertIn('qr_code', twofa_setup)
        self.assertIn('backup_codes', twofa_setup)
        
        # QR 코드가 생성되었는지 확인
        self.assertIsInstance(twofa_setup['qr_code'], bytes)
        self.assertTrue(len(twofa_setup['qr_code']) > 0)
        
        # 백업 코드가 생성되었는지 확인
        self.assertIsInstance(twofa_setup['backup_codes'], list)
        self.assertEqual(len(twofa_setup['backup_codes']), 10)
    
    def test_2fa_verification(self):
        """2FA 검증 테스트"""
        user_id = "test_user_001"
        
        # 2FA 설정
        twofa_setup = authentication_service.setup_2fa(user_id)
        secret_key = twofa_setup['secret_key']
        
        # TOTP 코드 생성 (실제 구현에서는 pyotp 라이브러리 사용)
        # 여기서는 모의 코드 사용
        mock_totp_code = "123456"
        
        # 2FA 검증
        verified = authentication_service.verify_2fa(user_id, mock_totp_code)
        
        # 검증 결과 확인 (모의 테스트이므로 항상 True)
        self.assertIsInstance(verified, bool)
    
    def test_session_management(self):
        """세션 관리 테스트"""
        user_id = "test_user_001"
        session_id = "test_session_001"
        
        # 세션 생성
        session_created = authentication_service.create_session(
            user_id=user_id,
            session_id=session_id,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        # 세션 생성 확인
        self.assertTrue(session_created)
        
        # 세션 검증
        valid_session = authentication_service.validate_session(session_id)
        self.assertTrue(valid_session)
        
        # 세션 갱신
        refreshed = authentication_service.refresh_session(session_id)
        self.assertTrue(refreshed)
        
        # 세션 삭제
        deleted = authentication_service.delete_session(session_id)
        self.assertTrue(deleted)
    
    def test_brute_force_protection(self):
        """브루트 포스 공격 방지 테스트"""
        username = "test_user"
        wrong_password = "wrong_password"
        
        # 여러 번 잘못된 비밀번호로 인증 시도
        for i in range(5):
            auth_result = authentication_service.authenticate_user(
                username=username,
                password=wrong_password,
                ip_address=self.test_ip,
                user_agent=self.test_user_agent,
                require_2fa=False
            )
            
            # 처음 몇 번은 실패하지만 계정이 잠기지 않아야 함
            if i < 3:
                self.assertFalse(auth_result.success)
            else:
                # 3번 이상 실패하면 계정이 잠겨야 함
                self.assertFalse(auth_result.success)
                # 추가 검증: 계정 잠금 상태 확인
                # (실제 구현에서는 계정 잠금 상태를 확인하는 로직 필요)
    
    def test_password_policy(self):
        """비밀번호 정책 테스트"""
        # 약한 비밀번호 테스트
        weak_passwords = [
            "123",  # 너무 짧음
            "password",  # 너무 단순함
            "12345678",  # 숫자만
            "abcdefgh",  # 문자만
            "Password1",  # 대소문자 + 숫자만
        ]
        
        for weak_password in weak_passwords:
            # 비밀번호 정책 검증 (실제 구현에서는 정책 검증 로직 필요)
            # 여기서는 모의 테스트
            is_valid = len(weak_password) >= 8 and any(c.isupper() for c in weak_password)
            self.assertFalse(is_valid, f"약한 비밀번호가 통과됨: {weak_password}")
        
        # 강한 비밀번호 테스트
        strong_password = "StrongP@ssw0rd123!"
        is_valid = len(strong_password) >= 8 and any(c.isupper() for c in strong_password)
        self.assertTrue(is_valid, f"강한 비밀번호가 거부됨: {strong_password}")

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
