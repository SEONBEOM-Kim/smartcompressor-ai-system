import sentry_sdk
from typing import Optional, Dict, Any


class ErrorTrackingService:
    """
    SignalCraft 시스템의 Sentry 기반 에러 추적 서비스
    """
    
    @staticmethod
    def capture_exception(
        exception: Exception, 
        context: Optional[Dict[str, Any]] = None,
        user_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        예외를 Sentry에 기록합니다.
        
        Args:
            exception: 기록할 예외 객체
            context: 추가 컨텍스트 정보 (예: 요청 데이터, 사용자 정보 등)
            user_info: 사용자 관련 정보 (예: user_id, username 등)
        """
        with sentry_sdk.push_scope() as scope:
            if context:
                scope.set_context("additional_info", context)
            
            if user_info:
                scope.user = user_info
            
            sentry_sdk.capture_exception(exception)

    @staticmethod
    def capture_message(
        message: str, 
        level: str = 'info',
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        메시지를 Sentry에 기록합니다.
        
        Args:
            message: 기록할 메시지
            level: 로그 레벨 ('debug', 'info', 'warning', 'error', 'fatal')
            context: 추가 컨텍스트 정보
        """
        with sentry_sdk.push_scope() as scope:
            if context:
                scope.set_context("additional_info", context)
            
            sentry_sdk.capture_message(message, level=level)

    @staticmethod
    def set_tag(key: str, value: str) -> None:
        """
        Sentry 이벤트에 태그를 추가합니다.
        
        Args:
            key: 태그 키
            value: 태그 값
        """
        sentry_sdk.set_tag(key, value)

    @staticmethod
    def set_extra(key: str, value: Any) -> None:
        """
        Sentry 이벤트에 추가 데이터를 설정합니다.
        
        Args:
            key: 데이터 키
            value: 데이터 값
        """
        sentry_sdk.set_extra(key, value)

    @staticmethod
    def start_transaction(name: str, op: str = "default") -> sentry_sdk.Transaction:
        """
        Sentry 트랜잭션을 시작합니다. (성능 모니터링용)
        
        Args:
            name: 트랜잭션 이름
            op: 작업 유형 (예: 'http.server', 'db.sql.query' 등)
        
        Returns:
            Transaction 객체
        """
        from sentry_sdk import start_transaction
        
        transaction = start_transaction(name=name, op=op)
        return transaction