#!/usr/bin/env python3
"""
카카오 로그인 API 라우트
"""

from flask import Blueprint, request, jsonify, session
import requests
import os
import secrets

kakao_auth_bp = Blueprint('kakao_auth', __name__)

# 카카오 API 설정
KAKAO_CLIENT_ID = os.environ.get('KAKAO_REST_API_KEY', 'your_kakao_client_id')
KAKAO_REDIRECT_URI = os.environ.get('KAKAO_REDIRECT_URI', 'http://localhost:8000/api/kakao/callback')
KAKAO_CLIENT_SECRET = os.environ.get('KAKAO_CLIENT_SECRET', 'your_kakao_client_secret')

@kakao_auth_bp.route('/api/kakao/login', methods=['GET'])
def kakao_login():
    """카카오 로그인 URL 생성"""
    try:
        # 상태 토큰 생성 (CSRF 방지)
        state = secrets.token_urlsafe(32)
        session['kakao_state'] = state
        
        # 카카오 로그인 URL 생성
        kakao_login_url = (
            f"https://kauth.kakao.com/oauth/authorize?"
            f"client_id={KAKAO_CLIENT_ID}&"
            f"redirect_uri={KAKAO_REDIRECT_URI}&"
            f"response_type=code&"
            f"state={state}"
        )
        
        return jsonify({
            'success': True,
            'login_url': kakao_login_url,
            'message': '카카오 로그인 URL이 생성되었습니다.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'카카오 로그인 URL 생성 오류: {str(e)}'
        }), 500

@kakao_auth_bp.route('/api/kakao/callback', methods=['GET'])
def kakao_callback():
    """카카오 로그인 콜백 처리"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        # 상태 토큰 검증
        if state != session.get('kakao_state'):
            return jsonify({
                'success': False,
                'message': '잘못된 상태 토큰입니다.'
            }), 400
        
        # 액세스 토큰 요청
        token_url = 'https://kauth.kakao.com/oauth/token'
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': KAKAO_CLIENT_ID,
            'client_secret': KAKAO_CLIENT_SECRET,
            'redirect_uri': KAKAO_REDIRECT_URI,
            'code': code
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        if 'access_token' not in token_json:
            return jsonify({
                'success': False,
                'message': '액세스 토큰을 받을 수 없습니다.'
            }), 400
        
        access_token = token_json['access_token']
        
        # 사용자 정보 요청
        user_info_url = 'https://kapi.kakao.com/v2/user/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(user_info_url, headers=headers)
        user_json = user_response.json()
        
        if 'id' not in user_json:
            return jsonify({
                'success': False,
                'message': '사용자 정보를 받을 수 없습니다.'
            }), 400
        
        # 사용자 정보 저장
        user_info = {
            'id': user_json['id'],
            'nickname': user_json['properties'].get('nickname', ''),
            'profile_image': user_json['properties'].get('profile_image', ''),
            'thumbnail_image': user_json['properties'].get('thumbnail_image', '')
        }
        
        # 세션에 사용자 정보 저장
        session['user'] = user_info
        session['kakao_access_token'] = access_token
        
        # 프론트엔드로 리다이렉트
        return f"""
        <script>
            // URL에서 파라미터 제거
            const newUrl = window.location.pathname;
            window.history.replaceState({{}}, document.title, newUrl);
            
            // 부모 창에 로그인 성공 알림
            if (window.opener) {{
                window.opener.postMessage({{type: 'kakao_login_success', user: {user_info}}}, '*');
                window.close();
            }} else {{
                // 팝업이 아닌 경우 페이지 새로고침
                window.location.href = '/?kakao_login=success&session_id={secrets.token_urlsafe(32)}';
            }}
        </script>
        """
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'카카오 로그인 콜백 오류: {str(e)}'
        }), 500

@kakao_auth_bp.route('/api/kakao/logout', methods=['POST'])
def kakao_logout():
    """카카오 로그아웃"""
    try:
        # 세션에서 사용자 정보 제거
        session.pop('user', None)
        session.pop('kakao_access_token', None)
        session.pop('kakao_state', None)
        
        return jsonify({
            'success': True,
            'message': '로그아웃되었습니다.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'로그아웃 오류: {str(e)}'
        }), 500

@kakao_auth_bp.route('/api/kakao/user', methods=['GET'])
def get_user_info():
    """현재 사용자 정보 조회"""
    try:
        user = session.get('user')
        if user:
            return jsonify({
                'success': True,
                'user': user
            })
        else:
            return jsonify({
                'success': False,
                'message': '로그인되지 않았습니다.'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'사용자 정보 조회 오류: {str(e)}'
        }), 500