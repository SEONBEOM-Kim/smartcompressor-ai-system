// static/js/dashboard/utils/formatters.js

// 날짜 포맷팅
function formatDate(dateString) {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 상태 텍스트 변환
function getStatusText(status) {
    const statusMap = {
        'active': '활성',
        'online': '온라인',
        'inactive': '비활성',
        'offline': '오프라인',
        'maintenance': '점검중',
        'warning': '경고',
        'critical': '위험',
        'sent': '전송됨',
        'delivered': '전달됨',
        'failed': '실패',
        'pending': '대기중'
    };
    return statusMap[status] || status;
}

// 상태 클래스 변환
function getStatusClass(status) {
    const statusMap = {
        'active': 'success',
        'online': 'success',
        'inactive': 'secondary',
        'offline': 'danger',
        'maintenance': 'info',
        'warning': 'warning',
        'critical': 'danger',
        'sent': 'success',
        'delivered': 'success',
        'failed': 'danger',
        'pending': 'warning'
    };
    return statusMap[status] || 'secondary';
}

// 우선순위 클래스 변환
function getPriorityClass(priority) {
    const priorityMap = {
        'low': 'secondary',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'danger'
    };
    return priorityMap[priority] || 'secondary';
}

// 헬스 스코어 클래스 변환
function getHealthClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'warning';
    return 'critical';
}