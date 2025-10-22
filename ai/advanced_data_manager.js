#!/usr/bin/env node
/**
 * 고급 데이터 관리 시스템
 * 엔지니어 라벨링 데이터를 효율적으로 관리
 */

const fs = require('fs');
const path = require('path');

class AdvancedDataManager {
    constructor() {
        this.dataDir = 'data/engineer_labeling';
        this.backupDir = 'data/backups';
        this.exportDir = 'data/exports';
        
        // 데이터 구조
        this.dataStructure = {
            engineer_info: {
                name: '',
                experience_years: 0,
                specialization: '',
                company: '',
                last_updated: ''
            },
            labeling_sessions: [],
            sound_files: {},
            ai_training_data: {},
            statistics: {
                total_files: 0,
                labeled_files: 0,
                normal_count: 0,
                abnormal_count: 0,
                average_confidence: 0,
                last_updated: ''
            }
        };
    }

    async initialize() {
        console.log('🔧 고급 데이터 관리 시스템 초기화');
        
        // 디렉토리 생성
        await this.ensureDir(this.dataDir);
        await this.ensureDir(this.backupDir);
        await this.ensureDir(this.exportDir);
        
        // 기존 데이터 로드
        await this.loadExistingData();
        
        console.log('✅ 데이터 관리 시스템 초기화 완료');
    }

    async loadExistingData() {
        const dataFile = path.join(this.dataDir, 'engineer_labeling_data.json');
        
        if (fs.existsSync(dataFile)) {
            try {
                const data = JSON.parse(fs.readFileSync(dataFile, 'utf8'));
                this.dataStructure = { ...this.dataStructure, ...data };
                console.log('📚 기존 라벨링 데이터 로드 완료');
            } catch (error) {
                console.log('⚠️ 기존 데이터 로드 실패, 새로 시작합니다.');
            }
        }
    }

    async saveData() {
        const dataFile = path.join(this.dataDir, 'engineer_labeling_data.json');
        const backupFile = path.join(this.backupDir, `backup_${new Date().toISOString().split('T')[0]}.json`);
        
        try {
            // 백업 생성
            if (fs.existsSync(dataFile)) {
                fs.copyFileSync(dataFile, backupFile);
            }
            
            // 데이터 저장
            this.dataStructure.statistics.last_updated = new Date().toISOString();
            fs.writeFileSync(dataFile, JSON.stringify(this.dataStructure, null, 2), 'utf8');
            
            console.log('💾 데이터 저장 완료');
            return true;
        } catch (error) {
            console.error('❌ 데이터 저장 실패:', error);
            return false;
        }
    }

    async addLabelingSession(sessionData) {
        const session = {
            id: `session_${Date.now()}`,
            timestamp: new Date().toISOString(),
            files_labeled: sessionData.files.length,
            duration_minutes: sessionData.duration || 0,
            files: sessionData.files
        };
        
        this.dataStructure.labeling_sessions.push(session);
        
        // 파일별 데이터 업데이트
        for (const file of sessionData.files) {
            this.dataStructure.sound_files[file.filename] = {
                ...file,
                session_id: session.id,
                last_updated: new Date().toISOString()
            };
        }
        
        // 통계 업데이트
        this.updateStatistics();
        
        await this.saveData();
        return session;
    }

    updateStatistics() {
        const allFiles = Object.values(this.dataStructure.sound_files);
        const labeledFiles = allFiles.filter(f => f.label);
        
        this.dataStructure.statistics = {
            total_files: allFiles.length,
            labeled_files: labeledFiles.length,
            normal_count: labeledFiles.filter(f => f.label && f.label.startsWith('normal')).length,
            abnormal_count: labeledFiles.filter(f => f.label && f.label.startsWith('abnormal')).length,
            average_confidence: labeledFiles.length > 0 ? 
                labeledFiles.reduce((sum, f) => sum + (f.confidence || 0), 0) / labeledFiles.length : 0,
            last_updated: new Date().toISOString()
        };
    }

    async exportForAITraining() {
        const labeledFiles = Object.values(this.dataStructure.sound_files)
            .filter(f => f.label && f.confidence);
        
        const trainingData = {
            metadata: {
                export_date: new Date().toISOString(),
                engineer_info: this.dataStructure.engineer_info,
                total_samples: labeledFiles.length,
                categories: [...new Set(labeledFiles.map(f => f.label))],
                average_confidence: this.dataStructure.statistics.average_confidence
            },
            samples: labeledFiles.map(file => ({
                filename: file.filename,
                label: file.label,
                confidence: file.confidence,
                notes: file.notes || '',
                features: file.features || [],
                timestamp: file.timestamp
            })),
            statistics: {
                by_category: this.getCategoryStatistics(labeledFiles),
                by_confidence: this.getConfidenceStatistics(labeledFiles),
                by_session: this.getSessionStatistics()
            }
        };
        
        const exportFile = path.join(this.exportDir, `ai_training_data_${new Date().toISOString().split('T')[0]}.json`);
        fs.writeFileSync(exportFile, JSON.stringify(trainingData, null, 2), 'utf8');
        
        console.log(`📤 AI 훈련용 데이터 내보내기 완료: ${exportFile}`);
        return trainingData;
    }

    getCategoryStatistics(files) {
        const stats = {};
        files.forEach(file => {
            if (!stats[file.label]) {
                stats[file.label] = { count: 0, avg_confidence: 0, confidences: [] };
            }
            stats[file.label].count++;
            stats[file.label].confidences.push(file.confidence);
        });
        
        Object.keys(stats).forEach(category => {
            const confidences = stats[category].confidences;
            stats[category].avg_confidence = confidences.reduce((a, b) => a + b, 0) / confidences.length;
        });
        
        return stats;
    }

    getConfidenceStatistics(files) {
        const confidences = files.map(f => f.confidence);
        return {
            min: Math.min(...confidences),
            max: Math.max(...confidences),
            avg: confidences.reduce((a, b) => a + b, 0) / confidences.length,
            high_confidence: confidences.filter(c => c >= 0.8).length,
            medium_confidence: confidences.filter(c => c >= 0.6 && c < 0.8).length,
            low_confidence: confidences.filter(c => c < 0.6).length
        };
    }

    getSessionStatistics() {
        return this.dataStructure.labeling_sessions.map(session => ({
            id: session.id,
            date: session.timestamp.split('T')[0],
            files_labeled: session.files_labeled,
            duration_minutes: session.duration_minutes
        }));
    }

    async generateReport() {
        const report = {
            title: '엔지니어 라벨링 데이터 보고서',
            generated_at: new Date().toISOString(),
            engineer_info: this.dataStructure.engineer_info,
            summary: this.dataStructure.statistics,
            detailed_analysis: {
                category_distribution: this.getCategoryStatistics(Object.values(this.dataStructure.sound_files).filter(f => f.label)),
                confidence_analysis: this.getConfidenceStatistics(Object.values(this.dataStructure.sound_files).filter(f => f.label)),
                session_analysis: this.getSessionStatistics(),
                quality_metrics: this.calculateQualityMetrics()
            },
            recommendations: this.generateRecommendations()
        };
        
        const reportFile = path.join(this.exportDir, `labeling_report_${new Date().toISOString().split('T')[0]}.json`);
        fs.writeFileSync(reportFile, JSON.stringify(report, null, 2), 'utf8');
        
        console.log(`📊 라벨링 보고서 생성 완료: ${reportFile}`);
        return report;
    }

    calculateQualityMetrics() {
        const labeledFiles = Object.values(this.dataStructure.sound_files).filter(f => f.label);
        
        return {
            completion_rate: this.dataStructure.statistics.labeled_files / this.dataStructure.statistics.total_files,
            average_confidence: this.dataStructure.statistics.average_confidence,
            consistency_score: this.calculateConsistencyScore(labeledFiles),
            data_quality: this.assessDataQuality(labeledFiles)
        };
    }

    calculateConsistencyScore(files) {
        // 같은 카테고리 파일들의 신뢰도 일관성 계산
        const categoryGroups = {};
        files.forEach(file => {
            if (!categoryGroups[file.label]) {
                categoryGroups[file.label] = [];
            }
            categoryGroups[file.label].push(file.confidence);
        });
        
        let totalVariance = 0;
        let groupCount = 0;
        
        Object.values(categoryGroups).forEach(confidences => {
            if (confidences.length > 1) {
                const avg = confidences.reduce((a, b) => a + b, 0) / confidences.length;
                const variance = confidences.reduce((sum, conf) => sum + Math.pow(conf - avg, 2), 0) / confidences.length;
                totalVariance += variance;
                groupCount++;
            }
        });
        
        return groupCount > 0 ? Math.max(0, 1 - (totalVariance / groupCount)) : 1;
    }

    assessDataQuality(files) {
        const quality = {
            has_notes: files.filter(f => f.notes && f.notes.trim()).length / files.length,
            high_confidence: files.filter(f => f.confidence >= 0.8).length / files.length,
            balanced_categories: this.checkCategoryBalance(files),
            recent_data: files.filter(f => {
                const fileDate = new Date(f.timestamp);
                const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
                return fileDate > weekAgo;
            }).length / files.length
        };
        
        return quality;
    }

    checkCategoryBalance(files) {
        const categoryCounts = {};
        files.forEach(file => {
            categoryCounts[file.label] = (categoryCounts[file.label] || 0) + 1;
        });
        
        const counts = Object.values(categoryCounts);
        const max = Math.max(...counts);
        const min = Math.min(...counts);
        
        return min / max; // 1에 가까울수록 균형잡힘
    }

    generateRecommendations() {
        const stats = this.dataStructure.statistics;
        const recommendations = [];
        
        if (stats.labeled_files < stats.total_files * 0.5) {
            recommendations.push('라벨링 완료율이 50% 미만입니다. 더 많은 파일을 라벨링해주세요.');
        }
        
        if (stats.average_confidence < 0.7) {
            recommendations.push('평균 신뢰도가 낮습니다. 더 확신 있는 분류를 위해 추가 검토가 필요합니다.');
        }
        
        if (stats.normal_count === 0 || stats.abnormal_count === 0) {
            recommendations.push('정상 또는 이상 데이터가 부족합니다. 균형잡힌 데이터셋을 위해 더 다양한 샘플이 필요합니다.');
        }
        
        if (recommendations.length === 0) {
            recommendations.push('데이터 품질이 우수합니다. AI 모델 훈련을 진행할 수 있습니다.');
        }
        
        return recommendations;
    }

    // 유틸리티 함수들
    async ensureDir(dir) {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    }
}

// 메인 실행
async function main() {
    const manager = new AdvancedDataManager();
    await manager.initialize();
    
    console.log('\n🎯 사용 가능한 기능:');
    console.log('1. 라벨링 세션 추가');
    console.log('2. AI 훈련용 데이터 내보내기');
    console.log('3. 라벨링 보고서 생성');
    console.log('4. 데이터 통계 확인');
    
    return manager;
}

if (require.main === module) {
    main().catch(console.error);
}

module.exports = AdvancedDataManager;
