"""
권한 관리 서비스 - Stripe & AWS IAM 벤치마킹
세밀한 권한 제어와 역할 기반 접근 제어(RBAC) 구현
"""

import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class Permission(Enum):
    """권한 정의"""
    # 사용자 관리
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # 매장 관리
    STORE_CREATE = "store:create"
    STORE_READ = "store:read"
    STORE_UPDATE = "store:update"
    STORE_DELETE = "store:delete"
    STORE_LIST = "store:list"
    STORE_APPROVE = "store:approve"
    STORE_SUSPEND = "store:suspend"
    
    # AI 진단
    AI_DIAGNOSE = "ai:diagnose"
    AI_TRAIN = "ai:train"
    AI_MODEL_MANAGE = "ai:model_manage"
    
    # 결제 관리
    PAYMENT_READ = "payment:read"
    PAYMENT_PROCESS = "payment:process"
    PAYMENT_REFUND = "payment:refund"
    
    # 알림 관리
    NOTIFICATION_SEND = "notification:send"
    NOTIFICATION_READ = "notification:read"
    NOTIFICATION_MANAGE = "notification:manage"
    
    # 로그 관리
    LOG_READ = "log:read"
    LOG_EXPORT = "log:export"
    LOG_DELETE = "log:delete"
    
    # 보안 관리
    SECURITY_READ = "security:read"
    SECURITY_MANAGE = "security:manage"
    IP_BLOCK = "security:ip_block"
    
    # 백업 관리
    BACKUP_CREATE = "backup:create"
    BACKUP_READ = "backup:read"
    BACKUP_DELETE = "backup:delete"
    BACKUP_RESTORE = "backup:restore"
    
    # 시스템 관리
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_CONFIGURE = "system:configure"
    SYSTEM_MAINTENANCE = "system:maintenance"

class Resource(Enum):
    """리소스 정의"""
    USER = "user"
    STORE = "store"
    AI_MODEL = "ai_model"
    PAYMENT = "payment"
    NOTIFICATION = "notification"
    LOG = "log"
    SECURITY = "security"
    BACKUP = "backup"
    SYSTEM = "system"

@dataclass
class Policy:
    """정책 정의"""
    name: str
    description: str
    permissions: List[Permission]
    resources: List[Resource]
    conditions: Dict = None
    effect: str = "Allow"  # Allow, Deny

@dataclass
class Role:
    """역할 정의"""
    name: str
    description: str
    policies: List[str]  # Policy 이름들
    is_system_role: bool = False

@dataclass
class UserPermission:
    """사용자 권한"""
    user_id: str
    roles: List[str]
    permissions: List[Permission]
    resource_restrictions: Dict[Resource, List[str]] = None  # 리소스별 제한
    expires_at: Optional[datetime] = None

class AuthorizationService:
    """
    Stripe & AWS IAM을 벤치마킹한 고급 권한 관리 서비스
    """
    
    def __init__(self):
        self.policies: Dict[str, Policy] = {}
        self.roles: Dict[str, Role] = {}
        self.user_permissions: Dict[str, UserPermission] = {}
        
        self._initialize_default_policies()
        self._initialize_default_roles()
        
        logger.info("AuthorizationService 초기화 완료")

    def _initialize_default_policies(self):
        """기본 정책 초기화"""
        # 슈퍼 관리자 정책
        self.policies["super_admin_policy"] = Policy(
            name="super_admin_policy",
            description="슈퍼 관리자 전체 권한",
            permissions=list(Permission),
            resources=list(Resource)
        )
        
        # 관리자 정책
        self.policies["admin_policy"] = Policy(
            name="admin_policy",
            description="관리자 권한",
            permissions=[
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_LIST,
                Permission.STORE_CREATE, Permission.STORE_READ, Permission.STORE_UPDATE, Permission.STORE_LIST,
                Permission.STORE_APPROVE, Permission.STORE_SUSPEND,
                Permission.AI_DIAGNOSE, Permission.AI_TRAIN, Permission.AI_MODEL_MANAGE,
                Permission.PAYMENT_READ, Permission.PAYMENT_PROCESS, Permission.PAYMENT_REFUND,
                Permission.NOTIFICATION_SEND, Permission.NOTIFICATION_READ, Permission.NOTIFICATION_MANAGE,
                Permission.LOG_READ, Permission.LOG_EXPORT,
                Permission.SECURITY_READ, Permission.SECURITY_MANAGE, Permission.IP_BLOCK,
                Permission.BACKUP_CREATE, Permission.BACKUP_READ, Permission.BACKUP_DELETE, Permission.BACKUP_RESTORE,
                Permission.SYSTEM_MONITOR, Permission.SYSTEM_CONFIGURE
            ],
            resources=list(Resource)
        )
        
        # 매장 주인 정책
        self.policies["store_owner_policy"] = Policy(
            name="store_owner_policy",
            description="매장 주인 권한",
            permissions=[
                Permission.STORE_READ, Permission.STORE_UPDATE,
                Permission.AI_DIAGNOSE,
                Permission.PAYMENT_READ, Permission.PAYMENT_PROCESS,
                Permission.NOTIFICATION_READ,
                Permission.LOG_READ
            ],
            resources=[Resource.STORE, Resource.AI_MODEL, Resource.PAYMENT, Resource.NOTIFICATION, Resource.LOG]
        )
        
        # 매장 관리자 정책
        self.policies["store_manager_policy"] = Policy(
            name="store_manager_policy",
            description="매장 관리자 권한",
            permissions=[
                Permission.STORE_READ, Permission.STORE_UPDATE,
                Permission.AI_DIAGNOSE,
                Permission.PAYMENT_READ,
                Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
                Permission.LOG_READ
            ],
            resources=[Resource.STORE, Resource.AI_MODEL, Resource.PAYMENT, Resource.NOTIFICATION, Resource.LOG]
        )
        
        # 기술자 정책
        self.policies["technician_policy"] = Policy(
            name="technician_policy",
            description="기술자 권한",
            permissions=[
                Permission.AI_DIAGNOSE, Permission.AI_TRAIN, Permission.AI_MODEL_MANAGE,
                Permission.STORE_READ,
                Permission.LOG_READ,
                Permission.SYSTEM_MONITOR
            ],
            resources=[Resource.AI_MODEL, Resource.STORE, Resource.LOG, Resource.SYSTEM]
        )
        
        # 고객 지원 정책
        self.policies["customer_support_policy"] = Policy(
            name="customer_support_policy",
            description="고객 지원 권한",
            permissions=[
                Permission.USER_READ, Permission.USER_UPDATE,
                Permission.STORE_READ,
                Permission.PAYMENT_READ,
                Permission.NOTIFICATION_READ, Permission.NOTIFICATION_SEND,
                Permission.LOG_READ
            ],
            resources=[Resource.USER, Resource.STORE, Resource.PAYMENT, Resource.NOTIFICATION, Resource.LOG]
        )
        
        # 조회자 정책
        self.policies["viewer_policy"] = Policy(
            name="viewer_policy",
            description="조회자 권한",
            permissions=[
                Permission.STORE_READ,
                Permission.PAYMENT_READ,
                Permission.NOTIFICATION_READ,
                Permission.LOG_READ
            ],
            resources=[Resource.STORE, Resource.PAYMENT, Resource.NOTIFICATION, Resource.LOG]
        )

    def _initialize_default_roles(self):
        """기본 역할 초기화"""
        self.roles["super_admin"] = Role(
            name="super_admin",
            description="슈퍼 관리자",
            policies=["super_admin_policy"],
            is_system_role=True
        )
        
        self.roles["admin"] = Role(
            name="admin",
            description="관리자",
            policies=["admin_policy"],
            is_system_role=True
        )
        
        self.roles["store_owner"] = Role(
            name="store_owner",
            description="매장 주인",
            policies=["store_owner_policy"],
            is_system_role=True
        )
        
        self.roles["store_manager"] = Role(
            name="store_manager",
            description="매장 관리자",
            policies=["store_manager_policy"],
            is_system_role=True
        )
        
        self.roles["technician"] = Role(
            name="technician",
            description="기술자",
            policies=["technician_policy"],
            is_system_role=True
        )
        
        self.roles["customer_support"] = Role(
            name="customer_support",
            description="고객 지원",
            policies=["customer_support_policy"],
            is_system_role=True
        )
        
        self.roles["viewer"] = Role(
            name="viewer",
            description="조회자",
            policies=["viewer_policy"],
            is_system_role=True
        )

    def create_policy(self, policy: Policy) -> bool:
        """정책 생성"""
        if policy.name in self.policies:
            logger.warning(f"정책 {policy.name}이 이미 존재합니다.")
            return False
        
        self.policies[policy.name] = policy
        logger.info(f"정책 {policy.name} 생성 완료")
        return True

    def update_policy(self, policy_name: str, policy: Policy) -> bool:
        """정책 업데이트"""
        if policy_name not in self.policies:
            logger.warning(f"정책 {policy_name}을 찾을 수 없습니다.")
            return False
        
        self.policies[policy_name] = policy
        logger.info(f"정책 {policy_name} 업데이트 완료")
        return True

    def delete_policy(self, policy_name: str) -> bool:
        """정책 삭제"""
        if policy_name not in self.policies:
            logger.warning(f"정책 {policy_name}을 찾을 수 없습니다.")
            return False
        
        # 사용 중인 역할 확인
        for role in self.roles.values():
            if policy_name in role.policies:
                logger.warning(f"정책 {policy_name}이 역할 {role.name}에서 사용 중입니다.")
                return False
        
        del self.policies[policy_name]
        logger.info(f"정책 {policy_name} 삭제 완료")
        return True

    def create_role(self, role: Role) -> bool:
        """역할 생성"""
        if role.name in self.roles:
            logger.warning(f"역할 {role.name}이 이미 존재합니다.")
            return False
        
        # 정책 존재 확인
        for policy_name in role.policies:
            if policy_name not in self.policies:
                logger.warning(f"정책 {policy_name}을 찾을 수 없습니다.")
                return False
        
        self.roles[role.name] = role
        logger.info(f"역할 {role.name} 생성 완료")
        return True

    def update_role(self, role_name: str, role: Role) -> bool:
        """역할 업데이트"""
        if role_name not in self.roles:
            logger.warning(f"역할 {role_name}을 찾을 수 없습니다.")
            return False
        
        # 정책 존재 확인
        for policy_name in role.policies:
            if policy_name not in self.policies:
                logger.warning(f"정책 {policy_name}을 찾을 수 없습니다.")
                return False
        
        self.roles[role_name] = role
        logger.info(f"역할 {role_name} 업데이트 완료")
        return True

    def delete_role(self, role_name: str) -> bool:
        """역할 삭제"""
        if role_name not in self.roles:
            logger.warning(f"역할 {role_name}을 찾을 수 없습니다.")
            return False
        
        if self.roles[role_name].is_system_role:
            logger.warning(f"시스템 역할 {role_name}은 삭제할 수 없습니다.")
            return False
        
        # 사용 중인 사용자 확인
        for user_permission in self.user_permissions.values():
            if role_name in user_permission.roles:
                logger.warning(f"역할 {role_name}이 사용자 {user_permission.user_id}에서 사용 중입니다.")
                return False
        
        del self.roles[role_name]
        logger.info(f"역할 {role_name} 삭제 완료")
        return True

    def assign_role_to_user(self, user_id: str, role_name: str) -> bool:
        """사용자에게 역할 할당"""
        if role_name not in self.roles:
            logger.warning(f"역할 {role_name}을 찾을 수 없습니다.")
            return False
        
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = UserPermission(
                user_id=user_id,
                roles=[],
                permissions=[]
            )
        
        if role_name not in self.user_permissions[user_id].roles:
            self.user_permissions[user_id].roles.append(role_name)
            self._update_user_permissions(user_id)
            logger.info(f"사용자 {user_id}에게 역할 {role_name} 할당 완료")
            return True
        
        return False

    def remove_role_from_user(self, user_id: str, role_name: str) -> bool:
        """사용자에서 역할 제거"""
        if user_id not in self.user_permissions:
            return False
        
        if role_name in self.user_permissions[user_id].roles:
            self.user_permissions[user_id].roles.remove(role_name)
            self._update_user_permissions(user_id)
            logger.info(f"사용자 {user_id}에서 역할 {role_name} 제거 완료")
            return True
        
        return False

    def grant_permission_to_user(self, user_id: str, permission: Permission) -> bool:
        """사용자에게 직접 권한 부여"""
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = UserPermission(
                user_id=user_id,
                roles=[],
                permissions=[]
            )
        
        if permission not in self.user_permissions[user_id].permissions:
            self.user_permissions[user_id].permissions.append(permission)
            logger.info(f"사용자 {user_id}에게 권한 {permission.value} 부여 완료")
            return True
        
        return False

    def revoke_permission_from_user(self, user_id: str, permission: Permission) -> bool:
        """사용자에서 직접 권한 제거"""
        if user_id not in self.user_permissions:
            return False
        
        if permission in self.user_permissions[user_id].permissions:
            self.user_permissions[user_id].permissions.remove(permission)
            logger.info(f"사용자 {user_id}에서 권한 {permission.value} 제거 완료")
            return True
        
        return False

    def _update_user_permissions(self, user_id: str):
        """사용자 권한 업데이트 (역할 기반)"""
        if user_id not in self.user_permissions:
            return
        
        user_permission = self.user_permissions[user_id]
        permissions = set(user_permission.permissions)  # 직접 부여된 권한
        
        # 역할에서 권한 수집
        for role_name in user_permission.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                for policy_name in role.policies:
                    if policy_name in self.policies:
                        policy = self.policies[policy_name]
                        permissions.update(policy.permissions)
        
        user_permission.permissions = list(permissions)

    def check_permission(self, user_id: str, permission: Permission, 
                        resource: Resource = None, resource_id: str = None) -> bool:
        """권한 확인"""
        if user_id not in self.user_permissions:
            return False
        
        user_permission = self.user_permissions[user_id]
        
        # 권한 만료 확인
        if user_permission.expires_at and datetime.now() > user_permission.expires_at:
            logger.warning(f"사용자 {user_id}의 권한이 만료되었습니다.")
            return False
        
        # 직접 권한 확인
        if permission in user_permission.permissions:
            # 리소스 제한 확인
            if resource and user_permission.resource_restrictions:
                if resource in user_permission.resource_restrictions:
                    if resource_id not in user_permission.resource_restrictions[resource]:
                        return False
            return True
        
        # 역할 기반 권한 확인
        for role_name in user_permission.roles:
            if role_name in self.roles:
                role = self.roles[role_name]
                for policy_name in role.policies:
                    if policy_name in self.policies:
                        policy = self.policies[policy_name]
                        if permission in policy.permissions:
                            if resource is None or resource in policy.resources:
                                return True
        
        return False

    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """사용자 권한 목록 조회"""
        if user_id not in self.user_permissions:
            return []
        
        return self.user_permissions[user_id].permissions

    def get_user_roles(self, user_id: str) -> List[str]:
        """사용자 역할 목록 조회"""
        if user_id not in self.user_permissions:
            return []
        
        return self.user_permissions[user_id].roles

    def get_role_permissions(self, role_name: str) -> List[Permission]:
        """역할 권한 목록 조회"""
        if role_name not in self.roles:
            return []
        
        permissions = set()
        role = self.roles[role_name]
        
        for policy_name in role.policies:
            if policy_name in self.policies:
                policy = self.policies[policy_name]
                permissions.update(policy.permissions)
        
        return list(permissions)

    def set_resource_restriction(self, user_id: str, resource: Resource, 
                                allowed_ids: List[str]) -> bool:
        """사용자 리소스 제한 설정"""
        if user_id not in self.user_permissions:
            return False
        
        if self.user_permissions[user_id].resource_restrictions is None:
            self.user_permissions[user_id].resource_restrictions = {}
        
        self.user_permissions[user_id].resource_restrictions[resource] = allowed_ids
        logger.info(f"사용자 {user_id}의 {resource.value} 리소스 제한 설정 완료")
        return True

    def get_effective_permissions(self, user_id: str) -> Dict:
        """사용자의 유효한 권한 조회"""
        if user_id not in self.user_permissions:
            return {
                "permissions": [],
                "roles": [],
                "resource_restrictions": {}
            }
        
        user_permission = self.user_permissions[user_id]
        self._update_user_permissions(user_id)
        
        return {
            "permissions": [p.value for p in user_permission.permissions],
            "roles": user_permission.roles,
            "resource_restrictions": {
                resource.value: ids 
                for resource, ids in (user_permission.resource_restrictions or {}).items()
            }
        }

    def audit_permission_check(self, user_id: str, permission: Permission, 
                              resource: Resource = None, resource_id: str = None, 
                              result: bool = False) -> None:
        """권한 확인 감사 로그"""
        logger.info(f"권한 확인 - 사용자: {user_id}, 권한: {permission.value}, "
                   f"리소스: {resource.value if resource else 'None'}, "
                   f"리소스ID: {resource_id or 'None'}, 결과: {result}")

# 싱글톤 인스턴스
authorization_service = AuthorizationService()
