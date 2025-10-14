const express = require('express');
const path = require('path');
const corsMiddleware = require('./middleware/cors');
const cookieParser = require('cookie-parser');
const SQLiteDatabaseService = require('../services/sqlite_database_service');

// 라우트 import
const authRoutes = require('./routes/authRoutes');
const aiRoutes = require('./routes/aiRoutes');
const adminRoutes = require('./routes/adminRoutes');
const kakaoRoutes = require('./routes/kakaoRoutes');
const monitoringRoutes = require('./routes/monitoringRoutes');
const notificationRoutes = require('./routes/notificationRoutes');

const app = express();
const db = new SQLiteDatabaseService();

// 미들웨어 설정
app.use(corsMiddleware);
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(cookieParser());

// 세션 검증 미들웨어 (authRoutes.js에서 가져옴)
const verifySession = async (req, res, next) => {
    try {
        const sessionId = req.cookies.sessionId;
        if (!sessionId) {
            return res.status(401).redirect('/'); // 세션 없으면 홈으로
        }
        const session = await db.getSession(sessionId);
        if (!session) {
            return res.status(401).redirect('/'); // 유효하지 않은 세션이면 홈으로
        }
        req.user = {
            userId: session.user_id,
            username: session.username,
            role: session.role
        };
        next();
    } catch (error) {
        console.error('세션 검증 오류:', error);
        return res.status(500).redirect('/');
    }
};

// 관리자 권한 확인 미들웨어
const ensureAdmin = (req, res, next) => {
    if (req.user && req.user.role === 'admin') {
        return next();
    }
    res.status(403).send('<h1>403 Forbidden</h1><p>접근 권한이 없습니다. 관리자만 접근할 수 있습니다.</p><a href="/">홈으로 돌아가기</a>');
};

// 보호할 직원용 자산 라우트 (정적 파일 서빙보다 먼저 와야 함)
app.get('/static/js/enhanced-registration.js', [verifySession, ensureAdmin], (req, res) => {
    res.sendFile(path.join(__dirname, '../static/js/enhanced-registration.js'));
});


// 정적 파일 서빙
app.use('/static', express.static(path.join(__dirname, '../static')));
app.use(express.static(path.join(__dirname, '../static')));

// 메인 페이지 (쇼윈도 - 로그인 화면)
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/index.html'));
});

// Additional static page routes
app.get('/index', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/index.html'));
});

// [보안 적용] /showcase 경로는 이제 관리자만 접근 가능
app.get('/showcase', [verifySession, ensureAdmin], (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/showcase.html'));
});

app.get('/audio_recorder_client', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/audio_recorder_client.html'));
});

app.get('/terms', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/legal.html'));
});

app.get('/privacy', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/legal.html'));
});

// Labeling-related routes
app.get('/labeling/interface', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/labeling/interface.html'));
});

app.get('/labeling/management', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/labeling/management.html'));
});

// Testing-related routes
app.get('/testing/noise_cancellation', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/testing/noise_cancellation.html'));
});

// Storage-related routes
app.get('/storage/dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, '../static/pages/storage/dashboard.html'));
});

// API 라우트
app.use('/api/auth', authRoutes);
app.use('/api/ai', aiRoutes);
app.use('/api/lightweight-analyze', aiRoutes); // 경량 AI는 별도 경로로도 접근 가능
app.use('/api/kakao', kakaoRoutes);
app.use('/api/monitoring', monitoringRoutes);
app.use('/api/notifications', notificationRoutes);

// 카카오 로그인 라우트 (별도 경로)
app.use('/auth/kakao', kakaoRoutes);

// 관리자 라우트
app.use('/admin', adminRoutes);

// 404 처리
app.use((req, res) => {
    res.status(404).send(`
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>404 - 페이지를 찾을 수 없습니다</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                }
                h1 { font-size: 4rem; margin-bottom: 20px; }
                p { font-size: 1.2rem; margin-bottom: 30px; }
                a { 
                    color: #fff; 
                    text-decoration: none; 
                    background: rgba(255,255,255,0.2);
                    padding: 10px 20px;
                    border-radius: 5px;
                    display: inline-block;
                }
                a:hover { background: rgba(255,255,255,0.3); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>404</h1>
                <p>요청하신 페이지를 찾을 수 없습니다.</p>
                <a href="/">홈으로 돌아가기</a>
            </div>
        </body>
        </html>
    `);
});

// 에러 처리 미들웨어
app.use((error, req, res, next) => {
    console.error('서버 오류:', error);
    
    // 502 Bad Gateway 오류 처리
    if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        return res.status(502).json({
            success: false,
            message: '서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.'
        });
    }
    
    // 일반적인 서버 오류
    res.status(500).json({
        success: false,
        message: '서버 내부 오류가 발생했습니다.',
        error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
});

module.exports = app;
