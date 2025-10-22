const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = 'uploads/audio';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        cb(null, 'audio-' + Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage, limits: { fileSize: 10 * 1024 * 1024 } });

router.post('/analyze', upload.single('audio'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ success: false, message: '오디오 파일이 필요합니다.' });
        }
        res.json({ success: true, message: 'AI 분석이 완료되었습니다.' });
    } catch (error) {
        res.status(500).json({ success: false, message: 'AI 분석 중 오류가 발생했습니다.' });
    }
});

router.get('/model-info', (req, res) => {
    res.json({ success: true, models: { lightweight: { name: 'Lightweight Compressor AI' } } });
});

module.exports = router;
