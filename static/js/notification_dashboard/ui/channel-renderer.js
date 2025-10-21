/**
 * Channel Renderer for Notification Dashboard
 * Renders channel list and handles channel-related UI updates
 */

import { getChannelIcon, getChannelDisplayName, formatDateTime } from '../utils/formatters.js';
import { showToast } from '../utils/toast-manager.js';

class ChannelRenderer {
    constructor(dataLoader) {
        this.dataLoader = dataLoader;
    }

    /**
     * Render the channels tab content
     */
    async renderChannels() {
        try {
            const channels = await this.dataLoader.loadChannels();
            this.displayChannels(channels);
        } catch (error) {
            console.error('Error rendering channels:', error);
            showToast('채널 데이터 로드 중 오류가 발생했습니다.', 'error');
        }
    }

    /**
     * Display channels in the UI
     */
    displayChannels(channels) {
        const container = document.getElementById('channelList');
        if (!container) return;

        // Clear existing content
        container.innerHTML = '';

        if (channels && channels.channels) {
            Object.entries(channels.channels).forEach(([name, channel]) => {
                const channelCard = document.createElement('div');
                channelCard.className = 'col-md-6 mb-3';
                channelCard.innerHTML = `
                    <div class="card">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h6 class="card-title mb-0">
                                    <i class="fas fa-${getChannelIcon(name)} me-2"></i>
                                    ${getChannelDisplayName(name)}
                                </h6>
                                <span class="badge badge-${channel.status === 'active' ? 'success' : 'danger'}">
                                    ${channel.status}
                                </span>
                            </div>
                            <p class="card-text text-muted">
                                마지막 사용: ${formatDateTime(channel.last_used || new Date().toISOString())}
                            </p>
                            <div class="d-flex gap-2">
                                <button class="btn btn-sm btn-primary" onclick="dashboard && dashboard.testChannel ? dashboard.testChannel('${name}') : testChannel('${name}')">
                                    <i class="fas fa-play me-1"></i>
                                    테스트
                                </button>
                                <button class="btn btn-sm btn-outline-secondary" onclick="dashboard && dashboard.configureChannel ? dashboard.configureChannel('${name}') : configureChannel('${name}')">
                                    <i class="fas fa-cog me-1"></i>
                                    설정
                                </button>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(channelCard);
            });
        }
    }
}

// Export the class for use in other modules
export default ChannelRenderer;