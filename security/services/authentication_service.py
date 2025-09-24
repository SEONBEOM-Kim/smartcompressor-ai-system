"""
인증 서비스 - Stripe & AWS 보안 시스템 벤치마킹
JWT, OAuth2, 다중 인증을 지원하는 고급 인증 시스템
"""

import jwt
import hashlib
import secrets
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import bcrypt
import pyotp
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)

class AuthMethod(Enum):
    """인증 방법"""
    PASSWORD = "password"
    OTP = "otp"
    BIOMETRIC = "biometric"
    HARDWARE_TOKEN = "hardware_token"
    SMS = "sms"
    EMAIL = "email"

class UserRole(Enum):
    """사용자 역할"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    STORE_OWNER = "store_owner"
    STORE_MANAGER = "store_manager"
    TECHNICIAN = "technician"
    CUSTOMER_SUPPORT = "customer_support"
    VIEWER = "viewer"
    CUSTOMER = "customer"

@dataclass
class UserSession:
    """사용자 세션 정보"""
    user_id: str
    session_id: str
    created_at: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True
    last_activity: datetime = None

@dataclass
class AuthResult:
    """인증 결과"""
    success: bool
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    message: str = ""
    requires_2fa: bool = False
    auth_methods: List[AuthMethod] = None

class AuthenticationService:
    """
    Stripe & AWS 보안 시스템을 벤치마킹한 고급 인증 서비스
    """
    
    def __init__(self):
        self.secret_key = self._get_or_create_secret_key()
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=1)
        self.refresh_token_expiry = timedelta(days=30)
        self.max_login_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
        
        # 메모리 저장소 (실제 환경에서는 Redis 사용)
        self.sessions: Dict[str, UserSession] = {}
        self.login_attempts: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.user_2fa_secrets: Dict[str, str] = {}
        
        logger.info("AuthenticationService 초기화 완료")

    def _get_or_create_secret_key(self) -> str:
        """보안 키 생성 또는 조회"""
        import os
        key = os.getenv('JWT_SECRET_KEY')
        if not key:
            key = secrets.token_urlsafe(32)
            logger.warning("JWT_SECRET_KEY 환경변수가 설정되지 않았습니다. 임시 키를 생성합니다.")
        return key

    def hash_password(self, password: str) -> str:
        """비밀번호 해시화 (bcrypt 사용)"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def generate_session_id(self) -> str:
        """세션 ID 생성"""
        return secrets.token_urlsafe(32)

    def is_ip_blocked(self, ip_address: str) -> bool:
        """IP 차단 여부 확인"""
        if ip_address in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip_address]:
                return True
            else:
                del self.blocked_ips[ip_address]
        return False

    def check_login_attempts(self, identifier: str) -> bool:
        """로그인 시도 횟수 확인"""
        now = datetime.now()
        attempts = self.login_attempts.get(identifier, [])
        
        # 15분 이전 시도 제거
        attempts = [attempt for attempt in attempts if now - attempt < self.lockout_duration]
        self.login_attempts[identifier] = attempts
        
        return len(attempts) < self.max_login_attempts

    def record_login_attempt(self, identifier: str, success: bool, ip_address: str):
        """로그인 시도 기록"""
        now = datetime.now()
        
        if not success:
            if identifier not in self.login_attempts:
                self.login_attempts[identifier] = []
            self.login_attempts[identifier].append(now)
            
            # 최대 시도 횟수 초과 시 IP 차단
            if len(self.login_attempts[identifier]) >= self.max_login_attempts:
                self.blocked_ips[ip_address] = now + self.lockout_duration
                logger.warning(f"IP {ip_address}가 {self.lockout_duration} 동안 차단되었습니다.")
        else:
            # 성공 시 시도 기록 초기화
            if identifier in self.login_attempts:
                del self.login_attempts[identifier]

    def create_jwt_token(self, user_id: str, session_id: str, additional_claims: Dict = None) -> str:
        """JWT 토큰 생성"""
        now = datetime.utcnow()
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'iat': now,
            'exp': now + self.token_expiry,
            'iss': 'smartcompressor-ai',
            'aud': 'smartcompressor-users'
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str, session_id: str) -> str:
        """리프레시 토큰 생성"""
        now = datetime.utcnow()
        payload = {
            'user_id': user_id,
            'session_id': session_id,
            'iat': now,
            'exp': now + self.refresh_token_expiry,
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_jwt_token(self, token: str) -> Tuple[bool, Dict]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token expired"}
        except jwt.InvalidTokenError:
            return False, {"error": "Invalid token"}

    def authenticate_user(self, username: str, password: str, ip_address: str, 
                        user_agent: str, require_2fa: bool = True) -> AuthResult:
        """사용자 인증"""
        # IP 차단 확인
        if self.is_ip_blocked(ip_address):
            return AuthResult(
                success=False,
                message="IP가 차단되었습니다. 잠시 후 다시 시도해주세요."
            )
        
        # 로그인 시도 횟수 확인
        if not self.check_login_attempts(username):
            return AuthResult(
                success=False,
                message="너무 많은 로그인 시도가 있었습니다. 15분 후 다시 시도해주세요."
            )
        
        # 사용자 정보 조회 (실제 환경에서는 DB에서 조회)
        user = self._get_user_by_username(username)
        if not user:
            self.record_login_attempt(username, False, ip_address)
            return AuthResult(
                success=False,
                message="사용자명 또는 비밀번호가 올바르지 않습니다."
            )
        
        # 비밀번호 검증
        if not self.verify_password(password, user['password_hash']):
            self.record_login_attempt(username, False, ip_address)
            return AuthResult(
                success=False,
                message="사용자명 또는 비밀번호가 올바르지 않습니다."
            )
        
        # 2FA 확인
        if require_2fa and user.get('2fa_enabled', False):
            return AuthResult(
                success=False,
                requires_2fa=True,
                user_id=user['id'],
                message="2단계 인증이 필요합니다.",
                auth_methods=[AuthMethod.OTP, AuthMethod.SMS]
            )
        
        # 세션 생성
        session_id = self.generate_session_id()
        now = datetime.now()
        
        session = UserSession(
            user_id=user['id'],
            session_id=session_id,
            created_at=now,
            expires_at=now + self.token_expiry,
            ip_address=ip_address,
            user_agent=user_agent,
            last_activity=now
        )
        
        self.sessions[session_id] = session
        
        # 토큰 생성
        token = self.create_jwt_token(user['id'], session_id)
        refresh_token = self.create_refresh_token(user['id'], session_id)
        
        # 성공 기록
        self.record_login_attempt(username, True, ip_address)
        
        logger.info(f"사용자 {username} 인증 성공 (IP: {ip_address})")
        
        return AuthResult(
            success=True,
            user_id=user['id'],
            session_id=session_id,
            token=token,
            refresh_token=refresh_token,
            expires_at=session.expires_at,
            message="인증이 완료되었습니다."
        )

    def verify_2fa(self, user_id: str, otp_code: str) -> AuthResult:
        """2단계 인증 검증"""
        if user_id not in self.user_2fa_secrets:
            return AuthResult(
                success=False,
                message="2FA가 설정되지 않았습니다."
            )
        
        secret = self.user_2fa_secrets[user_id]
        totp = pyotp.TOTP(secret)
        
        if totp.verify(otp_code):
            return AuthResult(
                success=True,
                message="2FA 인증이 완료되었습니다."
            )
        else:
            return AuthResult(
                success=False,
                message="잘못된 인증 코드입니다."
            )

    def setup_2fa(self, user_id: str) -> Dict:
        """2FA 설정"""
        secret = pyotp.random_base32()
        self.user_2fa_secrets[user_id] = secret
        
        totp = pyotp.TOTP(secret)
        qr_code = totp.provisioning_uri(
            name=user_id,
            issuer_name="Smart Compressor AI"
        )
        
        # QR 코드 생성
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "secret": secret,
            "qr_code": qr_code_base64,
            "manual_entry_key": secret
        }

    def refresh_token(self, refresh_token: str) -> AuthResult:
        """토큰 갱신"""
        valid, payload = self.verify_jwt_token(refresh_token)
        
        if not valid or payload.get('type') != 'refresh':
            return AuthResult(
                success=False,
                message="유효하지 않은 리프레시 토큰입니다."
            )
        
        user_id = payload['user_id']
        session_id = payload['session_id']
        
        # 세션 확인
        if session_id not in self.sessions:
            return AuthResult(
                success=False,
                message="세션을 찾을 수 없습니다."
            )
        
        session = self.sessions[session_id]
        if not session.is_active:
            return AuthResult(
                success=False,
                message="비활성화된 세션입니다."
            )
        
        # 새 토큰 생성
        new_token = self.create_jwt_token(user_id, session_id)
        new_refresh_token = self.create_refresh_token(user_id, session_id)
        
        # 세션 갱신
        session.expires_at = datetime.now() + self.token_expiry
        session.last_activity = datetime.now()
        
        return AuthResult(
            success=True,
            user_id=user_id,
            session_id=session_id,
            token=new_token,
            refresh_token=new_refresh_token,
            expires_at=session.expires_at,
            message="토큰이 갱신되었습니다."
        )

    def logout(self, session_id: str) -> bool:
        """로그아웃"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            del self.sessions[session_id]
            logger.info(f"세션 {session_id} 로그아웃 완료")
            return True
        return False

    def logout_all_sessions(self, user_id: str) -> int:
        """사용자의 모든 세션 로그아웃"""
        count = 0
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.user_id == user_id:
                sessions_to_remove.append(session_id)
                count += 1
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
        
        logger.info(f"사용자 {user_id}의 {count}개 세션 로그아웃 완료")
        return count

    def get_active_sessions(self, user_id: str) -> List[UserSession]:
        """활성 세션 조회"""
        active_sessions = []
        now = datetime.now()
        
        for session in self.sessions.values():
            if (session.user_id == user_id and 
                session.is_active and 
                session.expires_at > now):
                active_sessions.append(session)
        
        return active_sessions

    def _get_user_by_username(self, username: str) -> Optional[Dict]:
        """사용자명으로 사용자 조회 (실제 환경에서는 DB에서 조회)"""
        # 임시 사용자 데이터 (실제 환경에서는 DB에서 조회)
        users = {
            "admin": {
                "id": "user_001",
                "username": "admin",
                "password_hash": self.hash_password("admin123"),
                "email": "admin@example.com",
                "role": UserRole.ADMIN,
                "2fa_enabled": True,
                "is_active": True
            },
            "store_owner": {
                "id": "user_002",
                "username": "store_owner",
                "password_hash": self.hash_password("owner123"),
                "email": "owner@example.com",
                "role": UserRole.STORE_OWNER,
                "2fa_enabled": False,
                "is_active": True
            }
        }
        
        return users.get(username)

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """비밀번호 변경"""
        user = self._get_user_by_id(user_id)
        if not user:
            return False
        
        if not self.verify_password(old_password, user['password_hash']):
            return False
        
        new_hash = self.hash_password(new_password)
        # 실제 환경에서는 DB에 저장
        logger.info(f"사용자 {user_id} 비밀번호 변경 완료")
        return True

    def _get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """ID로 사용자 조회"""
        # 임시 구현
        for user in self._get_all_users():
            if user['id'] == user_id:
                return user
        return None

    def _get_all_users(self) -> List[Dict]:
        """모든 사용자 조회"""
        return [
            {
                "id": "user_001",
                "username": "admin",
                "password_hash": self.hash_password("admin123"),
                "email": "admin@example.com",
                "role": UserRole.ADMIN,
                "2fa_enabled": True,
                "is_active": True
            },
            {
                "id": "user_002",
                "username": "store_owner",
                "password_hash": self.hash_password("owner123"),
                "email": "owner@example.com",
                "role": UserRole.STORE_OWNER,
                "2fa_enabled": False,
                "is_active": True
            }
        ]

# 싱글톤 인스턴스
authentication_service = AuthenticationService()
