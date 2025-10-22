/**
 * Phase 3 통합 AI 서비스
 * 모든 AI 컴포넌트를 통합한 최종 시스템을 Node.js 서버에 통합
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;
const Phase1AIService = require('./phase1AIService');
const Phase2AdaptiveService = require('./phase2AdaptiveService');

class Phase3IntegratedService {
    constructor() {
        this.modelPath = path.join(__dirname, '../../data/models/phase3/');
        this.pythonScriptPath = path.join(__dirname, '../../ai/phase3_integrated_system.py');
        this.phase1Service = new Phase1AIService();
        this.phase2Service = new Phase2AdaptiveService();
        this.isInitialized = false;
        
        // 통합 시스템 파라미터
        this.integrationParams = {
            phase1Weight: 0.3,
            phase2Weight: 0.4,
            integratedWeight: 0.3,
            consensusThreshold: 0.6,
            confidenceThreshold: 0.7,
            reliabilityThreshold: 0.8
        };
        
        // 통합 성능 지표
        this.integratedMetrics = {
            totalDetections: 0,
            anomalyCount: 0,
            falsePositives: 0,
            falseNegatives: 0,
            averageProcessingTime: 0,
            accuracy: 0.0,
            precision: 0.0,
            recall: 0.0,
            f1Score: 0.0,
            systemReliability: 0.0,
            consensusRate: 0.0,
            lastUpdate: null
        };
        
        // 시스템 상태
        this.systemStatus = {
            phase1Ready: false,
            phase2Ready: false,
            integratedReady: false,
            overallReady: false,
            lastHealthCheck: null
        };
        
        // 모니터링 데이터
        this.monitoringData = {
            detectionHistory: [],
            performanceHistory: [],
            systemHealth: [],
            alertHistory: []
        };
        
        // 알림 시스템
        this.alertSystem = {
            enabled: true,
            thresholds: {
                accuracyDrop: 0.1,
                processingTimeIncrease: 2.0,
                anomalyRateSpike: 0.3,
                systemErrorRate: 0.05
            },
            notificationChannels: ['console', 'log', 'api']
        };
        
        console.log('🎯 Phase 3 통합 AI 서비스 초기화');
        console.log(`📁 모델 경로: ${this.modelPath}`);
        console.log(`🐍 Python 스크립트: ${this.pythonScriptPath}`);
        console.log(`🔧 통합 파라미터:`, this.integrationParams);
    }

    /**
     * Phase 1, 2 시스템으로 초기화
     */
    async initializeWithPhases() {
        try {
            console.log('🎯 Phase 1, 2 시스템으로 Phase 3 초기화 중...');
            
            // Phase 1 상태 확인
            const phase1Status = this.phase1Service.getModelStatus();
            this.systemStatus.phase1Ready = phase1Status.initialized;
            
            // Phase 2 상태 확인
            const phase2Status = this.phase2Service.getAdaptiveStatus();
            this.systemStatus.phase2Ready = phase2Status.initialized;
            
            if (!this.systemStatus.phase1Ready || !this.systemStatus.phase2Ready) {
                throw new Error('Phase 1 또는 Phase 2 시스템이 초기화되지 않았습니다.');
            }
            
            // Phase 3 Python 스크립트로 초기화
            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--initialize',
                '--phase1-model', path.join(this.phase1Service.modelPath, 'phase1_anomaly_detector.pkl'),
                '--phase2-model', path.join(this.phase2Service.modelPath, 'phase2_adaptive_system.pkl'),
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
                        console.log('✅ Phase 3 통합 시스템 초기화 완료');
                        this.systemStatus.integratedReady = true;
                        this.systemStatus.overallReady = true;
                        this.isInitialized = true;
                        this.updateSystemStatus();
                        resolve({
                            success: true,
                            message: 'Phase 3 통합 시스템 초기화 완료',
                            output: output
                        });
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`Phase 3 초기화 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ Phase 3 초기화 오류:', error);
            throw error;
        }
    }

    /**
     * 통합 이상 탐지 수행
     */
    async detectAnomalyIntegrated(audioBuffer, sampleRate = 16000, groundTruth = null) {
        if (!this.isInitialized) {
            return {
                isAnomaly: false,
                confidence: 0,
                message: 'Phase 3 시스템이 초기화되지 않았습니다.',
                anomalyType: 'system_not_initialized',
                processingTimeMs: 0,
                phase: 'Phase 3'
            };
        }

        try {
            const startTime = Date.now();
            
            // 임시 오디오 파일 생성
            const tempAudioPath = path.join(__dirname, '../../temp_audio_phase3.wav');
            await fs.writeFile(tempAudioPath, audioBuffer);

            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--detect-integrated',
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
                            this.updateIntegratedMetrics(result, groundTruth, processingTime);
                            
                            // 모니터링 데이터 업데이트
                            this.updateMonitoringData(result, groundTruth, processingTime);
                            
                            // 알림 조건 체크
                            this.checkAlertConditions();
                            
                            resolve(result);
                        } catch (parseError) {
                            console.error('❌ 결과 파싱 오류:', parseError);
                            reject(new Error('결과 파싱 실패'));
                        }
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`통합 탐지 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 통합 이상 탐지 오류:', error);
            return {
                isAnomaly: false,
                confidence: 0,
                message: `통합 분석 중 오류 발생: ${error.message}`,
                anomalyType: 'error',
                processingTimeMs: 0,
                phase: 'Phase 3'
            };
        }
    }

    /**
     * 통합 파라미터 업데이트
     */
    async updateIntegrationParams(params) {
        try {
            console.log('🔄 통합 파라미터 업데이트 중...');
            
            // 파라미터 검증
            const validParams = {};
            for (const [key, value] of Object.entries(params)) {
                if (key in this.integrationParams) {
                    if (key.includes('Weight') && value >= 0 && value <= 1) {
                        validParams[key] = value;
                    } else if (key.includes('Threshold') && value >= 0 && value <= 1) {
                        validParams[key] = value;
                    }
                }
            }
            
            // 파라미터 업데이트
            Object.assign(this.integrationParams, validParams);
            
            // Python 스크립트로 파라미터 전달
            const pythonProcess = spawn('python', [
                this.pythonScriptPath,
                '--update-integration-params',
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
                        console.log('✅ 통합 파라미터 업데이트 완료');
                        resolve({
                            success: true,
                            message: '통합 파라미터 업데이트 완료',
                            updatedParams: validParams
                        });
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`파라미터 업데이트 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 통합 파라미터 업데이트 오류:', error);
            throw error;
        }
    }

    /**
     * 시스템 상태 업데이트
     */
    updateSystemStatus() {
        this.systemStatus.overallReady = (
            this.systemStatus.phase1Ready && 
            this.systemStatus.phase2Ready && 
            this.systemStatus.integratedReady
        );
        this.systemStatus.lastHealthCheck = new Date().toISOString();
    }

    /**
     * 통합 성능 지표 업데이트
     */
    updateIntegratedMetrics(result, groundTruth, processingTime) {
        this.integratedMetrics.totalDetections++;
        
        if (result.isAnomaly) {
            this.integratedMetrics.anomalyCount++;
        }

        // 정확도 계산
        if (groundTruth !== null) {
            const predicted = result.isAnomaly;
            if (predicted && !groundTruth) {
                this.integratedMetrics.falsePositives++;
            } else if (!predicted && groundTruth) {
                this.integratedMetrics.falseNegatives++;
            }
            
            // 정확도, 정밀도, 재현율 계산
            const total = this.integratedMetrics.totalDetections;
            const correct = total - (this.integratedMetrics.falsePositives + 
                                   this.integratedMetrics.falseNegatives);
            
            this.integratedMetrics.accuracy = correct / total;
            
            // 정밀도
            const tp = this.integratedMetrics.anomalyCount - this.integratedMetrics.falsePositives;
            this.integratedMetrics.precision = tp / this.integratedMetrics.anomalyCount || 0;
            
            // 재현율
            const fn = this.integratedMetrics.falseNegatives;
            this.integratedMetrics.recall = tp / (tp + fn) || 0;
            
            // F1 점수
            const precision = this.integratedMetrics.precision;
            const recall = this.integratedMetrics.recall;
            this.integratedMetrics.f1Score = 2 * (precision * recall) / (precision + recall) || 0;
        }

        // 평균 처리 시간 업데이트
        const total = this.integratedMetrics.totalDetections;
        const currentAvg = this.integratedMetrics.averageProcessingTime;
        this.integratedMetrics.averageProcessingTime = 
            (currentAvg * (total - 1) + processingTime) / total;
        
        // 시스템 신뢰성 업데이트
        this.integratedMetrics.systemReliability = result.reliability || 0.0;
        
        // 합의율 업데이트
        const consensusInfo = result.consensusInfo || {};
        this.integratedMetrics.consensusRate = consensusInfo.consensusRate || 0.0;
        
        this.integratedMetrics.lastUpdate = new Date().toISOString();
    }

    /**
     * 모니터링 데이터 업데이트
     */
    updateMonitoringData(result, groundTruth, processingTime) {
        // 탐지 히스토리
        const detectionRecord = {
            timestamp: new Date().toISOString(),
            isAnomaly: result.isAnomaly,
            confidence: result.confidence,
            anomalyType: result.anomalyType,
            reliability: result.reliability || 0.0,
            processingTime: processingTime,
            groundTruth: groundTruth
        };
        this.monitoringData.detectionHistory.push(detectionRecord);
        
        // 최대 1000개 유지
        if (this.monitoringData.detectionHistory.length > 1000) {
            this.monitoringData.detectionHistory.shift();
        }
        
        // 성능 히스토리
        const performanceRecord = {
            timestamp: new Date().toISOString(),
            accuracy: this.integratedMetrics.accuracy,
            processingTime: processingTime,
            anomalyRate: this.integratedMetrics.anomalyCount / Math.max(1, this.integratedMetrics.totalDetections)
        };
        this.monitoringData.performanceHistory.push(performanceRecord);
        
        // 최대 100개 유지
        if (this.monitoringData.performanceHistory.length > 100) {
            this.monitoringData.performanceHistory.shift();
        }
        
        // 시스템 건강 상태
        const healthRecord = {
            timestamp: new Date().toISOString(),
            phase1Ready: this.systemStatus.phase1Ready,
            phase2Ready: this.systemStatus.phase2Ready,
            integratedReady: this.systemStatus.integratedReady,
            overallReady: this.systemStatus.overallReady,
            reliability: result.reliability || 0.0
        };
        this.monitoringData.systemHealth.push(healthRecord);
        
        // 최대 50개 유지
        if (this.monitoringData.systemHealth.length > 50) {
            this.monitoringData.systemHealth.shift();
        }
    }

    /**
     * 알림 조건 체크
     */
    checkAlertConditions() {
        if (!this.alertSystem.enabled) {
            return;
        }
        
        const alerts = [];
        const thresholds = this.alertSystem.thresholds;
        
        // 정확도 하락 체크
        if (this.monitoringData.performanceHistory.length >= 10) {
            const recentAccuracy = this.monitoringData.performanceHistory
                .slice(-10)
                .reduce((sum, p) => sum + p.accuracy, 0) / 10;
            
            if (recentAccuracy < (this.integratedMetrics.accuracy - thresholds.accuracyDrop)) {
                alerts.push({
                    type: 'accuracy_drop',
                    message: `정확도 하락 감지: ${(recentAccuracy * 100).toFixed(1)}%`,
                    severity: 'warning'
                });
            }
        }
        
        // 처리 시간 증가 체크
        if (this.monitoringData.performanceHistory.length >= 5) {
            const recentProcessingTime = this.monitoringData.performanceHistory
                .slice(-5)
                .reduce((sum, p) => sum + p.processingTime, 0) / 5;
            
            if (recentProcessingTime > (this.integratedMetrics.averageProcessingTime * thresholds.processingTimeIncrease)) {
                alerts.push({
                    type: 'processing_time_increase',
                    message: `처리 시간 증가 감지: ${recentProcessingTime.toFixed(1)}ms`,
                    severity: 'warning'
                });
            }
        }
        
        // 이상 탐지율 급증 체크
        if (this.monitoringData.detectionHistory.length >= 20) {
            const recentAnomalyRate = this.monitoringData.detectionHistory
                .slice(-20)
                .filter(d => d.isAnomaly).length / 20;
            
            if (recentAnomalyRate > thresholds.anomalyRateSpike) {
                alerts.push({
                    type: 'anomaly_rate_spike',
                    message: `이상 탐지율 급증: ${(recentAnomalyRate * 100).toFixed(1)}%`,
                    severity: 'critical'
                });
            }
        }
        
        // 알림 처리
        alerts.forEach(alert => this.processAlert(alert));
    }

    /**
     * 알림 처리
     */
    processAlert(alert) {
        alert.timestamp = new Date().toISOString();
        this.monitoringData.alertHistory.push(alert);
        
        // 최대 100개 유지
        if (this.monitoringData.alertHistory.length > 100) {
            this.monitoringData.alertHistory.shift();
        }
        
        // 콘솔 출력
        if (this.alertSystem.notificationChannels.includes('console')) {
            console.log(`🚨 알림: ${alert.message} (심각도: ${alert.severity})`);
        }
        
        // 로그 파일 (향후 구현)
        if (this.alertSystem.notificationChannels.includes('log')) {
            // 로그 파일에 기록
        }
        
        // API 알림 (향후 구현)
        if (this.alertSystem.notificationChannels.includes('api')) {
            // 외부 API로 알림 전송
        }
    }

    /**
     * 통합 성능 통계 조회
     */
    getIntegratedStats() {
        const stats = { ...this.integratedMetrics };
        
        if (stats.totalDetections > 0) {
            stats.anomalyRate = stats.anomalyCount / stats.totalDetections;
        } else {
            stats.anomalyRate = 0.0;
        }
        
        // 추가 통계
        stats.phase = 'Phase 3';
        stats.systemStatus = this.systemStatus;
        stats.integrationParams = this.integrationParams;
        stats.monitoringDataSize = {
            detectionHistory: this.monitoringData.detectionHistory.length,
            performanceHistory: this.monitoringData.performanceHistory.length,
            systemHealth: this.monitoringData.systemHealth.length,
            alertHistory: this.monitoringData.alertHistory.length
        };
        stats.lastUpdate = new Date().toISOString();
        
        return stats;
    }

    /**
     * 모니터링 데이터 조회
     */
    getMonitoringData(limit = 100) {
        return {
            detectionHistory: this.monitoringData.detectionHistory.slice(-limit),
            performanceHistory: this.monitoringData.performanceHistory.slice(-limit),
            systemHealth: this.monitoringData.systemHealth.slice(-limit),
            alertHistory: this.monitoringData.alertHistory.slice(-limit)
        };
    }

    /**
     * 통합 시스템 상태 조회
     */
    getIntegratedStatus() {
        return {
            initialized: this.isInitialized,
            modelPath: this.modelPath,
            pythonScriptPath: this.pythonScriptPath,
            phase1Service: this.phase1Service.getModelStatus(),
            phase2Service: this.phase2Service.getAdaptiveStatus(),
            systemStatus: this.systemStatus,
            integratedMetrics: this.integratedMetrics,
            integrationParams: this.integrationParams,
            alertSystem: this.alertSystem
        };
    }

    /**
     * 통합 시스템 저장
     */
    async saveIntegratedSystem() {
        try {
            console.log('💾 통합 시스템 저장 중...');
            
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
                        console.log('✅ 통합 시스템 저장 완료');
                        resolve({
                            success: true,
                            message: '통합 시스템 저장 완료',
                            output: output
                        });
                    } else {
                        console.error(`❌ Python 프로세스 종료 코드: ${code}`);
                        reject(new Error(`시스템 저장 실패: ${error}`));
                    }
                });
            });

        } catch (error) {
            console.error('❌ 통합 시스템 저장 오류:', error);
            throw error;
        }
    }
}

module.exports = Phase3IntegratedService;
