#!/usr/bin/env python3
"""
자동 리포트 생성 서비스
매장 운영 데이터 분석 리포트 자동 생성 및 이메일 발송
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import schedule
import time
import threading
from jinja2 import Template
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import base64
from io import BytesIO

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportType(Enum):
    """리포트 타입"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"

class ReportFormat(Enum):
    """리포트 형식"""
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"

@dataclass
class ReportConfig:
    """리포트 설정"""
    report_id: str
    report_name: str
    report_type: ReportType
    store_ids: List[str]
    metrics: List[str]
    recipients: List[str]
    schedule: str  # cron expression
    format: ReportFormat
    is_active: bool = True

@dataclass
class ReportData:
    """리포트 데이터"""
    report_id: str
    generated_at: datetime
    data: Dict[str, Any]
    charts: List[Dict]
    insights: List[str]
    recommendations: List[str]

class AutomatedReportingService:
    """자동 리포트 생성 서비스"""
    
    def __init__(self, db_path: str = "data/analytics.db"):
        self.db_path = db_path
        self.conn = None
        self.report_configs = {}
        self.is_running = False
        self.scheduler_thread = None
        
        # 이메일 설정
        self.smtp_config = {
            'server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('SMTP_USERNAME'),
            'password': os.getenv('SMTP_PASSWORD')
        }
        
        # 리포트 템플릿 디렉토리
        self.template_dir = "templates/reports"
        os.makedirs(self.template_dir, exist_ok=True)
        
        # 리포트 저장 디렉토리
        self.report_dir = "data/reports"
        os.makedirs(self.report_dir, exist_ok=True)
        
        # 초기화
        self._init_database()
        self._load_report_configs()
        self._create_default_templates()
        
        logger.info("자동 리포트 생성 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # 리포트 설정 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT UNIQUE NOT NULL,
                    report_name TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    store_ids TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    recipients TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    format TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 리포트 생성 이력 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT NOT NULL,
                    generated_at DATETIME NOT NULL,
                    status TEXT NOT NULL,
                    file_path TEXT,
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("리포트 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_report_configs(self):
        """리포트 설정 로드"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT * FROM report_configs WHERE is_active = TRUE
            ''')
            
            for row in cursor.fetchall():
                config = ReportConfig(
                    report_id=row[1],
                    report_name=row[2],
                    report_type=ReportType(row[3]),
                    store_ids=json.loads(row[4]),
                    metrics=json.loads(row[5]),
                    recipients=json.loads(row[6]),
                    schedule=row[7],
                    format=ReportFormat(row[8]),
                    is_active=bool(row[9])
                )
                
                self.report_configs[config.report_id] = config
            
            logger.info(f"리포트 설정 로드 완료: {len(self.report_configs)}개")
            
        except Exception as e:
            logger.error(f"리포트 설정 로드 오류: {e}")
    
    def _create_default_templates(self):
        """기본 리포트 템플릿 생성"""
        try:
            # 일일 리포트 템플릿
            daily_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ report_name }} - {{ date }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; text-align: center; }
        .summary { background: #ecf0f1; padding: 20px; margin: 20px 0; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: white; border-radius: 5px; }
        .chart { margin: 20px 0; text-align: center; }
        .insights { background: #e8f5e8; padding: 15px; margin: 20px 0; }
        .recommendations { background: #fff3cd; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report_name }}</h1>
        <p>생성일: {{ date }}</p>
    </div>
    
    <div class="summary">
        <h2>요약</h2>
        {% for metric in summary_metrics %}
        <div class="metric">
            <h3>{{ metric.name }}</h3>
            <p>{{ metric.value }}</p>
        </div>
        {% endfor %}
    </div>
    
    <div class="chart">
        <h3>매출 트렌드</h3>
        <img src="data:image/png;base64,{{ revenue_chart }}" alt="매출 트렌드">
    </div>
    
    <div class="insights">
        <h3>주요 인사이트</h3>
        <ul>
            {% for insight in insights %}
            <li>{{ insight }}</li>
            {% endfor %}
        </ul>
    </div>
    
    <div class="recommendations">
        <h3>권장사항</h3>
        <ul>
            {% for recommendation in recommendations %}
            <li>{{ recommendation }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
            '''
            
            with open(f"{self.template_dir}/daily_report.html", 'w', encoding='utf-8') as f:
                f.write(daily_template)
            
            # 주간 리포트 템플릿
            weekly_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ report_name }} - {{ week_range }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #34495e; color: white; padding: 20px; text-align: center; }
        .summary { background: #ecf0f1; padding: 20px; margin: 20px 0; }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: white; border-radius: 5px; }
        .chart { margin: 20px 0; text-align: center; }
        .comparison { background: #f8f9fa; padding: 15px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report_name }}</h1>
        <p>기간: {{ week_range }}</p>
    </div>
    
    <div class="summary">
        <h2>주간 요약</h2>
        {% for metric in summary_metrics %}
        <div class="metric">
            <h3>{{ metric.name }}</h3>
            <p>{{ metric.value }}</p>
            <small>{{ metric.change }}</small>
        </div>
        {% endfor %}
    </div>
    
    <div class="chart">
        <h3>주간 매출 비교</h3>
        <img src="data:image/png;base64,{{ weekly_chart }}" alt="주간 매출 비교">
    </div>
    
    <div class="comparison">
        <h3>전주 대비 변화</h3>
        <ul>
            {% for change in changes %}
            <li>{{ change }}</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
            '''
            
            with open(f"{self.template_dir}/weekly_report.html", 'w', encoding='utf-8') as f:
                f.write(weekly_template)
            
            logger.info("기본 리포트 템플릿 생성 완료")
            
        except Exception as e:
            logger.error(f"기본 템플릿 생성 오류: {e}")
    
    def create_report_config(self, config: ReportConfig) -> bool:
        """리포트 설정 생성"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO report_configs 
                (report_id, report_name, report_type, store_ids, metrics, 
                 recipients, schedule, format, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                config.report_id,
                config.report_name,
                config.report_type.value,
                json.dumps(config.store_ids),
                json.dumps(config.metrics),
                json.dumps(config.recipients),
                config.schedule,
                config.format.value,
                config.is_active
            ))
            
            self.conn.commit()
            
            # 메모리에 추가
            self.report_configs[config.report_id] = config
            
            logger.info(f"리포트 설정 생성 완료: {config.report_id}")
            return True
            
        except Exception as e:
            logger.error(f"리포트 설정 생성 오류: {e}")
            return False
    
    def generate_report(self, report_id: str) -> Optional[ReportData]:
        """리포트 생성"""
        try:
            config = self.report_configs.get(report_id)
            if not config:
                logger.error(f"리포트 설정을 찾을 수 없습니다: {report_id}")
                return None
            
            # 데이터 수집
            data = self._collect_report_data(config)
            
            # 차트 생성
            charts = self._generate_charts(data, config)
            
            # 인사이트 생성
            insights = self._generate_insights(data, config)
            
            # 권장사항 생성
            recommendations = self._generate_recommendations(data, config)
            
            # 리포트 데이터 생성
            report_data = ReportData(
                report_id=report_id,
                generated_at=datetime.now(),
                data=data,
                charts=charts,
                insights=insights,
                recommendations=recommendations
            )
            
            # 리포트 파일 생성
            file_path = self._create_report_file(report_data, config)
            
            # 이메일 발송
            if config.recipients:
                self._send_report_email(report_data, config, file_path)
            
            # 이력 저장
            self._save_report_history(report_id, 'success', file_path)
            
            logger.info(f"리포트 생성 완료: {report_id}")
            return report_data
            
        except Exception as e:
            logger.error(f"리포트 생성 오류: {e}")
            self._save_report_history(report_id, 'error', None, str(e))
            return None
    
    def _collect_report_data(self, config: ReportConfig) -> Dict[str, Any]:
        """리포트 데이터 수집"""
        try:
            data = {}
            
            for store_id in config.store_ids:
                # 매장별 데이터 조회
                query = '''
                    SELECT * FROM store_metrics 
                    WHERE store_id = ? AND timestamp >= ?
                    ORDER BY timestamp DESC
                '''
                
                # 기간 설정
                if config.report_type == ReportType.DAILY:
                    start_date = datetime.now() - timedelta(days=1)
                elif config.report_type == ReportType.WEEKLY:
                    start_date = datetime.now() - timedelta(days=7)
                elif config.report_type == ReportType.MONTHLY:
                    start_date = datetime.now() - timedelta(days=30)
                else:
                    start_date = datetime.now() - timedelta(days=7)
                
                df = pd.read_sql_query(query, self.conn, params=(store_id, start_date))
                
                if not df.empty:
                    store_data = {
                        'total_revenue': df['revenue'].sum(),
                        'avg_power_consumption': df['power_consumption'].mean(),
                        'avg_efficiency': df['compressor_efficiency'].mean(),
                        'total_customers': df['customer_count'].sum(),
                        'total_orders': df['order_count'].sum(),
                        'revenue_trend': df['revenue'].pct_change().mean(),
                        'hourly_revenue': df.groupby(df['timestamp'].dt.hour)['revenue'].sum().to_dict()
                    }
                    
                    data[store_id] = store_data
            
            return data
            
        except Exception as e:
            logger.error(f"데이터 수집 오류: {e}")
            return {}
    
    def _generate_charts(self, data: Dict[str, Any], config: ReportConfig) -> List[Dict]:
        """차트 생성"""
        try:
            charts = []
            
            # 매출 트렌드 차트
            if data:
                store_id = list(data.keys())[0]
                hourly_revenue = data[store_id].get('hourly_revenue', {})
                
                if hourly_revenue:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=list(hourly_revenue.keys()),
                        y=list(hourly_revenue.values()),
                        mode='lines+markers',
                        name='매출'
                    ))
                    
                    fig.update_layout(
                        title='시간별 매출 트렌드',
                        xaxis_title='시간',
                        yaxis_title='매출 (원)'
                    )
                    
                    # 차트를 base64로 인코딩
                    chart_html = fig.to_html(include_plotlyjs=False)
                    chart_base64 = base64.b64encode(chart_html.encode()).decode()
                    
                    charts.append({
                        'type': 'revenue_trend',
                        'title': '매출 트렌드',
                        'data': chart_base64
                    })
            
            return charts
            
        except Exception as e:
            logger.error(f"차트 생성 오류: {e}")
            return []
    
    def _generate_insights(self, data: Dict[str, Any], config: ReportConfig) -> List[str]:
        """인사이트 생성"""
        try:
            insights = []
            
            if not data:
                return insights
            
            # 전체 매출 분석
            total_revenue = sum(store_data.get('total_revenue', 0) for store_data in data.values())
            if total_revenue > 0:
                insights.append(f"총 매출: {total_revenue:,.0f}원")
            
            # 효율성 분석
            avg_efficiency = np.mean([store_data.get('avg_efficiency', 0) for store_data in data.values()])
            if avg_efficiency > 0.9:
                insights.append("압축기 효율성이 매우 우수합니다.")
            elif avg_efficiency < 0.7:
                insights.append("압축기 효율성 개선이 필요합니다.")
            
            # 고객 수 분석
            total_customers = sum(store_data.get('total_customers', 0) for store_data in data.values())
            if total_customers > 100:
                insights.append("고객 유입이 활발합니다.")
            elif total_customers < 20:
                insights.append("고객 유입이 저조합니다.")
            
            return insights
            
        except Exception as e:
            logger.error(f"인사이트 생성 오류: {e}")
            return []
    
    def _generate_recommendations(self, data: Dict[str, Any], config: ReportConfig) -> List[str]:
        """권장사항 생성"""
        try:
            recommendations = []
            
            if not data:
                return recommendations
            
            # 효율성 기반 권장사항
            avg_efficiency = np.mean([store_data.get('avg_efficiency', 0) for store_data in data.values()])
            if avg_efficiency < 0.8:
                recommendations.append("압축기 정기 점검을 권장합니다.")
                recommendations.append("온도 설정을 최적화하세요.")
            
            # 전력 사용량 기반 권장사항
            avg_power = np.mean([store_data.get('avg_power_consumption', 0) for store_data in data.values()])
            if avg_power > 1000:  # 임계값
                recommendations.append("피크 시간대 전력 사용량을 줄이세요.")
                recommendations.append("에너지 효율적인 장비 도입을 고려하세요.")
            
            # 고객 수 기반 권장사항
            total_customers = sum(store_data.get('total_customers', 0) for store_data in data.values())
            if total_customers < 50:
                recommendations.append("마케팅 활동을 강화하세요.")
                recommendations.append("고객 만족도 조사를 실시하세요.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"권장사항 생성 오류: {e}")
            return []
    
    def _create_report_file(self, report_data: ReportData, config: ReportConfig) -> str:
        """리포트 파일 생성"""
        try:
            # 파일명 생성
            timestamp = report_data.generated_at.strftime("%Y%m%d_%H%M%S")
            filename = f"{config.report_id}_{timestamp}.{config.format.value}"
            file_path = os.path.join(self.report_dir, filename)
            
            if config.format == ReportFormat.HTML:
                # HTML 리포트 생성
                template_path = f"{self.template_dir}/{config.report_type.value}_report.html"
                
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                template = Template(template_content)
                
                # 템플릿 변수 설정
                context = {
                    'report_name': config.report_name,
                    'date': report_data.generated_at.strftime("%Y-%m-%d %H:%M"),
                    'summary_metrics': self._format_summary_metrics(report_data.data),
                    'insights': report_data.insights,
                    'recommendations': report_data.recommendations,
                    'revenue_chart': report_data.charts[0]['data'] if report_data.charts else ''
                }
                
                html_content = template.render(**context)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
            
            elif config.format == ReportFormat.CSV:
                # CSV 리포트 생성
                df = pd.DataFrame(report_data.data).T
                df.to_csv(file_path, encoding='utf-8-sig')
            
            logger.info(f"리포트 파일 생성 완료: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"리포트 파일 생성 오류: {e}")
            return ""
    
    def _format_summary_metrics(self, data: Dict[str, Any]) -> List[Dict]:
        """요약 지표 포맷팅"""
        try:
            metrics = []
            
            if not data:
                return metrics
            
            # 전체 매출
            total_revenue = sum(store_data.get('total_revenue', 0) for store_data in data.values())
            metrics.append({
                'name': '총 매출',
                'value': f"{total_revenue:,.0f}원"
            })
            
            # 평균 효율성
            avg_efficiency = np.mean([store_data.get('avg_efficiency', 0) for store_data in data.values()])
            metrics.append({
                'name': '평균 효율성',
                'value': f"{avg_efficiency:.1%}"
            })
            
            # 총 고객 수
            total_customers = sum(store_data.get('total_customers', 0) for store_data in data.values())
            metrics.append({
                'name': '총 고객 수',
                'value': f"{total_customers:,}명"
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"요약 지표 포맷팅 오류: {e}")
            return []
    
    def _send_report_email(self, report_data: ReportData, config: ReportConfig, file_path: str) -> bool:
        """리포트 이메일 발송"""
        try:
            if not self.smtp_config['username'] or not self.smtp_config['password']:
                logger.warning("이메일 설정이 없습니다. 이메일을 발송하지 않습니다.")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['username']
            msg['To'] = ', '.join(config.recipients)
            msg['Subject'] = f"{config.report_name} - {report_data.generated_at.strftime('%Y-%m-%d')}"
            
            # 이메일 본문
            body = f"""
안녕하세요,

{config.report_name}이 생성되었습니다.

주요 인사이트:
{chr(10).join(f"- {insight}" for insight in report_data.insights)}

권장사항:
{chr(10).join(f"- {rec}" for rec in report_data.recommendations)}

자세한 내용은 첨부 파일을 참고해주세요.

감사합니다.
SmartCompressor AI 시스템
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 첨부 파일
            if file_path and os.path.exists(file_path):
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(file_path)}'
                    )
                    msg.attach(part)
            
            # 이메일 발송
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            logger.info(f"리포트 이메일 발송 완료: {config.recipients}")
            return True
            
        except Exception as e:
            logger.error(f"리포트 이메일 발송 오류: {e}")
            return False
    
    def _save_report_history(self, report_id: str, status: str, file_path: str = None, error_message: str = None) -> bool:
        """리포트 생성 이력 저장"""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO report_history 
                (report_id, generated_at, status, file_path, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (report_id, datetime.now(), status, file_path, error_message))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"리포트 이력 저장 오류: {e}")
            return False
    
    def start_scheduler(self):
        """스케줄러 시작"""
        try:
            if self.is_running:
                logger.warning("스케줄러가 이미 실행 중입니다.")
                return
            
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("리포트 스케줄러 시작")
            
        except Exception as e:
            logger.error(f"스케줄러 시작 오류: {e}")
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        try:
            self.is_running = False
            if self.scheduler_thread:
                self.scheduler_thread.join()
            
            logger.info("리포트 스케줄러 중지")
            
        except Exception as e:
            logger.error(f"스케줄러 중지 오류: {e}")
    
    def _scheduler_loop(self):
        """스케줄러 루프"""
        while self.is_running:
            try:
                # 현재 시간에 실행해야 할 리포트 확인
                current_time = datetime.now()
                
                for config in self.report_configs.values():
                    if self._should_run_report(config, current_time):
                        logger.info(f"리포트 생성 시작: {config.report_id}")
                        self.generate_report(config.report_id)
                
                time.sleep(60)  # 1분마다 확인
                
            except Exception as e:
                logger.error(f"스케줄러 루프 오류: {e}")
                time.sleep(60)
    
    def _should_run_report(self, config: ReportConfig, current_time: datetime) -> bool:
        """리포트 실행 여부 확인"""
        try:
            # 간단한 스케줄 확인 (실제 구현에서는 cron 파싱 필요)
            if config.schedule == "daily" and current_time.hour == 9:
                return True
            elif config.schedule == "weekly" and current_time.weekday() == 0 and current_time.hour == 9:
                return True
            elif config.schedule == "monthly" and current_time.day == 1 and current_time.hour == 9:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"리포트 실행 여부 확인 오류: {e}")
            return False

# 전역 인스턴스
automated_reporting_service = AutomatedReportingService()
