#!/usr/bin/env python3
"""
암호화 시스템 단위 테스트
데이터 암호화, 키 관리, 해시 함수 등을 테스트합니다.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.encryption_service import encryption_service, EncryptionType, KeyType

class TestEncryptionService(unittest.TestCase):
    """암호화 서비스 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_data = b"Hello, World! This is a test message for encryption."
        self.test_string = "안녕하세요! 이것은 암호화 테스트 메시지입니다."
        self.test_key_id = "test_key_001"
    
    def test_data_encryption_decryption(self):
        """데이터 암호화/복호화 테스트"""
        # 데이터 암호화
        encrypted = encryption_service.encrypt_data(self.test_data, self.test_key_id)
        
        # 암호화된 데이터가 원본과 다른지 확인
        self.assertNotEqual(encrypted, self.test_data)
        self.assertIsInstance(encrypted, bytes)
        self.assertTrue(len(encrypted) > 0)
        
        # 데이터 복호화
        decrypted = encryption_service.decrypt_data(encrypted)
        
        # 복호화된 데이터가 원본과 같은지 확인
        self.assertEqual(decrypted, self.test_data)
    
    def test_string_encryption_decryption(self):
        """문자열 암호화/복호화 테스트"""
        # 문자열 암호화
        encrypted_string = encryption_service.encrypt_string(self.test_string, self.test_key_id)
        
        # 암호화된 문자열이 원본과 다른지 확인
        self.assertNotEqual(encrypted_string, self.test_string)
        self.assertIsInstance(encrypted_string, str)
        self.assertTrue(len(encrypted_string) > 0)
        
        # 문자열 복호화
        decrypted_string = encryption_service.decrypt_string(encrypted_string)
        
        # 복호화된 문자열이 원본과 같은지 확인
        self.assertEqual(decrypted_string, self.test_string)
    
    def test_unicode_string_encryption(self):
        """유니코드 문자열 암호화 테스트"""
        unicode_strings = [
            "안녕하세요! こんにちは! Hello!",
            "🚀🔒💻🌟",
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "한글과 English와 日本語가 섞인 텍스트",
        ]
        
        for unicode_string in unicode_strings:
            # 암호화
            encrypted = encryption_service.encrypt_string(unicode_string, self.test_key_id)
            
            # 복호화
            decrypted = encryption_service.decrypt_string(encrypted)
            
            # 원본과 동일한지 확인
            self.assertEqual(decrypted, unicode_string)
    
    def test_large_data_encryption(self):
        """대용량 데이터 암호화 테스트"""
        # 1MB 데이터 생성
        large_data = b"x" * (1024 * 1024)
        
        # 암호화
        encrypted = encryption_service.encrypt_data(large_data, self.test_key_id)
        
        # 복호화
        decrypted = encryption_service.decrypt_data(encrypted)
        
        # 원본과 동일한지 확인
        self.assertEqual(decrypted, large_data)
    
    def test_key_generation(self):
        """키 생성 테스트"""
        # 새 키 생성
        new_key_id = encryption_service.generate_new_key(
            key_type=KeyType.DATA,
            encryption_type=EncryptionType.AES_256_GCM
        )
        
        # 키 ID가 생성되었는지 확인
        self.assertIsNotNone(new_key_id)
        self.assertIsInstance(new_key_id, str)
        self.assertTrue(len(new_key_id) > 0)
        
        # 키 정보 조회
        key_info = encryption_service.get_key_info(new_key_id)
        self.assertIsNotNone(key_info)
        self.assertEqual(key_info['key_id'], new_key_id)
        self.assertEqual(key_info['key_type'], KeyType.DATA.value)
        self.assertEqual(key_info['encryption_type'], EncryptionType.AES_256_GCM.value)
    
    def test_key_rotation(self):
        """키 로테이션 테스트"""
        # 새 키 생성
        old_key_id = encryption_service.generate_new_key(
            key_type=KeyType.DATA,
            encryption_type=EncryptionType.AES_256_GCM
        )
        
        # 데이터 암호화 (구 키 사용)
        encrypted_data = encryption_service.encrypt_data(self.test_data, old_key_id)
        
        # 키 로테이션
        new_key_id = encryption_service.rotate_key(old_key_id)
        
        # 새 키가 생성되었는지 확인
        self.assertIsNotNone(new_key_id)
        self.assertNotEqual(new_key_id, old_key_id)
        
        # 구 키로 암호화된 데이터는 여전히 복호화 가능해야 함
        decrypted_data = encryption_service.decrypt_data(encrypted_data)
        self.assertEqual(decrypted_data, self.test_data)
    
    def test_hash_functions(self):
        """해시 함수 테스트"""
        test_data = "test_data_for_hashing"
        
        # 해시 생성
        hashed_data = encryption_service.hash_sensitive_data(test_data)
        
        # 해시가 생성되었는지 확인
        self.assertIsNotNone(hashed_data)
        self.assertIsInstance(hashed_data, str)
        self.assertTrue(len(hashed_data) > 0)
        
        # 해시 검증
        verified = encryption_service.verify_hashed_data(test_data, hashed_data)
        self.assertTrue(verified)
        
        # 잘못된 데이터로 해시 검증
        wrong_verified = encryption_service.verify_hashed_data("wrong_data", hashed_data)
        self.assertFalse(wrong_verified)
    
    def test_hash_consistency(self):
        """해시 일관성 테스트"""
        test_data = "consistent_hash_test"
        
        # 같은 데이터로 여러 번 해시 생성
        hash1 = encryption_service.hash_sensitive_data(test_data)
        hash2 = encryption_service.hash_sensitive_data(test_data)
        
        # 같은 데이터는 같은 해시를 생성해야 함
        self.assertEqual(hash1, hash2)
    
    def test_different_encryption_types(self):
        """다양한 암호화 타입 테스트"""
        encryption_types = [
            EncryptionType.AES_256_GCM,
            EncryptionType.AES_256_CBC,
            EncryptionType.CHACHA20_POLY1305,
        ]
        
        for enc_type in encryption_types:
            # 키 생성
            key_id = encryption_service.generate_new_key(
                key_type=KeyType.DATA,
                encryption_type=enc_type
            )
            
            # 암호화
            encrypted = encryption_service.encrypt_data(self.test_data, key_id)
            
            # 복호화
            decrypted = encryption_service.decrypt_data(encrypted)
            
            # 원본과 동일한지 확인
            self.assertEqual(decrypted, self.test_data)
    
    def test_key_management(self):
        """키 관리 테스트"""
        # 키 목록 조회
        keys = encryption_service.list_keys()
        self.assertIsInstance(keys, list)
        
        # 새 키 생성
        key_id = encryption_service.generate_new_key(
            key_type=KeyType.DATA,
            encryption_type=EncryptionType.AES_256_GCM
        )
        
        # 키 목록에 새 키가 포함되었는지 확인
        updated_keys = encryption_service.list_keys()
        self.assertIn(key_id, [key['key_id'] for key in updated_keys])
        
        # 키 삭제
        deleted = encryption_service.delete_key(key_id)
        self.assertTrue(deleted)
        
        # 삭제된 키는 목록에 없어야 함
        final_keys = encryption_service.list_keys()
        self.assertNotIn(key_id, [key['key_id'] for key in final_keys])
    
    def test_encryption_performance(self):
        """암호화 성능 테스트"""
        import time
        
        # 성능 측정을 위한 데이터
        test_data = b"Performance test data" * 1000  # 약 22KB
        
        # 암호화 시간 측정
        start_time = time.time()
        encrypted = encryption_service.encrypt_data(test_data, self.test_key_id)
        encrypt_time = time.time() - start_time
        
        # 복호화 시간 측정
        start_time = time.time()
        decrypted = encryption_service.decrypt_data(encrypted)
        decrypt_time = time.time() - start_time
        
        # 성능 확인 (1초 이내에 완료되어야 함)
        self.assertLess(encrypt_time, 1.0, f"암호화 시간이 너무 오래 걸림: {encrypt_time:.3f}초")
        self.assertLess(decrypt_time, 1.0, f"복호화 시간이 너무 오래 걸림: {decrypt_time:.3f}초")
        
        # 원본과 동일한지 확인
        self.assertEqual(decrypted, test_data)
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        # 잘못된 키 ID로 암호화 시도
        with self.assertRaises(Exception):
            encryption_service.encrypt_data(self.test_data, "invalid_key_id")
        
        # 잘못된 암호화된 데이터로 복호화 시도
        with self.assertRaises(Exception):
            encryption_service.decrypt_data("invalid_encrypted_data")
        
        # 잘못된 해시로 검증 시도
        with self.assertRaises(Exception):
            encryption_service.verify_hashed_data(self.test_string, "invalid_hash")

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
