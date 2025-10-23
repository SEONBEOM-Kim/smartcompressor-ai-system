/**
 * ESP32 AI 분석 API 라우트
 */

const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

// AI 분석 결과 저장 디렉토리
const analysisDir = path.join(__dirname, '../../data/ai_analysis');
if (!fs.existsSync(analysisDir)) {
    fs.mkdirSync(analysisDir, { recursive: true });
}

/**
 * Python AI 서비스 호출 함수
 */
async function callPythonAI(sensorData) {
    return new Promise((resolve, reject) => {
        const pythonScript = path.join(__dirname, '../../services/ai_inference_service.py');
        
        // Python 스크립트 실행
        const python = spawn('python', [pythonScript], {
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        let result = '';
        let error = '';
        
        // 결과 수집
        python.stdout.on('data', (data) => {
            result += data.toString();
        });
        
        python.stderr.on('data', (data) => {
            error += data.toString();
        });
        
        // 입력 데이터 전송
        python.stdin.write(JSON.stringify(sensorData));
        python.stdin.end();
        
        // 완료 처리
        python.on('close', (code) => {
            if (code !== 0) {
                console.error(`Python 스크립트 실행 실패 (코드: ${code}):`, error);
                reject(new Error(`AI 분석 실패: ${error}`));
                return;
            }
            
            try {
                const analysisResult = JSON.parse(result);
                resolve(analysisResult);
            } catch (parseError) {
                console.error('AI 분석 결과 파싱 실패:', parseError);
                reject(new Error('AI 분석 결과 파싱 실패'));
            }
        });
        
        // 타임아웃 설정 (10초)
        setTimeout(() => {
            python.kill();
            reject(new Error('AI 분석 타임아웃'));
        }, 10000);
    });
}

/**
 * 분석 결과 저장
 */
async function saveAnalysisResult(result, deviceId = 'unknown') {
    try {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `analysis_${deviceId}_${timestamp}.json`;
        const filepath = path.join(analysisDir, filename);
        
        const dataToSave = {
            ...result,
            device_id: deviceId,
            saved_at: new Date().toISOString()
        };
        
        fs.writeFileSync(filepath, JSON.stringify(dataToSave, null, 2));
        console.log(`AI 분석 결과 저장: ${filename}`);
        
    } catch (error) {
        console.error('분석 결과 저장 실패:', error);
    }
}

/**
 * 알림 전송 (추후 카카오톡 연동)
 */
async function sendAlert(analysisResult) {
    try {
        const { is_anomaly, anomaly_score, severity, recommendation } = analysisResult;
        
        if (is_anomaly && anomaly_score > 0.6) {
            console.log(`🚨 이상 감지 알림 - 심각도: ${severity}, 점수: ${anomaly_score.toFixed(3)}`);
            console.log(`권장사항: ${recommendation}`);
            
            // TODO: 카카오톡 알림 구현
            // await sendKakaoAlert(analysisResult);
        }
        
    } catch (error) {
        console.error('알림 전송 실패:', error);
    }
}

/**
 * 실시간 AI 분석
 * POST /api/esp32/analyze
 */
router.post('/analyze', async (req, res) => {
    try {
        console.log('ESP32 AI 분석 요청 수신');
        
        const sensorData = req.body;
        const deviceId = req.headers['x-device-id'] || sensorData.device_id || 'unknown';
        
        // 입력 데이터 검증
        if (!sensorData || typeof sensorData !== 'object') {
            return res.status(400).json({
                success: false,
                error: '잘못된 센서 데이터 형식입니다.'
            });
        }
        
        // 필수 필드 확인
        const requiredFields = ['rms_energy', 'decibel_level', 'timestamp'];
        const missingFields = requiredFields.filter(field => !(field in sensorData));
        
        if (missingFields.length > 0) {
            return res.status(400).json({
                success: false,
                error: `필수 필드가 누락되었습니다: ${missingFields.join(', ')}`
            });
        }
        
        console.log(`AI 분석 시작 - 디바이스: ${deviceId}`);
        console.log(`센서 데이터: RMS=${sensorData.rms_energy}, dB=${sensorData.decibel_level}`);
        
        // Python AI 서비스 호출
        const analysisResult = await callPythonAI(sensorData);
        
        if (!analysisResult.success) {
            return res.status(500).json({
                success: false,
                error: analysisResult.error || 'AI 분석 실패'
            });
        }
        
        // 결과 저장
        await saveAnalysisResult(analysisResult, deviceId);
        
        // 이상 감지 시 알림
        if (analysisResult.is_anomaly) {
            await sendAlert(analysisResult);
        }
        
        console.log(`AI 분석 완료 - 이상: ${analysisResult.is_anomaly}, 점수: ${analysisResult.anomaly_score}`);
        
        res.json({
            success: true,
            ...analysisResult,
            device_id: deviceId,
            analyzed_at: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('ESP32 AI 분석 오류:', error);
        res.status(500).json({
            success: false,
            error: 'AI 분석 중 오류가 발생했습니다.',
            details: error.message
        });
    }
});

/**
 * 배치 AI 분석
 * POST /api/esp32/analyze/batch
 */
router.post('/analyze/batch', async (req, res) => {
    try {
        console.log('ESP32 배치 AI 분석 요청 수신');
        
        const { sensor_data_list, device_id } = req.body;
        
        if (!Array.isArray(sensor_data_list) || sensor_data_list.length === 0) {
            return res.status(400).json({
                success: false,
                error: '센서 데이터 리스트가 필요합니다.'
            });
        }
        
        console.log(`배치 분석 시작 - ${sensor_data_list.length}개 데이터`);
        
        // Python AI 서비스 호출 (배치 모드)
        const analysisResults = await callPythonAI({
            mode: 'batch',
            sensor_data_list: sensor_data_list,
            device_id: device_id || 'unknown'
        });
        
        if (!analysisResults.success) {
            return res.status(500).json({
                success: false,
                error: analysisResults.error || '배치 AI 분석 실패'
            });
        }
        
        // 결과 저장
        for (let i = 0; i < analysisResults.results.length; i++) {
            const result = analysisResults.results[i];
            const sensorData = sensor_data_list[i];
            await saveAnalysisResult(result, sensorData.device_id || device_id);
        }
        
        // 이상 감지 통계
        const anomalyCount = analysisResults.results.filter(r => r.is_anomaly).length;
        const avgAnomalyScore = analysisResults.results.reduce((sum, r) => sum + r.anomaly_score, 0) / analysisResults.results.length;
        
        console.log(`배치 분석 완료 - 이상 감지: ${anomalyCount}개, 평균 점수: ${avgAnomalyScore.toFixed(3)}`);
        
        res.json({
            success: true,
            results: analysisResults.results,
            summary: {
                total_samples: analysisResults.results.length,
                anomaly_count: anomalyCount,
                anomaly_rate: anomalyCount / analysisResults.results.length,
                avg_anomaly_score: avgAnomalyScore
            },
            analyzed_at: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('ESP32 배치 AI 분석 오류:', error);
        res.status(500).json({
            success: false,
            error: '배치 AI 분석 중 오류가 발생했습니다.',
            details: error.message
        });
    }
});

/**
 * AI 분석 결과 조회
 * GET /api/esp32/analysis/recent
 */
router.get('/analysis/recent', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 50;
        const deviceId = req.query.device_id;
        const hours = parseInt(req.query.hours) || 24;
        
        console.log(`AI 분석 결과 조회 - 디바이스: ${deviceId}, 제한: ${limit}, 시간: ${hours}시간`);
        
        // 분석 결과 파일들 읽기
        const files = fs.readdirSync(analysisDir)
            .filter(file => file.startsWith('analysis_') && file.endsWith('.json'))
            .map(file => {
                const filepath = path.join(analysisDir, file);
                const stats = fs.statSync(filepath);
                return {
                    filename: file,
                    filepath: filepath,
                    modified: stats.mtime
                };
            })
            .sort((a, b) => b.modified - a.modified)
            .slice(0, limit);
        
        const results = [];
        const cutoffTime = new Date(Date.now() - hours * 60 * 60 * 1000);
        
        for (const file of files) {
            try {
                const content = fs.readFileSync(file.filepath, 'utf8');
                const data = JSON.parse(content);
                
                // 시간 필터링
                const dataTime = new Date(data.analyzed_at || data.saved_at);
                if (dataTime >= cutoffTime) {
                    // 디바이스 ID 필터링
                    if (!deviceId || data.device_id === deviceId) {
                        results.push(data);
                    }
                }
            } catch (err) {
                console.error(`파일 읽기 오류: ${file.filename}`, err);
            }
        }
        
        // 시간순 정렬 (최신이 먼저)
        results.sort((a, b) => new Date(b.analyzed_at || b.saved_at) - new Date(a.analyzed_at || a.saved_at));
        
        res.json({
            success: true,
            data: results,
            count: results.length,
            total: files.length
        });
        
    } catch (error) {
        console.error('AI 분석 결과 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: 'AI 분석 결과 조회 중 오류가 발생했습니다.',
            details: error.message
        });
    }
});

/**
 * AI 모델 상태 조회
 * GET /api/esp32/ai/status
 */
router.get('/ai/status', (req, res) => {
    try {
        // Python AI 서비스 상태 확인
        const pythonScript = path.join(__dirname, '../../services/ai_inference_service.py');
        
        if (!fs.existsSync(pythonScript)) {
            return res.json({
                success: false,
                error: 'AI 서비스가 설치되지 않았습니다.'
            });
        }
        
        // 모델 파일 존재 확인
        const modelDir = path.join(__dirname, '../../data/ai_models');
        const modelFiles = fs.existsSync(modelDir) ? fs.readdirSync(modelDir) : [];
        
        const hasModel = modelFiles.some(file => file.includes('anomaly_detector'));
        const hasScaler = modelFiles.some(file => file.includes('anomaly_scaler'));
        
        res.json({
            success: true,
            ai_service: {
                available: true,
                model_loaded: hasModel && hasScaler,
                model_files: modelFiles
            },
            analysis_results: {
                total_files: fs.existsSync(analysisDir) ? fs.readdirSync(analysisDir).length : 0,
                directory: analysisDir
            }
        });
        
    } catch (error) {
        console.error('AI 상태 조회 오류:', error);
        res.status(500).json({
            success: false,
            error: 'AI 상태 조회 중 오류가 발생했습니다.',
            details: error.message
        });
    }
});

/**
 * AI 모델 재학습
 * POST /api/esp32/ai/retrain
 */
router.post('/ai/retrain', async (req, res) => {
    try {
        console.log('AI 모델 재학습 요청');
        
        const { hours = 24, device_id } = req.body;
        
        // Python 재학습 스크립트 호출
        const pythonScript = path.join(__dirname, '../../services/ai_training_service.py');
        
        if (!fs.existsSync(pythonScript)) {
            return res.status(404).json({
                success: false,
                error: 'AI 재학습 서비스가 설치되지 않았습니다.'
            });
        }
        
        const python = spawn('python', [pythonScript, '--hours', hours.toString()], {
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        let result = '';
        let error = '';
        
        python.stdout.on('data', (data) => {
            result += data.toString();
        });
        
        python.stderr.on('data', (data) => {
            error += data.toString();
        });
        
        python.on('close', (code) => {
            if (code !== 0) {
                console.error(`AI 재학습 실패 (코드: ${code}):`, error);
                return res.status(500).json({
                    success: false,
                    error: `AI 재학습 실패: ${error}`
                });
            }
            
            try {
                const trainingResult = JSON.parse(result);
                res.json({
                    success: true,
                    message: 'AI 모델 재학습 완료',
                    ...trainingResult
                });
            } catch (parseError) {
                res.json({
                    success: true,
                    message: 'AI 모델 재학습 완료',
                    output: result
                });
            }
        });
        
    } catch (error) {
        console.error('AI 재학습 오류:', error);
        res.status(500).json({
            success: false,
            error: 'AI 재학습 중 오류가 발생했습니다.',
            details: error.message
        });
    }
});

module.exports = router;
