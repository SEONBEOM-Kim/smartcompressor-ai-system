const express = require('express');
const router = express.Router();
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// 데이터베이스 연결
const dbPath = path.join(__dirname, '../../database/smartcompressor.db');
const db = new sqlite3.Database(dbPath);

// 센서 데이터 테이블 생성
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS sensor_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        temperature REAL,
        audio_level REAL,
        rms_energy REAL,
        decibel_level REAL,
        compressor_state INTEGER,
        vibration_x REAL,
        vibration_y REAL,
        vibration_z REAL,
        power_consumption REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
    
    // 인덱스 생성
    db.run(`CREATE INDEX IF NOT EXISTS idx_sensor_device_timestamp ON sensor_data(device_id, timestamp)`);
    db.run(`CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_data(timestamp)`);
});

// 센서 데이터 수신 API
router.post('/data', (req, res) => {
    try {
        const {
            device_id,
            temperature,
            audio_level,
            rms_energy,
            vibration,
            power_consumption,
            timestamp = new Date().toISOString()
        } = req.body;

        if (!device_id) {
            return res.status(400).json({
                success: false,
                message: 'device_id가 필요합니다.'
            });
        }

        // RMS 에너지를 데시벨로 변환
        const decibel_level = rms_energy ? 20 * Math.log10(rms_energy) : 0;
        
        // 45dB 기준으로 압축기 상태 결정
        const compressor_state = decibel_level >= 45 ? 1 : 0;

        // 데이터베이스에 저장
        const stmt = db.prepare(`
            INSERT INTO sensor_data 
            (device_id, timestamp, temperature, audio_level, rms_energy, decibel_level, 
             compressor_state, vibration_x, vibration_y, vibration_z, power_consumption)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);

        stmt.run([
            device_id,
            timestamp,
            temperature || null,
            audio_level || null,
            rms_energy || null,
            decibel_level,
            compressor_state,
            vibration?.x || null,
            vibration?.y || null,
            vibration?.z || null,
            power_consumption || null
        ], function(err) {
            if (err) {
                console.error('센서 데이터 저장 오류:', err);
                return res.status(500).json({
                    success: false,
                    message: '데이터 저장 실패'
                });
            }

            console.log(`센서 데이터 저장 완료 - Device: ${device_id}, Temp: ${temperature}°C, DB: ${decibel_level.toFixed(1)}dB, Compressor: ${compressor_state ? 'ON' : 'OFF'}`);
            
            res.json({
                success: true,
                message: '센서 데이터 저장 완료',
                data_id: this.lastID,
                timestamp: timestamp
            });
        });

        stmt.finalize();

    } catch (error) {
        console.error('센서 데이터 수신 오류:', error);
        res.status(500).json({
            success: false,
            message: '서버 오류'
        });
    }
});

// 센서 데이터 조회 API (최근 데이터)
router.get('/recent', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 50;
        const device_id = req.query.device_id;

        let query = `
            SELECT * FROM sensor_data 
            WHERE 1=1
        `;
        const params = [];

        if (device_id) {
            query += ` AND device_id = ?`;
            params.push(device_id);
        }

        query += ` ORDER BY timestamp DESC LIMIT ?`;
        params.push(limit);

        db.all(query, params, (err, rows) => {
            if (err) {
                console.error('센서 데이터 조회 오류:', err);
                return res.status(500).json({
                    success: false,
                    message: '데이터 조회 실패'
                });
            }

            res.json({
                success: true,
                data: rows,
                count: rows.length
            });
        });

    } catch (error) {
        console.error('센서 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '서버 오류'
        });
    }
});

// 온도-압축기 상관관계 데이터 조회 API
router.get('/correlation', (req, res) => {
    try {
        const hours = parseInt(req.query.hours) || 24;
        const device_id = req.query.device_id;

        const query = `
            SELECT 
                device_id,
                timestamp,
                temperature,
                decibel_level,
                compressor_state,
                rms_energy,
                power_consumption
            FROM sensor_data 
            WHERE timestamp >= datetime('now', '-${hours} hours')
            ${device_id ? 'AND device_id = ?' : ''}
            ORDER BY timestamp ASC
        `;

        const params = device_id ? [device_id] : [];

        db.all(query, params, (err, rows) => {
            if (err) {
                console.error('상관관계 데이터 조회 오류:', err);
                return res.status(500).json({
                    success: false,
                    message: '데이터 조회 실패'
                });
            }

            // 온도별 그룹화 및 통계 계산
            const tempGroups = {};
            rows.forEach(row => {
                if (row.temperature !== null) {
                    const tempRange = Math.floor(row.temperature / 5) * 5; // 5도 단위로 그룹화
                    if (!tempGroups[tempRange]) {
                        tempGroups[tempRange] = {
                            temperature: tempRange,
                            total_count: 0,
                            on_count: 0,
                            avg_decibel: 0,
                            avg_power: 0,
                            data_points: []
                        };
                    }
                    
                    tempGroups[tempRange].total_count++;
                    if (row.compressor_state === 1) {
                        tempGroups[tempRange].on_count++;
                    }
                    tempGroups[tempRange].avg_decibel += row.decibel_level;
                    tempGroups[tempRange].avg_power += (row.power_consumption || 0);
                    tempGroups[tempRange].data_points.push(row);
                }
            });

            // 평균 계산
            Object.values(tempGroups).forEach(group => {
                group.avg_decibel = group.avg_decibel / group.total_count;
                group.avg_power = group.avg_power / group.total_count;
                group.on_ratio = group.on_count / group.total_count;
            });

            res.json({
                success: true,
                data: rows,
                correlation_data: Object.values(tempGroups),
                summary: {
                    total_records: rows.length,
                    temperature_ranges: Object.keys(tempGroups).length,
                    avg_temperature: rows.reduce((sum, row) => sum + (row.temperature || 0), 0) / rows.length,
                    avg_on_ratio: rows.filter(row => row.compressor_state === 1).length / rows.length
                }
            });
        });

    } catch (error) {
        console.error('상관관계 데이터 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '서버 오류'
        });
    }
});

// 센서 통계 API
router.get('/stats', (req, res) => {
    try {
        const device_id = req.query.device_id;
        const hours = parseInt(req.query.hours) || 24;

        const query = `
            SELECT 
                COUNT(*) as total_count,
                AVG(temperature) as avg_temperature,
                MIN(temperature) as min_temperature,
                MAX(temperature) as max_temperature,
                AVG(decibel_level) as avg_decibel,
                MIN(decibel_level) as min_decibel,
                MAX(decibel_level) as max_decibel,
                SUM(compressor_state) as on_count,
                AVG(power_consumption) as avg_power,
                COUNT(DISTINCT device_id) as device_count
            FROM sensor_data 
            WHERE timestamp >= datetime('now', '-${hours} hours')
            ${device_id ? 'AND device_id = ?' : ''}
        `;

        const params = device_id ? [device_id] : [];

        db.get(query, params, (err, row) => {
            if (err) {
                console.error('센서 통계 조회 오류:', err);
                return res.status(500).json({
                    success: false,
                    message: '통계 조회 실패'
                });
            }

            const on_ratio = row.total_count > 0 ? row.on_count / row.total_count : 0;

            res.json({
                success: true,
                stats: {
                    total_count: row.total_count,
                    device_count: row.device_count,
                    temperature: {
                        avg: row.avg_temperature?.toFixed(2) || 0,
                        min: row.min_temperature?.toFixed(2) || 0,
                        max: row.max_temperature?.toFixed(2) || 0
                    },
                    audio: {
                        avg_decibel: row.avg_decibel?.toFixed(2) || 0,
                        min_decibel: row.min_decibel?.toFixed(2) || 0,
                        max_decibel: row.max_decibel?.toFixed(2) || 0
                    },
                    compressor: {
                        on_count: row.on_count,
                        on_ratio: (on_ratio * 100).toFixed(2),
                        off_count: row.total_count - row.on_count
                    },
                    power: {
                        avg_consumption: row.avg_power?.toFixed(2) || 0
                    }
                }
            });
        });

    } catch (error) {
        console.error('센서 통계 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '서버 오류'
        });
    }
});

// 테스트용 센서 데이터 생성 API
router.post('/test-data', (req, res) => {
    try {
        const { count = 10, device_id = 'TEST_DEVICE_001' } = req.body;
        const testData = [];
        
        for (let i = 0; i < count; i++) {
            const timestamp = new Date(Date.now() - i * 60 * 60 * 1000); // 1시간 간격
            const temperature = 15 + Math.sin(i / 24 * Math.PI * 2) * 10 + (Math.random() - 0.5) * 5;
            const rms_energy = Math.random() * 1000 + 100;
            const decibel_level = 20 * Math.log10(rms_energy);
            const compressor_state = decibel_level >= 45 ? 1 : 0;
            
            testData.push({
                device_id,
                timestamp: timestamp.toISOString(),
                temperature: temperature.toFixed(2),
                audio_level: decibel_level.toFixed(2),
                rms_energy: rms_energy.toFixed(2),
                vibration: {
                    x: (Math.random() - 0.5) * 10,
                    y: (Math.random() - 0.5) * 10,
                    z: (Math.random() - 0.5) * 10
                },
                power_consumption: 100 + Math.random() * 50
            });
        }
        
        // 테스트 데이터를 데이터베이스에 저장
        const stmt = db.prepare(`
            INSERT INTO sensor_data 
            (device_id, timestamp, temperature, audio_level, rms_energy, decibel_level, 
             compressor_state, vibration_x, vibration_y, vibration_z, power_consumption)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `);
        
        let successCount = 0;
        testData.forEach(data => {
            const decibel_level = parseFloat(data.audio_level);
            stmt.run([
                data.device_id,
                data.timestamp,
                parseFloat(data.temperature),
                decibel_level,
                parseFloat(data.rms_energy),
                decibel_level,
                decibel_level >= 45 ? 1 : 0,
                data.vibration.x,
                data.vibration.y,
                data.vibration.z,
                data.power_consumption
            ], function(err) {
                if (!err) successCount++;
            });
        });
        
        stmt.finalize();
        
        res.json({
            success: true,
            message: `${successCount}개의 테스트 데이터가 생성되었습니다.`,
            data: testData.slice(0, 3) // 처음 3개만 반환
        });
        
    } catch (error) {
        console.error('테스트 데이터 생성 오류:', error);
        res.status(500).json({
            success: false,
            message: '테스트 데이터 생성 실패'
        });
    }
});

module.exports = router;
