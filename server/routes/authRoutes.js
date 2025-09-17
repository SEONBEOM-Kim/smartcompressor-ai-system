const express = require('express');
const database = require('../config/database');
const router = express.Router();

router.get('/verify', (req, res) => {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        return res.json({
            success: false,
            message: '인증 토큰이 필요합니다.'
        });
    }
    
    const sessionId = authHeader.substring(7); // "Bearer " 제거
    
    // 세션 ID로 사용자 정보 조회
    const session = database.getSession(sessionId);
    
    if (!session) {
        return res.json({
            success: false,
            message: '유효하지 않은 세션입니다.'
        });
    }
    
    // 사용자 정보 조회
    const user = database.getUserById(session.userId);
    
    if (!user) {
        return res.json({
            success: false,
            message: '사용자 정보를 찾을 수 없습니다.'
        });
    }
    
    res.json({
        success: true,
        user: {
            id: user.id,
            email: user.email,
            name: user.name,
            company: user.company,
            role: user.role,
            provider: user.provider,
            profile_image: user.profile_image,
            thumbnail_image: user.thumbnail_image
        }
    });
});

router.post('/login', (req, res) => {
    res.json({
        success: false,
        message: '로그인 기능을 구현 중입니다.'
    });
});

router.post('/register', (req, res) => {
    res.json({
        success: false,
        message: '회원가입 기능을 구현 중입니다.'
    });
});

module.exports = router;