const https = require('https');
const express = require('express');
const cors = require('cors');
const path = require('path');
const selfsigned = require('selfsigned');

const app = express();
const PORT = 443;

// 미들웨어 설정
app.use(cors({
    origin: ['https://signalcraft.kr', 'https://www.signalcraft.kr', 'http://localhost:8000'],
    credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 정적 파일 서빙
app.use('/static', express.static(path.join(__dirname, 'static')));
app.use(express.static(path.join(__dirname, 'static')));

// 메모리 기반 사용자 저장소
let users = [
    {
        id: 1,
        email: 'admin@signalcraft.kr',
        password: 'admin123!',
        name: '관리자',
        company: 'Signalcraft',
        role: 'admin'
    }
];

let sessions = {};

// 유틸리티 함수
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function hashPassword(password) {
    return Buffer.from(password).toString('base64');
}

function verifyPassword(password, hash) {
    return hashPassword(password) === hash;
}

// 라우트 설정
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'static', 'index.html'));
});

// 로그인 API
app.post('/api/auth/login', (req, res) => {
    try {
        const { email, password } = req.body;
        
        if (!email || !password) {
            return res.status(400).json({
                success: false,
                message: '이메일과 비밀번호를 입력해주세요.'
            });
        }
        
        const user = users.find(u => u.email === email);
        
        if (!user || !verifyPassword(password, user.password)) {
            return res.status(401).json({
                success: false,
                message: '아이디 또는 비밀번호가 틀렸습니다.'
            });
        }
        
        const sessionId = generateSessionId();
        sessions[sessionId] = {
            userId: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
            createdAt: new Date()
        };
        
        res.json({
            success: true,
            message: '로그인 성공',
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                company: user.company,
                role: user.role
            },
            sessionId: sessionId
        });
        
    } catch (error) {
        console.error('로그인 오류:', error);
        res.status(500).json({
            success: false,
            message: '서버 오류가 발생했습니다.'
        });
    }
});

// 회원가입 API
app.post('/api/auth/register', (req, res) => {
    try {
        const { name, email, password, phone, company, marketing_agree } = req.body;
        
        if (!name || !email || !password || !phone) {
            return res.status(400).json({
                success: false,
                message: '필수 항목을 모두 입력해주세요.'
            });
        }
        
        if (users.find(u => u.email === email)) {
            return res.status(409).json({
                success: false,
                message: '이미 가입된 이메일입니다.'
            });
        }
        
        const newUser = {
            id: users.length + 1,
            email: email,
            password: hashPassword(password),
            name: name,
            phone: phone,
            company: company || '',
            marketing_agree: marketing_agree || false,
            role: 'user',
            createdAt: new Date()
        };
        
        users.push(newUser);
        
        res.json({
            success: true,
            message: `${name}님, 회원가입이 완료되었습니다!`,
            user: {
                id: newUser.id,
                email: newUser.email,
                name: newUser.name,
                company: newUser.company,
                role: newUser.role
            }
        });
        
    } catch (error) {
        console.error('회원가입 오류:', error);
        res.status(500).json({
            success: false,
            message: '서버 오류가 발생했습니다.'
        });
    }
});

// 로그아웃 API
app.post('/api/auth/logout', (req, res) => {
    try {
        const { sessionId } = req.body;
        
        if (sessionId && sessions[sessionId]) {
            delete sessions[sessionId];
        }
        
        res.json({
            success: true,
            message: '로그아웃 완료'
        });
        
    } catch (error) {
        console.error('로그아웃 오류:', error);
        res.status(500).json({
            success: false,
            message: '서버 오류가 발생했습니다.'
        });
    }
});

// 세션 확인 API
app.get('/api/auth/verify', (req, res) => {
    try {
        const sessionId = req.headers.authorization?.replace('Bearer ', '');
        
        if (!sessionId || !sessions[sessionId]) {
            return res.status(401).json({
                success: false,
                message: '인증이 필요합니다.'
            });
        }
        
        const session = sessions[sessionId];
        const user = users.find(u => u.id === session.userId);
        
        if (!user) {
            return res.status(401).json({
                success: false,
                message: '사용자를 찾을 수 없습니다.'
            });
        }
        
        res.json({
            success: true,
            user: {
                id: user.id,
                email: user.email,
                name: user.name,
                company: user.company,
                role: user.role
            }
        });
        
    } catch (error) {
        console.error('세션 확인 오류:', error);
        res.status(500).json({
            success: false,
            message: '서버 오류가 발생했습니다.'
        });
    }
});

// 404 처리
app.use((req, res) => {
    res.status(404).json({
        success: false,
        message: '요청한 페이지를 찾을 수 없습니다.'
    });
});

// 자체 서명 인증서 생성
const attrs = [{ name: 'commonName', value: 'signalcraft.kr' }];
const pems = selfsigned.generate(attrs, { days: 365 });

// HTTPS 서버 시작
https.createServer({
    key: pems.private,
    cert: pems.cert
}, app).listen(PORT, '0.0.0.0', () => {
    console.log(`🔒 Signalcraft HTTPS 서버가 https://0.0.0.0:${PORT} 에서 실행 중입니다`);
    console.log(`🌐 외부 접근: https://signalcraft.kr`);
    console.log(`📁 정적 파일: static/ 폴더`);
    console.log(`🔗 API 엔드포인트: /api/*`);
    console.log(`⏰ 시작 시간: ${new Date().toISOString()}`);
    console.log(`⚠️  자체 서명 인증서 사용 - 브라우저에서 보안 경고가 표시될 수 있습니다`);
});
