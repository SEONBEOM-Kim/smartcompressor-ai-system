const express = require('express');
const path = require('path');
const router = express.Router();

router.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../../admin/templates/admin_dashboard.html'));
});

router.get('/old', (req, res) => {
    res.send(`
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>관리자 대시보드 - Smart Compressor AI</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; color: #333;
            }
            .admin-container { max-width: 1400px; margin: 0 auto; padding: 20px; }
            .header {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            .header h1 {
                color: #2c3e50; font-size: 2.5rem; margin-bottom: 10px;
                display: flex; align-items: center; justify-content: center; gap: 15px;
            }
            .header p { color: #7f8c8d; font-size: 1.1rem; }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px; margin-bottom: 30px;
            }
            .stat-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px; padding: 25px; text-align: center;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
            }
            .stat-icon { font-size: 2.5rem; margin-bottom: 15px; color: #3498db; }
            .stat-number { font-size: 2.5rem; font-weight: bold; color: #2c3e50; margin-bottom: 5px; }
            .stat-label { color: #7f8c8d; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }
            .management-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 25px; margin-bottom: 30px;
            }
            .management-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 15px; padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
            }
            .management-card:hover { transform: translateY(-3px); }
            .management-card h3 {
                color: #2c3e50; font-size: 1.5rem; margin-bottom: 15px;
                display: flex; align-items: center; gap: 10px;
            }
            .management-card p { color: #7f8c8d; margin-bottom: 20px; line-height: 1.6; }
            .feature-list { list-style: none; padding: 0; }
            .feature-list li {
                padding: 8px 0; border-bottom: 1px solid #ecf0f1;
                display: flex; align-items: center; gap: 10px;
            }
            .feature-list li:last-child { border-bottom: none; }
            .feature-list li i { color: #27ae60; width: 20px; }
            .nav-buttons {
                display: flex; justify-content: center; gap: 15px;
                margin-top: 30px; flex-wrap: wrap;
            }
            .nav-btn {
                background: linear-gradient(45deg, #3498db, #2980b9);
                color: white; border: none; padding: 12px 25px;
                border-radius: 25px; text-decoration: none; font-weight: 600;
                transition: all 0.3s ease; display: flex; align-items: center; gap: 8px;
            }
            .nav-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
            }
            .status-indicator {
                display: inline-block; width: 12px; height: 12px;
                border-radius: 50%; background: #27ae60;
                margin-right: 8px; animation: pulse 2s infinite;
            }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
            .alert-banner {
                background: linear-gradient(45deg, #e74c3c, #c0392b);
                color: white; padding: 15px; border-radius: 10px;
                margin-bottom: 20px; text-align: center; font-weight: 600;
            }
            @media (max-width: 768px) {
                .admin-container { padding: 10px; }
                .header h1 { font-size: 2rem; }
                .stats-grid { grid-template-columns: 1fr; }
                .management-grid { grid-template-columns: 1fr; }
                .nav-buttons { flex-direction: column; align-items: center; }
            }
        </style>
    </head>
    <body>
        <div class="admin-container">
            <div class="header">
                <h1><i class="fas fa-shield-alt"></i> 관리자 대시보드</h1>
                <p>Smart Compressor AI System - 통합 관리 시스템</p>
                <div style="margin-top: 15px;">
                    <span class="status-indicator"></span>
                    <span>시스템 정상 작동 중</span>
                </div>
            </div>
            
            <div class="alert-banner">
                <i class="fas fa-exclamation-triangle"></i>
                긴급 알림: 3개의 매장에서 이상 신호가 감지되었습니다.
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-store"></i></div>
                    <div class="stat-number">12</div>
                    <div class="stat-label">활성 매장</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-chart-line"></i></div>
                    <div class="stat-number">156</div>
                    <div class="stat-label">총 진단 수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-percentage"></i></div>
                    <div class="stat-number">98.5%</div>
                    <div class="stat-label">시스템 가동률</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-exclamation-circle"></i></div>
                    <div class="stat-number">3</div>
                    <div class="stat-label">긴급 알림</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-users"></i></div>
                    <div class="stat-number">45</div>
                    <div class="stat-label">등록 사용자</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-dollar-sign"></i></div>
                    <div class="stat-number">₩2.4M</div>
                    <div class="stat-label">월 매출</div>
                </div>
            </div>
            
            <div class="management-grid">
                <div class="management-card">
                    <h3><i class="fas fa-store"></i> 매장 관리</h3>
                    <p>매장 등록, 승인, 설정 및 모니터링을 관리합니다.</p>
                    <ul class="feature-list">
                        <li><i class="fas fa-check"></i> 매장 등록 및 승인</li>
                        <li><i class="fas fa-check"></i> 실시간 상태 모니터링</li>
                        <li><i class="fas fa-check"></i> 설정 관리</li>
                        <li><i class="fas fa-check"></i> 성능 분석</li>
                    </ul>
                </div>
                
                <div class="management-card">
                    <h3><i class="fas fa-users"></i> 사용자 관리</h3>
                    <p>사용자 권한, 역할, 접근 제어를 관리합니다.</p>
                    <ul class="feature-list">
                        <li><i class="fas fa-check"></i> 사용자 등록 및 승인</li>
                        <li><i class="fas fa-check"></i> 역할 기반 접근 제어</li>
                        <li><i class="fas fa-check"></i> 권한 관리</li>
                        <li><i class="fas fa-check"></i> 감사 로그</li>
                    </ul>
                </div>
                
                <div class="management-card">
                    <h3><i class="fas fa-shield-alt"></i> 보안 관리</h3>
                    <p>보안 모니터링, 침입 탐지, 감사 로그를 관리합니다.</p>
                    <ul class="feature-list">
                        <li><i class="fas fa-check"></i> 실시간 보안 모니터링</li>
                        <li><i class="fas fa-check"></i> 침입 탐지 시스템</li>
                        <li><i class="fas fa-check"></i> 암호화 관리</li>
                        <li><i class="fas fa-check"></i> 보안 정책</li>
                    </ul>
                </div>
                
                <div class="management-card">
                    <h3><i class="fas fa-chart-bar"></i> 분석 및 보고서</h3>
                    <p>시스템 성능, 사용량, 비용 분석을 제공합니다.</p>
                    <ul class="feature-list">
                        <li><i class="fas fa-check"></i> 실시간 성능 지표</li>
                        <li><i class="fas fa-check"></i> 사용량 분석</li>
                        <li><i class="fas fa-check"></i> 비용 절약 분석</li>
                        <li><i class="fas fa-check"></i> 자동 보고서</li>
                    </ul>
                </div>
                
                <div class="management-card">
                    <h3><i class="fas fa-cog"></i> 시스템 설정</h3>
                    <p>시스템 전반의 설정과 구성을 관리합니다.</p>
                    <ul class="feature-list">
                        <li><i class="fas fa-check"></i> AI 모델 설정</li>
                        <li><i class="fas fa-check"></i> 알림 설정</li>
                        <li><i class="fas fa-check"></i> 백업 설정</li>
                        <li><i class="fas fa-check"></i> 통합 설정</li>
                    </ul>
                </div>
                
                <div class="management-card">
                    <h3><i class="fas fa-headset"></i> 고객 지원</h3>
                    <p>고객 지원 티켓과 문의를 관리합니다.</p>
                    <ul class="feature-list">
                        <li><i class="fas fa-check"></i> 티켓 관리</li>
                        <li><i class="fas fa-check"></i> 실시간 채팅</li>
                        <li><i class="fas fa-check"></i> FAQ 관리</li>
                        <li><i class="fas fa-check"></i> 지원 통계</li>
                    </ul>
                </div>
            </div>
            
            <div class="nav-buttons">
                <a href="/" class="nav-btn"><i class="fas fa-home"></i> 홈으로</a>
                <a href="/api/monitoring/status" class="nav-btn"><i class="fas fa-chart-line"></i> 모니터링</a>
                <a href="/api/auth/verify" class="nav-btn"><i class="fas fa-key"></i> 인증 상태</a>
                <a href="/mobile_app" class="nav-btn"><i class="fas fa-mobile-alt"></i> 모바일 앱</a>
            </div>
        </div>
        
        <script>
            function updateStats() { console.log('통계 데이터 업데이트 중...'); }
            setInterval(updateStats, 5000);
            document.addEventListener('DOMContentLoaded', function() {
                console.log('관리자 대시보드가 로드되었습니다.');
                updateStats();
            });
        </script>
    </body>
    </html>
    `);
});

module.exports = router;
