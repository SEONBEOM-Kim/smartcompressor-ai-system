#!/usr/bin/env python3
"""
로그 관리 및 분석 시스템
AWS CloudWatch를 벤치마킹한 로그 관리 시스템
"""

import asyncio
import json
import logging
import time
import os
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import deque
import re
import statistics
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """로그 레벨"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogSource(Enum):
    """로그 소스"""
    APPLICATION = "application"
    SYSTEM = "system"
    SECURITY = "security"
    AUDIT = "audit"
    PERFORMANCE = "performance"
    ERROR = "error"

class LogStatus(Enum):
    """로그 상태"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

@dataclass
class LogEntry:
    """로그 엔트리 클래스"""
    id: str
    timestamp: datetime
    level: LogLevel
    source: LogSource
    service: str
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    duration: Optional[float] = None
    status_code: Optional[int] = None
    metadata: Dict[str, Any] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class LogPattern:
    """로그 패턴 클래스"""
    id: str
    name: str
    pattern: str
    description: str
    severity: LogLevel
    category: str
    created_at: datetime
    is_active: bool = True
    match_count: int = 0
    last_match: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class LogAnalysis:
    """로그 분석 결과 클래스"""
    id: str
    analysis_type: str
    start_time: datetime
    end_time: datetime
    total_logs: int
    error_count: int
    warning_count: int
    critical_count: int
    top_errors: List[Dict[str, Any]]
    top_services: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    security_events: List[Dict[str, Any]]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class LogManagementService:
    """로그 관리 서비스"""
    
    def __init__(self):
        self.log_entries: deque = deque(maxlen=100000)  # 최대 10만개 로그 유지
        self.log_patterns: Dict[str, LogPattern] = {}
        self.log_analyses: List[LogAnalysis] = []
        self.log_callbacks: List[Callable] = []
        
        # 로그 디렉토리 설정
        self.log_directory = Path("logs")
        self.log_directory.mkdir(exist_ok=True)
        
        # 아카이브 디렉토리
        self.archive_directory = self.log_directory / "archive"
        self.archive_directory.mkdir(exist_ok=True)
        
        # 로그 파일 설정
        self.log_files = {
            LogSource.APPLICATION: self.log_directory / "application.log",
            LogSource.SYSTEM: self.log_directory / "system.log",
            LogSource.SECURITY: self.log_directory / "security.log",
            LogSource.AUDIT: self.log_directory / "audit.log",
            LogSource.PERFORMANCE: self.log_directory / "performance.log",
            LogSource.ERROR: self.log_directory / "error.log"
        }
        
        # 로그 로테이션 설정
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_files = 10
        self.retention_days = 30
        
        # 로그 패턴 초기화
        self._initialize_log_patterns()
        
        # 로그 모니터링 시작
        self._start_log_monitoring()
    
    def _initialize_log_patterns(self):
        """로그 패턴 초기화"""
        # 에러 패턴
        self.log_patterns["error_pattern"] = LogPattern(
            id="error_pattern",
            name="에러 패턴",
            pattern=r"ERROR|CRITICAL|Exception|Traceback",
            description="에러 및 예외 로그 패턴",
            severity=LogLevel.ERROR,
            category="error",
            created_at=datetime.now()
        )
        
        # 보안 패턴
        self.log_patterns["security_pattern"] = LogPattern(
            id="security_pattern",
            name="보안 패턴",
            pattern=r"unauthorized|forbidden|security|attack|hack|injection",
            description="보안 관련 로그 패턴",
            severity=LogLevel.WARNING,
            category="security"
        )
        
        # 성능 패턴
        self.log_patterns["performance_pattern"] = LogPattern(
            id="performance_pattern",
            name="성능 패턴",
            pattern=r"slow|timeout|latency|performance|memory|cpu",
            description="성능 관련 로그 패턴",
            severity=LogLevel.INFO,
            category="performance"
        )
        
        # 데이터베이스 패턴
        self.log_patterns["database_pattern"] = LogPattern(
            id="database_pattern",
            name="데이터베이스 패턴",
            pattern=r"database|sql|query|connection|transaction",
            description="데이터베이스 관련 로그 패턴",
            severity=LogLevel.INFO,
            category="database"
        )
        
        # API 패턴
        self.log_patterns["api_pattern"] = LogPattern(
            id="api_pattern",
            name="API 패턴",
            pattern=r"api|endpoint|request|response|http",
            description="API 관련 로그 패턴",
            severity=LogLevel.INFO,
            category="api"
        )
    
    def _start_log_monitoring(self):
        """로그 모니터링 시작"""
        # 로그 파일 모니터링 스레드 시작
        for source, log_file in self.log_files.items():
            if log_file.exists():
                thread = threading.Thread(
                    target=self._monitor_log_file,
                    args=(source, log_file),
                    daemon=True
                )
                thread.start()
        
        logger.info("로그 모니터링 시작")
    
    def _monitor_log_file(self, source: LogSource, log_file: Path):
        """로그 파일 모니터링"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                # 파일 끝으로 이동
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        self._process_log_line(source, line.strip())
                    else:
                        time.sleep(1)
        except Exception as e:
            logger.error(f"로그 파일 모니터링 오류 ({source.value}): {e}")
    
    def _process_log_line(self, source: LogSource, line: str):
        """로그 라인 처리"""
        try:
            # 로그 파싱
            log_entry = self._parse_log_line(source, line)
            if log_entry:
                # 로그 저장
                self.log_entries.append(log_entry)
                
                # 패턴 매칭
                self._match_log_patterns(log_entry)
                
                # 콜백 실행
                self._notify_log_entry(log_entry)
                
        except Exception as e:
            logger.error(f"로그 라인 처리 오류: {e}")
    
    def _parse_log_line(self, source: LogSource, line: str) -> Optional[LogEntry]:
        """로그 라인 파싱"""
        try:
            # JSON 로그 형식 파싱 시도
            if line.startswith('{'):
                data = json.loads(line)
                return LogEntry(
                    id=f"log_{int(time.time() * 1000000)}",
                    timestamp=datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat())),
                    level=LogLevel(data.get('level', 'INFO')),
                    source=source,
                    service=data.get('service', 'unknown'),
                    message=data.get('message', line),
                    user_id=data.get('user_id'),
                    session_id=data.get('session_id'),
                    ip_address=data.get('ip_address'),
                    user_agent=data.get('user_agent'),
                    request_id=data.get('request_id'),
                    duration=data.get('duration'),
                    status_code=data.get('status_code'),
                    metadata=data.get('metadata', {})
                )
            
            # 일반 로그 형식 파싱
            else:
                # 타임스탬프 추출
                timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                timestamp = datetime.now()
                if timestamp_match:
                    try:
                        timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                # 로그 레벨 추출
                level = LogLevel.INFO
                for log_level in LogLevel:
                    if log_level.value in line:
                        level = log_level
                        break
                
                return LogEntry(
                    id=f"log_{int(time.time() * 1000000)}",
                    timestamp=timestamp,
                    level=level,
                    source=source,
                    service="unknown",
                    message=line,
                    metadata={}
                )
                
        except Exception as e:
            logger.error(f"로그 라인 파싱 오류: {e}")
            return None
    
    def _match_log_patterns(self, log_entry: LogEntry):
        """로그 패턴 매칭"""
        for pattern in self.log_patterns.values():
            if not pattern.is_active:
                continue
            
            try:
                if re.search(pattern.pattern, log_entry.message, re.IGNORECASE):
                    pattern.match_count += 1
                    pattern.last_match = log_entry.timestamp
                    
                    # 패턴 매칭 알림
                    self._notify_pattern_match(pattern, log_entry)
                    
            except Exception as e:
                logger.error(f"패턴 매칭 오류 ({pattern.name}): {e}")
    
    def _notify_pattern_match(self, pattern: LogPattern, log_entry: LogEntry):
        """패턴 매칭 알림"""
        for callback in self.log_callbacks:
            try:
                callback({
                    'type': 'pattern_match',
                    'pattern': asdict(pattern),
                    'log_entry': asdict(log_entry)
                })
            except Exception as e:
                logger.error(f"패턴 매칭 알림 오류: {e}")
    
    def _notify_log_entry(self, log_entry: LogEntry):
        """로그 엔트리 알림"""
        for callback in self.log_callbacks:
            try:
                callback({
                    'type': 'log_entry',
                    'log_entry': asdict(log_entry)
                })
            except Exception as e:
                logger.error(f"로그 엔트리 알림 오류: {e}")
    
    def write_log(self, level: LogLevel, source: LogSource, service: str, 
                  message: str, **kwargs) -> str:
        """로그 작성"""
        log_entry = LogEntry(
            id=f"log_{int(time.time() * 1000000)}",
            timestamp=datetime.now(),
            level=level,
            source=source,
            service=service,
            message=message,
            user_id=kwargs.get('user_id'),
            session_id=kwargs.get('session_id'),
            ip_address=kwargs.get('ip_address'),
            user_agent=kwargs.get('user_agent'),
            request_id=kwargs.get('request_id'),
            duration=kwargs.get('duration'),
            status_code=kwargs.get('status_code'),
            metadata=kwargs.get('metadata', {})
        )
        
        # 메모리에 저장
        self.log_entries.append(log_entry)
        
        # 파일에 저장
        self._write_to_file(log_entry)
        
        # 패턴 매칭
        self._match_log_patterns(log_entry)
        
        # 콜백 실행
        self._notify_log_entry(log_entry)
        
        return log_entry.id
    
    def _write_to_file(self, log_entry: LogEntry):
        """파일에 로그 작성"""
        try:
            log_file = self.log_files[log_entry.source]
            
            # 로그 파일 로테이션 확인
            self._check_log_rotation(log_file)
            
            # 로그 작성
            with open(log_file, 'a', encoding='utf-8') as f:
                log_data = {
                    'id': log_entry.id,
                    'timestamp': log_entry.timestamp.isoformat(),
                    'level': log_entry.level.value,
                    'source': log_entry.source.value,
                    'service': log_entry.service,
                    'message': log_entry.message,
                    'user_id': log_entry.user_id,
                    'session_id': log_entry.session_id,
                    'ip_address': log_entry.ip_address,
                    'user_agent': log_entry.user_agent,
                    'request_id': log_entry.request_id,
                    'duration': log_entry.duration,
                    'status_code': log_entry.status_code,
                    'metadata': log_entry.metadata
                }
                f.write(json.dumps(log_data, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"로그 파일 작성 오류: {e}")
    
    def _check_log_rotation(self, log_file: Path):
        """로그 파일 로테이션 확인"""
        try:
            if not log_file.exists():
                return
            
            # 파일 크기 확인
            if log_file.stat().st_size > self.max_file_size:
                self._rotate_log_file(log_file)
                
        except Exception as e:
            logger.error(f"로그 로테이션 확인 오류: {e}")
    
    def _rotate_log_file(self, log_file: Path):
        """로그 파일 로테이션"""
        try:
            # 기존 파일들을 번호로 이동
            for i in range(self.max_files - 1, 0, -1):
                old_file = log_file.with_suffix(f'.{i}.log')
                new_file = log_file.with_suffix(f'.{i + 1}.log')
                
                if old_file.exists():
                    if i == self.max_files - 1:
                        old_file.unlink()  # 가장 오래된 파일 삭제
                    else:
                        shutil.move(str(old_file), str(new_file))
            
            # 현재 파일을 .1로 이동
            shutil.move(str(log_file), str(log_file.with_suffix('.1.log')))
            
            # 새 파일 생성
            log_file.touch()
            
            logger.info(f"로그 파일 로테이션 완료: {log_file}")
            
        except Exception as e:
            logger.error(f"로그 파일 로테이션 오류: {e}")
    
    def search_logs(self, query: str = None, level: LogLevel = None, 
                   source: LogSource = None, service: str = None,
                   start_time: datetime = None, end_time: datetime = None,
                   limit: int = 1000) -> List[LogEntry]:
        """로그 검색"""
        logs = list(self.log_entries)
        
        # 필터링
        if query:
            logs = [log for log in logs if query.lower() in log.message.lower()]
        
        if level:
            logs = [log for log in logs if log.level == level]
        
        if source:
            logs = [log for log in logs if log.source == source]
        
        if service:
            logs = [log for log in logs if log.service == service]
        
        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]
        
        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]
        
        # 정렬 및 제한
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
    
    def analyze_logs(self, start_time: datetime, end_time: datetime) -> LogAnalysis:
        """로그 분석"""
        # 분석할 로그 필터링
        logs = [log for log in self.log_entries 
                if start_time <= log.timestamp <= end_time]
        
        # 기본 통계
        total_logs = len(logs)
        error_count = len([log for log in logs if log.level == LogLevel.ERROR])
        warning_count = len([log for log in logs if log.level == LogLevel.WARNING])
        critical_count = len([log for log in logs if log.level == LogLevel.CRITICAL])
        
        # 상위 에러
        error_messages = {}
        for log in logs:
            if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                error_messages[log.message] = error_messages.get(log.message, 0) + 1
        
        top_errors = sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 상위 서비스
        service_counts = {}
        for log in logs:
            service_counts[log.service] = service_counts.get(log.service, 0) + 1
        
        top_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 성능 메트릭
        response_times = [log.duration for log in logs if log.duration is not None]
        performance_metrics = {
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'min_response_time': min(response_times) if response_times else 0,
            'total_requests': len(response_times)
        }
        
        # 보안 이벤트
        security_events = []
        for log in logs:
            if log.source == LogSource.SECURITY:
                security_events.append({
                    'timestamp': log.timestamp.isoformat(),
                    'message': log.message,
                    'level': log.level.value,
                    'user_id': log.user_id,
                    'ip_address': log.ip_address
                })
        
        # 분석 결과 생성
        analysis = LogAnalysis(
            id=f"analysis_{int(time.time() * 1000)}",
            analysis_type="comprehensive",
            start_time=start_time,
            end_time=end_time,
            total_logs=total_logs,
            error_count=error_count,
            warning_count=warning_count,
            critical_count=critical_count,
            top_errors=[{'message': msg, 'count': count} for msg, count in top_errors],
            top_services=[{'service': svc, 'count': count} for svc, count in top_services],
            performance_metrics=performance_metrics,
            security_events=security_events
        )
        
        self.log_analyses.append(analysis)
        
        return analysis
    
    def get_log_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """로그 통계 조회"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = [log for log in self.log_entries if log.timestamp >= cutoff_time]
        
        # 레벨별 통계
        level_stats = {}
        for level in LogLevel:
            level_stats[level.value] = len([log for log in recent_logs if log.level == level])
        
        # 소스별 통계
        source_stats = {}
        for source in LogSource:
            source_stats[source.value] = len([log for log in recent_logs if log.source == source])
        
        # 서비스별 통계
        service_stats = {}
        for log in recent_logs:
            service_stats[log.service] = service_stats.get(log.service, 0) + 1
        
        # 시간별 통계
        hourly_stats = {}
        for log in recent_logs:
            hour = log.timestamp.hour
            hourly_stats[hour] = hourly_stats.get(hour, 0) + 1
        
        return {
            'total_logs': len(recent_logs),
            'level_stats': level_stats,
            'source_stats': source_stats,
            'service_stats': dict(sorted(service_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
            'hourly_stats': hourly_stats,
            'time_range': {
                'start': cutoff_time.isoformat(),
                'end': datetime.now().isoformat()
            }
        }
    
    def archive_old_logs(self, days: int = 30):
        """오래된 로그 아카이브"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # 아카이브할 로그 필터링
            logs_to_archive = [log for log in self.log_entries if log.timestamp < cutoff_time]
            
            if not logs_to_archive:
                return
            
            # 아카이브 파일 생성
            archive_file = self.archive_directory / f"logs_{datetime.now().strftime('%Y%m%d')}.json.gz"
            
            with gzip.open(archive_file, 'wt', encoding='utf-8') as f:
                for log in logs_to_archive:
                    f.write(json.dumps(asdict(log), default=str, ensure_ascii=False) + '\n')
            
            # 아카이브된 로그 제거
            self.log_entries = deque([log for log in self.log_entries if log.timestamp >= cutoff_time])
            
            logger.info(f"로그 아카이브 완료: {len(logs_to_archive)}개 로그")
            
        except Exception as e:
            logger.error(f"로그 아카이브 오류: {e}")
    
    def add_log_callback(self, callback: Callable):
        """로그 콜백 함수 추가"""
        self.log_callbacks.append(callback)
    
    def remove_log_callback(self, callback: Callable):
        """로그 콜백 함수 제거"""
        if callback in self.log_callbacks:
            self.log_callbacks.remove(callback)
    
    def get_service_status(self) -> Dict[str, Any]:
        """서비스 상태 조회"""
        return {
            'total_logs': len(self.log_entries),
            'log_patterns': len(self.log_patterns),
            'log_analyses': len(self.log_analyses),
            'log_files': len(self.log_files),
            'archive_directory': str(self.archive_directory),
            'max_file_size': self.max_file_size,
            'retention_days': self.retention_days
        }

# 전역 인스턴스
log_management_service = LogManagementService()
