from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from models import User
import requests
import os
from dotenv import load_dotenv
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# 환경변수 로드
load_dotenv()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    data = request.get_json()
    email_or_id = data.get('email')
    password = data.get('password')

    # ID 또는 이메일로 로그인 가능하도록 수정
    if email_or_id == 'admin' and password == 'admin123!':
        # 관리자 계정 로그인
        session['user_id'] = 1
        session['username'] = 'admin'
        session['is_admin'] = True

        result = {
            'success': True,
            'user': {
                'id': 1,
                'email': 'admin@signalcraft.kr',
                'name': '관리자',
                'company': 'Signalcraft'
            },
            'token': 'admin_token_123'
        }
    else:
        # 일반 사용자 로그인 (데이터베이스 연동)
        result = User.login(email_or_id, password)

    return jsonify(result)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')
    company = data.get('company')
    marketing_agree = data.get('marketing_agree', False)

    user_id = User.register(email, password, name, phone, company, marketing_agree)

    if user_id:
        return jsonify({
            'success': True,
            'message': '회원가입이 완료되었습니다.',
            'user_id': user_id
        })
    else:
        return jsonify({
            'success': False,
            'message': '이미 존재하는 이메일입니다.'
        })

@auth_bp.route('/kakao')
def kakao_auth():
    """카카오 로그인 시작"""
    client_id = os.getenv('KAKAO_CLIENT_ID')
    redirect_uri = os.getenv('KAKAO_REDIRECT_URI')
    
    if not client_id or not redirect_uri:
        return jsonify({
            'success': False,
            'message': '카카오 로그인 설정이 필요합니다.'
        })

    kakao_url = f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&through_account=true&additional_auth_login=true"

    return redirect(kakao_url)

@auth_bp.route('/kakao/callback')
def kakao_callback():
    """카카오 로그인 콜백"""
    try:
        # 요청 파라미터 로깅
        logging.info(f"카카오 콜백 요청: {request.args}")
        logging.info(f"요청 URL: {request.url}")
        logging.info(f"요청 헤더: {dict(request.headers)}")
        
        client_id = os.getenv('KAKAO_CLIENT_ID')
        client_secret = os.getenv('KAKAO_CLIENT_SECRET')
        redirect_uri = os.getenv('KAKAO_REDIRECT_URI')

        code = request.args.get('code')
        error = request.args.get('error')
        error_description = request.args.get('error_description')

        # 오류 처리
        if error:
            logging.error(f"카카오 로그인 오류: {error} - {error_description}")
            return f'''
            <html>
            <head><title>카카오 로그인 오류</title></head>
            <body>
                <h1>카카오 로그인 오류</h1>
                <p>오류: {error}</p>
                <p>설명: {error_description}</p>
                <a href="/">메인 페이지로 돌아가기</a>
            </body>
            </html>
            '''

        if not code:
            logging.error("카카오 인증 코드가 없습니다.")
            logging.error(f"요청 파라미터: {request.args}")
            return f'''
            <html>
            <head><title>카카오 로그인 오류</title></head>
            <body>
                <h1>카카오 로그인 오류</h1>
                <p>인증 코드가 없습니다.</p>
                <p>요청 파라미터: {dict(request.args)}</p>
                <a href="/">메인 페이지로 돌아가기</a>
            </body>
            </html>
            '''

        logging.info(f"카카오 인증 코드: {code}")

        # 카카오에서 액세스 토큰 요청
        token_url = "https://kauth.kakao.com/oauth/token"
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'code': code
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()
        
        logging.info(f"카카오 토큰 응답: {token_json}")

        if 'access_token' not in token_json:
            logging.error(f"카카오 토큰 획득 실패: {token_json}")
            return f'''
            <html>
            <head><title>카카오 로그인 오류</title></head>
            <body>
                <h1>카카오 로그인 오류</h1>
                <p>토큰 획득 실패: {token_json.get('error_description', 'Unknown error')}</p>
                <a href="/">메인 페이지로 돌아가기</a>
            </body>
            </html>
            '''

        # 카카오에서 사용자 정보 요청
        user_url = "https://kapi.kakao.com/v2/user/me"
        headers = {'Authorization': f'Bearer {token_json["access_token"]}'}
        user_response = requests.get(user_url, headers=headers)
        user_json = user_response.json()
        
        logging.info(f"카카오 사용자 정보: {user_json}")

        if 'kakao_account' not in user_json:
            logging.error(f"카카오 사용자 정보 획득 실패: {user_json}")
            return f'''
            <html>
            <head><title>카카오 로그인 오류</title></head>
            <body>
                <h1>카카오 로그인 오류</h1>
                <p>사용자 정보를 가져올 수 없습니다.</p>
                <a href="/">메인 페이지로 돌아가기</a>
            </body>
            </html>
            '''

        # 카카오 사용자 정보 추출
        kakao_account = user_json['kakao_account']
        email = kakao_account.get('email', '')
        name = kakao_account.get('profile', {}).get('nickname', '')
        kakao_id = user_json.get('id', '')

        if not email:
            email = f'kakao_{kakao_id}@kakao.com'

        logging.info(f"카카오 사용자 정보 추출: email={email}, name={name}, id={kakao_id}")

        # 기존 사용자 확인 또는 새 사용자 생성
        from models.database import get_user_by_email, create_user
        existing_user = get_user_by_email(email)

        if existing_user:
            # 기존 사용자 로그인
            session['user_id'] = existing_user['id']
            session['username'] = existing_user['name']
            session['is_admin'] = False
            session['logged_in'] = True
            
            user_data = {
                'id': existing_user['id'],
                'email': email,
                'name': name,
                'company': 'Signalcraft',
                'login_time': '2024-01-01T00:00:00',
                'login_type': 'kakao'
            }
            session['user'] = user_data
            
        else:
            # 새 사용자 생성
            user_id = create_user(email, 'kakao_user', name)
            if user_id:
                session['user_id'] = user_id
                session['username'] = name
                session['is_admin'] = False
                session['logged_in'] = True
                
                user_data = {
                    'id': user_id,
                    'email': email,
                    'name': name,
                    'company': 'Signalcraft',
                    'login_time': '2024-01-01T00:00:00',
                    'login_type': 'kakao'
                }
                session['user'] = user_data
            else:
                logging.error("사용자 생성 실패")
                return f'''
                <html>
                <head><title>카카오 로그인 오류</title></head>
                <body>
                    <h1>카카오 로그인 오류</h1>
                    <p>사용자 생성에 실패했습니다.</p>
                    <a href="/">메인 페이지로 돌아가기</a>
                </body>
                </html>
                '''

        # 메인 페이지로 리다이렉트
        return redirect("/?login=success")

    except Exception as e:
        logging.error(f"카카오 로그인 오류: {e}")
        return f'''
        <html>
        <head><title>카카오 로그인 오류</title></head>
        <body>
            <h1>카카오 로그인 오류</h1>
            <p>오류가 발생했습니다: {str(e)}</p>
            <a href="/">메인 페이지로 돌아가기</a>
        </body>
        </html>
        '''

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """사용자 로그아웃"""
    session.clear()
    return jsonify({
        'success': True,
        'message': '로그아웃 성공'
    })

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """인증 상태 확인"""
    if 'user_id' in session:
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'is_admin': session.get('is_admin', False)
            }
        })
    else:
        return jsonify({
            'success': True,
            'authenticated': False
        })
