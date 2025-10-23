const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

// ESP32 특징 데이터 저장
router.post('/features', (req, res) => {
    try {
        console.log('ESP32 Features API 호출됨');
        console.log('Request body:', req.body);
        console.log('Request headers:', req.headers);
        
        const features = req.body;
        const deviceId = req.headers['x-device-id'] || 'unknown';
        
        console.log(`ESP32 특징 데이터 수신 - Device: ${deviceId}`);
        console.log(`RMS: ${features.rms_energy}, Compressor: ${features.compressor_state > 0.5 ? 'ON' : 'OFF'}`);
        console.log(`Anomaly: ${features.anomaly_score}, Efficiency: ${features.efficiency_score}`);
        
        // 특징 데이터를 파일로 저장
        const featuresDir = path.join(__dirname, '../../data/esp32_features');
        if (!fs.existsSync(featuresDir)) {
            fs.mkdirSync(featuresDir, { recursive: true });
        }
        
        const filename = `features_${deviceId}_${Date.now()}.json`;
        const filepath = path.join(featuresDir, filename);
        
        // 메타데이터 추가
        const dataWithMeta = {
            ...features,
            received_at: new Date().toISOString(),
            device_id: deviceId,
            store_type: req.headers['x-store-type'] || 'unknown'
        };
        
        // 파일로 저장
        fs.writeFileSync(filepath, JSON.stringify(dataWithMeta, null, 2));
        
        console.log(`✅ ESP32 데이터 저장 완료 - ${filename}`);
        
        res.json({
            success: true,
            message: 'ESP32 특징 데이터 저장 완료',
            device_id: deviceId,
            timestamp: features.timestamp,
            data_size: JSON.stringify(dataWithMeta).length
        });
        
    } catch (error) {
        console.error('ESP32 특징 데이터 처리 오류:', error);
        res.status(500).json({
            success: false,
            message: 'ESP32 특징 데이터 처리 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// ESP32 특징 데이터 조회
router.get('/features/recent', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 50;
        const deviceId = req.query.device_id;
        
        console.log(`ESP32 특징 데이터 조회 - Device: ${deviceId}, Limit: ${limit}`);
        
        const featuresDir = path.join(__dirname, '../../data/esp32_features');
        
        if (!fs.existsSync(featuresDir)) {
            return res.json({
                success: true,
                data: [],
                count: 0,
                total: 0
            });
        }
        
        // 모든 JSON 파일 찾기 (features_로 시작하는 파일과 test_data.json 포함)
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'))
            .map(file => {
                const filepath = path.join(featuresDir, file);
                const stats = fs.statSync(filepath);
                return {
                    filename: file,
                    filepath: filepath,
                    modified: stats.mtime
                };
            })
            .sort((a, b) => b.modified - a.modified)
            .slice(0, limit);
        
        const data = [];
        for (const file of files) {
            try {
                const content = fs.readFileSync(file.filepath, 'utf8');
                const parsed = JSON.parse(content);
                
                // 배열인 경우 각 항목을 개별적으로 추가
                if (Array.isArray(parsed)) {
                    data.push(...parsed);
                } else {
                    // 단일 객체인 경우 그대로 추가
                    data.push(parsed);
                }
            } catch (err) {
                console.error(`파일 읽기 오류: ${file.filename}`, err);
            }
        }
        
        // 시간순으로 정렬 (최신이 먼저)
        data.sort((a, b) => (b.timestamp || b.server_timestamp || 0) - (a.timestamp || a.server_timestamp || 0));
        
        // 디바이스 ID 필터링
        let filteredData = data;
        if (deviceId) {
            filteredData = data.filter(item => item.device_id === deviceId);
        }
        
        // 제한된 개수만 반환
        filteredData = filteredData.slice(0, limit);
        
        res.json({
            success: true,
            data: filteredData,
            count: filteredData.length,
            total: data.length
        });
        
    } catch (error) {
        console.error('ESP32 특징 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: 'ESP32 특징 데이터 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

module.exports = router;