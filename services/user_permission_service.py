#!/usr/bin/env python3
"""
사용자 권한 관리 서비스
Stripe Dashboard 스타일의 사용자 권한 관리 시스템
"""

import time
import logging
import hashlib
import uuid
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from sqlite3 import connect
import json
import re
from typing import Dict, List, Optional, Union, Tuple


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """사용자 역할 열거형"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    STORE_OWNER = "store_owner"
    STORE_MANAGER = "store_manager"
    TECHNICIAN = "technician"
    VIEWER = "viewer"

class Permission(Enum):
    """권한 열거형"""
    # 매장 관리
    STORE_CREATE = "store_create"
    STORE_READ = "store_read"
    STORE_UPDATE = "store_update"
    STORE_DELETE = "store_delete"
    
    # 디바이스 관리
    DEVICE_CREATE = "device_create"
    DEVICE_READ = "device_read"
    DEVICE_UPDATE = "device_update"
    DEVICE_DELETE = "device_delete"
    
    # 사용자 관리
    USER_CREATE = "user_create"
    USER_READ = "user_read"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    
    # 알림 관리
    NOTIFICATION_CREATE = "notification_create"
    NOTIFICATION_READ = "notification_read"
    NOTIFICATION_UPDATE = "notification_update"
    NOTIFICATION_DELETE = "notification_delete"
    
    # 분석 및 리포트
    ANALYTICS_READ = "analytics_read"
    REPORT_CREATE = "report_create"
    REPORT_READ = "report_read"
    
    # 시스템 관리
    SYSTEM_CONFIG = "system_config"
    SYSTEM_MONITOR = "system_monitor"

class UserStatus(Enum):
    """사용자 상태 열거형"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

@dataclass
class User:
    """사용자 정보"""
    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: str
    updated_at: str
    last_login: str
    password_hash: str
    profile: Dict
    settings: Dict

@dataclass
class RolePermission:
    """역할별 권한"""
    role: UserRole
    permissions: Set[Permission]
    description: str

@dataclass
class UserStoreAccess:
    """사용자 매장 접근 권한"""
    user_id: str
    store_id: str
    permissions: Set[Permission]
    granted_by: str
    granted_at: str
    expires_at: str

class UserPermissionService:
    """사용자 권한 관리 서비스 (Stripe Dashboard 스타일)"""
    
    def __init__(self, db_path: str = 'data/user_permissions.db'):
        self.db_path = db_path
        self.users = {}
        self.role_permissions = {}
        self.user_store_access = {}
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 기본 역할 권한 설정
        self._setup_default_role_permissions()
        
        # 기존 데이터 로드
        self._load_users()
        self._load_user_store_access()
        
        logger.info("사용자 권한 관리 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 사용자 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        full_name TEXT NOT NULL,
                        role TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        last_login TEXT,
                        password_hash TEXT NOT NULL,
                        profile TEXT DEFAULT '{}',
                        settings TEXT DEFAULT '{}'
                    )
                ''')
                
                # 사용자 매장 접근 권한 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_store_access (
                        user_id TEXT NOT NULL,
                        store_id TEXT NOT NULL,
                        permissions TEXT NOT NULL,
                        granted_by TEXT NOT NULL,
                        granted_at TEXT NOT NULL,
                        expires_at TEXT,
                        PRIMARY KEY (user_id, store_id),
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # 사용자 세션 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT NOT NULL,
                        ip_address TEXT,
                        user_agent TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_store_user ON user_store_access(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_store_store ON user_store_access(store_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id)')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _setup_default_role_permissions(self):
        """기본 역할 권한 설정"""
        try:
            # 슈퍼 관리자 - 모든 권한
            self.role_permissions[UserRole.SUPER_ADMIN] = RolePermission(
                role=UserRole.SUPER_ADMIN,
                permissions=set(Permission),
                description="시스템 전체 관리 권한"
            )
            
            # 관리자 - 대부분의 권한
            admin_permissions = {
                Permission.STORE_CREATE, Permission.STORE_READ, Permission.STORE_UPDATE, Permission.STORE_DELETE,
                Permission.DEVICE_CREATE, Permission.DEVICE_READ, Permission.DEVICE_UPDATE, Permission.DEVICE_DELETE,
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
                Permission.NOTIFICATION_CREATE, Permission.NOTIFICATION_READ, Permission.NOTIFICATION_UPDATE,
                Permission.ANALYTICS_READ, Permission.REPORT_CREATE, Permission.REPORT_READ,
                Permission.SYSTEM_MONITOR
            }
            self.role_permissions[UserRole.ADMIN] = RolePermission(
                role=UserRole.ADMIN,
                permissions=admin_permissions,
                description="시스템 관리 권한"
            )
            
            # 매장 소유자 - 매장 관련 권한
            store_owner_permissions = {
                Permission.STORE_READ, Permission.STORE_UPDATE,
                Permission.DEVICE_CREATE, Permission.DEVICE_READ, Permission.DEVICE_UPDATE, Permission.DEVICE_DELETE,
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
                Permission.NOTIFICATION_CREATE, Permission.NOTIFICATION_READ, Permission.NOTIFICATION_UPDATE,
                Permission.ANALYTICS_READ, Permission.REPORT_READ
            }
            self.role_permissions[UserRole.STORE_OWNER] = RolePermission(
                role=UserRole.STORE_OWNER,
                permissions=store_owner_permissions,
                description="매장 소유자 권한"
            )
            
            # 매장 관리자 - 매장 관리 권한
            store_manager_permissions = {
                Permission.STORE_READ,
                Permission.DEVICE_READ, Permission.DEVICE_UPDATE,
                Permission.USER_READ,
                Permission.NOTIFICATION_READ,
                Permission.ANALYTICS_READ, Permission.REPORT_READ
            }
            self.role_permissions[UserRole.STORE_MANAGER] = RolePermission(
                role=UserRole.STORE_MANAGER,
                permissions=store_manager_permissions,
                description="매장 관리자 권한"
            )
            
            # 기술자 - 디바이스 관리 권한
            technician_permissions = {
                Permission.DEVICE_READ, Permission.DEVICE_UPDATE,
                Permission.NOTIFICATION_READ,
                Permission.ANALYTICS_READ
            }
            self.role_permissions[UserRole.TECHNICIAN] = RolePermission(
                role=UserRole.TECHNICIAN,
                permissions=technician_permissions,
                description="기술자 권한"
            )
            
            # 뷰어 - 읽기 전용 권한
            viewer_permissions = {
                Permission.STORE_READ,
                Permission.DEVICE_READ,
                Permission.USER_READ,
                Permission.NOTIFICATION_READ,
                Permission.ANALYTICS_READ, Permission.REPORT_READ
            }
            self.role_permissions[UserRole.VIEWER] = RolePermission(
                role=UserRole.VIEWER,
                permissions=viewer_permissions,
                description="읽기 전용 권한"
            )
            
        except Exception as e:
            logger.error(f"기본 역할 권한 설정 실패: {e}")
    
    def _load_users(self):
        """사용자 데이터 로드"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users')
                
                for row in cursor.fetchall():
                    user = User(
                        user_id=row[0],
                        username=row[1],
                        email=row[2],
                        full_name=row[3],
                        role=UserRole(row[4]),
                        status=UserStatus(row[5]),
                        created_at=row[6],
                        updated_at=row[7],
                        last_login=row[8] or row[6],
                        password_hash=row[9],
                        profile=json.loads(row[10]) if row[10] else {},
                        settings=json.loads(row[11]) if row[11] else {}
                    )
                    
                    self.users[user.user_id] = user
                
                logger.info(f"사용자 데이터 로드 완료: {len(self.users)}명")
                
        except Exception as e:
            logger.error(f"사용자 데이터 로드 실패: {e}")
    
    def _load_user_store_access(self):
        """사용자 매장 접근 권한 로드"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM user_store_access')
                
                for row in cursor.fetchall():
                    access = UserStoreAccess(
                        user_id=row[0],
                        store_id=row[1],
                        permissions=set(Permission(p) for p in json.loads(row[2])),
                        granted_by=row[3],
                        granted_at=row[4],
                        expires_at=row[5] or ''
                    )
                    
                    key = f"{access.user_id}_{access.store_id}"
                    self.user_store_access[key] = access
                
                logger.info(f"사용자 매장 접근 권한 로드 완료: {len(self.user_store_access)}개")
                
        except Exception as e:
            logger.error(f"사용자 매장 접근 권한 로드 실패: {e}")
    
    def create_user(self, user_data: Dict) -> Tuple[bool, str]:
        """사용자 생성"""
        try:
            # 입력 데이터 검증
            validation_result = self._validate_user_data(user_data)
            if not validation_result[0]:
                return False, validation_result[1]
            
            # 사용자 ID 생성
            user_id = str(uuid.uuid4())
            
            # 중복 확인
            if user_data['email'] in [user.email for user in self.users.values()]:
                return False, "이미 등록된 이메일입니다."
            
            if user_data['username'] in [user.username for user in self.users.values()]:
                return False, "이미 사용 중인 사용자명입니다."
            
            # 비밀번호 해시 생성
            password_hash = self._hash_password(user_data['password'])
            
            # 사용자 객체 생성
            user = User(
                user_id=user_id,
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=UserRole(user_data.get('role', 'viewer')),
                status=UserStatus.PENDING,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                last_login=datetime.now().isoformat(),
                password_hash=password_hash,
                profile=user_data.get('profile', {}),
                settings=user_data.get('settings', {})
            )
            
            # 데이터베이스에 저장
            self._save_user(user)
            
            # 메모리에 추가
            self.users[user.user_id] = user
            
            logger.info(f"사용자 생성 완료: {user.user_id} - {user.username}")
            return True, user_id
            
        except Exception as e:
            logger.error(f"사용자 생성 실패: {e}")
            return False, str(e)
    
    def _validate_user_data(self, user_data: Dict) -> Tuple[bool, str]:
        """사용자 데이터 검증"""
        try:
            required_fields = ['username', 'email', 'full_name', 'password']
            
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    return False, f"필수 필드가 누락되었습니다: {field}"
            
            # 이메일 형식 검증
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, user_data['email']):
                return False, "올바른 이메일 형식이 아닙니다."
            
            # 사용자명 형식 검증
            username_pattern = r'^[a-zA-Z0-9_]{3,20}$'
            if not re.match(username_pattern, user_data['username']):
                return False, "사용자명은 3-20자의 영문, 숫자, 언더스코어만 사용 가능합니다."
            
            # 비밀번호 강도 검증
            password = user_data['password']
            if len(password) < 8:
                return False, "비밀번호는 최소 8자 이상이어야 합니다."
            
            return True, "검증 통과"
            
        except Exception as e:
            logger.error(f"사용자 데이터 검증 실패: {e}")
            return False, str(e)
    
    def _hash_password(self, password: str) -> str:
        """비밀번호 해시 생성"""
        try:
            salt = "signalcraft_salt_2024"
            return hashlib.sha256((password + salt).encode()).hexdigest()
        except Exception as e:
            logger.error(f"비밀번호 해시 생성 실패: {e}")
            return ""
    
    def authenticate_user(self, username: str, password: str) -> Tuple[bool, Optional[Dict]]:
        """사용자 인증"""
        try:
            # 사용자 찾기
            user = None
            for u in self.users.values():
                if u.username == username or u.email == username:
                    user = u
                    break
            
            if not user:
                return False, None
            
            # 비밀번호 확인
            password_hash = self._hash_password(password)
            if user.password_hash != password_hash:
                return False, None
            
            # 상태 확인
            if user.status != UserStatus.ACTIVE:
                return False, None
            
            # 로그인 시간 업데이트
            user.last_login = datetime.now().isoformat()
            self._save_user(user)
            
            # 사용자 정보 반환 (비밀번호 제외)
            user_dict = asdict(user)
            del user_dict['password_hash']
            user_dict['role'] = user.role.value
            user_dict['status'] = user.status.value
            
            return True, user_dict
            
        except Exception as e:
            logger.error(f"사용자 인증 실패: {e}")
            return False, None
    
    def update_user(self, user_id: str, updates: Dict) -> bool:
        """사용자 정보 업데이트"""
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            
            # 업데이트할 필드들
            for field, value in updates.items():
                if hasattr(user, field):
                    if field == 'role':
                        setattr(user, field, UserRole(value))
                    elif field == 'status':
                        setattr(user, field, UserStatus(value))
                    elif field == 'password':
                        setattr(user, field, self._hash_password(value))
                    else:
                        setattr(user, field, value)
            
            user.updated_at = datetime.now().isoformat()
            
            # 데이터베이스 업데이트
            self._save_user(user)
            
            logger.info(f"사용자 정보 업데이트 완료: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"사용자 정보 업데이트 실패: {e}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """사용자 삭제"""
        try:
            if user_id not in self.users:
                return False
            
            # 관련 데이터 삭제
            self._delete_user_store_access(user_id)
            self._delete_user_sessions(user_id)
            
            # 데이터베이스에서 삭제
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                conn.commit()
            
            # 메모리에서 삭제
            del self.users[user_id]
            
            logger.info(f"사용자 삭제 완료: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"사용자 삭제 실패: {e}")
            return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """사용자 정보 조회"""
        try:
            if user_id not in self.users:
                return None
            
            user = self.users[user_id]
            user_dict = asdict(user)
            del user_dict['password_hash']
            user_dict['role'] = user.role.value
            user_dict['status'] = user.status.value
            
            return user_dict
            
        except Exception as e:
            logger.error(f"사용자 정보 조회 실패: {e}")
            return None
    
    def get_users_by_role(self, role: str) -> List[Dict]:
        """역할별 사용자 목록 조회"""
        try:
            users = []
            
            for user in self.users.values():
                if user.role.value == role:
                    user_dict = asdict(user)
                    del user_dict['password_hash']
                    user_dict['role'] = user.role.value
                    user_dict['status'] = user.status.value
                    users.append(user_dict)
            
            return users
            
        except Exception as e:
            logger.error(f"역할별 사용자 목록 조회 실패: {e}")
            return []
    
    def check_permission(self, user_id: str, permission: Permission, store_id: str = None) -> bool:
        """권한 확인"""
        try:
            if user_id not in self.users:
                return False
            
            user = self.users[user_id]
            
            # 슈퍼 관리자는 모든 권한
            if user.role == UserRole.SUPER_ADMIN:
                return True
            
            # 역할 기반 권한 확인
            role_permissions = self.role_permissions.get(user.role, RolePermission(
                role=user.role,
                permissions=set(),
                description=""
            ))
            
            if permission in role_permissions.permissions:
                return True
            
            # 매장별 권한 확인
            if store_id:
                access_key = f"{user_id}_{store_id}"
                if access_key in self.user_store_access:
                    access = self.user_store_access[access_key]
                    
                    # 만료 확인
                    if access.expires_at and datetime.now() > datetime.fromisoformat(access.expires_at):
                        return False
                    
                    if permission in access.permissions:
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"권한 확인 실패: {e}")
            return False
    
    def grant_store_access(self, user_id: str, store_id: str, permissions: List[str], granted_by: str) -> bool:
        """매장 접근 권한 부여"""
        try:
            if user_id not in self.users:
                return False
            
            # 권한 변환
            permission_set = set(Permission(p) for p in permissions)
            
            # 접근 권한 객체 생성
            access = UserStoreAccess(
                user_id=user_id,
                store_id=store_id,
                permissions=permission_set,
                granted_by=granted_by,
                granted_at=datetime.now().isoformat(),
                expires_at=''  # 영구 권한
            )
            
            # 데이터베이스에 저장
            self._save_user_store_access(access)
            
            # 메모리에 추가
            access_key = f"{user_id}_{store_id}"
            self.user_store_access[access_key] = access
            
            logger.info(f"매장 접근 권한 부여 완료: {user_id} -> {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"매장 접근 권한 부여 실패: {e}")
            return False
    
    def revoke_store_access(self, user_id: str, store_id: str) -> bool:
        """매장 접근 권한 철회"""
        try:
            access_key = f"{user_id}_{store_id}"
            
            if access_key not in self.user_store_access:
                return False
            
            # 데이터베이스에서 삭제
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_store_access WHERE user_id = ? AND store_id = ?', 
                             (user_id, store_id))
                conn.commit()
            
            # 메모리에서 삭제
            del self.user_store_access[access_key]
            
            logger.info(f"매장 접근 권한 철회 완료: {user_id} -> {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"매장 접근 권한 철회 실패: {e}")
            return False
    
    def get_user_permissions(self, user_id: str, store_id: str = None) -> List[str]:
        """사용자 권한 목록 조회"""
        try:
            if user_id not in self.users:
                return []
            
            user = self.users[user_id]
            permissions = set()
            
            # 역할 기반 권한
            role_permissions = self.role_permissions.get(user.role, RolePermission(
                role=user.role,
                permissions=set(),
                description=""
            ))
            permissions.update(role_permissions.permissions)
            
            # 매장별 권한
            if store_id:
                access_key = f"{user_id}_{store_id}"
                if access_key in self.user_store_access:
                    access = self.user_store_access[access_key]
                    
                    # 만료 확인
                    if not access.expires_at or datetime.now() <= datetime.fromisoformat(access.expires_at):
                        permissions.update(access.permissions)
            
            return [p.value for p in permissions]
            
        except Exception as e:
            logger.error(f"사용자 권한 목록 조회 실패: {e}")
            return []
    
    def _save_user(self, user: User):
        """사용자 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, email, full_name, role, status, created_at, updated_at, 
                     last_login, password_hash, profile, settings)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user.user_id,
                    user.username,
                    user.email,
                    user.full_name,
                    user.role.value,
                    user.status.value,
                    user.created_at,
                    user.updated_at,
                    user.last_login,
                    user.password_hash,
                    json.dumps(user.profile),
                    json.dumps(user.settings)
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"사용자 저장 실패: {e}")
    
    def _save_user_store_access(self, access: UserStoreAccess):
        """사용자 매장 접근 권한 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO user_store_access 
                    (user_id, store_id, permissions, granted_by, granted_at, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    access.user_id,
                    access.store_id,
                    json.dumps([p.value for p in access.permissions]),
                    access.granted_by,
                    access.granted_at,
                    access.expires_at
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"사용자 매장 접근 권한 저장 실패: {e}")
    
    def _delete_user_store_access(self, user_id: str):
        """사용자의 모든 매장 접근 권한 삭제"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_store_access WHERE user_id = ?', (user_id,))
                conn.commit()
            
            # 메모리에서도 삭제
            keys_to_remove = [key for key in self.user_store_access.keys() if key.startswith(f"{user_id}_")]
            for key in keys_to_remove:
                del self.user_store_access[key]
                
        except Exception as e:
            logger.error(f"사용자 매장 접근 권한 삭제 실패: {e}")
    
    def _delete_user_sessions(self, user_id: str):
        """사용자의 모든 세션 삭제"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM user_sessions WHERE user_id = ?', (user_id,))
                conn.commit()
                
        except Exception as e:
            logger.error(f"사용자 세션 삭제 실패: {e}")

# 전역 서비스 인스턴스
user_permission_service = UserPermissionService()
