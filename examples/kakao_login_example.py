#!/usr/bin/env python3
"""
카카오 로그인 구현 예제
.env 파일에서 카카오 API 키를 로드하여 사용하는 방법
"""

import os
import requests
import json
from flask import Flask, request, redirect, session, jsonify
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key_here')

class KakaoLogin:
    """카카오 로그인 클래스"""
    
    def __init__(self):
        self.rest_api_key = os.getenv('KAKAO_REST_API_KEY')
        self.client_secret = os.getenv('KAKAO_CLIENT_SECRET')
        self.redirect_uri = os.getenv('KAKAO_REDIRECT_URI')
        self.admin_key = os.getenv('KAKAO_ADMIN_KEY')
        
        if not all([self.rest_api_key, self.client_secret, self.redirect_uri]):
            raise ValueError("카카오 API 키가 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    def get_auth_url(self):
        """카카오 로그인 URL 생성"""
        kakao_oauth_url = "https://kauth.kakao.com/oauth/authorize"
        params = {
            'client_id': self.rest_api_key,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code'
        }
        
        # URL 파라미터 생성
        param_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{kakao_oauth_url}?{param_string}"
    
    def get_access_token(self, code):
        """인가 코드로 액세스 토큰 발급"""
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.rest_api_key,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        
        response = requests.post(token_url, data=data)
        return response.json()
    
    def get_user_info(self, access_token):
        """사용자 정보 조회"""
        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.get(user_info_url, headers=headers)
        return response.json()
    
    def logout(self, access_token):
        """카카오 로그아웃"""
        logout_url = "https://kapi.kakao.com/v1/user/logout"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        response = requests.post(logout_url, headers=headers)
        return response.json()

# 카카오 로그인 인스턴스 생성
try:
    kakao_login = KakaoLogin()
    print("✅ 카카오 로그인 설정 완료!")
except ValueError as e:
    print(f"❌ 카카오 로그인 설정 오류: {e}")
    kakao_login = None

@app.route('/auth/kakao')
def kakao_auth():
    """카카오 로그인 시작"""
    if not kakao_login:
        return jsonify({'error': '카카오 로그인이 설정되지 않았습니다.'}), 500
    
    auth_url = kakao_login.get_auth_url()
    return redirect(auth_url)

@app.route('/auth/kakao/callback')
def kakao_callback():
    """카카오 로그인 콜백"""
    if not kakao_login:
        return jsonify({'error': '카카오 로그인이 설정되지 않았습니다.'}), 500
    
    code = request.args.get('code')
    if not code:
        return jsonify({'error': '인가 코드가 없습니다.'}), 400
    
    try:
        # 액세스 토큰 발급
        token_response = kakao_login.get_access_token(code)
        
        if 'access_token' not in token_response:
            return jsonify({'error': '토큰 발급 실패', 'details': token_response}), 400
        
        access_token = token_response['access_token']
        
        # 사용자 정보 조회
        user_info = kakao_login.get_user_info(access_token)
        
        if 'id' not in user_info:
            return jsonify({'error': '사용자 정보 조회 실패', 'details': user_info}), 400
        
        # 세션에 사용자 정보 저장
        session['kakao_user'] = {
            'id': user_info['id'],
            'nickname': user_info['kakao_account'].get('profile', {}).get('nickname'),
            'email': user_info['kakao_account'].get('email'),
            'access_token': access_token
        }
        
        return jsonify({
            'success': True,
            'message': '카카오 로그인 성공!',
            'user': session['kakao_user']
        })
        
    except Exception as e:
        return jsonify({'error': f'로그인 처리 중 오류: {str(e)}'}), 500

@app.route('/auth/kakao/logout')
def kakao_logout():
    """카카오 로그아웃"""
    if 'kakao_user' not in session:
        return jsonify({'error': '로그인된 사용자가 없습니다.'}), 400
    
    try:
        access_token = session['kakao_user']['access_token']
        kakao_login.logout(access_token)
        
        # 세션에서 사용자 정보 제거
        session.pop('kakao_user', None)
        
        return jsonify({
            'success': True,
            'message': '로그아웃 완료!'
        })
        
    except Exception as e:
        return jsonify({'error': f'로그아웃 처리 중 오류: {str(e)}'}), 500

@app.route('/user/profile')
def user_profile():
    """사용자 프로필 조회"""
    if 'kakao_user' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    return jsonify({
        'user': session['kakao_user']
    })

@app.route('/')
def index():
    """메인 페이지"""
    if 'kakao_user' in session:
        user = session['kakao_user']
        return f"""
        <h1>안녕하세요, {user['nickname']}님!</h1>
        <p>이메일: {user.get('email', 'N/A')}</p>
        <p>카카오 ID: {user['id']}</p>
        <a href="/auth/kakao/logout">로그아웃</a>
        """
    else:
        return """
        <h1>카카오 로그인 예제</h1>
        <a href="/auth/kakao">카카오로 로그인</a>
        """

if __name__ == '__main__':
    print("🚀 카카오 로그인 예제 서버 시작")
    print(f"카카오 REST API 키: {os.getenv('KAKAO_REST_API_KEY', 'Not Set')[:10]}...")
    print(f"리다이렉트 URI: {os.getenv('KAKAO_REDIRECT_URI', 'Not Set')}")
    print("브라우저에서 http://localhost:8000 접속하여 테스트하세요")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
