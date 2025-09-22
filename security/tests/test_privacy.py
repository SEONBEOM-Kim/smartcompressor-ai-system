#!/usr/bin/env python3
"""
개인정보보호 시스템 단위 테스트
개인정보 수집, 동의 관리, 데이터 주체 권리 등을 테스트합니다.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.privacy_service import privacy_service, PersonalDataType, ProcessingPurpose

class TestPrivacyService(unittest.TestCase):
    """개인정보보호 서비스 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_user_id = "test_user_001"
        self.test_data_value = "홍길동"
        self.test_ip = "192.168.1.100"
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def test_personal_data_collection(self):
        """개인정보 수집 테스트"""
        # 개인정보 수집
        data_id = privacy_service.collect_personal_data(
            user_id=self.test_user_id,
            data_type=PersonalDataType.IDENTIFIER,
            data_value=self.test_data_value,
            purpose=ProcessingPurpose.SERVICE_PROVISION
        )
        
        # 데이터 ID가 생성되었는지 확인
        self.assertIsNotNone(data_id)
        self.assertIsInstance(data_id, str)
        self.assertTrue(len(data_id) > 0)
        
        # 수집된 데이터 조회
        collected_data = privacy_service.get_personal_data(data_id)
        self.assertIsNotNone(collected_data)
        self.assertEqual(collected_data['user_id'], self.test_user_id)
        self.assertEqual(collected_data['data_type'], PersonalDataType.IDENTIFIER.value)
        self.assertEqual(collected_data['data_value'], self.test_data_value)
        self.assertEqual(collected_data['purpose'], ProcessingPurpose.SERVICE_PROVISION.value)
    
    def test_consent_management(self):
        """동의 관리 테스트"""
        # 동의 부여
        consent_id = privacy_service.grant_consent(
            user_id=self.test_user_id,
            purpose=ProcessingPurpose.SERVICE_PROVISION,
            data_types=[PersonalDataType.IDENTIFIER, PersonalDataType.SENSITIVE],
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        # 동의 ID가 생성되었는지 확인
        self.assertIsNotNone(consent_id)
        self.assertIsInstance(consent_id, str)
        self.assertTrue(len(consent_id) > 0)
        
        # 동의 조회
        consent = privacy_service.get_consent(consent_id)
        self.assertIsNotNone(consent)
        self.assertEqual(consent['user_id'], self.test_user_id)
        self.assertEqual(consent['purpose'], ProcessingPurpose.SERVICE_PROVISION.value)
        self.assertIn(PersonalDataType.IDENTIFIER.value, consent['data_types'])
        self.assertIn(PersonalDataType.SENSITIVE.value, consent['data_types'])
    
    def test_consent_withdrawal(self):
        """동의 철회 테스트"""
        # 동의 부여
        consent_id = privacy_service.grant_consent(
            user_id=self.test_user_id,
            purpose=ProcessingPurpose.SERVICE_PROVISION,
            data_types=[PersonalDataType.IDENTIFIER],
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        # 동의 철회
        withdrawn = privacy_service.withdraw_consent(consent_id)
        self.assertTrue(withdrawn)
        
        # 철회된 동의 조회
        consent = privacy_service.get_consent(consent_id)
        self.assertIsNotNone(consent)
        self.assertFalse(consent['is_active'])
    
    def test_data_subject_rights(self):
        """데이터 주체 권리 테스트"""
        # 데이터 열람 요청
        request_id = privacy_service.request_data_access(
            user_id=self.test_user_id,
            request_type="개인정보 열람 요청"
        )
        
        # 요청 ID가 생성되었는지 확인
        self.assertIsNotNone(request_id)
        self.assertIsInstance(request_id, str)
        self.assertTrue(len(request_id) > 0)
        
        # 요청 조회
        request = privacy_service.get_data_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request['user_id'], self.test_user_id)
        self.assertEqual(request['request_type'], "개인정보 열람 요청")
    
    def test_data_rectification(self):
        """데이터 정정 요청 테스트"""
        # 데이터 정정 요청
        request_id = privacy_service.request_data_rectification(
            user_id=self.test_user_id,
            data_id="test_data_001",
            current_value="홍길동",
            new_value="홍길순",
            reason="이름 변경"
        )
        
        # 요청 ID가 생성되었는지 확인
        self.assertIsNotNone(request_id)
        self.assertIsInstance(request_id, str)
        self.assertTrue(len(request_id) > 0)
        
        # 요청 조회
        request = privacy_service.get_data_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request['user_id'], self.test_user_id)
        self.assertEqual(request['request_type'], "데이터 정정 요청")
        self.assertEqual(request['current_value'], "홍길동")
        self.assertEqual(request['new_value'], "홍길순")
    
    def test_data_erasure(self):
        """데이터 삭제 요청 테스트"""
        # 데이터 삭제 요청
        request_id = privacy_service.request_data_erasure(
            user_id=self.test_user_id,
            data_id="test_data_001",
            reason="서비스 이용 중단"
        )
        
        # 요청 ID가 생성되었는지 확인
        self.assertIsNotNone(request_id)
        self.assertIsInstance(request_id, str)
        self.assertTrue(len(request_id) > 0)
        
        # 요청 조회
        request = privacy_service.get_data_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request['user_id'], self.test_user_id)
        self.assertEqual(request['request_type'], "데이터 삭제 요청")
        self.assertEqual(request['reason'], "서비스 이용 중단")
    
    def test_data_portability(self):
        """데이터 이전 요청 테스트"""
        # 데이터 이전 요청
        request_id = privacy_service.request_data_portability(
            user_id=self.test_user_id,
            destination_service="다른 서비스",
            data_types=[PersonalDataType.IDENTIFIER, PersonalDataType.SENSITIVE]
        )
        
        # 요청 ID가 생성되었는지 확인
        self.assertIsNotNone(request_id)
        self.assertIsInstance(request_id, str)
        self.assertTrue(len(request_id) > 0)
        
        # 요청 조회
        request = privacy_service.get_data_request(request_id)
        self.assertIsNotNone(request)
        self.assertEqual(request['user_id'], self.test_user_id)
        self.assertEqual(request['request_type'], "데이터 이전 요청")
        self.assertEqual(request['destination_service'], "다른 서비스")
    
    def test_privacy_policy(self):
        """개인정보 처리방침 테스트"""
        # 개인정보 처리방침 조회
        policy = privacy_service.get_privacy_policy()
        
        # 정책이 조회되었는지 확인
        self.assertIsNotNone(policy)
        self.assertIsInstance(policy, dict)
        self.assertIn('version', policy)
        self.assertIn('company_name', policy)
        self.assertIn('last_updated', policy)
        self.assertIn('data_collection', policy)
        self.assertIn('data_usage', policy)
        self.assertIn('data_sharing', policy)
        self.assertIn('data_retention', policy)
        self.assertIn('user_rights', policy)
        self.assertIn('contact_info', policy)
    
    def test_data_retention_policy(self):
        """데이터 보존 정책 테스트"""
        # 데이터 보존 정책 조회
        retention_policy = privacy_service.get_data_retention_policy()
        
        # 정책이 조회되었는지 확인
        self.assertIsNotNone(retention_policy)
        self.assertIsInstance(retention_policy, dict)
        self.assertIn('default_retention_days', retention_policy)
        self.assertIn('data_types', retention_policy)
        self.assertIn('retention_rules', retention_policy)
    
    def test_data_anonymization(self):
        """데이터 익명화 테스트"""
        # 개인정보 수집
        data_id = privacy_service.collect_personal_data(
            user_id=self.test_user_id,
            data_type=PersonalDataType.IDENTIFIER,
            data_value=self.test_data_value,
            purpose=ProcessingPurpose.SERVICE_PROVISION
        )
        
        # 데이터 익명화
        anonymized_id = privacy_service.anonymize_personal_data(data_id)
        
        # 익명화 ID가 생성되었는지 확인
        self.assertIsNotNone(anonymized_id)
        self.assertIsInstance(anonymized_id, str)
        self.assertTrue(len(anonymized_id) > 0)
        
        # 익명화된 데이터 조회
        anonymized_data = privacy_service.get_personal_data(anonymized_id)
        self.assertIsNotNone(anonymized_data)
        self.assertNotEqual(anonymized_data['data_value'], self.test_data_value)
    
    def test_data_breach_notification(self):
        """데이터 유출 통지 테스트"""
        # 데이터 유출 사고 등록
        breach_id = privacy_service.report_data_breach(
            description="개인정보 유출 사고",
            affected_users=100,
            data_types=[PersonalDataType.IDENTIFIER, PersonalDataType.SENSITIVE],
            discovery_date=datetime.now(),
            containment_date=datetime.now() + timedelta(hours=2),
            impact_assessment="중간 수준의 위험"
        )
        
        # 사고 ID가 생성되었는지 확인
        self.assertIsNotNone(breach_id)
        self.assertIsInstance(breach_id, str)
        self.assertTrue(len(breach_id) > 0)
        
        # 사고 조회
        breach = privacy_service.get_data_breach(breach_id)
        self.assertIsNotNone(breach)
        self.assertEqual(breach['description'], "개인정보 유출 사고")
        self.assertEqual(breach['affected_users'], 100)
        self.assertIn(PersonalDataType.IDENTIFIER.value, breach['data_types'])
        self.assertIn(PersonalDataType.SENSITIVE.value, breach['data_types'])
    
    def test_privacy_impact_assessment(self):
        """개인정보 영향평가 테스트"""
        # 영향평가 수행
        assessment_id = privacy_service.perform_privacy_impact_assessment(
            project_name="새로운 기능 개발",
            data_types=[PersonalDataType.IDENTIFIER, PersonalDataType.SENSITIVE],
            processing_purposes=[ProcessingPurpose.SERVICE_PROVISION, ProcessingPurpose.MARKETING],
            data_subjects=1000,
            data_retention_days=365
        )
        
        # 평가 ID가 생성되었는지 확인
        self.assertIsNotNone(assessment_id)
        self.assertIsInstance(assessment_id, str)
        self.assertTrue(len(assessment_id) > 0)
        
        # 평가 조회
        assessment = privacy_service.get_privacy_impact_assessment(assessment_id)
        self.assertIsNotNone(assessment)
        self.assertEqual(assessment['project_name'], "새로운 기능 개발")
        self.assertEqual(assessment['data_subjects'], 1000)
        self.assertEqual(assessment['data_retention_days'], 365)
    
    def test_consent_audit_trail(self):
        """동의 감사 추적 테스트"""
        # 동의 부여
        consent_id = privacy_service.grant_consent(
            user_id=self.test_user_id,
            purpose=ProcessingPurpose.SERVICE_PROVISION,
            data_types=[PersonalDataType.IDENTIFIER],
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        # 동의 철회
        privacy_service.withdraw_consent(consent_id)
        
        # 감사 추적 조회
        audit_trail = privacy_service.get_consent_audit_trail(consent_id)
        
        # 감사 추적이 조회되었는지 확인
        self.assertIsNotNone(audit_trail)
        self.assertIsInstance(audit_trail, list)
        self.assertTrue(len(audit_trail) >= 2)  # 부여 + 철회
        
        # 첫 번째 이벤트 (부여)
        self.assertEqual(audit_trail[0]['action'], 'granted')
        self.assertEqual(audit_trail[0]['user_id'], self.test_user_id)
        
        # 두 번째 이벤트 (철회)
        self.assertEqual(audit_trail[1]['action'], 'withdrawn')
        self.assertEqual(audit_trail[1]['user_id'], self.test_user_id)

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
