const express = require('express');
const router = express.Router();

router.get('/verify', (req, res) => {
    res.json({
        success: false,
        message: '인증 토큰이 필요합니다.'
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