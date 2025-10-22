#!/usr/bin/env node
/**
 * 고품질 압축기 합성음 생성 시스템
 * 실제 압축기의 물리적 특성을 반영한 현실적인 소리 생성
 */

const fs = require('fs');
const path = require('path');

class HighQualityCompressorSynthesizer {
    constructor() {
        this.outputDir = 'data/high_quality_sounds';
        this.sampleRate = 44100; // CD 품질
        this.bitDepth = 16;
        
        // 실제 압축기 특성 파라미터
        this.compressorCharacteristics = {
            // 정상 압축기
            normal_compressor: {
                baseFreq: 60,           // 기본 주파수 (Hz)
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20], // 고조파
                harmonicAmps: [0.8, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08, 0.05, 0.03],
                noiseLevel: 0.05,       // 노이즈 레벨
                modulation: 0.02,       // 주파수 변조
                attack: 0.1,            // 어택 시간
                decay: 0.3,             // 디케이 시간
                sustain: 0.7,           // 서스테인 레벨
                release: 0.5,           // 릴리즈 시간
                vibrato: 0.5,           // 비브라토 깊이
                tremolo: 0.1,           // 트레몰로 깊이
                description: '정상적인 압축기 작동음 - 일정한 저주파 소음과 안정적인 고조파'
            },
            
            // 정상 팬
            normal_fan: {
                baseFreq: 400,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08, 0.05, 0.03, 0.02],
                noiseLevel: 0.08,
                modulation: 0.03,
                attack: 0.05,
                decay: 0.2,
                sustain: 0.8,
                release: 0.3,
                vibrato: 0.3,
                tremolo: 0.05,
                description: '정상적인 팬 회전음 - 부드러운 중주파 소음과 일정한 회전음'
            },
            
            // 정상 모터
            normal_motor: {
                baseFreq: 150,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.7, 0.5, 0.35, 0.25, 0.18, 0.12, 0.08, 0.05, 0.03, 0.02],
                noiseLevel: 0.06,
                modulation: 0.025,
                attack: 0.08,
                decay: 0.25,
                sustain: 0.75,
                release: 0.4,
                vibrato: 0.4,
                tremolo: 0.08,
                description: '정상적인 모터 구동음 - 안정적인 저주파 소음과 일정한 구동음'
            },
            
            // 베어링 마모
            abnormal_bearing: {
                baseFreq: 3000,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.9, 0.7, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1, 0.08],
                noiseLevel: 0.15,
                modulation: 0.1,
                attack: 0.02,
                decay: 0.1,
                sustain: 0.9,
                release: 0.2,
                vibrato: 1.0,
                tremolo: 0.2,
                description: '베어링 마모로 인한 이상 소음 - 불규칙한 고주파 진동과 마찰음'
            },
            
            // 언밸런스
            abnormal_unbalance: {
                baseFreq: 200,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.8, 0.6, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08, 0.05, 0.03],
                noiseLevel: 0.12,
                modulation: 0.15,
                attack: 0.05,
                decay: 0.2,
                sustain: 0.8,
                release: 0.3,
                vibrato: 0.8,
                tremolo: 0.3,
                description: '언밸런스로 인한 진동 소음 - 주기적 진동과 불균형 소음'
            },
            
            // 마찰
            abnormal_friction: {
                baseFreq: 1500,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [0.7, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1, 0.08, 0.05],
                noiseLevel: 0.2,
                modulation: 0.08,
                attack: 0.03,
                decay: 0.15,
                sustain: 0.85,
                release: 0.25,
                vibrato: 0.6,
                tremolo: 0.15,
                description: '마찰로 인한 이상 소음 - 불규칙한 중주파와 마찰음'
            },
            
            // 과부하
            abnormal_overload: {
                baseFreq: 100,
                harmonics: [2, 3, 4, 5, 6, 8, 10, 12, 15, 20],
                harmonicAmps: [1.0, 0.8, 0.6, 0.5, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15],
                noiseLevel: 0.25,
                modulation: 0.2,
                attack: 0.01,
                decay: 0.05,
                sustain: 0.95,
                release: 0.1,
                vibrato: 1.2,
                tremolo: 0.4,
                description: '과부하 상태의 이상 소음 - 매우 강한 소음과 불규칙한 노이즈'
            }
        };
    }

    async run() {
        console.log('🎵 고품질 압축기 합성음 생성 시스템');
        console.log('='.repeat(60));
        console.log('실제 압축기의 물리적 특성을 반영한 현실적인 소리 생성');
        console.log('='.repeat(60));

        try {
            // 디렉토리 생성
            await this.createDirectories();

            // 각 카테고리별 고품질 합성음 생성
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
        
        // 각 카테고리별 디렉토리 생성
        for (const category of Object.keys(this.compressorCharacteristics)) {
            await this.ensureDir(path.join(this.outputDir, category));
        }
        
        console.log('   ✅ 디렉토리 생성 완료');
    }

    async generateHighQualitySounds() {
        console.log('   🎼 고품질 합성음 생성 중...');
        
        let totalGenerated = 0;
        
        for (const [category, characteristics] of Object.entries(this.compressorCharacteristics)) {
            console.log(`   📥 ${characteristics.description} 생성 중...`);
            
            // 각 카테고리별로 5개씩 생성 (다양한 변형)
            for (let i = 1; i <= 5; i++) {
                const filename = `${category}_hq_${i}.wav`;
                const filepath = path.join(this.outputDir, category, filename);
                
                try {
                    // 고품질 합성음 생성
                    const audioData = this.generateHighQualitySound(characteristics, i);
                    
                    // WAV 파일로 저장
                    await this.saveWavFile(filepath, audioData, this.sampleRate);
                    totalGenerated++;
                } catch (error) {
                    console.log(`   ⚠️ 생성 실패: ${filename}`);
                }
            }
        }

        console.log(`   ✅ ${totalGenerated}개 고품질 합성음 생성 완료`);
    }

    generateHighQualitySound(characteristics, variant) {
        const duration = 8; // 8초
        const samples = Math.floor(this.sampleRate * duration);
        const t = this.linspace(0, duration, samples);
        
        // 기본 신호 생성
        let signal = new Float32Array(samples);
        
        // 기본 주파수와 고조파 생성
        for (let i = 0; i < characteristics.harmonics.length; i++) {
            const freq = characteristics.baseFreq * characteristics.harmonics[i];
            const amp = characteristics.harmonicAmps[i];
            
            // 주파수 변조 (vibrato)
            const vibrato = characteristics.vibrato * Math.sin(2 * Math.PI * 0.5 * t);
            const modulatedFreq = freq * (1 + vibrato);
            
            // 진폭 변조 (tremolo)
            const tremolo = 1 + characteristics.tremolo * Math.sin(2 * Math.PI * 0.3 * t);
            
            // 기본 고조파 신호
            const harmonic = this.sin(this.multiplyArray(t, 2 * Math.PI * modulatedFreq));
            signal = this.addArrays(signal, this.multiplyArray(harmonic, amp * tremolo));
        }
        
        // ADSR 엔벨로프 적용
        const envelope = this.generateADSR(samples, characteristics);
        signal = this.multiplyArrays(signal, envelope);
        
        // 노이즈 추가
        const noise = this.generateNoise(samples, characteristics.noiseLevel);
        signal = this.addArrays(signal, noise);
        
        // 변형별 특수 효과 적용
        signal = this.applyVariantEffects(signal, characteristics, variant);
        
        // 정규화
        signal = this.normalize(signal);
        
        return signal;
    }

    generateADSR(samples, characteristics) {
        const envelope = new Float32Array(samples);
        const attackSamples = Math.floor(characteristics.attack * this.sampleRate);
        const decaySamples = Math.floor(characteristics.decay * this.sampleRate);
        const releaseSamples = Math.floor(characteristics.release * this.sampleRate);
        const sustainSamples = samples - attackSamples - decaySamples - releaseSamples;
        
        let sampleIndex = 0;
        
        // Attack
        for (let i = 0; i < attackSamples; i++) {
            envelope[sampleIndex] = i / attackSamples;
            sampleIndex++;
        }
        
        // Decay
        for (let i = 0; i < decaySamples; i++) {
            const decayProgress = i / decaySamples;
            envelope[sampleIndex] = 1 - (1 - characteristics.sustain) * decayProgress;
            sampleIndex++;
        }
        
        // Sustain
        for (let i = 0; i < sustainSamples; i++) {
            envelope[sampleIndex] = characteristics.sustain;
            sampleIndex++;
        }
        
        // Release
        for (let i = 0; i < releaseSamples; i++) {
            const releaseProgress = i / releaseSamples;
            envelope[sampleIndex] = characteristics.sustain * (1 - releaseProgress);
            sampleIndex++;
        }
        
        return envelope;
    }

    applyVariantEffects(signal, characteristics, variant) {
        const samples = signal.length;
        const t = this.linspace(0, samples / this.sampleRate, samples);
        
        // 변형별 특수 효과
        switch (variant) {
            case 1: // 기본 변형
                break;
                
            case 2: // 주파수 변조 강화
                const freqMod = 0.1 * Math.sin(2 * Math.PI * 0.2 * t);
                signal = this.multiplyArray(signal, 1 + freqMod);
                break;
                
            case 3: // 진폭 변조 강화
                const ampMod = 0.2 * Math.sin(2 * Math.PI * 0.15 * t);
                signal = this.multiplyArray(signal, 1 + ampMod);
                break;
                
            case 4: // 노이즈 레벨 증가
                const extraNoise = this.generateNoise(samples, characteristics.noiseLevel * 0.5);
                signal = this.addArrays(signal, extraNoise);
                break;
                
            case 5: // 복합 효과
                const complexMod = 0.05 * Math.sin(2 * Math.PI * 0.1 * t) + 
                                  0.03 * Math.sin(2 * Math.PI * 0.25 * t);
                signal = this.multiplyArray(signal, 1 + complexMod);
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
        const max = Math.max(...signal.map(Math.abs));
        if (max > 0) {
            return signal.map(x => x / max * 0.8); // 0.8로 정규화 (클리핑 방지)
        }
        return signal;
    }

    async prepareLabelingData() {
        console.log('   📋 라벨링용 데이터 준비 중...');
        
        const labelingData = {
            high_quality_sounds: [],
            total_files: 0,
            categories: Object.keys(this.compressorCharacteristics),
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
                categories: this.compressorCharacteristics
            }
        };

        // 고품질 소리 파일들 정리
        for (const category of Object.keys(this.compressorCharacteristics)) {
            const categoryDir = path.join(this.outputDir, category);
            
            if (fs.existsSync(categoryDir)) {
                const files = fs.readdirSync(categoryDir).filter(f => f.endsWith('.wav'));
                for (const file of files) {
                    const filepath = path.join(categoryDir, file);
                    const stats = fs.statSync(filepath);
                    
                    labelingData.high_quality_sounds.push({
                        filename: file,
                        category: category,
                        category_name: this.compressorCharacteristics[category].description,
                        type: 'high_quality_synthetic',
                        path: filepath,
                        size: stats.size,
                        duration: 8, // 8초
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
        
        for (const category of Object.keys(this.compressorCharacteristics)) {
            const count = labelingData.high_quality_sounds.filter(s => s.category === category).length;
            console.log(`      - ${this.compressorCharacteristics[category].description}: ${count}개`);
        }
    }

    // 유틸리티 함수들
    linspace(start, end, num) {
        const result = new Float32Array(num);
        const step = (end - start) / (num - 1);
        for (let i = 0; i < num; i++) {
            result[i] = start + i * step;
        }
        return result;
    }

    sin(array) {
        return array.map(x => Math.sin(x));
    }

    multiplyArray(array, scalar) {
        return array.map(x => x * scalar);
    }

    multiplyArrays(array1, array2) {
        return array1.map((x, i) => x * array2[i]);
    }

    addArrays(array1, array2) {
        return array1.map((x, i) => x + array2[i]);
    }

    async saveWavFile(filepath, audioData, sampleRate) {
        const numChannels = 1;
        const bitsPerSample = 16;
        const byteRate = sampleRate * numChannels * bitsPerSample / 8;
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
        buffer.writeUInt32LE(16, offset); offset += 4; // fmt chunk size
        buffer.writeUInt16LE(1, offset); offset += 2; // audio format (PCM)
        buffer.writeUInt16LE(numChannels, offset); offset += 2;
        buffer.writeUInt32LE(sampleRate, offset); offset += 4;
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
    const synthesizer = new HighQualityCompressorSynthesizer();
    await synthesizer.run();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = HighQualityCompressorSynthesizer;
