// ESP32 전용 서버 (SQLite3 없이 실행)
require('dotenv').config({ path: require('path').resolve(__dirname, '.env') });
const express = require('express');
const path = require('path');
const cors = require('cors');

const app = express();

// CORS 설정
app.use(cors({
    origin: ['https://signalcraft.kr', 'http://localhost:3000', 'http://127.0.0.1:3000'],
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'Origin', 'X-Requested-With', 'Accept']
}));

// 미들웨어 설정
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// 정적 파일 서빙
app.use('/static', express.static(path.join(__dirname, 'static')));
app.use(express.static(path.join(__dirname, 'static')));

// ESP32 대시보드 페이지
app.get('/esp32-dashboard', (req, res) => {
    res.removeHeader('ETag');
    res.removeHeader('Last-Modified');
    res.set('Cache-Control', 'no-cache, no-store, must-revalidate, private');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');
    res.set('Vary', '*');
    res.sendFile(path.join(__dirname, 'static/pages/esp32_dashboard.html'));
});

// ESP32 디버깅 페이지
app.get('/debug_esp32', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/pages/debug_esp32.html'));
});

// ESP32 API 라우트들
const esp32FeaturesApi = require('./server/routes/esp32FeaturesApi');
const esp32DashboardApi = require('./server/routes/esp32DashboardApi');
const esp32AiApi = require('./server/routes/esp32AiApi');

app.use('/api/esp32', esp32FeaturesApi);
app.use('/api/esp32', esp32DashboardApi);
app.use('/api/esp32', esp32AiApi);

// ESP32 센서를 위한 프록시 라우트 (3.39.124.0:3000 -> signalcraft.kr:3000)
app.use('/api/esp32/features', (req, res, next) => {
    if (req.get('host') && req.get('host').includes('3.39.124.0')) {
        console.log('ESP32 센서 요청 감지 - 프록시 처리');
        return esp32FeaturesApi(req, res, next);
    }
    next();
});

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
                <a href="/esp32-dashboard">ESP32 대시보드로 이동</a>
            </div>
        </body>
        </html>
    `);
});

// 에러 처리 미들웨어
app.use((error, req, res, next) => {
    console.error('서버 오류:', error);
    res.status(500).json({
        success: false,
        message: '서버 내부 오류가 발생했습니다.',
        error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
});

const PORT = process.env.PORT || 3000;
const HOST = process.env.HOST || '0.0.0.0';

app.listen(PORT, HOST, () => {
    console.log(`🚀 ESP32 서버가 http://${HOST}:${PORT}에서 실행 중입니다.`);
    console.log(`📊 대시보드: http://localhost:${PORT}/esp32-dashboard`);
    console.log(`🔧 디버깅: http://localhost:${PORT}/debug_esp32`);
});

module.exports = app;
