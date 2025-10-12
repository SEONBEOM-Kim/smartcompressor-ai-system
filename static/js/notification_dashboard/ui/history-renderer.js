/**
 * History Renderer for Notification Dashboard
 * Renders notification history in the UI
 */

import { getTypeColor, getTypeDisplayName, getPriorityColor, formatDateTime } from '../utils/formatters.js';
import { showToast } from '../utils/toast-manager.js';

class HistoryRenderer {
    constructor(dataLoader) {
        this.dataLoader = dataLoader;
    }

    /**
     * Render the history tab content
     */
    async renderHistory(filters = {}) {
        try {
            const history = await this.dataLoader.loadHistory(filters);
            this.displayHistory(history);
        } catch (error) {
            console.error('Error rendering history:', error);
            showToast('히스토리 데이터 로드 중 오류가 발생했습니다.', 'error');
        }
    }

    /**
     * Display history in the UI
     */
    displayHistory(history) {
        const tbody = document.getElementById('historyList');
        if (!tbody) return;

        // Clear existing content
        tbody.innerHTML = '';

        if (history) {
            history.forEach(notification => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${formatDateTime(notification.sent_at)}</td>
                    <td><span class="badge badge-${getTypeColor(notification.type)}">${getTypeDisplayName(notification.type)}</span></td>
                    <td>${notification.content || ''}</td>
                    <td>${notification.channels ? notification.channels.join(', ') : ''}</td>
                    <td><span class="badge badge-${getPriorityColor(notification.priority)}">${notification.priority || ''}</span></td>
                    <td><span class="badge badge-${notification.status === 'sent' ? 'success' : 'danger'}">${notification.status || ''}</span></td>
                `;
                tbody.appendChild(row);
            });
        }
    }
}

// Export the class for use in other modules
export default HistoryRenderer;