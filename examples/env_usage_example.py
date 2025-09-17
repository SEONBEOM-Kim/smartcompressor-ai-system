#!/usr/bin/env python3
"""
환경 변수 사용 예제
.env 파일에서 API 키들을 안전하게 로드하는 방법
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class APIConfig:
    """API 설정 클래스"""
    
    def __init__(self):
        # GitHub 설정
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.git_username = os.getenv('GIT_USER_NAME')
        self.git_email = os.getenv('GIT_USER_EMAIL')
        
        # 카카오 로그인 설정
        self.kakao_rest_api_key = os.getenv('KAKAO_REST_API_KEY')
        self.kakao_client_secret = os.getenv('KAKAO_CLIENT_SECRET')
        self.kakao_redirect_uri = os.getenv('KAKAO_REDIRECT_URI')
        
        # 네이버 로그인 설정
        self.naver_client_id = os.getenv('NAVER_CLIENT_ID')
        self.naver_client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.naver_redirect_uri = os.getenv('NAVER_REDIRECT_URI')
        
        # 구글 로그인 설정
        self.google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.google_redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
        
        # Flask 설정
        self.flask_secret_key = os.getenv('FLASK_SECRET_KEY')
        self.flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        self.flask_port = int(os.getenv('FLASK_PORT', 8000))
        
        # 데이터베이스 설정
        self.database_url = os.getenv('DATABASE_URL', 'sqlite:///smartcompressor.db')
        
        # AI 모델 설정
        self.ai_model_path = os.getenv('AI_MODEL_PATH', 'data/models/')
        self.ai_features_path = os.getenv('AI_FEATURES_PATH', 'data/features/')
        
        # 이메일 설정
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
        # 결제 시스템 설정
        self.toss_secret_key = os.getenv('TOSS_PAYMENTS_SECRET_KEY')
        self.toss_client_key = os.getenv('TOSS_PAYMENTS_CLIENT_KEY')
        
        # 알림 설정
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
    def validate_required_keys(self):
        """필수 API 키들이 설정되어 있는지 확인"""
        required_keys = {
            'GitHub Token': self.github_token,
            'Flask Secret Key': self.flask_secret_key,
        }
        
        missing_keys = []
        for key_name, key_value in required_keys.items():
            if not key_value or key_value.startswith('your_'):
                missing_keys.append(key_name)
        
        if missing_keys:
            print(f"❌ 누락된 필수 설정: {', '.join(missing_keys)}")
            return False
        
        print("✅ 모든 필수 설정이 완료되었습니다!")
        return True
    
    def get_kakao_config(self):
        """카카오 로그인 설정 반환"""
        if not self.kakao_rest_api_key or self.kakao_rest_api_key.startswith('your_'):
            return None
        
        return {
            'rest_api_key': self.kakao_rest_api_key,
            'client_secret': self.kakao_client_secret,
            'redirect_uri': self.kakao_redirect_uri
        }
    
    def get_database_config(self):
        """데이터베이스 설정 반환"""
        return {
            'url': self.database_url,
            'echo': self.flask_debug
        }
    
    def get_flask_config(self):
        """Flask 설정 반환"""
        return {
            'secret_key': self.flask_secret_key,
            'debug': self.flask_debug,
            'port': self.flask_port
        }

def main():
    """메인 함수 - 설정 확인 및 사용 예제"""
    print("🔐 API 설정 로드 중...")
    
    # API 설정 로드
    config = APIConfig()
    
    # 필수 설정 확인
    if not config.validate_required_keys():
        print("\n📝 .env 파일을 확인하고 필요한 설정을 추가하세요.")
        return
    
    # 카카오 로그인 설정 확인
    kakao_config = config.get_kakao_config()
    if kakao_config:
        print(f"✅ 카카오 로그인 설정 완료: {kakao_config['rest_api_key'][:10]}...")
    else:
        print("⚠️  카카오 로그인 설정이 필요합니다.")
    
    # Flask 설정 확인
    flask_config = config.get_flask_config()
    print(f"✅ Flask 설정: 포트 {flask_config['port']}, 디버그 {flask_config['debug']}")
    
    # 데이터베이스 설정 확인
    db_config = config.get_database_config()
    print(f"✅ 데이터베이스: {db_config['url']}")

if __name__ == "__main__":
    main()
