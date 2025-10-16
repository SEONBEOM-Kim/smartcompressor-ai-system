// diagnosis-controller.js - 메인 컨트롤러 (가벼움)
class DiagnosisController {
    constructor() {
        this.audioRecorder = new AudioRecorder();
        this.aiAnalyzer = new AIAnalyzer();
        this.ui = new DiagnosisUI();
        this.diagnosisResult = null;
        
        this.setupEventListeners();
        this.setupCallbacks();
    }

    setupEventListeners() {
        this.ui.recordBtn.addEventListener('click', () => this.toggleRecording());
        this.ui.analyzeBtn.addEventListener('click', () => this.analyzeAudio());
        this.ui.reportBtn.addEventListener('click', () => this.showDetailedReport());
    }

    setupCallbacks() {
        // 녹음 완료 콜백
        this.audioRecorder.onRecordingComplete = (audioBlob) => {
            this.ui.updateAnalyzeButton(true);
            this.ui.showStatus('✅ 녹음 완료! 진단하기 버튼을 클릭하세요.', 'success');
        };

        // 상태 변경 콜백
        this.audioRecorder.onStatusChange = (status, message) => {
            if (status === 'recording') {
                this.ui.updateRecordButton(true);
                this.ui.hideResult();
            } else if (status === 'stopped') {
                this.ui.updateRecordButton(false);
            } else if (status === 'error') {
                this.ui.updateRecordButton(false);
            }
            this.ui.showStatus(message, status === 'error' ? 'danger' : 'info');
        };

        // 분석 완료 콜백
        this.aiAnalyzer.onAnalysisComplete = (data) => {
            this.diagnosisResult = data;
            this.ui.showResult(data);
            this.ui.showReportButton();
        };

        // 분석 상태 변경 콜백
        this.aiAnalyzer.onStatusChange = (status, message) => {
            this.ui.showStatus(message, status === 'error' ? 'danger' : 'info');
        };
    }

    async toggleRecording() {
        if (!this.audioRecorder.isRecording) {
            await this.audioRecorder.startRecording();
        } else {
            this.audioRecorder.stopRecording();
        }
    }

    async analyzeAudio() {
        const audioBlob = this.audioRecorder.getAudioBlob();
        await this.aiAnalyzer.analyzeAudio(audioBlob);
    }

    showDetailedReport() {
        if (this.diagnosisResult) {
            sessionStorage.setItem('diagnosisResult', JSON.stringify(this.diagnosisResult));
            window.location.href = '/diagnosis-report';
        }
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    new DiagnosisController();
});
