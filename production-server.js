const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const HOST = '0.0.0.0'; // 모든 인터페이스에서 접근 가능

// MIME 타입 매핑
const mimeTypes = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    '.svg': 'image/svg+xml',
    '.wav': 'audio/wav',
    '.mp3': 'audio/mpeg',
    '.mp4': 'video/mp4',
    '.woff': 'font/woff',
    '.woff2': 'font/woff2',
    '.ttf': 'font/ttf',
    '.eot': 'application/vnd.ms-fontobject'
};

const server = http.createServer((req, res) => {
    const clientIP = req.connection.remoteAddress || req.socket.remoteAddress;
    console.log(`${new Date().toISOString()} - ${req.method} ${req.url} - IP: ${clientIP}`);
    
    let filePath = req.url;
    
    // 루트 경로는 index.html로 리다이렉트
    if (filePath === '/') {
        filePath = '/index.html';
    }
    
    // static 폴더에서 파일 제공
    const fullPath = path.join(__dirname, 'static', filePath);
    
    // 파일 존재 확인
    fs.access(fullPath, fs.constants.F_OK, (err) => {
        if (err) {
            // 파일이 없으면 404
            res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
            res.end(`
                <!DOCTYPE html>
                <html lang="ko">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>404 - Signalcraft</title>
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
            return;
        }
        
        // 파일 읽기
        fs.readFile(fullPath, (err, data) => {
            if (err) {
                res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
                res.end('서버 내부 오류');
                return;
            }
            
            // MIME 타입 결정
            const ext = path.extname(fullPath).toLowerCase();
            const contentType = mimeTypes[ext] || 'application/octet-stream';
            
            // 보안 헤더 추가
            res.setHeader('X-Content-Type-Options', 'nosniff');
            res.setHeader('X-Frame-Options', 'DENY');
            res.setHeader('X-XSS-Protection', '1; mode=block');
            res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
            
            // CORS 헤더 (필요한 경우에만)
            res.setHeader('Access-Control-Allow-Origin', '*');
            res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
            res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
            
            // 캐시 설정
            if (ext === '.html') {
                res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
                res.setHeader('Pragma', 'no-cache');
                res.setHeader('Expires', '0');
            } else {
                res.setHeader('Cache-Control', 'public, max-age=3600');
            }
            
            res.writeHead(200, { 'Content-Type': contentType + '; charset=utf-8' });
            res.end(data);
        });
    });
});

server.listen(PORT, HOST, () => {
    console.log(`🚀 Signalcraft 서버가 http://${HOST}:${PORT} 에서 실행 중입니다`);
    console.log(`🌐 외부 접근: http://signalcraft.kr:${PORT}`);
    console.log(`📁 정적 파일 서빙: static/ 폴더`);
    console.log(`⏰ 시작 시간: ${new Date().toISOString()}`);
    console.log(`🔗 로컬 접속: http://localhost:${PORT}`);
});

// 에러 처리
server.on('error', (err) => {
    console.error('서버 오류:', err);
    if (err.code === 'EADDRINUSE') {
        console.error(`포트 ${PORT}이 이미 사용 중입니다.`);
    }
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 서버를 종료합니다...');
    server.close(() => {
        console.log('✅ 서버가 안전하게 종료되었습니다.');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    console.log('\n🛑 서버를 종료합니다...');
    server.close(() => {
        console.log('✅ 서버가 안전하게 종료되었습니다.');
        process.exit(0);
    });
});
