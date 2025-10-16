// ai-analyzer.js - AI 분석 전용 모듈
class AIAnalyzer {
    constructor() {
        this.isAnalyzing = false;
        this.onAnalysisComplete = null;
        this.onStatusChange = null;
    }

    async analyzeAudio(audioBlob) {
        if (!audioBlob) {
            if (this.onStatusChange) {
                this.onStatusChange('error', '❌ 먼저 녹음을 해주세요.');
            }
            return;
        }

        this.isAnalyzing = true;
        
        if (this.onStatusChange) {
            this.onStatusChange('analyzing', '🔍 분석 중...');
        }

        try {
            const formData = new FormData();
            formData.append('audio', audioBlob, 'recording.webm');
            formData.append('timestamp', new Date().toISOString());

            const response = await fetch('/api/lightweight-analyze', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.status === 'success') {
                if (this.onAnalysisComplete) {
                    this.onAnalysisComplete(data);
                }
            } else {
                if (this.onStatusChange) {
                    this.onStatusChange('error', '❌ 분석 중 오류가 발생했습니다: ' + (data.error || 'Unknown error'));
                }
            }

        } catch (error) {
            console.error('분석 오류:', error);
            if (this.onStatusChange) {
                this.onStatusChange('error', '❌ 서버 연결 오류가 발생했습니다: ' + error.message);
            }
        } finally {
            this.isAnalyzing = false;
        }
    }

    isCurrentlyAnalyzing() {
        return this.isAnalyzing;
    }
}
