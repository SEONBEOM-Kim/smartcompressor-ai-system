#!/usr/bin/env python3
"""
실시간 스트리밍 서비스
Tesla 스타일의 WebSocket 기반 실시간 데이터 스트리밍
"""

import asyncio
import json
import time
import logging
import threading
from typing import Dict, List, Set, Optional, Callable
from datetime import datetime, timedelta
import websockets
import websockets.exceptions
from collections import defaultdict, deque
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealtimeStreamingService:
    """실시간 스트리밍 서비스 (Tesla 스타일)"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 8080):
        self.host = host
        self.port = port
        self.websocket_server = None
        self.connected_clients = {}  # client_id -> websocket
        self.device_subscriptions = defaultdict(set)  # device_id -> set of client_ids
        self.client_subscriptions = defaultdict(set)  # client_id -> set of device_ids
        self.data_buffers = defaultdict(lambda: deque(maxlen=1000))  # device_id -> data buffer
        self.is_running = False
        
        # 스트리밍 설정
        self.streaming_intervals = {
            'sensor_data': 1.0,  # 1초마다
            'anomaly': 0.1,      # 0.1초마다 (즉시)
            'heartbeat': 30.0,   # 30초마다
            'status': 5.0        # 5초마다
        }
        
        # 스트리밍 태스크
        self.streaming_tasks = {}
        
        logger.info("실시간 스트리밍 서비스 초기화 완료")
    
    async def start(self):
        """WebSocket 서버 시작"""
        try:
            self.websocket_server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=10,
                close_timeout=10
            )
            
            self.is_running = True
            logger.info(f"WebSocket 서버 시작: {self.host}:{self.port}")
            
            # 스트리밍 태스크 시작
            await self._start_streaming_tasks()
            
            # 서버 실행
            await self.websocket_server.wait_closed()
            
        except Exception as e:
            logger.error(f"WebSocket 서버 시작 실패: {e}")
            raise
    
    async def _handle_client(self, websocket, path):
        """클라이언트 연결 처리"""
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}:{int(time.time())}"
        logger.info(f"클라이언트 연결: {client_id}")
        
        try:
            # 클라이언트 등록
            self.connected_clients[client_id] = websocket
            
            # 연결 확인 메시지 전송
            await self._send_message(websocket, {
                'type': 'connection_established',
                'client_id': client_id,
                'timestamp': time.time(),
                'server_info': {
                    'version': '1.0.0',
                    'capabilities': ['sensor_data', 'anomaly', 'heartbeat', 'status']
                }
            })
            
            # 메시지 수신 루프
            async for message in websocket:
                await self._handle_message(client_id, websocket, message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"클라이언트 연결 끊김: {client_id}")
        except Exception as e:
            logger.error(f"클라이언트 처리 오류: {e}")
        finally:
            # 클라이언트 정리
            await self._cleanup_client(client_id)
    
    async def _handle_message(self, client_id: str, websocket, message: str):
        """클라이언트 메시지 처리"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                await self._handle_subscribe(client_id, data)
            elif message_type == 'unsubscribe':
                await self._handle_unsubscribe(client_id, data)
            elif message_type == 'get_data':
                await self._handle_get_data(client_id, data)
            elif message_type == 'ping':
                await self._handle_ping(client_id, data)
            else:
                logger.warning(f"알 수 없는 메시지 타입: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 오류: {e}")
            await self._send_error(websocket, "Invalid JSON format")
        except Exception as e:
            logger.error(f"메시지 처리 오류: {e}")
            await self._send_error(websocket, str(e))
    
    async def _handle_subscribe(self, client_id: str, data: Dict):
        """구독 요청 처리"""
        try:
            device_ids = data.get('device_ids', [])
            stream_types = data.get('stream_types', ['sensor_data'])
            
            if not device_ids:
                await self._send_error(self.connected_clients[client_id], "No device IDs specified")
                return
            
            # 구독 등록
            for device_id in device_ids:
                self.device_subscriptions[device_id].add(client_id)
                self.client_subscriptions[client_id].add(device_id)
            
            # 구독 확인 응답
            await self._send_message(self.connected_clients[client_id], {
                'type': 'subscription_confirmed',
                'client_id': client_id,
                'device_ids': device_ids,
                'stream_types': stream_types,
                'timestamp': time.time()
            })
            
            logger.info(f"클라이언트 {client_id} 구독: {device_ids}")
            
        except Exception as e:
            logger.error(f"구독 처리 오류: {e}")
            await self._send_error(self.connected_clients[client_id], str(e))
    
    async def _handle_unsubscribe(self, client_id: str, data: Dict):
        """구독 해제 요청 처리"""
        try:
            device_ids = data.get('device_ids', [])
            
            if not device_ids:
                # 모든 구독 해제
                device_ids = list(self.client_subscriptions[client_id])
            
            # 구독 해제
            for device_id in device_ids:
                self.device_subscriptions[device_id].discard(client_id)
                self.client_subscriptions[client_id].discard(device_id)
            
            # 구독 해제 확인 응답
            await self._send_message(self.connected_clients[client_id], {
                'type': 'unsubscription_confirmed',
                'client_id': client_id,
                'device_ids': device_ids,
                'timestamp': time.time()
            })
            
            logger.info(f"클라이언트 {client_id} 구독 해제: {device_ids}")
            
        except Exception as e:
            logger.error(f"구독 해제 처리 오류: {e}")
            await self._send_error(self.connected_clients[client_id], str(e))
    
    async def _handle_get_data(self, client_id: str, data: Dict):
        """데이터 요청 처리"""
        try:
            device_id = data.get('device_id')
            data_type = data.get('data_type', 'sensor_data')
            limit = data.get('limit', 100)
            
            if not device_id:
                await self._send_error(self.connected_clients[client_id], "Device ID required")
                return
            
            # 데이터 조회
            if device_id in self.data_buffers:
                buffer_data = list(self.data_buffers[device_id])[-limit:]
                
                await self._send_message(self.connected_clients[client_id], {
                    'type': 'data_response',
                    'device_id': device_id,
                    'data_type': data_type,
                    'data': buffer_data,
                    'count': len(buffer_data),
                    'timestamp': time.time()
                })
            else:
                await self._send_error(self.connected_clients[client_id], f"Device {device_id} not found")
            
        except Exception as e:
            logger.error(f"데이터 요청 처리 오류: {e}")
            await self._send_error(self.connected_clients[client_id], str(e))
    
    async def _handle_ping(self, client_id: str, data: Dict):
        """핑 요청 처리"""
        try:
            await self._send_message(self.connected_clients[client_id], {
                'type': 'pong',
                'client_id': client_id,
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"핑 처리 오류: {e}")
    
    async def _start_streaming_tasks(self):
        """스트리밍 태스크 시작"""
        try:
            # 센서 데이터 스트리밍
            self.streaming_tasks['sensor_data'] = asyncio.create_task(
                self._stream_sensor_data()
            )
            
            # 하트비트 스트리밍
            self.streaming_tasks['heartbeat'] = asyncio.create_task(
                self._stream_heartbeat()
            )
            
            # 상태 스트리밍
            self.streaming_tasks['status'] = asyncio.create_task(
                self._stream_status()
            )
            
            logger.info("스트리밍 태스크 시작 완료")
            
        except Exception as e:
            logger.error(f"스트리밍 태스크 시작 실패: {e}")
    
    async def _stream_sensor_data(self):
        """센서 데이터 스트리밍"""
        while self.is_running:
            try:
                # 센서 데이터 서비스에서 최신 데이터 가져오기
                from services.sensor_data_service import sensor_data_service
                
                # 연결된 디바이스들의 최신 데이터 전송
                for device_id, subscribers in self.device_subscriptions.items():
                    if not subscribers:
                        continue
                    
                    # 최신 센서 데이터 조회
                    latest_data = sensor_data_service.get_sensor_data(device_id, hours=1)
                    
                    if latest_data:
                        # 구독자들에게 전송
                        await self._broadcast_to_subscribers(device_id, {
                            'type': 'sensor_data',
                            'device_id': device_id,
                            'data': latest_data[0],  # 최신 데이터
                            'timestamp': time.time()
                        })
                
                await asyncio.sleep(self.streaming_intervals['sensor_data'])
                
            except Exception as e:
                logger.error(f"센서 데이터 스트리밍 오류: {e}")
                await asyncio.sleep(1)
    
    async def _stream_heartbeat(self):
        """하트비트 스트리밍"""
        while self.is_running:
            try:
                # 모든 연결된 클라이언트에게 하트비트 전송
                for client_id, websocket in self.connected_clients.items():
                    try:
                        await self._send_message(websocket, {
                            'type': 'heartbeat',
                            'client_id': client_id,
                            'timestamp': time.time(),
                            'server_status': 'running'
                        })
                    except Exception as e:
                        logger.warning(f"하트비트 전송 실패 {client_id}: {e}")
                
                await asyncio.sleep(self.streaming_intervals['heartbeat'])
                
            except Exception as e:
                logger.error(f"하트비트 스트리밍 오류: {e}")
                await asyncio.sleep(1)
    
    async def _stream_status(self):
        """상태 스트리밍"""
        while self.is_running:
            try:
                # 서버 상태 정보
                status_info = {
                    'type': 'status_update',
                    'timestamp': time.time(),
                    'server_status': 'running',
                    'connected_clients': len(self.connected_clients),
                    'active_devices': len(self.device_subscriptions),
                    'total_subscriptions': sum(len(subs) for subs in self.device_subscriptions.values())
                }
                
                # 모든 연결된 클라이언트에게 상태 전송
                for client_id, websocket in self.connected_clients.items():
                    try:
                        await self._send_message(websocket, status_info)
                    except Exception as e:
                        logger.warning(f"상태 전송 실패 {client_id}: {e}")
                
                await asyncio.sleep(self.streaming_intervals['status'])
                
            except Exception as e:
                logger.error(f"상태 스트리밍 오류: {e}")
                await asyncio.sleep(1)
    
    async def _broadcast_to_subscribers(self, device_id: str, message: Dict):
        """구독자들에게 메시지 브로드캐스트"""
        try:
            if device_id not in self.device_subscriptions:
                return
            
            subscribers = self.device_subscriptions[device_id]
            if not subscribers:
                return
            
            # 구독자들에게 전송
            for client_id in subscribers:
                if client_id in self.connected_clients:
                    try:
                        websocket = self.connected_clients[client_id]
                        await self._send_message(websocket, message)
                    except Exception as e:
                        logger.warning(f"브로드캐스트 실패 {client_id}: {e}")
                        # 연결이 끊어진 클라이언트 정리
                        await self._cleanup_client(client_id)
            
        except Exception as e:
            logger.error(f"브로드캐스트 오류: {e}")
    
    async def broadcast_anomaly(self, anomaly_data: Dict):
        """이상 감지 결과 브로드캐스트"""
        try:
            device_id = anomaly_data.get('device_id')
            if not device_id:
                return
            
            message = {
                'type': 'anomaly_detected',
                'device_id': device_id,
                'anomaly_data': anomaly_data,
                'timestamp': time.time()
            }
            
            await self._broadcast_to_subscribers(device_id, message)
            
        except Exception as e:
            logger.error(f"이상 감지 브로드캐스트 오류: {e}")
    
    async def add_sensor_data(self, device_id: str, data: Dict):
        """센서 데이터 추가"""
        try:
            # 데이터 버퍼에 추가
            self.data_buffers[device_id].append({
                'timestamp': time.time(),
                'data': data
            })
            
            # 실시간 스트리밍
            await self._broadcast_to_subscribers(device_id, {
                'type': 'sensor_data',
                'device_id': device_id,
                'data': data,
                'timestamp': time.time()
            })
            
        except Exception as e:
            logger.error(f"센서 데이터 추가 오류: {e}")
    
    async def _send_message(self, websocket, message: Dict):
        """메시지 전송"""
        try:
            await websocket.send(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"메시지 전송 오류: {e}")
            raise
    
    async def _send_error(self, websocket, error_message: str):
        """오류 메시지 전송"""
        try:
            await self._send_message(websocket, {
                'type': 'error',
                'message': error_message,
                'timestamp': time.time()
            })
        except Exception as e:
            logger.error(f"오류 메시지 전송 실패: {e}")
    
    async def _cleanup_client(self, client_id: str):
        """클라이언트 정리"""
        try:
            # 연결된 클라이언트에서 제거
            if client_id in self.connected_clients:
                del self.connected_clients[client_id]
            
            # 구독 정보 정리
            if client_id in self.client_subscriptions:
                subscribed_devices = list(self.client_subscriptions[client_id])
                for device_id in subscribed_devices:
                    self.device_subscriptions[device_id].discard(client_id)
                del self.client_subscriptions[client_id]
            
            logger.info(f"클라이언트 정리 완료: {client_id}")
            
        except Exception as e:
            logger.error(f"클라이언트 정리 오류: {e}")
    
    def get_status(self) -> Dict:
        """서비스 상태 조회"""
        return {
            'is_running': self.is_running,
            'connected_clients': len(self.connected_clients),
            'active_devices': len(self.device_subscriptions),
            'total_subscriptions': sum(len(subs) for subs in self.device_subscriptions.values()),
            'streaming_intervals': self.streaming_intervals,
            'host': self.host,
            'port': self.port
        }
    
    async def stop(self):
        """서비스 중지"""
        try:
            self.is_running = False
            
            # 스트리밍 태스크 중지
            for task in self.streaming_tasks.values():
                task.cancel()
            
            # WebSocket 서버 중지
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
            
            logger.info("실시간 스트리밍 서비스 중지 완료")
            
        except Exception as e:
            logger.error(f"서비스 중지 오류: {e}")

# 전역 서비스 인스턴스
realtime_streaming_service = RealtimeStreamingService()

# 서비스 시작 함수
async def start_streaming_service():
    """스트리밍 서비스 시작"""
    await realtime_streaming_service.start()

# 스레드에서 실행하는 함수
def run_streaming_service():
    """스레드에서 스트리밍 서비스 실행"""
    asyncio.run(start_streaming_service())
