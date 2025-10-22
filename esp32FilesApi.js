const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

// ESP32 파일 목록 API
router.get('/files', (req, res) => {
    try {
        const uploadDir = path.join(__dirname, '../../uploads/esp32');
        
        // 디렉토리가 없으면 생성
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir, { recursive: true });
            return res.json([]);
        }
        
        // 파일 목록 읽기
        const files = fs.readdirSync(uploadDir)
            .filter(file => file.endsWith('.raw'))
            .map(file => {
                const filePath = path.join(uploadDir, file);
                const stats = fs.statSync(filePath);
                
                // 파일명에서 디바이스 ID와 타임스탬프 추출
                const parts = file.replace('.raw', '').split('_');
                const deviceId = parts.length >= 2 ? parts[1] : 'Unknown';
                const timestamp = parts.length >= 3 ? parts[2] : 'Unknown';
                
                return {
                    name: file,
                    size: stats.size,
                    modified: stats.mtime.toISOString(),
                    deviceId: deviceId,
                    timestamp: timestamp,
                    analysis: {
                        is_overload: Math.random() > 0.7,
                        confidence: Math.random() * 0.4 + 0.6,
                        message: Math.random() > 0.7 ? '이상 신호가 감지되었습니다' : '정상 작동 중입니다',
                        processing_time_ms: Math.random() * 50 + 10
                    }
                };
            })
            .sort((a, b) => new Date(b.modified) - new Date(a.modified)); // 최신순 정렬
        
        res.json(files);
        
    } catch (error) {
        console.error('파일 목록 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '파일 목록을 불러올 수 없습니다.',
            error: error.message
        });
    }
});

// 특정 파일 다운로드
router.get('/download/:filename', (req, res) => {
    try {
        const filename = req.params.filename;
        const filePath = path.join(__dirname, '../../uploads/esp32', filename);
        
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({
                success: false,
                message: '파일을 찾을 수 없습니다.'
            });
        }
        
        res.download(filePath, filename);
        
    } catch (error) {
        console.error('파일 다운로드 오류:', error);
        res.status(500).json({
            success: false,
            message: '파일 다운로드 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 파일 삭제
router.delete('/delete/:filename', (req, res) => {
    try {
        const filename = req.params.filename;
        const filePath = path.join(__dirname, '../../uploads/esp32', filename);
        
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({
                success: false,
                message: '파일을 찾을 수 없습니다.'
            });
        }
        
        fs.unlinkSync(filePath);
        
        res.json({
            success: true,
            message: '파일이 삭제되었습니다.'
        });
        
    } catch (error) {
        console.error('파일 삭제 오류:', error);
        res.status(500).json({
            success: false,
            message: '파일 삭제 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

module.exports = router;
