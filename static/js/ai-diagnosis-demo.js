// 기존 복잡한 분석 로직을 단순화
class LightweightAIDemo {
    constructor() {
        this.isRecording = false;
        this.audioContext = null;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.analysisResults = null;
        this.overloadDetected = false; // 단순한 과부하 감지 플래그
    }

    // 기존 processAudioBlob 함수를 이렇게 수정:
    processAudioBlob(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('timestamp', new Date().toISOString());

        fetch('/api/lightweight-analyze', {  // 새로운 경량화 엔드포인트
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            this.analysisResults = data;
            this.overloadDetected = data.is_overload;
            this.displaySimpleResults(data);
        })
        .catch(error => {
            console.error('분석 중 오류:', error);
        });
    }

    // 단순화된 결과 표시
    displaySimpleResults(data) {
        const resultsContainer = document.getElementById('resultsContainer');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="result-card ${data.is_overload ? 'overload' : 'normal'}">
                    <h3>${data.is_overload ? '⚠️ 과부하음 감지' : '✅ 정상 작동'}</h3>
                    <p>신뢰도: ${Math.round(data.confidence * 100)}%</p>
                    <p>처리 시간: ${data.processing_time_ms.toFixed(1)}ms</p>
                    <p>${data.message}</p>
                </div>
            `;
        }
    }
}
