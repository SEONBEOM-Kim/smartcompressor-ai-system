// 관리자 대시보드 공통 JavaScript

// 로그아웃 함수
function logout() {
    if (confirm('로그아웃하시겠습니까?')) {
        localStorage.removeItem('currentUser');
        window.location.href = '/';
    }
}

// 공통 알림 함수
function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' :
                      type === 'error' ? 'alert-danger' :
                      type === 'warning' ? 'alert-warning' : 'alert-info';

    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // 3초 후 자동 제거
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 3000);
}

// API 호출 공통 함수
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showNotification('API 호출 중 오류가 발생했습니다.', 'error');
        throw error;
    }
}

// 페이지 로드 시 초기화 (인증 체크 비활성화)
document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin dashboard loaded successfully');
    // 인증 체크 비활성화 - 임시로 주석 처리
    /*
    const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
    if (!currentUser.email) {
        window.location.href = '/';
        return;
    }

    if (currentUser.email !== 'admin@signalcraft.kr' && currentUser.name !== '관리자') {
        showNotification('관리자 권한이 필요합니다.', 'error');
        window.location.href = '/';
        return;
    }
    */
});
