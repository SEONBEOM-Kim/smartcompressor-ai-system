class AIService {
    async lightweightAnalyze(audioData) {
        return {
            success: true,
            is_overload: false,
            confidence: 0.5,
            message: 'AI 분석 기능을 구현 중입니다.'
        };
    }
}

module.exports = new AIService();