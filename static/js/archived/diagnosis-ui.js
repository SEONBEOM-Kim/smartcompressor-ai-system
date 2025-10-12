// diagnosis-ui.js - UI 관리 전용 모듈
class DiagnosisUI {
    constructor() {
        this.recordBtn = null;
        this.analyzeBtn = null;
        this.reportBtn = null;
        this.status = null;
        this.result = null;
        this.init();
    }

    init() {
        this.recordBtn = document.getElementById('recordBtn');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.reportBtn = document.getElementById('reportBtn');
        this.status = document.getElementById('diagnosisStatus');
        this.result = document.getElementById('diagnosisResult');

        this.checkBrowserSupport();
    }

    checkBrowserSupport() {
        // 더 안전한 브라우저 호환성 확인
        const hasGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
        const hasMediaRecorder = typeof MediaRecorder !== 'undefined';
        
        if (!hasGetUserMedia || !hasMediaRecorder) {
            this.showStatus('❌ 이 브라우저는 녹음 기능을 지원하지 않습니다. 최신 Chrome, Firefox, Safari를 사용해주세요.', 'danger');
            this.recordBtn.disabled = true;
            return false;
        }

        // HTTPS 확인 (HTTP에서는 제한적)
        if (location.protocol !== 'https:' && location.hostname !== 'localhost') {
            this.showStatus('⚠️ 녹음 기능을 사용하려면 HTTPS 연결이 필요합니다. 현재는 제한된 기능만 사용 가능합니다.', 'warning');
        }

        return true;
    }

    showStatus(message, type) {
        this.status.textContent = message;
        this.status.className = `alert alert-${type} text-center`;
        this.status.style.display = 'block';
    }

    showResult(data) {
        this.result.style.display = 'block';
        this.result.className = `result-card ${data.is_overload ? 'overload' : 'normal'}`;
        
        this.result.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h4 class="card-title">${data.is_overload ? '⚠️ 과부하음 감지' : '✅ 정상 작동'}</h4>
                    <p class="card-text">
                        <strong>신뢰도:</strong> ${Math.round(data.confidence * 100)}%<br>
                        <strong>처리 시간:</strong> ${data.processing_time_ms.toFixed(1)}ms<br>
                        <strong>메시지:</strong> ${data.message}
                    </p>
                </div>
            </div>
        `;

        this.showStatus(data.is_overload ? '⚠️ 과부하음이 감지되었습니다!' : '✅ 정상 작동 중입니다!', 
                       data.is_overload ? 'warning' : 'success');
    }

    hideResult() {
        this.result.style.display = 'none';
        this.reportBtn.style.display = 'none';
    }

    updateRecordButton(isRecording) {
        if (isRecording) {
            this.recordBtn.textContent = '⏹️ 녹음 중지';
            this.recordBtn.className = 'btn btn-danger btn-lg';
        } else {
            this.recordBtn.textContent = '🎤 녹음 시작';
            this.recordBtn.className = 'btn btn-primary btn-lg';
        }
    }

    updateAnalyzeButton(enabled) {
        this.analyzeBtn.disabled = !enabled;
    }

    showReportButton() {
        this.reportBtn.style.display = 'inline-block';
    }

    hideReportButton() {
        this.reportBtn.style.display = 'none';
    }
}
