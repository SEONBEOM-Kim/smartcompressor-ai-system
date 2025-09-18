#!/usr/bin/env python3
"""
향상된 인증 라우트
벤치마킹 기반으로 개선된 회원가입 및 로그인 기능을 제공합니다.
"""

from flask import Blueprint, request, jsonify
import logging
import re
from datetime import datetime
from models.user import User
from models.database import create_user, get_user_by_email

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 향상된 인증 라우트 블루프린트 생성
enhanced_auth_bp = Blueprint('enhanced_auth', __name__, url_prefix='/api/auth')

@enhanced_auth_bp.route('/register-enhanced', methods=['POST'])
def register_enhanced():
    """향상된 회원가입"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name', 'email', 'password', 'phone', 'company']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field}은(는) 필수 입력 항목입니다.'
                }), 400
        
        # 이메일 중복 검사
        if get_user_by_email(data['email']):
            return jsonify({
                'success': False,
                'message': '이미 사용 중인 이메일입니다.'
            }), 400
        
        # 비밀번호 강도 검증
        password = data['password']
        if not validate_password_strength(password):
            return jsonify({
                'success': False,
                'message': '비밀번호는 8자 이상, 영문, 숫자, 특수문자를 포함해야 합니다.'
            }), 400
        
        # 전화번호 형식 검증
        phone = data['phone']
        if not validate_phone_number(phone):
            return jsonify({
                'success': False,
                'message': '올바른 전화번호 형식이 아닙니다. (예: 010-1234-5678)'
            }), 400
        
        # 사용자 데이터 준비
        user_data = {
            'email': data['email'],
            'password': data['password'],
            'name': data['name'],
            'phone': phone,
            'company': data['company'],
            'position': data.get('position', ''),
            'industry': data.get('industry', ''),
            'company_size': data.get('company_size', ''),
            'company_email': data.get('company_email', ''),
            'address': data.get('address', ''),
            'purpose': data.get('purpose', []),
            'budget': data.get('budget', ''),
            'timeline': data.get('timeline', ''),
            'device_count': data.get('device_count', ''),
            'email_alerts': data.get('email_alerts', True),
            'email_newsletter': data.get('email_newsletter', False),
            'sms_alerts': data.get('sms_alerts', True),
            'kakao_alerts': data.get('kakao_alerts', False),
            'privacy_agree': data.get('privacy_agree', False),
            'terms_agree': data.get('terms_agree', False),
            'marketing_agree': data.get('marketing_agree', False)
        }
        
        # 필수 동의 항목 검증
        if not user_data['privacy_agree'] or not user_data['terms_agree']:
            return jsonify({
                'success': False,
                'message': '개인정보처리방침 및 서비스 이용약관에 동의해주세요.'
            }), 400
        
        # 사용자 생성
        user_id = create_enhanced_user(user_data)
        
        if user_id:
            # 환영 이메일 발송 (비동기)
            send_welcome_email(user_data)
            
            # 카카오톡 환영 메시지 (설정된 경우)
            if user_data['kakao_alerts']:
                send_welcome_kakao(user_data)
            
            return jsonify({
                'success': True,
                'message': '회원가입이 완료되었습니다.',
                'user_id': user_id,
                'welcome_bonus': {
                    'discount_rate': 50,
                    'discount_period': '첫 달',
                    'message': '첫 달 50% 할인 혜택이 적용되었습니다.'
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '회원가입 중 오류가 발생했습니다.'
            }), 500
            
    except Exception as e:
        logger.error(f"향상된 회원가입 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'회원가입 오류: {str(e)}'
        }), 500

@enhanced_auth_bp.route('/profile', methods=['GET', 'PUT'])
def user_profile():
    """사용자 프로필 조회/수정"""
    try:
        if request.method == 'GET':
            # 프로필 조회
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '사용자 ID가 필요합니다.'
                }), 400
            
            # 사용자 정보 조회 (실제 구현 시)
            profile = get_user_profile(user_id)
            
            if profile:
                return jsonify({
                    'success': True,
                    'profile': profile
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '사용자를 찾을 수 없습니다.'
                }), 404
                
        elif request.method == 'PUT':
            # 프로필 수정
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '사용자 ID가 필요합니다.'
                }), 400
            
            # 프로필 업데이트 (실제 구현 시)
            success = update_user_profile(user_id, data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '프로필이 업데이트되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '프로필 업데이트에 실패했습니다.'
                }), 500
                
    except Exception as e:
        logger.error(f"프로필 처리 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'프로필 처리 오류: {str(e)}'
        }), 500

@enhanced_auth_bp.route('/preferences', methods=['GET', 'PUT'])
def user_preferences():
    """사용자 알림 설정 조회/수정"""
    try:
        if request.method == 'GET':
            user_id = request.args.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '사용자 ID가 필요합니다.'
                }), 400
            
            preferences = get_user_preferences(user_id)
            
            return jsonify({
                'success': True,
                'preferences': preferences
            })
            
        elif request.method == 'PUT':
            data = request.get_json()
            user_id = data.get('user_id')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '사용자 ID가 필요합니다.'
                }), 400
            
            success = update_user_preferences(user_id, data)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': '알림 설정이 업데이트되었습니다.'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '알림 설정 업데이트에 실패했습니다.'
                }), 500
                
    except Exception as e:
        logger.error(f"알림 설정 처리 오류: {e}")
        return jsonify({
            'success': False,
            'message': f'알림 설정 처리 오류: {str(e)}'
        }), 500

def validate_password_strength(password):
    """비밀번호 강도 검증"""
    if len(password) < 8:
        return False
    
    # 영문, 숫자, 특수문자 포함 검증
    has_letter = bool(re.search(r'[A-Za-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[@$!%*#?&]', password))
    
    return has_letter and has_digit and has_special

def validate_phone_number(phone):
    """전화번호 형식 검증"""
    phone_pattern = r'^010-\d{4}-\d{4}$'
    return bool(re.match(phone_pattern, phone))

def create_enhanced_user(user_data):
    """향상된 사용자 생성"""
    try:
        # 기본 사용자 생성
        user_id = User.register(
            email=user_data['email'],
            password=user_data['password'],
            name=user_data['name'],
            phone=user_data['phone'],
            company=user_data['company'],
            marketing_agree=user_data['marketing_agree']
        )
        
        if user_id:
            # 추가 정보 저장 (실제 구현 시 데이터베이스에 저장)
            save_enhanced_user_data(user_id, user_data)
            return user_id
        
        return None
        
    except Exception as e:
        logger.error(f"향상된 사용자 생성 오류: {e}")
        return None

def save_enhanced_user_data(user_id, user_data):
    """향상된 사용자 데이터 저장"""
    # 실제 구현 시 데이터베이스에 저장
    logger.info(f"사용자 {user_id}의 추가 정보 저장: {user_data}")

def get_user_profile(user_id):
    """사용자 프로필 조회"""
    # 실제 구현 시 데이터베이스에서 조회
    return {
        'user_id': user_id,
        'name': '사용자명',
        'email': 'user@example.com',
        'phone': '010-1234-5678',
        'company': '회사명',
        'position': '직책',
        'industry': '산업군',
        'company_size': '회사 규모',
        'created_at': datetime.now().isoformat()
    }

def update_user_profile(user_id, data):
    """사용자 프로필 업데이트"""
    # 실제 구현 시 데이터베이스 업데이트
    logger.info(f"사용자 {user_id} 프로필 업데이트: {data}")
    return True

def get_user_preferences(user_id):
    """사용자 알림 설정 조회"""
    return {
        'email_alerts': True,
        'email_newsletter': False,
        'sms_alerts': True,
        'kakao_alerts': False,
        'marketing_agree': False
    }

def update_user_preferences(user_id, data):
    """사용자 알림 설정 업데이트"""
    # 실제 구현 시 데이터베이스 업데이트
    logger.info(f"사용자 {user_id} 알림 설정 업데이트: {data}")
    return True

def send_welcome_email(user_data):
    """환영 이메일 발송"""
    # 실제 구현 시 이메일 서비스 연동
    logger.info(f"환영 이메일 발송: {user_data['email']}")

def send_welcome_kakao(user_data):
    """카카오톡 환영 메시지 발송"""
    # 실제 구현 시 카카오톡 서비스 연동
    logger.info(f"카카오톡 환영 메시지 발송: {user_data['phone']}")
