const express = require('express');
const router = express.Router();

router.get('/status', (req, res) => {
    res.json({
        success: true,
        is_running: false,
        message: '모니터링 서비스를 구현 중입니다.'
    });
});

module.exports = router;