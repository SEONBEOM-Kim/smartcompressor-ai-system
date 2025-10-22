const express = require('express');
const router = express.Router();
const path = require('path');
const fs = require('fs').promises;

// 지능형 라벨링 시스템 import
const IntelligentLabelingSystem = require('../../ai/intelligent_labeling_system');

// 지능형 라벨링 시스템 인스턴스
let labelingSystem = null;

// 시스템 초기화
async function initializeLabelingSystem() {
    try {
        if (!labelingSystem) {
            labelingSystem = new IntelligentLabelingSystem();
            console.log('✅ 지능형 라벨링 시스템 초기화 완료');
        }
    } catch (error) {
        console.error('❌ 지능형 라벨링 시스템 초기화 실패:', error);
    }
}

// 초기화 실행
initializeLabelingSystem();

// AI 제안 요청 API
router.post('/ai-suggestion', async (req, res) => {
    try {
        const { fileName } = req.body;
        
        if (!fileName) {
            return res.status(400).json({
                success: false,
                message: '파일명이 필요합니다.'
            });
        }

        // 시스템 초기화 확인
        if (!labelingSystem) {
            await initializeLabelingSystem();
        }

        // 오디오 파일 경로
        const audioPath = path.join(__dirname, '../../data/real_audio_uploads', fileName);
        
        // 파일 존재 확인
        try {
            await fs.access(audioPath);
        } catch (error) {
            return res.status(404).json({
                success: false,
                message: '오디오 파일을 찾을 수 없습니다.'
            });
        }

        // AI 분석 수행
        const suggestion = labelingSystem.analyze_audio(audioPath);
        
        res.json({
            success: true,
            suggestion: suggestion
        });

    } catch (error) {
        console.error('AI 제안 요청 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 제안 생성 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// AI 성능 조회 API
router.get('/ai-performance', async (req, res) => {
    try {
        // 시스템 초기화 확인
        if (!labelingSystem) {
            await initializeLabelingSystem();
        }

        const performance = labelingSystem.get_labeling_statistics();
        
        res.json({
            success: true,
            performance: performance
        });

    } catch (error) {
        console.error('AI 성능 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 성능 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 라벨링 결정 저장 API (AI 제안 포함)
router.post('/save-with-ai', async (req, res) => {
    try {
        const { 
            fileName, 
            label, 
            confidence, 
            notes, 
            labelerId, 
            aiSuggestion 
        } = req.body;
        
        if (!fileName || !label) {
            return res.status(400).json({
                success: false,
                message: '필수 필드가 누락되었습니다.'
            });
        }

        // 시스템 초기화 확인
        if (!labelingSystem) {
            await initializeLabelingSystem();
        }

        // 오디오 파일 경로
        const audioPath = path.join(__dirname, '../../data/real_audio_uploads', fileName);
        
        // AI 제안이 있는 경우 라벨링 결정 저장
        if (aiSuggestion) {
            const saved = labelingSystem.save_labeling_decision(
                audioPath,
                aiSuggestion,
                label,
                confidence / 100, // 백분율을 소수로 변환
                notes || ''
            );
            
            if (!saved) {
                return res.status(500).json({
                    success: false,
                    message: '라벨링 결정 저장에 실패했습니다.'
                });
            }
        }

        // 기존 라벨링 데이터 저장 로직
        const labelData = {
            id: Date.now(),
            fileName,
            label,
            confidence,
            notes,
            labelerId,
            aiSuggestion: aiSuggestion || null,
            timestamp: new Date().toISOString()
        };

        // 메모리 저장 (실제로는 데이터베이스에 저장)
        // 여기서는 간단히 JSON 파일로 저장
        const dataPath = path.join(__dirname, '../../data/labeling_data.json');
        let existingData = [];
        
        try {
            const data = await fs.readFile(dataPath, 'utf8');
            existingData = JSON.parse(data);
        } catch (error) {
            // 파일이 없으면 빈 배열로 시작
        }
        
        existingData.push(labelData);
        await fs.writeFile(dataPath, JSON.stringify(existingData, null, 2));
        
        res.json({
            success: true,
            data: labelData
        });

    } catch (error) {
        console.error('라벨링 저장 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨링 저장 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 라벨링 히스토리 조회 API
router.get('/history', async (req, res) => {
    try {
        // 시스템 초기화 확인
        if (!labelingSystem) {
            await initializeLabelingSystem();
        }

        const history = labelingSystem.labeling_history || [];
        
        res.json({
            success: true,
            history: history
        });

    } catch (error) {
        console.error('라벨링 히스토리 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '라벨링 히스토리 조회 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// AI 모델 재훈련 요청 API
router.post('/retrain-model', async (req, res) => {
    try {
        // 시스템 초기화 확인
        if (!labelingSystem) {
            await initializeLabelingSystem();
        }

        // 실제로는 모델 재훈련 로직을 실행
        // 여기서는 시뮬레이션
        console.log('🔄 AI 모델 재훈련 요청');
        
        // 재훈련 시뮬레이션 (실제로는 시간이 오래 걸림)
        setTimeout(() => {
            console.log('✅ AI 모델 재훈련 완료');
        }, 5000);
        
        res.json({
            success: true,
            message: 'AI 모델 재훈련이 시작되었습니다.',
            estimatedTime: '5-10분'
        });

    } catch (error) {
        console.error('모델 재훈련 오류:', error);
        res.status(500).json({
            success: false,
            message: '모델 재훈련 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 라벨링 품질 분석 API
router.get('/quality-analysis', async (req, res) => {
    try {
        // 시스템 초기화 확인
        if (!labelingSystem) {
            await initializeLabelingSystem();
        }

        const stats = labelingSystem.get_labeling_statistics();
        
        // 품질 분석
        const qualityAnalysis = {
            overall_quality: stats.agreement_rate > 0.8 ? 'excellent' : 
                           stats.agreement_rate > 0.6 ? 'good' : 
                           stats.agreement_rate > 0.4 ? 'fair' : 'poor',
            ai_accuracy: stats.agreement_rate,
            average_confidence: stats.average_confidence,
            total_decisions: stats.total_decisions,
            confidence_consistency: 1 - stats.average_confidence_difference,
            recommendations: generateRecommendations(stats)
        };
        
        res.json({
            success: true,
            analysis: qualityAnalysis
        });

    } catch (error) {
        console.error('품질 분석 오류:', error);
        res.status(500).json({
            success: false,
            message: '품질 분석 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

// 추천사항 생성 함수
function generateRecommendations(stats) {
    const recommendations = [];
    
    if (stats.agreement_rate < 0.6) {
        recommendations.push('AI 모델의 정확도가 낮습니다. 더 많은 훈련 데이터가 필요합니다.');
    }
    
    if (stats.average_confidence < 0.7) {
        recommendations.push('라벨링 신뢰도가 낮습니다. 전문가 검토를 늘려주세요.');
    }
    
    if (stats.average_confidence_difference > 0.3) {
        recommendations.push('AI와 전문가 간 신뢰도 차이가 큽니다. 라벨링 기준을 재검토해주세요.');
    }
    
    if (stats.total_decisions < 100) {
        recommendations.push('더 많은 라벨링 데이터를 수집하여 AI 성능을 향상시켜주세요.');
    }
    
    if (recommendations.length === 0) {
        recommendations.push('라벨링 품질이 우수합니다. 현재 상태를 유지해주세요.');
    }
    
    return recommendations;
}

module.exports = router;
