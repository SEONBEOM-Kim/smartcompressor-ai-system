/**
 * Settings Manager for Notification Dashboard
 * Handles settings form processing and loading
 */

import { showToast } from '../utils/toast-manager.js';

class SettingsManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add event listener to the settings form
        const form = document.getElementById('settingsForm');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveSettings();
            });
        }
    }

    /**
     * Load settings from the UI
     */
    async loadSettings() {
        // In a real implementation, this would fetch settings from an API
        // For now, we're just setting default values
        
        const defaultChannelsEl = document.getElementById('defaultChannels');
        if (defaultChannelsEl) {
            // Set default value for multi-select
            Array.from(defaultChannelsEl.options).forEach(option => {
                if (['websocket', 'email'].includes(option.value)) {
                    option.selected = true;
                } else {
                    option.selected = false;
                }
            });
        }

        const rateLimitEl = document.getElementById('rateLimit');
        if (rateLimitEl) {
            rateLimitEl.value = 100;
        }

        const emergencyChannelsEl = document.getElementById('emergencyChannels');
        if (emergencyChannelsEl) {
            // Set default value for multi-select
            Array.from(emergencyChannelsEl.options).forEach(option => {
                if (['websocket', 'slack', 'discord'].includes(option.value)) {
                    option.selected = true;
                } else {
                    option.selected = false;
                }
            });
        }

        const autoRetryEl = document.getElementById('autoRetry');
        if (autoRetryEl) {
            autoRetryEl.checked = true;
        }
    }

    /**
     * Save settings from the form
     */
    async saveSettings() {
        try {
            // In a real implementation, this would send settings to an API
            // For now, we're just showing a success message
            
            // Collect settings from form
            const defaultChannels = Array.from(document.getElementById('defaultChannels').selectedOptions).map(o => o.value);
            const rateLimit = parseInt(document.getElementById('rateLimit').value);
            const emergencyChannels = Array.from(document.getElementById('emergencyChannels').selectedOptions).map(o => o.value);
            const autoRetry = document.getElementById('autoRetry').checked;

            // In a real implementation, we would save these settings to the server
            // const settings = {
            //     default_channels: defaultChannels,
            //     rate_limit: rateLimit,
            //     emergency_channels: emergencyChannels,
            //     auto_retry: autoRetry
            // };
            //
            // await this.apiClient.saveSettings(settings);

            showToast('설정이 저장되었습니다.', 'success');
        } catch (error) {
            console.error('Error saving settings:', error);
            showToast('설정 저장 중 오류가 발생했습니다.', 'error');
        }
    }
}

// Export the class for use in other modules
export default SettingsManager;