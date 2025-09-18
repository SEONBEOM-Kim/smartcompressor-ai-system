#!/usr/bin/env python3
"""
카카오톡 알림 서비스
카카오 비즈니스 API를 사용하여 카카오톡으로 알림을 전송합니다.
"""

import requests
import json
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KakaoNotificationService:
    """카카오톡 알림 서비스"""
    
    def __init__(self):
        self.access_token = os.getenv('KAKAO_ACCESS_TOKEN', '')
        self.template_id = os.getenv('KAKAO_TEMPLATE_ID', '')
        self.api_url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
        self.template_url = 'https://kapi.kakao.com/v1/api/talk/friends/message/default/send'
        
        # 알림 템플릿
        self.templates = {
            'compressor_anomaly': {
                'title': '🚨 압축기 이상 감지',
                'message': '압축기에서 비정상적인 소음이 감지되었습니다.\n\n디바이스: {device_id}\n시간: {time}\n심각도: {severity}',
                'button_text': '상세보기',
                'button_url': 'https://signalcraft.kr/monitoring'
            },
            'temperature_anomaly': {
                'title': '🌡️ 온도 이상 감지',
                'message': '냉동고 온도가 설정값을 벗어났습니다.\n\n디바이스: {device_id}\n시간: {time}\n심각도: {severity}',
                'button_text': '온도 확인',
                'button_url': 'https://signalcraft.kr/monitoring'
            },
            'connection_lost': {
                'title': '📡 연결 끊김',
                'message': 'ESP32 디바이스 연결이 끊어졌습니다.\n\n디바이스: {device_id}\n시간: {time}',
                'button_text': '연결 상태 확인',
                'button_url': 'https://signalcraft.kr/devices'
            },
            'maintenance_required': {
                'title': '🔧 정기 점검 알림',
                'message': '정기 점검 시기가 되었습니다.\n\n디바이스: {device_id}\n시간: {time}',
                'button_text': '점검 일정 확인',
                'button_url': 'https://signalcraft.kr/maintenance'
            },
            'general_alert': {
                'title': '⚠️ Signalcraft 알림',
                'message': '{message}\n\n디바이스: {device_id}\n시간: {time}\n심각도: {severity}',
                'button_text': '상세보기',
                'button_url': 'https://signalcraft.kr/notifications'
            }
        }
    
    def send_notification(self, phone_number: str, alert_type: str, device_id: str, 
                         severity: str, message: str, data: Dict = None) -> bool:
        """카카오톡 알림 전송"""
        try:
            if not self.access_token:
                logger.error("카카오 액세스 토큰이 설정되지 않았습니다.")
                return False
            
            # 템플릿 선택
            template = self.templates.get(alert_type, self.templates['general_alert'])
            
            # 메시지 포맷팅
            formatted_message = self._format_message(template, device_id, severity, message, data)
            
            # 카카오 API 호출
            success = self._send_kakao_message(phone_number, formatted_message)
            
            if success:
                logger.info(f"카카오톡 알림 전송 성공: {phone_number}")
                return True
            else:
                logger.error(f"카카오톡 알림 전송 실패: {phone_number}")
                return False
                
        except Exception as e:
            logger.error(f"카카오톡 알림 전송 오류: {e}")
            return False
    
    def _format_message(self, template: Dict, device_id: str, severity: str, 
                       message: str, data: Dict = None) -> Dict:
        """메시지 포맷팅"""
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        formatted_text = template['message'].format(
            device_id=device_id,
            time=current_time,
            severity=severity,
            message=message
        )
        
        return {
            'title': template['title'],
            'message': formatted_text,
            'button_text': template['button_text'],
            'button_url': template['button_url']
        }
    
    def _send_kakao_message(self, phone_number: str, message_data: Dict) -> bool:
        """카카오 API로 메시지 전송"""
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # 카카오톡 메시지 데이터
            data = {
                'template_object': json.dumps({
                    'object_type': 'text',
                    'text': f"{message_data['title']}\n\n{message_data['message']}",
                    'link': {
                        'web_url': message_data['button_url'],
                        'mobile_web_url': message_data['button_url']
                    },
                    'button_title': message_data['button_text']
                }, ensure_ascii=False)
            }
            
            response = requests.post(self.api_url, headers=headers, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result_code') == 0:
                    return True
                else:
                    logger.error(f"카카오 API 오류: {result.get('msg', 'Unknown error')}")
                    return False
            else:
                logger.error(f"카카오 API HTTP 오류: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"카카오 메시지 전송 오류: {e}")
            return False
    
    def send_bulk_notification(self, phone_numbers: List[str], alert_type: str, 
                              device_id: str, severity: str, message: str, 
                              data: Dict = None) -> Dict:
        """다중 수신자에게 카카오톡 알림 전송"""
        results = {
            'success': [],
            'failed': []
        }
        
        for phone_number in phone_numbers:
            success = self.send_notification(
                phone_number, alert_type, device_id, severity, message, data
            )
            
            if success:
                results['success'].append(phone_number)
            else:
                results['failed'].append(phone_number)
        
        logger.info(f"카카오톡 대량 전송 완료: 성공 {len(results['success'])}개, 실패 {len(results['failed'])}개")
        return results
    
    def test_notification(self, phone_number: str) -> bool:
        """테스트 알림 전송"""
        return self.send_notification(
            phone_number=phone_number,
            alert_type='general_alert',
            device_id='TEST_DEVICE',
            severity='medium',
            message='Signalcraft 카카오톡 알림 테스트입니다.',
            data={'test': True}
        )
    
    def get_template_list(self) -> Dict:
        """사용 가능한 템플릿 목록 반환"""
        return {
            'templates': list(self.templates.keys()),
            'template_details': self.templates
        }

# 전역 인스턴스
kakao_notification_service = KakaoNotificationService()
