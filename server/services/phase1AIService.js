/**
 * Phase 1 AI 서비스
 * 기본 이상 탐지 시스템을 Node.js 서버에 통합
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

class Phase1AIService {
    constructor() {
        this.modelPath = path.join(__dirname, '../../data/models/phase1/');
        this.pythonScriptPath = path.join(__dirname, '../../ai/phase1_basic_anomaly.py');
        this.isInitialized = false;
        this.performanceStats = {
            totalDetections: 0,
            anomalyCount: 0,
            averageProcessingTime: 0,
            accuracy: 0
        };
        
        console.log('🧠 Phase 1 AI 서비스 초기화');
        console.log(`📁 모델 경로: ${this.modelPath}`);
        console.log(`🐍 Python 스크립트: ${this.pythonScriptPath}`);
    }

    /**
     * 정상 데이터로 모델 훈련
     * @param {Array} normalAudioFiles - 정상 오디오 파일 경로 배열
     * @returns {Promise<Object>} 훈련 결과
     */
    async trainOnNormalData(normalAudioFiles) {
        try {
            console.log('🎯 Phase 1: 정상 데이터로 모델 훈련 시작');
            console.log(`📁 정상 오디오 파일 수: ${normalAudioFiles.length}`);

            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--train',
                '--files', JSON.stringify(normalAudioFiles),
                '--output', this.modelPath
            ]);

            let output = '';
            let error = '';

            pythonProcess.stdout.on('data', (data) => {
                output += data.toString();
                console.log(`Python 출력: ${data.toString().trim()}`);
            });

            pythonProcess.stderr.on('data', (data) => {
                error += data.toString();
                console.error(`Python 오류: ${data.toString().trim()}`);
            });

            return new Promise((resolve, reject) => {
                pythonProcess.on('close', (code) => {
                    if (code === 0) {
                        console.log('✅ Phase 1 모델 훈련 완료');
                        this.isInitialized = true;
                        resolve({
                            success: true,
                            message: '모델 훈련 완료',
                            output: output
                        });
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`훈련 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 모델 훈련 오류:', error);
            throw error;
        }
    }

    /**
     * 오디오 데이터 이상 탐지
     * @param {Buffer} audioBuffer - 오디오 데이터 버퍼
     * @param {number} sampleRate - 샘플링 레이트
     * @returns {Promise<Object>} 탐지 결과
     */
    async detectAnomaly(audioBuffer, sampleRate = 16000) {
        if (!this.isInitialized) {
            return {
                isAnomaly: false,
                confidence: 0,
                message: '모델이 초기화되지 않았습니다.',
                anomalyType: 'model_not_initialized',
                processingTimeMs: 0
            };
        }

        try {
            const startTime = Date.now();
            
            // 임시 오디오 파일 생성
            const tempAudioPath = path.join(__dirname, '../../temp_audio.wav');
            await fs.writeFile(tempAudioPath, audioBuffer);

            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--detect',
                '--audio', tempAudioPath,
                '--sample-rate', sampleRate.toString(),
                '--model', this.modelPath
            ]);

            let output = '';
            let error = '';

            pythonProcess.stdout.on('data', (data) => {
                output += data.toString();
            });

            pythonProcess.stderr.on('data', (data) => {
                error += data.toString();
            });

            return new Promise((resolve, reject) => {
                pythonProcess.on('close', (code) => {
                    const processingTime = Date.now() - startTime;
                    
                    // 임시 파일 삭제
                    fs.unlink(tempAudioPath).catch(console.error);

                    if (code === 0) {
                        try {
                            const result = JSON.parse(output);
                            result.processingTimeMs = processingTime;
                            
                            // 성능 통계 업데이트
                            this.updatePerformanceStats(result);
                            
                            resolve(result);
                        } catch (parseError) {
                            console.error('❌ 결과 파싱 오류:', parseError);
                            reject(new Error('결과 파싱 실패'));
                        }
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`탐지 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 이상 탐지 오류:', error);
            return {
                isAnomaly: false,
                confidence: 0,
                message: `분석 중 오류 발생: ${error.message}`,
                anomalyType: 'error',
                processingTimeMs: 0
            };
        }
    }

    /**
     * 성능 통계 업데이트
     * @param {Object} result - 탐지 결과
     */
    updatePerformanceStats(result) {
        this.performanceStats.totalDetections++;
        
        if (result.isAnomaly) {
            this.performanceStats.anomalyCount++;
        }

        // 평균 처리 시간 업데이트
        const total = this.performanceStats.totalDetections;
        const currentAvg = this.performanceStats.averageProcessingTime;
        this.performanceStats.averageProcessingTime = 
            (currentAvg * (total - 1) + result.processingTimeMs) / total;
    }

    /**
     * 성능 통계 조회
     * @returns {Object} 성능 통계
     */
    getPerformanceStats() {
        const stats = { ...this.performanceStats };
        
        if (stats.totalDetections > 0) {
            stats.anomalyRate = stats.anomalyCount / stats.totalDetections;
        } else {
            stats.anomalyRate = 0;
        }

        stats.phase = 'Phase 1';
        stats.initialized = this.isInitialized;
        stats.lastUpdate = new Date().toISOString();

        return stats;
    }

    /**
     * 모델 상태 확인
     * @returns {Object} 모델 상태
     */
    getModelStatus() {
        return {
            initialized: this.isInitialized,
            modelPath: this.modelPath,
            pythonScriptPath: this.pythonScriptPath,
            performanceStats: this.getPerformanceStats()
        };
    }

    /**
     * 모델 초기화 상태 설정
     * @param {boolean} initialized - 초기화 상태
     */
    setInitialized(initialized) {
        this.isInitialized = initialized;
        console.log(`🔄 모델 초기화 상태: ${initialized ? '완료' : '미완료'}`);
    }

    /**
     * 성능 통계 리셋
     */
    resetPerformanceStats() {
        this.performanceStats = {
            totalDetections: 0,
            anomalyCount: 0,
            averageProcessingTime: 0,
            accuracy: 0
        };
        console.log('🔄 성능 통계 리셋 완료');
    }
}

module.exports = Phase1AIService;
