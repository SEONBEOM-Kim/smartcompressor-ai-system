#!/usr/bin/env python3
"""
백업 및 복구 시스템 단위 테스트
데이터 백업, 복구, 스케줄링 등을 테스트합니다.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 보안 서비스 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from security.services.backup_recovery_service import backup_recovery_service, BackupType, StorageType

class TestBackupRecoveryService(unittest.TestCase):
    """백업 및 복구 서비스 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.test_config_name = "test_backup_config"
        self.test_source_paths = ["/tmp/test_data"]
        self.test_destination = "/tmp/backups"
        self.test_retention_days = 7
    
    def test_backup_config_creation(self):
        """백업 설정 생성 테스트"""
        # 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name=self.test_config_name,
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days
        )
        
        # 설정 ID가 생성되었는지 확인
        self.assertIsNotNone(config_id)
        self.assertIsInstance(config_id, str)
        self.assertTrue(len(config_id) > 0)
        
        # 설정 조회
        config = backup_recovery_service.get_backup_config(config_id)
        self.assertIsNotNone(config)
        self.assertEqual(config['name'], self.test_config_name)
        self.assertEqual(config['backup_type'], BackupType.FULL.value)
        self.assertEqual(config['source_paths'], self.test_source_paths)
        self.assertEqual(config['destination'], self.test_destination)
        self.assertEqual(config['storage_type'], StorageType.LOCAL.value)
        self.assertEqual(config['schedule'], "manual")
        self.assertEqual(config['retention_days'], self.test_retention_days)
    
    def test_backup_execution(self):
        """백업 실행 테스트"""
        # 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name=self.test_config_name,
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days
        )
        
        # 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        
        # 백업 ID가 생성되었는지 확인
        self.assertIsNotNone(backup_id)
        self.assertIsInstance(backup_id, str)
        self.assertTrue(len(backup_id) > 0)
        
        # 백업 조회
        backup = backup_recovery_service.get_backup(backup_id)
        self.assertIsNotNone(backup)
        self.assertEqual(backup['config_id'], config_id)
        self.assertEqual(backup['backup_type'], BackupType.FULL.value)
        self.assertEqual(backup['status'], "completed")
    
    def test_backup_scheduling(self):
        """백업 스케줄링 테스트"""
        # 스케줄된 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name="scheduled_backup",
            backup_type=BackupType.INCREMENTAL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="daily",
            retention_days=self.test_retention_days
        )
        
        # 스케줄된 백업 목록 조회
        scheduled_backups = backup_recovery_service.get_scheduled_backups()
        
        # 스케줄된 백업이 조회되었는지 확인
        self.assertIsNotNone(scheduled_backups)
        self.assertIsInstance(scheduled_backups, list)
        self.assertTrue(len(scheduled_backups) > 0)
        
        # 스케줄된 백업 정보 확인
        scheduled_backup = scheduled_backups[0]
        self.assertEqual(scheduled_backup['config_id'], config_id)
        self.assertEqual(scheduled_backup['schedule'], "daily")
        self.assertIn('next_run', scheduled_backup)
    
    def test_backup_restoration(self):
        """백업 복구 테스트"""
        # 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name=self.test_config_name,
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days
        )
        
        # 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        
        # 백업 복구
        restore_id = backup_recovery_service.restore_backup(
            backup_id=backup_id,
            destination="/tmp/restored_data",
            overwrite=True
        )
        
        # 복구 ID가 생성되었는지 확인
        self.assertIsNotNone(restore_id)
        self.assertIsInstance(restore_id, str)
        self.assertTrue(len(restore_id) > 0)
        
        # 복구 조회
        restore = backup_recovery_service.get_restore(restore_id)
        self.assertIsNotNone(restore)
        self.assertEqual(restore['backup_id'], backup_id)
        self.assertEqual(restore['destination'], "/tmp/restored_data")
        self.assertTrue(restore['overwrite'])
        self.assertEqual(restore['status'], "completed")
    
    def test_backup_verification(self):
        """백업 검증 테스트"""
        # 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name=self.test_config_name,
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days
        )
        
        # 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        
        # 백업 검증
        verification_result = backup_recovery_service.verify_backup(backup_id)
        
        # 검증 결과 확인
        self.assertIsNotNone(verification_result)
        self.assertIsInstance(verification_result, dict)
        self.assertIn('is_valid', verification_result)
        self.assertIn('checksum', verification_result)
        self.assertIn('file_count', verification_result)
        self.assertIn('total_size', verification_result)
        self.assertIn('verification_time', verification_result)
        
        # 검증 성공 확인
        self.assertTrue(verification_result['is_valid'])
        self.assertIsNotNone(verification_result['checksum'])
        self.assertGreater(verification_result['file_count'], 0)
        self.assertGreater(verification_result['total_size'], 0)
    
    def test_backup_encryption(self):
        """백업 암호화 테스트"""
        # 암호화된 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name="encrypted_backup",
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days,
            encryption_enabled=True,
            encryption_key="test_encryption_key"
        )
        
        # 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        
        # 백업 조회
        backup = backup_recovery_service.get_backup(backup_id)
        self.assertIsNotNone(backup)
        self.assertTrue(backup['encryption_enabled'])
        self.assertEqual(backup['encryption_key'], "test_encryption_key")
    
    def test_backup_compression(self):
        """백업 압축 테스트"""
        # 압축된 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name="compressed_backup",
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days,
            compression_enabled=True,
            compression_level=6
        )
        
        # 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        
        # 백업 조회
        backup = backup_recovery_service.get_backup(backup_id)
        self.assertIsNotNone(backup)
        self.assertTrue(backup['compression_enabled'])
        self.assertEqual(backup['compression_level'], 6)
    
    def test_backup_retention(self):
        """백업 보존 정책 테스트"""
        # 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name=self.test_config_name,
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days
        )
        
        # 여러 백업 실행
        backup_ids = []
        for i in range(5):
            backup_id = backup_recovery_service.execute_backup(config_id)
            backup_ids.append(backup_id)
        
        # 백업 목록 조회
        backups = backup_recovery_service.list_backups()
        self.assertIsInstance(backups, list)
        self.assertTrue(len(backups) >= 5)
        
        # 만료된 백업 정리
        cleaned_count = backup_recovery_service.cleanup_expired_backups()
        self.assertGreaterEqual(cleaned_count, 0)
    
    def test_backup_statistics(self):
        """백업 통계 테스트"""
        # 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name=self.test_config_name,
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days
        )
        
        # 여러 백업 실행
        for i in range(3):
            backup_recovery_service.execute_backup(config_id)
        
        # 백업 통계 조회
        stats = backup_recovery_service.get_backup_statistics()
        
        # 통계가 조회되었는지 확인
        self.assertIsNotNone(stats)
        self.assertIsInstance(stats, dict)
        self.assertIn('total_jobs', stats)
        self.assertIn('completed_jobs', stats)
        self.assertIn('failed_jobs', stats)
        self.assertIn('total_size', stats)
        self.assertIn('average_duration', stats)
        self.assertIn('success_rate', stats)
        self.assertIn('backup_types', stats)
        self.assertIn('storage_types', stats)
        
        # 통계 값 확인
        self.assertGreaterEqual(stats['total_jobs'], 3)
        self.assertGreaterEqual(stats['completed_jobs'], 3)
        self.assertGreaterEqual(stats['success_rate'], 0)
        self.assertLessEqual(stats['success_rate'], 100)
    
    def test_disaster_recovery(self):
        """재해 복구 테스트"""
        # 재해 복구 계획 생성
        plan_id = backup_recovery_service.create_disaster_recovery_plan(
            name="test_dr_plan",
            description="테스트 재해 복구 계획",
            rto_hours=4,  # 복구 목표 시간
            rpo_hours=1,  # 복구 시점 목표
            critical_systems=["database", "application", "web"],
            backup_configs=["config1", "config2"],
            recovery_procedures=["step1", "step2", "step3"]
        )
        
        # 계획 ID가 생성되었는지 확인
        self.assertIsNotNone(plan_id)
        self.assertIsInstance(plan_id, str)
        self.assertTrue(len(plan_id) > 0)
        
        # 계획 조회
        plan = backup_recovery_service.get_disaster_recovery_plan(plan_id)
        self.assertIsNotNone(plan)
        self.assertEqual(plan['name'], "test_dr_plan")
        self.assertEqual(plan['description'], "테스트 재해 복구 계획")
        self.assertEqual(plan['rto_hours'], 4)
        self.assertEqual(plan['rpo_hours'], 1)
        self.assertEqual(plan['critical_systems'], ["database", "application", "web"])
        self.assertEqual(plan['backup_configs'], ["config1", "config2"])
        self.assertEqual(plan['recovery_procedures'], ["step1", "step2", "step3"])
    
    def test_backup_monitoring(self):
        """백업 모니터링 테스트"""
        # 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name=self.test_config_name,
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days
        )
        
        # 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        
        # 백업 모니터링 데이터 조회
        monitoring_data = backup_recovery_service.get_backup_monitoring_data()
        
        # 모니터링 데이터가 조회되었는지 확인
        self.assertIsNotNone(monitoring_data)
        self.assertIsInstance(monitoring_data, dict)
        self.assertIn('active_backups', monitoring_data)
        self.assertIn('failed_backups', monitoring_data)
        self.assertIn('storage_usage', monitoring_data)
        self.assertIn('performance_metrics', monitoring_data)
        self.assertIn('alerts', monitoring_data)
        
        # 모니터링 데이터 값 확인
        self.assertIsInstance(monitoring_data['active_backups'], list)
        self.assertIsInstance(monitoring_data['failed_backups'], list)
        self.assertIsInstance(monitoring_data['storage_usage'], dict)
        self.assertIsInstance(monitoring_data['performance_metrics'], dict)
        self.assertIsInstance(monitoring_data['alerts'], list)
    
    def test_backup_alerting(self):
        """백업 알림 테스트"""
        # 백업 설정 생성
        config_id = backup_recovery_service.create_backup_config(
            name=self.test_config_name,
            backup_type=BackupType.FULL,
            source_paths=self.test_source_paths,
            destination=self.test_destination,
            storage_type=StorageType.LOCAL,
            schedule="manual",
            retention_days=self.test_retention_days
        )
        
        # 백업 실행
        backup_id = backup_recovery_service.execute_backup(config_id)
        
        # 백업 알림 설정
        alert_id = backup_recovery_service.setup_backup_alerting(
            config_id=config_id,
            alert_types=["backup_failed", "backup_completed", "storage_full"],
            recipients=["admin@example.com", "backup@example.com"],
            notification_methods=["email", "sms"]
        )
        
        # 알림 ID가 생성되었는지 확인
        self.assertIsNotNone(alert_id)
        self.assertIsInstance(alert_id, str)
        self.assertTrue(len(alert_id) > 0)
        
        # 알림 조회
        alert = backup_recovery_service.get_backup_alert(alert_id)
        self.assertIsNotNone(alert)
        self.assertEqual(alert['config_id'], config_id)
        self.assertEqual(alert['alert_types'], ["backup_failed", "backup_completed", "storage_full"])
        self.assertEqual(alert['recipients'], ["admin@example.com", "backup@example.com"])
        self.assertEqual(alert['notification_methods'], ["email", "sms"])

if __name__ == '__main__':
    # 테스트 실행
    unittest.main(verbosity=2)
