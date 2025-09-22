#!/usr/bin/env python3
"""
카카오톡 비즈니스 API 연동 서비스
Slack과 Discord 스타일의 실시간 커뮤니케이션
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """메시지 타입"""
    TEXT = "text"
    IMAGE = "image"
    BUTTON = "button"
    CAROUSEL = "carousel"
    QUICK_REPLY = "quick_reply"

class Priority(Enum):
    """알림 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class KakaoMessage:
    """카카오톡 메시지 데이터 클래스"""
    message_type: MessageType
    content: str
    image_url: Optional[str] = None
    buttons: List[Dict] = None
    quick_replies: List[Dict] = None
    priority: Priority = Priority.NORMAL
    scheduled_time: Optional[datetime] = None

@dataclass
class KakaoUser:
    """카카오톡 사용자 정보"""
    user_id: str
    kakao_id: str
    nickname: str
    phone: str
    email: str
    is_active: bool = True
    notification_settings: Dict = None

class KakaoBusinessService:
    """카카오톡 비즈니스 API 서비스"""
    
    def __init__(self, api_key: str, secret_key: str, base_url: str = "https://kapi.kakao.com"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.access_token = None
        self.token_expires_at = None
        
        # 메시지 템플릿 저장소
        self.message_templates = {}
        self.user_database = {}
        
        # 알림 설정
        self.notification_settings = {
            'max_retry': 3,
            'retry_delay': 5,  # seconds
            'rate_limit': 100,  # messages per minute
        }
        
        # 메시지 큐 (스케줄링용)
        self.message_queue = []
        
        logger.info("카카오톡 비즈니스 서비스 초기화 완료")
    
    def authenticate(self) -> bool:
        """카카오톡 API 인증"""
        try:
            url = f"{self.base_url}/v2/auth/token"
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.api_key,
                'client_secret': self.secret_key
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
                
                logger.info("카카오톡 API 인증 성공")
                return True
            else:
                logger.error(f"카카오톡 API 인증 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"카카오톡 API 인증 오류: {e}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """인증 상태 확인 및 갱신"""
        if not self.access_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            return self.authenticate()
        return True
    
    def send_message(self, user_id: str, message: KakaoMessage) -> Dict:
        """메시지 전송"""
        try:
            if not self._ensure_authenticated():
                return {'success': False, 'error': '인증 실패'}
            
            # 사용자 정보 확인
            user = self.user_database.get(user_id)
            if not user or not user.is_active:
                return {'success': False, 'error': '사용자를 찾을 수 없거나 비활성 상태'}
            
            # 메시지 포맷팅
            formatted_message = self._format_message(message)
            
            # API 호출
            url = f"{self.base_url}/v2/api/talk/message/default/send"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'receiver_uuids': json.dumps([user.kakao_id]),
                'template_object': json.dumps(formatted_message)
            }
            
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                logger.info(f"메시지 전송 성공: {user_id}")
                return {
                    'success': True,
                    'message_id': response.json().get('result_code'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"메시지 전송 실패: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"API 오류: {response.status_code}",
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"메시지 전송 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_message(self, message: KakaoMessage) -> Dict:
        """메시지를 카카오톡 API 형식으로 포맷팅"""
        base_message = {
            "object_type": "text",
            "text": message.content,
            "link": {
                "web_url": "https://smartcompressor.ai",
                "mobile_web_url": "https://smartcompressor.ai"
            }
        }
        
        if message.message_type == MessageType.BUTTON and message.buttons:
            base_message["object_type"] = "buttons"
            base_message["buttons"] = message.buttons
            
        elif message.message_type == MessageType.CAROUSEL:
            base_message["object_type"] = "carousel"
            base_message["carousel"] = {
                "type": "basicCard",
                "items": message.buttons or []
            }
            
        elif message.message_type == MessageType.IMAGE and message.image_url:
            base_message["object_type"] = "image"
            base_message["image_url"] = message.image_url
            
        return base_message
    
    def send_bulk_message(self, user_ids: List[str], message: KakaoMessage) -> Dict:
        """대량 메시지 전송"""
        try:
            results = []
            success_count = 0
            
            for user_id in user_ids:
                result = self.send_message(user_id, message)
                results.append({
                    'user_id': user_id,
                    'result': result
                })
                
                if result['success']:
                    success_count += 1
                
                # Rate limiting
                import time
                time.sleep(0.6)  # 1분에 100개 제한
            
            return {
                'success': True,
                'total_sent': len(user_ids),
                'success_count': success_count,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"대량 메시지 전송 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def schedule_message(self, user_id: str, message: KakaoMessage, scheduled_time: datetime) -> Dict:
        """메시지 스케줄링"""
        try:
            scheduled_message = {
                'user_id': user_id,
                'message': message,
                'scheduled_time': scheduled_time,
                'created_at': datetime.now(),
                'status': 'scheduled'
            }
            
            self.message_queue.append(scheduled_message)
            self.message_queue.sort(key=lambda x: x['scheduled_time'])
            
            logger.info(f"메시지 스케줄링 완료: {user_id} - {scheduled_time}")
            return {
                'success': True,
                'scheduled_time': scheduled_time.isoformat(),
                'message': '메시지가 스케줄링되었습니다'
            }
            
        except Exception as e:
            logger.error(f"메시지 스케줄링 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_scheduled_messages(self) -> Dict:
        """스케줄된 메시지 처리"""
        try:
            now = datetime.now()
            processed_count = 0
            
            # 처리할 메시지 찾기
            messages_to_process = [
                msg for msg in self.message_queue
                if msg['scheduled_time'] <= now and msg['status'] == 'scheduled'
            ]
            
            for scheduled_msg in messages_to_process:
                result = self.send_message(
                    scheduled_msg['user_id'],
                    scheduled_msg['message']
                )
                
                if result['success']:
                    scheduled_msg['status'] = 'sent'
                    scheduled_msg['sent_at'] = now
                    processed_count += 1
                else:
                    scheduled_msg['status'] = 'failed'
                    scheduled_msg['error'] = result.get('error')
            
            # 처리된 메시지 제거
            self.message_queue = [
                msg for msg in self.message_queue
                if msg['status'] == 'scheduled'
            ]
            
            return {
                'success': True,
                'processed_count': processed_count,
                'remaining_count': len(self.message_queue)
            }
            
        except Exception as e:
            logger.error(f"스케줄된 메시지 처리 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_message_template(self, template_id: str, template: Dict) -> Dict:
        """메시지 템플릿 생성"""
        try:
            self.message_templates[template_id] = {
                'template': template,
                'created_at': datetime.now(),
                'usage_count': 0
            }
            
            logger.info(f"메시지 템플릿 생성 완료: {template_id}")
            return {
                'success': True,
                'template_id': template_id,
                'message': '템플릿이 생성되었습니다'
            }
            
        except Exception as e:
            logger.error(f"메시지 템플릿 생성 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_message_template(self, template_id: str) -> Optional[Dict]:
        """메시지 템플릿 조회"""
        return self.message_templates.get(template_id)
    
    def send_template_message(self, user_id: str, template_id: str, variables: Dict = None) -> Dict:
        """템플릿 메시지 전송"""
        try:
            template_data = self.get_message_template(template_id)
            if not template_data:
                return {'success': False, 'error': '템플릿을 찾을 수 없습니다'}
            
            # 변수 치환
            content = template_data['template']['content']
            if variables:
                for key, value in variables.items():
                    content = content.replace(f'{{{key}}}', str(value))
            
            # 메시지 생성
            message = KakaoMessage(
                message_type=MessageType(template_data['template']['type']),
                content=content,
                priority=Priority(template_data['template'].get('priority', 'normal'))
            )
            
            # 전송
            result = self.send_message(user_id, message)
            
            if result['success']:
                # 사용 횟수 증가
                self.message_templates[template_id]['usage_count'] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"템플릿 메시지 전송 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def register_user(self, user: KakaoUser) -> Dict:
        """사용자 등록"""
        try:
            self.user_database[user.user_id] = user
            logger.info(f"사용자 등록 완료: {user.user_id}")
            return {
                'success': True,
                'user_id': user.user_id,
                'message': '사용자가 등록되었습니다'
            }
            
        except Exception as e:
            logger.error(f"사용자 등록 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_user_settings(self, user_id: str, settings: Dict) -> Dict:
        """사용자 설정 업데이트"""
        try:
            user = self.user_database.get(user_id)
            if not user:
                return {'success': False, 'error': '사용자를 찾을 수 없습니다'}
            
            if user.notification_settings is None:
                user.notification_settings = {}
            
            user.notification_settings.update(settings)
            
            logger.info(f"사용자 설정 업데이트 완료: {user_id}")
            return {
                'success': True,
                'message': '설정이 업데이트되었습니다'
            }
            
        except Exception as e:
            logger.error(f"사용자 설정 업데이트 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_notification_history(self, user_id: str, limit: int = 50) -> Dict:
        """알림 히스토리 조회"""
        try:
            # 실제 구현에서는 데이터베이스에서 조회
            # 여기서는 메모리에서 시뮬레이션
            history = [
                {
                    'message_id': f'msg_{i}',
                    'content': f'알림 메시지 {i}',
                    'sent_at': (datetime.now() - timedelta(hours=i)).isoformat(),
                    'status': 'sent',
                    'priority': 'normal'
                }
                for i in range(min(limit, 10))
            ]
            
            return {
                'success': True,
                'history': history,
                'total_count': len(history)
            }
            
        except Exception as e:
            logger.error(f"알림 히스토리 조회 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def send_emergency_alert(self, message: str, priority: Priority = Priority.URGENT) -> Dict:
        """긴급 알림 전송"""
        try:
            # 모든 활성 사용자에게 전송
            active_users = [
                user_id for user_id, user in self.user_database.items()
                if user.is_active
            ]
            
            emergency_message = KakaoMessage(
                message_type=MessageType.TEXT,
                content=f"🚨 긴급 알림: {message}",
                priority=priority
            )
            
            result = self.send_bulk_message(active_users, emergency_message)
            
            logger.warning(f"긴급 알림 전송: {message}")
            return result
            
        except Exception as e:
            logger.error(f"긴급 알림 전송 오류: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_service_status(self) -> Dict:
        """서비스 상태 조회"""
        try:
            return {
                'success': True,
                'status': 'active',
                'authenticated': self.access_token is not None,
                'registered_users': len(self.user_database),
                'scheduled_messages': len(self.message_queue),
                'templates_count': len(self.message_templates),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"서비스 상태 조회 오류: {e}")
            return {'success': False, 'error': str(e)}

# 전역 인스턴스
kakao_business_service = KakaoBusinessService(
    api_key="your_kakao_api_key",
    secret_key="your_kakao_secret_key"
)
