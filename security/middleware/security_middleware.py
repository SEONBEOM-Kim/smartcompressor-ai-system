"""
보안 미들웨어 - Stripe & AWS 보안 시스템 벤치마킹
Rate Limiting, CORS, 인증, 권한 검증 등 API 보안 기능
"""

import time
import logging
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
from flask import request, jsonify, g, current_app
from functools import wraps
import ipaddress
import re
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class RateLimit:
    """Rate Limit 설정"""
    requests: int
    window: int  # 초 단위
    burst: int = 0  # 버스트 허용 요청 수

@dataclass
class SecurityEvent:
    """보안 이벤트"""
    event_type: str
    ip_address: str
    user_id: Optional[str]
    endpoint: str
    timestamp: datetime
    severity: str
    details: Dict = None

class SecurityMiddleware:
    """
    Stripe & AWS 보안 시스템을 벤치마킹한 보안 미들웨어
    """
    
    def __init__(self):
        # Rate Limiting
        self.rate_limits: Dict[str, RateLimit] = {
            "default": RateLimit(requests=100, window=60),
            "auth": RateLimit(requests=5, window=60),
            "api": RateLimit(requests=1000, window=3600),
            "upload": RateLimit(requests=10, window=60),
            "admin": RateLimit(requests=200, window=60)
        }
        
        # 요청 카운터 (실제 환경에서는 Redis 사용)
        self.request_counts: Dict[str, deque] = defaultdict(lambda: deque())
        
        # 차단된 IP 목록
        self.blocked_ips: Dict[str, datetime] = {}
        
        # 허용된 IP 목록 (화이트리스트)
        self.allowed_ips: List[str] = []
        
        # CORS 설정
        self.cors_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "https://smartcompressor-ai.com"
        ]
        
        # 보안 헤더 설정
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        }
        
        # 위험한 패턴들
        self.dangerous_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from",
            r"insert\s+into",
            r"update\s+set"
        ]
        
        logger.info("SecurityMiddleware 초기화 완료")

    def rate_limit(self, limit_name: str = "default"):
        """Rate Limiting 데코레이터"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self._check_rate_limit(limit_name):
                    return jsonify({
                        "error": "Rate limit exceeded",
                        "message": "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요.",
                        "retry_after": self.rate_limits[limit_name].window
                    }), 429
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def _check_rate_limit(self, limit_name: str) -> bool:
        """Rate Limit 확인"""
        if limit_name not in self.rate_limits:
            limit_name = "default"
        
        limit = self.rate_limits[limit_name]
        client_id = self._get_client_identifier()
        now = time.time()
        
        # 오래된 요청 제거
        while (client_id in self.request_counts and 
               self.request_counts[client_id] and 
               now - self.request_counts[client_id][0] > limit.window):
            self.request_counts[client_id].popleft()
        
        # 요청 수 확인
        if client_id in self.request_counts:
            current_requests = len(self.request_counts[client_id])
        else:
            current_requests = 0
        
        if current_requests >= limit.requests:
            self._log_security_event("rate_limit_exceeded", {
                "limit_name": limit_name,
                "current_requests": current_requests,
                "limit": limit.requests
            })
            return False
        
        # 요청 기록
        if client_id not in self.request_counts:
            self.request_counts[client_id] = deque()
        self.request_counts[client_id].append(now)
        
        return True

    def _get_client_identifier(self) -> str:
        """클라이언트 식별자 생성"""
        ip = self._get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        
        # IP와 User-Agent를 조합하여 식별자 생성
        identifier = f"{ip}:{hashlib.md5(user_agent.encode()).hexdigest()[:8]}"
        return identifier

    def _get_client_ip(self) -> str:
        """클라이언트 IP 주소 추출"""
        # 프록시 헤더 확인
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            ip = request.headers.get('X-Real-IP')
        else:
            ip = request.remote_addr
        
        return ip

    def ip_whitelist(self, allowed_ips: List[str]):
        """IP 화이트리스트 데코레이터"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                client_ip = self._get_client_ip()
                
                if not self._is_ip_allowed(client_ip, allowed_ips):
                    self._log_security_event("ip_not_allowed", {
                        "client_ip": client_ip,
                        "allowed_ips": allowed_ips
                    })
                    return jsonify({
                        "error": "Access denied",
                        "message": "허용되지 않은 IP 주소입니다."
                    }), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def _is_ip_allowed(self, client_ip: str, allowed_ips: List[str]) -> bool:
        """IP 허용 여부 확인"""
        try:
            client_ip_obj = ipaddress.ip_address(client_ip)
            
            for allowed_ip in allowed_ips:
                if '/' in allowed_ip:
                    # CIDR 표기법
                    network = ipaddress.ip_network(allowed_ip, strict=False)
                    if client_ip_obj in network:
                        return True
                else:
                    # 단일 IP
                    if client_ip == allowed_ip:
                        return True
            
            return False
        except ValueError:
            return False

    def require_auth(self, f):
        """인증 필요 데코레이터"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self._get_auth_token()
            
            if not token:
                return jsonify({
                    "error": "Authentication required",
                    "message": "인증이 필요합니다."
                }), 401
            
            # JWT 토큰 검증
            from security.services.authentication_service import authentication_service
            valid, payload = authentication_service.verify_jwt_token(token)
            
            if not valid:
                self._log_security_event("invalid_token", {
                    "token": token[:20] + "...",
                    "error": payload.get("error", "Unknown error")
                })
                return jsonify({
                    "error": "Invalid token",
                    "message": "유효하지 않은 토큰입니다."
                }), 401
            
            # 사용자 정보를 g에 저장
            g.user_id = payload.get('user_id')
            g.session_id = payload.get('session_id')
            
            return f(*args, **kwargs)
        return decorated_function

    def require_permission(self, permission: str, resource: str = None):
        """권한 필요 데코레이터"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not hasattr(g, 'user_id'):
                    return jsonify({
                        "error": "Authentication required",
                        "message": "인증이 필요합니다."
                    }), 401
                
                # 권한 확인
                from security.services.authorization_service import authorization_service, Permission, Resource
                
                perm_enum = Permission(permission)
                resource_enum = Resource(resource) if resource else None
                
                if not authorization_service.check_permission(g.user_id, perm_enum, resource_enum):
                    self._log_security_event("permission_denied", {
                        "user_id": g.user_id,
                        "permission": permission,
                        "resource": resource,
                        "endpoint": request.endpoint
                    })
                    return jsonify({
                        "error": "Permission denied",
                        "message": "권한이 없습니다."
                    }), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def _get_auth_token(self) -> Optional[str]:
        """인증 토큰 추출"""
        # Authorization 헤더에서 Bearer 토큰 추출
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]
        
        # 쿼리 파라미터에서 토큰 추출
        return request.args.get('token')

    def validate_input(self, required_fields: List[str] = None, 
                      max_length: int = 10000, 
                      allowed_extensions: List[str] = None):
        """입력 검증 데코레이터"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 필수 필드 확인
                if required_fields:
                    missing_fields = []
                    for field in required_fields:
                        if field not in request.json or not request.json[field]:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        return jsonify({
                            "error": "Missing required fields",
                            "message": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
                        }), 400
                
                # XSS 공격 패턴 검사
                if not self._validate_input_safety(request.json):
                    self._log_security_event("xss_attempt", {
                        "user_id": getattr(g, 'user_id', None),
                        "data": str(request.json)[:200]
                    })
                    return jsonify({
                        "error": "Invalid input",
                        "message": "잘못된 입력입니다."
                    }), 400
                
                # 파일 업로드 검증
                if request.files:
                    for file in request.files.values():
                        if not self._validate_file(file, allowed_extensions):
                            return jsonify({
                                "error": "Invalid file",
                                "message": "허용되지 않은 파일 형식입니다."
                            }), 400
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator

    def _validate_input_safety(self, data: Any) -> bool:
        """입력 데이터 안전성 검증"""
        if isinstance(data, dict):
            return all(self._validate_input_safety(v) for v in data.values())
        elif isinstance(data, list):
            return all(self._validate_input_safety(item) for item in data)
        elif isinstance(data, str):
            return not any(re.search(pattern, data, re.IGNORECASE) for pattern in self.dangerous_patterns)
        else:
            return True

    def _validate_file(self, file, allowed_extensions: List[str] = None) -> bool:
        """파일 검증"""
        if not file or not file.filename:
            return False
        
        # 파일 확장자 확인
        if allowed_extensions:
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                return False
        
        # 파일 크기 확인 (10MB 제한)
        file.seek(0, 2)  # 파일 끝으로 이동
        file_size = file.tell()
        file.seek(0)  # 파일 시작으로 이동
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return False
        
        return True

    def cors_headers(self, f):
        """CORS 헤더 추가 데코레이터"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            origin = request.headers.get('Origin')
            
            if origin and origin in self.cors_origins:
                response = f(*args, **kwargs)
                if isinstance(response, tuple):
                    response = response[0]
                
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Max-Age'] = '86400'
                
                return response
            else:
                return f(*args, **kwargs)
        return decorated_function

    def security_headers(self, f):
        """보안 헤더 추가 데코레이터"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)
            if isinstance(response, tuple):
                response = response[0]
            
            for header, value in self.security_headers.items():
                response.headers[header] = value
            
            return response
        return decorated_function

    def log_security_events(self, f):
        """보안 이벤트 로깅 데코레이터"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            client_ip = self._get_client_ip()
            user_id = getattr(g, 'user_id', None)
            
            try:
                response = f(*args, **kwargs)
                
                # 성공적인 요청 로깅
                self._log_security_event("api_request", {
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "status_code": response[1] if isinstance(response, tuple) else 200,
                    "response_time": time.time() - start_time,
                    "user_id": user_id
                })
                
                return response
                
            except Exception as e:
                # 오류 로깅
                self._log_security_event("api_error", {
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "error": str(e),
                    "user_id": user_id
                })
                raise
        return decorated_function

    def _log_security_event(self, event_type: str, details: Dict = None):
        """보안 이벤트 로깅"""
        event = SecurityEvent(
            event_type=event_type,
            ip_address=self._get_client_ip(),
            user_id=getattr(g, 'user_id', None),
            endpoint=request.endpoint or 'unknown',
            timestamp=datetime.now(),
            severity=self._get_event_severity(event_type),
            details=details or {}
        )
        
        logger.warning(f"보안 이벤트: {event.event_type} - IP: {event.ip_address}, "
                      f"사용자: {event.user_id}, 엔드포인트: {event.endpoint}")
        
        # 실제 환경에서는 보안 모니터링 시스템으로 전송
        self._send_to_security_monitoring(event)

    def _get_event_severity(self, event_type: str) -> str:
        """이벤트 심각도 결정"""
        high_severity = ["xss_attempt", "sql_injection", "rate_limit_exceeded", "invalid_token"]
        medium_severity = ["permission_denied", "ip_not_allowed", "api_error"]
        
        if event_type in high_severity:
            return "high"
        elif event_type in medium_severity:
            return "medium"
        else:
            return "low"

    def _send_to_security_monitoring(self, event: SecurityEvent):
        """보안 모니터링 시스템으로 이벤트 전송"""
        # 실제 환경에서는 보안 모니터링 서비스로 전송
        pass

    def block_ip(self, ip_address: str, duration: int = 3600):
        """IP 차단"""
        self.blocked_ips[ip_address] = datetime.now() + timedelta(seconds=duration)
        logger.warning(f"IP {ip_address}가 {duration}초 동안 차단되었습니다.")

    def unblock_ip(self, ip_address: str):
        """IP 차단 해제"""
        if ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
            logger.info(f"IP {ip_address} 차단이 해제되었습니다.")

    def is_ip_blocked(self, ip_address: str) -> bool:
        """IP 차단 여부 확인"""
        if ip_address in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip_address]:
                return True
            else:
                del self.blocked_ips[ip_address]
        return False

    def get_security_stats(self) -> Dict:
        """보안 통계 조회"""
        now = time.time()
        total_requests = sum(len(requests) for requests in self.request_counts.values())
        active_ips = len(self.request_counts)
        blocked_ips = len([ip for ip, block_time in self.blocked_ips.items() 
                          if datetime.now() < block_time])
        
        return {
            "total_requests": total_requests,
            "active_ips": active_ips,
            "blocked_ips": blocked_ips,
            "rate_limits": {name: limit.__dict__ for name, limit in self.rate_limits.items()}
        }

# 싱글톤 인스턴스
security_middleware = SecurityMiddleware()
