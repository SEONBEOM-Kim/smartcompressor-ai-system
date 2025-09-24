#!/usr/bin/env python3
"""
원격 진단 및 제어 서비스
Tesla App을 벤치마킹한 원격 제어 시스템
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ControlCommand(Enum):
    """제어 명령"""
    START_COMPRESSOR = "start_compressor"
    STOP_COMPRESSOR = "stop_compressor"
    ADJUST_TEMPERATURE = "adjust_temperature"
    ADJUST_PRESSURE = "adjust_pressure"
    EMERGENCY_STOP = "emergency_stop"
    RESET_SYSTEM = "reset_system"
    CALIBRATE_SENSORS = "calibrate_sensors"
    UPDATE_FIRMWARE = "update_firmware"

class CommandStatus(Enum):
    """명령 상태"""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DeviceStatus(Enum):
    """장비 상태"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    STANDBY = "standby"

@dataclass
class RemoteCommand:
    """원격 명령 클래스"""
    id: str
    command: ControlCommand
    device_id: str
    store_id: str
    parameters: Dict[str, Any]
    timestamp: datetime
    status: CommandStatus = CommandStatus.PENDING
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    executed_by: str = "system"

@dataclass
class DeviceInfo:
    """장비 정보 클래스"""
    device_id: str
    store_id: str
    device_type: str
    status: DeviceStatus
    last_seen: datetime
    firmware_version: str
    capabilities: List[str]
    current_settings: Dict[str, Any]
    health_score: float = 100.0

class RemoteControlService:
    """원격 제어 서비스"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceInfo] = {}
        self.command_queue: deque = deque()
        self.command_history: List[RemoteCommand] = []
        self.command_callbacks: List[Callable] = []
        self.is_processing = False
        self.processing_thread = None
        
        # 명령 실행 결과 저장소
        self.command_results: Dict[str, Any] = {}
        
        # 장비 상태 모니터링
        self.device_health_checkers: Dict[str, threading.Timer] = {}
        
        # 초기 장비 등록
        self._initialize_devices()
    
    def _initialize_devices(self):
        """초기 장비 등록"""
        # 압축기 장비 등록
        compressor = DeviceInfo(
            device_id="compressor_001",
            store_id="store_001",
            device_type="compressor",
            status=DeviceStatus.ONLINE,
            last_seen=datetime.now(),
            firmware_version="1.2.3",
            capabilities=[
                "start", "stop", "temperature_control", 
                "pressure_control", "emergency_stop", "reset"
            ],
            current_settings={
                "temperature": 25.0,
                "pressure": 2.5,
                "power_level": 80,
                "auto_mode": True
            }
        )
        self.devices[compressor.device_id] = compressor
        
        # 센서 장비 등록
        sensor = DeviceInfo(
            device_id="sensor_001",
            store_id="store_001",
            device_type="sensor",
            status=DeviceStatus.ONLINE,
            last_seen=datetime.now(),
            firmware_version="2.1.0",
            capabilities=[
                "calibrate", "reset", "update_firmware"
            ],
            current_settings={
                "sampling_rate": 1.0,
                "sensitivity": 0.8,
                "auto_calibration": True
            }
        )
        self.devices[sensor.device_id] = sensor
        
        # 장비 상태 모니터링 시작
        self._start_device_health_monitoring()
    
    def _start_device_health_monitoring(self):
        """장비 상태 모니터링 시작"""
        for device_id in self.devices:
            self._schedule_health_check(device_id)
    
    def _schedule_health_check(self, device_id: str):
        """장비 상태 체크 스케줄링"""
        def health_check():
            self._check_device_health(device_id)
            # 30초마다 체크
            self.device_health_checkers[device_id] = threading.Timer(30.0, health_check)
            self.device_health_checkers[device_id].start()
        
        health_check()
    
    def _check_device_health(self, device_id: str):
        """장비 상태 체크"""
        if device_id not in self.devices:
            return
        
        device = self.devices[device_id]
        current_time = datetime.now()
        
        # 마지막 통신 시간 체크
        time_since_last_seen = (current_time - device.last_seen).total_seconds()
        
        if time_since_last_seen > 60:  # 1분 이상 통신 없으면 오프라인
            device.status = DeviceStatus.OFFLINE
            device.health_score = max(0, device.health_score - 10)
        else:
            device.status = DeviceStatus.ONLINE
            device.health_score = min(100, device.health_score + 1)
        
        # 상태 변경 알림
        if device.status == DeviceStatus.OFFLINE:
            logger.warning(f"장비 오프라인: {device_id}")
            self._notify_device_status_change(device_id, DeviceStatus.OFFLINE)
    
    def _notify_device_status_change(self, device_id: str, new_status: DeviceStatus):
        """장비 상태 변경 알림"""
        for callback in self.command_callbacks:
            try:
                callback({
                    'type': 'device_status_change',
                    'device_id': device_id,
                    'status': new_status.value,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"장비 상태 변경 알림 오류: {e}")
    
    async def execute_command(self, command: RemoteCommand) -> bool:
        """명령 실행"""
        try:
            # 명령 유효성 검사
            if not self._validate_command(command):
                return False
            
            # 명령 큐에 추가
            self.command_queue.append(command)
            self.command_history.append(command)
            
            # 명령 처리 시작
            if not self.is_processing:
                self._start_command_processing()
            
            logger.info(f"원격 명령 큐에 추가: {command.command.value} - {command.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"명령 실행 오류: {e}")
            command.status = CommandStatus.FAILED
            command.error_message = str(e)
            return False
    
    def _validate_command(self, command: RemoteCommand) -> bool:
        """명령 유효성 검사"""
        # 장비 존재 확인
        if command.device_id not in self.devices:
            logger.error(f"존재하지 않는 장비: {command.device_id}")
            return False
        
        device = self.devices[command.device_id]
        
        # 장비 상태 확인
        if device.status == DeviceStatus.OFFLINE:
            logger.error(f"오프라인 장비에 명령 실행 불가: {command.device_id}")
            return False
        
        # 명령 지원 여부 확인
        if command.command.value not in device.capabilities:
            logger.error(f"지원하지 않는 명령: {command.command.value}")
            return False
        
        return True
    
    def _start_command_processing(self):
        """명령 처리 시작"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._command_processing_worker, daemon=True)
        self.processing_thread.start()
    
    def _command_processing_worker(self):
        """명령 처리 워커"""
        while self.is_processing and self.command_queue:
            try:
                command = self.command_queue.popleft()
                self._process_command(command)
                
                # 명령 간 간격 (1초)
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"명령 처리 워커 오류: {e}")
                time.sleep(5)
        
        self.is_processing = False
    
    def _process_command(self, command: RemoteCommand):
        """개별 명령 처리"""
        try:
            command.status = CommandStatus.EXECUTING
            command.executed_at = datetime.now()
            
            logger.info(f"명령 실행 시작: {command.command.value} - {command.device_id}")
            
            # 명령 타입별 처리
            success = False
            if command.command == ControlCommand.START_COMPRESSOR:
                success = self._start_compressor(command)
            elif command.command == ControlCommand.STOP_COMPRESSOR:
                success = self._stop_compressor(command)
            elif command.command == ControlCommand.ADJUST_TEMPERATURE:
                success = self._adjust_temperature(command)
            elif command.command == ControlCommand.ADJUST_PRESSURE:
                success = self._adjust_pressure(command)
            elif command.command == ControlCommand.EMERGENCY_STOP:
                success = self._emergency_stop(command)
            elif command.command == ControlCommand.RESET_SYSTEM:
                success = self._reset_system(command)
            elif command.command == ControlCommand.CALIBRATE_SENSORS:
                success = self._calibrate_sensors(command)
            elif command.command == ControlCommand.UPDATE_FIRMWARE:
                success = self._update_firmware(command)
            
            # 명령 결과 처리
            if success:
                command.status = CommandStatus.COMPLETED
                command.completed_at = datetime.now()
                logger.info(f"명령 실행 완료: {command.command.value} - {command.device_id}")
            else:
                command.status = CommandStatus.FAILED
                command.error_message = "명령 실행 실패"
                logger.error(f"명령 실행 실패: {command.command.value} - {command.device_id}")
            
            # 결과 저장
            self.command_results[command.id] = {
                'success': success,
                'timestamp': command.completed_at.isoformat() if command.completed_at else None,
                'error': command.error_message
            }
            
            # 콜백 실행
            self._notify_command_completed(command)
            
        except Exception as e:
            command.status = CommandStatus.FAILED
            command.error_message = str(e)
            logger.error(f"명령 처리 오류: {e}")
    
    def _start_compressor(self, command: RemoteCommand) -> bool:
        """압축기 시작"""
        device = self.devices[command.device_id]
        
        # 압축기 시작 로직 (시뮬레이션)
        time.sleep(2)  # 실제로는 IoT 장비와 통신
        
        # 설정 업데이트
        device.current_settings['power_level'] = command.parameters.get('power_level', 80)
        device.current_settings['auto_mode'] = command.parameters.get('auto_mode', True)
        
        # 상태 업데이트
        device.last_seen = datetime.now()
        device.health_score = min(100, device.health_score + 5)
        
        return True
    
    def _stop_compressor(self, command: RemoteCommand) -> bool:
        """압축기 중지"""
        device = self.devices[command.device_id]
        
        # 압축기 중지 로직 (시뮬레이션)
        time.sleep(1)
        
        # 설정 업데이트
        device.current_settings['power_level'] = 0
        device.current_settings['auto_mode'] = False
        
        # 상태 업데이트
        device.last_seen = datetime.now()
        
        return True
    
    def _adjust_temperature(self, command: RemoteCommand) -> bool:
        """온도 조정"""
        device = self.devices[command.device_id]
        target_temp = command.parameters.get('temperature')
        
        if target_temp is None:
            return False
        
        # 온도 조정 로직 (시뮬레이션)
        time.sleep(1)
        
        # 설정 업데이트
        device.current_settings['temperature'] = target_temp
        
        # 상태 업데이트
        device.last_seen = datetime.now()
        
        return True
    
    def _adjust_pressure(self, command: RemoteCommand) -> bool:
        """압력 조정"""
        device = self.devices[command.device_id]
        target_pressure = command.parameters.get('pressure')
        
        if target_pressure is None:
            return False
        
        # 압력 조정 로직 (시뮬레이션)
        time.sleep(1)
        
        # 설정 업데이트
        device.current_settings['pressure'] = target_pressure
        
        # 상태 업데이트
        device.last_seen = datetime.now()
        
        return True
    
    def _emergency_stop(self, command: RemoteCommand) -> bool:
        """긴급 정지"""
        device = self.devices[command.device_id]
        
        # 긴급 정지 로직 (시뮬레이션)
        time.sleep(0.5)
        
        # 모든 설정 초기화
        device.current_settings['power_level'] = 0
        device.current_settings['auto_mode'] = False
        device.status = DeviceStatus.STANDBY
        
        # 상태 업데이트
        device.last_seen = datetime.now()
        
        logger.warning(f"긴급 정지 실행: {command.device_id}")
        return True
    
    def _reset_system(self, command: RemoteCommand) -> bool:
        """시스템 리셋"""
        device = self.devices[command.device_id]
        
        # 시스템 리셋 로직 (시뮬레이션)
        time.sleep(3)
        
        # 기본 설정으로 복원
        device.current_settings = {
            "temperature": 25.0,
            "pressure": 2.5,
            "power_level": 0,
            "auto_mode": False
        }
        
        # 상태 업데이트
        device.status = DeviceStatus.ONLINE
        device.last_seen = datetime.now()
        device.health_score = 100.0
        
        return True
    
    def _calibrate_sensors(self, command: RemoteCommand) -> bool:
        """센서 보정"""
        device = self.devices[command.device_id]
        
        # 센서 보정 로직 (시뮬레이션)
        time.sleep(5)
        
        # 센서 설정 업데이트
        if 'sensitivity' in command.parameters:
            device.current_settings['sensitivity'] = command.parameters['sensitivity']
        
        # 상태 업데이트
        device.last_seen = datetime.now()
        device.health_score = min(100, device.health_score + 10)
        
        return True
    
    def _update_firmware(self, command: RemoteCommand) -> bool:
        """펌웨어 업데이트"""
        device = self.devices[command.device_id]
        new_version = command.parameters.get('version')
        
        if not new_version:
            return False
        
        # 펌웨어 업데이트 로직 (시뮬레이션)
        time.sleep(10)
        
        # 펌웨어 버전 업데이트
        device.firmware_version = new_version
        
        # 상태 업데이트
        device.last_seen = datetime.now()
        device.health_score = 100.0
        
        logger.info(f"펌웨어 업데이트 완료: {command.device_id} -> {new_version}")
        return True
    
    def _notify_command_completed(self, command: RemoteCommand):
        """명령 완료 알림"""
        for callback in self.command_callbacks:
            try:
                callback({
                    'type': 'command_completed',
                    'command_id': command.id,
                    'command': command.command.value,
                    'device_id': command.device_id,
                    'status': command.status.value,
                    'success': command.status == CommandStatus.COMPLETED,
                    'timestamp': command.completed_at.isoformat() if command.completed_at else None,
                    'error': command.error_message
                })
            except Exception as e:
                logger.error(f"명령 완료 알림 오류: {e}")
    
    def add_command_callback(self, callback: Callable):
        """명령 콜백 함수 추가"""
        self.command_callbacks.append(callback)
    
    def remove_command_callback(self, callback: Callable):
        """명령 콜백 함수 제거"""
        if callback in self.command_callbacks:
            self.command_callbacks.remove(callback)
    
    def get_device_info(self, device_id: str) -> Optional[DeviceInfo]:
        """장비 정보 조회"""
        return self.devices.get(device_id)
    
    def get_all_devices(self) -> List[DeviceInfo]:
        """모든 장비 정보 조회"""
        return list(self.devices.values())
    
    def get_command_history(self, device_id: str = None, limit: int = 100) -> List[RemoteCommand]:
        """명령 히스토리 조회"""
        history = self.command_history
        
        if device_id:
            history = [cmd for cmd in history if cmd.device_id == device_id]
        
        return history[-limit:]
    
    def get_command_status(self, command_id: str) -> Optional[Dict[str, Any]]:
        """명령 상태 조회"""
        return self.command_results.get(command_id)
    
    def cancel_command(self, command_id: str) -> bool:
        """명령 취소"""
        # 큐에서 명령 찾기
        for command in list(self.command_queue):
            if command.id == command_id:
                command.status = CommandStatus.CANCELLED
                self.command_queue.remove(command)
                logger.info(f"명령 취소됨: {command_id}")
                return True
        
        return False
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'is_processing': self.is_processing,
            'queue_size': len(self.command_queue),
            'total_devices': len(self.devices),
            'online_devices': len([d for d in self.devices.values() if d.status == DeviceStatus.ONLINE]),
            'offline_devices': len([d for d in self.devices.values() if d.status == DeviceStatus.OFFLINE]),
            'total_commands': len(self.command_history),
            'completed_commands': len([c for c in self.command_history if c.status == CommandStatus.COMPLETED]),
            'failed_commands': len([c for c in self.command_history if c.status == CommandStatus.FAILED])
        }
    
    def stop_service(self):
        """서비스 중지"""
        self.is_processing = False
        
        # 장비 상태 모니터링 중지
        for timer in self.device_health_checkers.values():
            timer.cancel()
        
        logger.info("원격 제어 서비스 중지")

# 전역 인스턴스
remote_control_service = RemoteControlService()
