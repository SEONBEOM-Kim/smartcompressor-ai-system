/**
 * Notification Sender for Notification Dashboard
 * Handles quick notification form processing
 */

import { showToast } from '../utils/toast-manager.js';

class NotificationSender {
    constructor(dataLoader) {
        this.dataLoader = dataLoader;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add event listener to the quick notification form
        const form = document.getElementById('quickNotificationForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendQuickNotification();
            });
        }
    }

    /**
     * Process quick notification form submission
     */
    async sendQuickNotification() {
        try {
            const type = document.getElementById('notificationType').value;
            const content = document.getElementById('messageContent').value;
            const channels = Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value);

            if (!content.trim()) {
                showToast('메시지를 입력해주세요.', 'warning');
                return;
            }

            const notificationData = {
                type: type,
                content: content,
                channels: channels,
                priority: 'normal'
            };

            const response = await this.dataLoader.sendNotification(notificationData);

            if (response.success) {
                showToast('알림이 전송되었습니다.', 'success');
                // Reset form after successful submission
                document.getElementById('quickNotificationForm').reset();
                // Re-check the default channel
                const webSocketChannel = document.getElementById('channelWebSocket');
                if (webSocketChannel) {
                    webSocketChannel.checked = true;
                }
            } else {
                showToast('알림 전송에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('Error sending notification:', error);
            showToast('알림 전송 중 오류가 발생했습니다.', 'error');
        }
    }
}

// Export the class for use in other modules
export default NotificationSender;