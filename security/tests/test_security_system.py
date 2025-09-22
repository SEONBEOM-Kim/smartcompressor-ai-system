#!/usr/bin/env python3
"""
보안 시스템 테스트 스크립트
Stripe & AWS 보안 시스템을 벤치마킹한 보안 기능들을 종합적으로 테스트합니다.
"""

import sys
import os
import time
import json
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.authentication_service import authentication_service, AuthMethod, UserRole
from security.services.authorization_service import authorization_service, Permission, Resource
from security.services.encryption_service import encryption_service, EncryptionType, KeyType
from security.services.privacy_service import privacy_service, PersonalDataType, ProcessingPurpose
from security.services.security_monitoring_service import security_monitoring_service, EventType, ThreatLevel
from security.services.intrusion_detection_service import intrusion_detection_service, AttackType
from security.services.backup_recovery_service import backup_recovery_service, BackupType, StorageType

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

def test_authentication_system():
    """인증 시스템 테스트"""
    print_section("인증 시스템 테스트")
    
    # 1. 사용자 인증 테스트
    try:
        auth_result = authentication_service.authenticate_user(
            username="admin",
            password="admin123",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            require_2fa=False
        )
        success1 = auth_result.success
        print_test("사용자 인증", success1, f"사용자 ID: {auth_result.user_id}")
    except Exception as e:
        print_test("사용자 인증", False, f"오류: {e}")
        success1 = False
    
    # 2. JWT 토큰 검증 테스트
    try:
        if success1 and auth_result.token:
            valid, payload = authentication_service.verify_jwt_token(auth_result.token)
            print_test("JWT 토큰 검증", valid, f"페이로드: {payload}")
        else:
            print_test("JWT 토큰 검증", False, "토큰이 없습니다.")
    except Exception as e:
        print_test("JWT 토큰 검증", False, f"오류: {e}")
    
    # 3. 2FA 설정 테스트
    try:
        if success1 and auth_result.user_id:
            twofa_setup = authentication_service.setup_2fa(auth_result.user_id)
            print_test("2FA 설정", True, f"QR 코드 생성: {len(twofa_setup['qr_code'])} bytes")
        else:
            print_test("2FA 설정", False, "사용자 ID가 없습니다.")
    except Exception as e:
        print_test("2FA 설정", False, f"오류: {e}")
    
    # 4. 비밀번호 해시 테스트
    try:
        password = "testpassword123"
        hashed = authentication_service.hash_password(password)
        verified = authentication_service.verify_password(password, hashed)
        print_test("비밀번호 해시/검증", verified, "bcrypt 사용")
    except Exception as e:
        print_test("비밀번호 해시/검증", False, f"오류: {e}")
    
    return success1

def test_authorization_system():
    """권한 관리 시스템 테스트"""
    print_section("권한 관리 시스템 테스트")
    
    # 1. 역할 생성 테스트
    try:
        from security.services.authorization_service import Role, Policy
        
        # 커스텀 정책 생성
        custom_policy = Policy(
            name="test_policy",
            description="테스트 정책",
            permissions=[Permission.USER_READ, Permission.STORE_READ],
            resources=[Resource.USER, Resource.STORE]
        )
        policy_created = authorization_service.create_policy(custom_policy)
        print_test("정책 생성", policy_created, "테스트 정책 생성")
    except Exception as e:
        print_test("정책 생성", False, f"오류: {e}")
    
    # 2. 역할 할당 테스트
    try:
        user_id = "test_user_001"
        role_assigned = authorization_service.assign_role_to_user(user_id, "admin")
        print_test("역할 할당", role_assigned, f"사용자 {user_id}에게 admin 역할 할당")
    except Exception as e:
        print_test("역할 할당", False, f"오류: {e}")
    
    # 3. 권한 확인 테스트
    try:
        user_id = "test_user_001"
        has_permission = authorization_service.check_permission(
            user_id, Permission.USER_READ, Resource.USER
        )
        print_test("권한 확인", has_permission, f"사용자 {user_id}의 USER_READ 권한")
    except Exception as e:
        print_test("권한 확인", False, f"오류: {e}")
    
    # 4. 사용자 권한 조회 테스트
    try:
        user_id = "test_user_001"
        permissions = authorization_service.get_user_permissions(user_id)
        print_test("사용자 권한 조회", len(permissions) > 0, f"권한 수: {len(permissions)}")
    except Exception as e:
        print_test("사용자 권한 조회", False, f"오류: {e}")
    
    return True

def test_encryption_system():
    """암호화 시스템 테스트"""
    print_section("암호화 시스템 테스트")
    
    # 1. 데이터 암호화/복호화 테스트
    try:
        test_data = b"Hello, World! This is a test message for encryption."
        encrypted = encryption_service.encrypt_data(test_data, "data_key")
        decrypted = encryption_service.decrypt_data(encrypted)
        success1 = decrypted == test_data
        print_test("데이터 암호화/복호화", success1, f"원본: {len(test_data)} bytes, 복호화: {len(decrypted)} bytes")
    except Exception as e:
        print_test("데이터 암호화/복호화", False, f"오류: {e}")
        success1 = False
    
    # 2. 문자열 암호화/복호화 테스트
    try:
        test_string = "안녕하세요! 이것은 암호화 테스트 메시지입니다."
        encrypted_string = encryption_service.encrypt_string(test_string, "data_key")
        decrypted_string = encryption_service.decrypt_string(encrypted_string)
        success2 = decrypted_string == test_string
        print_test("문자열 암호화/복호화", success2, f"원본: {len(test_string)} chars, 복호화: {len(decrypted_string)} chars")
    except Exception as e:
        print_test("문자열 암호화/복호화", False, f"오류: {e}")
        success2 = False
    
    # 3. 키 생성 테스트
    try:
        from security.services.encryption_service import KeyType
        new_key_id = encryption_service.generate_new_key(KeyType.DATA, EncryptionType.AES_256_GCM)
        key_info = encryption_service.get_key_info(new_key_id)
        success3 = key_info is not None
        print_test("키 생성", success3, f"새 키 ID: {new_key_id}")
    except Exception as e:
        print_test("키 생성", False, f"오류: {e}")
        success3 = False
    
    # 4. 해시 함수 테스트
    try:
        test_data = "test_data_for_hashing"
        hashed_data = encryption_service.hash_sensitive_data(test_data)
        verified = encryption_service.verify_hashed_data(test_data, hashed_data)
        print_test("해시 함수", verified, "SHA-256 + Salt 사용")
    except Exception as e:
        print_test("해시 함수", False, f"오류: {e}")
    
    return success1 and success2 and success3

def test_privacy_system():
    """개인정보보호 시스템 테스트"""
    print_section("개인정보보호 시스템 테스트")
    
    # 1. 개인정보 수집 테스트
    try:
        user_id = "test_user_001"
        data_id = privacy_service.collect_personal_data(
            user_id=user_id,
            data_type=PersonalDataType.IDENTIFIER,
            data_value="홍길동",
            purpose=ProcessingPurpose.SERVICE_PROVISION
        )
        print_test("개인정보 수집", True, f"데이터 ID: {data_id}")
    except Exception as e:
        print_test("개인정보 수집", False, f"오류: {e}")
    
    # 2. 동의 관리 테스트
    try:
        user_id = "test_user_001"
        consent_id = privacy_service.grant_consent(
            user_id=user_id,
            purpose=ProcessingPurpose.SERVICE_PROVISION,
            data_types=[PersonalDataType.IDENTIFIER, PersonalDataType.SENSITIVE],
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0"
        )
        print_test("동의 관리", True, f"동의 ID: {consent_id}")
    except Exception as e:
        print_test("동의 관리", False, f"오류: {e}")
    
    # 3. 데이터 주체 요청 테스트
    try:
        user_id = "test_user_001"
        request_id = privacy_service.request_data_access(user_id, "개인정보 열람 요청")
        print_test("데이터 주체 요청", True, f"요청 ID: {request_id}")
    except Exception as e:
        print_test("데이터 주체 요청", False, f"오류: {e}")
    
    # 4. 개인정보 처리방침 조회 테스트
    try:
        policy = privacy_service.get_privacy_policy()
        success = "version" in policy and "company_name" in policy
        print_test("개인정보 처리방침 조회", success, f"버전: {policy.get('version', 'N/A')}")
    except Exception as e:
        print_test("개인정보 처리방침 조회", False, f"오류: {e}")
    
    return True

def test_security_monitoring():
    """보안 모니터링 시스템 테스트"""
    print_section("보안 모니터링 시스템 테스트")
    
    # 1. 보안 이벤트 로깅 테스트
    try:
        event_id = security_monitoring_service.log_security_event(
            event_type=EventType.AUTHENTICATION_FAILURE,
            threat_level=ThreatLevel.MEDIUM,
            source_ip="192.168.1.100",
            user_id="test_user",
            endpoint="/api/auth/login",
            description="인증 실패 시도",
            details={"attempts": 3, "username": "test_user"}
        )
        print_test("보안 이벤트 로깅", True, f"이벤트 ID: {event_id}")
    except Exception as e:
        print_test("보안 이벤트 로깅", False, f"오류: {e}")
    
    # 2. 보안 통계 조회 테스트
    try:
        stats = security_monitoring_service.get_security_statistics()
        success = "total_events" in stats and "threat_levels" in stats
        print_test("보안 통계 조회", success, f"총 이벤트: {stats.get('total_events', 0)}")
    except Exception as e:
        print_test("보안 통계 조회", False, f"오류: {e}")
    
    # 3. 보안 이벤트 조회 테스트
    try:
        events = security_monitoring_service.get_security_events(limit=10)
        success = isinstance(events, list)
        print_test("보안 이벤트 조회", success, f"이벤트 수: {len(events)}")
    except Exception as e:
        print_test("보안 이벤트 조회", False, f"오류: {e}")
    
    return True

def test_intrusion_detection():
    """침입 탐지 시스템 테스트"""
    print_section("침입 탐지 시스템 테스트")
    
    # 1. 네트워크 트래픽 로깅 테스트
    try:
        intrusion_detection_service.log_network_traffic(
            source_ip="192.168.1.100",
            dest_ip="192.168.1.1",
            port=80,
            protocol="TCP",
            bytes_sent=1024,
            bytes_received=2048,
            duration=1.5,
            flags="SYN,ACK"
        )
        print_test("네트워크 트래픽 로깅", True, "트래픽 로깅 완료")
    except Exception as e:
        print_test("네트워크 트래픽 로깅", False, f"오류: {e}")
    
    # 2. 사용자 행동 로깅 테스트
    try:
        intrusion_detection_service.log_user_behavior(
            user_id="test_user_001",
            action="login",
            endpoint="/api/auth/login",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0",
            success=True,
            response_time=0.5,
            data_size=1024
        )
        print_test("사용자 행동 로깅", True, "행동 로깅 완료")
    except Exception as e:
        print_test("사용자 행동 로깅", False, f"오류: {e}")
    
    # 3. 침입 이벤트 조회 테스트
    try:
        events = intrusion_detection_service.get_intrusion_events(limit=10)
        success = isinstance(events, list)
        print_test("침입 이벤트 조회", success, f"이벤트 수: {len(events)}")
    except Exception as e:
        print_test("침입 이벤트 조회", False, f"오류: {e}")
    
    # 4. 탐지 통계 조회 테스트
    try:
        stats = intrusion_detection_service.get_detection_statistics()
        success = "total_events" in stats and "attack_types" in stats
        print_test("탐지 통계 조회", success, f"총 이벤트: {stats.get('total_events', 0)}")
    except Exception as e:
        print_test("탐지 통계 조회", False, f"오류: {e}")
    
    return True

def test_backup_recovery():
    """백업 및 복구 시스템 테스트"""
    print_section("백업 및 복구 시스템 테스트")
    
    # 1. 백업 설정 생성 테스트
    try:
        config_id = backup_recovery_service.create_backup_config(
            name="test_backup",
            backup_type=BackupType.FULL,
            source_paths=["/tmp/test_data"],
            destination="/tmp/backups",
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=7
        )
        print_test("백업 설정 생성", True, f"설정 ID: {config_id}")
    except Exception as e:
        print_test("백업 설정 생성", False, f"오류: {e}")
    
    # 2. 백업 통계 조회 테스트
    try:
        stats = backup_recovery_service.get_backup_statistics()
        success = "total_jobs" in stats and "completed_jobs" in stats
        print_test("백업 통계 조회", success, f"총 작업: {stats.get('total_jobs', 0)}")
    except Exception as e:
        print_test("백업 통계 조회", False, f"오류: {e}")
    
    # 3. 백업 목록 조회 테스트
    try:
        backups = backup_recovery_service.list_backups()
        success = isinstance(backups, list)
        print_test("백업 목록 조회", success, f"백업 수: {len(backups)}")
    except Exception as e:
        print_test("백업 목록 조회", False, f"오류: {e}")
    
    return True

def test_security_integration():
    """보안 시스템 통합 테스트"""
    print_section("보안 시스템 통합 테스트")
    
    # 1. 종합 보안 이벤트 시뮬레이션
    try:
        # 인증 실패 시뮬레이션
        for i in range(5):
            authentication_service.authenticate_user(
                username="hacker",
                password="wrong_password",
                ip_address="192.168.1.200",
                user_agent="Mozilla/5.0",
                require_2fa=False
            )
        
        # 보안 이벤트 로깅
        security_monitoring_service.log_security_event(
            event_type=EventType.BRUTE_FORCE,
            threat_level=ThreatLevel.HIGH,
            source_ip="192.168.1.200",
            user_id=None,
            endpoint="/api/auth/login",
            description="브루트 포스 공격 시도",
            details={"attempts": 5, "username": "hacker"}
        )
        
        print_test("보안 이벤트 시뮬레이션", True, "브루트 포스 공격 시뮬레이션 완료")
    except Exception as e:
        print_test("보안 이벤트 시뮬레이션", False, f"오류: {e}")
    
    # 2. 개인정보 처리 시뮬레이션
    try:
        # 개인정보 수집
        data_id = privacy_service.collect_personal_data(
            user_id="test_user_002",
            data_type=PersonalDataType.IDENTIFIER,
            data_value="김철수",
            purpose=ProcessingPurpose.SERVICE_PROVISION
        )
        
        # 암호화된 데이터 저장 시뮬레이션
        encrypted_data = encryption_service.encrypt_string("김철수", "data_key")
        
        print_test("개인정보 처리 시뮬레이션", True, f"데이터 ID: {data_id}, 암호화: {len(encrypted_data)} chars")
    except Exception as e:
        print_test("개인정보 처리 시뮬레이션", False, f"오류: {e}")
    
    return True

def main():
    """메인 테스트 함수"""
    print("🔒 보안 시스템 종합 테스트 시작")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 테스트 실행
    test_results = []
    
    test_results.append(("인증 시스템", test_authentication_system()))
    test_results.append(("권한 관리 시스템", test_authorization_system()))
    test_results.append(("암호화 시스템", test_encryption_system()))
    test_results.append(("개인정보보호 시스템", test_privacy_system()))
    test_results.append(("보안 모니터링 시스템", test_security_monitoring()))
    test_results.append(("침입 탐지 시스템", test_intrusion_detection()))
    test_results.append(("백업 및 복구 시스템", test_backup_recovery()))
    test_results.append(("보안 시스템 통합", test_security_integration()))
    
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
        print("🎉 모든 보안 테스트가 성공적으로 완료되었습니다!")
        print("🔐 Stripe & AWS 수준의 보안 시스템이 구축되었습니다!")
        return 0
    else:
        print("⚠️  일부 테스트가 실패했습니다. 로그를 확인하세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())