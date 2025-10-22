/**
 * 안전한 GPU 준비 서비스
 * GPU 없이도 안전하게 동작하고, GPU 도입 시점에 쉽게 전환할 수 있는 서비스
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

class SafeGPUReadyService {
    constructor() {
        this.serviceName = 'SafeGPUReadyService';
        this.pythonScript = path.join(__dirname, '../../ai/safe_gpu_ready_system.py');
        this.isInitialized = false;
        this.models = {};
        this.performanceMetrics = {};
        
        console.log(`🚀 ${this.serviceName} 초기화 완료`);
    }

    /**
     * 안전한 AI 파이프라인 실행
     */
    async runSafeAIPipeline(audioFiles, labels) {
        try {
            console.log('🛡️ 안전한 AI 파이프라인 시작');
            
            const result = await this._executePythonScript('safe_ai_pipeline', {
                audio_files: audioFiles,
                labels: labels
            });
            
            if (result.success) {
                this.isInitialized = true;
                this.models = result.models || {};
                this.performanceMetrics = result.performance_metrics || {};
                
                console.log(`✅ 안전 AI 파이프라인 완료! 정확도: ${result.best_accuracy?.toFixed(3)}`);
                console.log(`   GPU 사용 가능: ${result.gpu_available}`);
                console.log(`   현재 디바이스: ${result.device}`);
                console.log(`   최고 모델: ${result.best_model}`);
            }
            
            return result;
            
        } catch (error) {
            console.error(`❌ 안전 AI 파이프라인 오류:`, error);
            return {
                success: false,
                error: error.message,
                gpu_available: false,
                device: 'cpu'
            };
        }
    }

    /**
     * 안전한 특징 추출
     */
    async extractSafeFeatures(audioData, sampleRate = 16000) {
        try {
            const result = await this._executePythonScript('extract_safe_features', {
                audio_data: audioData,
                sample_rate: sampleRate
            });
            
            return result;
            
        } catch (error) {
            console.error(`❌ 안전 특징 추출 오류:`, error);
            return {
                success: false,
                error: error.message,
                features: {}
            };
        }
    }

    /**
     * 안전한 모델 훈련
     */
    async trainSafeModels(features, labels) {
        try {
            const result = await this._executePythonScript('train_safe_models', {
                features: features,
                labels: labels
            });
            
            if (result.success) {
                this.models = result.models || {};
                this.isInitialized = true;
            }
            
            return result;
            
        } catch (error) {
            console.error(`❌ 안전 모델 훈련 오류:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 안전한 예측
     */
    async predictSafe(features, modelName = null) {
        try {
            const result = await this._executePythonScript('predict_safe', {
                features: features,
                model_name: modelName
            });
            
            return result;
            
        } catch (error) {
            console.error(`❌ 안전 예측 오류:`, error);
            return {
                success: false,
                error: error.message,
                prediction: [],
                confidence: 0.0
            };
        }
    }

    /**
     * GPU 사용 가능 여부 확인
     */
    async checkGPUAvailability() {
        try {
            const result = await this._executePythonScript('check_gpu_availability');
            return result;
            
        } catch (error) {
            console.error(`❌ GPU 확인 오류:`, error);
            return {
                gpu_available: false,
                device: 'cpu',
                error: error.message
            };
        }
    }

    /**
     * 모델 저장
     */
    async saveModels(filepath = null) {
        try {
            const result = await this._executePythonScript('save_safe_models', {
                filepath: filepath
            });
            
            return result;
            
        } catch (error) {
            console.error(`❌ 모델 저장 오류:`, error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * 모델 로드
     */
    async loadModels(filepath = null) {
        try {
            const result = await this._executePythonScript('load_safe_models', {
                filepath: filepath
            });
            
            if (result.success) {
                this.models = result.models || {};
                this.isInitialized = true;
            }
            
            return result;
            
        } catch (error) {
            console.error(`❌ 모델 로드 오류:`, error);
            return {
                success: false,
                error: error.message
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
            const gpuStatus = await this.checkGPUAvailability();
            const performanceMetrics = await this.getPerformanceMetrics();
            
            return {
                service_name: this.serviceName,
                is_initialized: this.isInitialized,
                gpu_available: gpuStatus.gpu_available,
                device: gpuStatus.device,
                models_count: Object.keys(this.models).length,
                performance_metrics: performanceMetrics.metrics || {},
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            console.error(`❌ 시스템 상태 조회 오류:`, error);
            return {
                service_name: this.serviceName,
                is_initialized: false,
                gpu_available: false,
                device: 'cpu',
                models_count: 0,
                performance_metrics: {},
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
            this.isInitialized = false;
            this.performanceMetrics = {};
            
            console.log('🔄 안전 모델 리셋 완료');
            
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
            
            if (stats.size > 100 * 1024 * 1024) { // 100MB 제한
                return {
                    valid: false,
                    error: '파일 크기가 너무 큽니다. (100MB 제한)'
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
     * 배치 처리
     */
    async batchProcess(audioFiles, labels, batchSize = 10) {
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
                
                const batchResult = await this.runSafeAIPipeline(batchFiles, batchLabels);
                results.push(batchResult);
                
                // 배치 간 잠시 대기 (시스템 부하 방지)
                if (i < totalBatches - 1) {
                    await new Promise(resolve => setTimeout(resolve, 1000));
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
}

module.exports = SafeGPUReadyService;
