// static/js/dashboard/utils/helpers.js

// 알림 표시
function showAlert(message, type) {
    // 기존 알림이 있다면 제거
    const existingAlerts = document.querySelectorAll('.alert.position-fixed');
    existingAlerts.forEach(alert => alert.remove());

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// 자동 새로고침 시작 - utils 함수
function startAutoRefreshHelper(callback, interval = 30000) {
    return setInterval(callback, interval);
}

// 자동 새로고침 중지 - utils 함수
function stopAutoRefreshHelper(intervalId) {
    if (intervalId) {
        clearInterval(intervalId);
    }
}

// 모달 열기
function openModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement && window.bootstrap && window.bootstrap.Modal) {
        const modal = new window.bootstrap.Modal(modalElement);
        modal.show();
        return modal;
    }
}

// 모달 닫기
function closeModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement && window.bootstrap && window.bootstrap.Modal) {
        const modal = window.bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
}