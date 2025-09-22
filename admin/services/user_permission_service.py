#!/usr/bin/env python3
"""
사용자 권한 및 역할 관리 시스템
GitHub를 벤치마킹한 권한 관리 시스템
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import defaultdict
import uuid
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """사용자 역할"""
    SUPER_ADMIN = "super_admin"       # 최고 관리자
    ADMIN = "admin"                   # 관리자
    STORE_OWNER = "store_owner"       # 매장 주인
    STORE_MANAGER = "store_manager"   # 매장 관리자
    TECHNICIAN = "technician"         # 기술자
    CUSTOMER_SUPPORT = "customer_support"  # 고객 지원
    VIEWER = "viewer"                 # 조회자
    GUEST = "guest"                   # 게스트

class Permission(Enum):
    """권한"""
    # 매장 관리
    STORE_CREATE = "store:create"
    STORE_READ = "store:read"
    STORE_UPDATE = "store:update"
    STORE_DELETE = "store:delete"
    STORE_APPROVE = "store:approve"
    STORE_SUSPEND = "store:suspend"
    
    # 사용자 관리
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_ROLE_ASSIGN = "user:role_assign"
    
    # 장비 관리
    DEVICE_CREATE = "device:create"
    DEVICE_READ = "device:read"
    DEVICE_UPDATE = "device:update"
    DEVICE_DELETE = "device:delete"
    DEVICE_CONTROL = "device:control"
    
    # 결제 관리
    PAYMENT_READ = "payment:read"
    PAYMENT_REFUND = "payment:refund"
    PAYMENT_ANALYTICS = "payment:analytics"
    
    # 시스템 관리
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_CONFIG = "system:config"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_LOG = "system:log"
    
    # 고객 지원
    SUPPORT_TICKET_CREATE = "support:ticket_create"
    SUPPORT_TICKET_READ = "support:ticket_read"
    SUPPORT_TICKET_UPDATE = "support:ticket_update"
    SUPPORT_TICKET_DELETE = "support:ticket_delete"

class UserStatus(Enum):
    """사용자 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    LOCKED = "locked"

@dataclass
class User:
    """사용자 클래스"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime] = None
    password_hash: str = ""
    phone: str = ""
    department: str = ""
    store_ids: List[str] = None
    permissions: Set[Permission] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.store_ids is None:
            self.store_ids = []
        if self.permissions is None:
            self.permissions = set()
        if self.metadata is None:
            self.metadata = {}

@dataclass
class Role:
    """역할 클래스"""
    name: UserRole
    display_name: str
    description: str
    permissions: Set[Permission]
    is_system_role: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class PermissionGroup:
    """권한 그룹 클래스"""
    name: str
    display_name: str
    description: str
    permissions: Set[Permission]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AuditLog:
    """감사 로그 클래스"""
    id: str
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str = ""
    user_agent: str = ""
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}

class UserPermissionService:
    """사용자 권한 관리 서비스"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.roles: Dict[UserRole, Role] = {}
        self.permission_groups: Dict[str, PermissionGroup] = {}
        self.audit_logs: List[AuditLog] = []
        self.session_tokens: Dict[str, Dict[str, Any]] = {}
        
        # 콜백 함수들
        self.user_callbacks: List[Callable] = []
        self.permission_callbacks: List[Callable] = []
        
        # 초기화
        self._initialize_system_roles()
        self._initialize_permission_groups()
        self._create_default_admin()
    
    def _initialize_system_roles(self):
        """시스템 역할 초기화"""
        # 최고 관리자
        self.roles[UserRole.SUPER_ADMIN] = Role(
            name=UserRole.SUPER_ADMIN,
            display_name="최고 관리자",
            description="모든 권한을 가진 최고 관리자",
            permissions=set(Permission),
            is_system_role=True
        )
        
        # 관리자
        admin_permissions = {
            Permission.STORE_CREATE, Permission.STORE_READ, Permission.STORE_UPDATE,
            Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
            Permission.DEVICE_READ, Permission.DEVICE_UPDATE,
            Permission.PAYMENT_READ, Permission.PAYMENT_ANALYTICS,
            Permission.SYSTEM_MONITOR, Permission.SYSTEM_CONFIG,
            Permission.SUPPORT_TICKET_READ, Permission.SUPPORT_TICKET_UPDATE
        }
        self.roles[UserRole.ADMIN] = Role(
            name=UserRole.ADMIN,
            display_name="관리자",
            description="시스템 관리 권한을 가진 관리자",
            permissions=admin_permissions,
            is_system_role=True
        )
        
        # 매장 주인
        store_owner_permissions = {
            Permission.STORE_READ, Permission.STORE_UPDATE,
            Permission.DEVICE_READ, Permission.DEVICE_UPDATE, Permission.DEVICE_CONTROL,
            Permission.PAYMENT_READ, Permission.PAYMENT_ANALYTICS,
            Permission.SUPPORT_TICKET_CREATE, Permission.SUPPORT_TICKET_READ
        }
        self.roles[UserRole.STORE_OWNER] = Role(
            name=UserRole.STORE_OWNER,
            display_name="매장 주인",
            description="자신의 매장을 관리할 수 있는 권한",
            permissions=store_owner_permissions,
            is_system_role=True
        )
        
        # 매장 관리자
        store_manager_permissions = {
            Permission.STORE_READ,
            Permission.DEVICE_READ, Permission.DEVICE_UPDATE, Permission.DEVICE_CONTROL,
            Permission.PAYMENT_READ,
            Permission.SUPPORT_TICKET_CREATE, Permission.SUPPORT_TICKET_READ
        }
        self.roles[UserRole.STORE_MANAGER] = Role(
            name=UserRole.STORE_MANAGER,
            display_name="매장 관리자",
            description="매장 운영을 관리할 수 있는 권한",
            permissions=store_manager_permissions,
            is_system_role=True
        )
        
        # 기술자
        technician_permissions = {
            Permission.DEVICE_READ, Permission.DEVICE_UPDATE, Permission.DEVICE_CONTROL,
            Permission.SYSTEM_MONITOR,
            Permission.SUPPORT_TICKET_READ, Permission.SUPPORT_TICKET_UPDATE
        }
        self.roles[UserRole.TECHNICIAN] = Role(
            name=UserRole.TECHNICIAN,
            display_name="기술자",
            description="장비 및 시스템 기술 지원 권한",
            permissions=technician_permissions,
            is_system_role=True
        )
        
        # 고객 지원
        support_permissions = {
            Permission.USER_READ,
            Permission.STORE_READ,
            Permission.SUPPORT_TICKET_CREATE, Permission.SUPPORT_TICKET_READ,
            Permission.SUPPORT_TICKET_UPDATE, Permission.SUPPORT_TICKET_DELETE
        }
        self.roles[UserRole.CUSTOMER_SUPPORT] = Role(
            name=UserRole.CUSTOMER_SUPPORT,
            display_name="고객 지원",
            description="고객 지원 및 티켓 관리 권한",
            permissions=support_permissions,
            is_system_role=True
        )
        
        # 조회자
        viewer_permissions = {
            Permission.STORE_READ, Permission.DEVICE_READ, Permission.PAYMENT_READ
        }
        self.roles[UserRole.VIEWER] = Role(
            name=UserRole.VIEWER,
            display_name="조회자",
            description="읽기 전용 권한",
            permissions=viewer_permissions,
            is_system_role=True
        )
        
        # 게스트
        self.roles[UserRole.GUEST] = Role(
            name=UserRole.GUEST,
            display_name="게스트",
            description="제한된 권한",
            permissions=set(),
            is_system_role=True
        )
    
    def _initialize_permission_groups(self):
        """권한 그룹 초기화"""
        # 매장 관리 그룹
        self.permission_groups["store_management"] = PermissionGroup(
            name="store_management",
            display_name="매장 관리",
            description="매장 관련 모든 권한",
            permissions={
                Permission.STORE_CREATE, Permission.STORE_READ, Permission.STORE_UPDATE,
                Permission.STORE_DELETE, Permission.STORE_APPROVE, Permission.STORE_SUSPEND
            }
        )
        
        # 사용자 관리 그룹
        self.permission_groups["user_management"] = PermissionGroup(
            name="user_management",
            display_name="사용자 관리",
            description="사용자 관련 모든 권한",
            permissions={
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE,
                Permission.USER_DELETE, Permission.USER_ROLE_ASSIGN
            }
        )
        
        # 장비 관리 그룹
        self.permission_groups["device_management"] = PermissionGroup(
            name="device_management",
            display_name="장비 관리",
            description="장비 관련 모든 권한",
            permissions={
                Permission.DEVICE_CREATE, Permission.DEVICE_READ, Permission.DEVICE_UPDATE,
                Permission.DEVICE_DELETE, Permission.DEVICE_CONTROL
            }
        )
        
        # 시스템 관리 그룹
        self.permission_groups["system_management"] = PermissionGroup(
            name="system_management",
            display_name="시스템 관리",
            description="시스템 관련 모든 권한",
            permissions={
                Permission.SYSTEM_MONITOR, Permission.SYSTEM_CONFIG,
                Permission.SYSTEM_BACKUP, Permission.SYSTEM_LOG
            }
        )
    
    def _create_default_admin(self):
        """기본 관리자 생성"""
        admin_user = User(
            id="admin_001",
            username="admin",
            email="admin@smartcompressor.com",
            full_name="시스템 관리자",
            role=UserRole.SUPER_ADMIN,
            status=UserStatus.ACTIVE,
            created_at=datetime.now(),
            password_hash=self._hash_password("admin123!"),
            phone="010-0000-0000",
            department="IT",
            permissions=set(Permission)
        )
        
        self.users[admin_user.id] = admin_user
        logger.info("기본 관리자 계정 생성 완료")
    
    def _hash_password(self, password: str) -> str:
        """비밀번호 해시"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, user_data: Dict[str, Any], created_by: str) -> Optional[str]:
        """사용자 생성"""
        try:
            # 사용자 ID 생성
            user_id = f"user_{int(time.time() * 1000)}"
            
            # 역할 확인
            role = UserRole(user_data['role'])
            if role not in self.roles:
                logger.error(f"존재하지 않는 역할: {role}")
                return None
            
            # 사용자 생성
            user = User(
                id=user_id,
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role=role,
                status=UserStatus.PENDING,
                created_at=datetime.now(),
                password_hash=self._hash_password(user_data['password']),
                phone=user_data.get('phone', ''),
                department=user_data.get('department', ''),
                store_ids=user_data.get('store_ids', []),
                metadata=user_data.get('metadata', {})
            )
            
            # 역할에 따른 권한 설정
            user.permissions = self.roles[role].permissions.copy()
            
            # 사용자 저장
            self.users[user_id] = user
            
            # 감사 로그 기록
            self._log_audit_event(
                user_id=created_by,
                action="user_create",
                resource_type="user",
                resource_id=user_id,
                details={"created_user": user.username, "role": role.value}
            )
            
            logger.info(f"사용자 생성: {user_id} - {user.username}")
            return user_id
            
        except Exception as e:
            logger.error(f"사용자 생성 오류: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """사용자 인증"""
        # 사용자 찾기
        user = None
        for u in self.users.values():
            if u.username == username or u.email == username:
                user = u
                break
        
        if not user:
            return None
        
        # 비밀번호 확인
        if user.password_hash != self._hash_password(password):
            return None
        
        # 상태 확인
        if user.status != UserStatus.ACTIVE:
            return None
        
        # 마지막 로그인 시간 업데이트
        user.last_login = datetime.now()
        
        # 감사 로그 기록
        self._log_audit_event(
            user_id=user.id,
            action="user_login",
            resource_type="user",
            resource_id=user.id
        )
        
        return user
    
    def create_session(self, user: User, ip_address: str = "", user_agent: str = "") -> str:
        """세션 생성"""
        session_token = f"session_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
        
        self.session_tokens[session_token] = {
            'user_id': user.id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'ip_address': ip_address,
            'user_agent': user_agent,
            'expires_at': datetime.now() + timedelta(hours=24)
        }
        
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """세션 검증"""
        session_data = self.session_tokens.get(session_token)
        if not session_data:
            return None
        
        # 세션 만료 확인
        if datetime.now() > session_data['expires_at']:
            del self.session_tokens[session_token]
            return None
        
        # 사용자 조회
        user = self.users.get(session_data['user_id'])
        if not user or user.status != UserStatus.ACTIVE:
            del self.session_tokens[session_token]
            return None
        
        # 마지막 활동 시간 업데이트
        session_data['last_activity'] = datetime.now()
        
        return user
    
    def check_permission(self, user: User, permission: Permission, resource_id: str = None) -> bool:
        """권한 확인"""
        # 최고 관리자는 모든 권한
        if user.role == UserRole.SUPER_ADMIN:
            return True
        
        # 권한 확인
        if permission not in user.permissions:
            return False
        
        # 리소스별 권한 확인
        if resource_id and user.role in [UserRole.STORE_OWNER, UserRole.STORE_MANAGER]:
            # 매장 관련 사용자는 자신의 매장만 접근 가능
            if resource_id not in user.store_ids:
                return False
        
        return True
    
    def assign_role(self, user_id: str, new_role: UserRole, assigned_by: str) -> bool:
        """역할 할당"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        old_role = user.role
        user.role = new_role
        user.permissions = self.roles[new_role].permissions.copy()
        
        # 감사 로그 기록
        self._log_audit_event(
            user_id=assigned_by,
            action="role_assign",
            resource_type="user",
            resource_id=user_id,
            details={"old_role": old_role.value, "new_role": new_role.value}
        )
        
        logger.info(f"역할 할당: {user_id} - {old_role.value} -> {new_role.value}")
        return True
    
    def grant_permission(self, user_id: str, permission: Permission, granted_by: str) -> bool:
        """권한 부여"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.permissions.add(permission)
        
        # 감사 로그 기록
        self._log_audit_event(
            user_id=granted_by,
            action="permission_grant",
            resource_type="user",
            resource_id=user_id,
            details={"permission": permission.value}
        )
        
        logger.info(f"권한 부여: {user_id} - {permission.value}")
        return True
    
    def revoke_permission(self, user_id: str, permission: Permission, revoked_by: str) -> bool:
        """권한 회수"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        user.permissions.discard(permission)
        
        # 감사 로그 기록
        self._log_audit_event(
            user_id=revoked_by,
            action="permission_revoke",
            resource_type="user",
            resource_id=user_id,
            details={"permission": permission.value}
        )
        
        logger.info(f"권한 회수: {user_id} - {permission.value}")
        return True
    
    def update_user_status(self, user_id: str, status: UserStatus, updated_by: str, reason: str = None) -> bool:
        """사용자 상태 업데이트"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        old_status = user.status
        user.status = status
        
        # 감사 로그 기록
        self._log_audit_event(
            user_id=updated_by,
            action="user_status_update",
            resource_type="user",
            resource_id=user_id,
            details={"old_status": old_status.value, "new_status": status.value, "reason": reason}
        )
        
        logger.info(f"사용자 상태 변경: {user_id} - {old_status.value} -> {status.value}")
        return True
    
    def assign_store(self, user_id: str, store_id: str, assigned_by: str) -> bool:
        """매장 할당"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if store_id not in user.store_ids:
            user.store_ids.append(store_id)
            
            # 감사 로그 기록
            self._log_audit_event(
                user_id=assigned_by,
                action="store_assign",
                resource_type="user",
                resource_id=user_id,
                details={"store_id": store_id}
            )
            
            logger.info(f"매장 할당: {user_id} - {store_id}")
            return True
        
        return False
    
    def remove_store(self, user_id: str, store_id: str, removed_by: str) -> bool:
        """매장 제거"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        if store_id in user.store_ids:
            user.store_ids.remove(store_id)
            
            # 감사 로그 기록
            self._log_audit_event(
                user_id=removed_by,
                action="store_remove",
                resource_type="user",
                resource_id=user_id,
                details={"store_id": store_id}
            )
            
            logger.info(f"매장 제거: {user_id} - {store_id}")
            return True
        
        return False
    
    def _log_audit_event(self, user_id: str, action: str, resource_type: str, 
                        resource_id: str, details: Dict[str, Any] = None, 
                        ip_address: str = "", user_agent: str = ""):
        """감사 로그 기록"""
        log_id = f"audit_{int(time.time() * 1000)}"
        
        audit_log = AuditLog(
            id=log_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        
        self.audit_logs.append(audit_log)
        
        # 최대 10000개 로그만 유지
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
    
    def get_user(self, user_id: str) -> Optional[User]:
        """사용자 조회"""
        return self.users.get(user_id)
    
    def get_users(self, role: UserRole = None, status: UserStatus = None, limit: int = 100) -> List[User]:
        """사용자 목록 조회"""
        users = list(self.users.values())
        
        if role:
            users = [user for user in users if user.role == role]
        
        if status:
            users = [user for user in users if user.status == status]
        
        # 최신순 정렬
        users.sort(key=lambda x: x.created_at, reverse=True)
        return users[:limit]
    
    def get_audit_logs(self, user_id: str = None, action: str = None, 
                      start_date: datetime = None, end_date: datetime = None,
                      limit: int = 100) -> List[AuditLog]:
        """감사 로그 조회"""
        logs = list(self.audit_logs)
        
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if action:
            logs = [log for log in logs if log.action == action]
        
        if start_date:
            logs = [log for log in logs if log.timestamp >= start_date]
        
        if end_date:
            logs = [log for log in logs if log.timestamp <= end_date]
        
        # 최신순 정렬
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
    
    def get_permission_summary(self, user_id: str) -> Dict[str, Any]:
        """사용자 권한 요약"""
        user = self.users.get(user_id)
        if not user:
            return {}
        
        return {
            'user_id': user_id,
            'username': user.username,
            'role': user.role.value,
            'permissions': [p.value for p in user.permissions],
            'store_ids': user.store_ids,
            'status': user.status.value,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'total_users': len(self.users),
            'active_users': len([u for u in self.users.values() if u.status == UserStatus.ACTIVE]),
            'suspended_users': len([u for u in self.users.values() if u.status == UserStatus.SUSPENDED]),
            'total_roles': len(self.roles),
            'total_permission_groups': len(self.permission_groups),
            'active_sessions': len(self.session_tokens),
            'total_audit_logs': len(self.audit_logs)
        }

# 전역 인스턴스
user_permission_service = UserPermissionService()
