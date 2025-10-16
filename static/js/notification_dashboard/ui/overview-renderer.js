/**
 * Overview Renderer for Notification Dashboard
 * Updates statistics cards, channel status, and recent notifications
 */

import { getChannelIcon, getChannelDisplayName, getTypeColor, getTypeDisplayName, getPriorityColor, formatDateTime } from '../utils/formatters.js';
import { showToast } from '../utils/toast-manager.js';

class OverviewRenderer {
    constructor(dataLoader) {
        this.dataLoader = dataLoader;
    }

    /**
     * Render the overview tab content
     */
    async renderOverview() {
        try {
            // Load all required data
            const { status, channels, history } = await this.dataLoader.loadOverview();

            // Update statistics if data is available
            if (status) {
                this.updateOverviewStats(status);
            }

            // Update channel status if data is available
            if (channels) {
                this.updateChannelStatus(channels);
            }

            // Update recent notifications if data is available
            if (history) {
                this.updateRecentNotifications(history);
            }
        } catch (error) {
            console.error('Error rendering overview:', error);
            showToast('개요 데이터 로드 중 오류가 발생했습니다.', 'error');
        }
    }

    /**
     * Update overview statistics
     */
    updateOverviewStats(status) {
        const totalNotificationsEl = document.getElementById('totalNotifications');
        const successRateEl = document.getElementById('successRate');
        const activeChannelsEl = document.getElementById('activeChannels');
        const queueSizeEl = document.getElementById('queueSize');

        if (totalNotificationsEl) {
            totalNotificationsEl.textContent = status.queue_size || 0;
        }
        if (successRateEl) {
            // In a real implementation, this would be calculated from actual data
            successRateEl.textContent = '95%';
        }
        if (activeChannelsEl) {
            activeChannelsEl.textContent = status.channels ? status.channels.length : 0;
        }
        if (queueSizeEl) {
            queueSizeEl.textContent = status.queue_size || 0;
        }
    }

    /**
     * Update channel status display
     */
    updateChannelStatus(channels) {
        const container = document.getElementById('channelStatus');
        if (!container) return;

        // Clear existing content
        container.innerHTML = '';

        if (channels && channels.channels) {
            Object.entries(channels.channels).forEach(([name, channel]) => {
                const channelDiv = document.createElement('div');
                channelDiv.className = 'col-md-4';
                channelDiv.innerHTML = `
                    <div class="channel-status ${channel.status}">
                        <div class="channel-icon">
                            <i class="fas fa-${getChannelIcon(name)}"></i>
                        </div>
                        <div class="channel-name">${getChannelDisplayName(name)}</div>
                        <div class="channel-status-text">${channel.status}</div>
                        <button class="btn btn-sm btn-outline-light mt-2" onclick="dashboard && dashboard.testChannel ? dashboard.testChannel('${name}') : testChannel('${name}')">
                            테스트
                        </button>
                    </div>
                `;
                container.appendChild(channelDiv);
            });
        }
    }

    /**
     * Update recent notifications table
     */
    updateRecentNotifications(notifications) {
        const tbody = document.getElementById('recentNotifications');
        if (!tbody) return;

        // Clear existing content
        tbody.innerHTML = '';

        if (notifications) {
            notifications.forEach(notification => {
                const row = document.createElement('tr');
                row.className = `notification-${notification.type}`;
                row.innerHTML = `
                    <td>${formatDateTime(notification.sent_at)}</td>
                    <td><span class="badge badge-${getTypeColor(notification.type)}">${getTypeDisplayName(notification.type)}</span></td>
                    <td>${notification.content}</td>
                    <td>${notification.channels ? notification.channels.join(', ') : ''}</td>
                    <td><span class="badge badge-${getPriorityColor(notification.priority)}">${notification.priority}</span></td>
                `;
                tbody.appendChild(row);
            });
        }
    }
}

// Export the class for use in other modules
export default OverviewRenderer;