/**
 * Data Loader for Notification Dashboard
 * Manages data loading operations for different dashboard sections
 */

import NotificationApiClient from './api-client.js';

class NotificationDataLoader {
    constructor() {
        this.apiClient = new NotificationApiClient();
    }

    /**
     * Load overview data including status, channels, and recent notifications
     */
    async loadOverview() {
        try {
            // Load service status
            const statusResponse = await this.apiClient.fetchStatus();
            
            // Load channels status
            const channelsResponse = await this.apiClient.fetchChannels();
            
            // Load recent notifications
            const historyResponse = await this.apiClient.fetchHistory(10);

            return {
                status: statusResponse.success ? statusResponse.status : null,
                channels: channelsResponse.success ? channelsResponse.channels : null,
                history: historyResponse.success ? historyResponse.history : null
            };
        } catch (error) {
            console.error('Error loading overview data:', error);
            throw error;
        }
    }

    /**
     * Load channels data
     */
    async loadChannels() {
        try {
            const response = await this.apiClient.fetchChannels();
            return response.success ? response.channels : null;
        } catch (error) {
            console.error('Error loading channels data:', error);
            throw error;
        }
    }

    /**
     * Load templates data
     */
    async loadTemplates() {
        try {
            const response = await this.apiClient.fetchTemplates();
            return response.success ? response.templates : null;
        } catch (error) {
            console.error('Error loading templates data:', error);
            throw error;
        }
    }

    /**
     * Load history data with optional filters
     */
    async loadHistory(filters = {}) {
        try {
            const response = await this.apiClient.fetchFilteredHistory(filters);
            return response.success ? response.history : null;
        } catch (error) {
            console.error('Error loading history data:', error);
            throw error;
        }
    }

    /**
     * Create a new template
     */
    async createTemplate(templateData) {
        try {
            const response = await this.apiClient.createTemplate(templateData);
            return response;
        } catch (error) {
            console.error('Error creating template:', error);
            throw error;
        }
    }

    /**
     * Send a quick notification
     */
    async sendNotification(notificationData) {
        try {
            const response = await this.apiClient.sendNotification(notificationData);
            return response;
        } catch (error) {
            console.error('Error sending notification:', error);
            throw error;
        }
    }

    /**
     * Test a notification channel
     */
    async testChannel(channelName) {
        try {
            const response = await this.apiClient.testChannel(channelName);
            return response;
        } catch (error) {
            console.error('Error testing channel:', error);
            throw error;
        }
    }
}

// Export the class for use in other modules
export default NotificationDataLoader;