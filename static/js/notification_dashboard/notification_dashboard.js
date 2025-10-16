/**
 * Simplified entry point for Notification Dashboard
 * Orchestrates all the modular components
 */

// Import all modules
import NotificationDataLoader from './data/data-loader.js';
import TabManager from './ui/tab-manager.js';
import OverviewRenderer from './ui/overview-renderer.js';
import ChannelRenderer from './ui/channel-renderer.js';
import TemplateRenderer from './ui/template-renderer.js';
import HistoryRenderer from './ui/history-renderer.js';
import NotificationSender from './forms/notification-sender.js';
import SettingsManager from './forms/settings-manager.js';
import TemplateCreator from './forms/template-creator.js';

class NotificationDashboard {
    constructor() {
        this.currentTab = 'overview';
        this.refreshInterval = null;
        this.dataLoader = new NotificationDataLoader();
        
        // Initialize all modules
        this.tabManager = new TabManager(this.handleTabSwitch.bind(this));
        this.overviewRenderer = new OverviewRenderer(this.dataLoader);
        this.channelRenderer = new ChannelRenderer(this.dataLoader);
        this.templateRenderer = new TemplateRenderer(this.dataLoader);
        this.historyRenderer = new HistoryRenderer(this.dataLoader);
        this.notificationSender = new NotificationSender(this.dataLoader);
        this.settingsManager = new SettingsManager();
        this.templateCreator = new TemplateCreator(this.dataLoader);
        
        // Initialize the dashboard
        this.init();
    }

    init() {
        // Load initial data for overview
        this.loadOverview();
        // Start auto-refresh for overview data
        this.startAutoRefresh();
    }

    /**
     * Handle tab switching by loading appropriate data
     */
    async handleTabSwitch(tabName) {
        try {
            switch (tabName) {
                case 'overview':
                    await this.loadOverview();
                    break;
                case 'channels':
                    await this.loadChannels();
                    break;
                case 'templates':
                    await this.loadTemplates();
                    break;
                case 'history':
                    await this.loadHistory();
                    break;
                case 'settings':
                    await this.loadSettings();
                    break;
            }
        } catch (error) {
            console.error(`Error loading ${tabName} tab:`, error);
        }
    }

    // Tab-specific loading methods (for backward compatibility with HTML onclick attributes)
    async loadOverview() {
        await this.overviewRenderer.renderOverview();
    }

    async loadChannels() {
        await this.channelRenderer.renderChannels();
    }

    async loadTemplates() {
        await this.templateRenderer.renderTemplates();
    }

    async loadHistory() {
        // Get filters from UI elements
        const typeFilter = document.getElementById('historyFilter')?.value || '';
        const channelFilter = document.getElementById('channelFilter')?.value || '';
        const dateFilter = document.getElementById('dateFilter')?.value || '';

        const filters = {};
        if (typeFilter) filters.type = typeFilter;
        if (channelFilter) filters.channel = channelFilter;
        if (dateFilter) filters.date = dateFilter;

        await this.historyRenderer.renderHistory(filters);
    }

    async loadSettings() {
        await this.settingsManager.loadSettings();
    }

    // Form processing methods (for backward compatibility)
    async sendQuickNotification() {
        await this.notificationSender.sendQuickNotification();
    }

    async createTemplate() {
        await this.templateCreator.createTemplate();
    }

    // Channel-related methods (for backward compatibility)
    async testChannel(channelName) {
        try {
            const response = await this.dataLoader.testChannel(channelName);

            if (response.success) {
                // Import toast function for notification
                const { showToast } = await import('./utils/toast-manager.js');
                showToast(`${channelName} 채널 테스트가 성공했습니다.`, 'success');
            } else {
                const { showToast } = await import('./utils/toast-manager.js');
                showToast(`${channelName} 채널 테스트가 실패했습니다: ${response.error}`, 'error');
            }
        } catch (error) {
            console.error('Error testing channel:', error);
            const { showToast } = await import('./utils/toast-manager.js');
            showToast('채널 테스트 중 오류가 발생했습니다.', 'error');
        }
    }

    // Auto-refresh methods
    startAutoRefresh() {
        // Clear any existing interval
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        // Set up new interval to refresh overview data every 30 seconds
        this.refreshInterval = setInterval(() => {
            if (this.tabManager.getCurrentTab() === 'overview') {
                this.loadOverview();
            }
        }, 30000); // 30 seconds
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // Utility methods for backward compatibility
    async saveSettings() {
        await this.settingsManager.saveSettings();
    }
}

// Create global functions for backward compatibility with HTML onclick attributes
function loadHistory() {
    if (window.dashboard) {
        window.dashboard.loadHistory();
    }
}

function createTemplate() {
    if (window.dashboard) {
        window.dashboard.createTemplate();
    }
}

function testChannel(channelName) {
    if (window.dashboard) {
        window.dashboard.testChannel(channelName);
    }
}

function editTemplate(templateId) {
    // Implementation for editing a template
    console.log(`Editing template: ${templateId}`);
}

function deleteTemplate(templateId) {
    // Implementation for deleting a template
    console.log(`Deleting template: ${templateId}`);
}

function configureChannel(channelName) {
    // Implementation for configuring a channel
    console.log(`Configuring channel: ${channelName}`);
}

// Initialize the dashboard when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new NotificationDashboard();
});

// Export the main class for potential use in other modules
export default NotificationDashboard;