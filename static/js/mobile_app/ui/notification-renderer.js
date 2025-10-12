class NotificationRenderer {
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) {
            return '방금 전';
        } else if (diff < 3600000) {
            return `${Math.floor(diff / 60000)}분 전`;
        } else if (diff < 86400000) {
            return `${Math.floor(diff / 600000)}시간 전`;
        } else {
            return date.toLocaleDateString('ko-KR');
        }
    }

    updateNotificationBadge(notifications) {
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            const unreadCount = (notifications || []).filter(n => !n.read).length;
            badge.textContent = unreadCount;
            badge.style.display = unreadCount > 0 ? 'block' : 'none';
        }
    }

    updateNotificationHistory(notifications) {
        const historyList = document.getElementById('notificationHistory');
        if (!historyList) return;

        historyList.innerHTML = '';

        (notifications || []).slice(0, 10).forEach(notification => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.innerHTML = `
                <div class="notification-content">
                    <h5>${notification.title}</h5>
                    <p>${notification.message}</p>
                    <small>${this.formatTime(notification.timestamp)}</small>
                </div>
                <div class="notification-status">
                    <i class="fas fa-${notification.read ? 'check' : 'circle'}"></i>
                </div>
            `;
            historyList.appendChild(historyItem);
        });
    }
}

export default NotificationRenderer;