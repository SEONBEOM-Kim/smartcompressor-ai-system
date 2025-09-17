class AuthService:
    @staticmethod
    def validate_login(email, password):
        """로그인 유효성 검사"""
        if email == 'admin' and password == 'admin123!':
            return {
                "success": True,
                "message": "로그인 성공",
                "user": {"email": "admin", "role": "admin"}
            }
        else:
            return {
                "success": False,
                "message": "아이디 또는 비밀번호가 틀렸습니다"
            }
    
    @staticmethod
    def validate_registration(data):
        """회원가입 유효성 검사"""
        name = data.get('name', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        password = data.get('password', '')
        company = data.get('company', '')
        marketing_agree = data.get('marketing_agree', False)

        # 필수 필드 검증
        if not name or not email or not phone or not password:
            return {"success": False, "message": "필수 항목을 모두 입력해주세요."}

        # 이메일 형식 간단 검증
        if '@' not in email:
            return {"success": False, "message": "올바른 이메일 형식을 입력해주세요."}

        # 전화번호 형식 간단 검증
        if len(phone) < 10:
            return {"success": False, "message": "올바른 전화번호를 입력해주세요."}

        # 콘솔에 가입 정보 출력 (실제로는 DB 저장)
        print(f"🎉 신규 가입: {name}, {email}, {phone}, {company}, 마케팅동의: {marketing_agree}")

        return {
            "success": True,
            "message": f"{name}님, 회원가입이 완료되었습니다! 로그인해주세요.",
            "redirect": "/dashboard"
        }
    
    @staticmethod
    def create_kakao_user():
        """카카오 사용자 생성"""
        return {
            'id': 'kakao_user_' + str(int(__import__('time').time() * 1000)),
            'email': 'kakao@example.com',
            'name': '카카오 사용자'
        }
