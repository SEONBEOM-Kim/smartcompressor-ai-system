const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');

// 특징 데이터 저장 디렉토리
const featuresDir = path.join(__dirname, '../../data/esp32_features');
const audioDir = path.join(__dirname, '../../uploads/esp32');

console.log(`[DEBUG] esp32DashboardApi.js 로드됨`);
console.log(`[DEBUG] __dirname: ${__dirname}`);
console.log(`[DEBUG] featuresDir: ${featuresDir}`);
console.log(`[DEBUG] featuresDir exists: ${require('fs').existsSync(featuresDir)}`);

// 디렉토리 생성
if (!fs.existsSync(featuresDir)) {
    fs.mkdirSync(featuresDir, { recursive: true });
}

// 최근 특징 데이터 조회
router.get('/features/recent', (req, res) => {
    console.log(`[TEST] features/recent API 호출됨!`);
    
    try {
        const limit = parseInt(req.query.limit) || 50;
        const deviceId = req.query.device_id;

        console.log(`[DEBUG] features/recent 요청 - limit: ${limit}, deviceId: ${deviceId}`);
        console.log(`[DEBUG] featuresDir: ${featuresDir}`);

        // 디렉토리 존재 확인
        if (!fs.existsSync(featuresDir)) {
            console.log(`[DEBUG] 디렉토리가 존재하지 않음: ${featuresDir}`);
            return res.json({
                success: true,
                data: [],
                count: 0,
                total: 0
            });
        }

        // 모든 특징 데이터 파일 읽기
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'))
            .sort((a, b) => {
                const statA = fs.statSync(path.join(featuresDir, a));
                const statB = fs.statSync(path.join(featuresDir, b));
                return statB.mtime - statA.mtime; // 최신순 정렬
            });

        console.log(`[DEBUG] 찾은 파일 수: ${files.length}`);
        console.log(`[DEBUG] 파일 목록: ${files.slice(0, 5).join(', ')}`);

        let allData = [];

        // 최근 파일들에서 데이터 읽기
        for (let i = 0; i < Math.min(files.length, 10); i++) {
            try {
                const filePath = path.join(featuresDir, files[i]);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);

                console.log(`[DEBUG] 파일 ${files[i]} 데이터 타입: ${Array.isArray(data) ? 'array' : 'object'}`);
                console.log(`[DEBUG] 파일 ${files[i]} 데이터 길이: ${Array.isArray(data) ? data.length : 1}`);

                if (Array.isArray(data)) {
                    allData = allData.concat(data);
                } else {
                    allData.push(data);
                }
            } catch (error) {
                console.error(`파일 읽기 오류 ${files[i]}:`, error.message);
            }
        }

        console.log(`[DEBUG] 총 수집된 데이터: ${allData.length}`);

        // 디바이스 ID 필터링
        if (deviceId) {
            allData = allData.filter(item => item.device_id === deviceId);
            console.log(`[DEBUG] 디바이스 필터링 후: ${allData.length}`);
        }

        // 타임스탬프 기준 정렬 (최신순)
        allData.sort((a, b) => b.timestamp - a.timestamp);

        // 제한된 개수만 반환
        const recentData = allData.slice(0, limit);

        console.log(`[DEBUG] 최종 반환 데이터: ${recentData.length}`);

        res.json({
            success: true,
            data: recentData,
            count: recentData.length,
            total: allData.length
        });

    } catch (error) {
        console.error('최근 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '데이터 조회 실패',
            error: error.message
        });
    }
});

// 디바이스 목록 조회
router.get('/devices', (req, res) => {
    try {
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'));

        const devices = new Set();
        let totalDataCount = 0;

        files.forEach(file => {
            try {
                const filePath = path.join(featuresDir, file);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);
                
                if (Array.isArray(data)) {
                    data.forEach(item => {
                        if (item.device_id) {
                            devices.add(item.device_id);
                        }
                    });
                    totalDataCount += data.length;
                } else if (data.device_id) {
                    devices.add(data.device_id);
                    totalDataCount++;
                }
            } catch (error) {
                console.error(`파일 읽기 오류 ${file}:`, error.message);
            }
        });

        const deviceList = Array.from(devices).map(deviceId => ({
            device_id: deviceId,
            last_seen: getLastSeenTime(deviceId),
            data_count: getDataCount(deviceId)
        }));

        res.json({
            success: true,
            devices: deviceList,
            total_devices: deviceList.length,
            total_data: totalDataCount
        });

    } catch (error) {
        console.error('디바이스 목록 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '디바이스 목록 조회 실패',
            error: error.message
        });
    }
});

// 통계 데이터 조회
router.get('/stats', (req, res) => {
    try {
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'));

        let allData = [];
        const deviceStats = {};
        const hourlyStats = {};

        // 모든 데이터 수집
        files.forEach(file => {
            try {
                const filePath = path.join(featuresDir, file);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);
                
                if (Array.isArray(data)) {
                    allData = allData.concat(data);
                } else {
                    allData.push(data);
                }
            } catch (error) {
                console.error(`파일 읽기 오류 ${file}:`, error.message);
            }
        });

        // 통계 계산
        allData.forEach(item => {
            const deviceId = item.device_id;
            const hour = new Date(item.timestamp).getHours();

            // 디바이스별 통계
            if (!deviceStats[deviceId]) {
                deviceStats[deviceId] = {
                    count: 0,
                    total_rms: 0,
                    total_anomaly: 0,
                    compressor_on_count: 0,
                    max_rms: 0,
                    max_anomaly: 0
                };
            }

            deviceStats[deviceId].count++;
            deviceStats[deviceId].total_rms += item.rms_energy || 0;
            deviceStats[deviceId].total_anomaly += item.anomaly_score || 0;
            deviceStats[deviceId].max_rms = Math.max(deviceStats[deviceId].max_rms, item.rms_energy || 0);
            deviceStats[deviceId].max_anomaly = Math.max(deviceStats[deviceId].max_anomaly, item.anomaly_score || 0);
            
            if (item.compressor_state > 0.5) {
                deviceStats[deviceId].compressor_on_count++;
            }

            // 시간대별 통계
            if (!hourlyStats[hour]) {
                hourlyStats[hour] = {
                    count: 0,
                    total_rms: 0,
                    compressor_on_count: 0
                };
            }
            hourlyStats[hour].count++;
            hourlyStats[hour].total_rms += item.rms_energy || 0;
            if (item.compressor_state > 0.5) {
                hourlyStats[hour].compressor_on_count++;
            }
        });

        // 평균 계산
        Object.keys(deviceStats).forEach(deviceId => {
            const stats = deviceStats[deviceId];
            stats.avg_rms = stats.total_rms / stats.count;
            stats.avg_anomaly = stats.total_anomaly / stats.count;
            stats.compressor_ratio = stats.compressor_on_count / stats.count;
        });

        Object.keys(hourlyStats).forEach(hour => {
            const stats = hourlyStats[hour];
            stats.avg_rms = stats.total_rms / stats.count;
            stats.compressor_ratio = stats.compressor_on_count / stats.count;
        });

        // 전체 통계
        const totalData = allData.length;
        const avgRms = allData.reduce((sum, item) => sum + (item.rms_energy || 0), 0) / totalData;
        const avgAnomaly = allData.reduce((sum, item) => sum + (item.anomaly_score || 0), 0) / totalData;
        const compressorOnCount = allData.filter(item => item.compressor_state > 0.5).length;
        const compressorRatio = compressorOnCount / totalData;

        res.json({
            success: true,
            stats: {
                total_data: totalData,
                total_devices: Object.keys(deviceStats).length,
                avg_rms: avgRms,
                avg_anomaly: avgAnomaly,
                compressor_ratio: compressorRatio,
                device_stats: deviceStats,
                hourly_stats: hourlyStats
            }
        });

    } catch (error) {
        console.error('통계 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '통계 조회 실패',
            error: error.message
        });
    }
});

// 오디오 파일 목록 조회
router.get('/audio/files', (req, res) => {
    try {
        const files = fs.readdirSync(audioDir)
            .filter(file => file.endsWith('.raw'))
            .map(file => {
                const filePath = path.join(audioDir, file);
                const stats = fs.statSync(filePath);
                return {
                    filename: file,
                    size: stats.size,
                    created: stats.birthtime,
                    modified: stats.mtime
                };
            })
            .sort((a, b) => b.modified - a.modified);

        res.json({
            success: true,
            files: files,
            count: files.length
        });

    } catch (error) {
        console.error('오디오 파일 목록 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '오디오 파일 목록 조회 실패',
            error: error.message
        });
    }
});

// 헬퍼 함수들
function getLastSeenTime(deviceId) {
    try {
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'))
            .sort((a, b) => {
                const statA = fs.statSync(path.join(featuresDir, a));
                const statB = fs.statSync(path.join(featuresDir, b));
                return statB.mtime - statA.mtime;
            });

        for (const file of files) {
            try {
                const filePath = path.join(featuresDir, file);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);
                
                const items = Array.isArray(data) ? data : [data];
                const deviceData = items.find(item => item.device_id === deviceId);
                
                if (deviceData) {
                    return new Date(deviceData.timestamp).toISOString();
                }
            } catch (error) {
                continue;
            }
        }
        return null;
    } catch (error) {
        return null;
    }
}

function getDataCount(deviceId) {
    try {
        const files = fs.readdirSync(featuresDir)
            .filter(file => file.endsWith('.json'));

        let count = 0;
        files.forEach(file => {
            try {
                const filePath = path.join(featuresDir, file);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);
                
                const items = Array.isArray(data) ? data : [data];
                count += items.filter(item => item.device_id === deviceId).length;
            } catch (error) {
                // 무시
            }
        });
        return count;
    } catch (error) {
        return 0;
    }
}

module.exports = router;
