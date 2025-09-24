#!/usr/bin/env python3
"""
보안 모니터링 시스템 단위 테스트
보안 이벤트 로깅, 위협 탐지, 모니터링 등을 테스트합니다.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.security_monitoring_service import security_monitoring_service, EventType, ThreatLevel

class TestSecurityMonitoringService(unittest.TestCase):
    """보안 모니터링 서비스 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_user_id = "test_user_001"
        self.test_ip = "192.168.1.100"
        self.test_endpoint = "/api/auth/login"
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def test_security_event_logging(self):
        """보안 이벤트 로깅 테스트"""
        # 보안 이벤트 로깅
        event_id = security_monitoring_service.log_security_event(
            event_type=EventType.AUTHENTICATION_FAILURE,
            threat_level=ThreatLevel.MEDIUM,
            source_ip=self.test_ip,
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            description="인증 실패 시도",
            details={"attempts": 3, "username": "test_user"}
        )
        
        # 이벤트 ID가 생성되었는지 확인
        self.assertIsNotNone(event_id)
        self.assertIsInstance(event_id, str)
        self.assertTrue(len(event_id) > 0)
        
        # 이벤트 조회
        event = security_monitoring_service.get_security_event(event_id)
        self.assertIsNotNone(event)
        self.assertEqual(event['event_type'], EventType.AUTHENTICATION_FAILURE.value)
        self.assertEqual(event['threat_level'], ThreatLevel.MEDIUM.value)
        self.assertEqual(event['source_ip'], self.test_ip)
        self.assertEqual(event['user_id'], self.test_user_id)
        self.assertEqual(event['endpoint'], self.test_endpoint)
        self.assertEqual(event['description'], "인증 실패 시도")
    
    def test_security_events_query(self):
        """보안 이벤트 조회 테스트"""
        # 여러 이벤트 로깅
        event_ids = []
        for i in range(5):
            event_id = security_monitoring_service.log_security_event(
                event_type=EventType.AUTHENTICATION_FAILURE,
                threat_level=ThreatLevel.LOW,
                source_ip=f"192.168.1.{100 + i}",
                user_id=f"test_user_{i:03d}",
                endpoint=self.test_endpoint,
                description=f"인증 실패 시도 {i+1}",
                details={"attempts": i+1}
            )
            event_ids.append(event_id)
        
        # 이벤트 목록 조회
        events = security_monitoring_service.get_security_events(limit=10)
        self.assertIsInstance(events, list)
        self.assertTrue(len(events) >= 5)
        
        # 특정 사용자의 이벤트 조회
        user_events = security_monitoring_service.get_security_events(
            user_id=self.test_user_id,
            limit=10
        )
        self.assertIsInstance(user_events, list)
        
        # 특정 IP의 이벤트 조회
        ip_events = security_monitoring_service.get_security_events(
            source_ip=self.test_ip,
            limit=10
        )
        self.assertIsInstance(ip_events, list)
    
    def test_security_statistics(self):
        """보안 통계 테스트"""
        # 여러 이벤트 로깅
        for i in range(10):
            security_monitoring_service.log_security_event(
                event_type=EventType.AUTHENTICATION_FAILURE,
                threat_level=ThreatLevel.LOW,
                source_ip=f"192.168.1.{100 + i}",
                user_id=f"test_user_{i:03d}",
                endpoint=self.test_endpoint,
                description=f"인증 실패 시도 {i+1}",
                details={"attempts": i+1}
            )
        
        # 보안 통계 조회
        stats = security_monitoring_service.get_security_statistics()
        
        # 통계가 조회되었는지 확인
        self.assertIsNotNone(stats)
        self.assertIsInstance(stats, dict)
        self.assertIn('total_events', stats)
        self.assertIn('threat_levels', stats)
        self.assertIn('event_types', stats)
        self.assertIn('top_ips', stats)
        self.assertIn('top_users', stats)
        self.assertIn('top_endpoints', stats)
        
        # 통계 값 확인
        self.assertGreaterEqual(stats['total_events'], 10)
        self.assertIsInstance(stats['threat_levels'], dict)
        self.assertIsInstance(stats['event_types'], dict)
        self.assertIsInstance(stats['top_ips'], list)
        self.assertIsInstance(stats['top_users'], list)
        self.assertIsInstance(stats['top_endpoints'], list)
    
    def test_threat_detection(self):
        """위협 탐지 테스트"""
        # 브루트 포스 공격 시뮬레이션
        for i in range(10):
            security_monitoring_service.log_security_event(
                event_type=EventType.AUTHENTICATION_FAILURE,
                threat_level=ThreatLevel.MEDIUM,
                source_ip=self.test_ip,
                user_id=self.test_user_id,
                endpoint=self.test_endpoint,
                description=f"브루트 포스 공격 시도 {i+1}",
                details={"attempts": i+1, "username": "test_user"}
            )
        
        # 위협 탐지
        threats = security_monitoring_service.detect_threats()
        
        # 위협이 탐지되었는지 확인
        self.assertIsNotNone(threats)
        self.assertIsInstance(threats, list)
        self.assertTrue(len(threats) > 0)
        
        # 브루트 포스 공격이 탐지되었는지 확인
        brute_force_detected = any(
            threat['threat_type'] == 'brute_force' for threat in threats
        )
        self.assertTrue(brute_force_detected)
    
    def test_alert_generation(self):
        """알림 생성 테스트"""
        # 고위험 이벤트 로깅
        event_id = security_monitoring_service.log_security_event(
            event_type=EventType.BRUTE_FORCE,
            threat_level=ThreatLevel.HIGH,
            source_ip=self.test_ip,
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            description="브루트 포스 공격 감지",
            details={"attempts": 20, "username": "test_user"}
        )
        
        # 알림 생성
        alert_id = security_monitoring_service.generate_alert(
            event_id=event_id,
            alert_type="security_incident",
            priority="high",
            message="브루트 포스 공격이 감지되었습니다.",
            recipients=["admin@example.com", "security@example.com"]
        )
        
        # 알림 ID가 생성되었는지 확인
        self.assertIsNotNone(alert_id)
        self.assertIsInstance(alert_id, str)
        self.assertTrue(len(alert_id) > 0)
        
        # 알림 조회
        alert = security_monitoring_service.get_alert(alert_id)
        self.assertIsNotNone(alert)
        self.assertEqual(alert['event_id'], event_id)
        self.assertEqual(alert['alert_type'], "security_incident")
        self.assertEqual(alert['priority'], "high")
        self.assertEqual(alert['message'], "브루트 포스 공격이 감지되었습니다.")
    
    def test_security_dashboard_data(self):
        """보안 대시보드 데이터 테스트"""
        # 다양한 이벤트 로깅
        event_types = [
            EventType.AUTHENTICATION_FAILURE,
            EventType.AUTHENTICATION_SUCCESS,
            EventType.BRUTE_FORCE,
            EventType.SUSPICIOUS_ACTIVITY,
            EventType.DATA_ACCESS
        ]
        
        threat_levels = [ThreatLevel.LOW, ThreatLevel.MEDIUM, ThreatLevel.HIGH, ThreatLevel.CRITICAL]
        
        for i, event_type in enumerate(event_types):
            for j, threat_level in enumerate(threat_levels):
                security_monitoring_service.log_security_event(
                    event_type=event_type,
                    threat_level=threat_level,
                    source_ip=f"192.168.1.{100 + i}",
                    user_id=f"test_user_{i:03d}",
                    endpoint=f"/api/endpoint_{i}",
                    description=f"테스트 이벤트 {i}-{j}",
                    details={"test": True}
                )
        
        # 대시보드 데이터 조회
        dashboard_data = security_monitoring_service.get_dashboard_data()
        
        # 대시보드 데이터가 조회되었는지 확인
        self.assertIsNotNone(dashboard_data)
        self.assertIsInstance(dashboard_data, dict)
        self.assertIn('recent_events', dashboard_data)
        self.assertIn('threat_levels', dashboard_data)
        self.assertIn('event_types', dashboard_data)
        self.assertIn('top_ips', dashboard_data)
        self.assertIn('top_users', dashboard_data)
        self.assertIn('alerts', dashboard_data)
        self.assertIn('statistics', dashboard_data)
    
    def test_security_incident_management(self):
        """보안 사고 관리 테스트"""
        # 보안 사고 등록
        incident_id = security_monitoring_service.create_security_incident(
            title="브루트 포스 공격 사고",
            description="다수의 인증 실패 시도가 감지되었습니다.",
            severity="high",
            affected_systems=["authentication", "user_management"],
            assigned_to="security_team",
            status="open"
        )
        
        # 사고 ID가 생성되었는지 확인
        self.assertIsNotNone(incident_id)
        self.assertIsInstance(incident_id, str)
        self.assertTrue(len(incident_id) > 0)
        
        # 사고 조회
        incident = security_monitoring_service.get_security_incident(incident_id)
        self.assertIsNotNone(incident)
        self.assertEqual(incident['title'], "브루트 포스 공격 사고")
        self.assertEqual(incident['description'], "다수의 인증 실패 시도가 감지되었습니다.")
        self.assertEqual(incident['severity'], "high")
        self.assertEqual(incident['status'], "open")
        
        # 사고 업데이트
        updated = security_monitoring_service.update_security_incident(
            incident_id=incident_id,
            status="investigating",
            notes="조사 중입니다.",
            updated_by="security_analyst"
        )
        self.assertTrue(updated)
        
        # 업데이트된 사고 조회
        updated_incident = security_monitoring_service.get_security_incident(incident_id)
        self.assertEqual(updated_incident['status'], "investigating")
        self.assertEqual(updated_incident['notes'], "조사 중입니다.")
    
    def test_security_metrics(self):
        """보안 메트릭 테스트"""
        # 메트릭 수집
        metrics = security_monitoring_service.collect_security_metrics()
        
        # 메트릭이 수집되었는지 확인
        self.assertIsNotNone(metrics)
        self.assertIsInstance(metrics, dict)
        self.assertIn('total_events', metrics)
        self.assertIn('threat_levels', metrics)
        self.assertIn('event_types', metrics)
        self.assertIn('response_times', metrics)
        self.assertIn('error_rates', metrics)
        self.assertIn('system_health', metrics)
    
    def test_security_audit_log(self):
        """보안 감사 로그 테스트"""
        # 감사 로그 조회
        audit_logs = security_monitoring_service.get_security_audit_logs()
        
        # 감사 로그가 조회되었는지 확인
        self.assertIsNotNone(audit_logs)
        self.assertIsInstance(audit_logs, list)
        
        # 각 로그 항목 확인
        for log in audit_logs:
            self.assertIn('timestamp', log)
            self.assertIn('user_id', log)
            self.assertIn('action', log)
            self.assertIn('resource', log)
            self.assertIn('ip_address', log)
            self.assertIn('user_agent', log)
            self.assertIn('success', log)
    
    def test_security_compliance(self):
        """보안 규정 준수 테스트"""
        # 규정 준수 상태 조회
        compliance = security_monitoring_service.get_security_compliance()
        
        # 규정 준수 상태가 조회되었는지 확인
        self.assertIsNotNone(compliance)
        self.assertIsInstance(compliance, dict)
        self.assertIn('overall_score', compliance)
        self.assertIn('compliance_items', compliance)
        self.assertIn('last_audit', compliance)
        self.assertIn('next_audit', compliance)
        self.assertIn('recommendations', compliance)
        
        # 전체 점수 확인
        self.assertIsInstance(compliance['overall_score'], (int, float))
        self.assertGreaterEqual(compliance['overall_score'], 0)
        self.assertLessEqual(compliance['overall_score'], 100)

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
