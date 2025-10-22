const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs');

// ESP32 상태 확인
router.get('/status', (req, res) => {
    res.json({
        status: 'online',
        timestamp: new Date().toISOString(),
        message: 'ESP32 API is working'
    });
});

// ESP32 오디오 업로드 (application/octet-stream 처리)
router.post('/audio/upload', (req, res) => {
    try {
        const deviceId = req.headers['x-device-id'];
        const timestamp = req.headers['x-timestamp'];
        const sampleRate = req.headers['x-sample-rate'];
        
        console.log(`ESP32 업로드 - Device: ${deviceId}, Timestamp: ${timestamp}, Sample Rate: ${sampleRate}`);
        
        // 업로드 디렉토리 생성
        const uploadDir = 'uploads/esp32';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
        }
        
        // 파일명 생성
        const filename = `esp32_${deviceId}_${timestamp}.raw`;
        const filepath = path.join(uploadDir, filename);
        
        // 오디오 데이터를 파일로 저장
        const writeStream = fs.createWriteStream(filepath);
        
        req.on('data', (chunk) => {
            writeStream.write(chunk);
        });
        
        req.on('end', () => {
            writeStream.end();
            
            // 파일 크기 확인
            const stats = fs.statSync(filepath);
            const fileSize = stats.size;
            
            console.log(`오디오 파일 저장 완료: ${filepath} (${fileSize} bytes)`);
            
            // AI 분석 시뮬레이션
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
                file_size: fileSize,
                file_path: filepath,
                analysis: analysisResult
            });
        });
        
        req.on('error', (error) => {
            console.error('ESP32 업로드 오류:', error);
            writeStream.end();
            res.status(500).json({
                success: false,
                message: '오디오 업로드 중 오류가 발생했습니다.',
                error: error.message
            });
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
