#!/usr/bin/env python3
"""
침입 탐지 시스템 단위 테스트
네트워크 트래픽 분석, 사용자 행동 분석, 침입 탐지 등을 테스트합니다.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.intrusion_detection_service import intrusion_detection_service, AttackType

class TestIntrusionDetectionService(unittest.TestCase):
    """침입 탐지 서비스 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_user_id = "test_user_001"
        self.test_ip = "192.168.1.100"
        self.test_endpoint = "/api/auth/login"
        self.test_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    def test_network_traffic_logging(self):
        """네트워크 트래픽 로깅 테스트"""
        # 네트워크 트래픽 로깅
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
        
        # 트래픽 ID가 생성되었는지 확인
        self.assertIsNotNone(traffic_id)
        self.assertIsInstance(traffic_id, str)
        self.assertTrue(len(traffic_id) > 0)
        
        # 트래픽 조회
        traffic = intrusion_detection_service.get_network_traffic(traffic_id)
        self.assertIsNotNone(traffic)
        self.assertEqual(traffic['source_ip'], self.test_ip)
        self.assertEqual(traffic['dest_ip'], "192.168.1.1")
        self.assertEqual(traffic['port'], 80)
        self.assertEqual(traffic['protocol'], "TCP")
        self.assertEqual(traffic['bytes_sent'], 1024)
        self.assertEqual(traffic['bytes_received'], 2048)
        self.assertEqual(traffic['duration'], 1.5)
        self.assertEqual(traffic['flags'], "SYN,ACK")
    
    def test_user_behavior_logging(self):
        """사용자 행동 로깅 테스트"""
        # 사용자 행동 로깅
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
        
        # 행동 ID가 생성되었는지 확인
        self.assertIsNotNone(behavior_id)
        self.assertIsInstance(behavior_id, str)
        self.assertTrue(len(behavior_id) > 0)
        
        # 행동 조회
        behavior = intrusion_detection_service.get_user_behavior(behavior_id)
        self.assertIsNotNone(behavior)
        self.assertEqual(behavior['user_id'], self.test_user_id)
        self.assertEqual(behavior['action'], "login")
        self.assertEqual(behavior['endpoint'], self.test_endpoint)
        self.assertEqual(behavior['ip_address'], self.test_ip)
        self.assertEqual(behavior['user_agent'], self.test_user_agent)
        self.assertTrue(behavior['success'])
        self.assertEqual(behavior['response_time'], 0.5)
        self.assertEqual(behavior['data_size'], 1024)
    
    def test_anomaly_detection(self):
        """이상 행동 탐지 테스트"""
        # 정상 행동 로깅
        for i in range(10):
            intrusion_detection_service.log_user_behavior(
                user_id=self.test_user_id,
                action="login",
                endpoint=self.test_endpoint,
                ip_address=self.test_ip,
                user_agent=self.test_user_agent,
                success=True,
                response_time=0.5,
                data_size=1024
            )
        
        # 이상 행동 로깅 (다른 IP에서 접근)
        intrusion_detection_service.log_user_behavior(
            user_id=self.test_user_id,
            action="login",
            endpoint=self.test_endpoint,
            ip_address="192.168.1.200",  # 다른 IP
            user_agent=self.test_user_agent,
            success=True,
            response_time=0.5,
            data_size=1024
        )
        
        # 이상 행동 탐지
        anomalies = intrusion_detection_service.detect_anomalies()
        
        # 이상 행동이 탐지되었는지 확인
        self.assertIsNotNone(anomalies)
        self.assertIsInstance(anomalies, list)
        self.assertTrue(len(anomalies) > 0)
        
        # IP 변경 이상 행동이 탐지되었는지 확인
        ip_anomaly_detected = any(
            anomaly['anomaly_type'] == 'ip_change' for anomaly in anomalies
        )
        self.assertTrue(ip_anomaly_detected)
    
    def test_brute_force_detection(self):
        """브루트 포스 공격 탐지 테스트"""
        # 브루트 포스 공격 시뮬레이션
        for i in range(20):
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
        
        # 브루트 포스 공격 탐지
        brute_force_attacks = intrusion_detection_service.detect_brute_force_attacks()
        
        # 브루트 포스 공격이 탐지되었는지 확인
        self.assertIsNotNone(brute_force_attacks)
        self.assertIsInstance(brute_force_attacks, list)
        self.assertTrue(len(brute_force_attacks) > 0)
        
        # 공격 정보 확인
        attack = brute_force_attacks[0]
        self.assertEqual(attack['attack_type'], AttackType.BRUTE_FORCE.value)
        self.assertEqual(attack['source_ip'], self.test_ip)
        self.assertEqual(attack['target_user'], self.test_user_id)
        self.assertGreaterEqual(attack['attempts'], 20)
    
    def test_ddos_detection(self):
        """DDoS 공격 탐지 테스트"""
        # DDoS 공격 시뮬레이션 (다수의 IP에서 동시 접근)
        for i in range(100):
            intrusion_detection_service.log_network_traffic(
                source_ip=f"192.168.1.{100 + i}",
                dest_ip="192.168.1.1",
                port=80,
                protocol="TCP",
                bytes_sent=1024,
                bytes_received=2048,
                duration=0.1,
                flags="SYN"
            )
        
        # DDoS 공격 탐지
        ddos_attacks = intrusion_detection_service.detect_ddos_attacks()
        
        # DDoS 공격이 탐지되었는지 확인
        self.assertIsNotNone(ddos_attacks)
        self.assertIsInstance(ddos_attacks, list)
        self.assertTrue(len(ddos_attacks) > 0)
        
        # 공격 정보 확인
        attack = ddos_attacks[0]
        self.assertEqual(attack['attack_type'], AttackType.DDOS.value)
        self.assertEqual(attack['target_ip'], "192.168.1.1")
        self.assertEqual(attack['target_port'], 80)
        self.assertGreaterEqual(attack['source_ips'], 100)
    
    def test_sql_injection_detection(self):
        """SQL 인젝션 공격 탐지 테스트"""
        # SQL 인젝션 공격 시뮬레이션
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1' UNION SELECT * FROM users--",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --"
        ]
        
        for payload in sql_injection_payloads:
            intrusion_detection_service.log_user_behavior(
                user_id=self.test_user_id,
                action="search",
                endpoint="/api/search",
                ip_address=self.test_ip,
                user_agent=self.test_user_agent,
                success=False,
                response_time=0.1,
                data_size=len(payload),
                additional_data={"query": payload}
            )
        
        # SQL 인젝션 공격 탐지
        sql_injection_attacks = intrusion_detection_service.detect_sql_injection_attacks()
        
        # SQL 인젝션 공격이 탐지되었는지 확인
        self.assertIsNotNone(sql_injection_attacks)
        self.assertIsInstance(sql_injection_attacks, list)
        self.assertTrue(len(sql_injection_attacks) > 0)
        
        # 공격 정보 확인
        attack = sql_injection_attacks[0]
        self.assertEqual(attack['attack_type'], AttackType.SQL_INJECTION.value)
        self.assertEqual(attack['source_ip'], self.test_ip)
        self.assertEqual(attack['target_user'], self.test_user_id)
        self.assertIn('payload', attack)
    
    def test_xss_detection(self):
        """XSS 공격 탐지 테스트"""
        # XSS 공격 시뮬레이션
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>"
        ]
        
        for payload in xss_payloads:
            intrusion_detection_service.log_user_behavior(
                user_id=self.test_user_id,
                action="comment",
                endpoint="/api/comments",
                ip_address=self.test_ip,
                user_agent=self.test_user_agent,
                success=True,
                response_time=0.1,
                data_size=len(payload),
                additional_data={"content": payload}
            )
        
        # XSS 공격 탐지
        xss_attacks = intrusion_detection_service.detect_xss_attacks()
        
        # XSS 공격이 탐지되었는지 확인
        self.assertIsNotNone(xss_attacks)
        self.assertIsInstance(xss_attacks, list)
        self.assertTrue(len(xss_attacks) > 0)
        
        # 공격 정보 확인
        attack = xss_attacks[0]
        self.assertEqual(attack['attack_type'], AttackType.XSS.value)
        self.assertEqual(attack['source_ip'], self.test_ip)
        self.assertEqual(attack['target_user'], self.test_user_id)
        self.assertIn('payload', attack)
    
    def test_intrusion_events_query(self):
        """침입 이벤트 조회 테스트"""
        # 여러 침입 이벤트 로깅
        event_ids = []
        for i in range(5):
            event_id = intrusion_detection_service.log_intrusion_event(
                attack_type=AttackType.BRUTE_FORCE,
                source_ip=f"192.168.1.{100 + i}",
                target_ip="192.168.1.1",
                target_port=80,
                severity="high",
                description=f"브루트 포스 공격 시도 {i+1}",
                payload="test_payload",
                user_id=f"test_user_{i:03d}",
                endpoint=f"/api/endpoint_{i}",
                additional_data={"test": True}
            )
            event_ids.append(event_id)
        
        # 침입 이벤트 목록 조회
        events = intrusion_detection_service.get_intrusion_events(limit=10)
        self.assertIsInstance(events, list)
        self.assertTrue(len(events) >= 5)
        
        # 특정 공격 타입의 이벤트 조회
        brute_force_events = intrusion_detection_service.get_intrusion_events(
            attack_type=AttackType.BRUTE_FORCE,
            limit=10
        )
        self.assertIsInstance(brute_force_events, list)
        self.assertTrue(len(brute_force_events) >= 5)
        
        # 특정 IP의 이벤트 조회
        ip_events = intrusion_detection_service.get_intrusion_events(
            source_ip="192.168.1.100",
            limit=10
        )
        self.assertIsInstance(ip_events, list)
    
    def test_detection_statistics(self):
        """탐지 통계 테스트"""
        # 다양한 공격 타입의 이벤트 로깅
        attack_types = [
            AttackType.BRUTE_FORCE,
            AttackType.DDOS,
            AttackType.SQL_INJECTION,
            AttackType.XSS,
            AttackType.MALWARE
        ]
        
        for i, attack_type in enumerate(attack_types):
            for j in range(3):
                intrusion_detection_service.log_intrusion_event(
                    attack_type=attack_type,
                    source_ip=f"192.168.1.{100 + i}",
                    target_ip="192.168.1.1",
                    target_port=80,
                    severity="high",
                    description=f"테스트 공격 {i}-{j}",
                    payload="test_payload",
                    user_id=f"test_user_{i:03d}",
                    endpoint=f"/api/endpoint_{i}",
                    additional_data={"test": True}
                )
        
        # 탐지 통계 조회
        stats = intrusion_detection_service.get_detection_statistics()
        
        # 통계가 조회되었는지 확인
        self.assertIsNotNone(stats)
        self.assertIsInstance(stats, dict)
        self.assertIn('total_events', stats)
        self.assertIn('attack_types', stats)
        self.assertIn('severity_levels', stats)
        self.assertIn('top_source_ips', stats)
        self.assertIn('top_target_ips', stats)
        self.assertIn('top_target_ports', stats)
        self.assertIn('top_users', stats)
        self.assertIn('top_endpoints', stats)
        
        # 통계 값 확인
        self.assertGreaterEqual(stats['total_events'], 15)
        self.assertIsInstance(stats['attack_types'], dict)
        self.assertIsInstance(stats['severity_levels'], dict)
        self.assertIsInstance(stats['top_source_ips'], list)
        self.assertIsInstance(stats['top_target_ips'], list)
        self.assertIsInstance(stats['top_target_ports'], list)
        self.assertIsInstance(stats['top_users'], list)
        self.assertIsInstance(stats['top_endpoints'], list)
    
    def test_threat_intelligence(self):
        """위협 인텔리전스 테스트"""
        # 위협 인텔리전스 조회
        threat_intel = intrusion_detection_service.get_threat_intelligence()
        
        # 위협 인텔리전스가 조회되었는지 확인
        self.assertIsNotNone(threat_intel)
        self.assertIsInstance(threat_intel, dict)
        self.assertIn('known_malicious_ips', threat_intel)
        self.assertIn('known_malicious_domains', threat_intel)
        self.assertIn('known_malicious_urls', threat_intel)
        self.assertIn('known_malicious_hashes', threat_intel)
        self.assertIn('threat_actors', threat_intel)
        self.assertIn('attack_patterns', threat_intel)
        self.assertIn('last_updated', threat_intel)
    
    def test_incident_response(self):
        """사고 대응 테스트"""
        # 침입 이벤트 로깅
        event_id = intrusion_detection_service.log_intrusion_event(
            attack_type=AttackType.BRUTE_FORCE,
            source_ip=self.test_ip,
            target_ip="192.168.1.1",
            target_port=80,
            severity="high",
            description="브루트 포스 공격 감지",
            payload="test_payload",
            user_id=self.test_user_id,
            endpoint=self.test_endpoint,
            additional_data={"test": True}
        )
        
        # 사고 대응 조치
        response_id = intrusion_detection_service.create_incident_response(
            event_id=event_id,
            response_type="block_ip",
            description="공격 IP 차단",
            severity="high",
            assigned_to="security_team",
            status="open"
        )
        
        # 대응 ID가 생성되었는지 확인
        self.assertIsNotNone(response_id)
        self.assertIsInstance(response_id, str)
        self.assertTrue(len(response_id) > 0)
        
        # 대응 조회
        response = intrusion_detection_service.get_incident_response(response_id)
        self.assertIsNotNone(response)
        self.assertEqual(response['event_id'], event_id)
        self.assertEqual(response['response_type'], "block_ip")
        self.assertEqual(response['description'], "공격 IP 차단")
        self.assertEqual(response['severity'], "high")
        self.assertEqual(response['status'], "open")

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
