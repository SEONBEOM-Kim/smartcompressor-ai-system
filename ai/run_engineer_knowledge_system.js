#!/usr/bin/env node
/**
 * 엔지니어 지식 활용 AI 학습 시스템 실행
 * 기계 설치 전에 엔지니어의 5년 경력을 활용하여 AI 학습 데이터 생성
 */

const fs = require('fs');
const path = require('path');

class EngineerKnowledgeSystem {
    constructor() {
        this.engineerKnowledge = {};
        this.explicitRules = {};
        this.syntheticData = {};
        this.trainingData = {};
    }

    async run() {
        console.log('🚀 엔지니어 지식 활용 AI 학습 시스템');
        console.log('='.repeat(60));
        console.log('기계 설치 전에 엔지니어의 5년 경력을 활용하여 AI 학습 데이터 생성');
        console.log('='.repeat(60));

        try {
            // 1단계: 엔지니어 지식 수집 시뮬레이션
            console.log('\n1️⃣ 엔지니어 지식 수집 시뮬레이션');
            this.engineerKnowledge = this.simulateEngineerKnowledge();

            // 2단계: 지식 명시화
            console.log('\n2️⃣ 지식 명시화');
            this.explicitRules = this.convertToExplicitRules(this.engineerKnowledge);

            // 3단계: 합성 데이터 생성
            console.log('\n3️⃣ 합성 데이터 생성');
            this.syntheticData = this.generateSyntheticData(this.explicitRules);

            // 4단계: AI 학습 데이터 준비
            console.log('\n4️⃣ AI 학습 데이터 준비');
            this.trainingData = this.prepareTrainingData(this.syntheticData);

            // 5단계: 결과 저장
            console.log('\n5️⃣ 결과 저장');
            await this.saveResults();

            console.log('\n🎉 엔지니어 지식 활용 AI 학습 시스템 완료!');
            console.log('이제 웹 브라우저에서 http://localhost:3000/static/sound_labeling_tool.html 을 열어서');
            console.log('실제 오디오 파일을 라벨링할 수 있습니다.');

            return true;
        } catch (error) {
            console.error('❌ 오류 발생:', error);
            return false;
        }
    }

    simulateEngineerKnowledge() {
        console.log('   📚 5년 경력 엔지니어 지식 수집 중...');

        const engineerKnowledge = {
            engineer_info: {
                name: '김기술',
                experience_years: 5,
                specialization: '산업용 압축기',
                company: '스마트압축기',
                interview_date: new Date().toISOString()
            },

            sound_classification: {
                '정상_압축기': {
                    description: '일정한 저주파 소음, 안정적인 작동음',
                    frequency_range: '20-200Hz',
                    amplitude_range: '0.1-0.3',
                    temporal_pattern: '일정한 리듬',
                    stability: '높음',
                    confidence: 0.9
                },
                '정상_팬': {
                    description: '일정한 중주파 소음, 부드러운 회전음',
                    frequency_range: '200-1000Hz',
                    amplitude_range: '0.2-0.4',
                    temporal_pattern: '일정한 리듬',
                    stability: '높음',
                    confidence: 0.9
                },
                '정상_모터': {
                    description: '일정한 저주파 소음, 안정적인 구동음',
                    frequency_range: '50-500Hz',
                    amplitude_range: '0.15-0.35',
                    temporal_pattern: '일정한 리듬',
                    stability: '높음',
                    confidence: 0.9
                },
                '베어링_마모': {
                    description: '불규칙한 고주파 진동, 마찰음',
                    frequency_range: '2000-8000Hz',
                    amplitude_range: '0.6-1.0',
                    temporal_pattern: '불규칙한 진동',
                    stability: '낮음',
                    confidence: 0.85
                },
                '언밸런스': {
                    description: '주기적 진동, 불균형 소음',
                    frequency_range: '50-500Hz',
                    amplitude_range: '0.3-0.8',
                    temporal_pattern: '주기적 진동',
                    stability: '중간',
                    confidence: 0.8
                },
                '마찰': {
                    description: '불규칙한 중주파, 마찰음',
                    frequency_range: '500-3000Hz',
                    amplitude_range: '0.25-0.7',
                    temporal_pattern: '불규칙한 패턴',
                    stability: '낮음',
                    confidence: 0.75
                },
                '과부하': {
                    description: '매우 강한 소음, 불규칙한 노이즈',
                    frequency_range: '20-8000Hz',
                    amplitude_range: '0.5-1.0',
                    temporal_pattern: '불규칙한 노이즈',
                    stability: '매우 낮음',
                    confidence: 0.9
                }
            },

            diagnostic_methods: {
                '안정성_평가': {
                    method: 'RMS와 ZCR의 변동계수 계산',
                    criteria: '시간에 따른 변화율',
                    threshold: '0.8 이상이면 안정적',
                    confidence: 0.9
                },
                '주파수_일관성': {
                    method: '스펙트럼 센트로이드의 안정성',
                    criteria: '시간에 따른 주파수 분포 변화',
                    threshold: '0.7 이상이면 일관적',
                    confidence: 0.8
                },
                '패턴_규칙성': {
                    method: '자기상관 함수를 이용한 주기성',
                    criteria: '주기적 패턴의 일관성',
                    threshold: '0.7 이상이면 규칙적',
                    confidence: 0.8
                }
            },

            experience_cases: [
                {
                    situation: '베어링 마모 초기 단계',
                    symptoms: ['고주파 진동', '불규칙한 소음', '진동 증가'],
                    diagnosis: '베어링 마모',
                    solution: '베어링 교체',
                    prevention: '정기 윤활 및 모니터링',
                    confidence: 0.9
                },
                {
                    situation: '언밸런스로 인한 진동',
                    symptoms: ['주기적 진동', '불균형 소음', '진동 증가'],
                    diagnosis: '언밸런스',
                    solution: '밸런싱 작업',
                    prevention: '정기 밸런싱 점검',
                    confidence: 0.8
                }
            ],

            heuristic_knowledge: {
                abnormal_feeling: '소음이 갑자기 증가하면 이상 징후',
                quick_judgment: 'RMS 변화율과 주파수 일관성 확인',
                noise_level: '정상: 0.1-0.4, 주의: 0.4-0.7, 위험: 0.7 이상',
                environment: '온도, 습도, 부하에 따라 임계값 조정 필요'
            }
        };

        console.log(`   ✅ ${Object.keys(engineerKnowledge.sound_classification).length}개 소리 분류 수집`);
        console.log(`   ✅ ${Object.keys(engineerKnowledge.diagnostic_methods).length}개 진단 방법 수집`);
        console.log(`   ✅ ${engineerKnowledge.experience_cases.length}개 경험 사례 수집`);

        return engineerKnowledge;
    }

    convertToExplicitRules(engineerKnowledge) {
        console.log('   🔄 암묵적 지식 → 명시적 규칙 변환 중...');

        const explicitRules = {
            if_then_rules: [],
            fuzzy_rules: [],
            threshold_rules: [],
            confidence_rules: []
        };

        // 소리 분류 규칙 생성
        let ruleId = 1;
        for (const [soundType, soundInfo] of Object.entries(engineerKnowledge.sound_classification)) {
            const rule = {
                rule_id: `R_${ruleId.toString().padStart(3, '0')}`,
                description: `${soundType} 판단 규칙`,
                if_conditions: [
                    `frequency_range == '${soundInfo.frequency_range}'`,
                    `amplitude_range == '${soundInfo.amplitude_range}'`,
                    `temporal_pattern == '${soundInfo.temporal_pattern}'`,
                    `stability == '${soundInfo.stability}'`
                ],
                then_action: `classify_as_${soundType}`,
                confidence: soundInfo.confidence,
                source: 'engineer_experience'
            };
            explicitRules.if_then_rules.push(rule);
            ruleId++;
        }

        // 진단 방법 규칙 생성
        let thresholdId = 1;
        for (const [methodName, methodInfo] of Object.entries(engineerKnowledge.diagnostic_methods)) {
            const rule = {
                rule_id: `T_${thresholdId.toString().padStart(3, '0')}`,
                description: `${methodName} 임계값 규칙`,
                method: methodInfo.method,
                threshold: methodInfo.threshold,
                confidence: methodInfo.confidence,
                source: 'engineer_experience'
            };
            explicitRules.threshold_rules.push(rule);
            thresholdId++;
        }

        // 퍼지 규칙 생성
        const fuzzyRule = {
            rule_id: 'F001',
            description: '소음 레벨 퍼지 판단',
            input_variables: {
                noise_level: {
                    low: [0.0, 0.3],
                    medium: [0.2, 0.7],
                    high: [0.6, 1.0]
                }
            },
            output_variable: 'noise_severity',
            rules: [
                'IF noise_level IS low THEN noise_severity IS normal',
                'IF noise_level IS medium THEN noise_severity IS warning',
                'IF noise_level IS high THEN noise_severity IS critical'
            ]
        };
        explicitRules.fuzzy_rules.push(fuzzyRule);

        console.log(`   ✅ ${explicitRules.if_then_rules.length}개 IF-THEN 규칙 생성`);
        console.log(`   ✅ ${explicitRules.threshold_rules.length}개 임계값 규칙 생성`);
        console.log(`   ✅ ${explicitRules.fuzzy_rules.length}개 퍼지 규칙 생성`);

        return explicitRules;
    }

    generateSyntheticData(explicitRules) {
        console.log('   🎵 합성 오디오 데이터 생성 중...');

        const syntheticData = {
            audio_samples: [],
            feature_vectors: [],
            labels: [],
            metadata: []
        };

        // 정상 소리 데이터 생성 (100개)
        const normalSamples = this.generateNormalSamples(100);
        syntheticData.audio_samples.push(...normalSamples.samples);
        syntheticData.feature_vectors.push(...normalSamples.features);
        syntheticData.labels.push(...normalSamples.labels);
        syntheticData.metadata.push(...normalSamples.metadata);

        // 이상 소리 데이터 생성 (100개)
        const abnormalSamples = this.generateAbnormalSamples(100);
        syntheticData.audio_samples.push(...abnormalSamples.samples);
        syntheticData.feature_vectors.push(...abnormalSamples.features);
        syntheticData.labels.push(...abnormalSamples.labels);
        syntheticData.metadata.push(...abnormalSamples.metadata);

        console.log(`   ✅ ${syntheticData.audio_samples.length}개 합성 오디오 샘플 생성`);
        console.log(`   ✅ ${syntheticData.feature_vectors.length}개 특징 벡터 생성`);
        console.log(`   ✅ ${syntheticData.labels.length}개 라벨 생성`);

        return syntheticData;
    }

    generateNormalSamples(count) {
        const samples = [];
        const features = [];
        const labels = [];
        const metadata = [];

        for (let i = 0; i < count; i++) {
            let sample, label;

            if (i < count / 3) {
                // 정상 압축기
                sample = this.generateCompressorSound();
                label = 'normal_compressor';
            } else if (i < 2 * count / 3) {
                // 정상 팬
                sample = this.generateFanSound();
                label = 'normal_fan';
            } else {
                // 정상 모터
                sample = this.generateMotorSound();
                label = 'normal_motor';
            }

            // 특징 추출
            const featureVector = this.extractFeatures(sample);

            samples.push(sample);
            features.push(featureVector);
            labels.push(label);
            metadata.push({
                type: 'synthetic',
                category: 'normal',
                subcategory: label,
                generation_time: new Date().toISOString()
            });
        }

        return {
            samples,
            features,
            labels,
            metadata
        };
    }

    generateAbnormalSamples(count) {
        const samples = [];
        const features = [];
        const labels = [];
        const metadata = [];

        for (let i = 0; i < count; i++) {
            let sample, label;

            if (i < count / 4) {
                // 베어링 마모
                sample = this.generateBearingWearSound();
                label = 'abnormal_bearing';
            } else if (i < count / 2) {
                // 언밸런스
                sample = this.generateUnbalanceSound();
                label = 'abnormal_unbalance';
            } else if (i < 3 * count / 4) {
                // 마찰
                sample = this.generateFrictionSound();
                label = 'abnormal_friction';
            } else {
                // 과부하
                sample = this.generateOverloadSound();
                label = 'abnormal_overload';
            }

            // 특징 추출
            const featureVector = this.extractFeatures(sample);

            samples.push(sample);
            features.push(featureVector);
            labels.push(label);
            metadata.push({
                type: 'synthetic',
                category: 'abnormal',
                subcategory: label,
                generation_time: new Date().toISOString()
            });
        }

        return {
            samples,
            features,
            labels,
            metadata
        };
    }

    generateCompressorSound() {
        // 5초, 22050Hz 샘플링
        const duration = 5.0;
        const sampleRate = 22050;
        const t = this.linspace(0, duration, Math.floor(sampleRate * duration));

        // 저주파 기본 신호 (20-200Hz)
        const baseFreq = 60;
        let signal = this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq));

        // 하모닉 추가
        signal = this.addArrays(signal, this.multiplyArray(this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq * 2)), 0.3));
        signal = this.addArrays(signal, this.multiplyArray(this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq * 3)), 0.1));

        // 노이즈 추가 (정상 범위)
        const noise = this.generateNoise(t.length, 0.05);
        signal = this.addArrays(signal, noise);

        // 진폭 조정 (0.1-0.3)
        signal = this.multiplyArray(signal, 0.2);

        return signal;
    }

    generateFanSound() {
        const duration = 5.0;
        const sampleRate = 22050;
        const t = this.linspace(0, duration, Math.floor(sampleRate * duration));

        // 중주파 기본 신호 (200-1000Hz)
        const baseFreq = 400;
        let signal = this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq));

        // 하모닉 추가
        signal = this.addArrays(signal, this.multiplyArray(this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq * 2)), 0.2));
        signal = this.addArrays(signal, this.multiplyArray(this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq * 3)), 0.1));

        // 노이즈 추가
        const noise = this.generateNoise(t.length, 0.03);
        signal = this.addArrays(signal, noise);

        // 진폭 조정 (0.2-0.4)
        signal = this.multiplyArray(signal, 0.3);

        return signal;
    }

    generateMotorSound() {
        const duration = 5.0;
        const sampleRate = 22050;
        const t = this.linspace(0, duration, Math.floor(sampleRate * duration));

        // 저주파 기본 신호 (50-500Hz)
        const baseFreq = 150;
        let signal = this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq));

        // 하모닉 추가
        signal = this.addArrays(signal, this.multiplyArray(this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq * 2)), 0.25));
        signal = this.addArrays(signal, this.multiplyArray(this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq * 3)), 0.1));

        // 노이즈 추가
        const noise = this.generateNoise(t.length, 0.04);
        signal = this.addArrays(signal, noise);

        // 진폭 조정 (0.15-0.35)
        signal = this.multiplyArray(signal, 0.25);

        return signal;
    }

    generateBearingWearSound() {
        const duration = 5.0;
        const sampleRate = 22050;
        const t = this.linspace(0, duration, Math.floor(sampleRate * duration));

        // 고주파 마찰음 (2000-8000Hz)
        const baseFreq = 3000;
        let signal = this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq));

        // 불규칙한 진동 추가
        const irregularity = this.generateNoise(t.length, 0.3, 1);
        signal = this.multiplyArrays(signal, irregularity);

        // 고주파 노이즈 추가
        const noise = this.generateNoise(t.length, 0.2);
        signal = this.addArrays(signal, noise);

        // 진폭 조정 (0.6-1.0)
        signal = this.multiplyArray(signal, 0.8);

        return signal;
    }

    generateUnbalanceSound() {
        const duration = 5.0;
        const sampleRate = 22050;
        const t = this.linspace(0, duration, Math.floor(sampleRate * duration));

        // 주기적 진동 (50-500Hz)
        const baseFreq = 200;
        let signal = this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq));

        // 주기적 진동 추가
        const vibration = this.multiplyArray(this.sin(this.multiplyArray(t, 2 * Math.PI * 0.5)), 0.5);
        signal = this.multiplyArrays(signal, this.addArrays(this.createArray(t.length, 1), vibration));

        // 노이즈 추가
        const noise = this.generateNoise(t.length, 0.1);
        signal = this.addArrays(signal, noise);

        // 진폭 조정 (0.3-0.8)
        signal = this.multiplyArray(signal, 0.5);

        return signal;
    }

    generateFrictionSound() {
        const duration = 5.0;
        const sampleRate = 22050;
        const t = this.linspace(0, duration, Math.floor(sampleRate * duration));

        // 중주파 마찰음 (500-3000Hz)
        const baseFreq = 1500;
        let signal = this.sin(this.multiplyArray(t, 2 * Math.PI * baseFreq));

        // 불규칙한 마찰 패턴
        const frictionPattern = this.generateNoise(t.length, 0.4, 1);
        signal = this.multiplyArrays(signal, frictionPattern);

        // 노이즈 추가
        const noise = this.generateNoise(t.length, 0.15);
        signal = this.addArrays(signal, noise);

        // 진폭 조정 (0.25-0.7)
        signal = this.multiplyArray(signal, 0.45);

        return signal;
    }

    generateOverloadSound() {
        const duration = 5.0;
        const sampleRate = 22050;
        const t = this.linspace(0, duration, Math.floor(sampleRate * duration));

        // 전체 주파수 대역 노이즈 (20-8000Hz)
        let signal = this.createArray(t.length, 0);

        // 여러 주파수 대역의 노이즈
        const frequencies = [100, 500, 1000, 2000, 4000, 6000];
        for (const freq of frequencies) {
            const component = this.multiplyArray(this.sin(this.multiplyArray(t, 2 * Math.PI * freq)), 0.3);
            signal = this.addArrays(signal, component);
        }

        // 강한 노이즈 추가
        const noise = this.generateNoise(t.length, 0.3);
        signal = this.addArrays(signal, noise);

        // 진폭 조정 (0.5-1.0)
        signal = this.multiplyArray(signal, 0.7);

        return signal;
    }

    extractFeatures(signal) {
        // 간단한 특징 추출 (실제로는 더 복잡한 특징 사용)
        const mean = this.mean(signal);
        const std = this.std(signal);
        const max = Math.max(...signal);
        const min = Math.min(...signal);
        const var_ = this.variance(signal);
        const meanAbs = this.mean(this.abs(signal));
        const maxAbs = Math.max(...this.abs(signal));
        const totalEnergy = this.sum(this.abs(signal));
        const meanSquared = this.mean(this.square(signal));
        const diff = this.diff(signal);
        const diffStd = this.std(diff);

        return [mean, std, max, min, var_, meanAbs, maxAbs, totalEnergy, meanSquared, diffStd];
    }

    prepareTrainingData(syntheticData) {
        console.log('   🤖 AI 학습용 데이터 준비 중...');

        const trainingData = {
            X: syntheticData.feature_vectors,
            y: syntheticData.labels,
            metadata: syntheticData.metadata,
            feature_names: [
                'mean', 'std', 'max', 'min', 'var',
                'mean_abs', 'max_abs', 'total_energy',
                'mean_squared', 'diff_std'
            ],
            label_mapping: {
                'normal_compressor': 0,
                'normal_fan': 1,
                'normal_motor': 2,
                'abnormal_bearing': 3,
                'abnormal_unbalance': 4,
                'abnormal_friction': 5,
                'abnormal_overload': 6
            }
        };

        console.log(`   ✅ ${trainingData.X.length}개 학습 샘플 준비`);
        console.log(`   ✅ ${trainingData.X[0].length}개 특징 사용`);
        console.log(`   ✅ ${Object.keys(trainingData.label_mapping).length}개 클래스 정의`);

        return trainingData;
    }

    async saveResults() {
        console.log('   💾 결과 저장 중...');

        // 결과 디렉토리 생성
        await this.ensureDir('data/engineer_knowledge');
        await this.ensureDir('data/synthetic_data');
        await this.ensureDir('data/training_data');

        // 엔지니어 지식 저장
        await this.writeFile('data/engineer_knowledge/engineer_knowledge.json', 
            JSON.stringify(this.engineerKnowledge, null, 2));

        // 명시적 규칙 저장
        await this.writeFile('data/engineer_knowledge/explicit_rules.json', 
            JSON.stringify(this.explicitRules, null, 2));

        // 합성 데이터 저장 (메타데이터만)
        const syntheticMetadata = {
            total_samples: this.syntheticData.audio_samples.length,
            feature_vectors: this.syntheticData.feature_vectors,
            labels: this.syntheticData.labels,
            metadata: this.syntheticData.metadata
        };

        await this.writeFile('data/synthetic_data/synthetic_metadata.json', 
            JSON.stringify(syntheticMetadata, null, 2));

        // 학습 데이터 저장
        const trainingMetadata = {
            X_shape: [this.trainingData.X.length, this.trainingData.X[0].length],
            y: this.trainingData.y,
            feature_names: this.trainingData.feature_names,
            label_mapping: this.trainingData.label_mapping,
            X_data: this.trainingData.X
        };

        await this.writeFile('data/training_data/training_metadata.json', 
            JSON.stringify(trainingMetadata, null, 2));

        console.log('   ✅ 모든 결과 저장 완료');
        console.log('   📁 저장 위치:');
        console.log('      - data/engineer_knowledge/');
        console.log('      - data/synthetic_data/');
        console.log('      - data/training_data/');
    }

    // 유틸리티 함수들
    linspace(start, stop, num) {
        const step = (stop - start) / (num - 1);
        return Array.from({ length: num }, (_, i) => start + i * step);
    }

    sin(x) {
        return x.map(val => Math.sin(val));
    }

    addArrays(a, b) {
        return a.map((val, i) => val + b[i]);
    }

    multiplyArray(arr, scalar) {
        return arr.map(val => val * scalar);
    }

    multiplyArrays(a, b) {
        return a.map((val, i) => val * b[i]);
    }

    generateNoise(length, std, mean = 0) {
        return Array.from({ length }, () => this.gaussianRandom(mean, std));
    }

    gaussianRandom(mean = 0, std = 1) {
        let u = 0, v = 0;
        while (u === 0) u = Math.random();
        while (v === 0) v = Math.random();
        return mean + std * Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
    }

    createArray(length, value) {
        return Array(length).fill(value);
    }

    mean(arr) {
        return arr.reduce((sum, val) => sum + val, 0) / arr.length;
    }

    std(arr) {
        const mean = this.mean(arr);
        const variance = this.mean(arr.map(val => Math.pow(val - mean, 2)));
        return Math.sqrt(variance);
    }

    variance(arr) {
        const mean = this.mean(arr);
        return this.mean(arr.map(val => Math.pow(val - mean, 2)));
    }

    abs(arr) {
        return arr.map(val => Math.abs(val));
    }

    square(arr) {
        return arr.map(val => val * val);
    }

    sum(arr) {
        return arr.reduce((sum, val) => sum + val, 0);
    }

    diff(arr) {
        return arr.slice(1).map((val, i) => val - arr[i]);
    }

    async ensureDir(dir) {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    }

    async writeFile(filePath, data) {
        return new Promise((resolve, reject) => {
            fs.writeFile(filePath, data, 'utf8', (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }
}

// 메인 실행
async function main() {
    const system = new EngineerKnowledgeSystem();
    await system.run();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = EngineerKnowledgeSystem;
