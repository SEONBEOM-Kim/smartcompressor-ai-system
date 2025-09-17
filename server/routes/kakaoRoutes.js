const express = require('express');
const kakaoService = require('../services/kakaoService');

const router = express.Router();

// 카카오 로그인 URL 생성
router.get('/login', (req, res) => {
    try {
        // 캐시 무효화 헤더 추가
        res.set({
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        });
        
        const loginUrl = kakaoService.getLoginUrl();
        console.log('생성된 카카오 로그인 URL:', loginUrl);
        
        res.json({
            success: true,
            login_url: loginUrl
        });
    } catch (error) {
        console.error('카카오 로그인 URL 생성 오류:', error);
        res.status(500).json({
            success: false,
            message: '카카오 로그인 URL을 생성할 수 없습니다.'
        });
    }
});

// 카카오 로그인 (액세스 토큰으로)
router.post('/login', async (req, res) => {
    try {
        const { access_token } = req.body;
        
        if (!access_token) {
            return res.status(400).json({
                success: false,
                message: '카카오 액세스 토큰이 필요합니다.'
            });
        }

        const result = await kakaoService.login(access_token);
        
        if (result.success) {
            res.json(result);
        } else {
            res.status(401).json(result);
        }
    } catch (error) {
        console.error('카카오 로그인 오류:', error);
        res.status(500).json({
            success: false,
            message: '카카오 로그인 중 오류가 발생했습니다.'
        });
    }
});

// 카카오 로그인 콜백 (인증 코드로)
router.get('/callback', async (req, res) => {
    try {
        const { code, error } = req.query;
        
        if (error) {
            return res.status(400).json({
                success: false,
                message: `카카오 로그인 오류: ${error}`
            });
        }

        if (!code) {
            return res.status(400).json({
                success: false,
                message: '인증 코드가 없습니다.'
            });
        }

        // 인증 코드로 액세스 토큰 발급
        const tokenResult = await kakaoService.getAccessToken(code);
        
        if (!tokenResult.success) {
            return res.status(400).json(tokenResult);
        }

        // 액세스 토큰으로 로그인 처리
        const loginResult = await kakaoService.login(tokenResult.access_token);
        
        if (loginResult.success) {
            // 성공 시 프론트엔드로 리다이렉트 (세션 정보 포함)
            const frontendUrl = process.env.FRONTEND_URL || 'https://signalcraft.kr:3000';
            const redirectUrl = `${frontendUrl}?kakao_login=success&session_id=${loginResult.sessionId}`;
            console.log('카카오 로그인 성공, 리다이렉트:', redirectUrl);
            res.redirect(redirectUrl);
        } else {
            res.status(401).json(loginResult);
        }
    } catch (error) {
        console.error('카카오 로그인 콜백 오류:', error);
        res.status(500).json({
            success: false,
            message: '카카오 로그인 콜백 처리 중 오류가 발생했습니다.'
        });
    }
});

// 카카오 로그아웃
router.post('/logout', async (req, res) => {
    try {
        const { access_token } = req.body;
        const result = await kakaoService.logout(access_token);
        res.json(result);
    } catch (error) {
        console.error('카카오 로그아웃 오류:', error);
        res.status(500).json({
            success: false,
            message: '카카오 로그아웃 중 오류가 발생했습니다.'
        });
    }
});

module.exports = router;
