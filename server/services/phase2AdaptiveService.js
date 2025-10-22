/**
 * Phase 2 적응형 AI 서비스
 * 환경 변화에 자동으로 적응하는 AI 시스템을 Node.js 서버에 통합
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const Phase1AIService = require('./phase1AIService');

class Phase2AdaptiveService {
    constructor() {
        this.modelPath = path.join(__dirname, '../../data/models/phase2/');
        this.pythonScriptPath = path.join(__dirname, '../../ai/phase2_adaptive_system.py');
        this.phase1Service = new Phase1AIService();
        this.isInitialized = false;
        
        // 적응형 통계
        this.adaptiveStats = {
            totalAdaptations: 0,
            lastAdaptation: null,
            adaptationEffectiveness: 0.0,
            thresholdUpdates: 0,
            modelUpdates: 0
        };
        
        // 성능 지표
        this.performanceMetrics = {
            totalDetections: 0,
            anomalyCount: 0,
            falsePositives: 0,
            falseNegatives: 0,
            averageProcessingTime: 0,
            accuracy: 0.0,
            adaptationAccuracy: 0.0,
            lastUpdate: null
        };
        
        // 적응형 파라미터
        this.adaptationParams = {
            sensitivity: 0.1,
            learningRate: 0.01,
            confidenceThreshold: 0.7,
            anomalyThreshold: 0.05,
            adaptationThreshold: 0.1
        };
        
        console.log('🔄 Phase 2 적응형 AI 서비스 초기화');
        console.log(`📁 모델 경로: ${this.modelPath}`);
        console.log(`🐍 Python 스크립트: ${this.pythonScriptPath}`);
    }

    /**
     * Phase 1 시스템으로 초기화
     */
    async initializeWithPhase1() {
        try {
            console.log('🔄 Phase 1 시스템으로 Phase 2 초기화 중...');
            
            // Phase 1 시스템 상태 확인
            const phase1Status = this.phase1Service.getModelStatus();
            if (!phase1Status.initialized) {
                throw new Error('Phase 1 시스템이 초기화되지 않았습니다.');
            }
            
            // Phase 2 Python 스크립트로 초기화
            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--initialize',
                '--phase1-model', path.join(this.phase1Service.modelPath, 'phase1_anomaly_detector.pkl'),
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
                        console.log('✅ Phase 2 적응형 시스템 초기화 완료');
                        this.isInitialized = true;
                        resolve({
                            success: true,
                            message: 'Phase 2 적응형 시스템 초기화 완료',
                            output: output
                        });
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`Phase 2 초기화 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ Phase 2 초기화 오류:', error);
            throw error;
        }
    }

    /**
     * 적응형 이상 탐지 수행
     */
    async detectAnomalyAdaptive(audioBuffer, sampleRate = 16000, groundTruth = null) {
        if (!this.isInitialized) {
            return {
                isAnomaly: false,
                confidence: 0,
                message: 'Phase 2 시스템이 초기화되지 않았습니다.',
                anomalyType: 'system_not_initialized',
                processingTimeMs: 0,
                phase: 'Phase 2'
            };
        }

        try {
            const startTime = Date.now();
            
            // 임시 오디오 파일 생성
            const tempAudioPath = path.join(__dirname, '../../temp_audio_phase2.wav');
            await fs.writeFile(tempAudioPath, audioBuffer);

            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--detect-adaptive',
                '--audio', tempAudioPath,
                '--sample-rate', sampleRate.toString(),
                '--model', this.modelPath,
                '--ground-truth', groundTruth ? 'true' : 'false'
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
                            this.updatePerformanceMetrics(result, groundTruth, processingTime);
                            
                            resolve(result);
                        } catch (parseError) {
                            console.error('❌ 결과 파싱 오류:', parseError);
                            reject(new Error('결과 파싱 실패'));
                        }
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`적응형 탐지 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 적응형 이상 탐지 오류:', error);
            return {
                isAnomaly: false,
                confidence: 0,
                message: `적응형 분석 중 오류 발생: ${error.message}`,
                anomalyType: 'error',
                processingTimeMs: 0,
                phase: 'Phase 2'
            };
        }
    }

    /**
     * 적응형 파라미터 업데이트
     */
    async updateAdaptationParams(params) {
        try {
            console.log('🔄 적응형 파라미터 업데이트 중...');
            
            // 파라미터 검증
            const validParams = {};
            for (const [key, value] of Object.entries(params)) {
                if (key in this.adaptationParams) {
                    if (key === 'sensitivity' && value >= 0 && value <= 1) {
                        validParams[key] = value;
                    } else if (key === 'learningRate' && value > 0 && value <= 1) {
                        validParams[key] = value;
                    } else if (key === 'confidenceThreshold' && value >= 0 && value <= 1) {
                        validParams[key] = value;
                    } else if (key === 'anomalyThreshold' && value >= 0 && value <= 1) {
                        validParams[key] = value;
                    } else if (key === 'adaptationThreshold' && value >= 0 && value <= 1) {
                        validParams[key] = value;
                    }
                }
            }
            
            // 파라미터 업데이트
            Object.assign(this.adaptationParams, validParams);
            
            // Python 스크립트로 파라미터 전달
            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--update-params',
                '--params', JSON.stringify(validParams),
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
                    if (code === 0) {
                        console.log('✅ 적응형 파라미터 업데이트 완료');
                        resolve({
                            success: true,
                            message: '적응형 파라미터 업데이트 완료',
                            updatedParams: validParams
                        });
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`파라미터 업데이트 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 적응형 파라미터 업데이트 오류:', error);
            throw error;
        }
    }

    /**
     * 강제 적응형 업데이트 수행
     */
    async forceAdaptiveUpdate() {
        try {
            console.log('🔄 강제 적응형 업데이트 수행 중...');
            
            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--force-update',
                '--model', this.modelPath
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
                        console.log('✅ 강제 적응형 업데이트 완료');
                        this.adaptiveStats.totalAdaptations++;
                        this.adaptiveStats.lastAdaptation = new Date().toISOString();
                        resolve({
                            success: true,
                            message: '강제 적응형 업데이트 완료',
                            output: output
                        });
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`강제 업데이트 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 강제 적응형 업데이트 오류:', error);
            throw error;
        }
    }

    /**
     * 성능 통계 업데이트
     */
    updatePerformanceMetrics(result, groundTruth, processingTime) {
        this.performanceMetrics.totalDetections++;
        
        if (result.isAnomaly) {
            this.performanceMetrics.anomalyCount++;
        }

        // 정확도 계산
        if (groundTruth !== null) {
            const predicted = result.isAnomaly;
            if (predicted && !groundTruth) {
                this.performanceMetrics.falsePositives++;
            } else if (!predicted && groundTruth) {
                this.performanceMetrics.falseNegatives++;
            }
            
            // 정확도 업데이트
            const total = this.performanceMetrics.totalDetections;
            const correct = total - (this.performanceMetrics.falsePositives + 
                                   this.performanceMetrics.falseNegatives);
            this.performanceMetrics.accuracy = correct / total;
        }

        // 평균 처리 시간 업데이트
        const total = this.performanceMetrics.totalDetections;
        const currentAvg = this.performanceMetrics.averageProcessingTime;
        this.performanceMetrics.averageProcessingTime = 
            (currentAvg * (total - 1) + processingTime) / total;
        
        this.performanceMetrics.lastUpdate = new Date().toISOString();
    }

    /**
     * 적응형 통계 조회
     */
    getAdaptiveStats() {
        const stats = { ...this.performanceMetrics };
        
        if (stats.totalDetections > 0) {
            stats.anomalyRate = stats.anomalyCount / stats.totalDetections;
        } else {
            stats.anomalyRate = 0.0;
        }

        // 적응형 통계 추가
        stats.phase = 'Phase 2';
        stats.adaptiveStats = this.adaptiveStats;
        stats.adaptationParams = this.adaptationParams;
        stats.initialized = this.isInitialized;
        stats.lastUpdate = new Date().toISOString();

        return stats;
    }

    /**
     * 적응형 시스템 상태 조회
     */
    getAdaptiveStatus() {
        return {
            initialized: this.isInitialized,
            modelPath: this.modelPath,
            pythonScriptPath: this.pythonScriptPath,
            phase1Service: this.phase1Service.getModelStatus(),
            adaptiveStats: this.adaptiveStats,
            performanceMetrics: this.performanceMetrics,
            adaptationParams: this.adaptationParams
        };
    }

    /**
     * 적응형 통계 리셋
     */
    resetAdaptiveStats() {
        this.adaptiveStats = {
            totalAdaptations: 0,
            lastAdaptation: null,
            adaptationEffectiveness: 0.0,
            thresholdUpdates: 0,
            modelUpdates: 0
        };
        
        this.performanceMetrics = {
            totalDetections: 0,
            anomalyCount: 0,
            falsePositives: 0,
            falseNegatives: 0,
            averageProcessingTime: 0,
            accuracy: 0.0,
            adaptationAccuracy: 0.0,
            lastUpdate: null
        };
        
        console.log('🔄 적응형 통계 리셋 완료');
    }

    /**
     * 적응형 시스템 저장
     */
    async saveAdaptiveSystem() {
        try {
            console.log('💾 적응형 시스템 저장 중...');
            
            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--save',
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
                    if (code === 0) {
                        console.log('✅ 적응형 시스템 저장 완료');
                        resolve({
                            success: true,
                            message: '적응형 시스템 저장 완료',
                            output: output
                        });
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`시스템 저장 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 적응형 시스템 저장 오류:', error);
            throw error;
        }
    }
}

module.exports = Phase2AdaptiveService;
