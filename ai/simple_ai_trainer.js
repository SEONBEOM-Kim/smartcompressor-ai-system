#!/usr/bin/env node
/**
 * 간단한 AI 모델 훈련 시스템
 * 엔지니어 지식 기반 합성 데이터로 AI 모델 훈련
 */

const fs = require('fs');
const path = require('path');

class SimpleAITrainer {
    constructor() {
        this.trainingData = null;
        this.model = null;
        this.scaler = null;
    }

    async run() {
        console.log('🤖 간단한 AI 모델 훈련 시스템');
        console.log('='.repeat(60));
        console.log('엔지니어 지식 기반 합성 데이터로 AI 모델 훈련');
        console.log('='.repeat(60));

        try {
            // 1단계: 학습 데이터 로드
            console.log('\n1️⃣ 학습 데이터 로드');
            await this.loadTrainingData();

            // 2단계: 데이터 전처리
            console.log('\n2️⃣ 데이터 전처리');
            this.preprocessData();

            // 3단계: 모델 훈련
            console.log('\n3️⃣ 모델 훈련');
            await this.trainModel();

            // 4단계: 모델 평가
            console.log('\n4️⃣ 모델 평가');
            this.evaluateModel();

            // 5단계: 모델 저장
            console.log('\n5️⃣ 모델 저장');
            await this.saveModel();

            console.log('\n🎉 AI 모델 훈련 완료!');
            console.log('이제 실제 오디오 파일을 진단할 수 있습니다.');

            return true;
        } catch (error) {
            console.error('❌ 오류 발생:', error);
            return false;
        }
    }

    async loadTrainingData() {
        console.log('   📚 학습 데이터 로드 중...');

        const trainingDataPath = 'data/training_data/training_metadata.json';
        const data = JSON.parse(fs.readFileSync(trainingDataPath, 'utf8'));

        this.trainingData = {
            X: data.X_data,
            y: data.y,
            feature_names: data.feature_names,
            label_mapping: data.label_mapping
        };

        console.log(`   ✅ ${this.trainingData.X.length}개 학습 샘플 로드`);
        console.log(`   ✅ ${this.trainingData.X[0].length}개 특징 사용`);
        console.log(`   ✅ ${Object.keys(this.trainingData.label_mapping).length}개 클래스 정의`);
    }

    preprocessData() {
        console.log('   🔄 데이터 전처리 중...');

        // 특징 정규화 (Min-Max Scaling)
        this.scaler = this.fitMinMaxScaler(this.trainingData.X);
        this.trainingData.X_scaled = this.transformMinMaxScaler(this.trainingData.X, this.scaler);

        // 라벨을 숫자로 변환
        this.trainingData.y_numeric = this.trainingData.y.map(label => 
            this.trainingData.label_mapping[label]
        );

        console.log('   ✅ 특징 정규화 완료');
        console.log('   ✅ 라벨 숫자 변환 완료');
    }

    async trainModel() {
        console.log('   🧠 모델 훈련 중...');

        // 간단한 규칙 기반 모델 (엔지니어 지식 활용)
        this.model = new RuleBasedModel(this.trainingData.label_mapping);

        // 훈련 데이터로 모델 파라미터 설정
        this.model.fit(this.trainingData.X_scaled, this.trainingData.y_numeric);

        console.log('   ✅ 모델 훈련 완료');
    }

    evaluateModel() {
        console.log('   📊 모델 평가 중...');

        // 훈련 데이터로 예측
        const predictions = this.trainingData.X_scaled.map(features => 
            this.model.predict(features)
        );

        // 정확도 계산
        const correct = predictions.filter((pred, i) => pred === this.trainingData.y_numeric[i]).length;
        const accuracy = correct / predictions.length;

        // 클래스별 정확도
        const classAccuracy = {};
        for (const [label, classId] of Object.entries(this.trainingData.label_mapping)) {
            const classIndices = this.trainingData.y_numeric.map((y, i) => y === classId ? i : -1).filter(i => i !== -1);
            const classPredictions = classIndices.map(i => predictions[i]);
            const classCorrect = classPredictions.filter((pred, i) => pred === this.trainingData.y_numeric[classIndices[i]]).length;
            classAccuracy[label] = classCorrect / classIndices.length;
        }

        console.log(`   ✅ 전체 정확도: ${(accuracy * 100).toFixed(2)}%`);
        console.log('   📈 클래스별 정확도:');
        for (const [label, acc] of Object.entries(classAccuracy)) {
            console.log(`      - ${label}: ${(acc * 100).toFixed(2)}%`);
        }

        this.model.accuracy = accuracy;
        this.model.classAccuracy = classAccuracy;
    }

    async saveModel() {
        console.log('   💾 모델 저장 중...');

        // 모델 디렉토리 생성
        await this.ensureDir('data/models');

        // 모델 메타데이터 저장
        const modelMetadata = {
            model_type: 'rule_based',
            accuracy: this.model.accuracy,
            class_accuracy: this.model.classAccuracy,
            feature_names: this.trainingData.feature_names,
            label_mapping: this.trainingData.label_mapping,
            scaler: this.scaler,
            training_date: new Date().toISOString(),
            total_samples: this.trainingData.X.length,
            features_count: this.trainingData.X[0].length
        };

        await this.writeFile('data/models/model_metadata.json', 
            JSON.stringify(modelMetadata, null, 2));

        // 모델 규칙 저장
        await this.writeFile('data/models/model_rules.json', 
            JSON.stringify(this.model.rules, null, 2));

        console.log('   ✅ 모델 저장 완료');
        console.log('   📁 저장 위치: data/models/');
    }

    // 유틸리티 함수들
    fitMinMaxScaler(X) {
        const scaler = { min: [], max: [] };
        const nFeatures = X[0].length;

        for (let i = 0; i < nFeatures; i++) {
            const values = X.map(row => row[i]);
            scaler.min[i] = Math.min(...values);
            scaler.max[i] = Math.max(...values);
        }

        return scaler;
    }

    transformMinMaxScaler(X, scaler) {
        return X.map(row => 
            row.map((value, i) => 
                (value - scaler.min[i]) / (scaler.max[i] - scaler.min[i])
            )
        );
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

class RuleBasedModel {
    constructor(labelMapping) {
        this.labelMapping = labelMapping;
        this.rules = [];
        this.accuracy = 0;
        this.classAccuracy = {};
    }

    fit(X, y) {
        // 엔지니어 지식 기반 규칙 생성
        this.rules = this.generateRules(X, y);
    }

    generateRules(X, y) {
        const rules = [];
        const nFeatures = X[0].length;

        // 각 클래스별 특징 범위 분석
        const classStats = {};
        for (const [label, classId] of Object.entries(this.labelMapping)) {
            const classIndices = y.map((yVal, i) => yVal === classId ? i : -1).filter(i => i !== -1);
            if (classIndices.length === 0) continue;

            const classFeatures = classIndices.map(i => X[i]);
            const stats = {
                mean: this.calculateMean(classFeatures),
                std: this.calculateStd(classFeatures),
                min: this.calculateMin(classFeatures),
                max: this.calculateMax(classFeatures)
            };
            classStats[classId] = { label, stats };
        }

        // 규칙 생성
        for (const [classId, { label, stats }] of Object.entries(classStats)) {
            const rule = {
                class_id: parseInt(classId),
                class_label: label,
                conditions: [],
                confidence: 0.8
            };

            // 각 특징에 대한 조건 생성
            for (let i = 0; i < nFeatures; i++) {
                const mean = stats.mean[i];
                const std = stats.std[i];
                const threshold = std * 1.5; // 1.5 표준편차 범위

                rule.conditions.push({
                    feature_index: i,
                    min_value: Math.max(0, mean - threshold),
                    max_value: Math.min(1, mean + threshold),
                    weight: 1.0 / nFeatures
                });
            }

            rules.push(rule);
        }

        return rules;
    }

    predict(features) {
        let bestClass = 0;
        let bestScore = -1;

        for (const rule of this.rules) {
            let score = 0;
            let totalWeight = 0;

            for (const condition of rule.conditions) {
                const value = features[condition.feature_index];
                const weight = condition.weight;
                
                if (value >= condition.min_value && value <= condition.max_value) {
                    score += weight;
                }
                totalWeight += weight;
            }

            const normalizedScore = totalWeight > 0 ? score / totalWeight : 0;

            if (normalizedScore > bestScore) {
                bestScore = normalizedScore;
                bestClass = rule.class_id;
            }
        }

        return bestClass;
    }

    calculateMean(data) {
        const nFeatures = data[0].length;
        const mean = new Array(nFeatures).fill(0);

        for (const row of data) {
            for (let i = 0; i < nFeatures; i++) {
                mean[i] += row[i];
            }
        }

        return mean.map(val => val / data.length);
    }

    calculateStd(data) {
        const mean = this.calculateMean(data);
        const nFeatures = data[0].length;
        const variance = new Array(nFeatures).fill(0);

        for (const row of data) {
            for (let i = 0; i < nFeatures; i++) {
                variance[i] += Math.pow(row[i] - mean[i], 2);
            }
        }

        return variance.map(val => Math.sqrt(val / data.length));
    }

    calculateMin(data) {
        const nFeatures = data[0].length;
        const min = new Array(nFeatures).fill(Infinity);

        for (const row of data) {
            for (let i = 0; i < nFeatures; i++) {
                min[i] = Math.min(min[i], row[i]);
            }
        }

        return min;
    }

    calculateMax(data) {
        const nFeatures = data[0].length;
        const max = new Array(nFeatures).fill(-Infinity);

        for (const row of data) {
            for (let i = 0; i < nFeatures; i++) {
                max[i] = Math.max(max[i], row[i]);
            }
        }

        return max;
    }
}

// 메인 실행
async function main() {
    const trainer = new SimpleAITrainer();
    await trainer.run();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = SimpleAITrainer;
