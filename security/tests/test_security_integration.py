#!/usr/bin/env python3
"""
보안 시스템 통합 테스트
여러 보안 서비스 간의 상호작용을 테스트합니다.
"""

import sys
import os
import unittest
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

class TestSecurityIntegration(unittest.TestCase):
    """보안 시스템 통합 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_user_id = "integration_test_user_001"
        self.test_username = "integration_test_user"
        self.test_password = "integration_test_password_123"
        self.test_ip = "192.168.1.100"
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.test_endpoint = "/api/integration/test"
    
    def test_authentication_authorization_integration(self):
        """인증-권한 관리 통합 테스트"""
        # 1. 사용자 인증
        auth_result = authentication_service.authenticate_user(
            username=self.test_username,
            password=self.test_password,
            ip_address=self.test_ip,
            user_agent=self.test_user_agent,
            require_2fa=False
        )
        
        self.assertTrue(auth_result.success)
        self.assertEqual(auth_result.user_id, self.test_user_id)
        self.assertIsNotNone(auth_result.token)
        
        # 2. JWT 토큰 검증
        valid, payload = authentication_service.verify_jwt_token(auth_result.token)
        self.assertTrue(valid)
        self.assertEqual(payload['user_id'], self.test_user_id)
        
        # 3. 권한 확인
        has_permission = authorization_service.check_permission(
            user_id=self.test_user_id,
            permission=Permission.USER_READ,
            resource=Resource.USER
        )
        self.assertTrue(has_permission)
        
        # 4. 보안 이벤트 로깅
        event_id = security_monitoring_service.log_security_event(
            event_type=EventType.AUTHENTICATION_SUCCESS,
            threat_level=ThreatLevel.LOW,
            source_ip=self.test_ip,
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            description="통합 테스트 인증 성공",
            details={"test": "integration"}
        )
        
        self.assertIsNotNone(event_id)
    
    def test_encryption_privacy_integration(self):
        """암호화-개인정보보호 통합 테스트"""
        # 1. 개인정보 수집
        data_id = privacy_service.collect_personal_data(
            user_id=self.test_user_id,
            data_type=PersonalDataType.IDENTIFIER,
            data_value="홍길동",
            purpose=ProcessingPurpose.SERVICE_PROVISION
        )
        
        self.assertIsNotNone(data_id)
        
        # 2. 개인정보 암호화
        personal_data = privacy_service.get_personal_data(data_id)
        encrypted_data = encryption_service.encrypt_string(
            personal_data['data_value'], 
            "privacy_key"
        )
        
        self.assertNotEqual(encrypted_data, personal_data['data_value'])
        
        # 3. 암호화된 데이터 복호화
        decrypted_data = encryption_service.decrypt_string(encrypted_data)
        self.assertEqual(decrypted_data, personal_data['data_value'])
        
        # 4. 개인정보 처리 감사 로그
        audit_logs = privacy_service.get_consent_audit_trail(data_id)
        self.assertIsInstance(audit_logs, list)
    
    def test_monitoring_intrusion_detection_integration(self):
        """모니터링-침입 탐지 통합 테스트"""
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
        
        self.assertIsNotNone(behavior_id)
        
        # 2. 네트워크 트래픽 로깅
        traffic_id = intrusion_detection_service.log_network_traffic(
            source_ip=self.test_ip,
            dest_ip="192.168.1.1",
            port=80,
            protocol="TCP",
            bytes_sent=1024,
            bytes_received=2048,
            duration=1.5,
            flags="SYN,ACK"
        )
        
        self.assertIsNotNone(traffic_id)
        
        # 3. 이상 행동 탐지
        anomalies = intrusion_detection_service.detect_anomalies()
        self.assertIsInstance(anomalies, list)
        
        # 4. 보안 이벤트 로깅
        if anomalies:
            event_id = security_monitoring_service.log_security_event(
                event_type=EventType.SUSPICIOUS_ACTIVITY,
                threat_level=ThreatLevel.MEDIUM,
                source_ip=self.test_ip,
                user_id=self.test_user_id,
                endpoint=self.test_endpoint,
                description="이상 행동 탐지",
                details={"anomalies": len(anomalies)}
            )
            
            self.assertIsNotNone(event_id)
    
    def test_backup_encryption_integration(self):
        """백업-암호화 통합 테스트"""
        # 1. 백업 설정 생성 (암호화 활성화)
        config_id = backup_recovery_service.create_backup_config(
            name="encrypted_integration_backup",
            backup_type=BackupType.FULL,
            source_paths=["/tmp/test_data"],
            destination="/tmp/backups",
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=7,
            encryption_enabled=True,
            encryption_key="backup_encryption_key"
        )
        
        self.assertIsNotNone(config_id)
        
        # 2. 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        self.assertIsNotNone(backup_id)
        
        # 3. 백업 검증
        verification_result = backup_recovery_service.verify_backup(backup_id)
        self.assertTrue(verification_result['is_valid'])
        
        # 4. 백업 복구
        restore_id = backup_recovery_service.restore_backup(
            backup_id=backup_id,
            destination="/tmp/restored_data",
            overwrite=True
        )
        
        self.assertIsNotNone(restore_id)
    
    def test_security_incident_response_integration(self):
        """보안 사고 대응 통합 테스트"""
        # 1. 브루트 포스 공격 시뮬레이션
        for i in range(10):
            intrusion_detection_service.log_user_behavior(
                user_id=self.test_user_id,
                action="login",
                endpoint=self.test_endpoint,
                ip_address=self.test_ip,
                user_agent=self.test_user_agent,
                success=False,  # 실패
                response_time=0.1,
                data_size=512
            )
        
        # 2. 브루트 포스 공격 탐지
        brute_force_attacks = intrusion_detection_service.detect_brute_force_attacks()
        self.assertTrue(len(brute_force_attacks) > 0)
        
        # 3. 보안 이벤트 로깅
        event_id = security_monitoring_service.log_security_event(
            event_type=EventType.BRUTE_FORCE,
            threat_level=ThreatLevel.HIGH,
            source_ip=self.test_ip,
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            description="브루트 포스 공격 감지",
            details={"attempts": 10, "attack_type": "brute_force"}
        )
        
        self.assertIsNotNone(event_id)
        
        # 4. 보안 사고 등록
        incident_id = security_monitoring_service.create_security_incident(
            title="브루트 포스 공격 사고",
            description="다수의 인증 실패 시도가 감지되었습니다.",
            severity="high",
            affected_systems=["authentication", "user_management"],
            assigned_to="security_team",
            status="open"
        )
        
        self.assertIsNotNone(incident_id)
        
        # 5. 사고 대응 조치
        response_id = intrusion_detection_service.create_incident_response(
            event_id=event_id,
            response_type="block_ip",
            description="공격 IP 차단",
            severity="high",
            assigned_to="security_team",
            status="open"
        )
        
        self.assertIsNotNone(response_id)
    
    def test_privacy_compliance_integration(self):
        """개인정보보호 규정 준수 통합 테스트"""
        # 1. 개인정보 수집
        data_id = privacy_service.collect_personal_data(
            user_id=self.test_user_id,
            data_type=PersonalDataType.IDENTIFIER,
            data_value="홍길동",
            purpose=ProcessingPurpose.SERVICE_PROVISION
        )
        
        # 2. 동의 부여
        consent_id = privacy_service.grant_consent(
            user_id=self.test_user_id,
            purpose=ProcessingPurpose.SERVICE_PROVISION,
            data_types=[PersonalDataType.IDENTIFIER],
            ip_address=self.test_ip,
            user_agent=self.test_user_agent
        )
        
        # 3. 데이터 주체 요청
        request_id = privacy_service.request_data_access(
            user_id=self.test_user_id,
            request_type="개인정보 열람 요청"
        )
        
        # 4. 개인정보 처리방침 조회
        policy = privacy_service.get_privacy_policy()
        self.assertIsNotNone(policy)
        
        # 5. 데이터 보존 정책 조회
        retention_policy = privacy_service.get_data_retention_policy()
        self.assertIsNotNone(retention_policy)
        
        # 6. 개인정보 영향평가
        assessment_id = privacy_service.perform_privacy_impact_assessment(
            project_name="통합 테스트 프로젝트",
            data_types=[PersonalDataType.IDENTIFIER],
            processing_purposes=[ProcessingPurpose.SERVICE_PROVISION],
            data_subjects=100,
            data_retention_days=365
        )
        
        self.assertIsNotNone(assessment_id)
    
    def test_security_metrics_integration(self):
        """보안 메트릭 통합 테스트"""
        # 1. 보안 이벤트 로깅
        for i in range(5):
            security_monitoring_service.log_security_event(
                event_type=EventType.AUTHENTICATION_FAILURE,
                threat_level=ThreatLevel.MEDIUM,
                source_ip=f"192.168.1.{100 + i}",
                user_id=f"test_user_{i:03d}",
                endpoint=self.test_endpoint,
                description=f"인증 실패 시도 {i+1}",
                details={"attempts": i+1}
            )
        
        # 2. 보안 통계 조회
        security_stats = security_monitoring_service.get_security_statistics()
        self.assertIsNotNone(security_stats)
        
        # 3. 침입 탐지 통계 조회
        intrusion_stats = intrusion_detection_service.get_detection_statistics()
        self.assertIsNotNone(intrusion_stats)
        
        # 4. 백업 통계 조회
        backup_stats = backup_recovery_service.get_backup_statistics()
        self.assertIsNotNone(backup_stats)
        
        # 5. 종합 보안 메트릭
        overall_metrics = {
            'security_events': security_stats.get('total_events', 0),
            'intrusion_events': intrusion_stats.get('total_events', 0),
            'backup_jobs': backup_stats.get('total_jobs', 0),
            'success_rate': backup_stats.get('success_rate', 0)
        }
        
        self.assertIsInstance(overall_metrics, dict)
        self.assertIn('security_events', overall_metrics)
        self.assertIn('intrusion_events', overall_metrics)
        self.assertIn('backup_jobs', overall_metrics)
        self.assertIn('success_rate', overall_metrics)
    
    def test_security_alerting_integration(self):
        """보안 알림 통합 테스트"""
        # 1. 고위험 이벤트 로깅
        event_id = security_monitoring_service.log_security_event(
            event_type=EventType.BRUTE_FORCE,
            threat_level=ThreatLevel.CRITICAL,
            source_ip=self.test_ip,
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            description="치명적인 브루트 포스 공격 감지",
            details={"attempts": 100, "username": "admin"}
        )
        
        # 2. 알림 생성
        alert_id = security_monitoring_service.generate_alert(
            event_id=event_id,
            alert_type="security_incident",
            priority="critical",
            message="치명적인 보안 사고가 발생했습니다.",
            recipients=["admin@example.com", "security@example.com", "cto@example.com"]
        )
        
        self.assertIsNotNone(alert_id)
        
        # 3. 침입 탐지 알림
        intrusion_alert_id = intrusion_detection_service.create_incident_response(
            event_id=event_id,
            response_type="emergency_lockdown",
            description="긴급 락다운 실행",
            severity="critical",
            assigned_to="security_team",
            status="executing"
        )
        
        self.assertIsNotNone(intrusion_alert_id)
        
        # 4. 백업 알림 설정
        backup_alert_id = backup_recovery_service.setup_backup_alerting(
            config_id="test_config",
            alert_types=["backup_failed", "backup_completed"],
            recipients=["admin@example.com"],
            notification_methods=["email", "sms"]
        )
        
        self.assertIsNotNone(backup_alert_id)
    
    def test_security_audit_integration(self):
        """보안 감사 통합 테스트"""
        # 1. 인증 감사 로그
        auth_audit = authentication_service.get_audit_logs()
        self.assertIsInstance(auth_audit, list)
        
        # 2. 권한 감사 로그
        authz_audit = authorization_service.get_audit_logs()
        self.assertIsInstance(authz_audit, list)
        
        # 3. 보안 모니터링 감사 로그
        security_audit = security_monitoring_service.get_security_audit_logs()
        self.assertIsInstance(security_audit, list)
        
        # 4. 개인정보 처리 감사 로그
        privacy_audit = privacy_service.get_consent_audit_trail("test_consent_id")
        self.assertIsInstance(privacy_audit, list)
        
        # 5. 종합 감사 로그
        comprehensive_audit = {
            'authentication_events': len(auth_audit),
            'authorization_events': len(authz_audit),
            'security_events': len(security_audit),
            'privacy_events': len(privacy_audit)
        }
        
        self.assertIsInstance(comprehensive_audit, dict)
        self.assertIn('authentication_events', comprehensive_audit)
        self.assertIn('authorization_events', comprehensive_audit)
        self.assertIn('security_events', comprehensive_audit)
        self.assertIn('privacy_events', comprehensive_audit)

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
