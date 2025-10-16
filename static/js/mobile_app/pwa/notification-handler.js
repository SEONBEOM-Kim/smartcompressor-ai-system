class NotificationHandler {
    async testPushNotification(type) {
        try {
            const response = await fetch('/api/notifications/test-push', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    user_id: 'test_user'
                })
            });

            if (response.ok) {
                this.showToast('푸시 알림 테스트 완료', 'success');
            } else {
                throw new Error('푸시 알림 테스트 실패');
            }
        } catch (error) {
            console.error('푸시 알림 테스트 오류:', error);
            this.showToast('푸시 알림 테스트 실파', 'error');
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--tesla-gray-800);
            color: var(--tesla-white);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border: 1px solid var(--tesla-gray-700);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 3000);
    }
}

export default NotificationHandler;