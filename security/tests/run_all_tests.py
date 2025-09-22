#!/usr/bin/env python3
"""
보안 시스템 전체 테스트 실행 스크립트
모든 보안 테스트를 실행하고 결과를 종합합니다.
"""

import sys
import os
import unittest
import time
from datetime import datetime

# 테스트 모듈 import
from test_authentication import TestAuthenticationService
from test_encryption import TestEncryptionService
from test_privacy import TestPrivacyService
from test_security_monitoring import TestSecurityMonitoringService
from test_intrusion_detection import TestIntrusionDetectionService
from test_backup_recovery import TestBackupRecoveryService

def run_security_tests():
    """보안 테스트 실행"""
    print("🔒 보안 시스템 전체 테스트 시작")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 각 테스트 클래스 추가
    test_classes = [
        TestAuthenticationService,
        TestEncryptionService,
        TestPrivacyService,
        TestSecurityMonitoringService,
        TestIntrusionDetectionService,
        TestBackupRecoveryService
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # 결과 요약
    print("\n" + "="*80)
    print("🔒 보안 시스템 테스트 결과 요약")
    print("="*80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"총 테스트 수: {total_tests}")
    print(f"✅ 통과: {passed}")
    print(f"❌ 실패: {failures}")
    print(f"⚠️  오류: {errors}")
    print(f"⏭️  건너뜀: {skipped}")
    print(f"성공률: {(passed/total_tests*100):.1f}%")
    
    # 실패한 테스트 상세 정보
    if failures > 0:
        print("\n❌ 실패한 테스트:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    # 오류가 발생한 테스트 상세 정보
    if errors > 0:
        print("\n⚠️  오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # 전체 결과
    if failures == 0 and errors == 0:
        print("\n🎉 모든 보안 테스트가 성공적으로 완료되었습니다!")
        print("🔐 Stripe & AWS 수준의 보안 시스템이 구축되었습니다!")
        return True
    else:
        print(f"\n⚠️  {failures + errors}개의 테스트가 실패했습니다.")
        print("로그를 확인하고 문제를 해결하세요.")
        return False

def main():
    """메인 함수"""
    try:
        success = run_security_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"\n💥 테스트 실행 중 오류 발생: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
