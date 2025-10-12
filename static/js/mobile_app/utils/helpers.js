function handleOnlineStatus(isOnline, callback) {
    const statusIndicator = document.getElementById('connectionStatus');
    if (statusIndicator) {
        const icon = statusIndicator.querySelector('i');
        if (isOnline) {
            icon.className = 'fas fa-wifi';
            icon.style.color = 'var(--status-normal)';
        } else {
            icon.className = 'fas fa-wifi-slash';
            icon.style.color = 'var(--status-error)';
            showOfflineModal();
        }
    }
    
    if (callback && typeof callback === 'function') {
        callback(isOnline);
    }
}

function showOfflineModal() {
    const modal = new bootstrap.Modal(document.getElementById('offlineModal'));
    modal.show();
}

function animateDiagnosisProgress() {
    const progressFill = document.querySelector('.progress-fill');
    const progressText = document.querySelector('.progress-text');
    const description = document.querySelector('.progress-description');
    
    if (!progressFill || !progressText || !description) return;
    
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 100) progress = 100;
        
        progressFill.style.background = `conic-gradient(var(--sbux-light-green) ${progress * 3.6}deg, var(--tesla-gray-800) 0deg)`;
        progressText.textContent = `${Math.round(progress)}%`;
        
        if (progress >= 100) {
            clearInterval(interval);
            description.textContent = '진단 완료!';
        }
    }, 200);
}

function showDiagnosisResult(result) {
    const progressDiv = document.getElementById('diagnosisProgress');
    const resultDiv = document.getElementById('diagnosisResult');
    
    if (progressDiv && resultDiv) {
        progressDiv.style.display = 'none';
        resultDiv.style.display = 'block';
        
        const status = result.status || '정상';
        const confidence = result.confidence || 0.95;
        
        document.getElementById('diagnosisStatus').textContent = status;
        document.getElementById('diagnosisConfidence').textContent = `${Math.round(confidence * 100)}%`;
        
        const resultIcon = resultDiv.querySelector('.result-icon i');
        if (status === '정상') {
            resultIcon.className = 'fas fa-check-circle';
            resultIcon.style.color = 'var(--status-normal)';
        } else if (status === '경고') {
            resultIcon.className = 'fas fa-exclamation-triangle';
            resultIcon.style.color = 'var(--status-warning)';
        } else {
            resultIcon.className = 'fas fa-times-circle';
            resultIcon.style.color = 'var(--status-error)';
        }
    }
}

function showDiagnosisError(showToastCallback) {
    if (showToastCallback) {
        showToastCallback('진단 중 오류가 발생했습니다', 'error');
    }
    // In a full implementation, this would navigate to dashboard
}

export { 
    handleOnlineStatus, 
    showOfflineModal, 
    animateDiagnosisProgress, 
    showDiagnosisResult, 
    showDiagnosisError 
};