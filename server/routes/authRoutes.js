const express = require('express');
const bcrypt = require('bcryptjs');
const SQLiteDatabaseService = require('../../services/sqlite_database_service');

const router = express.Router();
const db = new SQLiteDatabaseService();

// 회원가입 (4단계 지원)
router.post('/register', async (req, res) => {
    try {
        const { 
            username, 
            email, 
            password, 
            full_name, 
            phone,
            position,
            company,
            industry,
            company_size,
            company_email,
            address,
            purpose,
            budget,
            timeline,
            device_count,
            email_alerts,
            email_newsletter,
            sms_alerts,
            kakao_alerts,
            privacy_agree,
            terms_agree,
            marketing_agree,
            role = 'user'
        } = req.body;
        
        // 필수 필드 검증
        if (!username || !email || !password) {
            return res.status(400).json({ 
                success: false, 
                message: '사용자명, 이메일, 비밀번호는 필수입니다.' 
            });
        }
        
        // 개인정보처리방침 및 서비스 이용약관 동의 확인
        if (!privacy_agree || !terms_agree) {
            return res.status(400).json({ 
                success: false, 
                message: '개인정보처리방침 및 서비스 이용약관에 동의해주세요.' 
            });
        }

        // 이메일 형식 검증
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return res.status(400).json({ 
                success: false, 
                message: '올바른 이메일 형식이 아닙니다.' 
            });
        }

        // 비밀번호 길이 검증
        if (password.length < 6) {
            return res.status(400).json({ 
                success: false, 
                message: '비밀번호는 최소 6자 이상이어야 합니다.' 
            });
        }

        // 중복 사용자명 확인
        const existingUser = await db.getUserByUsername(username);
        if (existingUser) {
            return res.status(409).json({ 
                success: false, 
                message: '이미 사용 중인 사용자명입니다.' 
            });
        }

        // 중복 이메일 확인
        const existingEmail = await db.getUserByEmail(email);
        if (existingEmail) {
            return res.status(409).json({ 
                success: false, 
                message: '이미 사용 중인 이메일입니다.' 
            });
        }

        // 비밀번호 해시화
        const saltRounds = 10;
        const password_hash = await bcrypt.hash(password, saltRounds);

        // 사용자 생성 (4단계 데이터 포함)
        const userData = {
            username,
            email,
            password_hash,
            full_name: full_name || username, // full_name이 없으면 username 사용
            phone: phone || null,
            role: role || 'user',
            // 추가 필드들을 JSON으로 저장 (향후 확장 가능)
            additional_info: {
                position,
                company,
                industry,
                company_size,
                company_email,
                address,
                purpose: Array.isArray(purpose) ? purpose : (purpose ? [purpose] : []),
                budget,
                timeline,
                device_count,
                preferences: {
                    email_alerts: email_alerts || false,
                    email_newsletter: email_newsletter || false,
                    sms_alerts: sms_alerts || false,
                    kakao_alerts: kakao_alerts || false,
                    marketing_agree: marketing_agree || false
                }
            }
        };

        const newUser = await db.createUser(userData);

        // 세션 생성
        const sessionId = generateSessionId();
        const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24시간
        
        await db.createSession(sessionId, newUser.id, expiresAt);

        // 세션 쿠키 설정
        res.cookie('sessionId', sessionId, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            maxAge: 24 * 60 * 60 * 1000, // 24시간
            sameSite: 'lax'
        });

        res.status(201).json({ 
            success: true, 
            message: '회원가입이 완료되었습니다.',
            user: { 
                id: newUser.id,
                username: newUser.username, 
                email: newUser.email,
                full_name: newUser.full_name,
                role: newUser.role
            }
        });

    } catch (error) {
        console.error('회원가입 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '회원가입 중 오류가 발생했습니다.' 
        });
    }
});

// 로그인
router.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        
        // 필수 필드 검증
        if (!username || !password) {
            return res.status(400).json({ 
                success: false, 
                message: '사용자명과 비밀번호를 입력해주세요.' 
            });
        }

        // 사용자 조회 (사용자명 또는 이메일로)
        let user = await db.getUserByUsername(username);
        if (!user) {
            user = await db.getUserByEmail(username);
        }

        if (!user) {
            return res.status(401).json({ 
                success: false, 
                message: '잘못된 사용자명 또는 비밀번호입니다.' 
            });
        }

        // 비밀번호 확인
        const isPasswordValid = await bcrypt.compare(password, user.password_hash);
        if (!isPasswordValid) {
            return res.status(401).json({ 
                success: false, 
                message: '잘못된 사용자명 또는 비밀번호입니다.' 
            });
        }

        // 마지막 로그인 시간 업데이트
        await db.updateUserLastLogin(user.id);

        // 세션 생성
        const sessionId = generateSessionId();
        const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24시간
        
        await db.createSession(sessionId, user.id, expiresAt);

        // 세션 쿠키 설정
        res.cookie('sessionId', sessionId, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            maxAge: 24 * 60 * 60 * 1000, // 24시간
            sameSite: 'lax'
        });

        res.json({ 
            success: true, 
            message: '로그인 성공',
            user: { 
                id: user.id,
                username: user.username, 
                email: user.email,
                full_name: user.full_name,
                role: user.role
            }
        });

    } catch (error) {
        console.error('로그인 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '로그인 중 오류가 발생했습니다.' 
        });
    }
});

// 세션 검증 미들웨어
const authenticateSession = async (req, res, next) => {
    try {
        const sessionId = req.cookies.sessionId;

        if (!sessionId) {
            return res.status(401).json({ 
                success: false, 
                message: '로그인이 필요합니다.' 
            });
        }

        const session = await db.getSession(sessionId);
        
        if (!session) {
            return res.status(401).json({ 
                success: false, 
                message: '유효하지 않은 세션입니다.' 
            });
        }

        req.user = {
            userId: session.user_id,
            username: session.username,
            role: session.role
        };
        next();
    } catch (error) {
        console.error('세션 검증 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '세션 검증 중 오류가 발생했습니다.' 
        });
    }
};

// 사용자 정보 조회
router.get('/profile', authenticateSession, async (req, res) => {
    try {
        const user = await db.getUserByUsername(req.user.username);
        if (!user) {
            return res.status(404).json({ 
                success: false, 
                message: '사용자를 찾을 수 없습니다.' 
            });
        }

        res.json({ 
            success: true, 
            user: { 
                id: user.id,
                username: user.username, 
                email: user.email,
                full_name: user.full_name,
                phone: user.phone,
                role: user.role,
                created_at: user.created_at,
                last_login: user.last_login
            }
        });

    } catch (error) {
        console.error('프로필 조회 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '프로필 조회 중 오류가 발생했습니다.' 
        });
    }
});

// 로그아웃 (세션 삭제)
router.post('/logout', async (req, res) => {
    try {
        const sessionId = req.cookies.sessionId;
        
        if (sessionId) {
            await db.deleteSession(sessionId);
            res.clearCookie('sessionId');
        }
        
        res.json({ 
            success: true, 
            message: '로그아웃되었습니다.' 
        });
    } catch (error) {
        console.error('로그아웃 오류:', error);
        res.status(500).json({ 
            success: false, 
            message: '로그아웃 중 오류가 발생했습니다.' 
        });
    }
});

// 세션 ID 생성 함수
function generateSessionId() {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

// 1시간마다 만료된 세션 정리
setInterval(async () => {
    try {
        await db.cleanupExpiredSessions();
    } catch (error) {
        console.error('세션 정리 오류:', error);
    }
}, 60 * 60 * 1000);

module.exports = router;