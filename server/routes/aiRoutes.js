const express = require('express');
const router = express.Router();

router.post('/lightweight-analyze', (req, res) => {
    res.json({
        success: true,
        message: 'AI 분석 기능을 구현 중입니다.',
        is_overload: false,
        confidence: 0.5
    });
});

module.exports = router;