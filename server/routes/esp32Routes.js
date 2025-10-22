const express = require('express');
const router = express.Router();
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Multer 설정 (오디오 파일 업로드용)
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = 'uploads/esp32';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        const deviceId = req.headers['x-device-id'] || 'unknown';
        const timestamp = req.headers['x-timestamp'] || Date.now();
        cb(null, `esp32_${deviceId}_${timestamp}.raw`);
    }
});

const upload = multer({
    storage: storage,
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB 제한
    }
});

// ESP32 상태 확인
router.get('/status', (req, res) => {
    res.json({
        status: 'online',
        timestamp: new Date().toISOString(),
        message: 'ESP32 API is working'
    });
});

// ESP32 오디오 업로드
router.post('/audio/upload', upload.single('audio'), (req, res) => {
    try {
        const deviceId = req.headers['x-device-id'];
        const timestamp = req.headers['x-timestamp'];
        const sampleRate = req.headers['x-sample-rate'];
        
        console.log(`ESP32 업로드 - Device: ${deviceId}, Timestamp: ${timestamp}, Sample Rate: ${sampleRate}`);
        
        if (!req.file) {
            return res.status(400).json({
                success: false,
                message: '오디오 데이터가 필요합니다.'
            });
        }
        
        // 여기에 AI 분석 로직 추가 가능
        const analysisResult = {
            is_overload: Math.random() > 0.7,
            confidence: Math.random() * 0.4 + 0.6,
            message: Math.random() > 0.7 ? '이상 신호가 감지되었습니다' : '정상 작동 중입니다',
            processing_time_ms: Math.random() * 50 + 10
        };
        
        res.json({
            success: true,
            message: '오디오 업로드 성공',
            device_id: deviceId,
            timestamp: timestamp,
            sample_rate: sampleRate,
            file_size: req.file.size,
            analysis: analysisResult
        });
        
    } catch (error) {
        console.error('ESP32 업로드 오류:', error);
        res.status(500).json({
            success: false,
            message: '오디오 업로드 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

module.exports = router;
