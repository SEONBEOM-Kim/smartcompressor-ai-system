const express = require('express');
const path = require('path');

const app = express();
const PORT = 3000;

// 정적 파일 서빙
app.use('/static', express.static(path.join(__dirname, 'static')));
app.use(express.static(path.join(__dirname, 'static')));

// ESP32 센서 대시보드 페이지
app.get('/esp32-dashboard', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/pages/esp32_dashboard.html'));
});

// 오디오 연구 페이지
app.get('/audio-research', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/pages/audio_research.html'));
});

// 메인 페이지
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'static/showcase.html'));
});

// ESP32 API 라우트들
app.use('/api/esp32', require('./server/routes/esp32Routes'));
app.use('/api/esp32', require('./server/routes/esp32FilesApi'));
app.use('/api/esp32', require('./server/routes/esp32FeaturesApi'));
app.use('/api/esp32', require('./server/routes/esp32DashboardApi'));

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

app.listen(PORT, () => {
    console.log(`🚀 Simple Dashboard Server running on port ${PORT}`);
    console.log(`📊 ESP32 Dashboard: http://localhost:${PORT}/esp32-dashboard`);
    console.log(`🎵 Audio Research: http://localhost:${PORT}/audio-research`);
});
