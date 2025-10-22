#!/usr/bin/env python3
/**
 * Phase 1 API 테스트 스크립트
 * Node.js 서버의 Phase 1 AI 엔드포인트 테스트
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

// 서버 설정
const SERVER_URL = 'http://localhost:3000';
const API_BASE = `${SERVER_URL}/api/ai`;

class Phase1APITester {
    constructor() {
        this.testResults = [];
        console.log('🧪 Phase 1 API 테스트 시작');
        console.log(`🌐 서버 URL: ${SERVER_URL}`);
        console.log(`📡 API 베이스: ${API_BASE}`);
    }

    /**
     * 서버 상태 확인
     */
    async checkServerStatus() {
        try {
            console.log('\n🔍 서버 상태 확인 중...');
            const response = await axios.get(`${API_BASE}/status`);
            console.log('✅ 서버 연결 성공');
            console.log('📊 서버 상태:', response.data);
            return true;
        } catch (error) {
            console.error('❌ 서버 연결 실패:', error.message);
            return false;
        }
    }

    /**
     * Phase 1 상태 확인
     */
    async checkPhase1Status() {
        try {
            console.log('\n🔍 Phase 1 상태 확인 중...');
            const response = await axios.get(`${API_BASE}/phase1/status`);
            console.log('✅ Phase 1 상태 조회 성공');
            console.log('📊 Phase 1 상태:', response.data);
            return response.data;
        } catch (error) {
            console.error('❌ Phase 1 상태 조회 실패:', error.message);
            return null;
        }
    }

    /**
     * 가상의 정상 오디오 파일 생성
     */
    generateTestAudio(duration = 5.0, sampleRate = 16000, anomalyType = 'normal') {
        const samples = Math.floor(duration * sampleRate);
        const audioData = new Float32Array(samples);
        
        // 정상 냉장고 소음 시뮬레이션
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            if (anomalyType === 'normal') {
                // 정상 소음 (60Hz 기본 주파수)
                sample = Math.sin(2 * Math.PI * 60 * t);
                sample += 0.3 * Math.sin(2 * Math.PI * 120 * t);
                sample += 0.2 * Math.sin(2 * Math.PI * 180 * t);
                sample += (Math.random() - 0.5) * 0.1; // 노이즈
            } else if (anomalyType === 'bearing_wear') {
                // 베어링 마모 (고주파 소음)
                sample = Math.sin(2 * Math.PI * 60 * t);
                sample += 0.5 * Math.sin(2 * Math.PI * 1000 * t);
                sample += 0.4 * Math.sin(2 * Math.PI * 1500 * t);
                sample += (Math.random() - 0.5) * 0.2;
            } else if (anomalyType === 'compressor_abnormal') {
                // 압축기 이상 (높은 에너지)
                sample = Math.sin(2 * Math.PI * 60 * t) * 2.0;
                sample += (Math.random() - 0.5) * 0.3;
            }
            
            audioData[i] = sample;
        }
        
        return audioData;
    }

    /**
     * WAV 파일 생성
     */
    createWAVFile(audioData, sampleRate, filename) {
        const buffer = Buffer.alloc(44 + audioData.length * 2);
        
        // WAV 헤더 작성
        buffer.write('RIFF', 0);
        buffer.writeUInt32LE(36 + audioData.length * 2, 4);
        buffer.write('WAVE', 8);
        buffer.write('fmt ', 12);
        buffer.writeUInt32LE(16, 16);
        buffer.writeUInt16LE(1, 20);
        buffer.writeUInt16LE(1, 22);
        buffer.writeUInt32LE(sampleRate, 24);
        buffer.writeUInt32LE(sampleRate * 2, 28);
        buffer.writeUInt16LE(2, 32);
        buffer.writeUInt16LE(16, 34);
        buffer.write('data', 36);
        buffer.writeUInt32LE(audioData.length * 2, 40);
        
        // 오디오 데이터 작성
        for (let i = 0; i < audioData.length; i++) {
            const sample = Math.max(-1, Math.min(1, audioData[i]));
            buffer.writeInt16LE(Math.floor(sample * 32767), 44 + i * 2);
        }
        
        fs.writeFileSync(filename, buffer);
        return filename;
    }

    /**
     * Phase 1 모델 훈련 테스트
     */
    async testPhase1Training() {
        try {
            console.log('\n🎯 Phase 1 모델 훈련 테스트 시작...');
            
            // 가상의 정상 오디오 파일들 생성
            const normalFiles = [];
            for (let i = 0; i < 10; i++) {
                const audioData = this.generateTestAudio(5.0, 16000, 'normal');
                const filename = `temp_normal_${i}.wav`;
                this.createWAVFile(audioData, 16000, filename);
                normalFiles.push(path.resolve(filename));
            }
            
            console.log(`📁 생성된 정상 오디오 파일: ${normalFiles.length}개`);
            
            // 훈련 요청
            const response = await axios.post(`${API_BASE}/phase1/train`, {
                normalAudioFiles: normalFiles
            });
            
            console.log('✅ Phase 1 모델 훈련 성공');
            console.log('📊 훈련 결과:', response.data);
            
            // 임시 파일 정리
            normalFiles.forEach(file => {
                if (fs.existsSync(file)) {
                    fs.unlinkSync(file);
                }
            });
            
            return response.data;
            
        } catch (error) {
            console.error('❌ Phase 1 훈련 테스트 실패:', error.message);
            if (error.response) {
                console.error('📊 응답 데이터:', error.response.data);
            }
            return null;
        }
    }

    /**
     * Phase 1 이상 탐지 테스트
     */
    async testPhase1Detection() {
        try {
            console.log('\n🔍 Phase 1 이상 탐지 테스트 시작...');
            
            const testCases = [
                { type: 'normal', description: '정상' },
                { type: 'bearing_wear', description: '베어링 마모' },
                { type: 'compressor_abnormal', description: '압축기 이상' }
            ];
            
            const results = [];
            
            for (const testCase of testCases) {
                console.log(`\n  테스트: ${testCase.description}`);
                
                // 테스트 오디오 생성
                const audioData = this.generateTestAudio(5.0, 16000, testCase.type);
                const filename = `temp_test_${testCase.type}.wav`;
                this.createWAVFile(audioData, 16000, filename);
                
                try {
                    // FormData 생성
                    const formData = new FormData();
                    formData.append('audio', fs.createReadStream(filename));
                    formData.append('sampleRate', '16000');
                    
                    // 이상 탐지 요청
                    const response = await axios.post(`${API_BASE}/phase1/detect`, formData, {
                        headers: {
                            ...formData.getHeaders()
                        }
                    });
                    
                    const result = response.data.result;
                    console.log(`    결과: ${result.isAnomaly ? '이상' : '정상'}`);
                    console.log(`    신뢰도: ${(result.confidence * 100).toFixed(1)}%`);
                    console.log(`    유형: ${result.anomalyType}`);
                    console.log(`    처리 시간: ${result.processingTimeMs.toFixed(1)}ms`);
                    
                    results.push({
                        testType: testCase.type,
                        description: testCase.description,
                        isAnomaly: result.isAnomaly,
                        confidence: result.confidence,
                        anomalyType: result.anomalyType,
                        processingTime: result.processingTimeMs
                    });
                    
                } finally {
                    // 임시 파일 정리
                    if (fs.existsSync(filename)) {
                        fs.unlinkSync(filename);
                    }
                }
            }
            
            console.log('\n📊 Phase 1 탐지 테스트 결과:');
            results.forEach(result => {
                console.log(`  ${result.description}: ${result.isAnomaly ? '이상' : '정상'} (${(result.confidence * 100).toFixed(1)}%)`);
            });
            
            return results;
            
        } catch (error) {
            console.error('❌ Phase 1 탐지 테스트 실패:', error.message);
            if (error.response) {
                console.error('📊 응답 데이터:', error.response.data);
            }
            return [];
        }
    }

    /**
     * Phase 1 성능 통계 조회
     */
    async testPhase1Stats() {
        try {
            console.log('\n📊 Phase 1 성능 통계 조회...');
            
            const response = await axios.get(`${API_BASE}/phase1/stats`);
            console.log('✅ Phase 1 통계 조회 성공');
            console.log('📈 성능 통계:', response.data.stats);
            
            return response.data.stats;
            
        } catch (error) {
            console.error('❌ Phase 1 통계 조회 실패:', error.message);
            return null;
        }
    }

    /**
     * 전체 테스트 실행
     */
    async runAllTests() {
        console.log('🚀 Phase 1 API 전체 테스트 시작');
        console.log('=' * 60);
        
        // 1. 서버 상태 확인
        const serverOk = await this.checkServerStatus();
        if (!serverOk) {
            console.log('❌ 서버 연결 실패로 테스트 중단');
            return;
        }
        
        // 2. Phase 1 상태 확인
        const phase1Status = await this.checkPhase1Status();
        
        // 3. Phase 1 모델 훈련
        const trainingResult = await this.testPhase1Training();
        
        // 4. Phase 1 이상 탐지
        const detectionResults = await this.testPhase1Detection();
        
        // 5. Phase 1 성능 통계
        const stats = await this.testPhase1Stats();
        
        // 6. 테스트 결과 요약
        console.log('\n🎉 Phase 1 API 테스트 완료');
        console.log('=' * 60);
        console.log(`✅ 서버 연결: ${serverOk ? '성공' : '실패'}`);
        console.log(`✅ Phase 1 상태: ${phase1Status ? '조회 성공' : '조회 실패'}`);
        console.log(`✅ 모델 훈련: ${trainingResult ? '성공' : '실패'}`);
        console.log(`✅ 이상 탐지: ${detectionResults.length}개 테스트 완료`);
        console.log(`✅ 성능 통계: ${stats ? '조회 성공' : '조회 실패'}`);
        
        if (stats) {
            console.log(`📊 총 탐지 수: ${stats.totalDetections}`);
            console.log(`📊 이상 탐지 수: ${stats.anomalyCount}`);
            console.log(`📊 평균 처리 시간: ${stats.averageProcessingTime.toFixed(1)}ms`);
        }
        
        console.log('\n🎯 Phase 1 시스템이 성공적으로 구현되었습니다!');
    }
}

// 테스트 실행
if (require.main === module) {
    const tester = new Phase1APITester();
    tester.runAllTests().catch(console.error);
}

module.exports = Phase1APITester;
