const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
    res.send('관리자 대시보드');
});

module.exports = router;