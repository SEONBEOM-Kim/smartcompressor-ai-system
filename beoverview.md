Backend Services Overview
Relevant source files
Purpose and Scope
This document describes the dual-backend architecture of the Signalcraft system, where Node.js (Express) and Python (Flask) applications run concurrently to serve different system responsibilities. This page covers the architectural pattern, service boundaries, port configuration, and coordination mechanisms between the two backends.

For details on how these backends are deployed and managed, see Infrastructure & Deployment. For information on specific route implementations and business logic, see Node.js Express Server and Flask Python Server.

Architectural Pattern: Dual-Backend Design
The system employs a parallel backend architecture where two independent application servers operate simultaneously on the same EC2 instance. This design allows the system to leverage the strengths of both ecosystems: Node.js for its asynchronous I/O and JavaScript ecosystem, and Python for its AI/ML libraries and data processing capabilities.

Backend Architecture Diagram














Sources: 
app.py
1-184
 
server/app.js
1-118
 Diagram 1 from system architecture

Node.js Express Backend
The Express backend is the primary entry point for user-facing operations, authentication, and real-time communication.

Application Structure
The Express application is structured in server/app.js with modular route imports:

Component	File Path	Purpose
Main Application	server/app.js	Express app configuration and middleware setup
Authentication Routes	server/routes/authRoutes.js	User login, registration, session management
AI Routes	server/routes/aiRoutes.js	AI analysis request proxying
Admin Routes	server/routes/adminRoutes.js	Administrative operations
Kakao Routes	server/routes/kakaoRoutes.js	Kakao OAuth integration
Monitoring Routes	server/routes/monitoringRoutes.js	System monitoring endpoints
Notification Routes	server/routes/notificationRoutes.js	Real-time notification streaming
Sources: 
server/app.js
1-118

Express Application Initialization











Sources: 
server/app.js
1-44

Express Middleware Stack
The Express backend configures middleware in the following order 
server/app.js
16-24
:

CORS Middleware - Cross-origin request handling
JSON Body Parser - Parses JSON payloads with 10MB limit
URL-encoded Parser - Handles form submissions with 10MB limit
Cookie Parser - Extracts and parses cookies
Express Route Responsibilities
Route Prefix	Module	Primary Functions
/api/auth	authRoutes	Login, registration, session verification, logout
/api/ai	aiRoutes	AI analysis request handling
/api/kakao	kakaoRoutes	Kakao OAuth flow, token exchange
/api/monitoring	monitoringRoutes	Server health checks, metrics
/api/notifications	notificationRoutes	SSE stream, notification history
/admin	adminRoutes	Administrative dashboard and operations
/	Static handler	Serves showcase.html as landing page
Sources: 
server/app.js
26-43

Express Port Configuration
The Express server listens on port 3000 by default, configured through server.js which imports the Express app from server/app.js. This is the standard port used in all deployment scripts and referenced in health checks.

Sources: 
package.json
10
 
scripts/deploy-ec2-pm2.sh
56-57

Flask Python Backend
The Flask backend specializes in AI/ML operations, IoT sensor data processing, and Python-specific services that require scientific computing libraries.

Application Factory Pattern
Flask uses the application factory pattern in app.py:


















Sources: 
app.py
43-150

Flask Blueprint Architecture
Flask organizes routes using blueprints, registered in create_app() 
app.py
74-101
:

Blueprint	URL Prefix	Module Path	Primary Responsibility
main_bp	/	routes.main_routes	Root endpoints, static pages
auth_bp	/api/auth	routes.auth_routes	Basic authentication
enhanced_auth_bp	/api/auth	routes.enhanced_auth_routes	4-step enhanced registration
ai_bp	/api	routes.ai_routes	AI analysis, model inference
esp32_bp	/api/esp32	routes.esp32_routes	IoT device communication
notification_bp	/api/notifications	routes.notification_routes	Notification dispatch
kakao_notification_bp	Various	routes.kakao_notification_routes	Kakao message integration
kakao_auth_bp	/auth/kakao	routes.kakao_auth_routes	Kakao OAuth
iot_sensor_bp	/api/sensors	routes.iot_sensor_routes	Sensor data endpoints
dashboard_bp	/dashboard	routes.dashboard_routes	Dashboard UI
mobile_app_bp	/mobile_app	routes.mobile_app_routes	Mobile application API
Sources: 
app.py
16-31
 
app.py
74-101

Flask API Compatibility Routes
Flask provides compatibility routes for frontend requests that may target either backend 
app.py
107-130
:

@app.route('/api/auth/login', methods=['POST'])
@app.route('/api/auth/register', methods=['POST'])
@app.route('/api/auth/logout', methods=['POST'])
@app.route('/api/auth/verify', methods=['GET'])
@app.route('/api/lightweight-analyze', methods=['POST'])
These routes delegate to the appropriate blueprint handlers, ensuring requests reach the correct service regardless of which backend receives them.

Sources: 
app.py
107-130

Flask Port Configuration
The Flask application runs on port 8000 by default 
app.py
163
 configured through the PORT environment variable. This port is distinct from the Express port to avoid conflicts.

Sources: 
app.py
163-183

Flask Service Initialization
Flask initializes background services during application startup 
app.py
34-42
:

Service	Import Path	Initialization Call	Purpose
ensemble_ai_service	services.ai_service	Import only	AI model ensemble for predictions
sensor_data_service	services.sensor_data_service	Import only	Sensor data processing
realtime_streaming_service	services.realtime_streaming_service	Import only	Real-time data streaming
sensor_monitoring_service	services.sensor_monitoring_service	start_monitoring()	Continuous sensor monitoring loop
firmware_ota_service	services.firmware_ota_service	Import only	Firmware over-the-air updates
Sources: 
app.py
34-42
 
app.py
104

Backend Coordination and Responsibilities
Service Responsibility Matrix
The following table defines which backend handles specific functional areas:

Functional Area	Primary Backend	Rationale
User authentication (login/register)	Both (Node.js primary)	Node.js handles initial auth, Flask provides enhanced registration
Session management	Node.js	Express middleware and cookie handling
Kakao OAuth	Both	Redundant implementation for reliability
AI audio analysis	Flask	Python ML libraries (librosa, sklearn)
ESP32 sensor data	Flask	Python data processing capabilities
Real-time notifications (SSE)	Node.js	Express streaming response handling
Kakao notifications	Flask	Python Kakao SDK integration
Dashboard rendering	Flask	Template rendering via Jinja2
Static file serving	Node.js	Express static middleware
Admin operations	Both	Node.js for UI, Flask for Python-specific tasks
Sources: 
app.py
1-184
 
server/app.js
1-118

Data Sharing via SQLite
Both backends access the same SQLite database file, enabling data consistency:







Sources: 
app.py
52-53
 Diagram 3 from system architecture

Both backends use the same database initialization function init_db() from models.database, ensuring schema consistency. For detailed schema information, see Data Storage & Models.

Routing Strategy and URL Patterns
Nginx Reverse Proxy Configuration
Nginx routes requests to the appropriate backend based on URL patterns. The general pattern is:

URL Pattern	Target Backend	Target Port
/api/auth/*	Node.js	3000
/api/ai/*	Node.js	3000
/api/kakao/*	Node.js	3000
/api/monitoring/*	Node.js	3000
/api/notifications/*	Node.js	3000
/api/lightweight-analyze	Flask	8000
/api/esp32/*	Flask	8000
/dashboard	Flask	8000
/mobile_app	Flask	8000
/admin	Node.js	3000
/* (default)	Node.js	3000
Sources: Diagram 1 from system architecture, 
app.py
127-130

Request Flow Diagram
Sources: 
server/app.js
32-37
 
app.py
127-130

Process Management and Lifecycle
PM2 Configuration
Both backends are managed by PM2 through ecosystem.config.js. The Node.js backend is explicitly configured in the PM2 ecosystem file, while the Flask backend is started separately but still monitored by PM2.

Deployment Process:

PM2 deletes all existing processes 
scripts/deploy-ec2-pm2.sh
37-40
All Node.js and Python processes are killed forcefully
PM2 starts the Node.js server using the ecosystem configuration
Flask is started either manually or through a separate PM2 process definition
Sources: 
scripts/deploy-ec2-pm2.sh
37-62
 
scripts/deploy-ec2-pm2.ps1
42-68

Health Check Endpoints
Both backends expose health check endpoints for deployment verification:

Node.js Health Check:

GET http://localhost:3000/api/auth/verify
This endpoint is called during deployment to verify the Express server is responding 
scripts/deploy-ec2-pm2.sh
56-57

Flask Health Check: The Flask backend can be verified through any of its registered routes, though no specific health check endpoint is defined in the provided code.

Sources: 
scripts/deploy-ec2-pm2.sh
56-57
 
scripts/deploy-ec2-pm2.ps1
62

CORS Configuration
Express CORS Setup
Express uses a dedicated CORS middleware module 
server/app.js
3
 that configures cross-origin access for the web application.

Sources: 
server/app.js
17

Flask CORS Setup
Flask uses the flask_cors library with explicit origin whitelisting 
app.py
57-61
:

CORS(app,
     origins=['https://signalcraft.kr', 'https://www.signalcraft.kr'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)
Flask also implements a @app.before_request handler for OPTIONS preflight requests 
app.py
64-72
 ensuring proper CORS negotiation.

Sources: 
app.py
57-72

Enhanced Authentication System
The Flask backend provides an enhanced registration system through enhanced_auth_routes.py that captures additional business context during user registration 
routes/enhanced_auth_routes.py
1-325

Enhanced Registration Flow







Sources: 
routes/enhanced_auth_routes.py
21-124

Enhanced Registration Data Structure
The enhanced registration captures the following additional fields beyond basic authentication:

Category	Fields
Business Context	company, position, industry, company_size, company_email, address
Requirements	purpose (array), budget, timeline, device_count
Notification Preferences	email_alerts, email_newsletter, sms_alerts, kakao_alerts
Legal Agreements	privacy_agree, terms_agree, marketing_agree
Sources: 
routes/enhanced_auth_routes.py
60-82

Real-Time Communication Architecture
Server-Sent Events (SSE) in Express
The Express backend provides Server-Sent Events for real-time notifications through notificationRoutes.js 
server/routes/notificationRoutes.js
1-120
:









Sources: 
server/routes/notificationRoutes.js
5-31

The SSE implementation includes:

Initial connection confirmation message
30-second heartbeat to maintain connection 
server/routes/notificationRoutes.js
19-21
Cleanup on client disconnect 
server/routes/notificationRoutes.js
24-27
Error Handling Strategy
Express Error Middleware
Express implements a centralized error handler that catches connection errors and server errors 
server/app.js
98-115
:

502 Bad Gateway: Detects ECONNREFUSED and ETIMEDOUT errors
500 Internal Server Error: Generic fallback with conditional error details in development mode
Flask Error Handling
Flask does not implement a global error handler in app.py. Error handling is delegated to individual route handlers within each blueprint.

Sources: 
server/app.js
98-115

Deployment Coordination
Both backends are deployed simultaneously through the CI/CD pipeline. The deployment process in deploy-ec2-pm2.sh performs the following steps for both services:

Code Update: git pull origin main
Dependency Installation: npm install (Node.js dependencies)
Process Cleanup: Kill all existing Node.js and Python processes
Service Start: PM2 starts the ecosystem configuration
Health Verification: Curl test against Express endpoints
The Flask application dependencies (Python packages) are managed separately and assumed to be pre-installed or installed through a separate step not shown in the provided deployment scripts.

Sources: 
scripts/deploy-ec2-pm2.sh
19-63

Summary
The dual-backend architecture provides:

Technology-appropriate service distribution: Node.js handles I/O-intensive operations (authentication, real-time streaming), while Flask handles CPU-intensive operations (AI inference, data processing)
Redundant authentication paths: Both backends can handle authentication, providing fallback capability
Shared data consistency: SQLite provides a single source of truth for user and session data
Independent scalability: Each backend can be scaled or restarted independently
Clear service boundaries: Routing rules enforce separation of concerns
This architecture enables the system to leverage the best features of both JavaScript and Python ecosystems while maintaining operational simplicity through shared infrastructure and data storage.

Sources: 
app.py
1-184
 
server/app.js
1-118
 
package.json
1-50
 all deployment scripts


 ## 🤖 AI 계획 수립을 위한 데이터베이스 현황 보고서
1. 개요 (Overview)
프로젝트명: SignalCraft AI System

목적: AI 기반 산업용 컴프레서 모니터링 플랫폼의 백엔드 데이터베이스

데이터베이스 종류: PostgreSQL, AWS의 완전 관리형 서비스인 RDS를 통해 운영

2. 인프라 및 위치 (Infrastructure & Location)
클라우드 서비스: Amazon RDS (Relational Database Service)

물리적 위치 (Region): 아시아 태평양 (서울) ap-northeast-2

컨텍스트: 초기 설정은 미국 동부(us-east-1)였으나, 한국 내 사용자 경험 및 개발 속도 향상을 위해 서울 리전으로 이전을 완료함.

인스턴스 사양:

클래스: db.t4g.micro (2 vCPUs, 1 GiB RAM)

스토리지: 20 GB 범용 SSD (gp2)

구성: 단일 AZ (Single-AZ) 배포

컨텍스트: 현재 AWS 프리 티어(무료 사용량) 범위 내에서 운영 중인 개발 및 초기 운영 단계의 사양임.

3. 네트워크 및 연결 정보 (Network & Connection Details)
엔드포인트 (Endpoint): signalcraft.cb8e6ea8w70p.ap-northeast-2.rds.amazonaws.com

포트 (Port): 5432

데이터베이스 이름 (DB Name): signalcraft

연결 주체: 서울 리전의 EC2 인스턴스 (i-04f841e538f31fdf9) 와 연결되도록 설정됨.

4. 보안 설정 (Security Configuration)
퍼블릭 액세스: 아니요 (Disabled)

컨텍스트: 데이터베이스는 외부 인터넷에 직접 노출되어 있지 않으며, 오직 지정된 내부 네트워크(VPC)에서만 접근 가능하여 보안 수준이 높음.

방화벽 (Security Group):

데이터베이스(RDS) 전용 보안 그룹이 설정되어 있음.

이 보안 그룹의 인바운드 규칙은 오직 연결된 EC2 인스턴스의 보안 그룹으로부터 오는 PostgreSQL(5432 포트) 트래픽만 허용함.

컨텍스트: IP 주소 기반이 아닌, 보안 그룹 ID 기반으로 규칙이 설정되어 있어 EC2 인스턴스의 IP가 변경되어도 연결이 유지되는 유연하고 안전한 방식임.

5. 현재 상태 및 컨텍스트 (Current Status & Context)
마이그레이션: 로컬 환경의 SQLite에서 PostgreSQL로 전환을 완료함.

데이터 상태: 현재 비어있는 상태. 미국 리전의 이전 데이터는 옮기지 않았으며, 애플리케이션의 초기화 코드(database_service.js)가 처음 연결될 때 필요한 테이블 스키마를 자동으로 생성하도록 설계되어 있음.

운영 상태: 인스턴스는 '사용 가능(Available)' 또는 '백업 중(Backing up)' 상태로, 정상적으로 실행 중임.