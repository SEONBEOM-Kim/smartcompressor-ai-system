// static/js/landing/ai-diagnosis.js
class IntegratedAIDiagnosis {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioBlob = null;
        this.diagnosisResult = null;
        this.init();
    }

    init() {
        this.recordBtn = document.getElementById('recordBtn');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.reportBtn = document.getElementById('reportBtn');
        this.status = document.getElementById('diagnosisStatus');
        this.result = document.getElementById('diagnosisResult');

        if (this.recordBtn) {
            this.recordBtn.addEventListener('click', () => this.toggleRecording());
        }
        if (this.analyzeBtn) {
            this.analyzeBtn.addEventListener('click', () => this.analyzeAudio());
        }
        if (this.reportBtn) {
            this.reportBtn.addEventListener('click', () => this.showDetailedReport());
        }

        this.checkBrowserSupport();
    }

    checkBrowserSupport() {
        const hasGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
        const hasMediaRecorder = typeof MediaRecorder !== 'undefined';
        
        if (!hasGetUserMedia || !hasMediaRecorder) {
            this.showStatus('❌ 이 브라우저는 녹음 기능을 지원하지 않습니다. 최신 Chrome, Firefox, Safari를 사용해주세요.', 'danger');
            if (this.recordBtn) this.recordBtn.disabled = true;
            return false;
        }

        if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
            this.showStatus('⚠️ 녹음 기능을 사용하려면 HTTPS 연결이 필요합니다. 현재는 제한된 기능만 사용 가능합니다.', 'warning');
        }

        return true;
    }

    async toggleRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }

    async startRecording() {
        try {
            const constraints = {
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 16000
                }
            };

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.mediaRecorder = new MediaRecorder(stream, {
                mimeType: 'audio/webm;codecs=opus'
            });

            this.audioChunks = [];
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                this.analyzeBtn.disabled = false;
                this.showStatus('✅ 녹음 완료! 진단하기 버튼을 클릭하세요.', 'success');
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            this.recordBtn.textContent = '⏹️ 녹음 중지';
            this.recordBtn.className = 'btn btn-danger btn-lg me-3';
            this.analyzeBtn.disabled = true;
            this.hideResult();

            this.showStatus('🎤 녹음 중... (5-10초간 녹음하세요)', 'info');

        } catch (error) {
            console.error('녹음 오류:', error);
            this.showStatus('❌ 녹음 중 오류가 발생했습니다: ' + error.message, 'danger');
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            this.recordBtn.textContent = '🎤 녹음 시작';
            this.recordBtn.className = 'btn btn-primary btn-lg me-3';
        }
    }

    async analyzeAudio() {
        if (!this.audioBlob) {
            this.showStatus('❌ 먼저 녹음을 완료해주세요.', 'danger');
            return;
        }

        this.showStatus('🔍 AI가 오디오를 분석 중입니다...', 'info');
        this.analyzeBtn.disabled = true;

        try {
            const formData = new FormData();
            formData.append('audio', this.audioBlob);
            formData.append('timestamp', new Date().toISOString());

            const response = await fetch('/api/lightweight-analyze', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            this.diagnosisResult = data;
            this.showResult(data);
            this.reportBtn.style.display = 'inline-block';

        } catch (error) {
            console.error('분석 오류:', error);
            this.showStatus('❌ 분석 중 오류가 발생했습니다.', 'danger');
        } finally {
            this.analyzeBtn.disabled = false;
        }
    }

    showResult(data) {
        const resultClass = data.is_overload ? 'overload' : 'normal';
        this.result.innerHTML = `
            <div class="result-card ${resultClass}">
                <h3>${data.is_overload ? '⚠️ 과부하음 감지' : '✅ 정상 작동'}</h3>
                <p>신뢰도: ${Math.round(data.confidence * 100)}%</p>
                <p>처리 시간: ${data.processing_time_ms.toFixed(1)}ms</p>
                <p>${data.message}</p>
            </div>
        `;
        this.result.style.display = 'block';
    }

    showDetailedReport() {
        if (this.diagnosisResult) {
            sessionStorage.setItem('diagnosisResult', JSON.stringify(this.diagnosisResult));
            window.location.href = '/diagnosis-report';
        }
    }

    showStatus(message, type) {
        if (this.status) {
            this.status.textContent = message;
            this.status.className = `alert alert-${type} text-center`;
            this.status.style.display = 'block';
        }
    }

    hideResult() {
        if (this.result) {
            this.result.style.display = 'none';
        }
        if (this.reportBtn) {
            this.reportBtn.style.display = 'none';
        }
    }
}

// 페이지 로드 시 자동 초기화
document.addEventListener('DOMContentLoaded', () => {
    new IntegratedAIDiagnosis();
});