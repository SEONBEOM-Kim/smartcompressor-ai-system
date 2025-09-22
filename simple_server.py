#!/usr/bin/env python3
"""
간단한 테스트 서버
"""

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    """홈페이지"""
    return jsonify({
        "message": "🚀 Smart Compressor AI System",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "AI 진단 시스템",
            "IoT 센서 모니터링", 
            "실시간 알림",
            "대시보드",
            "모바일 앱",
            "보안 시스템"
        ]
    })

@app.route('/health')
def health():
    """헬스 체크"""
    return jsonify({"status": "healthy", "message": "서버가 정상적으로 실행 중입니다."})

@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Compressor AI System</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
            .feature-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 30px; }
            .feature-card { background: #ecf0f1; padding: 20px; border-radius: 8px; border-left: 4px solid #3498db; }
            .feature-card h3 { color: #2c3e50; margin-top: 0; }
            .status { background: #27ae60; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }
            .nav { text-align: center; margin: 20px 0; }
            .nav a { display: inline-block; margin: 0 10px; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 5px; }
            .nav a:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔧 Smart Compressor AI System</h1>
            <div class="status">
                ✅ 시스템이 정상적으로 실행 중입니다
            </div>
            
            <div class="nav">
                <a href="/">홈</a>
                <a href="/health">헬스 체크</a>
                <a href="/dashboard">대시보드</a>
                <a href="/mobile_app">모바일 앱</a>
                <a href="/admin">관리자</a>
            </div>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>🤖 AI 진단 시스템</h3>
                    <p>머신러닝 기반 압축기 이상 진단 및 예측 유지보수</p>
                </div>
                
                <div class="feature-card">
                    <h3>📡 IoT 센서 모니터링</h3>
                    <p>실시간 센서 데이터 수집 및 분석</p>
                </div>
                
                <div class="feature-card">
                    <h3>🔔 실시간 알림</h3>
                    <p>카카오톡, 이메일, SMS를 통한 즉시 알림</p>
                </div>
                
                <div class="feature-card">
                    <h3>📊 대시보드</h3>
                    <p>실시간 모니터링 및 데이터 시각화</p>
                </div>
                
                <div class="feature-card">
                    <h3>📱 모바일 앱</h3>
                    <p>점주용 모바일 애플리케이션</p>
                </div>
                
                <div class="feature-card">
                    <h3>🔒 보안 시스템</h3>
                    <p>Stripe & AWS 수준의 엔터프라이즈 보안</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/mobile_app')
def mobile_app():
    """모바일 앱 페이지"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>모바일 앱 - Smart Compressor AI</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a1a; color: white; }
            .mobile-container { max-width: 400px; margin: 0 auto; background: #2c2c2c; border-radius: 20px; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; }
            .status-card { background: #27ae60; padding: 15px; border-radius: 10px; margin: 15px 0; text-align: center; }
            .feature-list { list-style: none; padding: 0; }
            .feature-list li { background: #3c3c3c; margin: 10px 0; padding: 15px; border-radius: 10px; }
            .nav-buttons { display: flex; justify-content: space-around; margin-top: 20px; }
            .nav-btn { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 20px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="mobile-container">
            <div class="header">
                <h1>📱 Smart Compressor AI</h1>
                <p>점주용 모바일 앱</p>
            </div>
            
            <div class="status-card">
                ✅ 모든 시스템 정상 작동
            </div>
            
            <ul class="feature-list">
                <li>🏠 대시보드</li>
                <li>🔍 진단 결과</li>
                <li>💳 결제 관리</li>
                <li>🔔 알림 설정</li>
                <li>⚙️ 시스템 설정</li>
            </ul>
            
            <div class="nav-buttons">
                <button class="nav-btn">홈</button>
                <button class="nav-btn">진단</button>
                <button class="nav-btn">결제</button>
                <button class="nav-btn">알림</button>
            </div>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/admin')
def admin():
    """관리자 페이지"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>관리자 대시보드 - Smart Compressor AI</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
            .admin-container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
            .management-section { background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="admin-container">
            <div class="header">
                <h1>🔧 관리자 대시보드</h1>
                <p>Smart Compressor AI System 관리</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">12</div>
                    <div>활성 매장</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">156</div>
                    <div>총 진단 수</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">98.5%</div>
                    <div>시스템 가동률</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">3</div>
                    <div>긴급 알림</div>
                </div>
            </div>
            
            <div class="management-section">
                <h3>🏪 매장 관리</h3>
                <p>매장 등록, 승인, 설정 관리</p>
            </div>
            
            <div class="management-section">
                <h3>👥 사용자 관리</h3>
                <p>사용자 권한, 역할, 접근 제어</p>
            </div>
            
            <div class="management-section">
                <h3>🔒 보안 관리</h3>
                <p>보안 모니터링, 침입 탐지, 감사 로그</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    print("🚀 Smart Compressor AI System 시작 중...")
    print("📍 서버 주소: http://localhost:5000")
    print("🔧 대시보드: http://localhost:5000/dashboard")
    print("📱 모바일 앱: http://localhost:5000/mobile_app")
    print("🔧 관리자: http://localhost:5000/admin")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
