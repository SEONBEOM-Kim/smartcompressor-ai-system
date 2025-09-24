#!/usr/bin/env python3
"""
이메일 템플릿 시스템
Slack과 Discord 스타일의 알림 시스템
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import os
from jinja2 import Template, Environment, FileSystemLoader

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailPriority(Enum):
    """이메일 우선순위"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class EmailType(Enum):
    """이메일 타입"""
    TEXT = "text"
    HTML = "html"
    MULTIPART = "multipart"

@dataclass
class EmailMessage:
    """이메일 메시지 데이터 클래스"""
    to: str
    subject: str
    content: str
    html_content: Optional[str] = None
    from_email: Optional[str] = None
    priority: EmailPriority = EmailPriority.NORMAL
    email_type: EmailType = EmailType.HTML
    attachments: List[Dict] = None
    template_id: Optional[str] = None
    variables: Dict = None
    scheduled_time: Optional[datetime] = None

@dataclass
class EmailTemplate:
    """이메일 템플릿 데이터 클래스"""
    template_id: str
    name: str
    subject: str
    html_content: str
    text_content: str
    variables: List[str]
    category: str
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

class EmailTemplateService:
    """이메일 템플릿 서비스"""
    
    def __init__(self, templates_dir: str = "templates/email"):
        self.templates_dir = templates_dir
        self.templates = {}
        self.jinja_env = Environment(loader=FileSystemLoader(templates_dir))
        
        # 템플릿 디렉토리 생성
        os.makedirs(templates_dir, exist_ok=True)
        
        # 기본 템플릿 로드
        self._load_default_templates()
        
        logger.info("이메일 템플릿 서비스 초기화 완료")
    
    def _load_default_templates(self):
        """기본 템플릿 로드"""
        try:
            # 시스템 알림 템플릿
            self.create_template(
                template_id="system_notification",
                name="시스템 알림",
                subject="[SmartCompressor] 시스템 알림",
                html_content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{{ subject }}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f8f9fa; }
                        .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
                        .alert { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }
                        .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }
                        .error { background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 15px 0; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>SmartCompressor AI</h1>
                            <p>무인 아이스크림 매장 관리 시스템</p>
                        </div>
                        <div class="content">
                            <h2>{{ title }}</h2>
                            <p>{{ message }}</p>
                            {% if details %}
                            <div class="alert">
                                <strong>상세 정보:</strong><br>
                                {{ details }}
                            </div>
                            {% endif %}
                            {% if action_url %}
                            <p style="text-align: center; margin: 30px 0;">
                                <a href="{{ action_url }}" style="background: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">확인하기</a>
                            </p>
                            {% endif %}
                        </div>
                        <div class="footer">
                            <p>이 이메일은 SmartCompressor AI 시스템에서 자동으로 발송되었습니다.</p>
                            <p>문의사항이 있으시면 고객지원팀으로 연락해주세요.</p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                text_content="SmartCompressor AI 시스템 알림\n\n{{ title }}\n{{ message }}\n\n{% if details %}상세 정보:\n{{ details }}\n{% endif %}",
                variables=["title", "message", "details", "action_url"],
                category="system"
            )
            
            # 주문 알림 템플릿
            self.create_template(
                template_id="order_notification",
                name="주문 알림",
                subject="[SmartCompressor] 새로운 주문이 들어왔습니다",
                html_content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{{ subject }}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #28a745; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f8f9fa; }
                        .order-info { background: white; padding: 20px; border-radius: 5px; margin: 15px 0; }
                        .order-item { border-bottom: 1px solid #eee; padding: 10px 0; }
                        .order-item:last-child { border-bottom: none; }
                        .total { font-size: 18px; font-weight: bold; color: #28a745; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>새로운 주문</h1>
                            <p>주문 번호: {{ order_number }}</p>
                        </div>
                        <div class="content">
                            <div class="order-info">
                                <h3>주문 정보</h3>
                                <p><strong>고객명:</strong> {{ customer_name }}</p>
                                <p><strong>연락처:</strong> {{ customer_phone }}</p>
                                <p><strong>주문 시간:</strong> {{ order_time }}</p>
                                <p><strong>주문 상태:</strong> {{ order_status }}</p>
                            </div>
                            
                            <div class="order-info">
                                <h3>주문 내역</h3>
                                {% for item in order_items %}
                                <div class="order-item">
                                    <strong>{{ item.name }}</strong> x {{ item.quantity }}<br>
                                    <span style="color: #666;">{{ item.options }}</span><br>
                                    <span class="total">₩{{ item.total_price | format_currency }}</span>
                                </div>
                                {% endfor %}
                                
                                <div style="border-top: 2px solid #28a745; padding-top: 15px; margin-top: 15px;">
                                    <p><strong>총 금액: ₩{{ total_amount | format_currency }}</strong></p>
                                </div>
                            </div>
                            
                            <p style="text-align: center; margin: 30px 0;">
                                <a href="{{ order_url }}" style="background: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">주문 확인하기</a>
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                text_content="새로운 주문이 들어왔습니다\n\n주문 번호: {{ order_number }}\n고객명: {{ customer_name }}\n연락처: {{ customer_phone }}\n주문 시간: {{ order_time }}\n\n주문 내역:\n{% for item in order_items %}- {{ item.name }} x {{ item.quantity }} (₩{{ item.total_price }})\n{% endfor %}\n\n총 금액: ₩{{ total_amount }}",
                variables=["order_number", "customer_name", "customer_phone", "order_time", "order_status", "order_items", "total_amount", "order_url"],
                category="order"
            )
            
            # 결제 알림 템플릿
            self.create_template(
                template_id="payment_notification",
                name="결제 알림",
                subject="[SmartCompressor] 결제가 완료되었습니다",
                html_content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{{ subject }}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #17a2b8; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f8f9fa; }
                        .payment-info { background: white; padding: 20px; border-radius: 5px; margin: 15px 0; }
                        .success { color: #28a745; font-weight: bold; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>결제 완료</h1>
                            <p>주문 번호: {{ order_number }}</p>
                        </div>
                        <div class="content">
                            <div class="payment-info">
                                <h3>결제 정보</h3>
                                <p><strong>결제 방법:</strong> {{ payment_method }}</p>
                                <p><strong>결제 금액:</strong> <span class="success">₩{{ payment_amount | format_currency }}</span></p>
                                <p><strong>결제 시간:</strong> {{ payment_time }}</p>
                                <p><strong>거래 ID:</strong> {{ transaction_id }}</p>
                                <p><strong>결제 상태:</strong> <span class="success">{{ payment_status }}</span></p>
                            </div>
                            
                            <p style="text-align: center; margin: 30px 0;">
                                <a href="{{ payment_url }}" style="background: #17a2b8; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">결제 내역 확인</a>
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                text_content="결제가 완료되었습니다\n\n주문 번호: {{ order_number }}\n결제 방법: {{ payment_method }}\n결제 금액: ₩{{ payment_amount }}\n결제 시간: {{ payment_time }}\n거래 ID: {{ transaction_id }}\n결제 상태: {{ payment_status }}",
                variables=["order_number", "payment_method", "payment_amount", "payment_time", "transaction_id", "payment_status", "payment_url"],
                category="payment"
            )
            
            # 장비 상태 알림 템플릿
            self.create_template(
                template_id="equipment_alert",
                name="장비 상태 알림",
                subject="[SmartCompressor] 장비 상태 알림",
                html_content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{{ subject }}</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: #dc3545; color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f8f9fa; }
                        .alert-info { background: white; padding: 20px; border-radius: 5px; margin: 15px 0; }
                        .status-normal { color: #28a745; }
                        .status-warning { color: #ffc107; }
                        .status-error { color: #dc3545; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>장비 상태 알림</h1>
                            <p>매장: {{ store_name }}</p>
                        </div>
                        <div class="content">
                            <div class="alert-info">
                                <h3>장비 정보</h3>
                                <p><strong>장비명:</strong> {{ equipment_name }}</p>
                                <p><strong>장비 ID:</strong> {{ equipment_id }}</p>
                                <p><strong>현재 상태:</strong> <span class="status-{{ alert_level }}">{{ equipment_status }}</span></p>
                                <p><strong>알림 시간:</strong> {{ alert_time }}</p>
                                <p><strong>알림 레벨:</strong> {{ alert_level }}</p>
                            </div>
                            
                            <div class="alert-info">
                                <h3>상세 정보</h3>
                                <p>{{ alert_message }}</p>
                                {% if sensor_data %}
                                <h4>센서 데이터</h4>
                                <ul>
                                    {% for sensor, value in sensor_data.items() %}
                                    <li><strong>{{ sensor }}:</strong> {{ value }}</li>
                                    {% endfor %}
                                </ul>
                                {% endif %}
                            </div>
                            
                            <p style="text-align: center; margin: 30px 0;">
                                <a href="{{ equipment_url }}" style="background: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px;">장비 상태 확인</a>
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """,
                text_content="장비 상태 알림\n\n매장: {{ store_name }}\n장비명: {{ equipment_name }}\n장비 ID: {{ equipment_id }}\n현재 상태: {{ equipment_status }}\n알림 시간: {{ alert_time }}\n알림 레벨: {{ alert_level }}\n\n상세 정보:\n{{ alert_message }}\n\n{% if sensor_data %}센서 데이터:\n{% for sensor, value in sensor_data.items() %}- {{ sensor }}: {{ value }}\n{% endfor %}{% endif %}",
                variables=["store_name", "equipment_name", "equipment_id", "equipment_status", "alert_time", "alert_level", "alert_message", "sensor_data", "equipment_url"],
                category="equipment"
            )
            
            logger.info("기본 이메일 템플릿 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 템플릿 로드 오류: {e}")
    
    def create_template(self, template_id: str, name: str, subject: str, 
                       html_content: str, text_content: str, 
                       variables: List[str], category: str) -> bool:
        """이메일 템플릿 생성"""
        try:
            template = EmailTemplate(
                template_id=template_id,
                name=name,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                variables=variables,
                category=category,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.templates[template_id] = template
            
            # 파일로 저장
            template_file = os.path.join(self.templates_dir, f"{template_id}.html")
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"이메일 템플릿 생성 완료: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 템플릿 생성 오류: {e}")
            return False
    
    def get_template(self, template_id: str) -> Optional[EmailTemplate]:
        """이메일 템플릿 조회"""
        return self.templates.get(template_id)
    
    def render_template(self, template_id: str, variables: Dict) -> Optional[EmailMessage]:
        """템플릿 렌더링"""
        try:
            template = self.get_template(template_id)
            if not template:
                return None
            
            # Jinja2 템플릿 렌더링
            html_template = self.jinja_env.from_string(template.html_content)
            text_template = self.jinja_env.from_string(template.text_content)
            subject_template = self.jinja_env.from_string(template.subject)
            
            # 변수 치환
            rendered_html = html_template.render(**variables)
            rendered_text = text_template.render(**variables)
            rendered_subject = subject_template.render(**variables)
            
            return EmailMessage(
                to="",  # 실제 사용 시 설정
                subject=rendered_subject,
                content=rendered_text,
                html_content=rendered_html,
                template_id=template_id,
                variables=variables
            )
            
        except Exception as e:
            logger.error(f"템플릿 렌더링 오류: {e}")
            return None
    
    def get_templates_by_category(self, category: str) -> List[EmailTemplate]:
        """카테고리별 템플릿 조회"""
        return [template for template in self.templates.values() if template.category == category]
    
    def update_template(self, template_id: str, **kwargs) -> bool:
        """템플릿 업데이트"""
        try:
            template = self.get_template(template_id)
            if not template:
                return False
            
            # 필드 업데이트
            for key, value in kwargs.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            
            template.updated_at = datetime.now()
            
            # 파일 업데이트
            template_file = os.path.join(self.templates_dir, f"{template_id}.html")
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template.html_content)
            
            logger.info(f"이메일 템플릿 업데이트 완료: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 템플릿 업데이트 오류: {e}")
            return False
    
    def delete_template(self, template_id: str) -> bool:
        """템플릿 삭제"""
        try:
            if template_id not in self.templates:
                return False
            
            del self.templates[template_id]
            
            # 파일 삭제
            template_file = os.path.join(self.templates_dir, f"{template_id}.html")
            if os.path.exists(template_file):
                os.remove(template_file)
            
            logger.info(f"이메일 템플릿 삭제 완료: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 템플릿 삭제 오류: {e}")
            return False
    
    def get_template_list(self) -> List[Dict]:
        """템플릿 목록 조회"""
        try:
            templates = []
            for template in self.templates.values():
                templates.append({
                    'template_id': template.template_id,
                    'name': template.name,
                    'category': template.category,
                    'is_active': template.is_active,
                    'created_at': template.created_at.isoformat() if template.created_at else None,
                    'updated_at': template.updated_at.isoformat() if template.updated_at else None,
                    'variables': template.variables
                })
            
            return sorted(templates, key=lambda x: x['created_at'] or '', reverse=True)
            
        except Exception as e:
            logger.error(f"템플릿 목록 조회 오류: {e}")
            return []
    
    def validate_template(self, template_id: str, variables: Dict) -> Dict:
        """템플릿 유효성 검사"""
        try:
            template = self.get_template(template_id)
            if not template:
                return {'valid': False, 'error': '템플릿을 찾을 수 없습니다'}
            
            # 필수 변수 확인
            missing_variables = []
            for var in template.variables:
                if var not in variables:
                    missing_variables.append(var)
            
            if missing_variables:
                return {
                    'valid': False,
                    'error': f'필수 변수가 누락되었습니다: {", ".join(missing_variables)}'
                }
            
            # 템플릿 렌더링 테스트
            rendered = self.render_template(template_id, variables)
            if not rendered:
                return {'valid': False, 'error': '템플릿 렌더링 실패'}
            
            return {
                'valid': True,
                'rendered_subject': rendered.subject,
                'rendered_content_length': len(rendered.content)
            }
            
        except Exception as e:
            logger.error(f"템플릿 유효성 검사 오류: {e}")
            return {'valid': False, 'error': str(e)}

# 전역 인스턴스
email_template_service = EmailTemplateService()
