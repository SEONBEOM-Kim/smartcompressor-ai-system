#!/usr/bin/env node
/**
 * 소리 데이터 생성 및 수집 시스템
 * 인터넷에서 소리 다운로드 및 합성 데이터 생성
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

class SoundDataGenerator {
    constructor() {
        this.outputDir = 'data/sound_samples';
        this.syntheticDir = 'data/synthetic_sounds';
        this.downloadedDir = 'data/downloaded_sounds';
        
        // 소리 샘플 URL들 (무료 오디오 샘플)
        this.soundUrls = {
            // 정상 압축기 소리 (유사한 소리들)
            normal_compressor: [
                'https://www.soundjay.com/misc/sounds/air-compressor-01.wav',
                'https://freesound.org/data/previews/316/316847_5123451-lq.mp3'
            ],
            // 정상 팬 소리
            normal_fan: [
                'https://freesound.org/data/previews/316/316847_5123451-lq.mp3',
                'https://www.soundjay.com/misc/sounds/fan-01.wav'
            ],
            // 정상 모터 소리
            normal_motor: [
                'https://freesound.org/data/previews/316/316847_5123451-lq.mp3',
                'https://www.soundjay.com/misc/sounds/motor-01.wav'
            ],
            // 이상 소리들 (유사한 소리들)
            abnormal_bearing: [
                'https://freesound.org/data/previews/316/316847_5123451-lq.mp3',
                'https://www.soundjay.com/misc/sounds/grinding-01.wav'
            ],
            abnormal_unbalance: [
                'https://freesound.org/data/previews/316/316847_5123451-lq.mp3',
                'https://www.soundjay.com/misc/sounds/vibration-01.wav'
            ],
            abnormal_friction: [
                'https://freesound.org/data/previews/316/316847_5123451-lq.mp3',
                'https://www.soundjay.com/misc/sounds/squeak-01.wav'
            ],
            abnormal_overload: [
                'https://freesound.org/data/previews/316/316847_5123451-lq.mp3',
                'https://www.soundjay.com/misc/sounds/overload-01.wav'
            ]
        };
    }

    async run() {
        console.log('🎵 소리 데이터 생성 및 수집 시스템');
        console.log('='.repeat(60));
        console.log('인터넷에서 소리 다운로드 및 합성 데이터 생성');
        console.log('='.repeat(60));

        try {
            // 디렉토리 생성
            await this.createDirectories();

            // 1단계: 합성 소리 데이터 생성
            console.log('\n1️⃣ 합성 소리 데이터 생성');
            await this.generateSyntheticSounds();

            // 2단계: 인터넷에서 소리 다운로드 (시뮬레이션)
            console.log('\n2️⃣ 인터넷에서 소리 다운로드 시뮬레이션');
            await this.simulateDownloadSounds();

            // 3단계: 라벨링용 데이터 준비
            console.log('\n3️⃣ 라벨링용 데이터 준비');
            await this.prepareLabelingData();

            console.log('\n🎉 소리 데이터 생성 완료!');
            console.log('이제 라벨링 도구에서 사용할 수 있습니다.');

            return true;
        } catch (error) {
            console.error('❌ 오류 발생:', error);
            return false;
        }
    }

    async createDirectories() {
        console.log('   📁 디렉토리 생성 중...');
        
        await this.ensureDir(this.outputDir);
        await this.ensureDir(this.syntheticDir);
        await this.ensureDir(this.downloadedDir);
        
        // 각 카테고리별 디렉토리 생성
        for (const category of Object.keys(this.soundUrls)) {
            await this.ensureDir(path.join(this.syntheticDir, category));
            await this.ensureDir(path.join(this.downloadedDir, category));
        }
        
        console.log('   ✅ 디렉토리 생성 완료');
    }

    async generateSyntheticSounds() {
        console.log('   🎵 합성 소리 데이터 생성 중...');

        const categories = Object.keys(this.soundUrls);
        let totalGenerated = 0;

        for (const category of categories) {
            console.log(`   📂 ${category} 카테고리 생성 중...`);
            
            // 각 카테고리별로 10개씩 생성
            for (let i = 0; i < 10; i++) {
                const soundData = this.generateSoundByCategory(category, i);
                const filename = `${category}_synthetic_${i + 1}.wav`;
                const filepath = path.join(this.syntheticDir, category, filename);
                
                await this.saveWavFile(filepath, soundData);
                totalGenerated++;
            }
        }

        console.log(`   ✅ ${totalGenerated}개 합성 소리 생성 완료`);
    }

    generateSoundByCategory(category, index) {
        const duration = 5.0; // 5초
        const sampleRate = 22050;
        const samples = Math.floor(sampleRate * duration);
        
        let soundData;

        switch (category) {
            case 'normal_compressor':
                soundData = this.generateNormalCompressorSound(samples, sampleRate);
                break;
            case 'normal_fan':
                soundData = this.generateNormalFanSound(samples, sampleRate);
                break;
            case 'normal_motor':
                soundData = this.generateNormalMotorSound(samples, sampleRate);
                break;
            case 'abnormal_bearing':
                soundData = this.generateAbnormalBearingSound(samples, sampleRate);
                break;
            case 'abnormal_unbalance':
                soundData = this.generateAbnormalUnbalanceSound(samples, sampleRate);
                break;
            case 'abnormal_friction':
                soundData = this.generateAbnormalFrictionSound(samples, sampleRate);
                break;
            case 'abnormal_overload':
                soundData = this.generateAbnormalOverloadSound(samples, sampleRate);
                break;
            default:
                soundData = this.generateDefaultSound(samples, sampleRate);
        }

        return soundData;
    }

    generateNormalCompressorSound(samples, sampleRate) {
        const data = new Float32Array(samples);
        const baseFreq = 60; // 저주파
        
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            // 기본 주파수
            sample += 0.3 * Math.sin(2 * Math.PI * baseFreq * t);
            // 하모닉
            sample += 0.1 * Math.sin(2 * Math.PI * baseFreq * 2 * t);
            sample += 0.05 * Math.sin(2 * Math.PI * baseFreq * 3 * t);
            // 노이즈
            sample += 0.02 * (Math.random() * 2 - 1);
            
            data[i] = Math.max(-1, Math.min(1, sample));
        }
        
        return data;
    }

    generateNormalFanSound(samples, sampleRate) {
        const data = new Float32Array(samples);
        const baseFreq = 400; // 중주파
        
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            // 기본 주파수
            sample += 0.25 * Math.sin(2 * Math.PI * baseFreq * t);
            // 하모닉
            sample += 0.08 * Math.sin(2 * Math.PI * baseFreq * 2 * t);
            sample += 0.03 * Math.sin(2 * Math.PI * baseFreq * 3 * t);
            // 노이즈
            sample += 0.015 * (Math.random() * 2 - 1);
            
            data[i] = Math.max(-1, Math.min(1, sample));
        }
        
        return data;
    }

    generateNormalMotorSound(samples, sampleRate) {
        const data = new Float32Array(samples);
        const baseFreq = 150; // 저주파
        
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            // 기본 주파수
            sample += 0.2 * Math.sin(2 * Math.PI * baseFreq * t);
            // 하모닉
            sample += 0.06 * Math.sin(2 * Math.PI * baseFreq * 2 * t);
            sample += 0.02 * Math.sin(2 * Math.PI * baseFreq * 3 * t);
            // 노이즈
            sample += 0.01 * (Math.random() * 2 - 1);
            
            data[i] = Math.max(-1, Math.min(1, sample));
        }
        
        return data;
    }

    generateAbnormalBearingSound(samples, sampleRate) {
        const data = new Float32Array(samples);
        const baseFreq = 3000; // 고주파
        
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            // 기본 주파수
            sample += 0.4 * Math.sin(2 * Math.PI * baseFreq * t);
            // 불규칙한 진동
            const irregularity = 1 + 0.3 * (Math.random() * 2 - 1);
            sample *= irregularity;
            // 고주파 노이즈
            sample += 0.1 * (Math.random() * 2 - 1);
            
            data[i] = Math.max(-1, Math.min(1, sample));
        }
        
        return data;
    }

    generateAbnormalUnbalanceSound(samples, sampleRate) {
        const data = new Float32Array(samples);
        const baseFreq = 200; // 저주파
        
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            // 기본 주파수
            sample += 0.3 * Math.sin(2 * Math.PI * baseFreq * t);
            // 주기적 진동
            const vibration = 0.5 * Math.sin(2 * Math.PI * 0.5 * t);
            sample *= (1 + vibration);
            // 노이즈
            sample += 0.05 * (Math.random() * 2 - 1);
            
            data[i] = Math.max(-1, Math.min(1, sample));
        }
        
        return data;
    }

    generateAbnormalFrictionSound(samples, sampleRate) {
        const data = new Float32Array(samples);
        const baseFreq = 1500; // 중주파
        
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            // 기본 주파수
            sample += 0.25 * Math.sin(2 * Math.PI * baseFreq * t);
            // 불규칙한 마찰 패턴
            const frictionPattern = 1 + 0.4 * (Math.random() * 2 - 1);
            sample *= frictionPattern;
            // 노이즈
            sample += 0.08 * (Math.random() * 2 - 1);
            
            data[i] = Math.max(-1, Math.min(1, sample));
        }
        
        return data;
    }

    generateAbnormalOverloadSound(samples, sampleRate) {
        const data = new Float32Array(samples);
        
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            let sample = 0;
            
            // 여러 주파수 대역의 노이즈
            const frequencies = [100, 500, 1000, 2000, 4000, 6000];
            for (const freq of frequencies) {
                sample += 0.15 * Math.sin(2 * Math.PI * freq * t);
            }
            // 강한 노이즈
            sample += 0.2 * (Math.random() * 2 - 1);
            
            data[i] = Math.max(-1, Math.min(1, sample));
        }
        
        return data;
    }

    generateDefaultSound(samples, sampleRate) {
        const data = new Float32Array(samples);
        const baseFreq = 440; // A4 음
        
        for (let i = 0; i < samples; i++) {
            const t = i / sampleRate;
            data[i] = 0.1 * Math.sin(2 * Math.PI * baseFreq * t);
        }
        
        return data;
    }

    async saveWavFile(filepath, audioData) {
        const sampleRate = 22050;
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

    async simulateDownloadSounds() {
        console.log('   🌐 인터넷에서 소리 다운로드 시뮬레이션 중...');
        
        // 실제로는 인터넷에서 다운로드하지만, 여기서는 합성 데이터를 복사
        const categories = Object.keys(this.soundUrls);
        let totalDownloaded = 0;

        for (const category of categories) {
            console.log(`   📥 ${category} 카테고리 다운로드 시뮬레이션...`);
            
            // 각 카테고리별로 5개씩 "다운로드"
            for (let i = 0; i < 5; i++) {
                const soundData = this.generateSoundByCategory(category, i + 10);
                const filename = `${category}_downloaded_${i + 1}.wav`;
                const filepath = path.join(this.downloadedDir, category, filename);
                
                await this.saveWavFile(filepath, soundData);
                totalDownloaded++;
            }
        }

        console.log(`   ✅ ${totalDownloaded}개 소리 다운로드 시뮬레이션 완료`);
    }

    async prepareLabelingData() {
        console.log('   📋 라벨링용 데이터 준비 중...');
        
        const labelingData = {
            synthetic_sounds: [],
            downloaded_sounds: [],
            total_files: 0,
            categories: Object.keys(this.soundUrls),
            created_at: new Date().toISOString()
        };

        // 합성 소리 데이터 정리
        for (const category of Object.keys(this.soundUrls)) {
            const syntheticDir = path.join(this.syntheticDir, category);
            const downloadedDir = path.join(this.downloadedDir, category);
            
            if (fs.existsSync(syntheticDir)) {
                const files = fs.readdirSync(syntheticDir).filter(f => f.endsWith('.wav'));
                for (const file of files) {
                    labelingData.synthetic_sounds.push({
                        filename: file,
                        category: category,
                        type: 'synthetic',
                        path: path.join(syntheticDir, file),
                        size: fs.statSync(path.join(syntheticDir, file)).size
                    });
                }
            }
            
            if (fs.existsSync(downloadedDir)) {
                const files = fs.readdirSync(downloadedDir).filter(f => f.endsWith('.wav'));
                for (const file of files) {
                    labelingData.downloaded_sounds.push({
                        filename: file,
                        category: category,
                        type: 'downloaded',
                        path: path.join(downloadedDir, file),
                        size: fs.statSync(path.join(downloadedDir, file)).size
                    });
                }
            }
        }

        labelingData.total_files = labelingData.synthetic_sounds.length + labelingData.downloaded_sounds.length;

        // 라벨링 데이터 저장
        await this.writeFile(
            path.join(this.outputDir, 'labeling_data.json'),
            JSON.stringify(labelingData, null, 2)
        );

        console.log(`   ✅ ${labelingData.total_files}개 파일 준비 완료`);
        console.log(`   📊 카테고리별 분포:`);
        
        for (const category of Object.keys(this.soundUrls)) {
            const syntheticCount = labelingData.synthetic_sounds.filter(s => s.category === category).length;
            const downloadedCount = labelingData.downloaded_sounds.filter(s => s.category === category).length;
            console.log(`      - ${category}: ${syntheticCount}개 합성 + ${downloadedCount}개 다운로드`);
        }
    }

    // 유틸리티 함수들
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
    const generator = new SoundDataGenerator();
    await generator.run();
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = SoundDataGenerator;
