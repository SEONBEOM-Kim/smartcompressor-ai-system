/**
 * 경량화된 3순위 조합 서비스
 * 10-15개 하드웨어로 딥러닝 + 다중 센서 융합 + 실시간 적응형 학습 구현
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

class Lightweight3TierService {
    constructor(hardwareCount = 10) {
        this.serviceName = 'Lightweight3TierService';
        this.hardwareCount = hardwareCount;
        this.pythonScript = path.join(__dirname, '../../ai/lightweight_3tier_system.py');
        this.isInitialized = false;
        this.models = {};
        this.sensors = {};
        this.learningSystems = {};
        this.performanceMetrics = {};
        
        console.log(`🚀 ${this.serviceName} 초기화 완료 (하드웨어 수: ${hardwareCount})`);
    }

    /**
     * 통합 3순위 조합 시스템 실행
     */
    async runIntegrated3TierSystem(audioFiles, labels) {
        try {
            console.log('🚀 통합 3순위 조합 시스템 시작');
            
            const result = await this._executePythonScript('integrated_3tier_system', {
                audio_files: audioFiles,
                labels: labels,
                hardware_count: this.hardwareCount
            });
            
            if (result.success) {
                this.isInitialized = true;
                this.models = result.models || {};
                this.sensors = result.sensors || {};
                this.learningSystems = result.learning_systems || {};
                this.performanceMetrics = result.performance_metrics || {};
                
                console.log(`✅ 통합 3순위 조합 시스템 완료!`);
                console.log(`   최종 정확도: ${result.final_accuracy?.toFixed(3)}`);
                console.log(`   딥러닝 정확도: ${result.dl_accuracy?.toFixed(3)}`);
                console.log(`   센서 융합 성공: ${result.sensor_success}`);
                console.log(`   적응형 학습 성공률: ${result.adaptive_success_rate?.toFixed(3)}`);
            }
            
            return result;
            
        } catch (error) {
            console.error(`❌ 통합 3순위 조합 시스템 오류:`, error);
            return {
                success: false,
                error: error.message,
                hardware_count: this.hardwareCount
            };
        }
    }

    /**
     * 경량화된 딥러닝 모델 훈련
     */
    async trainLightweightModels(features, labels) {
        try {
            console.log('🧠 경량화된 딥러닝 모델 훈련 시작');
            
            const result = await this._executePythonScript('train_lightweight_models', {
                features: features,
                labels: labels,
                hardware_count: this.hardwareCount
            });
            
            if (result.success) {
                this.models = result.models || {};
                console.log(`✅ 딥러닝 모델 훈련 완료! 평균 정확도: ${result.overall_accuracy?.toFixed(3)}`);
            }
            
            return result;
            
        } catch (error) {
            console.error(`❌ 딥러닝 모델 훈련 오류:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 다중 센서 융합
     */
    async multiSensorFusion(audioData, sampleRate = 16000) {
        try {
            console.log('🔍 다중 센서 융합 시작');
            
            const result = await this._executePythonScript('multi_sensor_fusion', {
                audio_data: audioData,
                sample_rate: sampleRate,
                hardware_count: this.hardwareCount
            });
            
            if (result.success) {
                console.log(`✅ 다중 센서 융합 완료! 융합된 특징 수: ${result.fused_features?.length || 0}`);
            }
            
            return result;
            
        } catch (error) {
            console.error(`❌ 다중 센서 융합 오류:`, error);
            return {
                success: false,
                error: error.message,
                fused_features: []
            };
        }
    }

    /**
     * 실시간 적응형 학습
     */
    async adaptiveLearning(audioData, groundTruth, hardwareId = 0) {
        try {
            const result = await this._executePythonScript('adaptive_learning', {
                audio_data: audioData,
                ground_truth: groundTruth,
                hardware_id: hardwareId,
                hardware_count: this.hardwareCount
            });
            
            return result;
            
        } catch (error) {
            console.error(`❌ 적응형 학습 오류:`, error);
            return {
                success: false,
                error: error.message,
                prediction: 0,
                confidence: 0.0
            };
        }
    }

    /**
     * 하드웨어 사양 확인
     */
    async checkHardwareSpecs() {
        try {
            const result = await this._executePythonScript('check_hardware_specs');
            return result;
            
        } catch (error) {
            console.error(`❌ 하드웨어 사양 확인 오류:`, error);
            return {
                success: false,
                error: error.message,
                specs: {
                    cpu_cores: 4,
                    ram_gb: 8,
                    disk_gb: 50,
                    gpu_available: false,
                    network_mbps: 100
                }
            };
        }
    }

    /**
     * 성능 메트릭 조회
     */
    async getPerformanceMetrics() {
        try {
            const result = await this._executePythonScript('get_performance_metrics');
            return result;
            
        } catch (error) {
            console.error(`❌ 성능 메트릭 조회 오류:`, error);
            return {
                success: false,
                error: error.message,
                metrics: {}
            };
        }
    }

    /**
     * 시스템 상태 조회
     */
    async getSystemStatus() {
        try {
            const hardwareSpecs = await this.checkHardwareSpecs();
            const performanceMetrics = await this.getPerformanceMetrics();
            
            return {
                service_name: this.serviceName,
                is_initialized: this.isInitialized,
                hardware_count: this.hardwareCount,
                hardware_specs: hardwareSpecs.specs || {},
                performance_metrics: performanceMetrics.metrics || {},
                models_count: Object.keys(this.models).length,
                sensors_count: Object.keys(this.sensors).length,
                learning_systems_count: Object.keys(this.learningSystems).length,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error(`❌ 시스템 상태 조회 오류:`, error);
            return {
                service_name: this.serviceName,
                is_initialized: false,
                hardware_count: this.hardwareCount,
                hardware_specs: {},
                performance_metrics: {},
                models_count: 0,
                sensors_count: 0,
                learning_systems_count: 0,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * 모델 리셋
     */
    async resetModels() {
        try {
            this.models = {};
            this.sensors = {};
            this.learningSystems = {};
            this.isInitialized = false;
            this.performanceMetrics = {};
            
            console.log('🔄 경량화된 3순위 조합 모델 리셋 완료');
            
            return {
                success: true,
                message: '모델이 리셋되었습니다.'
            };
            
        } catch (error) {
            console.error(`❌ 모델 리셋 오류:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 배치 처리
     */
    async batchProcess(audioFiles, labels, batchSize = 5) {
        try {
            console.log(`🔄 배치 처리 시작 (배치 크기: ${batchSize})`);
            
            const results = [];
            const totalBatches = Math.ceil(audioFiles.length / batchSize);
            
            for (let i = 0; i < totalBatches; i++) {
                const start = i * batchSize;
                const end = Math.min(start + batchSize, audioFiles.length);
                const batchFiles = audioFiles.slice(start, end);
                const batchLabels = labels.slice(start, end);
                
                console.log(`   배치 ${i + 1}/${totalBatches} 처리 중...`);
                
                const batchResult = await this.runIntegrated3TierSystem(batchFiles, batchLabels);
                results.push(batchResult);
                
                // 배치 간 잠시 대기 (시스템 부하 방지)
                if (i < totalBatches - 1) {
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
            }
            
            console.log('✅ 배치 처리 완료');
            
            return {
                success: true,
                total_batches: totalBatches,
                results: results
            };
            
        } catch (error) {
            console.error(`❌ 배치 처리 오류:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 하드웨어별 성능 분석
     */
    async analyzeHardwarePerformance() {
        try {
            const result = await this._executePythonScript('analyze_hardware_performance');
            return result;
            
        } catch (error) {
            console.error(`❌ 하드웨어 성능 분석 오류:`, error);
            return {
                success: false,
                error: error.message,
                analysis: {}
            };
        }
    }

    /**
     * 시스템 최적화
     */
    async optimizeSystem() {
        try {
            console.log('⚡ 시스템 최적화 시작');
            
            const result = await this._executePythonScript('optimize_system', {
                hardware_count: this.hardwareCount
            });
            
            if (result.success) {
                console.log('✅ 시스템 최적화 완료');
            }
            
            return result;
            
        } catch (error) {
            console.error(`❌ 시스템 최적화 오류:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Python 스크립트 실행
     */
    async _executePythonScript(functionName, params = {}) {
        return new Promise((resolve, reject) => {
            try {
                const pythonProcess = spawn('python', [
                    this.pythonScript,
                    '--function', functionName,
                    '--params', JSON.stringify(params)
                ]);

                let stdout = '';
                let stderr = '';

                pythonProcess.stdout.on('data', (data) => {
                    stdout += data.toString();
                });

                pythonProcess.stderr.on('data', (data) => {
                    stderr += data.toString();
                });

                pythonProcess.on('close', (code) => {
                    if (code === 0) {
                        try {
                            const result = JSON.parse(stdout);
                            resolve(result);
                        } catch (parseError) {
                            console.error('Python 출력 파싱 오류:', parseError);
                            console.error('원본 출력:', stdout);
                            reject(new Error('Python 출력 파싱 실패'));
                        }
                    } else {
                        console.error('Python 스크립트 실행 오류:', stderr);
                        reject(new Error(`Python 스크립트 실행 실패 (코드: ${code})`));
                    }
                });

                pythonProcess.on('error', (error) => {
                    console.error('Python 프로세스 오류:', error);
                    reject(error);
                });

            } catch (error) {
                console.error('Python 스크립트 실행 중 오류:', error);
                reject(error);
            }
        });
    }

    /**
     * 오디오 파일 검증
     */
    async validateAudioFile(filePath) {
        try {
            await fs.access(filePath);
            const stats = await fs.stat(filePath);
            
            if (stats.size === 0) {
                return {
                    valid: false,
                    error: '파일이 비어있습니다.'
                };
            }
            
            if (stats.size > 50 * 1024 * 1024) { // 50MB 제한 (경량화)
                return {
                    valid: false,
                    error: '파일 크기가 너무 큽니다. (50MB 제한)'
                };
            }
            
            return {
                valid: true,
                size: stats.size
            };
            
        } catch (error) {
            return {
                valid: false,
                error: `파일 접근 오류: ${error.message}`
            };
        }
    }

    /**
     * 하드웨어 수 조정
     */
    async adjustHardwareCount(newCount) {
        try {
            if (newCount < 1 || newCount > 50) {
                throw new Error('하드웨어 수는 1-50 사이여야 합니다.');
            }
            
            this.hardwareCount = newCount;
            
            // 모델 리셋
            await this.resetModels();
            
            console.log(`✅ 하드웨어 수 조정 완료: ${newCount}`);
            
            return {
                success: true,
                message: `하드웨어 수가 ${newCount}개로 조정되었습니다.`,
                hardware_count: this.hardwareCount
            };
            
        } catch (error) {
            console.error(`❌ 하드웨어 수 조정 오류:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

module.exports = Lightweight3TierService;
