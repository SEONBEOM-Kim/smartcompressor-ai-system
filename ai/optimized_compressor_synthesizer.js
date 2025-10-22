#!/usr/bin/env node
/**
 * 최적화된 압축기 합성음 생성 시스템
 * 메모리 효율적이고 안정적인 고품질 소리 생성
 */

const fs = require('fs');
const path = require('path');

class OptimizedCompressorSynthesizer {
    constructor() {
        this.outputDir = 'data/high_quality_sounds';
        this.sampleRate = 44100;
        this.bitDepth = 16;
        
        // 실제 압축기 특성 파라미터
        this.compressorTypes = {
            normal_compressor: {
                baseFreq: 60,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.8, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08, 0.05, 0.03],
                noiseLevel: 0.05,
                description: '정상적인 압축기 작동음'
            },
            normal_fan: {
                baseFreq: 400,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08, 0.05, 0.03, 0.02],
                noiseLevel: 0.08,
                description: '정상적인 팬 회전음'
            },
            normal_motor: {
                baseFreq: 150,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.7, 0.5, 0.35, 0.25, 0.18, 0.12, 0.08, 0.05, 0.03, 0.02],
                noiseLevel: 0.06,
                description: '정상적인 모터 구동음'
            },
            abnormal_bearing: {
                baseFreq: 3000,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.9, 0.7, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1, 0.08],
                noiseLevel: 0.15,
                description: '베어링 마모로 인한 이상 소음'
            },
            abnormal_unbalance: {
                baseFreq: 200,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.8, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08, 0.05, 0.03],
                noiseLevel: 0.12,
                description: '언밸런스로 인한 진동 소음'
            },
            abnormal_friction: {
                baseFreq: 1500,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.7, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1, 0.08, 0.05],
                noiseLevel: 0.2,
                description: '마찰로 인한 이상 소음'
            },
            abnormal_overload: {
                baseFreq: 100,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [1.0, 0.8, 0.6, 0.5, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15],
                noiseLevel: 0.25,
                description: '과부하 상태의 이상 소음'
            }
        };
    }

    async run() {
        console.log('🎵 최적화된 압축기 합성음 생성 시스템');
        console.log('='.repeat(60));
        console.log('메모리 효율적이고 안정적인 고품질 소리 생성');
        console.log('='.repeat(60));

        try {
            // 디렉토리 생성
            await this.createDirectories();

            // 고품질 합성음 생성
            console.log('\n1️⃣ 고품질 합성음 생성');
            await this.generateHighQualitySounds();

            // 라벨링용 데이터 준비
            console.log('\n2️⃣ 라벨링용 데이터 준비');
            await this.prepareLabelingData();

            console.log('\n🎉 고품질 합성음 생성 완료!');
            console.log('이제 엔지니어님이 실제와 유사한 소리로 라벨링할 수 있습니다.');

            return true;
        } catch (error) {
            console.error('❌ 오류 발생:', error);
            return false;
        }
    }

    async createDirectories() {
        console.log('   📁 디렉토리 생성 중...');
        
        await this.ensureDir(this.outputDir);
        
        for (const category of Object.keys(this.compressorTypes)) {
            await this.ensureDir(path.join(this.outputDir, category));
        }
        
        console.log('   ✅ 디렉토리 생성 완료');
    }

    async generateHighQualitySounds() {
        console.log('   🎼 고품질 합성음 생성 중...');
        
        let totalGenerated = 0;
        
        for (const [category, characteristics] of Object.entries(this.compressorTypes)) {
            console.log(`   📥 ${characteristics.description} 생성 중...`);
            
            // 각 카테고리별로 5개씩 생성
            for (let i = 1; i <= 5; i++) {
                const filename = `${category}_hq_${i}.wav`;
                const filepath = path.join(this.outputDir, category, filename);
                
                try {
                    // 최적화된 고품질 합성음 생성
                    const audioData = this.generateOptimizedSound(characteristics, i);
                    
                    // WAV 파일로 저장
                    await this.saveWavFile(filepath, audioData);
                    totalGenerated++;
                } catch (error) {
                    console.log(`   ⚠️ 생성 실패: ${filename} - ${error.message}`);
                }
            }
        }

        console.log(`   ✅ ${totalGenerated}개 고품질 합성음 생성 완료`);
    }

    generateOptimizedSound(characteristics, variant) {
        const duration = 5; // 5초
        const samples = Math.floor(this.sampleRate * duration);
        
        // 메모리 효율적인 신호 생성
        let signal = new Float32Array(samples);
        
        // 기본 주파수와 고조파 생성 (배치 처리)
        for (let i = 0; i < characteristics.harmonics.length; i++) {
            const freq = characteristics.baseFreq * characteristics.harmonics[i];
            const amp = characteristics.harmonicAmps[i];
            
            // 고조파 신호 생성 (배치 처리)
            for (let j = 0; j < samples; j++) {
                const t = j / this.sampleRate;
                const harmonic = Math.sin(2 * Math.PI * freq * t);
                signal[j] += harmonic * amp;
            }
        }
        
        // 변형별 특수 효과 적용
        signal = this.applyVariantEffects(signal, characteristics, variant);
        
        // 노이즈 추가
        const noise = this.generateNoise(samples, characteristics.noiseLevel);
        for (let i = 0; i < samples; i++) {
            signal[i] += noise[i];
        }
        
        // 정규화
        signal = this.normalize(signal);
        
        return signal;
    }

    applyVariantEffects(signal, characteristics, variant) {
        const samples = signal.length;
        
        // 변형별 특수 효과
        switch (variant) {
            case 1: // 기본 변형
                break;
                
            case 2: // 주파수 변조
                for (let i = 0; i < samples; i++) {
                    const t = i / this.sampleRate;
                    const freqMod = 0.05 * Math.sin(2 * Math.PI * 0.2 * t);
                    signal[i] *= (1 + freqMod);
                }
                break;
                
            case 3: // 진폭 변조
                for (let i = 0; i < samples; i++) {
                    const t = i / this.sampleRate;
                    const ampMod = 0.1 * Math.sin(2 * Math.PI * 0.15 * t);
                    signal[i] *= (1 + ampMod);
                }
                break;
                
            case 4: // 노이즈 레벨 증가
                const extraNoise = this.generateNoise(samples, characteristics.noiseLevel * 0.3);
                for (let i = 0; i < samples; i++) {
                    signal[i] += extraNoise[i];
                }
                break;
                
            case 5: // 복합 효과
                for (let i = 0; i < samples; i++) {
                    const t = i / this.sampleRate;
                    const complexMod = 0.03 * Math.sin(2 * Math.PI * 0.1 * t) + 
                                      0.02 * Math.sin(2 * Math.PI * 0.25 * t);
                    signal[i] *= (1 + complexMod);
                }
                break;
        }
        
        return signal;
    }

    generateNoise(samples, level) {
        const noise = new Float32Array(samples);
        for (let i = 0; i < samples; i++) {
            noise[i] = (Math.random() * 2 - 1) * level;
        }
        return noise;
    }

    normalize(signal) {
        let max = 0;
        for (let i = 0; i < signal.length; i++) {
            const abs = Math.abs(signal[i]);
            if (abs > max) max = abs;
        }
        
        if (max > 0) {
            const factor = 0.8 / max;
            for (let i = 0; i < signal.length; i++) {
                signal[i] *= factor;
            }
        }
        
        return signal;
    }

    async prepareLabelingData() {
        console.log('   📋 라벨링용 데이터 준비 중...');
        
        const labelingData = {
            high_quality_sounds: [],
            total_files: 0,
            categories: Object.keys(this.compressorTypes),
            created_at: new Date().toISOString(),
            instructions: {
                title: '고품질 압축기 소리 라벨링 가이드',
                description: '실제 압축기와 유사한 고품질 합성음으로 정확한 분류를 수행하세요.',
                steps: [
                    '1. 고품질 합성음을 재생하여 들어보세요',
                    '2. 실제 압축기 경험을 바탕으로 분류하세요',
                    '3. 신뢰도 점수를 설정하세요 (0-100%)',
                    '4. 소리의 특징과 품질을 메모에 기록하세요'
                ],
                categories: this.compressorTypes
            }
        };

        // 고품질 소리 파일들 정리
        for (const category of Object.keys(this.compressorTypes)) {
            const categoryDir = path.join(this.outputDir, category);
            
            if (fs.existsSync(categoryDir)) {
                const files = fs.readdirSync(categoryDir).filter(f => f.endsWith('.wav'));
                for (const file of files) {
                    const filepath = path.join(categoryDir, file);
                    const stats = fs.statSync(filepath);
                    
                    labelingData.high_quality_sounds.push({
                        filename: file,
                        category: category,
                        category_name: this.compressorTypes[category].description,
                        type: 'high_quality_synthetic',
                        path: filepath,
                        size: stats.size,
                        duration: 5,
                        sample_rate: this.sampleRate,
                        channels: 1,
                        bit_depth: this.bitDepth,
                        quality: 'high',
                        status: 'pending',
                        engineer_label: null,
                        engineer_confidence: null,
                        engineer_notes: null,
                        labeled_at: null
                    });
                }
            }
        }

        labelingData.total_files = labelingData.high_quality_sounds.length;

        // 라벨링 데이터 저장
        await this.writeFile(
            path.join(this.outputDir, 'labeling_data.json'),
            JSON.stringify(labelingData, null, 2)
        );

        console.log(`   ✅ ${labelingData.total_files}개 고품질 소리 파일 준비 완료`);
        console.log(`   📊 카테고리별 분포:`);
        
        for (const category of Object.keys(this.compressorTypes)) {
            const count = labelingData.high_quality_sounds.filter(s => s.category === category).length;
            console.log(`      - ${this.compressorTypes[category].description}: ${count}개`);
        }
    }

    async saveWavFile(filepath, audioData) {
        const numChannels = 1;
        const bitsPerSample = 16;
        const byteRate = this.sampleRate * numChannels * bitsPerSample / 8;
        const blockAlign = numChannels * bitsPerSample / 8;
        const dataSize = audioData.length * blockAlign;
        const fileSize = 44 + dataSize;

        const buffer = Buffer.alloc(44 + dataSize);
        let offset = 0;

        // WAV 헤더 작성
        buffer.write('RIFF', offset); offset += 4;
        buffer.writeUInt32LE(fileSize - 8, offset); offset += 4;
        buffer.write('WAVE', offset); offset += 4;
        buffer.write('fmt ', offset); offset += 4;
        buffer.writeUInt32LE(16, offset); offset += 4;
        buffer.writeUInt16LE(1, offset); offset += 2;
        buffer.writeUInt16LE(numChannels, offset); offset += 2;
        buffer.writeUInt32LE(this.sampleRate, offset); offset += 4;
        buffer.writeUInt32LE(byteRate, offset); offset += 4;
        buffer.writeUInt16LE(blockAlign, offset); offset += 2;
        buffer.writeUInt16LE(bitsPerSample, offset); offset += 2;
        buffer.write('data', offset); offset += 4;
        buffer.writeUInt32LE(dataSize, offset); offset += 4;

        // 오디오 데이터 작성
        for (let i = 0; i < audioData.length; i++) {
            const sample = Math.max(-1, Math.min(1, audioData[i]));
            const intSample = Math.round(sample * 32767);
            buffer.writeInt16LE(intSample, offset);
            offset += 2;
        }

        await this.writeFile(filepath, buffer);
    }

    async ensureDir(dir) {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    }

    async writeFile(filepath, data) {
        return new Promise((resolve, reject) => {
            fs.writeFile(filepath, data, (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }
}

// 메인 실행
async function main() {
    const synthesizer = new OptimizedCompressorSynthesizer();
    await synthesizer.run();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = OptimizedCompressorSynthesizer;
