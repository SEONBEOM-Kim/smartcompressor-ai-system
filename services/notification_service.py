#!/usr/bin/env python3
"""
통합 알림 서비스
다양한 알림 채널을 지원하는 실시간 알림 시스템
Slack과 Discord 스타일의 커뮤니케이션 시스템
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import threading
import queue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
import asyncio
import aiohttp

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationPriority(Enum):
    """알림 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationType(Enum):
    """알림 타입"""
    SYSTEM = "system"
    PAYMENT = "payment"
    DIAGNOSIS = "diagnosis"
    EQUIPMENT = "equipment"
    ORDER = "order"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"

class NotificationChannel(ABC):
    """알림 채널 추상 클래스"""
    
    @abstractmethod
    def send_notification(self, message: Dict) -> bool:
        """알림 전송"""
        pass
    
    @abstractmethod
    def get_channel_name(self) -> str:
        """채널 이름 반환"""
        pass

class WebSocketNotificationChannel(NotificationChannel):
    """WebSocket 알림 채널"""
    
    def __init__(self):
        self.connected_clients = set()
        self.message_queue = queue.Queue()
        
    def add_client(self, client):
        """클라이언트 추가"""
        self.connected_clients.add(client)
        logger.info(f"WebSocket 클라이언트 추가: {len(self.connected_clients)}개 연결")
    
    def remove_client(self, client):
        """클라이언트 제거"""
        self.connected_clients.discard(client)
        logger.info(f"WebSocket 클라이언트 제거: {len(self.connected_clients)}개 연결")
    
    def send_notification(self, message: Dict) -> bool:
        """WebSocket으로 알림 전송"""
        try:
            message_json = json.dumps(message, ensure_ascii=False)
            disconnected_clients = set()
            
            for client in self.connected_clients:
                try:
                    client.send(message_json)
                except Exception as e:
                    logger.warning(f"WebSocket 전송 실패: {e}")
                    disconnected_clients.add(client)
            
            # 연결이 끊어진 클라이언트 제거
            for client in disconnected_clients:
                self.remove_client(client)
            
            logger.info(f"WebSocket 알림 전송 완료: {len(self.connected_clients)}개 클라이언트")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket 알림 전송 실패: {e}")
            return False
    
    def get_channel_name(self) -> str:
        return "websocket"

class EmailNotificationChannel(NotificationChannel):
    """이메일 알림 채널"""
    
    def __init__(self, smtp_server: str, smtp_port: int, 
                 username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_notification(self, message: Dict) -> bool:
        """이메일로 알림 전송"""
        try:
            recipient = message.get('recipient')
            if not recipient:
                logger.error("이메일 수신자가 지정되지 않았습니다")
                return False
            
            # 이메일 내용 생성
            subject = message.get('subject', 'Signalcraft 알림')
            body = self._create_email_body(message)
            
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            logger.info(f"이메일 알림 전송 완료: {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 알림 전송 실패: {e}")
            return False
    
    def _create_email_body(self, message: Dict) -> str:
        """이메일 본문 생성"""
        notification_type = message.get('type', 'general')
        data = message.get('data', {})
        
        if notification_type == 'payment_completed':
            return f"""
            <html>
            <body>
                <h2>🎉 결제가 완료되었습니다!</h2>
                <p>안녕하세요, Signalcraft 고객님!</p>
                <p>결제가 성공적으로 완료되었습니다.</p>
                <ul>
                    <li><strong>결제 금액:</strong> {data.get('amount', 0):,}원</li>
                    <li><strong>플랜:</strong> {data.get('plan_name', 'Unknown')}</li>
                    <li><strong>결제 시간:</strong> {data.get('timestamp', 'Unknown')}</li>
                </ul>
                <p>이제 Signalcraft AI 진단 서비스를 이용하실 수 있습니다.</p>
                <p>문의사항이 있으시면 언제든 연락주세요.</p>
                <br>
                <p>감사합니다.<br>Signalcraft 팀</p>
            </body>
            </html>
            """
        elif notification_type == 'diagnosis_alert':
            return f"""
            <html>
            <body>
                <h2>⚠️ 냉동고 이상 감지!</h2>
                <p>안녕하세요, Signalcraft 고객님!</p>
                <p>AI 진단 결과 이상이 감지되었습니다.</p>
                <ul>
                    <li><strong>진단 결과:</strong> {data.get('result', 'Unknown')}</li>
                    <li><strong>신뢰도:</strong> {data.get('confidence', 0):.1%}</li>
                    <li><strong>진단 시간:</strong> {data.get('timestamp', 'Unknown')}</li>
                </ul>
                <p>빠른 조치를 위해 기술 지원팀에 연락드리겠습니다.</p>
                <p>긴급 문의: 010-8533-6898</p>
                <br>
                <p>감사합니다.<br>Signalcraft 팀</p>
            </body>
            </html>
            """
        else:
            return f"""
            <html>
            <body>
                <h2>Signalcraft 알림</h2>
                <p>{message.get('content', '알림이 있습니다.')}</p>
                <br>
                <p>감사합니다.<br>Signalcraft 팀</p>
            </body>
            </html>
            """
    
    def get_channel_name(self) -> str:
        return "email"

class KakaoNotificationChannel(NotificationChannel):
    """카카오톡 알림 채널"""
    
    def __init__(self, admin_key: str):
        self.admin_key = admin_key
        self.base_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        self.headers = {
            "Authorization": f"KakaoAK {admin_key}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
    def send_notification(self, message: Dict) -> bool:
        """카카오톡으로 알림 전송"""
        try:
            recipient_id = message.get('recipient_id')
            if not recipient_id:
                logger.error("카카오톡 수신자 ID가 지정되지 않았습니다")
                return False
            
            # 카카오톡 메시지 생성
            template_object = self._create_kakao_template(message)
            
            data = {
                "template_object": json.dumps(template_object, ensure_ascii=False)
            }
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=data
            )
            
            if response.status_code == 200:
                logger.info(f"카카오톡 알림 전송 완료: {recipient_id}")
                return True
            else:
                logger.error(f"카카오톡 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"카카오톡 알림 전송 실패: {e}")
            return False
    
    def _create_kakao_template(self, message: Dict) -> Dict:
        """카카오톡 템플릿 생성"""
        notification_type = message.get('type', 'general')
        data = message.get('data', {})
        
        if notification_type == 'payment_completed':
            return {
                "object_type": "text",
                "text": f"🎉 결제 완료!\n\nSignalcraft 구독이 활성화되었습니다.\n\n결제 금액: {data.get('amount', 0):,}원\n플랜: {data.get('plan_name', 'Unknown')}\n\n이제 AI 진단 서비스를 이용하실 수 있습니다!",
                "link": {
                    "web_url": "https://signalcraft.kr",
                    "mobile_web_url": "https://signalcraft.kr"
                },
                "button_title": "서비스 이용하기"
            }
        elif notification_type == 'diagnosis_alert':
            return {
                "object_type": "text",
                "text": f"⚠️ 냉동고 이상 감지!\n\nAI 진단 결과 이상이 감지되었습니다.\n\n진단 결과: {data.get('result', 'Unknown')}\n신뢰도: {data.get('confidence', 0):.1%}\n\n빠른 조치가 필요합니다!\n긴급 문의: 010-8533-6898",
                "link": {
                    "web_url": "https://signalcraft.kr",
                    "mobile_web_url": "https://signalcraft.kr"
                },
                "button_title": "상세 보기"
            }
        else:
            return {
                "object_type": "text",
                "text": f"Signalcraft 알림\n\n{message.get('content', '알림이 있습니다.')}",
                "link": {
                    "web_url": "https://signalcraft.kr",
                    "mobile_web_url": "https://signalcraft.kr"
                },
                "button_title": "확인하기"
            }
    
    def get_channel_name(self) -> str:
        return "kakao"

class SlackNotificationChannel(NotificationChannel):
    """Slack 알림 채널"""
    
    def __init__(self, webhook_url: str, channel: str = "#general"):
        self.webhook_url = webhook_url
        self.channel = channel
    
    def send_notification(self, message: Dict) -> bool:
        """Slack으로 알림 전송"""
        try:
            # Slack 메시지 포맷팅
            slack_message = self._format_slack_message(message)
            
            response = requests.post(
                self.webhook_url,
                json=slack_message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"Slack 알림 전송 완료: {self.channel}")
                return True
            else:
                logger.error(f"Slack 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Slack 알림 전송 실패: {e}")
            return False
    
    def _format_slack_message(self, message: Dict) -> Dict:
        """Slack 메시지 포맷팅"""
        notification_type = message.get('type', 'general')
        data = message.get('data', {})
        priority = message.get('priority', 'normal')
        
        # 우선순위에 따른 색상 설정
        color_map = {
            'low': '#36a64f',      # 녹색
            'normal': '#36a64f',   # 녹색
            'high': '#ff9500',     # 주황색
            'urgent': '#ff0000'    # 빨간색
        }
        
        # 기본 메시지 구조
        slack_message = {
            "channel": self.channel,
            "attachments": [{
                "color": color_map.get(priority, '#36a64f'),
                "title": f"SmartCompressor AI 알림",
                "text": message.get('content', '알림이 있습니다.'),
                "timestamp": int(datetime.now().timestamp()),
                "footer": "SmartCompressor AI",
                "footer_icon": "https://smartcompressor.ai/icon.png"
            }]
        }
        
        # 알림 타입별 특화 메시지
        if notification_type == 'payment_completed':
            slack_message["attachments"][0].update({
                "title": "🎉 결제 완료",
                "text": f"결제가 성공적으로 완료되었습니다.\n금액: {data.get('amount', 0):,}원\n플랜: {data.get('plan_name', 'Unknown')}",
                "fields": [
                    {"title": "결제 금액", "value": f"{data.get('amount', 0):,}원", "short": True},
                    {"title": "플랜", "value": data.get('plan_name', 'Unknown'), "short": True}
                ]
            })
        elif notification_type == 'diagnosis_alert':
            slack_message["attachments"][0].update({
                "title": "⚠️ 냉동고 이상 감지",
                "text": f"AI 진단 결과 이상이 감지되었습니다.\n진단 결과: {data.get('result', 'Unknown')}\n신뢰도: {data.get('confidence', 0):.1%}",
                "fields": [
                    {"title": "진단 결과", "value": data.get('result', 'Unknown'), "short": True},
                    {"title": "신뢰도", "value": f"{data.get('confidence', 0):.1%}", "short": True}
                ]
            })
        elif notification_type == 'equipment_alert':
            slack_message["attachments"][0].update({
                "title": "🔧 장비 상태 알림",
                "text": f"장비 상태가 변경되었습니다.\n장비: {data.get('equipment_name', 'Unknown')}\n상태: {data.get('status', 'Unknown')}",
                "fields": [
                    {"title": "장비명", "value": data.get('equipment_name', 'Unknown'), "short": True},
                    {"title": "상태", "value": data.get('status', 'Unknown'), "short": True}
                ]
            })
        
        return slack_message
    
    def get_channel_name(self) -> str:
        return "slack"

class DiscordNotificationChannel(NotificationChannel):
    """Discord 알림 채널"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_notification(self, message: Dict) -> bool:
        """Discord로 알림 전송"""
        try:
            # Discord 메시지 포맷팅
            discord_message = self._format_discord_message(message)
            
            response = requests.post(
                self.webhook_url,
                json=discord_message,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 204:
                logger.info("Discord 알림 전송 완료")
                return True
            else:
                logger.error(f"Discord 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Discord 알림 전송 실패: {e}")
            return False
    
    def _format_discord_message(self, message: Dict) -> Dict:
        """Discord 메시지 포맷팅"""
        notification_type = message.get('type', 'general')
        data = message.get('data', {})
        priority = message.get('priority', 'normal')
        
        # 우선순위에 따른 이모지 설정
        emoji_map = {
            'low': '📢',
            'normal': '📢',
            'high': '⚠️',
            'urgent': '🚨'
        }
        
        # 기본 메시지 구조
        discord_message = {
            "content": f"{emoji_map.get(priority, '📢')} SmartCompressor AI 알림",
            "embeds": [{
                "title": "SmartCompressor AI 알림",
                "description": message.get('content', '알림이 있습니다.'),
                "color": 0x36a64f,  # 녹색
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "SmartCompressor AI"
                }
            }]
        }
        
        # 알림 타입별 특화 메시지
        if notification_type == 'payment_completed':
            discord_message["embeds"][0].update({
                "title": "🎉 결제 완료",
                "description": f"결제가 성공적으로 완료되었습니다.",
                "color": 0x36a64f,
                "fields": [
                    {"name": "결제 금액", "value": f"{data.get('amount', 0):,}원", "inline": True},
                    {"name": "플랜", "value": data.get('plan_name', 'Unknown'), "inline": True}
                ]
            })
        elif notification_type == 'diagnosis_alert':
            discord_message["embeds"][0].update({
                "title": "⚠️ 냉동고 이상 감지",
                "description": f"AI 진단 결과 이상이 감지되었습니다.",
                "color": 0xff9500,
                "fields": [
                    {"name": "진단 결과", "value": data.get('result', 'Unknown'), "inline": True},
                    {"name": "신뢰도", "value": f"{data.get('confidence', 0):.1%}", "inline": True}
                ]
            })
        elif notification_type == 'equipment_alert':
            discord_message["embeds"][0].update({
                "title": "🔧 장비 상태 알림",
                "description": f"장비 상태가 변경되었습니다.",
                "color": 0xff0000,
                "fields": [
                    {"name": "장비명", "value": data.get('equipment_name', 'Unknown'), "inline": True},
                    {"name": "상태", "value": data.get('status', 'Unknown'), "inline": True}
                ]
            })
        
        return discord_message
    
    def get_channel_name(self) -> str:
        return "discord"

class WhatsAppBusinessChannel(NotificationChannel):
    """WhatsApp Business 알림 채널"""
    
    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.base_url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    
    def send_notification(self, message: Dict) -> bool:
        """WhatsApp Business로 알림 전송"""
        try:
            recipient = message.get('recipient')
            if not recipient:
                logger.error("WhatsApp 수신자가 지정되지 않았습니다")
                return False
            
            # WhatsApp 메시지 포맷팅
            whatsapp_message = self._format_whatsapp_message(message)
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                self.base_url,
                json=whatsapp_message,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp 알림 전송 완료: {recipient}")
                return True
            else:
                logger.error(f"WhatsApp 알림 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp 알림 전송 실패: {e}")
            return False
    
    def _format_whatsapp_message(self, message: Dict) -> Dict:
        """WhatsApp 메시지 포맷팅"""
        notification_type = message.get('type', 'general')
        data = message.get('data', {})
        
        # 기본 메시지 템플릿
        template_name = "general_notification"
        
        # 알림 타입별 템플릿 선택
        if notification_type == 'payment_completed':
            template_name = "payment_completed"
        elif notification_type == 'diagnosis_alert':
            template_name = "diagnosis_alert"
        elif notification_type == 'equipment_alert':
            template_name = "equipment_alert"
        
        # 템플릿 변수 설정
        template_variables = {
            "1": message.get('content', '알림이 있습니다.'),
            "2": data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        }
        
        # 알림 타입별 특화 변수
        if notification_type == 'payment_completed':
            template_variables.update({
                "3": f"{data.get('amount', 0):,}원",
                "4": data.get('plan_name', 'Unknown')
            })
        elif notification_type == 'diagnosis_alert':
            template_variables.update({
                "3": data.get('result', 'Unknown'),
                "4": f"{data.get('confidence', 0):.1%}"
            })
        elif notification_type == 'equipment_alert':
            template_variables.update({
                "3": data.get('equipment_name', 'Unknown'),
                "4": data.get('status', 'Unknown')
            })
        
        return {
            "messaging_product": "whatsapp",
            "to": message.get('recipient'),
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": "ko"
                },
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": template_variables.get(str(i+1), "")}
                            for i in range(len(template_variables))
                        ]
                    }
                ]
            }
        }
    
    def get_channel_name(self) -> str:
        return "whatsapp"

class UnifiedNotificationService:
    """통합 알림 서비스"""
    
    def __init__(self):
        self.channels = {}
        self.notification_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        
        # 알림 채널 초기화
        self._initialize_channels()
        
        # 워커 스레드 시작
        self.start_worker()
        
        logger.info("통합 알림 서비스 초기화 완료")
    
    def _initialize_channels(self):
        """알림 채널 초기화"""
        try:
            # WebSocket 채널
            self.channels['websocket'] = WebSocketNotificationChannel()
            
            # 이메일 채널
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            if smtp_username and smtp_password:
                self.channels['email'] = EmailNotificationChannel(
                    smtp_server, smtp_port, smtp_username, smtp_password
                )
                logger.info("이메일 알림 채널 초기화 완료")
            
            # 카카오톡 채널
            kakao_admin_key = os.getenv('KAKAO_ADMIN_KEY')
            if kakao_admin_key:
                self.channels['kakao'] = KakaoNotificationChannel(kakao_admin_key)
                logger.info("카카오톡 알림 채널 초기화 완료")
            
            # Slack 채널
            slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
            slack_channel = os.getenv('SLACK_CHANNEL', '#general')
            if slack_webhook_url:
                self.channels['slack'] = SlackNotificationChannel(slack_webhook_url, slack_channel)
                logger.info("Slack 알림 채널 초기화 완료")
            
            # Discord 채널
            discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
            if discord_webhook_url:
                self.channels['discord'] = DiscordNotificationChannel(discord_webhook_url)
                logger.info("Discord 알림 채널 초기화 완료")
            
            # WhatsApp Business 채널
            whatsapp_access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
            whatsapp_phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
            if whatsapp_access_token and whatsapp_phone_number_id:
                self.channels['whatsapp'] = WhatsAppBusinessChannel(whatsapp_access_token, whatsapp_phone_number_id)
                logger.info("WhatsApp Business 알림 채널 초기화 완료")
            
        except Exception as e:
            logger.error(f"알림 채널 초기화 실패: {e}")
    
    def start_worker(self):
        """알림 워커 스레드 시작"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("알림 워커 스레드 시작")
    
    def stop_worker(self):
        """알림 워커 스레드 중지"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join()
        logger.info("알림 워커 스레드 중지")
    
    def _worker_loop(self):
        """알림 워커 루프"""
        while self.is_running:
            try:
                # 큐에서 알림 가져오기 (1초 타임아웃)
                message = self.notification_queue.get(timeout=1)
                self._process_notification(message)
                self.notification_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"알림 처리 중 오류: {e}")
    
    def _process_notification(self, message: Dict):
        """알림 처리"""
        try:
            channels = message.get('channels', ['websocket'])
            notification_type = message.get('type', 'general')
            
            logger.info(f"알림 처리 시작: {notification_type}, 채널: {channels}")
            
            # 각 채널로 알림 전송
            for channel_name in channels:
                if channel_name in self.channels:
                    channel = self.channels[channel_name]
                    success = channel.send_notification(message)
                    
                    if success:
                        logger.info(f"알림 전송 성공: {channel_name}")
                    else:
                        logger.warning(f"알림 전송 실패: {channel_name}")
                else:
                    logger.warning(f"지원하지 않는 알림 채널: {channel_name}")
            
        except Exception as e:
            logger.error(f"알림 처리 실패: {e}")
    
    def send_notification(self, notification_type: str, data: Dict, 
                         channels: List[str] = None, 
                         recipient: str = None,
                         priority: str = 'normal') -> bool:
        """알림 전송"""
        try:
            if channels is None:
                channels = ['websocket']  # 기본 채널
            
            message = {
                'type': notification_type,
                'data': data,
                'channels': channels,
                'recipient': recipient,
                'priority': priority,
                'timestamp': datetime.now().isoformat()
            }
            
            # 우선순위에 따라 큐에 추가
            if priority == 'high':
                # 높은 우선순위는 즉시 처리
                self._process_notification(message)
            else:
                # 일반 우선순위는 큐에 추가
                self.notification_queue.put(message)
            
            logger.info(f"알림 큐에 추가: {notification_type}")
            return True
            
        except Exception as e:
            logger.error(f"알림 전송 실패: {e}")
            return False
    
    def send_payment_notification(self, payment_data: Dict, 
                                 user_email: str = None,
                                 user_kakao_id: str = None) -> bool:
        """결제 완료 알림 전송"""
        try:
            channels = ['websocket']
            
            if user_email:
                channels.append('email')
            
            if user_kakao_id:
                channels.append('kakao')
            
            return self.send_notification(
                notification_type='payment_completed',
                data=payment_data,
                channels=channels,
                recipient=user_email or user_kakao_id,
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"결제 알림 전송 실패: {e}")
            return False
    
    def send_diagnosis_alert(self, diagnosis_data: Dict,
                           user_email: str = None,
                           user_kakao_id: str = None) -> bool:
        """진단 경고 알림 전송"""
        try:
            channels = ['websocket']
            
            if user_email:
                channels.append('email')
            
            if user_kakao_id:
                channels.append('kakao')
            
            return self.send_notification(
                notification_type='diagnosis_alert',
                data=diagnosis_data,
                channels=channels,
                recipient=user_email or user_kakao_id,
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"진단 경고 알림 전송 실패: {e}")
            return False
    
    def add_websocket_client(self, client):
        """WebSocket 클라이언트 추가"""
        if 'websocket' in self.channels:
            self.channels['websocket'].add_client(client)
    
    def remove_websocket_client(self, client):
        """WebSocket 클라이언트 제거"""
        if 'websocket' in self.channels:
            self.channels['websocket'].remove_client(client)
    
    def send_emergency_alert(self, alert_data: Dict, channels: List[str] = None) -> bool:
        """긴급 알림 전송"""
        try:
            if channels is None:
                channels = ['websocket', 'slack', 'discord', 'whatsapp']
            
            return self.send_notification(
                notification_type='emergency',
                data=alert_data,
                channels=channels,
                priority='urgent'
            )
            
        except Exception as e:
            logger.error(f"긴급 알림 전송 실패: {e}")
            return False
    
    def send_equipment_alert(self, equipment_data: Dict, 
                           user_email: str = None,
                           user_kakao_id: str = None) -> bool:
        """장비 상태 알림 전송"""
        try:
            channels = ['websocket']
            
            if user_email:
                channels.append('email')
            
            if user_kakao_id:
                channels.append('kakao')
            
            # Slack과 Discord에도 전송
            if 'slack' in self.channels:
                channels.append('slack')
            
            if 'discord' in self.channels:
                channels.append('discord')
            
            return self.send_notification(
                notification_type='equipment_alert',
                data=equipment_data,
                channels=channels,
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"장비 알림 전송 실패: {e}")
            return False
    
    def send_order_notification(self, order_data: Dict, 
                              user_email: str = None,
                              user_kakao_id: str = None) -> bool:
        """주문 알림 전송"""
        try:
            channels = ['websocket']
            
            if user_email:
                channels.append('email')
            
            if user_kakao_id:
                channels.append('kakao')
            
            return self.send_notification(
                notification_type='order',
                data=order_data,
                channels=channels,
                priority='normal'
            )
            
        except Exception as e:
            logger.error(f"주문 알림 전송 실패: {e}")
            return False
    
    def send_maintenance_notification(self, maintenance_data: Dict, 
                                    channels: List[str] = None) -> bool:
        """점검 알림 전송"""
        try:
            if channels is None:
                channels = ['websocket', 'email', 'slack', 'discord']
            
            return self.send_notification(
                notification_type='maintenance',
                data=maintenance_data,
                channels=channels,
                priority='normal'
            )
            
        except Exception as e:
            logger.error(f"점검 알림 전송 실패: {e}")
            return False
    
    def get_notification_history(self, limit: int = 100) -> List[Dict]:
        """알림 히스토리 조회"""
        try:
            # 실제 구현에서는 데이터베이스에서 조회
            # 여기서는 메모리에서 시뮬레이션
            history = [
                {
                    'id': f'notif_{i}',
                    'type': 'system',
                    'content': f'알림 메시지 {i}',
                    'channels': ['websocket', 'email'],
                    'priority': 'normal',
                    'sent_at': (datetime.now() - timedelta(hours=i)).isoformat(),
                    'status': 'sent'
                }
                for i in range(min(limit, 10))
            ]
            
            return history
            
        except Exception as e:
            logger.error(f"알림 히스토리 조회 오류: {e}")
            return []
    
    def get_channel_statistics(self) -> Dict:
        """채널별 통계 조회"""
        try:
            stats = {}
            
            for channel_name, channel in self.channels.items():
                stats[channel_name] = {
                    'name': channel.get_channel_name(),
                    'status': 'active',
                    'last_used': datetime.now().isoformat()
                }
            
            return {
                'total_channels': len(self.channels),
                'channels': stats,
                'queue_size': self.notification_queue.qsize(),
                'worker_status': 'running' if self.is_running else 'stopped'
            }
            
        except Exception as e:
            logger.error(f"채널 통계 조회 오류: {e}")
            return {}
    
    def test_channel(self, channel_name: str) -> Dict:
        """채널 테스트"""
        try:
            if channel_name not in self.channels:
                return {'success': False, 'error': '채널을 찾을 수 없습니다'}
            
            test_message = {
                'type': 'test',
                'content': '채널 테스트 메시지입니다.',
                'data': {'test': True},
                'priority': 'normal',
                'timestamp': datetime.now().isoformat()
            }
            
            channel = self.channels[channel_name]
            success = channel.send_notification(test_message)
            
            return {
                'success': success,
                'channel': channel_name,
                'message': '테스트 성공' if success else '테스트 실패'
            }
            
        except Exception as e:
            logger.error(f"채널 테스트 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_service_status(self) -> Dict:
        """서비스 상태 확인"""
        return {
            'status': 'running' if self.is_running else 'stopped',
            'channels': list(self.channels.keys()),
            'queue_size': self.notification_queue.qsize(),
            'worker_running': self.is_running,
            'supported_channels': ['websocket', 'email', 'kakao', 'slack', 'discord', 'whatsapp']
        }

# 전역 서비스 인스턴스
unified_notification_service = UnifiedNotificationService()