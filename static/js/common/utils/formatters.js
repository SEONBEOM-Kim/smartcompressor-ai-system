/**
 * Common formatters for all modules
 * Consolidates duplicated formatting functions from various modules
 */

/**
 * Format date string to Korean format
 * @param {string|null|undefined} dateString - Date string to format
 * @returns {string} Formatted date string in Korean format
 */
export function formatDate(dateString) {
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

/**
 * Format date string to readable format with fallback
 * @param {string|null|undefined} dateString - Date string to format
 * @returns {string} Formatted date string
 */
export function formatDateTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    
    // Check if the date is valid
    if (isNaN(date.getTime())) {
        return '';
    }
    
    return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format relative time (e.g., "5분 전", "2시간 전")
 * @param {string|number} timestamp - Timestamp to format
 * @returns {string} Formatted relative time string
 */
export function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) {
        return '방금 전';
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}분 전`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}시간 전`;
    } else {
        return date.toLocaleDateString('ko-KR');
    }
}

/**
 * Get status display text for various status values
 * @param {string} status - Status value
 * @returns {string} Display text for the status
 */
export function getStatusText(status) {
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
        'pending': '대기중',
        'general': '일반',
        'emergency': '긴급',
        'equipment': '장비',
        'order': '주문',
        'payment': '결제'
    };
    return statusMap[status] || status;
}

/**
 * Get CSS class for various status values
 * @param {string} status - Status value
 * @returns {string} CSS class for the status
 */
export function getStatusClass(status) {
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

/**
 * Get priority CSS class for notification priority
 * @param {string} priority - Priority level
 * @returns {string} CSS class for the priority
 */
export function getPriorityClass(priority) {
    const priorityMap = {
        'low': 'secondary',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'danger',
        'normal': 'info',
        'urgent': 'danger'
    };
    return priorityMap[priority] || 'secondary';
}

/**
 * Get health CSS class based on score
 * @param {number} score - Health score
 * @returns {string} CSS class for the health score
 */
export function getHealthClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'warning';
    return 'critical';
}

/**
 * Get the appropriate color for a notification type
 * @param {string} type - Notification type
 * @returns {string} Bootstrap color class
 */
export function getTypeColor(type) {
    const colors = {
        'general': 'info',
        'emergency': 'danger',
        'equipment': 'warning',
        'order': 'success',
        'payment': 'primary'
    };
    return colors[type] || 'secondary';
}

/**
 * Get the display name for a notification type
 * @param {string} type - Notification type
 * @returns {string} Display name
 */
export function getTypeDisplayName(type) {
    const names = {
        'general': '일반',
        'emergency': '긴급',
        'equipment': '장비',
        'order': '주문',
        'payment': '결제'
    };
    return names[type] || type;
}

/**
 * Get the appropriate color for a priority level
 * @param {string} priority - Priority level
 * @returns {string} Bootstrap color class
 */
export function getPriorityColor(priority) {
    const colors = {
        'low': 'secondary',
        'normal': 'info',
        'high': 'warning',
        'urgent': 'danger'
    };
    return colors[priority] || 'secondary';
}

/**
 * Get the appropriate icon for a channel
 * @param {string} channelName - Name of the channel
 * @returns {string} Icon class name
 */
export function getChannelIcon(channelName) {
    const icons = {
        'websocket': 'wifi',
        'email': 'envelope',
        'kakao': 'comment',
        'slack': 'slack',
        'discord': 'discord',
        'whatsapp': 'whatsapp'
    };
    return icons[channelName] || 'bell';
}

/**
 * Get the display name for a channel
 * @param {string} channelName - Name of the channel
 * @returns {string} Display name
 */
export function getChannelDisplayName(channelName) {
    const names = {
        'websocket': 'WebSocket',
        'email': '이메일',
        'kakao': '카카오톡',
        'slack': 'Slack',
        'discord': 'Discord',
        'whatsapp': 'WhatsApp'
    };
    return names[channelName] || channelName;
}