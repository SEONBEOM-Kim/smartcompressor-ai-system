// audio-recorder.js - 오디오 녹음 전용 모듈
class AudioRecorder {
    constructor() {
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.audioBlob = null;
        this.onRecordingComplete = null;
        this.onStatusChange = null;
    }

    async startRecording() {
        try {
            // 더 안전한 constraints 설정
            let constraints = {
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true
                }
            };

            // 브라우저별 호환성 처리
            if (navigator.userAgent.includes('Chrome')) {
                constraints.audio.sampleRate = 16000;
            }

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // MediaRecorder 옵션 설정
            let options = {};
            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                options.mimeType = 'audio/webm;codecs=opus';
            } else if (MediaRecorder.isTypeSupported('audio/webm')) {
                options.mimeType = 'audio/webm';
            } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                options.mimeType = 'audio/mp4';
            }

            this.mediaRecorder = new MediaRecorder(stream, options);
            this.audioChunks = [];

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                const mimeType = this.mediaRecorder.mimeType || 'audio/webm';
                this.audioBlob = new Blob(this.audioChunks, { type: mimeType });
                if (this.onRecordingComplete) {
                    this.onRecordingComplete(this.audioBlob);
                }
            };

            this.mediaRecorder.start();
            this.isRecording = true;
            
            if (this.onStatusChange) {
                this.onStatusChange('recording', '🎤 녹음 중... (5-10초간 녹음하세요)');
            }

        } catch (error) {
            console.error('녹음 오류:', error);
            if (this.onStatusChange) {
                this.onStatusChange('error', this.getErrorMessage(error));
            }
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            if (this.onStatusChange) {
                this.onStatusChange('stopped', '✅ 녹음 완료!');
            }
        }
    }

    getErrorMessage(error) {
        if (error.name === 'NotAllowedError') {
            return '❌ 마이크 접근 권한이 거부되었습니다. 브라우저 설정에서 마이크 권한을 허용해주세요.';
        } else if (error.name === 'NotFoundError') {
            return '❌ 마이크를 찾을 수 없습니다. 마이크가 연결되어 있는지 확인해주세요.';
        } else if (error.name === 'NotSupportedError') {
            return '❌ 이 브라우저는 녹음 기능을 지원하지 않습니다.';
        } else {
            return '❌ 녹음 중 오류가 발생했습니다: ' + error.message;
        }
    }

    getAudioBlob() {
        return this.audioBlob;
    }

    clear() {
        this.audioBlob = null;
        this.audioChunks = [];
    }
}
